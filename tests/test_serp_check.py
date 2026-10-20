import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "serp_check.py"
SPEC = importlib.util.spec_from_file_location("serp_check", MODULE_PATH)
serp_check = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(serp_check)

FILLER = "<div>" + ("x " * 2000) + "</div>"


class SerpCheckTests(unittest.TestCase):
    def test_google_redirect_shell_in_chinese_is_invalid(self) -> None:
        html = "<html><body>Google Search " + FILLER + " 如果您在几秒钟内没有被重定向，请点击 <a href='/search?q=x&sei=1'>此处</a>。</body></html>"
        result = serp_check.assess(html, "google", "https://www.google.com/search?q=x")
        self.assertFalse(result["valid"])
        self.assertIn("没有被重定向", result["reason"])

    def test_baidu_captcha_page_is_invalid(self) -> None:
        html = "<html><title>百度安全验证</title><body>百度安全验证 网络不给力，请稍后重试 <a href='https://www.baidu.com'>返回首页</a></body></html>"
        result = serp_check.assess(html, "baidu", "https://www.baidu.com/s?wd=x")
        self.assertFalse(result["valid"])

    def test_result_page_with_external_links_is_valid(self) -> None:
        items = "".join(
            f"<li class='b_algo'><h2><a href='https://site{i}.example.org/article/{i}'>Result title number {i}</a></h2></li>" for i in range(5)
        )
        html = f"<html><body><a href='https://cn.bing.com/images'>图片</a><ol>{items}</ol>{FILLER}</body></html>"
        result = serp_check.assess(html, "bing_cn", "https://cn.bing.com/search?q=x")
        self.assertTrue(result["valid"])
        self.assertEqual(result["result_links"], 5)
        self.assertEqual(len(result["domains"]), 5)

    def test_bing_click_wrapper_is_decoded(self) -> None:
        import base64
        encoded = "a1" + base64.urlsafe_b64encode(b"https://real.example.com/page").decode().rstrip("=")
        url, wrapped = serp_check.resolve_href(f"https://www.bing.com/ck/a?!&&p=abc&u={encoded}&ntb=1", "https://cn.bing.com/")
        self.assertEqual(url, "https://real.example.com/page")
        self.assertFalse(wrapped)

    def test_duckduckgo_and_google_redirects_are_unwrapped(self) -> None:
        url, _ = serp_check.resolve_href("//duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.com%2Fa&rut=1", "https://lite.duckduckgo.com/lite/")
        self.assertEqual(url, "https://example.com/a")
        url, _ = serp_check.resolve_href("/url?q=https://example.net/b&sa=U", "https://www.google.com/search?q=x")
        self.assertEqual(url, "https://example.net/b")

    def test_sogou_wrapped_results_count_without_domains(self) -> None:
        items = "".join(f"<h3><a href='/link?url=abc{i}'>搜狗结果标题第{i}条内容</a></h3>" for i in range(4))
        result = serp_check.assess(f"<html><body>{items}{FILLER}</body></html>", "sogou", "https://sogou.com/web?query=x")
        self.assertTrue(result["valid"])
        self.assertEqual(result["wrapped_links"], 4)
        self.assertEqual(result["domains"], [])

    def test_empty_small_page_is_invalid(self) -> None:
        result = serp_check.assess("<html><body>ok</body></html>", "yahoo")
        self.assertFalse(result["valid"])


if __name__ == "__main__":
    unittest.main()
