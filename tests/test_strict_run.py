import json
import tempfile
import unittest
from pathlib import Path
import importlib.util


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "strict-run.py"
SPEC = importlib.util.spec_from_file_location("strict_run", MODULE_PATH)
strict_run = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(strict_run)


class StrictRunTests(unittest.TestCase):
    def test_report_template_contains_required_sections(self) -> None:
        plan = {"query": "test query"}
        run_summary = {"generated_at": "2026-04-17T00:00:00Z"}
        template = strict_run.build_report_template(plan, run_summary, 3)
        self.assertIn("执行摘要 / Executive Summary", template)
        self.assertIn("附录 / Appendices", template)

    def test_parse_news_output_extracts_json_array(self) -> None:
        stdout = "/Users/example/warn\n[{\"source\":\"Hacker News\",\"url\":\"https://example.com\"}]"
        parsed = strict_run.parse_news_output(stdout)
        self.assertEqual(parsed[0]["source"], "Hacker News")

    def test_write_json_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "artifact.json"
            payload = {"strict": True, "artifacts": ["plan.json"]}
            strict_run.write_json(path, payload)
            self.assertEqual(json.loads(path.read_text()), payload)

    def build_report(self, sources_payload, deviations=None, min_domains=3, artifacts=None):
        plan = {"query": "test query", "intent": "universal", "primary_agent": "Global Observer", "platform": "codex", "strict": True, "min_domains": min_domains}
        run_summary = {"generated_at": "2026-04-17T00:00:00Z", "artifacts": artifacts if artifacts is not None else {"plan": "/tmp/plan.json"}}
        return strict_run.build_final_report(plan, run_summary, sources_payload, {"deviations": deviations or []})

    def test_build_final_report_counts_result_links_and_real_domains(self) -> None:
        sources_payload = {
            "broad_web_search": {"engines_success": 2, "engines_total": 5, "result_links_total": 12,
                                 "domains": ["example.com", "example.org"], "results_dir": "/tmp/results"},
            "community_discussion": [{"source": "Hacker News", "title": "Example", "url": "https://news.ycombinator.com/item?id=1"}],
        }
        report = self.build_report(sources_payload)
        self.assertEqual(report["data_points"], 13)          # parsed candidates, not engine count
        self.assertEqual(report["source_domains"], 3)        # real domains, not capability names
        self.assertEqual(report["overall_confidence"], "MEDIUM")
        self.assertEqual(report["verified_evidence"], 0)
        self.assertIn("执行摘要 / Executive Summary", report["sections"])

    def test_engine_successes_without_parsed_links_are_low_confidence(self) -> None:
        sources_payload = {"broad_web_search": {"engines_success": 6, "engines_total": 7, "result_links_total": 0, "domains": []}, "community_discussion": []}
        report = self.build_report(sources_payload)
        self.assertEqual(report["data_points"], 0)
        self.assertEqual(report["overall_confidence"], "LOW")

    def test_too_few_domains_is_low_and_never_high(self) -> None:
        few = {"broad_web_search": {"result_links_total": 30, "domains": ["a.com"]}, "community_discussion": []}
        self.assertEqual(self.build_report(few)["overall_confidence"], "LOW")
        many = {"broad_web_search": {"result_links_total": 30, "domains": [f"d{i}.com" for i in range(10)]}, "community_discussion": [{"url": "https://x.org/1"}]}
        self.assertEqual(self.build_report(many)["overall_confidence"], "MEDIUM")

    def test_appendix_lists_artifacts_and_deviations(self) -> None:
        report = self.build_report({"broad_web_search": {}, "community_discussion": []},
                                   deviations=[{"stage": "broad_web_search", "summary": "Some search engines failed", "detail": "{}"}],
                                   artifacts={"plan": "/tmp/plan.json", "sources": "/tmp/sources.json"})
        appendix = report["sections"]["附录 / Appendices"]
        self.assertIn("/tmp/plan.json", appendix)
        self.assertIn("Some search engines failed", appendix)

    def test_stage_status_marks_partial(self) -> None:
        self.assertEqual(strict_run.stage_status(0, ok=True, partial=False), "completed")
        self.assertEqual(strict_run.stage_status(0, ok=False, partial=True), "partial")
        self.assertEqual(strict_run.stage_status(0, ok=False, partial=False), "failed")
        self.assertEqual(strict_run.stage_status(1, ok=True, partial=True), "failed")

    def test_render_final_report_markdown_includes_metadata(self) -> None:
        report = {
            "title": "⚡ Deep-Search: test",
            "generated_at": "2026-04-17T00:00:00Z",
            "data_points": 3,
            "source_domains": 2,
            "overall_confidence": "MEDIUM",
            "sections": {
                "执行摘要 / Executive Summary": "summary",
                "研究方法 / Methodology": "method",
                "全景分析 / Universal Analysis": "analysis",
                "实证数据 / Empirical Evidence": "evidence",
                "垂直分析 / Domain Analysis": "domain",
                "综合评估 / Synthesis": "synthesis",
                "行动建议 / Recommendations": "recommendations",
                "附录 / Appendices": "appendix",
            },
        }
        markdown = strict_run.render_final_report_markdown(report)
        self.assertIn("整体置信度", markdown)
        self.assertIn("## 8. 附录 / Appendices", markdown)


if __name__ == "__main__":
    unittest.main()
