# 2026-03-23 10:38 UTC · Rank 148 / intraday cross-sectional reversal（US 时段）fresh intake

- 严格遵循：`docs/TODO.md` 顶部 `TRADING DESK BOARD`、`docs/AUTO_OPTIMIZATION_LOOP.md`、`docs/BOT2_BOT3_OPERATING_CARD.md`
- 本轮路径：`Scout`
- 本轮范围：只做 **1 个主点 + 1 个紧邻子点**

## 0. 顶板判路
- `Paper / 待开启自动运行 = empty`
- 顶板未写入新的 `stale / error / refresh drift / ledger/open-position anomaly / red-watch`
- 因此本轮不走 `Paper launch`，也不走 `Interrupt`，按 `Next 3 bot3 runs` 执行：
  - **Run 1 = fresh intake / active reserve**

## 1. 为什么本轮选 fresh intake，而不是继续磨旧 P1
顶板已把：
- `Rank 125 / 112 / 111` 固定为本轮不再续磨的 `keep_P1`
- `Rank 147 / 146` 也都已花掉各自最短预算，当前都停在 `keep_P1 / reserve`

所以本轮最有杠杆的小步，不是继续给 exhausted P1 做近义二刀，而是给最新、独立家族的 raw alpha 候选一个 reader-facing 最小 intake。

## 2. 本轮主点
### 主点
- **`Rank 148 / intraday cross-sectional reversal (US session)`**

reader-facing 定义：
> 在固定 US 时段窗口里，按窗口内相对涨跌做横截面排序，做“多输家、空赢家”的下一窗口日内反转组合；它是独立 raw alpha，不是 breakout 或结构过滤配件。

### 使用证据
- digest：`research/quant_digests/2026-03-23_1023_intraday-cross-sectional-reversal-us-session.md`
- 本地产物：
  - `reports/artifacts/quant_digests/intraday_cs_reversal_20260323/summary.csv`
  - `reports/artifacts/quant_digests/intraday_cs_reversal_20260323/daily_window_returns.csv`
  - `reports/artifacts/quant_digests/intraday_cs_reversal_20260323/run_meta.txt`

## 3. 最小 intake 结论
这条线值得被正式记为新的 Scout，但当前只到：
- **`P1 / keep_P1 / fresh intake admitted / raw-alpha reserve / large-cap lower-bound weak`**

原因很直接：
- 它的价值在于 **家族独立性**：横截面/相对价值/日内 session effect，能扩 raw alpha 池；
- 但当前本地大币快检只给出：
  - `morning window ≈ +0.33 bps/day, Sharpe ≈ 0.17`
  - `close window ≈ -0.92 bps/day, Sharpe ≈ -0.54`
- 这说明在 **20 个主流 USDT 对 + 15m + 112 天** 口径下，它还远没到可交易下限，更别说成本后可部署。

最诚实读法不是“这条 alpha 死了”，而是：
> **raw alpha 方向值得留档，但主流大币宇宙只是保守下限；若后续继续，只该去验证中盘可交易宇宙 + execution/capacity overlay，而不是现在就升 P2。**

## 4. 紧邻子点
### 紧邻子点：它现在能不能越过 `Rank 147 / 146` 成为默认 primary？
结论：**不能。**

理由：
1. 它虽然是更独立的 raw alpha 家族，但目前证据仍是 **single quickcheck + large-cap lower bound**；
2. 当前结果更像“值得保留的研究方向”，还不是“已形成新的 P2 动能”；
3. 因此它可以进入 active Scout，但先停在 `fresh intake reserve / keep_P1`，不应该直接接管默认 primary。

## 5. 简短 scorecard
- `usefulness = 3/3`
- `time_stability = 1/3`
- `cross_asset_stability = 1/3`
- `cost_trade_stability = 0/3`
- `deployability = 1/3`
- `recommended_action = keep_P1`
- `why_now = queue 为空时最该补的是独立 raw alpha 家族的新 intake，而不是继续磨掉预算的旧 P1。`
- `main_weakness = 主流大币 15m 快检 alpha 很弱，且最容易死在成本/冲击；尚未验证中盘宇宙与 execution pocket。`

### hard-fail flags
- `cost_fragile`
- `large_cap_universe_weak`
- `session_pocket_unproven`
- `not_ready_for_P2`

## 6. 本轮交付
- 日志：`research/optimization_loop/2026-03-23_1038_rank148-intraday-cs-reversal-intake.md`
- scorecard：
  - `reports/artifacts/scout_rank148_intraday_cs_reversal_15m/promotion_scorecard.csv`
  - `reports/artifacts/scout_rank148_intraday_cs_reversal_15m/promotion_scorecard.json`
- authoritative writeback：把 `Rank 148` 补入 `Active Scout` 与 `最近关键 evidence`

## 7. 一句话结论
`Rank 148` 现在最像：**值得保留的独立 raw-alpha reserve**，不是立刻可升层的 paper 候选；它回答的是“值得不值得继续挖这条家族”，答案是 **值得留档，但先停在 keep_P1**。
