# 2026-03-16 19:42 UTC｜Scout Seat：Rank 2 narrow paper refresh seed rows（基于现有历史样本）

## 为什么这轮选这个
按 `TRADING DESK BOARD` 执行顺序先判断席位：

- `Run 1 / Paper Seat (EMA)`：当前仍是 `waiting_not_due`，不能把整轮耗在等新 bar；
- `Run 2 / Scout Seat`：默认主资源位；
- `Live Seat` 仍暂空，且没有 bot2 新 promoted candidate 点名。

本轮先比较 active Scout 候选边际价值：

1. **Rank 2 combo_all（当前 narrow paper pilot approved）**
   - 已有 `paper candidate admission + monitoring + ledger template`；
   - 若继续认领，按 board 7.6 只能做 `paper ledger / monitoring / refresh / review` 最小接线，或一刀会改变 paper verdict 的检查；
   - 边际价值仍高，因为能直接把“模板”推进成“可回放 seed row”。
2. **Rank 4b stat-arb**
   - 已在 `18:53` 给出 hard verdict：`park / evidence pool`；
   - 没有新数据源/新 universe/新 spec，不应继续占默认主资源。
3. **Rank 5/6 source intake 候补**
   - 当前更像新 intake，离本轮 desk 主线（把已晋级候选压成可执行 paper plumbing）更远。

因此本轮主点固定为：
- **把 Rank 2 的 narrow paper pilot 从“ledger 模板”推进到“refresh seed rows（可回放最小样本）”**。

紧邻子点：
- 同步 reader-facing 页面与 trial_meta verdict，确保不是只写日志/邮件。

## 开始前检查
- `git status --short`：repo 内外仍有大量与本轮无关脏文件/未跟踪文件，本轮不混提。
- 最近 runs：
  - `2026-03-16_1934_rank2-narrow-paper-ledger-template.md`
  - `2026-03-16_1853_rank4b-time-stability-park.md`
  - `2026-03-16_1838_rank4b-clean-replication.md`
- 当前 Rank 2 trial_meta 状态（轮前）：
  - 已有 `paper_candidate_admission_verdict`
  - 已有 `paper_candidate_monitoring_verdict`
  - 已有 `narrow_paper_pilot_ledger_verdict`
  - 但尚无可回放 `refresh seed rows` 产物。

## 本轮改动
### 1) `scripts/build_volume_supportflip_higherlow_first_verdict.py`
新增路径：
- `reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_narrow_paper_pilot_refresh_seed_rows.csv`

新增函数：
- `build_narrow_paper_pilot_refresh_seed_rows(trades_df)`
  - 从已有 `trades.csv` 中仅取 `combo_all`；
  - 对每个资产（BTC/ETH/SOL）抽取最新一条交易作为 replay seed；
  - 不拉新数据，不追最新 bar。
- `derive_narrow_paper_pilot_refresh_seed_verdict(seed_rows)`
  - 产出 reader-facing headline + bullets（只用于接线与审计，不作为新 alpha 证据）。

并把新内容接入：
- `trial_meta.csv` 字段：`narrow_paper_pilot_refresh_seed_verdict`
- report 新卡片：`narrow paper pilot refresh seed rows`
- `next_step` 更新为优先基于 seed rows 补 `weekly review row`。

### 2) `scripts/build_trendline_alpha_scout_report.py`
在 Rank 2 汇总卡新增：
- `narrow paper refresh seed` verdict 行；
- 指向新 artifact：`combo_all_narrow_paper_pilot_refresh_seed_rows.csv`。

## 最小验证
已执行并通过：
1. `python3 -m py_compile scripts/build_volume_supportflip_higherlow_first_verdict.py scripts/build_trendline_alpha_scout_report.py`
2. `python3 scripts/build_volume_supportflip_higherlow_first_verdict.py`
3. `python3 scripts/build_trendline_alpha_scout_report.py`
4. `grep` 命中 reader-facing 落点：
   - `reports/site/factors/scout_volume_supportflip_higherlow_15m/report.html`
   - `reports/site/reading/trendline_alpha_scout/report.html`

## 新产物 / deployable artifact
- `reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_narrow_paper_pilot_refresh_seed_rows.csv`

当前 seed rows（每资产 1 行，来自现有历史交易）：
- BTC-USD：`2026-01-31T16:15:00Z` entry，`net_ret≈-0.69%`
- ETH-USD：`2026-03-06T17:45:00Z` entry，`net_ret≈-0.92%`
- SOL-USD：`2026-03-03T10:15:00Z` entry，`net_ret≈-0.78%`

## 硬结论（hard verdict）
- 本轮新增结论：
  - `narrow paper refresh seed：已从现有 combo_all 历史交易里抽出每个资产最新一条可回放 seed row；后续可直接用这组 row 做 paper ledger refresh / review 演练，而不需要再写抽象接线说明。`
- 解释边界：
  - 这不是新 alpha 证据，不改变 Rank 2 的策略优劣判断；
  - 这是 **paper plumbing artifact**，用于把 `narrow paper pilot` 的审计链从模板推进到可回放样本。

## 对 desk 主线的意义
- 符合 7.6：已进入 `narrow paper pilot` 的候选，继续认领时只做最小 `ledger / refresh / review` 接线。
- 相比继续写 closeout/packet，这轮确实减少了执行 gate：
  - 现在可以直接在 seed rows 上补 `weekly_review_status / operator_action`，而不是空转式文档打磨。

## 网页可见落点
- `reports/site/factors/scout_volume_supportflip_higherlow_15m/report.html`
- `reports/site/reading/trendline_alpha_scout/report.html`

## 风险 / 边界
- 当前 seed rows 为历史样本 replay seed，不代表 forward continuity；
- Rank 2 仍需保留 `idle-gap / time-pocket / BTC weak pocket` 诚实 watch，不得误写为 live-ready。

## Git / 提交
- 未提交。
- 原因：工作区存在大量与本轮无关脏文件/未跟踪文件，不适合安全 selective commit。
