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
DEFAULT_CODEX_HOME = Path("~/.codex").expanduser()
DEFAULT_AGENTS_HOME = Path("~/.agents").expanduser()


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
        "--codex-home",
        type=Path,
        default=DEFAULT_CODEX_HOME,
        help=f"Codex 配置目录，默认是 {DEFAULT_CODEX_HOME}",
    )
    parser.add_argument(
        "--agents-home",
        type=Path,
        default=DEFAULT_AGENTS_HOME,
        help=f"用户级 agents 目录，默认是 {DEFAULT_AGENTS_HOME}",
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


def collect_actions(codex_home: Path, agents_home: Path) -> list[InstallAction]:
    actions: list[InstallAction] = []

    agents_file = REPO_ROOT / "AGENTS.md"
    if agents_file.exists():
        actions.append(InstallAction(agents_file, codex_home / "AGENTS.md", "file"))

    skills_dir = REPO_ROOT / "skills"
    if skills_dir.exists():
        for skill_dir in sorted(path for path in skills_dir.iterdir() if path.is_dir()):
            if skill_dir.name.startswith("."):
                continue
            actions.append(InstallAction(skill_dir, agents_home / "skills" / skill_dir.name, "dir"))

    return actions


def backup_existing(destination: Path, backup_base: Path, backup_root: Path) -> Path | None:
    if not destination.exists():
        return None

    backup_path = backup_root / destination.relative_to(backup_base)
    backup_path.parent.mkdir(parents=True, exist_ok=True)

    if destination.is_dir():
        shutil.copytree(destination, backup_path)
    else:
        shutil.copy2(destination, backup_path)

    return backup_path


def install_action(action: InstallAction, backup_base: Path, backup_root: Path, dry_run: bool) -> None:
    if action.destination.exists() and same_path_content(action.source, action.destination):
        print(f"跳过，内容相同: {action.destination}")
        return

    if dry_run:
        if action.destination.exists():
            print(f"将备份并覆盖: {action.destination}")
        else:
            print(f"将安装: {action.destination}")
        return

    backup_path = backup_existing(action.destination, backup_base, backup_root)
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


def remove_misplaced_agents_file(agents_home: Path, backup_root: Path, dry_run: bool) -> None:
    misplaced_file = agents_home / "AGENTS.md"
    source_file = REPO_ROOT / "AGENTS.md"

    if not misplaced_file.exists():
        return

    if dry_run:
        if source_file.exists() and same_path_content(source_file, misplaced_file):
            print(f"将移除误装的 AGENTS.md: {misplaced_file}")
        else:
            print(f"将备份并移除误装的 AGENTS.md: {misplaced_file}")
        return

    if source_file.exists() and same_path_content(source_file, misplaced_file):
        misplaced_file.unlink()
        print(f"已移除误装的 AGENTS.md: {misplaced_file}")
        return

    backup_path = backup_existing(misplaced_file, agents_home, backup_root)
    if backup_path:
        print(f"已备份误装的 AGENTS.md: {misplaced_file} -> {backup_path}")
    misplaced_file.unlink()
    print(f"已移除误装的 AGENTS.md: {misplaced_file}")


def main() -> None:
    args = parse_args()
    codex_home = args.codex_home.expanduser().resolve()
    agents_home = args.agents_home.expanduser().resolve()
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    codex_backup_root = codex_home / ".backups" / timestamp
    agents_backup_root = agents_home / ".backups" / timestamp
    actions = collect_actions(codex_home, agents_home)

    if not actions:
        print("没有找到可安装的配置。")
        return

    print(f"仓库目录: {REPO_ROOT}")
    print(f"Codex 配置目录: {codex_home}")
    print(f"Agents 目录: {agents_home}")

    for action in actions:
        if action.destination.is_relative_to(codex_home):
            install_action(action, codex_home, codex_backup_root, args.dry_run)
        else:
            install_action(action, agents_home, agents_backup_root, args.dry_run)

    remove_misplaced_agents_file(agents_home, agents_backup_root, args.dry_run)


if __name__ == "__main__":
    main()
