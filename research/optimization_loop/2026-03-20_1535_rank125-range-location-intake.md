# Rank 125 / range location veto gate source intake

## 为什么这次选这个
- 先按 desk 规则再次执行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`；结果继续如实返回：`EMA / Paper Seat` 仍是 `waiting_not_due`，最近 due 约为美股 `4.4h`、Crypto `8.4h`、创业板ETF `63.4h`。
- 因此这轮不能回头磨 `Rank 112 / 111` 这类已 `budget used` 的旧 `P1`，也不该去消费 `Rank 122` 的 `P3 continuity` 预算；按顶板只能回到 fresh intake。
- 重新比较 `RECENT_PAPER_SEEDS / quant_digests / validated shortlist` 后，这轮选择把 `2026-03-20 15:30 UTC` 的 digest 正式冻结为 **`Rank 125 / range location veto gate`**：它更像三条主线共用的快速 veto/confirm 层，而且只用公开 OHLCV 就能 clean-room，不需要新重型数据。

## 做了什么改动
1. 运行 `EMA due-check first`，确认当前全 desk 仍是 `waiting_not_due`。
2. 把 fresh source 正式编号为 **`Rank 125 / range location veto gate`**。
3. 完成两条轻量诚实守门并把角色边界写死：
   - 它不是独立 alpha；
   - 只配先当 `breakout-short` 的 no-chase veto，与 `Fib retest_hold / EMA-PSAR long` 的 reclaim-confirm layer；
   - 定义冻结为 `RL_n = (close - rolling_low_n) / (rolling_high_n - rolling_low_n + 1e-9)`；
   - clean replication 必须统一 `signal 当根及之前数据 + next-bar open + no-overlap`。
4. 写入最小 reader-facing 落点：
   - `reports/artifacts/literature/scout_rank125_range_location_veto_source_intake_card.csv`
   - `reports/site/reading/repo_scout/rank125_range_location_veto_source_intake.html`
5. 最小更新顶板 `docs/TODO.md`：
   - 把当前 active Scout 主点写成 `Rank 125 / range location veto gate`；
   - 更新 active Scout 顺序；
   - 把 `Next 3` 前推为：`Run 1 EMA due-check -> Run 2 Rank 125 minimal clean replication -> Run 3 根据 Rank 125 verdict 决定 promote/park 或回 fresh intake`。

## 验证 / 证据
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due` 输出继续明确：当前没有 `due-now / overdue lane`，不允许伪造 refresh。
- digest 的核心可复用旁支已经足够清楚：不是照搬论文 CNN 主叙事，而是只偷 `range location` 这条可解释旁支，翻成 15m desk 上的 shared veto/confirm 读数。
- 本轮 reader-facing 页面与 source-intake artifact 已实际落地，可供后续 clean replication 直接承接。

## 当前硬结论
**`Rank 125 / range location veto gate = guard-passed / admit_to_clean_replication_queue`**。

翻成人话：这条线值得拿 **1 次最小 clean replication** 预算，但它当前只配先回答：
- short 侧是不是已经贴着近期区间下沿、别再追；
- long retest 侧是不是已经从低位重新被接住。

它还不是新策略，更不配抢 `Live Seat`。

## 风险 / 边界
- 论文主样本是股票日频，不是 crypto 15m；本轮只借“range location”这个可解释旁支，不搬运原论文主模型收益表。
- 若后续 clean replication 的改善主要来自明显砍样本，而不是更诚实地降低失败率，就应直接 `park`。
- 当前 repo 工作区非常脏（本轮检查约 `1895` 条脏文件），不能安全混提。

## 下一步建议
- 若下一轮 `EMA` 仍 `waiting_not_due`，只给 `Rank 125` **1 次最小 clean replication**：
  - 固定 `BTC/ETH/SOL 120d 15m` 本地 cache；
  - 只比较 baseline vs RL veto/confirm 的最小版本；
  - 主看 `post-cost expectancy / failure-before-target / trade_count_retention`；
  - 若至少两条 baseline 在不过度掉交易数的前提下保留 honest uplift，再决定 `keep_P1 / promote_P2 / park`。

## Commit hash
- 未提交。
- 原因：工作区存在大量与本轮无关的脏文件，当前不适合做安全 selective commit。
