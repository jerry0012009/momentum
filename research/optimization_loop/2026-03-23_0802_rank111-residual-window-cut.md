# 2026-03-23 08:02 UTC · Rank 111 residual-window cut

## 本轮路径
- 顶板：`Paper / 待开启自动运行 = empty`
- 无新 interrupt 迹象
- 按 `Next 3 bot3 runs`，本轮走 **Scout / Run 1 / Rank 111**

## 本轮只做的一刀
主点：对 `Rank 111 / abnormal-return event clock` 做 **去重叠窗口的残余收益复核**。

紧邻子点：把结果落成 reader-facing 页面，避免后面又把它误讲成“后段也有明确 alpha”。

为什么是这刀：
- `Rank 139` 刚按更严格的 `T+3 -> T+8` 残余窗口重跑后，强 edge 明显消失；
- `Rank 111` 之前的 clean replication 也存在同类风险：`same-window / timeout` 看起来改善，可能主要来自前几根路径，而不是后段仍有可交易信息；
- 所以本轮最有杠杆的验证，就是看 **把前 3 根切掉后，后段残余收益还剩什么**。

## 使用输入
- 既有 trade log：`reports/artifacts/scout_rank111_event_clock_15m/trade_log.csv`
- 既有 frozen frames：
  - `reports/artifacts/scout_rank111_event_clock_15m/btcusdt_frame.csv`
  - `reports/artifacts/scout_rank111_event_clock_15m/ethusdt_frame.csv`
  - `reports/artifacts/scout_rank111_event_clock_15m/solusdt_frame.csv`
- 固定口径：`T+3 -> T+8 residual`，仍按 `6bps/side`

## 新增产物
- `reports/artifacts/scout_rank111_event_clock_15m/residual_window_trade_log_tplus3_tplus8.csv`
- `reports/artifacts/scout_rank111_event_clock_15m/residual_window_overall_summary_tplus3_tplus8.csv`
- `reports/artifacts/scout_rank111_event_clock_15m/residual_window_setup_summary_tplus3_tplus8.csv`
- `reports/artifacts/scout_rank111_event_clock_15m/residual_window_asset_summary_tplus3_tplus8.csv`
- `reports/artifacts/scout_rank111_event_clock_15m/residual_window_summary_tplus3_tplus8.json`
- reader-facing：`reports/site/reading/repo_scout/rank111_event_clock_residual_window_tplus3_tplus8.html`

## 结果摘要
### overall
- `baseline`
  - `trades = 198`
  - `mean_residual_net_return = -0.0152%`
  - `mean_residual_total_return = -1.0024%`
  - `positive_asset_ratio = 2/3`
- `same_window_only`
  - `trades = 106`
  - `retention = 53.54%`
  - `mean_residual_net_return = -0.0607%`
  - `mean_residual_total_return = -2.1438%`
  - `positive_asset_ratio = 2/3`
- `window_plus_timeout`
  - `trades = 114`
  - `retention = 57.58%`
  - `mean_residual_net_return = -0.0664%`
  - `mean_residual_total_return = -2.5225%`
  - `positive_asset_ratio = 2/3`

### setup breakdown（只看最关键）
- `breakout_short`
  - `baseline residual ≈ -0.0547%`
  - `same_window_only residual ≈ +0.0733%`
  - `window_plus_timeout residual ≈ +0.0116%`
  - 说明它仍有一点点“后段不那么差”的迹象，但没有强到能单独托起全局。
- `fib_retest_long`
  - 三臂都接近零上下，小幅正
  - 更像中性偏正，不是 decisive edge
- `ema_psar_long`
  - `baseline residual ≈ -0.0043%`
  - `same_window_only residual ≈ -0.1499%`
  - `window_plus_timeout residual ≈ -0.1404%`
  - 这是本轮最关键的拖累：**原先 gate 的改善没有延续到后段，反而把最差腿放大了。**

## 人话结论
这轮把前 3 根切掉之后，`Rank 111` 的故事明显收紧：

1. **它之前的改善，主要不是“后段还有更强 alpha”，而更像“少追了前段坏单 / 缩短了暴露”。**
2. 一旦只看 `T+3 -> T+8` 残余窗口，`same_window_only` 和 `window_plus_timeout` 都 **没有跑赢 baseline**。
3. `breakout_short` 还有一点残余改善，但不够覆盖 `ema_psar_long` 的明显恶化。
4. 所以 desk 口径应继续收紧：
   - `Rank 111` 可以保留为 **P1 / evidence anchor / diagnostic overlay**；
   - 但**不应该**再把它讲成“后段仍有可交易 follow-up edge”的 active candidate。

## 对 desk 的最小 writeback 结论
- 层级：继续 `P1 / keep_P1`
- 角色：`evidence anchor / diagnostic overlay`
- 不是：`default primary`，也不是 `P2 -> P3` 候选

## 简短 scorecard
- `usefulness = 2/3`
- `time_stability = 1/3`
- `cross_asset_stability = 1/3`
- `cost_trade_stability = 1/3`
- `deployability = 0/3`
- `recommended_action = keep_P1`
- `why_now = 用最小 residual cut 先排除“窗口重叠带来的假改善”`
- `main_weakness = 后段 residual 不成立，且 ema_psar_long 被放大为主要拖累`

## 对后续 Run 2 / Run 3 的含义
这刀已经把 `Rank 111` 最重要的一块边际信息补齐了：
- 它适合作为 compare / diagnostic 证据；
- 不值得再继续烧默认主资源去找“是不是还能再讲成 shared gate”。

## 验证命令
```bash
python3 - <<'PY'
# 使用既有 trade_log + frozen frames 计算 T+3 -> T+8 residual
PY
```

## 交付
- 日志：`research/optimization_loop/2026-03-23_0802_rank111-residual-window-cut.md`
- 新 artifact：见上
- reader-facing 页面：`reports/site/reading/repo_scout/rank111_event_clock_residual_window_tplus3_tplus8.html`
