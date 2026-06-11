# 2026-03-25 15:36 UTC — Rank 164 survivor follow-up：三腿真实执行口径后直接 drop_to_background

## 本轮执行的小点
- target: Surviving candidate slot
- action: 对 `Rank 164 / ALTBTC synthetic-cross parity mean reversion` 执行那唯一一次 decisive follow-up，只回答三腿真实执行口径下 `best bid/ask + 三腿 round-trip 成本 + 残余 BTC 暴露` 后是否仍值得升 `P2`
- success_criterion: 在 `promote_P2` 与 `drop_to_background` 之间给出单一诚实 verdict，并把唯一 follow-up 预算收口

## 这次只看一个问题
- fresh intake 首判已经证明：`ALTBTC` 挂牌价 vs 合成价的 parity spread **会回归**。
- 这次不再补论文、不再扩 symbol，只检查：**close-based 回归幅度，能不能穿过 current best bid/ask 的三腿可成交成本地板。**

## 使用的数据
- 历史 gross 代理：沿用 `reports/artifacts/quant_digests/synthetic_cross_parity_altbtc_20260325_1350/summary.json` 中的 `next3_revert_bps (5m)` 与 `next1_revert_bps (15m)`，取每个 symbol 更乐观的一侧作为 gross 上界。
- current quote 成本：Binance Spot `bookTicker`，抓取时间 `2026-03-25 15:42 UTC`。
- 成本口径：
  1. **spread-only floor** = `ALTBTC + ALTUSDT + BTCUSDT` 三腿各自一整次 bid/ask round-trip；
  2. **spread + 45bps** = 给 `7.5bps × 6 trades` 的偏乐观 BNB-discount taker 费率下界；
  3. **spread + 60bps** = 给 `10bps × 6 trades` 的普通 spot taker 费率。
- 若连 `spread-only floor` 都过不去，说明 kline 上看到的偏离大概率只是 tick / quote band，不是可成交 edge；若只剩 `1~3bps` 边际，则任意手续费、排队失败或残余 BTC 暴露都足以把它翻负。

## 核心结果（bps）

| symbol | gross上界 | ALTBTC spread | ALTUSDT spread | BTCUSDT spread | 三腿spread地板 | gross-spread | gross-(spread+45) | gross-(spread+60) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| DOGEBTC | 57.43 | 73.80 | 1.04 | 0.00 | 74.85 | -17.42 | -62.42 | -77.42 |
| ADABTC | 29.64 | 26.28 | 3.71 | 0.00 | 30.00 | -0.35 | -45.35 | -60.35 |
| LTCBTC | 17.99 | 12.67 | 1.79 | 0.00 | 14.46 | 3.53 | -41.47 | -56.47 |
| XRPBTC | 7.32 | 5.04 | 0.71 | 0.00 | 5.75 | 1.56 | -43.44 | -58.44 |
| ETHBTC | 4.64 | 3.28 | 0.05 | 0.00 | 3.33 | 1.31 | -43.69 | -58.69 |

## 读法
- **DOGEBTC**：历史最好看的 gross 回归上界约 `57.43 bps`，但仅 direct cross 自己的一跳 spread 就有 `73.80 bps`；三腿 spread 地板合计 `74.85 bps`，说明 close-based “厚偏离” 本身就被当前 tick/quote band 吃掉了。
- **ADABTC**：最好 gross 上界 `29.64 bps`，而三腿 spread 地板 `29.99 bps`，已经在**不算任何手续费**时转负。
- **LTCBTC / XRPBTC / ETHBTC**：spread-only 还勉强剩 `0.18~3.52 bps`，但这点残差远小于任意现实手续费；一旦加上最偏乐观的 `45 bps` fee floor，全部直接转成 `-41~-45 bps`。
- 上面还**没有**计入三腿异步成交带来的残余 `BTC` 暴露、盘口排队失败、跨档成交和最小成交量约束；这些只会让结果更差，不会更好。

## 诚实 verdict
**`Rank 164 / ALTBTC synthetic-cross parity mean reversion` 本轮应直接 `drop_to_background`，不升 `P2`。**

原因不是 “parity spread 不回归”，而是更关键的交易性问题已经被回答：
1. 厚尾 `ALTBTC` 交叉在 close-based K 线里看到的 gross 偏离，和 current tick/bid-ask band 同量级，甚至更小；
2. 较薄的 `ETH/XRP/LTC` 虽然统计上会回，但留给真钱的毛边只有几 bps，远不足以覆盖三腿费用与残余腿风险；
3. 因此这条线当前更像“microstructure / quote-band 现象素材”，还不够诚实地进入 `P2 admission`。

## 本轮回写要点
- `Surviving candidate slot`：清空，并把 `followup_budget_remaining` 收口为已使用
- `Fresh intake slot`：释放前排，改为 `ready_for_new_intake / current_target: none`
- `Background pool.latest_parked`：更新为 `Rank 164`
- `cycle_plan[3]`：
  - `result` = `Rank 164 / ALTBTC synthetic-cross parity mean reversion` 的厚尾 close-based 偏离与 current 三腿 bid/ask 地板同量级，加入任何现实手续费与残余 BTC 暴露后净边都会转负，因此 survivor follow-up 直接收口为 `drop_to_background`，不升 `P2`。
  - `status` = `done`

## 一句话结论
`Rank 164 / ALTBTC synthetic-cross parity mean reversion` 作为 raw alpha 想法是成立的，但它在 current top-of-book 三腿可成交口径下并没有穿过真钱成本线；这说明前面看到的“厚偏离”主要停留在 quote band，而不是足以推进到 `P2` 的可交易 edge。
