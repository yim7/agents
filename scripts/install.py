#!/usr/bin/env python3
"""安装 agents 仓库中的通用配置和 skills。"""

from __future__ import annotations

import argparse
import filecmp
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TARGET_DIR = Path("~/.agents").expanduser()
RENAMED_SKILLS = {
    "software-design-philosophy": "design-before-coding",
    "software-design-philosophy-review": "design-review",
}


@dataclass(frozen=True)
class InstallAction:
    source: Path
    destination: Path
    kind: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="把当前仓库中的 AGENTS.md 和 skills/ 安装到本机 agent 配置目录。"
    )
    parser.add_argument(
        "--target-dir",
        type=Path,
        default=DEFAULT_TARGET_DIR,
        help=f"目标目录，默认是 {DEFAULT_TARGET_DIR}",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只打印将要执行的动作，不修改文件。",
    )
    return parser.parse_args()


def same_path_content(left: Path, right: Path) -> bool:
    if not left.exists() or not right.exists():
        return False
    if left.is_file() and right.is_file():
        return filecmp.cmp(left, right, shallow=False)
    if left.is_dir() and right.is_dir():
        left_files = sorted(path.relative_to(left) for path in left.rglob("*") if path.is_file())
        right_files = sorted(path.relative_to(right) for path in right.rglob("*") if path.is_file())
        if left_files != right_files:
            return False
        return all(filecmp.cmp(left / rel, right / rel, shallow=False) for rel in left_files)
    return False


def collect_actions(target_dir: Path) -> list[InstallAction]:
    actions: list[InstallAction] = []

    agents_file = REPO_ROOT / "AGENTS.md"
    if agents_file.exists():
        actions.append(InstallAction(agents_file, target_dir / "AGENTS.md", "file"))

    skills_dir = REPO_ROOT / "skills"
    if skills_dir.exists():
        for skill_dir in sorted(path for path in skills_dir.iterdir() if path.is_dir()):
            if skill_dir.name.startswith("."):
                continue
            actions.append(InstallAction(skill_dir, target_dir / "skills" / skill_dir.name, "dir"))

    return actions


def backup_existing(destination: Path, target_dir: Path, backup_root: Path) -> Path | None:
    if not destination.exists():
        return None

    backup_path = backup_root / destination.relative_to(target_dir)
    backup_path.parent.mkdir(parents=True, exist_ok=True)

    if destination.is_dir():
        shutil.copytree(destination, backup_path)
    else:
        shutil.copy2(destination, backup_path)

    return backup_path


def install_action(action: InstallAction, target_dir: Path, backup_root: Path, dry_run: bool) -> None:
    if action.destination.exists() and same_path_content(action.source, action.destination):
        print(f"跳过，内容相同: {action.destination}")
        return

    if dry_run:
        if action.destination.exists():
            print(f"将备份并覆盖: {action.destination}")
        else:
            print(f"将安装: {action.destination}")
        return

    backup_path = backup_existing(action.destination, target_dir, backup_root)
    if backup_path:
        print(f"已备份: {action.destination} -> {backup_path}")

    action.destination.parent.mkdir(parents=True, exist_ok=True)
    if action.destination.exists():
        if action.destination.is_dir():
            shutil.rmtree(action.destination)
        else:
            action.destination.unlink()

    if action.kind == "dir":
        shutil.copytree(action.source, action.destination)
    else:
        shutil.copy2(action.source, action.destination)

    print(f"已安装: {action.destination}")


def remove_renamed_skills(target_dir: Path, backup_root: Path, dry_run: bool) -> None:
    skills_source_dir = REPO_ROOT / "skills"
    target_skills_dir = target_dir / "skills"

    for old_name, new_name in RENAMED_SKILLS.items():
        if not (skills_source_dir / new_name).exists():
            continue

        old_destination = target_skills_dir / old_name
        if not old_destination.exists():
            continue

        if dry_run:
            print(f"将备份并移除旧 skill 名称: {old_destination}")
            continue

        backup_path = backup_existing(old_destination, target_dir, backup_root)
        if backup_path:
            print(f"已备份旧 skill: {old_destination} -> {backup_path}")

        if old_destination.is_dir():
            shutil.rmtree(old_destination)
        else:
            old_destination.unlink()

        print(f"已移除旧 skill 名称: {old_destination}")


def main() -> None:
    args = parse_args()
    target_dir = args.target_dir.expanduser().resolve()
    backup_root = target_dir / ".backups" / datetime.now().strftime("%Y%m%d-%H%M%S")
    actions = collect_actions(target_dir)

    if not actions:
        print("没有找到可安装的配置。")
        return

    print(f"仓库目录: {REPO_ROOT}")
    print(f"目标目录: {target_dir}")

    for action in actions:
        install_action(action, target_dir, backup_root, args.dry_run)

    remove_renamed_skills(target_dir, backup_root, args.dry_run)


if __name__ == "__main__":
    main()
