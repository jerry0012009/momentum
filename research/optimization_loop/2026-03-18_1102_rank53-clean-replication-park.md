# 2026-03-18 11:02 UTC — Rank 53 最小 clean replication 后压回 park

## 为什么这次选这个
- 先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 检查当前席位状态。
- `Run 1 / Paper Seat`：重新读取 `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`，当前 `美股 -> 2026-03-18 20:00 UTC`、`Crypto -> 2026-03-19 00:00 UTC`、`A股 -> 2026-03-19 07:00 UTC`，全部仍是 `waiting_not_due`，没有真实 `due-now / overdue` 动作。
- 依照上轮板上写回，当前允许动作里 `Rank 53 / close-confirmed CHoCH compression gate minimal clean replication` 的边际价值高于 `Rank 35b / Rank 16b / tiny-live plumbing`，因此本轮只认领这一个主点，不并行打开第二个 fresh 候选。

## 做了什么改动
### 主点：Rank 53 最小 clean replication
- 新增脚本：
  - `scripts/build_rank53_close_confirmed_choch_clean_replication.py`
- 新增 artifact：
  - `reports/artifacts/scout_rank53_close_confirmed_choch_15m/overall_summary.csv`
  - `reports/artifacts/scout_rank53_close_confirmed_choch_15m/asset_summary.csv`
  - `reports/artifacts/scout_rank53_close_confirmed_choch_15m/time_pocket_summary.csv`
  - `reports/artifacts/scout_rank53_close_confirmed_choch_15m/trades_primary_6bps.csv`
  - `reports/artifacts/scout_rank53_close_confirmed_choch_15m/meta.csv`
- 新增 reader-facing 页面：
  - `reports/site/factors/scout_rank53_close_confirmed_choch_15m/report.html`
  - `reports/site/reading/repo_scout/rank53_close_confirmed_choch_clean_replication.html`

### 紧邻子点：authoritative board 最小写回
- 在 `docs/TODO.md` 顶部权威区追加 `2026-03-18 11:02 UTC` 补充：
  - 写回 `Rank 53` 的最小 clean replication 结果与 hard verdict；
  - 把 `Next 3` 恢复到 `fresh paper/repo intake -> Rank 35b/16b/tiny-live fallback` 的读法；
  - 同时把 `10:34 UTC` 那条“下一轮做 Rank 53 replication”的旧排班备注明确标成历史备注，避免后续误认领。

## 验证 / 证据
### 1）Paper Seat 仍是 waiting_not_due
`ema_paper_trading_due_guardrail_snapshot.csv` 当前字段里：
- `美股 1d+1wk -> next_expected_close_utc = 2026-03-18 20:00 UTC`
- `Crypto 1d+1wk -> next_expected_close_utc = 2026-03-19 00:00 UTC`
- `A股三条 lane -> next_expected_close_utc = 2026-03-19 07:00 UTC`
- `due_bucket` 全部仍是 `waiting_not_due`

这说明本轮最诚实动作仍应是 `Run 2 / Scout Seat`，而不是伪造 paper continuation。

### 2）最小 clean replication 口径
- 固定复用 `BTC/ETH/SOL 120d 15m` cache，不追新 bar；
- 先重采样 `1h`，只用 **confirmed pivot close** 构造 CHoCH / sweep 状态；
- 只在两条最小 archetype 上比较：
  - `ema_pullback_long`
  - `breakdown_reclaim_short`
- 只比较四臂：
  - `base`
  - `htf_close_trend_gate`
  - `no_choch_no_flip`
  - `liquidity_sweep_veto`
- 执行口径固定为：`15m next-bar open + no-overlap + hold 8 bars`

### 3）主读法结果
`reports/artifacts/scout_rank53_close_confirmed_choch_15m/overall_summary.csv` 显示：
- `breakdown_reclaim_short + liquidity_sweep_veto` 在 `6bps/side` 下跨资产：
  - `mean_total_return ≈ -2.88%`
  - `positive_asset_ratio = 0/3`
  - `mean_trades ≈ 8.0`
  - `mean_trade_count_retention ≈ 39.97%`
  - `mean_false_hold_4bars_rate ≈ 36.38%`
- 对照 `breakdown_reclaim_short + base`：
  - `mean_total_return ≈ -3.55%`
  - `mean_trades ≈ 20.3`
  - `mean_trade_count_retention ≈ 97.44%`
  - `mean_false_hold_4bars_rate ≈ 34.14%`

直白读法：`Rank 53` 的结构 gate 确实把亏损略微收窄了，但主要代价是把样本砍到只剩原来的约 `40%`，而且跨资产仍然 `0/3` 为正，说明改善不足以支撑继续留在 active clean-replication 队列。

### 4）time-pocket honesty
`time_pocket_summary.csv` 显示主读法 `breakdown_reclaim_short + liquidity_sweep_veto`：
- `bucket_1 ≈ -0.33% / positive_asset_ratio ≈ 33.33%`
- `bucket_2 ≈ -1.77% / positive_asset_ratio ≈ 0.00%`
- `bucket_3 ≈ -0.79% / positive_asset_ratio ≈ 33.33%`

并没有出现“最近窗口已明显翻正、只差一点 admission wording”的证据；更像是各 pocket 都偏弱。

## 当前硬结论
- **`Rank 53 / close-confirmed CHoCH compression gate = park / evidence pool`**。
- 更直白地说：它当前更像一个会切样本的结构 veto，而不是能把现有 15m base setup 真正推入 `paper candidate pool` 的 shared failure gate。
- 因此这条线本轮预算用尽，不应继续停在 `Run 2 / active clean replication` 队列。

## Reader-facing 落点
- `reports/site/factors/scout_rank53_close_confirmed_choch_15m/report.html`
- `reports/site/reading/repo_scout/rank53_close_confirmed_choch_clean_replication.html`
- `docs/TODO.md` 顶部权威板已同步写回

## 风险 / 边界
- 这仍是 desk 语义下的最小 clean-room 迁移，不是对原 repo 全量框架的完全复刻。
- 当前为了保证这一轮按时拿 hard verdict，把成本维度收窄到 `6bps/side` 主读法；没有扩成更重的多成本矩阵。
- 当前 git 工作区存在大量与本轮无关的脏文件与未跟踪产物，不安全混提。

## 下一步建议
1. 下一轮先继续 `EMA due-check only`。
2. 若仍 `waiting_not_due`，按规则回到 **fresh paper / repo based 5m / 15m crypto intake**，先从：
   - `docs/RECENT_PAPER_SEEDS.md`
   - `research/quant_digests/INDEX.md`
   - `reports/artifacts/literature/validated_alpha_shortlist_2026-03-10.md`
   再认领 1 条新的 source。
3. 只有 fresh intake 这一轮也真实 exhausted，才回退比较 `Rank 35b > Rank 16b > tiny-live plumbing`。

## Commit hash
- 未提交。
- 原因：当前 repo 存在大量与本轮无关的脏文件与未跟踪产物，不适合安全 selective commit。
