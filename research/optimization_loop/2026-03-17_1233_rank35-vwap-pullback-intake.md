# 2026-03-17 12:33 UTC · Rank 35 VWAP pullback + trend-template qualifier source intake

## 本轮归属
- Desk lane：`Run 2 / Scout Fast Lane`
- 触发原因：`Paper Seat / EMA` 继续 `waiting_not_due`；按顶板顺序先看 `Run 1`，当前没有新的 `due-now / overdue` lane，因此不能停在 waiting-window 空转，自动切到 `Scout Seat`。

## 开始前检查
- 已先读：`docs/AUTO_OPTIMIZATION_LOOP.md`、`docs/TODO.md` 顶部 `TRADING DESK BOARD`。
- repo 状态：工作区仍有大量与本轮无关的脏文件 / 未跟踪文件，因此本轮只做 selective 写入，不混提。
- 最近 runs（抽查）：
  - `2026-03-17_1222_rank34-clean-replication-park.md`
  - `2026-03-17_1006_rank29-p3-monitoring-redwatch.md`
  - `2026-03-17_0706_ema-ashare-due-followup.md`
- 当前席位状态：
  - `Paper Seat = EMA waiting_not_due`
  - `Live Seat = 空`
  - `Scout Seat = fresh intake first`

## active Scout 边际价值比较（本轮前）
- `Rank 17 / Rank 2 / Rank 29`：当前都没有新的真实 `append/review need`；继续认领大概率只是近义 wiring。
- `Rank 30 / Rank 31 / Rank 32 / Rank 33 / Rank 34`：都已完成当前允许动作并 park；本轮不应重开。
- `Rank 5 / Rank 6`：仍偏外部数据，不适合作为这轮默认主资源。
- 结论：按 board 规则，应切去**新的 paper / repo based 5m / 15m crypto fresh intake**。

## 本轮主点 + 紧邻子点
- **主点**：新增一条 fresh intake——`Rank 35 VWAP pullback + trend-template qualifier`。
- **紧邻子点**：把 intake card、reader-facing 页面、`TODO` 顶板与 scout 总览页一起写回，避免只留内部日志。

## 为什么选 Rank 35
- 本轮不再默认强调 breakout，而是优先找一条更偏 `long-only pullback / reclaim` 的候补。
- 通过轻量网页抓取，命中一个可 clean-room 吸收的开源脚本来源：
  - `Advanced VWAP_Pullback Strategy_Trend-Template Qualifier`
  - 来源：`hasnocool/tradingview-pine-scripts`
- 原脚本虽然带重股票语境（`Minervini / 52-week / IBD RS`），但其中的核心可压成更适合 15m crypto 的最小规则：
  - `higher-tf trend qualifier`
  - `RSI pullback / oversold`
  - `VWAP reclaim`
  - 默认 `long-only`

## 两条轻量诚实守门
1. **trade on / trade off 可清楚写出**
   - `trade on = higher_tf trend-template proxy 为真，最近 N 根出现 RSI oversold / weak-pullback，然后短均线重新上穿 session VWAP；默认只做 long-only`
   - `trade off = higher_tf bias 缺失或反向、最近并无 pullback/oversold、短均线没有重新站回 VWAP、或 reclaim 很快跌回 VWAP 下方`
2. **没有偷做 lookahead / leakage**
   - 本轮没有复现，只做 source intake；
   - 但已明确下一轮必须先冻结 `VWAP anchor`（UTC-day / session window）与 `higher-tf trend proxy`，不能事后挑最好看的版本；
   - 原脚本的股票式 `52-week / IBD RS` 语境也不能原样搬进 15m crypto。

## 本轮交付
### 1) deployable artifact
- 新增：`reports/artifacts/literature/scout_rank35_vwap_pullback_source_intake_card.csv`

### 2) reader-facing 页面
- 新增：`reports/site/reading/trendline_alpha_scout/rank35_vwap_pullback_source_intake.html`
- 更新：`reports/site/reading/trendline_alpha_scout/report.html`

### 3) 指挥板写回
- 更新：`docs/TODO.md`
- 写回内容：
  - 顶部 authoritative override 改为：`Rank 34` 已 park，当前 fresh intake 主线切到 `Rank 35`；
  - `Run 2` 新增 `2z. Rank 35 ...` 执行口径；
  - rank 主清单新增 `35` 条目，明确这轮只到 `fresh intake only / pending Stage A + clean replication`。

## 当前 hard verdict
- **`Rank 35 -> fresh intake only / pending Stage A + clean replication`**
- 这不是 `paper candidate`，更不是 `narrow paper pilot`。
- 这轮最诚实的结论只有一个：
  - 它值得拿 **1 次最小 clean replication 预算**；
  - 但在 `VWAP anchor` 与 `higher-tf trend proxy` 的 crypto 版 clean-room 表达没冻结前，不应提前升格。

## 下一轮允许动作（已在 board 写清）
- 只允许复用 `BTC/ETH/SOL 120d 15m` cache；
- 只比较四档最小规则：
  - `baseline_higher_tf_bias`
  - `bias_plus_rsi_pullback`
  - `bias_plus_vwap_reclaim`
  - `combo_long_only`
- 先回答四个便宜问题：
  - `post_cost_return`
  - `trade_count`
  - `time-pocket honesty`
  - `anchor sensitivity`
- 若 `VWAP anchor` 或 `higher-tf qualifier` 一改就失真，直接 `park`，不进入完整 stability pack。

## 最小验证
- 已检查新写入文件存在且关键字段可读：
  - `docs/TODO.md`
  - `reports/artifacts/literature/scout_rank35_vwap_pullback_source_intake_card.csv`
  - `reports/site/reading/trendline_alpha_scout/rank35_vwap_pullback_source_intake.html`
  - `reports/site/reading/trendline_alpha_scout/report.html`
- 这轮没有重跑重型下载，也没有扩成 clean replication。

## 风险 / 边界
- 外部来源只是 open-source script，不是可直接照搬的 production rule。
- 股票式 trend-template 迁移到 15m crypto 时，最容易失真的就是 `52-week / IBD RS / stock selection` 这部分；因此它们都被明确挡在本轮范围外。
- 本轮没有给收益结论，只做了下一轮可执行的 source intake 压缩。

## Git
- 未提交。
- 原因：当前 repo 仍有大量与本轮无关的脏文件 / 未跟踪文件，避免混提。
