# Rank 363 / HTF EMA gate × 15m RSI pullback continuation / fresh intake keep_P1

- 时间：2026-04-08 04:30 UTC
- 执行轮次：bot3 13m auto
- 对象：`research/quant_digests/2026-04-08_0405_htf-ema-rsi-pullback-trend-shell.md`
- 结论：`keep_P1`
- 正式 Rank：`363`

## 本轮只回答的问题
这条对象是否已经形成一条可审计、可单独命名的 raw alpha intake，而不是把常见的 EMA/RSI/MACD 指标堆叠教程误当成前排候选。

## 最小核对
我只做了 intake 所需的最小交叉核对：
1. 该 digest 的主语已经收口为 `HTF EMA200 regime gate -> LTF shallow pullback continuation`，不是“很多指标一起确认趋势”的泛教程；
2. 过滤层和 raw alpha 主体能分层：
   - raw alpha 主体是 `1h/4h 趋势已成立后，15m 小回踩恢复继续顺势`；
   - `RSI 40~65`、`close < BB mid`、`MACD > signal` 更像 entry 压缩和追高 veto，而不是另一条独立 alpha；
3. digest 已给出最小可复刻实验壳：标的、周期、gate、entry、可选确认、ATR 出场和 `8~10 bps` 成本口径都已写清，说明它不是只停留在 README 叙事。

## 为什么这轮不给 P2
它足够成为正式 intake，但还没到 P2 admission：
1. 现有证据主要是源码/工程规则，不是 clean-room replication；
2. 还没证明 post-cost edge 真来自“浅回踩恢复”，而不是靠 trend beta 或少量大波段收益硬抬出来；
3. 还没完成最关键的剥皮：`HTF gate only -> +EMA9/21 -> +RSI zone -> +MACD -> +BB mid`，因此目前不能诚实回答哪些过滤层真在增益、哪些只是把交易次数压低。

## 本轮 verdict
`HTF EMA gate × 15m RSI pullback continuation` 已经形成可审计的顺势 raw alpha skeleton：主体是高周期趋势成立后的低周期浅回踩 continuation，确认层与风险壳也能和 alpha 本体分开描述，因此本轮给予正式 `Rank 363` 并首判 `keep_P1`；后续唯一 survivor follow-up 应只回答在统一成本与统一样本下，这条 continuation 在 majors perp 上是否仍保留可迁移的 post-cost expectancy，以及增益究竟来自 `HTF gate` 本体还是来自 `RSI/BB/MACD` 这些 entry 压缩层。