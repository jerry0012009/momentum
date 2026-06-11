# 2026-03-19 22:33 UTC — Rank 101 3-step volume dry-down long-bias gate minimal clean replication

## 本轮先核对的 desk 状态
- repo 工作区仍有大量与本轮无关的既有脏文件；本轮未做 commit，也未混提无关改动。
- 最近 optimization logs：
  - `2026-03-19_2212_rank101-volume-drydown-intake.md`
  - `2026-03-19_2200_rank100-fib-depth-clean-replication.md`
  - `2026-03-19_2140_rank100-fib-depth-intake.md`
- 先实际执行：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 结果：`waiting_not_due`
  - 当前无 `due-now / overdue` lane；最近 due 仍是 `Crypto 1d+1wk（BTC/ETH/SOL）`，约 `1.5h` 后到点。
  - 结论：`Paper Seat = EMA / running paper / waiting_not_due`
- `manual_narrow_paper_last_run_summary.json`
  - 当前未出现新的 `new_closed_trades_appended` 状态变化
  - 结论：本轮没有需要 bot3 插队主资源处理的 `P3 status-changing event`

## Active Scout 候选边际比较（本轮先比较后认领）
1. **`Rank 101 / 3-step volume dry-down long-bias gate`**
   - 上一轮已 `guard-passed / admit_to_clean_replication_queue`
   - 顶板当前 `Next 3` 明确要求：若 `EMA` 仍 `waiting_not_due`，本轮就只给它 `1` 次最小 clean replication
   - 它直接回答当前 desk 对 `pullback participation decay` 的最后一个最小问题：缩量回踩究竟能不能从“经验话”压成可保留的 gate
2. **fresh source pool retry（7.10）**
   - 只有当 `Rank 101` 给出 hard verdict 后，才轮到它接棒
3. **`tiny-live plumbing`**
   - 当前没有新的 promoted live candidate，也没有执行面变化，不应插队

结论：本轮主资源继续给 `Rank 101`；紧邻子点只做顶板写回与 reader-facing 外显，不并开新的 fresh intake。

## 本轮只认领的主点
- **主点：`Scout Seat / Rank 101 / 3-step volume dry-down long-bias gate` 的 1 次最小 clean replication**
- 紧邻子点：把 hard verdict 写回 `TODO` 顶板，并同步 reader-facing 页面与 artifact

## 本轮 clean replication 口径
- 严格复用 `reports/artifacts/quant_digests/abnormal_volume_pullback_proxy/`
- 数据口径：`BTC / ETH / SOL | 120d | 15m | next-bar open | no-overlap | 6bps/side`
- 本轮不追新 bar，不重拉重型数据，只把既有代理快检收口成 desk 级 hard verdict
- 对比臂：
  - long：`baseline / dv3 / lv80 / dv3_lv80`
  - short：仅保留 `baseline / dv3 / lv80 / dv3_lv80` 作为镜像诚实检查，不做 short admission 推进
- 这轮主看：
  - `avg_net_ret_h8`
  - `win_rate`
  - `retention_vs_baseline`
  - `positive_asset_ratio`

## 最小结果
### long side 总表读法
- `baseline`
  - `trades = 1582`
  - `avg_net_ret_h8 ≈ -11.71bps`
  - `win_rate ≈ 38.37%`
- `dv3`
  - `trades = 74`
  - `avg_net_ret_h8 ≈ -4.30bps`
  - `win_rate ≈ 45.95%`
  - `retention_vs_baseline ≈ 4.68%`
- `lv80`
  - `trades = 696`
  - `avg_net_ret_h8 ≈ -10.55bps`
  - `win_rate ≈ 40.09%`
  - `retention_vs_baseline ≈ 43.99%`
- `dv3_lv80`
  - `trades = 54`
  - `avg_net_ret_h8 ≈ +0.12bps`
  - `win_rate ≈ 48.15%`
  - `retention_vs_baseline ≈ 3.41%`
  - `positive_asset_ratio ≈ 66.67%`

### 按资产拆开后的最诚实读法
- `dv3_lv80` 只有 `ETH / SOL` 转正：
  - `ETH ≈ +20.53bps`
  - `SOL ≈ +1.67bps`
