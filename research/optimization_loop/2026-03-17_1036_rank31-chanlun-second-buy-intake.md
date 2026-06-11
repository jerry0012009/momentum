# 2026-03-17 10:36 UTC · Rank 31 chanlun-pro second-buy fresh intake

## 本轮归属
- Desk lane：`Run 2 / Scout Fast Lane`
- 先执行顶板守门结论：`EMA / Paper Seat` 当前仍是 `waiting_not_due`，全 desk 没有 `due-now / overdue` lane。
- 因此按当前板子规则，从 `Paper Seat` 自动切到 `Scout Seat`，且不能在 waiting-window 空转。

## repo / 最近 runs / 脏文件 / 席位状态检查
- `git status --short --branch`：工作区仍有大量与本轮无关的已修改/未跟踪文件；本轮不混提。
- 最近 runs：`1029 rank30-clean-replication-park`、`1007 rank30-trendln-channel-intake`、`1006 rank29-p3-monitoring-redwatch`、`0941 rank29-time-stability-p3`、`0925 rank29-no-overlap-honesty-check`。
- `Paper Seat / EMA`：真实 `waiting_not_due`，当前最靠前 due 仍是 `美股 1d+1wk -> 2026-03-17 20:00 UTC`。
- `Live Seat`：仍无 bot2 新 promoted candidate；继续暂空。
- `Scout Seat`：
  - `Rank 17 / Rank 2 / Rank 29` 当前都没有新的真实 `append/review` need；
  - `Rank 26 / Rank 27 / Rank 28 / Rank 30` 已 park；
  - 因此本轮默认应回到新的 `paper / repo based 5m / 15m crypto` fresh intake。

## active Scout 边际价值比较（本轮前）
- `Rank 29 / Rank 17 / Rank 2`：都已到 `P3/P2` 的最小接线边界，当前没有新的真实 append/review row；继续补近义 wiring 边际价值低。
- `Rank 30`：已完成最小 clean replication，并给出明确 `park / evidence pool`；不应再重开。
- `Rank 5 Polymarket lag-arb`：需要 prediction-market 执行数据，当前不是最便宜诚实的一轮动作。
- `Rank 6 BTC-equity proxy spread`：需要同步 equity proxy 数据，也不如纯 crypto 15m 候选直接。
- **`Rank 31 chanlun-pro second-buy / breakout-retest continuation gate`**：repo-based、5m/15m 直接可落、又比继续扩 trendline 旁支更贴近当前已存活的 pullback / recovery 家族；因此当前边际价值最高。

## 本轮主点 + 紧邻子点
- 主点：把 `Rank 31 chanlun-pro second-buy / breakout-retest continuation gate` 落成新的 fresh-intake artifact。
- 紧邻子点：把 hard verdict 同步回 `TODO` 顶板与 reader-facing 页面，避免下一轮再误回已 park 的旧线。

## 两条轻量诚实守门（先过）
1. **trade on / trade off 可清楚写成规则**
   - `trade on = higher_tf_bias_up + 已确认结构突破 + pullback 不跌破最新因果确认结构低点/中枢下沿 + close 重新站上 pre-pullback reclaim level`
   - `trade off = 没有已确认结构突破 / pullback 跌破结构地板 / 回抽后始终无法 reclaim 触发位`
2. **没有把 lookahead / repaint 偷塞进 intake**
   - 明确遵守 `chanlun-pro` README 自己写明的 `逐 Bar / 增量确认` 口径；
   - 所有 pivot / pen / zone 代理都只能用因果确认版本，不能把事后画出的结构回填成入场依据。

## 做了什么改动
1. 新增脚本：
   - `scripts/build_rank31_chanlun_second_buy_source_intake.py`
2. 新增 artifact：
   - `reports/artifacts/literature/scout_rank31_chanlun_second_buy_source_intake_card.csv`
3. 新增 reader-facing 页面：
   - `reports/site/reading/trendline_alpha_scout/rank31_chanlun_second_buy_source_intake.html`
4. 更新 reader-facing 入口：
   - `reports/site/reading/trendline_alpha_scout/report.html`
   - 新增 `Rank 31 · chanlun-pro second-buy：fresh intake` 卡。
5. 更新 desk 顶板：
   - `docs/TODO.md`
   - 把当前 fresh-intake 默认主资源明确收敛到 `Rank 31`；下一轮若 `EMA` 仍未 due、`Rank 29 / Rank 17 / Rank 2` 仍无真实 append/review row，默认只允许做 `Rank 31` 的 1 次最小 clean replication。

## 当前 hard verdict
- **`Rank 31` 当前 hard verdict = `admit_to_clean_replication_queue`。**
- 更直白地说：这轮只回答“下一条新的 `paper / repo based 15m crypto` 候选应该是谁”。
- 当前最诚实答案是：**`chanlun-pro` 的 `二买 / 回抽确认` 程序化近似，比重开已 park 的 `Rank 30` 更值得拿下一轮最小 clean replication 预算。**
- 但这轮**没有**偷把它升到 `P1 / P2`；下一轮若要继续认领，也只允许做 1 次最小 clean replication：
  - `raw pullback-recovery baseline`
  - `structural higher-low reclaim`
  - `center-breakout-retest-reclaim`
  - 先看 `post_cost_return / false_reclaim_ratio / trade_count / no_trade_ratio`
  - 若 trade count 过薄或成本后继续转负，就快速 `park`。

## 最小验证
已执行并通过：
1. `python3 scripts/build_rank31_chanlun_second_buy_source_intake.py`
2. `python3 -m py_compile scripts/build_rank31_chanlun_second_buy_source_intake.py`
3. 文本抽查：
   - `docs/TODO.md` 已包含 `Rank 31 chanlun-pro second-buy` 与 `admit_to_clean_replication_queue`
   - `reports/site/reading/trendline_alpha_scout/report.html` 已包含新的 `Rank 31` 卡
   - `reports/site/reading/trendline_alpha_scout/rank31_chanlun_second_buy_source_intake.html` 已包含 `center-breakout-retest-reclaim` 与 `admit_to_clean_replication_queue`

## reader-facing 落点
- `reports/site/reading/trendline_alpha_scout/rank31_chanlun_second_buy_source_intake.html`
- `reports/site/reading/trendline_alpha_scout/report.html`
- `docs/TODO.md` 顶部 `TRADING DESK BOARD`

## 风险 / 边界
- 这轮**没有**追新 bar；
- **没有**重跑任何重型 clean replication；
- **没有**同时打开第二个 fresh candidate；
- 这轮交付的是一张 honest source-intake card + 下一轮单步执行约束，不是假装已经完成 clean replication。

## 下一步建议
1. 下一轮若 `EMA` 仍未 due，就直接做 `Rank 31` 的最小 clean replication；
2. 严格只跑一刀：`raw pullback-recovery baseline` vs `structural higher-low reclaim` vs `center-breakout-retest-reclaim`；
3. 若成本后没有形成清楚改善，快速压回 `park / evidence pool`，不要让它长期停在 intake 文案态。

## Commit hash
- 未提交。
- 原因：当前 repo 存在大量与本轮无关的脏文件与未跟踪文件，避免混提。
