#!/usr/bin/env bash
# ==============================================================================
# Search Swarm Dispatcher (deep-search 5.0) — FALLBACK search layer
#
# Prefer host-native search tools. This script fetches a few keyless engines
# directly and validates every result page with scripts/serp_check.py:
# captcha pages, JavaScript redirect shells and empty pages count as FAILED.
#
# Engine sets follow the 2026-10-19 measurement (see LOCAL-NOTES.md). Run
# `python3 scripts/probe-search.py` to re-measure in the current network.
#
# Env: DS_RESULTS_ROOT (default /tmp/omo-deep-search), DS_CONNECT_TIMEOUT (10),
#      DS_MAX_TIME (20)
# ==============================================================================

PLAN_FILE=""
PLATFORM="codex"
if [ "${1:-}" = "--plan" ]; then
  PLAN_FILE="${2:-}"
  shift 2
fi

if [ "${1:-}" = "--platform" ]; then
  PLATFORM="${2:-codex}"
  shift 2
fi

QUERY="${1:-}"
MODE="${2:-general}"  # general, cn, news
RESULTS_DIR="${DS_RESULTS_ROOT:-/tmp/omo-deep-search}/swarm-$(date +%s)-$$"
CONNECT_TIMEOUT="${DS_CONNECT_TIMEOUT:-10}"
MAX_TIME="${DS_MAX_TIME:-20}"
mkdir -p "$RESULTS_DIR"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CHECKER="$ROOT_DIR/scripts/serp_check.py"

if [ -n "$PLAN_FILE" ]; then
  if [ ! -f "$PLAN_FILE" ]; then
    echo "❌ plan file not found: $PLAN_FILE"
    exit 1
  fi
  eval "$(python3 - "$PLAN_FILE" <<'PY'
import json, shlex, sys
with open(sys.argv[1], encoding="utf-8") as fh:
    data = json.load(fh)
print("PLAN_QUERY=" + shlex.quote(data.get("query", "")))
print("PLAN_MODE=" + shlex.quote(data.get("search_mode", "general")))
print("PLAN_PLATFORM=" + shlex.quote(data.get("platform", "codex")))
PY
)"
  [ -n "$PLAN_QUERY" ] && QUERY="$PLAN_QUERY"
  [ -n "$PLAN_MODE" ] && MODE="$PLAN_MODE"
  [ -n "$PLAN_PLATFORM" ] && PLATFORM="$PLAN_PLATFORM"
fi

if [ -z "$QUERY" ]; then
  echo "❌ usage: $0 [--plan plan.json] [--platform platform] <query> [mode]"
  exit 1
fi

ADAPTER_FILE="$ROOT_DIR/adapters/$PLATFORM/adapter.json"
if [ ! -f "$ADAPTER_FILE" ]; then
  echo "❌ adapter file not found for platform '$PLATFORM': $ADAPTER_FILE"
  exit 1
fi

ENCODED_QUERY=$(python3 -c 'import sys, urllib.parse; print(urllib.parse.quote_plus(sys.argv[1]))' "$QUERY")
USER_AGENT="Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

# Engines that returned parseable results in the 2026-10-19 measurement come first.
ENGINES_GENERAL=(
  "bing_cn|https://cn.bing.com/search?q=$ENCODED_QUERY&ensearch=0"
  "qwant|https://www.qwant.com/?q=$ENCODED_QUERY&t=web"
  "bing_int|https://cn.bing.com/search?q=$ENCODED_QUERY&ensearch=1"
  "ddg_lite|https://lite.duckduckgo.com/lite/?q=$ENCODED_QUERY"
)

ENGINES_CN=(
  "bing_cn|https://cn.bing.com/search?q=$ENCODED_QUERY&ensearch=0"
  "so360|https://www.so.com/s?q=$ENCODED_QUERY"
  "sogou|https://sogou.com/web?query=$ENCODED_QUERY"
  "toutiao|https://so.toutiao.com/search?keyword=$ENCODED_QUERY"
)

ENGINES_NEWS=(
  "bing_news|https://cn.bing.com/news/search?q=$ENCODED_QUERY"
  "qwant_news|https://www.qwant.com/?q=$ENCODED_QUERY&t=news"
  "bing_cn|https://cn.bing.com/search?q=$ENCODED_QUERY&ensearch=0"
)

