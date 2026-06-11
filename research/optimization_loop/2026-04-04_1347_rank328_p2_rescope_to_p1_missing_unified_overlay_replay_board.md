# bot3 optimization loop — Rank 328 P2 admission exits via one-time P2 -> P1 re-scope

- Time: 2026-04-04 13:47 UTC
- Target: `Rank 328 / water-filling leverage equalization × factor-adjusted deleveraging shared risk overlay`
- Action: execute the first `Active P2` admission round, prioritizing `effectiveness / expected return` and `cross-asset stability`
- Verdict: `one-time P2 -> P1 re-scope`

## What was checked
本轮没有再复述 paper 叙事，而是直接核对当前 repo 里能否诚实支撑这条 overlay 的 admission：

1. **现有运行态是否已经有可复用的 sleeve/account state**
   - `reports/artifacts/paper_rank154_crypto_stat_arb_runner/rank154_paper_state.json`：有 `current_equity` 与 25 个 symbol 级 `positions`，但仓位字段主要是 `entry_price / quantity / weight`；
   - `reports/artifacts/rank32b_shadow_global_winner/paper_open_positions.json`：有单笔 shadow 持仓的 `order_notional_usdt / mark / spread / impact / timeout`；
   - `reports/artifacts/paper_rank229_eth_abnormal_day/rank229_state.json`、`paper_rank213_largecap_xs_jump_veto/rank213_state.json`、`paper_rank200_btc_weekday_hour_sparse_short/rank200_state.json`、`paper_rank201_utc_clock_low_switch/rank201_state.json`、`paper_rank183_cbeth_eth_basis/rank183_state.json`：都证明 repo 里确实存在多个 paper runner state，但字段口径各异。

2. **repo 里是否已经有 Rank 328 对应的 replay board / runner / metric artifact**
   - 以 `rank328 / waterfill / factor_adjusted / deleverag` 为文件名搜索，只找到：
     - 原 digest；
     - `11:59` first verdict 日志；
     - `12:12` survivor->P2 日志；
     - 已发布 digest 页面；
   - **没有**找到 dedicated overlay replay runner、统一 replay board、或任何 `tail shortfall / forced-close turnover / hedge false-positive cuts` 的实际 artifact。

## Why this fails honest P2 admission right now
`Rank 328` 当前的 P2 admission 要回答的是：
- factor-adjusted 版本是否在多个 sleeve 组合上留下清楚 overlay edge；
- 这种 edge 是否跨资产稳定，而不是只在单一 pocket 成立。

但现有 repo 只能证明“有若干 runner state 可供未来挂接”，**还不能证明这些状态已经被统一成同一张多 sleeve replay board**。当前最关键的缺口不是更多理论维度，而是一个单一、明确、会决定 admission 能否成立的 blocker：

> **缺少统一的 overlay replay board/schema。**

具体说：
- `rank154` 的 cross-sectional paper state 提供组合权重，但没有和其他 runner 共用的 `beta / factor-adjusted leverage / expected edge` 板；
- `rank32b` 的 shadow state 更像单笔执行壳，不是多 sleeve risk board；
- `rank229 / 213 / 200 / 201 / 183` 等 runner 各自独立运行，尚未暴露成同一套可对比的 deleveraging 输入矩阵；
- 因此现在继续把它留在 `Active P2`，会变成“先假设 board 未来会出现，再讨论 admission 指标”，这不符合 policy 要求的诚实收口。

## Why the correct exit is re-scope, not P3 and not P0
- **不是 `promote_P3`**：因为还没有任何真实 replay 结果能证明它在多个可挂接 sleeve 上留下可复现 edge；
- **不是 `drop_to_background/P0`**：因为对象没有致命 flaw，paper 与 desk shell 仍然成立；
- **而是一次明确的 `P2 -> P1 re-scope`**：把对象从“泛化 multi-sleeve factor-adjusted overlay admission”收窄成“先做一个统一 replay board/schema，再用同一 schema 跑 gross vs factor-adjusted 的第一版 board-level 对照”。

这个 re-scope 方向是唯一明确的：**不是再补一个 admission 维度，而是先把 admission 的统一输入板搭出来。**

## Runtime conclusion
`Rank 328` 本轮 `Active P2` admission 第一轮已诚实收口：当前 repo 虽然已经有多个可挂接的 paper/shadow state artifact，但它们尚未形成一张统一的 multi-sleeve overlay replay board，因此还不能诚实回答 `effectiveness / cross-asset stability`；这构成单一 decisive blocker。故本轮不再开放式 `keep_P2`，而是将 `Rank 328` 做 **one-time `P2 -> P1 re-scope`**：从泛化 shared overlay admission 收窄为“先统一 deleveraging replay schema/board，再重开验证”，并退出 `Active P2` 前排槽位。