# 2026-03-23 11:48 UTC · Rank 151 / EWMAC breakout band-pass gate fresh intake

- 严格遵循：`docs/TODO.md` 顶部 `TRADING DESK BOARD`、`docs/AUTO_OPTIMIZATION_LOOP.md`、`docs/BOT2_BOT3_OPERATING_CARD.md`
- 本轮路径：`Scout`
- 本轮范围：只做 **1 个主点 + 1 个紧邻子点**

## 0. 顶板判路
- `Paper / 待开启自动运行 = empty`
- 顶板未写入新的 `stale / error / refresh drift / ledger/open-position anomaly / red-watch`
- 因此本轮继续走 `Scout`
- 按顶板 `Run 1 = 下一条 fresh intake / raw-alpha reserve 守门` 执行，但在 `Rank 150` 已于上一轮完成后，本轮补一条 **新的独立 fresh intake reserve**，避免回头重磨 `148/149` 近亲

## 1. 为什么本轮选 Rank 151
`EWMAC breakout band-pass gate` 值得拿到下一个未使用 Rank，原因很直接：
- 它不依赖双腿配对执行，不是 `148/149` 那种成本一上来就直接塌掉的结构；
- 它也不是新的重型家族，而是能直接服务 `breakout-short / fib retest / EMA-PSAR` 的共享 admission/sizing 闸门；
- digest 已经给出一个对 desk 很有用的反直觉点：**不是分数越高越好，而是中段对齐比分数尾部更诚实**。

## 2. 本轮主点
### 主点
- **`Rank 151 / EWMAC breakout band-pass gate`**

reader-facing 定义：
> 不把 `EMA32-EMA96` 与 breakout 对齐分数当作“越高越该追”的单调绿灯，而是把它当成一个 band-pass 过滤器：中段顺势样本优先，极端强分数尾部降权或 veto，因为那一段更像 late-chase。

### 使用证据
- digest：`research/quant_digests/2026-03-23_0735_ewmac-breakout-bandpass-not-highest-score-wins.md`
- repo anchor：`nicolasdd1996/crypto-trend-follow`
- 本地快检：`BTC/ETH/SOL 15m`、`20-bar breakout`、`8-bar signed return`

## 3. 最小 intake 结论
这条线现在最诚实的口径是：
- **`P1 / keep_P1 / fresh intake admitted / shared sizing-gate candidate`**

原因：
1. **有 desk 相关性**：它能直接嫁接现有 continuation 事件，不需要新 execution stack；
2. **有可验证的最小差异**：baseline vs hard-positive vs band-pass 三臂 A/B/C 很清楚；
3. **有初步正面信号**：digest 里的 `BTC/ETH/SOL 15m` 快检显示，中段 band-pass 的 `8-bar signed return` 明显优于尾部分数；
4. **但还没有 frozen family-level honest cut**：当前只是 generic breakout 快检，不是已经在某一条 desk family 上走完 post-cost + retention 的正式守门。

所以它值得入列 active Scout，但还不能升 `P2`。

## 4. 紧邻子点
### 紧邻子点：它能不能直接越过 `Rank 140 / 150` 成为默认 primary？
结论：**不能。**

- `Rank 140` 仍是 desk-local compare anchor；
- `Rank 150` 已经占住“shared regime gate reserve”这个位置；
- `Rank 151` 当前只是说明“别把最强 EMA 对齐当自动放行”，还没做 family-level frozen A/B/C，因此更适合排在 `150` 后、作为另一条共享 filter reserve。

但它比继续打磨 `148/149` 更值得保留：
- 不是 paired-cost fragility；
- 不是又一条独立 execution-heavy raw alpha；
- 如果成立，会直接改善现有 breakout / retest / EMA continuation 的 late-chase 问题。

## 5. 简短 scorecard
- `usefulness = 3/3`
- `time_stability = 1/3`
- `cross_asset_stability = 2/3`
- `cost_trade_stability = 2/3`
- `deployability = 2/3`
- `recommended_action = keep_P1`
- `why_now = 顶板要求补 fresh intake reserve；band-pass EWMAC 是非配对、可共享、能直接接到现有 continuation 家族上的更高杠杆新候选。`
- `main_weakness = 只有 generic breakout 快检，还没有一条 desk family 上的 frozen A/B/C honest cut。`

### hard-fail flags
- `not_independent_alpha`
- `quantile_thresholds_need_frozen_oos_check`
- `tail_chase_may_be_setup_specific`
- `not_ready_for_P2`

## 6. 本轮交付
- 日志：`research/optimization_loop/2026-03-23_1148_rank151-ewmac-bandpass-intake.md`
- scorecard：
  - `reports/artifacts/scout_rank151_ewmac_breakout_bandpass_gate_15m/promotion_scorecard.csv`
  - `reports/artifacts/scout_rank151_ewmac_breakout_bandpass_gate_15m/promotion_scorecard.json`
- source intake：
  - `reports/artifacts/scout_rank151_ewmac_breakout_bandpass_gate_15m/source_intake_card.csv`

## 7. 一句话结论
`Rank 151` 现在最像：**一个值得纳入 active Scout 的 shared sizing/filter reserve**；它不是新 raw alpha 主线，但比回头继续磨已 park 的 `148/149` 更能给现有 continuation 家族带来下一刀价值。
