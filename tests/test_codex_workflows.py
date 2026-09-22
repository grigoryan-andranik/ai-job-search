"""Codex entry points must reach the same workflows and facts as Claude.

These checks catch the original conversion failures: missing command entry
points, nonexistent .Codex paths, and copied profiles that drift after setup.
They run offline and never modify candidate data.
"""

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / ".agents" / "skills"


def canonical_source(path):
    match = re.search(r"^  canonical-source: (.+)$", path.read_text(encoding="utf-8"), re.M)
    return match.group(1) if match else None


def local_links(path):
    text = path.read_text(encoding="utf-8")
    return [
        (path.parent / link.split("#", 1)[0]).resolve()
        for link in re.findall(r"\]\(([^)]+)\)", text)
        if "://" not in link and not link.startswith("#")
    ]


class CodexWorkflowTests(unittest.TestCase):
    def test_every_command_has_a_discoverable_adapter(self):
        for command in (ROOT / ".claude" / "commands").glob("*.md"):
            with self.subTest(command=command.name):
                adapter = SKILLS / command.stem / "SKILL.md"
                self.assertTrue(adapter.is_file(), f"Missing Codex skill for {command.name}")
                text = adapter.read_text(encoding="utf-8")
                self.assertRegex(text, rf"(?m)^name: {re.escape(command.stem)}$")
                self.assertEqual(canonical_source(adapter), command.relative_to(ROOT).as_posix())

    def test_shared_skills_and_legacy_aliases_reach_the_original_sources(self):
        sources = {
            "job-scraper": ".claude/skills/job-scraper/SKILL.md",
            "job-application-assistant": ".claude/skills/job-application-assistant/SKILL.md",
            "upskill": ".claude/skills/upskill/SKILL.md",
            "source-command-expand": ".claude/commands/expand.md",
            "source-command-html-report": ".claude/commands/html-report.md",
        }
        for folder, source in sources.items():
            with self.subTest(folder=folder):
                self.assertEqual(canonical_source(SKILLS / folder / "SKILL.md"), source)

    def test_adapter_links_resolve_to_source_profile_and_runtime_guide(self):
        for adapter in SKILLS.glob("*/SKILL.md"):
            source = canonical_source(adapter)
            if source is None:
                continue  # Portal skills contain their own executable workflow.
            with self.subTest(adapter=adapter.parent.name):
                links = local_links(adapter)
                self.assertIn(ROOT / source, links)
                self.assertIn(ROOT / "CODEX.md", links)
                self.assertIn(ROOT / "CLAUDE.md", links)
                for target in links:
                    self.assertTrue(target.is_relative_to(ROOT), str(target))
                    self.assertTrue(target.is_file(), str(target))
                # Adapters route to the canonical workflow, never embed it.
                source_body = (ROOT / source).read_text(encoding="utf-8")
                self.assertLess(len(adapter.read_text(encoding="utf-8")), len(source_body))

    def test_profile_and_query_references_are_pointers_not_stale_copies(self):
        for folder, pattern in (("job-application-assistant", "[0-9]*.md"), ("job-scraper", "search-queries.md")):
            for source in (ROOT / ".claude" / "skills" / folder).glob(pattern):
                with self.subTest(source=source.name):
                    pointer = SKILLS / folder / source.name
                    self.assertIn(source, local_links(pointer))
                    self.assertLess(len(pointer.read_text(encoding="utf-8")), 1000)

    def test_no_broken_conversion_paths_or_duplicate_skill_names(self):
        names = set()
        for path in SKILLS.rglob("*.md"):
            text = path.read_text(encoding="utf-8")
            self.assertNotRegex(text, r"\.(?:Codex|CODEX)/", str(path))
            if path.name != "SKILL.md":
                continue
            name = re.search(r"^name: [\"']?([a-z0-9-]+)", text, re.M)
            self.assertIsNotNone(name, str(path))
            self.assertNotIn(name.group(1), names)
            names.add(name.group(1))
        self.assertIn("scrape", names)


if __name__ == "__main__":
    unittest.main()
