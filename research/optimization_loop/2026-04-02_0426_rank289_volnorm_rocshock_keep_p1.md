# Rank 289 — vol-normalized ROC shock × EMA displacement × volume confirmation — first verdict keep_P1

- 时间：2026-04-02 04:26 UTC
- 对象：`research/quant_digests/2026-04-02_0344_volnorm-rocshock-ema-volume-alpha.md`
- 结论：`keep_P1`
- Rank：`289`

## 本轮执行的小点
按 `cycle_plan` 第一个 pending 小点，对这条 `volnorm roc-shock EMA volume` fresh intake 做 first verdict，不补做下一条 intake，也不重排后续队列。

## 为什么这轮不是 P0
这条对象已经不是“ROC/EMA/volume 指标拼装”层面的空故事，而是一个可独立审计的 directional raw alpha skeleton：

1. **alpha 主语清楚**：核心不是均线本身，而是 `ROC > k × rolling_std(ROC)` 的异常收益冲击延续；
2. **admission layer 清楚**：`price vs EMA`、`EMA displacement`、`volume > volume_MA`、`ROC acceleration` 都已经写成明确条件；
3. **exit shell 清楚**：`EMA cross-back` + `trailing stop`，不是只靠固定持有期；
4. **research shell 清楚**：源码已经给出 `6m train / 3m test / 3m step` 的 walk-forward 外壳；
5. **transfer path 清楚**：公开 `Binance 1m -> 15m` 数据即可做最小 clean-room 复刻，不依赖私有数据。

因此它满足 fresh intake 首判进入研究前排的最低条件，不能直接打回 background/P0。

## 为什么这轮也不直升 P2
当前证据仍主要停留在 repo/source audit，离 `P2 admission` 还差一段诚实验证：

1. **distinctness 够用但还未被 clean-room 证明**：它比“裸 TSMOM / breakout + volume gate”更像 `vol-normalized shock continuation`，但还没做 shock-only / +EMA / +volume / +displacement 的 ablation，尚不能证明 edge 真的来自这条新骨架而不是旧 trend family 换皮；
2. **成本口径明显偏薄**：repo 只按约 `4 bps` round-trip 计费，没覆盖更厚的 `10~30 bps` desk 口径；
3. **跨资产稳定性未知**：当前 repo 主要围绕 `BTCUSDT`，还没证明 ETH / SOL / BNB 甚至 BTC 本身在去优化版参数下仍留下 after-cost pocket；
4. **参数搜索先于 existence**：源码强调 WFO + Optuna，但我们自己的 first admission 还没先回答“去优化版是否存在稳定毛边/净边”。

所以本轮最诚实的 first verdict 是：**给正式 Rank，记为 `keep_P1`，保留一次 survivor follow-up；不直接升 `P2`。**

## 本轮改变系统认知的话
`Rank 289` 首判完成：这条 2026 repo 并非旧 breakout/TSMOM 换名，而是具备清晰 signal / admission / exit / data-transfer path 的 `vol-normalized shock continuation` raw alpha skeleton；但当前证据仍停留在单 repo source audit 与偏薄成本壳，尚未完成去优化 clean-room existence、ablation 与厚成本跨资产诚实线，因此本轮记为 `keep_P1`，进入 survivor 槽位，不直升 `P2`。

## 下一步唯一合法 survivor follow-up（供后续轮次使用，不在本轮执行）
只剩 1 次高杠杆 follow-up：

- 先做 `15m` 去优化 clean-room baseline，比较 `shock only`、`+EMA`、`+EMA+volume`、`+EMA+volume+displacement`；
- 标的至少覆盖 `BTC/ETH/SOL`；
- 成本至少看 `10/20/30 bps`；
- 直接回答 after-cost 下是否仍有可迁移 pocket，以及 edge 是否真来自 `shock continuation skeleton` 而不是旧 trend family。
