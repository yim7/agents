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
             *args],
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
        self.assertFalse((self.agents / ".backups").exists())

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
        self.assertFalse((self.agents / MANIFEST).exists())
        self.assertFalse((self.agents / ".backups").exists())
        self.assertEqual((self.source / "skills" / NEW / "SKILL.md").read_text(), "new skill\n")


    def test_project_context_bundle_and_migration_boundaries(self) -> None:
        bundle = INSTALLER.parents[1] / "skills" / "project-context"
        self.assertEqual(
            {p.relative_to(bundle).as_posix() for p in bundle.rglob("*") if p.is_file()},
            {"SKILL.md", "references/project-agents.md",
             "references/domain-context.md", "references/decision-record.md"},
        )
        shutil.copytree(bundle, self.source / "skills" / "project-context")
        self.write(self.source / "docs" / "maintainer.md", "not installed\n")
        self.write(self.source / "evals" / "case.md", "not a runtime prompt\n")
        for tracked in (True, False, None):
            with self.subTest(tracked=tracked):
                self.codex = self.root / str(tracked) / "codex"
                self.agents = self.root / str(tracked) / "agents"
                old_name = "domain-modeling"
                legacy = self.agents / "skills" / old_name / "SKILL.md"
                self.write(legacy, "local domain notes\n")
                self.write(self.agents / "skills" / "unrelated" / "SKILL.md", "keep me\n")
                if tracked is not None:
                    self.write(self.agents / MANIFEST, json.dumps(
                        {"agents": None, "skills": [old_name] if tracked else []}
                    ) + "\n")
                result = self.run_install()
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                installed = self.agents / "skills" / "project-context"
                for source_file in bundle.rglob("*"):
                    if source_file.is_file():
                        self.assertEqual(
                            (installed / source_file.relative_to(bundle)).read_bytes(),
                            source_file.read_bytes(),
                        )
                if tracked:
                    self.assertFalse(legacy.parent.exists())
                    backups = list((self.agents / ".backups").glob(
                        f"*/skills/{old_name}/SKILL.md"
                    ))
                    self.assertEqual(len(backups), 1)
                    self.assertEqual(backups[0].read_text(), "local domain notes\n")
                else:
                    self.assertEqual(legacy.read_text(), "local domain notes\n")
                self.assertEqual(
                    json.loads((self.agents / MANIFEST).read_text())["skills"],
                    ["project-context", NEW],
                )
                self.assertEqual((self.agents / "skills" / "unrelated" / "SKILL.md").read_text(), "keep me\n")
                for target in (self.codex, self.agents):
                    self.assertFalse((target / "docs").exists())
                    self.assertFalse((target / "evals").exists())
                    self.assertFalse((target / "skills" / "docs").exists())
                    self.assertFalse((target / "skills" / "evals").exists())


if __name__ == "__main__":
    unittest.main()