- `BTC @ dv3_lv80` 仍为负：`≈ -22.89bps`
- 因此这条线更像局部 pocket 的 long-side 吸收语义，不是跨资产足够硬的独立 edge

### short 镜像诚实检查
- `short baseline ≈ -7.03bps`
- `short dv3_lv80 ≈ -24.71bps`
- 结论：short 镜像明显更差；这条线不能被包装成 breakout-short 的 shared admission

## 本轮 hard verdict
- **`Rank 101 / 3-step volume dry-down long-bias gate = park / evidence pool`**

### 为什么不是 promote_to_P2
1. `dv3_lv80` 虽把 long baseline 从负值抬到近乎持平，但真正 post-cost 只剩 `≈ +0.12bps`，还谈不上 deployable edge
2. 样本保留率只有 `≈ 3.41%`，更像极窄切样本，而不是足够诚实的 broad hold-quality gate
3. 跨资产仍不统一：`BTC` 口袋继续为负，说明它连 long side 也还没过最小稳定性门槛

### 为什么也不是 keep_P1
- `Rank 101` 上一轮已经把 `trade on / trade off` 与 `no-lookahead / no-leakage` 守门讲清楚了；这一轮最小 clean replication 后，问题已不再是“它有没有一点 alpha 味道”，而是“它值不值得继续占 Scout 主资源”。
- 当前答案已经足够硬：**不值得**。它最多只配保留为：
  - `long-side hold-quality note`
  - `short-veto / size-down note`
- 不应继续把它写成 active Scout 候选，更不应推进到 `paper candidate pool`

## 产物
- script:
  - `scripts/build_rank101_volume_drydown_clean_replication.py`
- artifact:
  - `reports/artifacts/scout_rank101_volume_drydown_long_bias_15m/long_overall_summary.csv`
  - `reports/artifacts/scout_rank101_volume_drydown_long_bias_15m/long_asset_summary.csv`
  - `reports/artifacts/scout_rank101_volume_drydown_long_bias_15m/short_overall_summary.csv`
  - `reports/artifacts/scout_rank101_volume_drydown_long_bias_15m/short_asset_summary.csv`
  - `reports/artifacts/scout_rank101_volume_drydown_long_bias_15m/verdict_summary.csv`
- reader-facing:
  - `reports/site/factors/scout_rank101_volume_drydown_long_bias_15m/report.html`
  - `reports/site/reading/repo_scout/rank101_volume_drydown_long_bias_clean_replication.html`

## 对顶板的更新结论
- `Rank 101 = park / evidence pool`
- `3-step volume dry-down` 对当前 desk 的保留价值：**long-side hold-quality / short-veto note only**
- 最新 `Next 3`：
  1. `Run 1 = EMA due-check only`
  2. `Run 2 = 若 EMA 仍 waiting_not_due，则按 7.10 回 fresh source pool（优先 RECENT_PAPER_SEEDS / quant_digests / validated shortlist）再认领 1 条新的 5m/15m crypto paper-repo source`
  3. `Run 3 = 若 fresh intake 已 guard-passed 且 EMA 仍 waiting_not_due，则只给它 1 次最小 clean replication；只有 fresh source 也 exhausted 时才回退到 tiny-live plumbing`

## 最小验证
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 如实确认当前还是 `waiting_not_due`
- `python3 scripts/build_rank101_volume_drydown_clean_replication.py`
  - 已成功写出 artifact 与两张 reader-facing 页面
- 读回 `reports/artifacts/scout_rank101_volume_drydown_long_bias_15m/verdict_summary.csv`
  - 已确认 hard verdict、关键指标与生成时间写入成功
- `docs/TODO.md`
  - 已写回最新 supplement、verdict 与下一轮 `Next 3`

## 备注
- 本轮没有并开新的 fresh source intake；只完成 `1 个主点 + 1 个紧邻子点`
- 本轮没有触发 `P3 continuity` 预算，也没有提前切回 `tiny-live plumbing`
- 工作区仍有大量历史脏文件；本轮未尝试整理、提交或覆盖这些无关改动
