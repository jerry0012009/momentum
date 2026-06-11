# 2026-03-17 12:48 UTC · Rank 35 VWAP pullback clean replication park

## 本轮归属
- Desk lane：`Run 2 / Scout Fast Lane`
- 触发原因：`Paper Seat / EMA` 继续处于 `waiting_not_due`，没有新的 `due-now / overdue` lane；按 `TRADING DESK BOARD` 默认顺序切到 `Scout Seat`。

## 开始前检查
- 已先读：`docs/AUTO_OPTIMIZATION_LOOP.md`、`docs/TODO.md` 顶部 `TRADING DESK BOARD`
- repo 状态：工作区仍有大量与本轮无关的脏文件 / 未跟踪文件，因此本轮只做 selective 写入，不混提。
- 最近 runs（抽查）：
  - `2026-03-17_1233_rank35-vwap-pullback-intake.md`
  - `2026-03-17_1222_rank34-clean-replication-park.md`
  - `2026-03-17_1006_rank29-p3-monitoring-redwatch.md`
- 当前席位状态：
  - `Paper Seat = EMA waiting_not_due`
  - `Live Seat = 空`
  - `Scout Seat = Rank 35 最小 clean replication`

## active Scout 边际价值比较（本轮前）
- `Rank 17 / Rank 2 / Rank 29`：当前没有新的真实 `append/review need`；继续认领大概率只会补近义 wiring。
- `Rank 30 / 31 / 32 / 33 / 34`：已完成当前允许动作并 `park`，不应重开。
- `Rank 5 / Rank 6`：仍偏外部数据依赖，不适合作为这轮默认主资源。
- 结论：按 board 约束，`Rank 35` 是本轮边际价值最高、且允许执行的唯一 fresh Scout 主线。

## 本轮主点 + 紧邻子点
- **主点**：把 `Rank 35 VWAP pullback + trend-template qualifier` 从 `source intake` 推到 **1 次最小 clean replication**。
- **紧邻子点**：把 verdict 同步写回 `TODO` 与 reader-facing 页面，避免只留内部日志。

## 冻结后的最小 clean-room 规则
- 样本：固定复用 `BTC/ETH/SOL 120d 15m` cache
- 执行：`next-bar open` 进场，固定持有 `8` 根 15m bar
- `higher_tf trend proxy` 固定为：
  - `1h close > EMA20 > EMA50`
  - `4h close > EMA20`
- 只比较四档最小规则：
  1. `baseline_higher_tf_bias`：higher-tf bias 从 false→true 时开 long
  2. `bias_plus_rsi_pullback`：bias 为真，且 RSI14 先跌入 pullback 区、再重回 40 上方
  3. `bias_plus_vwap_reclaim`：bias 为真，且价格在 pullback 后重新站回冻结 VWAP
  4. `combo_long_only`：RSI reclaim 与 VWAP reclaim 同时成立
- `VWAP anchor` 只允许两档对照：
  - `utc_day`
  - `funding_8h`

## 本轮先回答的 4 个便宜问题
1. `post_cost_return`
2. `trade_count`
3. `time-pocket honesty`
4. `anchor sensitivity`

## 关键结果
### 1) 主变体 hard evidence
主变体固定为 `combo_long_only`，`6bps/side` 下：
- `utc_day`：`mean_total_return≈+1.72%`、`positive_asset_ratio≈66.67%`、`mean_trades≈3.7`、`mean_no_trade_ratio≈99.89%`
- `funding_8h`：`mean_total_return≈+1.97%`、`positive_asset_ratio≈66.67%`、`mean_trades≈4.0`、`mean_no_trade_ratio≈99.88%`

这两个 anchor 都没有直接塌成负数，但交易密度极薄，离合格 `paper candidate` 还差得很远。

### 2) time-pocket honesty
主变体 `6bps/side`：
- `utc_day`
  - `bucket_1≈+0.89%`（4 笔）
  - `bucket_2≈-1.18%`（3 笔）
  - `bucket_3≈+5.37%`（4 笔）
- `funding_8h`
  - `bucket_1≈+1.85%`（4 笔）
  - `bucket_2≈-2.79%`（4 笔）
  - `bucket_3≈+7.01%`（4 笔）

