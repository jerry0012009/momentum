# 2026-03-17 07:59 UTC · Rank 27 Mt.Gox neckline confirmation fresh intake

## 为什么这轮选这个
- 先检查了 repo 状态、最近 runs、当前脏文件与 desk 顶板：`EMA / Paper Seat` 在 `07:04 UTC` 的 due-follow-up 已如实消化，当前回到 `waiting_not_due`；`Rank 26` 已在 genuinely verdict-changing 最小检查后压回 `park`；`Rank 17 / Rank 2` 这两条 `P3` 当前可见的最小 `weekly review writeback` need 也都已被上一两轮消化。
- 按当前 authoritative 顺序，`P3 / P2 / P1` 没有新的高边际价值动作时，应切 fresh intake，而不是继续围着 `Rank 2 / Rank 17 / Rank 26` 打磨近义接线。
- 本轮比较了剩余 fresh-intake 候选的边际价值：
  1. `Rank 5 Polymarket lag-arb`：需要额外 prediction-market 执行数据，不适合作为当前最便宜的一轮 fast-lane 动作；
  2. `Rank 6 BTC-equity proxy spread`：需要同步 equity proxy 数据，当前不如纯 crypto 15m 候选直接；
  3. `Mt.Gox neckline confirmation / pattern-complete breakout gate`：直接贴合现有 `15m crypto breakout / retest` 语义与 Lo-style extrema 思路，不需要新数据源，最适合拿下一轮 clean replication 预算。
- 因此这轮主点不是继续做 P3 wiring，而是把新的 paper-based fresh intake 收敛成一张可直接执行的 source-intake 卡，并给出下一轮唯一允许动作。

## 本轮主点 + 紧邻子点
- 主点：把 `Mt.Gox neckline confirmation / pattern-complete breakout gate` 落成新的 `Rank 27` fresh-intake artifact。
- 紧邻子点：把这个 fresh intake 同步写回 `docs/TODO.md` 顶板与网页可见入口，让后续轮次能直接认领下一步 clean replication。

## 先过两条轻量诚实守门
1. **trade on / trade off 可清楚写成规则**
   - `trade on = pattern_complete + neckline_break + confirm_window 内至少 2 根收盘留在 neckline 外`
   - `trade off = 形态未完成 / 突破未发生 / 确认失败回落`
   - short 侧默认仍需额外 `EMA/downtrend gate`，不能直接镜像 long。
2. **不把 lookahead / repaint 混进 source-intake**
   - 论文基于 Lo-style 可编程形态与颈线确认，适合按因果 extrema + 延迟确认来实现；
   - `2-of-12 confirm` 的正确读法是**延迟入场**，不是事后偷看结果。

## 做了什么
### 1) 新增 source-intake 生成脚本
- `scripts/build_mtgox_neckline_source_intake.py`

### 2) 产出新的 Scout artifact
- `reports/artifacts/literature/scout_rank27_mtgox_neckline_source_intake_card.csv`
- `reports/site/reading/trendline_alpha_scout/rank27_mtgox_neckline_source_intake.html`

卡里明确写清了：
- 为什么它比 `Rank 5 / Rank 6` 更适合当前 fresh-intake 主资源；
- 可冻结的 `trade on / trade off`；
- 下一轮的最小 clean replication 计划：
  - `BTC / ETH / SOL perpetual`
  - `15m`
  - `raw_breakout vs neckline_confirm vs neckline_confirm_plus_retest_hold`
  - 先看 `false_break_ratio / post_cost_return / time_to_failure`

### 3) 写回 desk 顶板
- 更新 `docs/TODO.md`：
  - 在 `Rank 26` 后新增 `Rank 27 Mt.Gox neckline confirmation / pattern-complete breakout gate`；
  - 更新 `Next 3 bot3 runs` 顶部 override，明确：
    - `EMA` 继续按 `waiting_not_due` 处理；
    - `Rank 2 / Rank 17 / Rank 26` 不是本轮默认主资源；
    - fresh intake 已收敛到 `Rank 27`；
    - 下一轮只允许做它的 `1` 个最小 clean replication。

### 4) 同步 reader-facing 页面
- 更新 `reports/site/reading/trendline_alpha_scout/report.html`
  - 新增 `最新 fresh intake（Rank 27 · Mt.Gox neckline confirmation）` 卡片；
  - 直接给出本轮 hard verdict：`admit_to_clean_replication_queue`。

## 关键结果（hard verdict）
**本轮 hard verdict 不是把 Rank 27 偷升成 `P1 / P2`，而是：`admit_to_clean_replication_queue`。**

更直白地说：
- 这轮只回答“下一条 fresh intake 应该是谁”；
- 当前最诚实答案是：**`Rank 27` 比 `Rank 5 / Rank 6` 更值得吃掉下一轮 clean replication 预算**；
- 如果下一轮最小 replication 跑不出足够清楚的 `false_break_ratio / post_cost return / time_to_failure` 改善，就应快速 `park`，而不是让它长期停在 source-card 态。

## 最小验证
已执行并通过：
1. `python3 scripts/build_mtgox_neckline_source_intake.py`
2. `python3 -m py_compile scripts/build_mtgox_neckline_source_intake.py`
3. `sed -n '1,8p' reports/artifacts/literature/scout_rank27_mtgox_neckline_source_intake_card.csv`
4. `grep -n "Rank 27 Mt.Gox\|07:58 UTC\|admit_to_clean_replication_queue" docs/TODO.md`
5. `grep -n "最新 fresh intake（Rank 27\|admit_to_clean_replication_queue\|rank27_mtgox_neckline_source_intake.html" reports/site/reading/trendline_alpha_scout/report.html`

## reader-facing 落点
- `reports/site/reading/trendline_alpha_scout/rank27_mtgox_neckline_source_intake.html`
- `reports/site/reading/trendline_alpha_scout/report.html`
- `docs/TODO.md` 顶部 `TRADING DESK BOARD`

## 风险 / 边界
- 这轮**没有**追新 bar；
- **没有**重跑重型 clean replication；
- **没有**同时打开第二个 fresh candidate；
- 这轮交付的是一张 honest source-intake card + 下一轮单步执行约束，不是假装已经完成 clean replication。

## 下一步建议
1. 下一轮若仍无新的 `EMA due-now`，就直接做 `Rank 27` 的最小 clean replication；
2. 严格只跑一刀：`raw_breakout vs neckline_confirm vs neckline_confirm_plus_retest_hold`；
3. 若 `false_break_ratio / post_cost_return / time_to_failure` 没有形成清楚改善，就快速 `park`，不要把这条 fresh intake 拖成长研究线。

## Git
- 工作区存在大量与本轮无关的脏文件 / 未跟踪文件；本轮不做 commit，避免混提。
