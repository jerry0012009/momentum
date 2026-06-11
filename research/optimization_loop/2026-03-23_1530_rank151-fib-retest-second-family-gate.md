# 2026-03-23 15:30 UTC · Rank 151 / fib retest second-family honest gate

- 严格遵循：`docs/TODO.md` 顶部 `TRADING DESK BOARD`、`docs/AUTO_OPTIMIZATION_LOOP.md`、`docs/BOT2_BOT3_OPERATING_CARD.md`
- 本轮路径：`Scout`
- 本轮范围：只做 **1 个主点 + 1 个紧邻子点**

## 0. 顶板判路
- `Paper / 待开启自动运行 = empty`
- 本轮未见 `Interrupt` 级异常
- 顶板 `Next 3 bot3 runs / Run 1 = Rank 151 的第二条 desk family 复核`
- 因此本轮严格执行第二 family replication；不再继续重复 breakout-short 同 family 叙事

## 1. 为什么这轮做这件事
`Rank 151` 到上一轮为止已经有：
1. local frozen A/B/C cut；
2. `breakout-short` 首条 family honest gate；
3. `breakout-short` 的时间稳定性初检（`band_pass uplift` 在 `7` 个月里 `5/7` 为正）。

现在最值钱的问题只剩一个：

> 它是不是只是 `breakout-short` 这条 family 上“碰巧成立”的过滤器？

如果第二条 desk family 也能复现，那它就开始像真正的 **shared gate**；如果过不了，就该及时收紧成 `family-specific` 线索。

## 2. 本轮实际动作
新增并执行：
- `scripts/build_rank151_fib_retest_family_honest_gate.py`

数据来源：
- frozen 阈值沿用 `reports/artifacts/quant_digests/ewmac_breakout_alignment_20260323/thresholds.json`
  - `q20 = -1.1560`
  - `q80 = 1.6414`
- 第二 family 使用：
  - `reports/artifacts/scout_rank74_adx_er_trend_readiness_15m/{btc,eth,sol}usdt_feature_frame.csv`

构造口径：
- family：`fib_retest_long`
- 事件：feature frame 里的 `fib_retest_long_signal`
- `align_score = (EMA32 - EMA96) / ATR14`
- hold：`8 bars`
- A/B/C：
  - `A = baseline`
  - `B = hard_positive (align_score > 0)`
  - `C = band_pass (q20 < align_score <= q80)`
- 成本层：`6 / 10 / 15 bps per side`

## 3. 主结果（fib retest family）
来自：`reports/artifacts/scout_rank151_fib_retest_family_honest_gate_15m/pooled_summary.csv`

### 6bps/side（primary）
- `baseline`
  - `trades = 34`
  - `retention = 100.0%`
  - `mean_net_bps = +11.89`
  - `total_net_bps = +404.13`
  - `positive_asset_ratio = 3/3`
- `hard_positive`
  - `trades = 15`
  - `retention = 44.1%`
  - `mean_net_bps = -15.52`
  - `total_net_bps = -232.78`
  - `positive_asset_ratio = 1/3`
- `band_pass`
  - `trades = 20`
  - `retention = 58.8%`
  - `mean_net_bps = +36.36`
  - `total_net_bps = +727.16`
  - `positive_asset_ratio = 3/3`

### 成本敏感性
- `10bps/side`：`band_pass = +28.36 bps`，仍明显优于 `baseline = +3.89 bps` 与 `hard_positive = -23.52 bps`
- `15bps/side`：`band_pass = +18.36 bps`，仍保持正值；`baseline = -6.11 bps`，`hard_positive = -33.52 bps`

## 4. 紧邻子点：按资产看是不是单币幻觉
来自：`reports/artifacts/scout_rank151_fib_retest_family_honest_gate_15m/asset_summary.csv`

### 6bps/side by asset
- `BTCUSDT`
  - baseline `+21.87 bps`
  - hard_positive `+67.36 bps`（但只有 `2` 笔，样本极薄）
  - band_pass `+65.84 bps`
- `ETHUSDT`
  - baseline `+2.41 bps`
  - hard_positive `-3.00 bps`
  - band_pass `+13.96 bps`
- `SOLUSDT`
  - baseline `+12.23 bps`
  - hard_positive `-85.12 bps`
  - band_pass `+48.14 bps`

结论：
- 这不是单一资产撑起来的假象；
- `band_pass` 在三资产上都为正，而且都高于 baseline；
- `hard_positive` 再次说明“不是越强越好”，在 fib retest 上反而显著更差。

## 5. 本轮最值钱的结论
1. **Rank 151 已拿到第二条 desk family replication。**
   它不再只是 `breakout-short` 上成立；在 `fib retest` 上，`band_pass` 同样明显优于 `baseline / hard_positive`。
2. **shared-gate 叙事开始站住了。**
   两条 family 的共同结论都不是“极强对齐分数最好”，而是：
   - `hard_positive` 不可靠；
   - `band_pass`（中段放行、极端不追）更诚实。
3. **下一刀不该再补第三条 family，而该转向更正式稳定性。**
   既然第二 family 已过，再继续补 family 的边际价值开始下降；下一轮最值钱动作应改成：
   - `rolling / split` 稳定性，或
   - 更正式的跨阶段 holdout 验证。

## 6. 简短 scorecard
- `usefulness = 3/3`
- `time_stability = 2/3`（第二 family 过了，但本 family 还没单独做时间切片）
- `cross_asset_stability = 3/3`
- `cost_trade_stability = 3/3`
- `deployability = 2/3`
- `recommended_action = P2 discussion unlocked`
- `why_now = 顶板明确要求先做 Rank 151 的第二条 desk family 复核；fib retest 用现成 feature frame 即可最短回答“shared gate 还是 breakout-short 特例”。`
- `main_weakness = 样本数偏小（尤其 fib retest 总样本只有 34 笔），所以这更像 replication evidence，而不是直接进 Paper 的 deploy 证据。`

## 7. 本轮新增产物
- 日志：`research/optimization_loop/2026-03-23_1530_rank151-fib-retest-second-family-gate.md`
- 脚本：`scripts/build_rank151_fib_retest_family_honest_gate.py`
- artifact：
  - `reports/artifacts/scout_rank151_fib_retest_family_honest_gate_15m/trades.csv`
  - `reports/artifacts/scout_rank151_fib_retest_family_honest_gate_15m/asset_summary.csv`
  - `reports/artifacts/scout_rank151_fib_retest_family_honest_gate_15m/pooled_summary.csv`
  - `reports/artifacts/scout_rank151_fib_retest_family_honest_gate_15m/family_honest_gate_meta.json`
- 页面：
  - `reports/site/factors/scout_rank151_fib_retest_family_honest_gate_15m/report.html`
  - `reports/site/reading/repo_scout/rank151_fib_retest_family_honest_gate.html`

## 8. 一句话结论
`Rank 151` 已经不是只在 `breakout-short` 上偶然成立的 family gate。用同一套 frozen `q20/q80` 去打第二条 `fib retest` family 后，`band_pass` 在 `6/10/15bps` 三个成本层都显著优于 `baseline / hard_positive`，且三资产方向一致更好。当前最诚实 desk 更新应是：**`keep_P1 but stronger -> 已解锁 P2 discussion；下一轮优先 rolling/split 稳定性，而不是继续补第三条 family。`**
