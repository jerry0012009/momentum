# Hegic quote-benchmark mispricing alpha — fresh intake first verdict：不进入 P1，直接 background/P0

- 时间：2026-04-13 05:24 UTC
- 执行器：bot3
- 对象：`research/quant_digests/2026-04-13_0508_hegic-quote-benchmark-mispricing-alpha.md`
- 对应小点：`cycle_plan #1`

## 本轮执行（仅此一个小点）
按 `fresh intake first-verdict` 要求完成两件事：
1) 最小费后可交易性判定（统一成本口径）
2) 1 条 honesty / execution realism 子检查（可成交性代理 + 延迟/滑点对齐）

## 最小判定口径
使用 digest 已给出的最小交易壳，不扩展为第二个小点：
- 信号：`score = (model_price - executable_option_ask) / underlying_mid`
- 候选入场阈值：`30 / 60 / 100 bps`（digest 建议）
- 统一成本：链上 option 交易费+gas + 对冲腿 round-trip 滑点/手续费 + 对冲持有 carry

结论不是“论文有没有统计显著”，而是：
**在当前 runtime 证据下，尚无可验证的 `executable_option_ask` 与延迟对齐成交链路，无法把 residual 从“paper quote”转成“可成交净边际”；因此不能证明费后净边际为正。**

## honesty / execution realism（最小子检查）
针对本小点只做 1 条最小检查：
- 检查点：是否已有可复用的、时间对齐的执行证据（on-chain option quote 时间戳/可成交价 + hedge 腿成交价 + gas）可用于构造 `edge_after_cost`
- 结果：当前项目内无该对象的执行级 artifact（仅有论文/digest 叙述），无法排除 `stale quote / fill mismatch / leg desync` 对 residual 的吞噬。

该检查直接影响 verdict，且是当前唯一 decisive blocker。

## first verdict
`background/P0`（不保留为 `keep_P1`）。

## 会改变系统认知的一句话
`hegic quote-benchmark mispricing alpha` 在 fresh intake 轮被直接收口到 `background/P0`：当前缺少时间对齐的可成交价与成本实测链路，唯一 decisive blocker 为 `edge_after_cost` 无法被执行级证据成立。

## blocker
- decisive blocker：`missing execution-grade executable quote + latency-aligned hedge fills -> edge_after_cost not provable`
- 动作：`fresh intake -> background/P0`
