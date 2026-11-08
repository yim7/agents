#!/usr/bin/env python3
"""把 AGENTS.md 和 skills 复制到本机各 agent 的配置目录。

覆盖或删除前先备份到目标目录的 .backups/<时间>/。每个目标目录的
.installed-skills.json 记录本脚本装过的技能，仓库里删掉的技能只从
登记过的目录移除，别处装的技能不动。
"""

from __future__ import annotations

import argparse
import filecmp
import json
import os
import shutil
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_NAME = ".installed-skills.json"

# (参数名, 默认目录, 指令文件装成什么名字或 None, 是否装 skills)
TARGETS = [
    ("claude", "~/.claude", "CLAUDE.md", True),
    ("dsh", os.environ.get("DSH_HOME") or "~/.dsh", "AGENTS.md", False),
    ("agents", "~/.agents", None, True),  # DeepSeek Harness 和 Codex 都从这里读 skills
    ("codex", "~/.codex", "AGENTS.md", False),
]


def same_content(a: Path, b: Path) -> bool:
    if a.is_file() and b.is_file():
        return filecmp.cmp(a, b, shallow=False)
    if a.is_dir() and b.is_dir():
        files = sorted(p.relative_to(a) for p in a.rglob("*") if p.is_file())
        if files != sorted(p.relative_to(b) for p in b.rglob("*") if p.is_file()):
            return False
        return all(filecmp.cmp(a / f, b / f, shallow=False) for f in files)
    return False


def copy(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir():
        shutil.copytree(src, dest)
    else:
        shutil.copy2(src, dest)


def remove(path: Path, home: Path, backups: Path) -> None:
    """先备份到 backups 下的同名相对路径，再删除。"""
    copy(path, backups / path.relative_to(home))
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()
    print(f"  已备份: {path} -> {backups / path.relative_to(home)}")


def install(src: Path, dest: Path, home: Path, backups: Path, dry_run: bool) -> bool:
    if dest.exists() and same_content(src, dest):
        return False
    if dry_run:
        print(f"  将{'备份并覆盖' if dest.exists() else '安装'}: {dest}")
        return True
    if dest.exists():
        remove(dest, home, backups)
    copy(src, dest)
    print(f"  已安装: {dest}")
    return True


def sync(home: Path, agents_name: str | None, with_skills: bool, backups: Path, dry_run: bool) -> None:
    manifest_path = home / MANIFEST_NAME
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {"agents": None, "skills": []}
    changed = False

    if agents_name:
        changed |= install(REPO_ROOT / "AGENTS.md", home / agents_name, home, backups, dry_run)
        manifest["agents"] = agents_name

    skills = sorted(d.name for d in (REPO_ROOT / "skills").iterdir()
                    if d.is_dir() and not d.name.startswith(".")) if with_skills else []
    for name in skills:
        changed |= install(REPO_ROOT / "skills" / name, home / "skills" / name, home, backups, dry_run)
    for name in manifest.get("skills", []):
        stale = home / "skills" / name
        if name not in skills and stale.exists():
            changed = True
            if dry_run:
                print(f"  将移除旧 skill: {stale}")
            else:
                remove(stale, home, backups)
                print(f"  已移除旧 skill: {stale}")
    manifest["skills"] = skills

    if not dry_run and (changed or not manifest_path.exists()):
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="同步 AGENTS.md 和 skills 到本机 agent 配置目录。")
    for name, default, _, _ in TARGETS:
        parser.add_argument(f"--{name}-home", type=Path, default=Path(default))
    parser.add_argument("--dry-run", action="store_true", help="只预览，不修改文件。")
    args = parser.parse_args()

    homes = {name: getattr(args, f"{name}_home").expanduser().resolve() for name, *_ in TARGETS}
    for name, _, _, with_skills in TARGETS:
        if with_skills and (homes[name] / "skills").is_symlink():
            raise SystemExit(f"请先将软链接替换为独立目录，再安装: {homes[name] / 'skills'}")

    skills_dir = REPO_ROOT / "skills"
    if not skills_dir.is_dir() or not any(d.is_dir() and not d.name.startswith(".") for d in skills_dir.iterdir()):
        raise SystemExit("仓库里没有可安装的 skill，停止安装，避免把已装的技能当成旧技能删掉。")

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    print(f"仓库目录: {REPO_ROOT}")
    for name, _, agents_name, with_skills in TARGETS:
        home = homes[name]
        print(f"{name}: {home}")
        sync(home, agents_name, with_skills, home / ".backups" / stamp, args.dry_run)


if __name__ == "__main__":
    main()
