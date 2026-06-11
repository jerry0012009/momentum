# 2026-04-10 02:10 UTC — intraday lagged-return horizon router first verdict

## 本轮对象
- target: `research/quant_digests/2026-04-10_0047_intraday-momentum-reversal-crypto-router.md`
- slot: `Fresh intake`
- action: 判断 `5m ultra-short continuation + post-jump 1h fade` 是否构成独立于既有短周期 `horizon-router / jump-fade / continuation` 家族的新 raw alpha 主语

## 结论
`intraday lagged-return horizon router` 当前不构成新的独立 fresh intake：它最强的信息增量仍是“同一 lagged-return sign 在不同 horizon / jump / liquidity 状态下要切 continuation 或 fade”，本质更像既有短周期 `horizon-router / shock-jump / continuation-vs-reversal` 家族的 admission 路由经验，而不是新的 queue-facing raw alpha 主语，因此本轮诚实收口为 `background / P0`，不分配新 Rank。

## 为什么不 keep_P1
1. **独立主语不够硬**：对象自己最值钱的翻译是 `5m ultra-short continuation` 和 `post-jump 1h fade` 两个 sleeve 的 horizon router，而不是一条新的单独 alpha。`same lagged-return sign, different horizon -> different action` 这件事与现有 `intraday-horizon-router-cubic`、`asymmetric-shock-horizon-router`、多条 jump / fade / continuation intake 已高度同族。
2. **新增证据仍停留在 router/veto，而不是独立交易书**：digest 里的本地 probe 已明确写出 `5m` continuation 约 `+0.29 bps/bar`、`1h sign` future-4-bar 约 `-0.18 bps`、`jump + high-liquidity` bucket 约 `-2.09 bps`；这更像告诉 desk “什么时候别追、什么时候切反手”，而不是证明 `always-momentum` 或 `always-fade` 之外出现了能独立站住、after-cost 明显存活的新书。
3. **单一 decisive blocker 已经暴露在成本/执行层**：作者自己已经承认 `5m` edge 偏小、若全吃 taker 很多版本会被成本吞掉，因此更合理的位置是 `router / veto / sleeve selector`。在这种前提下，把它作为独立 fresh intake 往前排推进，等于默认忽略了最关键的 post-cost honesty 问题。
4. **与现有前史重复度过高**：仓库里已有 `2026-04-04_2132_intraday-horizon-router-cubic-alpha.md`、`2026-04-08_1729_asymmetric-shock-horizon-router-alpha.md`，以及多条 jump / reversal / short-cycle continuation 线；本对象没有给出足以和这些旧对象切开的新的 execution shell、资产边界或 after-cost pocket。

## Minimal evidence used
- 目标 digest 中的 paper metadata + Binance USDⓈ-M `5m` portability probe。
- 现有 family overlap 核对：`intraday-horizon-router-cubic`、`asymmetric-shock-horizon-router`、若干 jump / continuation / reversal digest 与对应 optimization logs。

## Runtime writeback
- `Fresh intake slot.latest_result` 更新为本对象 `background / P0` 收口。
- `Fresh intake slot.current_target` 前移到下一条：`research/quant_digests/2026-04-09_2235_anchor-open-vwap-sigma-continuation-alpha.md`。
- `Background pool.latest_parked` 更新为本对象。
- `cycle_plan` 第 2 项状态更新为 `done`。

## 本轮一句话 result
`intraday lagged-return horizon router` 没有形成独立于既有短周期 `horizon-router / shock-jump / continuation-vs-reversal` 家族的新 raw alpha 主语，且最关键 post-cost 结论已经指向“更适合作为 router/veto 而非独立交易书”，因此 fresh intake 首判直接收口为 `background / P0`。
