#!/usr/bin/env python3
"""安装 agents 仓库中的通用配置和 skills。"""

from __future__ import annotations

import argparse
import filecmp
import json
import shutil
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CODEX_HOME = Path("~/.codex").expanduser()
DEFAULT_AGENTS_HOME = Path("~/.agents").expanduser()
DEFAULT_CLAUDE_HOME = Path("~/.claude").expanduser()
MANIFEST_NAME = ".installed-skills.json"


# ── Manifest ────────────────────────────────────────────────


def read_manifest(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text())
    return {"agents": None, "skills": []}


def write_manifest(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


# ── File helpers ────────────────────────────────────────────


def same_content(left: Path, right: Path) -> bool:
    if not left.exists() or not right.exists():
        return False
    if left.is_file() and right.is_file():
        return filecmp.cmp(left, right, shallow=False)
    if left.is_dir() and right.is_dir():
        left_files = sorted(p.relative_to(left) for p in left.rglob("*") if p.is_file())
        right_files = sorted(p.relative_to(right) for p in right.rglob("*") if p.is_file())
        if left_files != right_files:
            return False
        return all(filecmp.cmp(left / r, right / r, shallow=False) for r in left_files)
    return False


def backup(path: Path, base: Path, backup_root: Path) -> Path | None:
    if not path.exists():
        return None
    bp = backup_root / path.relative_to(base)
    bp.parent.mkdir(parents=True, exist_ok=True)
    if path.is_dir():
        shutil.copytree(path, bp)
    else:
        shutil.copy2(path, bp)
    return bp


def safe_remove(path: Path) -> None:
    if not path.exists():
        return
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()


# ── Install ────────────────────────────────────────────────


def install_file(source: Path, dest: Path, base: Path, backup_root: Path, dry_run: bool) -> bool:
    """Install a single file or directory. Returns True if anything changed."""
    if dest.exists() and same_content(source, dest):
        return False
    if dry_run:
        print(f"  将{'备份并覆盖' if dest.exists() else '安装'}: {dest}")
        return True
    bp = backup(dest, base, backup_root)
    if bp:
        print(f"  已备份: {dest} -> {bp}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    safe_remove(dest)
    if source.is_dir():
        shutil.copytree(source, dest)
    else:
        shutil.copy2(source, dest)
    print(f"  已安装: {dest}")
    return True


# ── Sync logic ──────────────────────────────────────────────


def sync_target(
    agents_source: Path | None,
    skills_source: Path | None,
    target: Path,
    backup_root: Path,
    dry_run: bool,
    *,
    agents_dest_name: str = "AGENTS.md",
) -> None:
    """Sync one target directory: install/update from repo, remove stale tracked items."""
    manifest_path = target / MANIFEST_NAME
    manifest = read_manifest(manifest_path)
    changed = False

    # Sync agents file
    if agents_source and agents_source.exists():
        agents_dest = target / agents_dest_name
        if install_file(agents_source, agents_dest, target, backup_root, dry_run):
            changed = True
        if not dry_run:
            manifest["agents"] = agents_dest_name

    # Sync skills
    repo_skills: list[str] = []
    if skills_source and skills_source.exists():
        for d in sorted(skills_source.iterdir()):
            if d.is_dir() and not d.name.startswith("."):
                repo_skills.append(d.name)
                dest = target / "skills" / d.name
                if install_file(d, dest, target, backup_root, dry_run):
                    changed = True

    # Remove skills in manifest but not in repo
    for skill in manifest.get("skills", []):
        if skill not in repo_skills:
            p = target / "skills" / skill
            if p.exists():
                if dry_run:
                    print(f"  将移除旧 skill: {p}")
                else:
                    backup(p, target, backup_root)
                    safe_remove(p)
                    print(f"  已移除旧 skill: {p}")
                    changed = True

    if not dry_run:
        manifest["skills"] = repo_skills
        if changed or not manifest_path.exists():
            write_manifest(manifest_path, manifest)


def remove_misplaced_agents_file(agents_home: Path, backup_root: Path, dry_run: bool) -> None:
    misplaced = agents_home / "AGENTS.md"
    source = REPO_ROOT / "AGENTS.md"
    if not misplaced.exists():
        return
    if dry_run:
        tag = "移除" if (source.exists() and same_content(source, misplaced)) else "备份并移除"
        print(f"  将{tag}误装的 AGENTS.md: {misplaced}")
        return
    if source.exists() and same_content(source, misplaced):
        misplaced.unlink()
        print(f"  已移除误装的 AGENTS.md: {misplaced}")
    else:
        bp = backup(misplaced, agents_home, backup_root)
        if bp:
            print(f"  已备份: {misplaced} -> {bp}")
        misplaced.unlink()
        print(f"  已移除误装的 AGENTS.md: {misplaced}")


# ── CLI ─────────────────────────────────────────────────────


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="同步 AGENTS.md 和 skills 到本机 agent 配置目录。"
    )
    parser.add_argument("--codex-home", type=Path, default=DEFAULT_CODEX_HOME)
    parser.add_argument("--agents-home", type=Path, default=DEFAULT_AGENTS_HOME)
    parser.add_argument("--claude-home", type=Path, default=DEFAULT_CLAUDE_HOME)
    parser.add_argument("--dry-run", action="store_true", help="只预览，不修改文件。")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    codex = args.codex_home.expanduser().resolve()
    agents = args.agents_home.expanduser().resolve()
    claude = args.claude_home.expanduser().resolve()
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")

    print(f"仓库目录: {REPO_ROOT}")
    print(f"Codex: {codex}")
    print(f"Agents: {agents}")
    print(f"Claude: {claude}")

    skills_dir = REPO_ROOT / "skills"
    agents_file = REPO_ROOT / "AGENTS.md"

    if skills_dir.exists() and not any(
        d.is_dir() and not d.name.startswith(".")
        for d in skills_dir.iterdir()
    ):
        print("没有找到可安装的 skill。")
        return

    print()
    sync_target(agents_file, None, codex, codex / ".backups" / ts, args.dry_run)
    sync_target(None, skills_dir, agents, agents / ".backups" / ts, args.dry_run)
    sync_target(agents_file, skills_dir, claude, claude / ".backups" / ts, args.dry_run, agents_dest_name="CLAUDE.md")
    remove_misplaced_agents_file(agents, agents / ".backups" / ts, args.dry_run)


if __name__ == "__main__":
    main()
