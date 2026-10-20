# Deep Search Output Contract (deep-search 5.0)

报告结构是模板，不是段落配额。选择**能完整回答问题的最小形式**。

## Output Forms

### COMPACT

用于窄的事实题、单点核实。

- 直接答案 / 结论
- 关键依据（优先一手来源）
- 必要的限定或不确定性
- 来源

### STANDARD

用于比较题和中等规模的多部分研究。

- 结论
- 按实际子问题组织的分析
- 证据与冲突
- 局限 / 不确定性
- 来源

### FULL

用于范围广、逻辑嵌套深、开放探索、高风险，或用户明确要求完整报告的任务。使用 8 段结构（详见 `references/schemas/report-format.md`）：

1. `执行摘要 / Executive Summary`
2. `研究方法 / Methodology`
3. `全景分析 / Universal Analysis`
4. `实证数据 / Empirical Evidence`
5. `垂直分析 / Domain Analysis`
6. `综合评估 / Synthesis`
7. `行动建议 / Recommendations`
8. `附录 / Appendices`

FULL 报告的顶部元数据：报告标题、生成时间、已核验证据条数、独立来源数、整体置信度及一句理由。

`scripts/strict-run.py` 的审计产物固定使用 FULL 结构，便于机器校验。

## Rules For Every Form

- 不为凑模板写空段；某一段确实不适用时，写一句"不适用：原因"或直接省略（COMPACT/STANDARD）。
- 不为凑字数或段落数扩写简单答案。
- 用户指定的格式优先于默认形式。
- **篇幅变短，证据标准不降低。**

## Required Behavioral Guarantees (all forms)

- 只引用本次运行实际取得的材料，不编造来源
- 证据与推断分开
- 说明局限，不掩盖不确定性
- 置信度要有依据，不用含糊措辞代替
- 会影响结论的冲突写进正文
- 工具失败或降级时如实说明（见 `contracts/runtime-contract.md` 的 Degraded Mode）

## Not Allowed

- 隐藏证据出处
- 用"多数来源"代替冲突分析
- 把搜索引擎数量、数据点数量或段落数量当成质量证明
- 把旧事实当作当前状态陈述
