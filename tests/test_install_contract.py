"""Exercise the real installer in temporary source and target directories."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


INSTALLER = Path(__file__).resolve().parents[1] / "scripts" / "install.py"
MANIFEST = ".installed-skills.json"
OLD = "design-before-coding"
NEW = "software-design"


class InstallContractTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="agents-install-test-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.source = self.root / "source"
        self.codex = self.root / "codex"
        self.agents = self.root / "agents"
        self.claude = self.root / "home" / ".claude"
        (self.source / "scripts").mkdir(parents=True)
        shutil.copy2(INSTALLER, self.source / "scripts" / "install.py")
        self.write(self.source / "AGENTS.md", "# Test configuration\n")
        self.write(self.source / "skills" / NEW / "SKILL.md", "new skill\n")

    @staticmethod
    def write(path: Path, text: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def seed_legacy(self, tracked: bool | None) -> Path:
        legacy = self.agents / "skills" / OLD / "SKILL.md"
        self.write(legacy, "local legacy content\n")
        self.write(self.agents / "skills" / "unrelated" / "SKILL.md", "keep me\n")
        if tracked is not None:
            data = {"agents": None, "skills": [OLD] if tracked else []}
            self.write(self.agents / MANIFEST, json.dumps(data) + "\n")
        return legacy

    def run_install(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(self.source / "scripts" / "install.py"),
             "--codex-home", str(self.codex), "--agents-home", str(self.agents),
             "--claude-home", str(self.claude), *args],
            cwd=self.source,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            capture_output=True, text=True, encoding="utf-8", timeout=20,
            check=False,
        )

    def test_tracked_legacy_is_backed_up_and_removed(self) -> None:
        legacy = self.seed_legacy(tracked=True)
        result = self.run_install()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(legacy.parent.exists())
        self.assertEqual((self.agents / "skills" / NEW / "SKILL.md").read_text(), "new skill\n")
        backups = list((self.agents / ".backups").glob(f"*/skills/{OLD}/SKILL.md"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), "local legacy content\n")
        self.assertEqual(json.loads((self.agents / MANIFEST).read_text())["skills"], [NEW])
        self.assertEqual((self.agents / "skills" / "unrelated" / "SKILL.md").read_text(), "keep me\n")

    def assert_untracked_legacy_survives(self, tracked: bool | None) -> None:
        legacy = self.seed_legacy(tracked)
        result = self.run_install()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(legacy.read_text(), "local legacy content\n")
        self.assertTrue((self.agents / "skills" / NEW / "SKILL.md").is_file())
        self.assertNotIn(OLD, json.loads((self.agents / MANIFEST).read_text())["skills"])
        self.assertEqual((self.agents / "skills" / "unrelated" / "SKILL.md").read_text(), "keep me\n")

    def test_missing_manifest_does_not_delete_legacy(self) -> None:
        self.assert_untracked_legacy_survives(tracked=None)

    def test_existing_manifest_without_old_name_does_not_delete_legacy(self) -> None:
        self.assert_untracked_legacy_survives(tracked=False)

    def test_dry_run_does_not_write_or_remove_files(self) -> None:
        self.seed_legacy(tracked=True)
        before = {p.relative_to(self.root): p.read_bytes()
                  for p in self.root.rglob("*") if p.is_file()}
        result = self.run_install("--dry-run")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        after = {p.relative_to(self.root): p.read_bytes()
                 for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)
        self.assertFalse(self.codex.exists())
        self.assertFalse(self.claude.exists())
        self.assertFalse((self.agents / ".backups").exists())

    def test_claude_installs_independent_copies_and_is_idempotent(self) -> None:
        self.write(self.source / "skills" / NEW / "references" / "guide.md", "reference\n")
        result = self.run_install()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for dest in (self.codex / "AGENTS.md", self.claude / "CLAUDE.md"):
            self.assertEqual(dest.read_bytes(), (self.source / "AGENTS.md").read_bytes())
            self.assertFalse(dest.is_symlink())
        self.assertFalse((self.claude / "AGENTS.md").exists())
        self.assertFalse((self.codex / "skills").exists())
        for target in (self.agents, self.claude):
            installed = target / "skills" / NEW
            self.assertFalse((target / "skills").is_symlink())
            self.assertFalse(installed.is_symlink())
            self.assertEqual((installed / "references" / "guide.md").read_text(), "reference\n")
        self.assertEqual(json.loads((self.claude / MANIFEST).read_text()),
                         {"agents": "CLAUDE.md", "skills": [NEW]})
        before = {p.relative_to(self.root): (p.read_bytes(), p.stat().st_mtime_ns)
                  for p in self.root.rglob("*") if p.is_file()}
        result = self.run_install()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        after = {p.relative_to(self.root): (p.read_bytes(), p.stat().st_mtime_ns)
                 for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)
        self.write(self.claude / "skills" / NEW / "SKILL.md", "local edit\n")
        self.assertEqual((self.source / "skills" / NEW / "SKILL.md").read_text(), "new skill\n")
        self.assertEqual((self.agents / "skills" / NEW / "SKILL.md").read_text(), "new skill\n")

    def test_claude_backup_and_cleanup_respect_its_own_manifest(self) -> None:
        self.write(self.claude / "CLAUDE.md", "local instructions\n")
        self.write(self.claude / "skills" / NEW / "SKILL.md", "local skill\n")
        self.write(self.claude / "skills" / OLD / "SKILL.md", "old skill\n")
        self.write(self.claude / "skills" / "unrelated" / "SKILL.md", "keep me\n")
        self.write(self.claude / MANIFEST, json.dumps(
            {"agents": "CLAUDE.md", "skills": [OLD]}
        ))
        self.seed_legacy(tracked=False)
        before = {p.relative_to(self.root): p.read_bytes()
                  for p in self.root.rglob("*") if p.is_file()}
        preview = self.run_install("--dry-run")
        self.assertEqual(preview.returncode, 0, preview.stdout + preview.stderr)
        self.assertEqual(before, {p.relative_to(self.root): p.read_bytes()
                                for p in self.root.rglob("*") if p.is_file()})
        result = self.run_install()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse((self.claude / "skills" / OLD).exists())
        self.assertTrue((self.agents / "skills" / OLD / "SKILL.md").is_file())
        self.assertEqual((self.claude / "skills" / "unrelated" / "SKILL.md").read_text(), "keep me\n")
        self.assertEqual((self.claude / "skills" / NEW / "SKILL.md").read_text(), "new skill\n")
        self.assertEqual((self.claude / "CLAUDE.md").read_text(), "# Test configuration\n")
        for relative, expected in (("CLAUDE.md", "local instructions\n"),
                                   (f"skills/{NEW}/SKILL.md", "local skill\n"),
                                   (f"skills/{OLD}/SKILL.md", "old skill\n")):
            backups = list((self.claude / ".backups").glob(f"*/{relative}"))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(), expected)
        self.assertEqual(json.loads((self.claude / MANIFEST).read_text()),
                         {"agents": "CLAUDE.md", "skills": [NEW]})

    def test_claude_symlinked_skills_root_is_rejected_before_any_target_write(self) -> None:
        self.claude.mkdir(parents=True)
        link = self.claude / "skills"
        try:
            link.symlink_to(self.source / "skills", target_is_directory=True)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"Symlinks are unavailable: {exc}")
        result = self.run_install()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(str(link), result.stdout + result.stderr)
        self.assertTrue(link.is_symlink())
        self.assertFalse(self.codex.exists())
        self.assertFalse(self.agents.exists())
        self.assertFalse((self.claude / "CLAUDE.md").exists())
        self.assertFalse((self.claude / MANIFEST).exists())
        self.assertFalse((self.claude / ".backups").exists())

    def test_symlinked_skills_root_is_rejected_without_writes(self) -> None:
        self.agents.mkdir()
        link = self.agents / "skills"
        try:
            link.symlink_to(self.source / "skills", target_is_directory=True)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"Symlinks are unavailable: {exc}")
        result = self.run_install()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("软链接", result.stdout + result.stderr)
        self.assertTrue(link.is_symlink())
        self.assertFalse(self.codex.exists())
        self.assertFalse(self.claude.exists())
        self.assertFalse((self.agents / MANIFEST).exists())
        self.assertFalse((self.agents / ".backups").exists())
        self.assertEqual((self.source / "skills" / NEW / "SKILL.md").read_text(), "new skill\n")


    def test_repo_skills_install_with_references_only(self) -> None:
        repo_skills = INSTALLER.parents[1] / "skills"
        shutil.rmtree(self.source / "skills")
        shutil.copytree(repo_skills, self.source / "skills")
        self.write(self.source / "docs" / "maintainer.md", "not installed\n")
        self.write(self.source / "evals" / "case.md", "not a runtime prompt\n")
        result = self.run_install()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        expected = sorted(p.name for p in repo_skills.iterdir() if p.is_dir())
        for target in (self.agents, self.claude):
            self.assertEqual(json.loads((target / MANIFEST).read_text())["skills"], expected)
            for source_file in repo_skills.rglob("*"):
                if source_file.is_file():
                    installed = target / "skills" / source_file.relative_to(repo_skills)
                    self.assertEqual(installed.read_bytes(), source_file.read_bytes())
        for target in (self.codex, self.agents, self.claude):
            self.assertFalse((target / "docs").exists())
            self.assertFalse((target / "evals").exists())


if __name__ == "__main__":
    unittest.main()
