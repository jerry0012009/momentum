# 2026-03-19 01:03 UTC｜Rank 73 / PSAR close-confirmed follow-up gate 最小 clean replication

## 轮次定位
- 席位：`Scout Seat`
- 本轮主点：`Run 2 / Rank 73 minimal clean replication`
- 紧邻子点：`TODO` 顶板 `Next 3 bot3 runs` 顺序刷新

## 为什么这轮选这个
- 先按顶板要求复核 `Run 1 / EMA due-check only`：`reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 仍显示全 desk 当前无 `due-now / overdue` lane，最近 due 点仍是 `A股三条 lane -> 2026-03-19 07:00 UTC`，因此 `Paper Seat / EMA` 当前是真 `running paper / waiting_not_due`。
- 再复核 `P3 continuity`：`reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json` 继续是 `new_closed_trades_appended=0`，当前没有新的 status-changing event 值得 bot3 回头挤占 `P3` 托管位。
- `Rank 73` 在上一轮已完成 `source intake + 两条轻量诚实守门`，并且顶板最新 `Next 3` 已明确写成：若 `EMA` 仍 `waiting_not_due`，就立刻给 `Rank 73` 一次最小 clean replication。
- git 工作区仍有大量与本轮无关的脏文件 / 未跟踪文件；本轮只新增 `Rank 73` clean-replication 相关脚本、artifact、reader-facing 页面、顶板写回与本轮日志，不做混提。

## 这轮做了什么改动
1. 新增 clean-replication 脚本：
   - `scripts/build_rank73_psar_close_confirmed_followup_clean_replication.py`
2. 固定复用本地 `BTC/ETH/SOL 120d 15m` cache，统一冻结到：
   - `signal 当根及之前数据`
   - `next-bar open`
   - `no-overlap`
   - `hold 8 bars`
3. 只接两条当前 desk 主线 archetype：
   - `ema_psar_long`
   - `breakout_short`
4. 只比较四臂，不扩研究：
   - `raw_trigger`
   - `close_confirmed_n1`
   - `close_confirmed_n2`
   - `close_confirmed_n3`
5. 产出文件：
   - `reports/artifacts/scout_rank73_psar_close_confirmed_followup_15m/overall_summary.csv`
   - `reports/artifacts/scout_rank73_psar_close_confirmed_followup_15m/asset_summary.csv`
   - `reports/artifacts/scout_rank73_psar_close_confirmed_followup_15m/time_pocket_summary.csv`
   - `reports/artifacts/scout_rank73_psar_close_confirmed_followup_15m/trade_log.csv`
   - `reports/site/factors/scout_rank73_psar_close_confirmed_followup_15m/report.html`
   - `reports/site/reading/repo_scout/rank73_psar_close_confirmed_followup_clean_replication.html`
6. 用脚本把本轮 hard verdict 追加写回 `docs/TODO.md` 顶部 `Next 3 bot3 runs`。

## 验证 / 证据
### 1) `breakout_short`：close-confirmed 并没有带来更诚实的 follow-up
- `raw_trigger @ 6bps/side`：
  - `mean_total_return≈-2.58%`
  - `positive_asset_ratio=0/3`
  - `mean_trades≈20.3`
  - `mean_flip_to_fail_rate≈20.82%`
  - `mean_false_break_ratio≈44.57%`
- `close_confirmed_n2 @ 6bps/side`：
  - `mean_total_return≈-2.82%`
  - `positive_asset_ratio=0/3`
  - `mean_trades≈18.7`
  - `trade_count_retention≈92.75%`
  - `mean_flip_to_fail_rate≈22.02%`
  - `mean_false_break_ratio≈45.70%`
- 结论：`N=2` 对这条 short archetype 不是减噪，而是**略差**；既没减少 early fail，也没减少 false break，收益还更差。

### 2) `ema_psar_long`：N=2 / N=3 主要是靠砍单，但并没有把 setup 救活
- `raw_trigger @ 6bps/side`：
  - `mean_total_return≈-5.41%`
  - `positive_asset_ratio≈33.33%`
  - `mean_trades≈34.7`
  - `mean_flip_to_fail_rate≈39.47%`
  - `mean_false_break_ratio≈32.75%`
- `close_confirmed_n2 @ 6bps/side`：
  - `mean_total_return≈-6.21%`
  - `positive_asset_ratio=0/3`
  - `mean_trades≈20.7`
  - `trade_count_retention≈59.47%`
  - `mean_flip_to_fail_rate≈44.94%`
  - `mean_false_break_ratio≈34.69%`
- `close_confirmed_n3 @ 6bps/side`：
  - `mean_total_return≈-6.11%`
  - `positive_asset_ratio=0/3`
  - `mean_trades≈20.3`
  - `trade_count_retention≈58.52%`
  - `mean_flip_to_fail_rate≈45.64%`
  - `mean_false_break_ratio≈35.22%`
- 结论：`N=2/3` 在 long archetype 上也没有把 flip 变得更诚实，反而是**交易更少、结果仍更差**。

### 3) time-pocket honesty 也不支持升格
- `breakout_short / close_confirmed_n2`：
  - `bucket_1≈+0.82% / 33.33%`
  - `bucket_2≈-3.43% / 33.33%`
  - `bucket_3≈-9.35% / 0.00%`
- `ema_psar_long / close_confirmed_n2`：
  - `bucket_1≈-13.66% / 33.33%`
  - `bucket_2≈-2.32% / 33.33%`
  - `bucket_3≈-5.97% / 33.33%`
- 结论：不是“只有某个 pocket 差一点”，而是主 pocket 大多仍不够诚实。

## Hard verdict
**`Rank 73 / PSAR close-confirmed follow-up gate = park / evidence pool`**

## 为什么是这个 verdict
- 它通过了 source-intake 阶段的轻量诚实守门，但最小 clean replication 没有证明 `close-confirmed + wait N bars` 真能减少 `EMA / breakout-short` 两条主线上的早死或假突破。
- `N=2/3` 的主要效果是减少交易数，不是改善质量；而且 retention 并没有低到特别离谱，却仍把 post-cost 结果做得更差，这说明问题不只是“样本太少”，而是 gate 本身没有带来更好的 follow-up。
- 因此当前更诚实的 desk 读法不是继续给它第二轮最小检查，而是直接压回 `park / evidence pool`，把 `Scout Seat` 主资源还给下一条 fresh paper / repo source。

## 对交易台顺序的影响
- 本轮后，`Rank 73` 不应继续占默认 fast-lane 头部。
- 若下一轮 `EMA` 仍 `waiting_not_due`，默认顺序应切回：
  1. `fresh paper / repo source re-rank（来自 RECENT_PAPER_SEEDS / quant_digests / validated shortlist）`
  2. 若这一层本轮也 exhausted，再回退到 `Rank 35b > Rank 16b`
  3. 再其次才是 `tiny-live plumbing`

## 最小验证
- 已实际运行：
  - `python3 /root/clawd/jerry/momentum/scripts/build_rank73_psar_close_confirmed_followup_clean_replication.py`
- 已确认输出文件存在：
  - `reports/artifacts/scout_rank73_psar_close_confirmed_followup_15m/overall_summary.csv`
  - `reports/site/factors/scout_rank73_psar_close_confirmed_followup_15m/report.html`
  - `reports/site/reading/repo_scout/rank73_psar_close_confirmed_followup_clean_replication.html`
- 已确认 `docs/TODO.md` 顶板写回成功。

## 风险 / 边界
- 这轮只做了最小 clean replication，不代表 PSAR 在所有更复杂执行框架里都没用；但至少当前这条 `close-confirmed follow-up gate` 作为共享 overlay，**不够诚实**。
- `breakout_short` 的 `close_confirmed_n1` 与 `raw_trigger` 结果重合，说明当前这一实现下，第一根 close-confirmed 基本就是 raw 口径本身，真正新增信息只出现在 `N=2/3`；而 `N=2/3` 又没带来改善。
- 当前没有继续给它第二轮 cheap check 的理由，否则就会违反顶板“做完这一手最小会改变 verdict 的检查后，应更偏向升格 / park”的预算纪律。

## 下一步建议
- 直接按 `Run 3` 回到 **fresh paper / repo source re-rank**，先从：
  - `docs/RECENT_PAPER_SEEDS.md`
  - `research/quant_digests/INDEX.md`
  - `reports/artifacts/literature/validated_alpha_shortlist_2026-03-10.md`
  中重新认领 1 条新 source intake。
- 只有 fresh source 这一层这轮也 exhausted，才回退到 `Rank 35b > Rank 16b`。

## Commit hash
- 未提交。
- 原因：git 工作区存在大量与本轮无关的脏文件 / 未跟踪文件，当前不适合安全 selective commit。
