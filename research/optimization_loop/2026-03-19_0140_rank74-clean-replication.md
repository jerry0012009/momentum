# 2026-03-19 01:40 UTC｜Rank 74 / ADX+ER price-only trend-readiness gate 最小 clean replication

## 轮次定位
- 席位：`Scout Seat`
- 本轮主点：`Run 2 / Rank 74 minimal clean replication`
- 紧邻子点：`TODO` 顶板 `Next 3 bot3 runs` 顺序刷新

## 为什么这轮选这个
- 先按顶板要求复核 `Run 1 / EMA due-check only`：`reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 仍显示全 desk 当前无 `due-now / overdue` lane，最近 due 点仍是 `A股三条 lane -> 2026-03-19 07:00 UTC`，因此 `Paper Seat / EMA` 当前是真 `running paper / waiting_not_due`。
- 再复核 `P3 continuity`：`reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json` 继续是 `new_closed_trades_appended=0`，当前没有新的 status-changing event 值得 bot3 回头挤占 `P3` 托管位。
- `Rank 74` 在上一轮已完成 `source intake + 两条轻量诚实守门`，并且顶板最新 `Next 3` 已明确写成：若 `EMA` 仍 `waiting_not_due`，就立刻给它 1 次最小 clean replication。
- git 工作区仍有大量与本轮无关的脏文件 / 未跟踪文件；本轮只新增 `Rank 74` clean-replication 相关脚本、artifact、reader-facing 页面、顶板写回与本轮日志，不做混提。

## 这轮做了什么改动
1. 新增 clean-replication 脚本：
   - `scripts/build_rank74_adx_er_trend_readiness_clean_replication.py`
2. 固定复用本地 `BTC/ETH/SOL 120d 15m` cache，统一冻结到：
   - `signal 当根及之前数据`
   - `next-bar open`
   - `no-overlap`
   - `hold 8 bars`
3. 只接三条当前 desk 主线 archetype：
   - `ema_psar_long`
   - `fib_retest_long`
   - `breakout_short`
4. 只比较五臂，不扩研究：
   - `baseline`
   - `adx_only`
   - `er_only`
   - `adx_plus_er`
   - `adx_plus_er_plus_di`
5. 产出文件：
   - `reports/artifacts/scout_rank74_adx_er_trend_readiness_15m/overall_summary.csv`
   - `reports/artifacts/scout_rank74_adx_er_trend_readiness_15m/asset_summary.csv`
   - `reports/artifacts/scout_rank74_adx_er_trend_readiness_15m/time_pocket_summary.csv`
   - `reports/artifacts/scout_rank74_adx_er_trend_readiness_15m/trade_log.csv`
   - `reports/site/factors/scout_rank74_adx_er_trend_readiness_15m/report.html`
   - `reports/site/reading/repo_scout/rank74_adx_er_trend_readiness_clean_replication.html`
6. 用脚本把本轮 hard verdict 追加写回 `docs/TODO.md` 顶部 `Next 3 bot3 runs`。

## 验证 / 证据
### 1) `breakout_short`：ADX+ER 确实减了噪，但还没减到能升格
- `baseline @ 6bps/side`：
  - `mean_total_return≈-2.58%`
  - `positive_asset_ratio=0/3`
  - `mean_trades≈20.3`
  - `mean_false_break_ratio≈44.57%`
- `adx_plus_er_plus_di @ 6bps/side`：
  - `mean_total_return≈-0.48%`
  - `positive_asset_ratio≈33.33%`
  - `mean_trades≈8.3`
  - `trade_count_retention≈41.22%`
  - `mean_false_break_ratio≈41.11%`
- 结论：这条 short archetype 上确实有一些 shared anti-chop 味道，但改善仍主要靠砍掉近六成样本；还不足以单独把整条 gate 推成 candidate。

### 2) `ema_psar_long`：趋势口袋过滤没有把 raw lane 救活
- `baseline @ 6bps/side`：
  - `mean_total_return≈-5.41%`
  - `positive_asset_ratio≈33.33%`
  - `mean_trades≈34.7`
  - `mean_false_break_ratio≈32.75%`
- `adx_plus_er_plus_di @ 6bps/side`：
  - `mean_total_return≈-5.90%`
  - `positive_asset_ratio=0/3`
  - `mean_trades≈11.3`
  - `trade_count_retention≈32.72%`
  - `mean_false_break_ratio≈29.29%`
- 结论：它把 long 样本切得更少，但 post-cost 结果并没有更好；这不是“更干净”，而是“更少但仍不够好”。

### 3) `fib_retest_long`：单点看着顺眼，但 retention 已经低到失真边缘
- `baseline @ 6bps/side`：
  - `mean_total_return≈+0.88%`
  - `positive_asset_ratio≈33.33%`
  - `mean_trades≈11.0`
  - `mean_false_break_ratio≈36.36%`
- `er_only @ 6bps/side`：
  - `mean_total_return≈+2.16%`
  - `positive_asset_ratio≈100.00%`
  - `mean_trades≈3.0`
  - `trade_count_retention≈27.27%`
  - `mean_false_break_ratio≈0.00%`
- `adx_plus_er_plus_di @ 6bps/side`：
  - `mean_total_return≈+0.12%`
  - `positive_asset_ratio≈33.33%`
  - `mean_trades≈0.7`
  - `trade_count_retention≈6.06%`
  - `mean_false_break_ratio≈0.00%`
- 结论：这条线说明 `ER` 对“回踩后是不是还在顺推”有一点局部价值，但一旦加上 ADX+DI，交易数已经接近失真，不够拿来证明 shared gate 可升格。

### 4) time-pocket honesty：只有局部 pocket 比 baseline 好，谈不上跨期稳定
- `breakout_short / adx_plus_er_plus_di`：
  - `bucket_1≈+0.51% / 33.33%`
  - `bucket_2≈-1.45% / 33.33%`
  - `bucket_3≈-2.33% / 0.00%`
- `ema_psar_long / adx_plus_er_plus_di`：
  - `bucket_1≈-15.59% / 0.00%`
  - `bucket_2≈+2.14% / 66.67%`
  - `bucket_3≈-5.85% / 0.00%`
- 结论：不是“普遍变好，只差一点”，而是只有局部 pocket 变干净，跨时间稳定性还不够诚实。

## Hard verdict
**`Rank 74 / ADX+ER price-only trend-readiness gate = park / evidence pool`**

## 为什么是这个 verdict
- 它不是完全没信号：`breakout_short` 确实从 `-2.58%` 拉到 `-0.48%`，`fib_retest_long / er_only` 也显示出一点局部 alpha-candidate 味道。
- 但 shared 主读法 `adx_plus_er_plus_di` 没有在三条 archetype 上同时给出足够诚实的改善：
  - `breakout_short` 改善主要来自砍单；
  - `ema_psar_long` 更少但没更好；
  - `fib_retest_long` 在主读法下 retention 已低到 `≈6.06%`，不够拿来证明 shared gate 可部署。
- 因此当前更诚实的 desk 读法不是继续给它第二轮预算，而是直接压回 `park / evidence pool`，并把 `Scout Seat` 主资源还给下一条 fresh paper / repo source。

## 对交易台顺序的影响
- 本轮后，`Rank 74` 不应继续占默认 fast-lane 头部。
- 若下一轮 `EMA` 仍 `waiting_not_due`，默认顺序应切回：
  1. `fresh paper / repo source re-rank（默认比较 GCR extreme-sentiment exhaustion veto > one-regime-per-session overlay > 其他 fresh pool）`
  2. 若这一层本轮也 exhausted，再回退到 `Rank 35b > Rank 16b`
  3. 再其次才是 `tiny-live plumbing`

## 最小验证
- 已实际运行：
  - `python3 /root/clawd/jerry/momentum/scripts/build_rank74_adx_er_trend_readiness_clean_replication.py`
- 已确认输出文件存在：
  - `reports/artifacts/scout_rank74_adx_er_trend_readiness_15m/overall_summary.csv`
  - `reports/site/factors/scout_rank74_adx_er_trend_readiness_15m/report.html`
  - `reports/site/reading/repo_scout/rank74_adx_er_trend_readiness_clean_replication.html`
- 已确认 `docs/TODO.md` 顶板写回成功。

## 风险 / 边界
- 这轮只做了最小 clean replication，不代表 `ADX / ER` 在所有执行框架里都没价值；更像是说明：**当它被压成三条主线共用的单一 shared gate 时，当前证据还不够升格。**
- 当前结果更支持“`ER only` 在 Fib 类 setup 上可做后续局部观察”，不支持“`ADX+ER+DI` 已是可直接共用的 desk spine”。
- 若以后继续回看这条线，应该优先按已暴露的局部价值拆层重看，而不是继续围着当前 shared 主读法写 admission / closeout 近义文案。

## 下一步建议
- 直接按 `Run 2` 回到 **fresh paper / repo source re-rank**，先比较：
  - `GCR extreme-sentiment exhaustion veto`
  - `one-regime-per-session overlay`
  - `docs/RECENT_PAPER_SEEDS.md` / `research/quant_digests/INDEX.md` / validated shortlist 里的其他 fresh source
- 只有 fresh source 这一层本轮也 exhausted，才回退到 `Rank 35b > Rank 16b`。

## Commit hash
- 未提交。
- 原因：git 工作区存在大量与本轮无关的脏文件 / 未跟踪文件，当前不适合安全 selective commit。
