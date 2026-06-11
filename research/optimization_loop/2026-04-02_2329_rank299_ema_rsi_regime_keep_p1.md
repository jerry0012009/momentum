# Rank 299 — EMA(RSI) regime hierarchy trend alpha：fresh intake first verdict = keep_P1

- 时间：2026-04-02 23:29 UTC
- 对象：`research/quant_digests/2026-04-02_2214_ema-rsi-regime-hierarchy-trend-alpha.md`
- 执行动作：fresh intake first verdict
- 结论：`Rank 299 / keep_P1`

## 为什么不是直接进 P2
这条对象的 raw-alpha 主语是清楚的：**单资产趋势跟随 + EMA(RSI) regime gate + uptrend-only entry permission + state/PSAR-style protective exit**。它不是纯 overlay，也不是只能解释收益的论文包装；entry / exit / state-machine / public-data clean-room 路径都已经够完整，值得保留到前排。

但它现在还不该直接进 `P2`，原因也同样明确：

1. **当前证据主体仍是日频、单资产、long-flat BTC paper**，还没有 short-cycle clean-room 结果。
2. 最关键的 desk 命题其实不是 headline gross，而是：
   - `EMA(RSI)>60` 这类 regime gate 在 `15m/5m` 上是否真能稳定减少 fee drag 和 drawdown；
   - `EMA7(RSI)` 是否稳健优于 `EMA9(RSI)`；
   - `uptrend-only` 是否只是把交易次数砍少，还是确实留下了成本后可存活的 trend sleeve。
3. 论文内的 `fluctuating` 支路与 `PSAR` 保护逻辑都还停留在 paper 描述层，尚未证明在 perp/短周期上能维持 honest net edge。

## 为什么仍然值得 keep_P1
它满足保留到 survivor 的几个关键条件：

1. **独立 raw-alpha 主语明确**：不是“再加个指标更安全”，而是把 `EMA(RSI)` 用作市场结构分类器，只在 `uptrend` 放行趋势入场。
2. **clean-room 可迁移路径明确**：只需要公开 OHLCV，就能先在 BTC `15m` 做最小实验，再下钻到 `5m/3m`；不依赖私有数据或复杂执行基础设施。
3. **与现有素材池互补**：这轮前排多数是 pairs / carry / stat-arb / cross-sectional 家族，它补的是轻量级单资产 trend shell。
4. **后续唯一 survivor follow-up 很具体**：直接回答 regime gate 对 short-cycle trend sleeve 的净增益是否成立，而不是开放式继续读 paper。

## runtime 影响
- 分配新正式身份：`Rank 299`
- fresh intake first verdict：`keep_P1`
- 进入 `Surviving candidate slot`
- `followup_budget_remaining = 1`

## 下一步唯一合法 survivor follow-up（供 bot2 下轮决定是否继续排）
在高流动 BTC perp clean-room 上做最小 decisive follow-up：比较裸 `EMA9/20` 趋势 vs `EMA9/20 + EMA7(RSI)>60` uptrend gate（必要时加 `PSAR` 保护退场），看 `15m/5m` 下一到四根持有下是否出现**成本后更诚实的净趋势 sleeve**；若没有，就应在 survivor 轮直接收口回 `background/P0`。