结论：不是单边全面失效，但中间 bucket 明确翻负，且每桶交易数太少，不能把这读成稳定 pocket。

### 3) anchor sensitivity
- `bias_plus_vwap_reclaim` 对 anchor 非常敏感：
  - `utc_day @ 6bps ≈ +8.69%`
  - `funding_8h @ 6bps ≈ -0.51%`
- `combo_long_only` 虽在两档 anchor 下都略正，但 trade count 只有 `3.7~4.0`，并没有形成可部署密度。

更直白地说：这条线最关键的诚实门槛不是“能不能讲出 pullback 故事”，而是 **VWAP anchor 一改，结果会不会明显变形；就算不变形，交易数也是否薄到不值得升格**。

### 4) 为什么不能被 `baseline_higher_tf_bias` 的正收益误导
- `baseline_higher_tf_bias` 在两档 anchor 下都很强（`6bps` 约 `+53.93%`、`1.0 positive_asset_ratio`、`mean_trades≈89.3`）。
- 但这只是说明 **higher-tf bias 本身在这段样本里有方向性**；它不是 `Rank 35` 想验证的 `VWAP pullback + RSI reclaim` admission edge。
- 真正要看的主问题是：加上 `RSI pullback + VWAP reclaim` 以后，是否得到更诚实、可复用的 pullback entry；当前答案是否定的。

## 本轮 hard verdict
- **`Rank 35 -> park / evidence pool`**

原因不是“完全没 pocket”，而是：
1. `combo_long_only` 交易数过薄（`mean_trades≈4`）
2. `time-pocket honesty` 中段翻负
3. `VWAP anchor sensitivity` 明显存在
4. 因此还不配进入 `paper candidate pool`，更不配继续占用默认主资源位

## 本轮交付
### deployable artifacts
- `reports/artifacts/scout_rank35_vwap_pullback_15m/overall_summary.csv`
- `reports/artifacts/scout_rank35_vwap_pullback_15m/asset_summary.csv`
- `reports/artifacts/scout_rank35_vwap_pullback_15m/time_bucket_summary.csv`
- `reports/artifacts/scout_rank35_vwap_pullback_15m/primary_trades_6bps.csv`
- `reports/artifacts/scout_rank35_vwap_pullback_15m/meta.csv`

### reader-facing 页面
- `reports/site/factors/scout_rank35_vwap_pullback_15m/report.html`
- `reports/site/reading/trendline_alpha_scout/rank35_vwap_pullback_clean_replication.html`
- 同步更新：`reports/site/reading/trendline_alpha_scout/report.html`

### 指挥板写回
- 更新：`docs/TODO.md`
- 写回方向：
  - `Rank 35` 从 `fresh intake only` 改成 `park / evidence pool`
  - `Run 2 / 2z` 写回 clean replication 口径与 hard verdict
  - 顶部 override 改成：下一轮默认回到新的 `paper / repo based 5m / 15m crypto` fresh intake，而不是继续磨 `Rank 35`

## 最小验证
- 已运行：`python3 scripts/build_rank35_vwap_pullback_clean_replication.py`
- 结果：脚本成功退出（code 0）
- 已抽查：
  - `reports/artifacts/scout_rank35_vwap_pullback_15m/overall_summary.csv`
  - `reports/artifacts/scout_rank35_vwap_pullback_15m/time_bucket_summary.csv`
  - `reports/site/reading/trendline_alpha_scout/report.html`
  - `docs/TODO.md`
- 未重跑任何重型下载；只复用现有 cache。

## 风险 / 边界
- 这轮用的是非常保守的 clean-room 映射：明确排除了原脚本中的 `52-week / IBD RS / Minervini stock-template` 语境。
- 因为样本内 `combo` 信号太少，所以这里的 `park` 不是说 idea 毫无启发，而是说 **按当前 desk 的 admission 标准，它不值得继续吃默认预算**。
- 若后续想重开，必须拿出 genuinely verdict-changing 的更强 freeze（例如不同但预先声明的 higher-tf qualifier 或更诚实的 pullback 定义），而不是继续微调说明文案。

## Git
- 未提交。
- 原因：repo 内仍有大量与本轮无关的脏文件 / 未跟踪文件，避免混提。
