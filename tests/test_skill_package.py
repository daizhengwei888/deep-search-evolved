import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SkillPackageTests(unittest.TestCase):
    def test_frontmatter_fits_host_limits(self) -> None:
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        match = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
        self.assertIsNotNone(match)
        fields = dict(line.split(":", 1) for line in match.group(1).splitlines() if ":" in line)
        self.assertEqual(fields["name"].strip(), "deep-search")
        self.assertLessEqual(len(fields["description"].strip()), 1024)   # ZCode drops skills with longer descriptions
        self.assertLess(len(text.encode("utf-8")), 100 * 1024)            # ZCode truncates bodies over 100 KB

    def test_core_files_avoid_host_specific_worker_syntax(self) -> None:
        for name in ("SKILL.md", "DEEP_SEARCH.md", "DEEP_SEARCH_EXECUTOR.md", "contracts/runtime-contract.md"):
            text = (ROOT / name).read_text(encoding="utf-8")
            self.assertNotIn("subagent_type", text, name)
            self.assertNotIn("load_skills", text, name)
            self.assertNotIn("task({", text, name)

    def test_local_links_in_skill_md_resolve(self) -> None:
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for target in re.findall(r"\]\(([^)#]+)\)", text):
            if "://" in target:
                continue
            self.assertTrue((ROOT / target).exists(), target)

    def test_evals_are_offline_fixtures_with_rubrics(self) -> None:
        data = json.loads((ROOT / "evals" / "evals.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(data["evals"]), 5)
        for item in data["evals"]:
            self.assertTrue(item["prompt"].strip())
            self.assertTrue(item["assertions"])
            self.assertTrue(item.get("offline", False))

    def test_all_adapters_have_manifests(self) -> None:
        for platform in ("claude-code", "codex", "opencode", "zcode", "hermes", "openclaw"):
            manifest = json.loads((ROOT / "adapters" / platform / "adapter.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["platform"], platform)
            self.assertTrue((ROOT / "adapters" / platform / "README.md").exists())


if __name__ == "__main__":
    unittest.main()
