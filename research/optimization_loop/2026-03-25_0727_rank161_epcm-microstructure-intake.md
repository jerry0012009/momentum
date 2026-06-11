# Rank 161 intake — EPCM microstructure taker alpha 进入 P1

- 时间：2026-03-25 07:27 UTC
- 对象：Rank 161 / EPCM microstructure taker alpha
- 别名：Explainable Patterns in Cryptocurrency Microstructure / `amazingchow/epcm`
- 来源摘要：`research/quant_digests/2026-03-25_0318_single-asset-microstructure-taker-alpha.md`
- 本轮动作：fresh intake 最小公开证据 + 本地快检收口，只回答 `park / keep_P1`
- 本轮结论：`keep_P1`

## 为什么这轮不是直接 park
这条线和常见“把盘口特征当解释变量”的材料不一样，它已经具备一个可以独立验证的完整 raw alpha 骨架：

1. **base alpha 明确**：`OFI + depth imbalance + VWAP pressure (+ spread)` 直接预测未来 `3s` 收益方向，而不是模糊地“辅助择时”。
2. **执行形态明确**：超过阈值就按预测方向立即吃单，退出也有自然定义（反向/阈值回落/最大持有秒数）。
3. **公开证据不是单点故事**：论文覆盖多币、给出 taker/maker 区分与极端行情表现；同名 repo 提供了可复现工程路径。
4. **本地快检没有把方向性打没**：digest 里用 Binance 公共 `bookTicker + trades` 的最小 proxy，在 `ROSEUSDT / ENJUSDT` 的未来 `3s` 收益上仍能看到显著方向信息，说明至少值得留一次 survivor follow-up，而不是 intake 当场否决。

## 为什么这轮也不直接升 P2
当前证据仍然只够说明“**有可验证的 microstructure directional edge 线索**”，还不够说明“**成本后、跨币、跨日都足以进 pre-paper admission**”。

最关键的未决点只有一个：

> **在 desk 可接受的 taker friction 与可交易触发密度下，这条 `3s` 事件驱动 alpha 是否还能留下稳定为正的 `post-cost avg bps/event`？**

如果这个问题答不出来，继续往 P2 推会太早。

## 单一 decisive blocker（供下一次 survivor follow-up 使用）
只做一件事：

- 用公开 Binance Futures 原始数据，先在 `BTC / ETH / 1 个中小币` 上做最小滚动快检；
- 固定 paper 原生特征，不扩模型；
- 只扫 `hold_seconds × threshold × cost ladder`；
- 收口指标只看：`events/day`、`avg bps/event`、`post-cost avg bps/event`。

允许的下一步 verdict 只有两个：
- 若成本后仍有稳定正 pocket：`promote_P2`
- 若成本后优势被吃光或只剩不可交易的稀薄事件：`drop_to_background`

## 本轮写回 runtime 的一句话
`Rank 161 / EPCM microstructure taker alpha` 具备明确的单资产事件驱动 raw alpha 骨架，且本地最小快检仍看到未来 `3s` 方向信息，因此 intake 不直接 park，而是进入 `keep_P1`，把唯一一次 follow-up 收口到“成本后是否还剩稳定正的 `post-cost avg bps/event` pocket”。
