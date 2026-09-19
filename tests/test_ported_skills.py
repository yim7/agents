"""Check packaged resources and real installer behavior, not model behavior."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
NAMES = ("to-spec", "handoff", "code-review")
NOTICE = "THIRD_PARTY_NOTICES.txt"
INSTALLED_NOTICE = "yim7-agents-NOTICES.txt"
UPSTREAM = "c55ee46073ed923f86ce59a5eb3b6d895095d1b7"
SOURCES = {
    "to-spec": "skills/engineering/to-spec/SKILL.md",
    "handoff": "skills/productivity/handoff/SKILL.md",
    "code-review": "skills/engineering/code-review/SKILL.md",
}


def files_at(root: Path) -> dict[str, bytes]:
    return {str(p.relative_to(root)): p.read_bytes()
            for p in root.rglob("*") if p.is_file()}


class PortedSkillTests(unittest.TestCase):
    def test_names_sources_and_license(self) -> None:
        notices = (ROOT / NOTICE).read_bytes()
        self.assertEqual(notices.count(b"MIT License\n"), 1)
        license_bytes = b"MIT License\n" + notices.split(b"MIT License\n", 1)[1]
        digest = hashlib.sha1(
            f"blob {len(license_bytes)}\0".encode() + license_bytes
        ).hexdigest()
        self.assertEqual(digest, "f1dd2c09108dde1a5f56097cee8461b3ea834499")
        for name in NAMES:
            with self.subTest(skill=name):
                folder = ROOT / "skills" / name
                text = (folder / "SKILL.md").read_text(encoding="utf-8")
                self.assertTrue(text.startswith("---\n"))
                header, body = text[4:].split("\n---\n", 1)
                self.assertIn(f"name: {name}\n", header + "\n")
                self.assertIn(f"/blob/{UPSTREAM}/{SOURCES[name]}", header)
                self.assertIn("license: MIT", header)
                self.assertTrue(body.strip())
                self.assertFalse((folder / "LICENSE.txt").exists())
                self.assertIn(f"skills/{name}/".encode(), notices)

    def test_invocation_declarations(self) -> None:
        # Verify these scalar declarations only; this is not a YAML parser.
        for name in NAMES:
            with self.subTest(skill=name):
                folder = ROOT / "skills" / name
                header = (folder / "SKILL.md").read_text(encoding="utf-8").split("---\n")[1]
                self.assertNotRegex(header, r"(?m)^\s*(disableModelInvocation|modelInvocable):")
                if name in ("to-spec", "handoff"):
                    self.assertEqual(header.count("disable-model-invocation: true"), 1)
                    self.assertEqual(
                        (folder / "agents" / "openai.yaml").read_text(encoding="utf-8"),
                        "policy:\n  allow_implicit_invocation: false\n",
                    )
                else:
                    self.assertNotIn("disable-model-invocation:", header)
                    self.assertFalse((folder / "agents" / "openai.yaml").exists())

    def test_local_resource_links_are_self_contained(self) -> None:
        for name in NAMES:
            folder = (ROOT / "skills" / name).resolve()
            for path in folder.rglob("*.md"):
                for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
                    if "://" in target or target.startswith("#"):
                        continue
                    resolved = (path.parent / target.split("#", 1)[0]).resolve()
                    with self.subTest(skill=name, target=target):
                        self.assertTrue(resolved.is_relative_to(folder))
                        self.assertTrue(resolved.is_file())

    def install_fixture(self, root: Path) -> tuple[Path, Path, Path]:
        source, codex, agents = root / "source", root / "codex", root / "agents"
        (source / "scripts").mkdir(parents=True)
        shutil.copy2(ROOT / "scripts" / "install.py", source / "scripts" / "install.py")
        (source / "AGENTS.md").write_text("# Fixture only\n", encoding="utf-8")
        shutil.copy2(ROOT / NOTICE, source / NOTICE)
        for name in NAMES:
            shutil.copytree(ROOT / "skills" / name, source / "skills" / name)
        for directory in ("docs", "evals"):
            (source / directory).mkdir()
            (source / directory / "not-runtime.md").write_text("do not install\n", encoding="utf-8")
        for name in ("handoff", "unmanaged-example"):
            folder = agents / "skills" / name
            folder.mkdir(parents=True)
            (folder / "SKILL.md").write_text("existing local content\n", encoding="utf-8")
        (agents / "skills/handoff/LICENSE.txt").write_text("legacy license\n", encoding="utf-8")
        return source, codex, agents

    def run_installer(self, source: Path, codex: Path, agents: Path, *extra: str) -> None:
        result = subprocess.run(
            [sys.executable, str(source / "scripts" / "install.py"),
             "--codex-home", str(codex), "--agents-home", str(agents), *extra],
            cwd=source, env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            capture_output=True, text=True, encoding="utf-8", timeout=20, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_real_installer_copies_resources_and_backs_up_same_name(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ported-skills-") as tmp:
            source, codex, agents = self.install_fixture(Path(tmp))
            self.run_installer(source, codex, agents)
            for name in NAMES:
                with self.subTest(skill=name):
                    self.assertEqual(files_at(source / "skills" / name), files_at(agents / "skills" / name))
            backups = list((agents / ".backups").glob("*/skills/handoff/SKILL.md"))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(encoding="utf-8"), "existing local content\n")
            self.assertEqual((backups[0].parent / "LICENSE.txt").read_text(encoding="utf-8"), "legacy license\n")
            self.assertEqual((agents / INSTALLED_NOTICE).read_bytes(), (source / NOTICE).read_bytes())
            self.assertFalse((codex / INSTALLED_NOTICE).exists())
            self.assertFalse(list((agents / "skills").rglob("LICENSE.txt")))
            self.assertEqual((agents / "skills/unmanaged-example/SKILL.md").read_text(encoding="utf-8"), "existing local content\n")
            self.assertEqual(json.loads((agents / ".installed-skills.json").read_text())["skills"], sorted(NAMES))
            for target in (codex, agents):
                for directory in ("docs", "evals"):
                    self.assertFalse((target / directory).exists())

    def test_shared_notice_is_backed_up_and_repeat_install_is_unchanged(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ported-skills-") as tmp:
            root = Path(tmp)
            source, codex, agents = self.install_fixture(root)
            (agents / INSTALLED_NOTICE).write_text("earlier notice\n", encoding="utf-8")
            self.run_installer(source, codex, agents)
            backups = list((agents / ".backups").glob(f"*/{INSTALLED_NOTICE}"))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(encoding="utf-8"), "earlier notice\n")
            self.assertEqual((agents / INSTALLED_NOTICE).read_bytes(), (source / NOTICE).read_bytes())
            before = files_at(root)
            self.run_installer(source, codex, agents)
            self.assertEqual(before, files_at(root))

    def test_dry_run_preserves_existing_files(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ported-skills-") as tmp:
            root = Path(tmp)
            source, codex, agents = self.install_fixture(root)
            before = files_at(root)
            self.run_installer(source, codex, agents, "--dry-run")
            self.assertEqual(before, files_at(root))
            self.assertFalse(codex.exists())
            self.assertFalse((agents / ".backups").exists())
            self.assertFalse((agents / ".installed-skills.json").exists())


if __name__ == "__main__":
    unittest.main()