fetch_engine() {
  local engine_name="$1" engine_url="$2" output_file="$3" status_file="$4"
  local http_code="" effective_url="" attempt=1 response
  while [ "$attempt" -le 2 ]; do
    response=$(curl -sS -L --compressed \
      -A "$USER_AGENT" \
      -H "Accept-Language: zh-CN,zh;q=0.9,en;q=0.8" \
      --connect-timeout "$CONNECT_TIMEOUT" \
      --max-time "$MAX_TIME" \
      -o "$output_file" \
      -w "%{http_code} %{url_effective}" \
      "$engine_url" 2>/dev/null || true)
    http_code=$(printf '%s' "$response" | awk '{print $1}')
    effective_url=$(printf '%s' "$response" | cut -d' ' -f2-)
    if [ "$http_code" = "200" ] && [ -s "$output_file" ]; then
      break
    fi
    attempt=$((attempt + 1))
    sleep 1
  done
  python3 - "$status_file" "${http_code:-000}" "${effective_url:-}" "$attempt" <<'PY'
import json, sys
json.dump({"http_code": sys.argv[2], "effective_url": sys.argv[3], "attempts": min(int(sys.argv[4]), 2)}, open(sys.argv[1], "w"))
PY
  [ "$http_code" = "200" ] && [ -s "$output_file" ] || return 1
  python3 "$CHECKER" "$output_file" "$engine_name" --base-url "${effective_url:-$engine_url}" --json-out "${output_file%.html}.check.json"
}

unique_engines() {
  python3 - "$@" <<'PY'
import sys
seen = set()
for engine in sys.argv[1:]:
    name = engine.split("|", 1)[0]
    if name not in seen:
        seen.add(name)
        print(engine)
PY
}

load_engines() {
  ENGINES=()
  while IFS= read -r line; do
    [ -n "$line" ] && ENGINES+=("$line")
  done < <(unique_engines "$@")
}

case "$MODE" in
  cn)   load_engines "${ENGINES_CN[@]}" "${ENGINES_GENERAL[@]:0:2}" ;;
  news) load_engines "${ENGINES_NEWS[@]}" "${ENGINES_GENERAL[@]:0:2}" ;;
  *)    load_engines "${ENGINES_GENERAL[@]}" ;;
esac

echo "🔍 Search Swarm (fallback layer): '$QUERY'"
echo "🧩 Platform: $PLATFORM"
echo "📊 Mode: $MODE"
echo "🌐 Engines: ${#ENGINES[@]}"
echo "📁 Results: $RESULTS_DIR"
echo ""

SUCCESS_COUNT=0
FAIL_COUNT=0
for engine_def in "${ENGINES[@]}"; do
  ENGINE_NAME="${engine_def%%|*}"
  ENGINE_URL="${engine_def#*|}"
  echo -n "  🚀 $ENGINE_NAME ... "
  case "$ENGINE_NAME" in
    bing*) sleep 2 ;;
    *) sleep 1 ;;
  esac
  HTML_FILE="$RESULTS_DIR/${ENGINE_NAME}.html"
  STATUS_FILE="$RESULTS_DIR/${ENGINE_NAME}.json"
  if fetch_engine "$ENGINE_NAME" "$ENGINE_URL" "$HTML_FILE" "$STATUS_FILE"; then
    LINKS=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["result_links"])' "$RESULTS_DIR/${ENGINE_NAME}.check.json")
    echo "✅ ($LINKS result links)"
    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
  else
    REASON=$(python3 - "$STATUS_FILE" "$RESULTS_DIR/${ENGINE_NAME}.check.json" <<'PY'
import json, os, sys
status = json.load(open(sys.argv[1]))
if os.path.exists(sys.argv[2]):
    print(json.load(open(sys.argv[2])).get("reason", "invalid page"))
else:
    print("HTTP " + str(status.get("http_code", "000")))
PY
)
    echo "❌ ($REASON)"
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
done

python3 - "$RESULTS_DIR" "$QUERY" "$PLATFORM" "$MODE" "${#ENGINES[@]}" "$SUCCESS_COUNT" "$FAIL_COUNT" <<'PY'
import json, sys, time
from pathlib import Path
results_dir, query, platform, mode, total, ok, fail = sys.argv[1:8]
root = Path(results_dir)
engines, domains, links_total = [], set(), 0
for status_file in sorted(root.glob("*.json")):
    if status_file.name.endswith(".check.json") or status_file.name == "summary.json":
        continue
    name = status_file.stem
    status = json.loads(status_file.read_text())
    check_file = root / (name + ".check.json")
    check = json.loads(check_file.read_text()) if check_file.exists() else {}
    valid = bool(check.get("valid"))
    if valid:
        links_total += int(check.get("result_links", 0))
        domains.update(check.get("domains", []))
    engines.append({
        "name": name,
        "http_code": status.get("http_code"),
        "valid": valid,
        "reason": check.get("reason") or ("HTTP " + str(status.get("http_code"))),
        "result_links": int(check.get("result_links", 0)) if valid else 0,
    })
summary = {
    "query": query,
    "platform": platform,
    "mode": mode,
    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "engines_total": int(total),
    "engines_success": int(ok),
    "engines_fail": int(fail),
    "result_links_total": links_total,
    "domains": sorted(domains),
    "engines": engines,
    "results_dir": results_dir,
    "note": "Result links are unverified candidates. Open the pages before citing anything.",
}
(root / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY

echo ""
echo "📈 Results:"
echo "  ✅ Valid result pages: $SUCCESS_COUNT"
echo "  ❌ Failed or blocked: $FAIL_COUNT"
echo "  📂 Output: $RESULTS_DIR/"
echo ""
echo "✅ Swarm search complete (candidates only — verify before citing)"
