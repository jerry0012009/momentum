# 2026-03-17 02:54 UTC · Desk Board Review

## 本轮一句话判断

**这轮不是换席，但 `Scout Seat` 的 desk judgment 终于发生了真正有边际价值的变化：`Paper Seat = EMA running paper / waiting_not_due` 继续不变；`Live Seat` 继续保持暂空；但 `Scout Seat` 已不再是纯 `park` 串——`Rank 17 pullback recovery confirmation` 已通过 `clean replication + Light Stability Pack` 并进入 **`paper candidate pool`**，随后又被压成最小 `paper candidate wiring`；与此同时，`Rank 18 EMA neighborhood consensus / plateau-stable crossover` 已进入 **`source intake / clean replication next`**。因此当前 desk 的默认顺序已不该再读成“无脑 fresh intake first”，而应更精确地读成：**`Rank 18 clean replication next；Rank 17 仅在 genuinely verdict-changing check 时继续；Rank 2 只在真实 append/review need 时继续。`**

## 当前 strongest evidence

1. **Paper Seat 继续是真实 waiting_not_due，不需要临时切回 due-followup**
   - `2026-03-17 00:20 UTC` 已实际执行：
     - `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
   - `ema_paper_trading_refresh_history.csv` 已新增：
     - `Crypto 1d+1wk（BTC/ETH/SOL） | Crypto-1d | 2026-03-16 00:00 UTC`
   - 当前累计 completed-bar rows 已增至：`8`
   - 最新 due guardrail 显示：
     - A 股下一次 close：`2026-03-17 07:00 UTC`
     - 美股下一次 close：`2026-03-17 20:00 UTC`
     - Crypto 下一次 close：`2026-03-18 00:00 UTC`
   - 因此当前对 `Paper Seat` 的正确读法仍是：
     - **`running paper pilot / waiting_not_due`**

2. **Live Seat 继续保持暂空**
   - 当前没有任何候选已经走到足以抢占 `Live Seat` 的程度；
   - `Rank 17` 目前只是 `paper candidate pool`，还没到 `narrow paper pilot`；
   - `Rank 2` 虽是 `narrow paper pilot approved`，但它仍是 paper-only / wiring 侧候选，而不是新的 tiny-live promoted scout winner；
   - 因此当前 desk call 继续是：**`Live Seat = 暂空 / waiting for next promoted scout winner`**。

3. **Rank 17 已成为当前唯一真正活着的 Scout 新晋 `paper candidate`**
   - `Rank 17 pullback recovery confirmation` 已完成：
     - `paper/repo based source mapping -> clean replication -> Light Stability Pack`
   - 当前 hard verdict = **`paper candidate pool`**；
   - 主变体：`pullback2_vol1.0_break1`
   - 关键证据：
     - `6bps/side mean_total_return ≈ +10.21%`
     - `positive_asset_ratio = 2/3`
     - `mean_trades ≈ 69.7`
     - `10bps/side ≈ +4.07%`
   - 但这条线当前还**不够资格自动升到 `narrow paper pilot`**，因为：
     - `15bps/side ≈ -3.13%`
     - `20bps/side ≈ -9.81%`
     - 时间稳定性仍偏混合（约 `4/9` positive buckets）
     - `BTC weak leg` 仍明显拖后腿
   - 因此当前最诚实的 desk 读法是：
     - **它已够格进 `paper candidate pool`**；
     - 但**只能停在 `paper candidate only`，不能偷升格**。

4. **Rank 17 的最小 paper-candidate wiring 已经补齐，后续不能再无限磨近义卡**
   - `02:33 UTC` 已新增：
     - `paper_candidate_monitoring_board.csv`
     - `paper_candidate_refresh_seed_rows.csv`
     - `paper_candidate_refresh_history.csv`
   - 这意味着 Rank 17 现在已经不缺最小 paper-candidate 接线；
   - 当前更诚实的策略不是继续堆更多 admission wording，而是：
     - 要么只做一个 genuinely verdict-changing check；
     - 要么把主资源让回 fresh intake。

5. **Rank 18 已成为当前新的默认 Scout 入口**
   - `Rank 18 EMA neighborhood consensus / plateau-stable crossover` 已完成：
     - `paper-based source intake -> clean-room spec`
   - 当前 hard verdict 仍只是：
     - **`source intake / clean replication next`**
   - 但它现在边际价值最高，因为它能最快回答：
     - EMA 结果到底是“单点 lucky pixel”，还是相邻参数确实存在小平台；
     - plateau / consensus 版本究竟是真稳定，还是只是靠 `no_trade_ratio` 飙升伪装出来。
   - 所以当前默认 `Run 2` 的第一顺位，应明确切到：
     - **`Rank 18 clean replication next`**

6. **Rank 16 及更早 fast-lane 候选继续维持 park，不存在默认重开价值**
   - `Rank 16 ORB threshold + protective closing session gate`：
     - clean replication + Light Stability Pack 后仍是 `park`
     - `confirm1_outside @ 6bps ≈ -7.51%`
     - `positive_asset_ratio = 0/3`
   - `Rank 7 ~ Rank 16` 其余候选也都继续在 `park / evidence pool`
   - 因此当前 desk 的新信息，不是又多一个 failed candidate，而是：
     - **终于有 `Rank 17` 从 park 串里穿出来，变成 `paper candidate`。**

7. **Rank 2 仍保留 narrow paper pilot 身份，但当前继续退居第三优先级**
   - `Rank 2 combo_all` 仍是 **`narrow paper pilot approved`**；
   - 但它近期已连续补完：
     - `ledger template -> refresh seed -> weekly review seed -> writeback seed -> continuity snapshot -> refresh history`
   - 当前更诚实的 desk 读法仍是：
     - 它继续保留席位；
     - 但只有在出现真实 `append/review need` 或 verdict-changing check 时，才值得再占主资源；
     - 否则当前主资源应先给 `Rank 18`，其次保留给 `Rank 17` 的 genuinely new honest check。

## 当前 weakest / should-park lines

- 继续把 `Rank 16` 或更早 `Rank 7~16` 候选当 active 默认主线：应停止。
- 在 `Rank 17` 已补完最小 paper-candidate wiring 后，再继续默认堆近义 wiring：应停止。
- 把 `Rank 17` 当前状态误写成“几乎等于 `narrow paper pilot`”：当前不诚实。
- 把 `Rank 18` 在没跑 clean replication 前误写成 `paper candidate`：也不诚实。

## Desk verdict

- **Paper Seat：`EMA baseline family`**
- **Paper Seat 当前读法：`running paper pilot / waiting_not_due`**
- **Live Seat：`暂空 / waiting for next promoted scout winner`**
- **Live Seat 当前判断：继续保持暂空；本轮没有候选值得被升格。**
- **Scout Seat：当前复刻的 paper / repo candidates 与阶段如下：**
  1. `Rank 1 τ-band / no-trade breakout filter`（De Angelis et al. 2021）→ `park`
  2. `Rank 2 volume + support-flip + higher-low / combo_all`（Yumna et al. 2024）→ **`narrow paper pilot approved`**
  3. `Rank 3 third-touch + EMA/MACD confluence`（Wiśniewski 2024）→ `park`
  4. `Rank 4 crypto pairs trading / stat-arb`（原 frozen-beta 版本）→ `park`
  5. `Rank 4b crypto stat-arb reframe`（rolling-beta 窄重开）→ `park`
  6. `Rank 5 session-aware intraday TSMOM`（Li, Sakkas, Urquhart 2022）→ `park`
  7. `Rank 7 adaptive trend signal combination / state-weighted component vote`（Mugueta-Aguinaga et al. 2023）→ `park`
  8. `Rank 8 EMA shielding / threshold + retest_hold`（De Angelis et al. 2021）→ `park`
  9. `Rank 9 regime-switch indicator stack / no-buy-downtrend gate`（Naganjaneyulu et al. 2023）→ `park`
  10. `Rank 10 volatility-managed EMA / ATR sizing overlay`（Moreira & Muir 2017 + ATR proxy）→ `park`
  11. `Rank 11 Lo-style causal extrema pattern gate`（Lo et al. 2000 + SITONGRUC repo）→ `park`
  12. `Rank 12 averaged support/resistance zone + context gate`（Zhang & Zhou 2024）→ `park`
  13. `Rank 13 partial-moment asymmetry TSMOM gate`（Liu, Lu, Wang 2021）→ `park`
  14. `Rank 14 cross-asset TSMOM confirmation gate`（Pitkäjärvi, Suominen, Vaittinen 2020）→ `park`
  15. `Rank 15 support/resistance regime-switch confirmation gate`（Henderson, Jacka, Liu, Maeda 2021/2025）→ `park`
  16. `Rank 16 ORB threshold + protective closing session gate`（Wu, Syu, Lin, Ho 2021；Syu et al. 2020）→ `park`
  17. `Rank 17 pullback recovery confirmation`（Lo et al. 2000 / Jiang, Kelly, Xiu 2023 -> repo module）→ **`paper candidate pool`**
  18. `Rank 18 EMA neighborhood consensus / plateau-stable crossover`（Chiu et al. 2023）→ **`source intake / clean replication next`**

## 接下来优先级 Top 1~3

1. **优先做 `Rank 18 EMA neighborhood consensus / plateau-stable crossover` 的最小 clean replication**
   - 第一刀重点先看：
     - `post_cost_return`
     - `positive_asset_ratio`
     - `no_trade_ratio`
     - `cost_survival`
   - 若 plateau / consensus 版本只是靠 `no_trade_ratio > 80%` 才勉强转正，或对 `anchor_10_40` 没有更诚实的跨资产改善，则直接 `park`。

2. **`Rank 17` 只在存在 genuinely verdict-changing honest check 时再继续认领**
   - 它当前已经不是“还缺接线”的状态；
   - 已有最小 paper-candidate wiring；
   - 若继续做，必须是会改变 `paper candidate only` 结论的一刀检查，而不是继续堆近义 monitoring/wording。

3. **`Rank 2` 只在出现真实 append/review need 或 verdict-changing check 时再继续认领**
   - 它没有退出桌面；
   - 但当前默认优先级应排在 `Rank 18` 与 `Rank 17 genuinely new check` 之后。

## TODO / web / cron 的改动或建议

### 本轮已改
- 当前 top board 已由最新 bot3 产物完成关键同步：
  - `Rank 17 -> paper candidate pool`
  - `Rank 17` 的最小 paper-candidate wiring 已落地
  - `Rank 18 -> source intake / clean replication next`
  - 当前窗口默认顺序已改成：`Rank 18 clean replication next；Rank 17 仅在 genuinely verdict-changing check 时继续`
- 新增本轮 review：`research/strategy_review/2026-03-17_0254_strategy-review.md`
- 刷新首页 index
- 发送中文邮件摘要

### 本轮不改
- **不改 seat assignment**：`Paper Seat` 仍是 EMA；`Live Seat` 仍暂空。
- **不改 cron 频率**：当前 `bot2` / `bot3` / `bot7` 状态都为 `running/ok`，节奏可先维持。

## 风险与不确定性

1. `Rank 17` 虽已进 `paper candidate pool`，但高 friction 脆弱性仍明显：`15bps` 已转负、`20bps` 更差；当前不能因它终于转正就过度乐观。
2. `Rank 18` 现在还只是 `source intake / clean replication next`；它值钱，但还不是结果。
3. `Paper Seat` 当前虽是 `waiting_not_due`，但 A 股下一次 close 已在几小时内；若 close 后未 append，需要再次临时切回 `Run 1`。

## 本轮一句话结论（给 Jerry）

**这轮真正的变化不是换席，而是 `Scout Seat` 终于从纯 `park` 串里跑出一个能活下来的新东西：`Rank 17` 已进入 `paper candidate pool`，而默认 fresh intake 入口也切到了 `Rank 18 clean replication next`。因此当前最诚实的排班已变成：先做 `Rank 18` clean replication，`Rank 17` 只在 genuinely verdict-changing check 时继续，`Rank 2` 则继续退居真实 append/review need 才回补。**
