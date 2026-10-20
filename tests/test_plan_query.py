import json
import tempfile
import unittest
from pathlib import Path
import importlib.util


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "plan-query.py"
SPEC = importlib.util.spec_from_file_location("plan_query", MODULE_PATH)
plan_query = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(plan_query)


REPO_ROOT = Path(__file__).resolve().parents[1]


class PlanQueryTests(unittest.TestCase):
    def build_plan(self, query: str) -> dict:
        return plan_query.build_plan(query, REPO_ROOT, "codex")

    def test_english_legal_query_stays_general(self) -> None:
        plan = self.build_plan("analyze legal compliance risks of a startup fundraising memo")
        self.assertEqual(plan["intent"], "legal")
        self.assertEqual(plan["search_mode"], "general")

    def test_chinese_query_prefers_cn_search(self) -> None:
        plan = self.build_plan("分析中国AI芯片行业趋势")
        self.assertEqual(plan["intent"], "hardware")
        self.assertEqual(plan["search_mode"], "cn")

    def test_community_query_prefers_news_mode(self) -> None:
        plan = self.build_plan("reddit complaints about claude opus 4.7")
        self.assertEqual(plan["intent"], "community")
        self.assertEqual(plan["search_mode"], "news")

    def test_missing_optional_capability_is_reported(self) -> None:
        plan = self.build_plan("analyze legal compliance risks of a startup fundraising memo")
        capabilities = {item["name"]: item for item in plan["capabilities"]}
        self.assertEqual(capabilities["document_processing"]["status"], "MISSING")
        self.assertFalse(capabilities["document_processing"]["required"])

    def test_fallback_provider_is_used_when_primary_missing(self) -> None:
        registry = {
            "capabilities": [
                {
                    "name": "broad_web_search",
                    "primary_provider": "missing-primary",
                    "fallback_providers": ["available-fallback"],
                    "platform_providers": {"codex": "missing-primary"},
                    "platform_fallback_providers": {"codex": ["available-fallback"]},
                    "required": True,
                    "used_for": ["coverage"],
                }
            ]
        }
        with tempfile.TemporaryDirectory() as home_dir, tempfile.TemporaryDirectory() as workspace_dir:
            home_skills = Path(home_dir)
            workspace_skills = Path(workspace_dir)
            (workspace_skills / "available-fallback").mkdir()
            resolved = plan_query.resolve_capabilities(
                ["broad_web_search"],
                registry,
                "codex",
                home_skills,
                workspace_skills,
                True,
            )

        self.assertEqual(len(resolved), 1)
        self.assertEqual(resolved[0]["status"], "FALLBACK")
        self.assertEqual(resolved[0]["provider"], "available-fallback")

    def test_non_bundled_optional_provider_can_be_declared(self) -> None:
        registry_path = REPO_ROOT / "config" / "capability-registry.json"
        registry = json.loads(registry_path.read_text())
        providers = {item["primary_provider"]: item for item in registry["capabilities"]}
        self.assertTrue(providers["github"]["optional_external"])
        self.assertTrue(providers["pdf-text-extractor"]["optional_external"])

    def test_tariff_and_license_questions_route_to_legal(self) -> None:
        self.assertEqual(self.build_plan("2026 年中国新能源车出口欧洲的关税变化")["intent"], "legal")
        self.assertEqual(self.build_plan("某开源模型的许可证能不能商用")["intent"], "legal")
        self.assertEqual(self.build_plan("EU tariffs on Chinese electric vehicles")["intent"], "legal")

    def test_ascii_keywords_match_whole_words_only(self) -> None:
        self.assertEqual(self.build_plan("capital markets outlook")["intent"], "universal")    # "api" inside "capital"
        self.assertEqual(self.build_plan("second quarter results")["intent"], "universal")     # "sec" inside "second"
        self.assertEqual(self.build_plan("compare REST API frameworks")["intent"], "code_tech")

    def test_generic_research_words_do_not_force_academic(self) -> None:
        self.assertEqual(self.build_plan("帮我研究一下店铺的库存周转")["intent"], "universal")
        self.assertEqual(self.build_plan("deep research agent")["intent"], "universal")
        self.assertEqual(self.build_plan("大模型幻觉检测的最新论文")["intent"], "academic")

    def test_output_form_hint(self) -> None:
        self.assertEqual(self.build_plan("Python 3.12 正式版是哪年发布的")["output_form_hint"], "COMPACT")
        self.assertEqual(self.build_plan("对比 React 和 Vue 在企业项目里的优缺点")["output_form_hint"], "STANDARD")
        self.assertEqual(self.build_plan("全面调研 2026 年 AI 编程工具市场")["output_form_hint"], "FULL")

    def test_zcode_platform_and_host_tools(self) -> None:
        plan = plan_query.build_plan("deep research agent", REPO_ROOT, "zcode")
        self.assertEqual(plan["platform"], "zcode")
        self.assertIn("web_search", plan["host_native_tools"])
        self.assertTrue(plan["guardrails_are_soft"])
        claude = plan_query.build_plan("deep research agent", REPO_ROOT, "claude-code")
        self.assertIn("WebSearch", claude["host_native_tools"])

    def test_strict_plan_emits_artifact_requirements(self) -> None:
        plan = plan_query.build_plan("strict audit query", REPO_ROOT, "codex", strict=True)
        self.assertTrue(plan["strict"])
        self.assertEqual(plan["artifact_contract"], "contracts/execution-artifact-schema.json")
        self.assertIn("run-summary.json", plan["required_artifacts"])
        self.assertIn("final-report.json", plan["required_artifacts"])


if __name__ == "__main__":
    unittest.main()
