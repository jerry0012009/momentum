# 2026-03-31 00:49 UTC — Rank 264 survivor follow-up：perp / confirm / veto 口径后回 background/P0

## 本轮执行的小点
- target: `Rank 264 / QQQ-NVDA lead-lag × crypto 15m spillover`
- action: 作为当前唯一合法前排 survivor，只执行这一次 decisive follow-up，直接回答 `QQQ / NVDA 5m downside shock -> ETH / BTC future 15m follow-down` 在 perp / live-feasible 口径、显式 taker/slippage 成本与 `QQQ-only / NVDA-only / confirm / crypto veto` 规则下，是否还保留足够可重复的成本后 pocket
- success_criterion: 在 `promote_P2` 与 `回 background/P0` 之间给出单一出口 verdict，并把 survivor 唯一 follow-up 预算收口

## 这次实际做了什么
只做了这一次 follow-up，不扩新 intake、不重排其余 cycle plan：
1. 用 Yahoo Finance Chart API 重抓 `QQQ`、`NVDA` 的 regular-session `5m` bar；
2. 用 Binance USDⓈ-M Futures 公共 `5m` K 线重抓 `BTCUSDT`、`ETHUSDT`；
3. 在最近 `60d` 的重叠样本上，对齐 shared `5m` 时间戳；
4. 按 `leader 当前 5m shock -> next crypto bar 入场 -> 持有 15m` 的代理口径，分别评估：
   - `QQQ-only downside`
   - `NVDA-only downside`
   - `QQQ + NVDA confirm downside`
   - `QQQ + NVDA confirm + target-local crypto veto`
5. 显式扣除保守 round-trip 成本：`BTC = 8 bps`，`ETH = 10 bps`。

## Artifact
- `reports/artifacts/optimization_loop/rank264_survivor_followup_20260331/same_clock_perp_short_summary.csv`
- `reports/artifacts/optimization_loop/rank264_survivor_followup_20260331/fullsample_threshold_sanity.csv`
- `reports/artifacts/optimization_loop/rank264_survivor_followup_20260331/meta.json`

## 核心结果（same-clock / perp / next-bar execution）

| asset | rule | events | gross mean (bps) | net mean (bps) | gross hit-rate | net hit-rate |
|---|---|---:|---:|---:|---:|---:|
| BTC | QQQ-only downside | 404 | -0.08 | -8.08 | 47.28% | 37.62% |
| BTC | NVDA-only downside | 381 | 0.57 | -7.43 | 49.08% | 39.37% |
| BTC | QQQ+NVDA confirm downside | 230 | 3.09 | -4.91 | 47.83% | 38.70% |
| BTC | confirm + crypto veto | 96 | 3.00 | -5.00 | 47.92% | 40.62% |
| ETH | QQQ-only downside | 404 | -0.73 | -10.73 | 46.78% | 36.88% |
| ETH | NVDA-only downside | 381 | -1.10 | -11.10 | 49.87% | 39.11% |
| ETH | QQQ+NVDA confirm downside | 230 | 2.23 | -7.77 | 48.70% | 39.13% |
| ETH | confirm + crypto veto | 93 | 0.91 | -9.09 | 51.61% | 39.78% |

### 读法
- 若按更诚实的 **same-clock rolling percentile + Binance perp + next-bar 15m hold** 口径，`Rank 264` 最好的版本也只是：
  - BTC：`QQQ+NVDA confirm downside`，gross 约 `+3.09 bps`；
  - ETH：`QQQ+NVDA confirm downside`，gross 约 `+2.23 bps`。
- 这离可交易的 `8~10 bps` round-trip 成本线还差很远；扣成本后所有版本都转成明显负值。
- 加 `crypto veto` 并没有把 pocket 救活：事件数显著下降，但 net edge 仍然没转正。
- 换句话说，原 intake 里看到的“QQQ downside -> ETH/BTC 15m follow-down”更像 **spot-like / transfer check 上的弱方向感**，而不是已经穿过 perp execution 地板的可 admission 口袋。

## sanity cross-check（更接近原 digest 的 full-sample tail）
为了确认不是 `same-clock` 规范化把结果“压死”，我又补看了更接近原 digest 的 full-sample downside tail：

- BTC / `QQQ_down_fullsample`: gross `-1.43 bps`
- BTC / `NVDA_down_fullsample`: gross `-0.60 bps`
- BTC / `QQQ+NVDA_confirm_down_fullsample`: gross `+0.65 bps`
- ETH / `QQQ_down_fullsample`: gross `-0.26 bps`
- ETH / `NVDA_down_fullsample`: gross `+0.95 bps`
- ETH / `QQQ+NVDA_confirm_down_fullsample`: gross `+3.86 bps`

即使退回更宽松的 full-sample tail 读法，gross 也仍然只有 `0.65~3.86 bps` 量级，依旧远低于诚实的 perp 成本门槛。

## 诚实 verdict
**`Rank 264 / QQQ-NVDA lead-lag × crypto 15m spillover` 的 survivor 唯一 follow-up 已经给出出口结论：不升 `P2`，直接回 `background/P0`。**

原因不是这篇 paper 完全没价值，而是更关键的交易性问题已经被回答：
1. 把对象锁定到最值钱的窄主语——`QQQ/NVDA downside 5m shock -> BTC/ETH next 15m follow-down`——之后，gross 只剩几 bps；
2. 这些 gross 幅度在 Binance perp 的 next-bar execution + round-trip 成本下全部不够；
3. `QQQ-only / NVDA-only / confirm / crypto veto` 都没有把它抬到可以诚实进入 `P2 admission` 的水平；
4. 因此这条线当前更像“值得保留论文启发，但 desk 版本尚未通过真钱门槛”的 background 证据，而不是应继续前排占资源的 survivor。

## 本轮回写要点
- `Surviving candidate slot`：清空，`followup_budget_remaining` 收口为 `0`
- `Fresh intake slot`：释放前排，改为 `ready_for_new_intake / current_target: none`
- `Background pool.latest_parked`：更新为 `Rank 264`
- `cycle_plan[1]`：
  - `result` = `Rank 264：唯一 survivor follow-up 完成；QQQ/NVDA 5m downside shock 在 Binance perp 的 next-bar 15m 口径下，即使加双 leader confirm 与 crypto veto，BTC/ETH 平均 gross 也只剩约 3.09/2.23 bps、扣 8~10 bps 成本后全为负，因此不够支撑 P2，预算用尽后回 background/P0。`
  - `status` = `done`

## 一句话结论
`Rank 264` 的 raw alpha 主语并没有被证明“毫无方向感”，但一旦切到更诚实的 Binance perp / next-bar / costed execution 口径，它就没有穿过真钱门槛；因此这次 survivor follow-up 应直接收口为 `background/P0`，而不是继续拖成开放式研究。
