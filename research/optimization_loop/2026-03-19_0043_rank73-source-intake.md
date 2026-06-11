# Rank 73 / PSAR close-confirmed follow-up gate source intake（guard-passed）

## 轮次定位
- 时间：2026-03-19 00:43 UTC
- 席位：`Scout Seat`
- 本轮主点：`Run 2 / Rank 73 source intake + 两条轻量诚实守门`
- 紧邻子点：`TODO 顶板顺序刷新`

## 开始前检查
- `Run 1 / EMA due-check`：最新 `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 继续显示全 desk 当前无 `due-now / overdue` lane；最早 due 点仍是 `A股三条 lane -> 2026-03-19 07:00 UTC`，因此 `Paper Seat / EMA` 仍是真 `running paper / waiting_not_due`。
- `P3 continuity`：`reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json` 继续是 `new_closed_trades_appended=0`，当前没有新的 `P3 status-changing event` 值得 bot3 回头挤占 continuity。
- 上一轮 `Rank 72` 已在 minimal clean replication 后给出 **`park / evidence pool`** hard verdict；因此按顶板最新 `Next 3`，本轮合法主动作必须切到下一条 fresh source，而不是继续回头磨 `Rank 72` 或 `P3` 托管位。
- git 工作区仍有大量与本轮无关的脏文件 / 未跟踪文件；本轮只新增 `Rank 73` source-intake artifact、reader-facing 页面、`TODO` 顶板写回与本轮日志，不做混提。

## 为什么这轮选 Rank 73
当前允许动作按边际价值重排后，最诚实的顺序已经是：
- `Rank 73 / PSAR close-confirmed follow-up gate`
- `Rank 35b`
- `Rank 16b`
- `tiny-live plumbing`

先认领 `Rank 73` 的原因：
1. `Rank 72` 已经在允许预算内交出 hard verdict，fresh source 队列自然往下走到 `Rank 73`；
2. 它不是继续发明新大框架，而是给 `PSAR` 一个更诚实的岗位：**close-confirmed flip + 第 N 根 trend bar** 的 shared follow-up gate；
3. 这条线直接服务当前 desk 主线里的 `EMA / PSAR raw alpha focus` 和 `breakout-short follow-up`，比回头磨 `Rank 35b / 16b` 更贴主线；
4. 它满足当前 Scout Seat 预算：先 `source intake -> guard-passed`，若通过，再给 `1` 次最小 clean replication。

## 这轮冻结的两条轻量诚实守门
- `trade on`：base setup 继续负责方向与原始 trigger；`PSAR` 只负责回答这次翻向是否已经 `close-confirmed`，以及是否值得等到第 `N` 根 trend bar 再放行。首轮冻结三臂：
  - `N=1`：close-confirmed 后立刻进（最接近 raw PSAR）
  - `N=2`
  - `N=3`
- `trade off`：若只是 wick 穿越 PSAR、`close` 没有真正越过上一根 `psar`，或 follow-up bar 根数还没到 `N`，则不放行；它不能单独开仓，也不能顺手改原 setup 的方向。
- `lookahead / repaint / leakage`：源码里的核心规则是 `close <= psar[1]` / `close >= psar[1]` 才翻向，且 `strategy.entry(... when = trend_bars == ±entry_bars)` 把第 `N` 根 follow-up 明确写成可复刻条件，源码层未见一眼可判死刑的未来函数；但 desk 迁移必须统一冻结成 `signal 当根及之前数据 + next-bar open + no-overlap`，不得把同 bar close flip 与同 bar 成交混成乐观填单，也不得用 signal 后的 trend_bars 回填 admission。

## 本轮新增产物
1. Source-intake 构建脚本：
   - `scripts/build_rank73_psar_close_confirmed_followup_source_intake.py`
2. Source-intake artifact：
   - `reports/artifacts/literature/scout_rank73_psar_close_confirmed_followup_source_intake_card.csv`
3. Reader-facing 页面：
   - `reports/site/reading/repo_scout/rank73_psar_close_confirmed_followup_source_intake.html`
4. Queue-facing 更新：
   - `docs/TODO.md` 顶部 `Next 3 bot3 runs`

## Hard verdict
**`Rank 73 / PSAR close-confirmed follow-up gate = guard-passed / admit_to_clean_replication_queue`**

## 为什么是这个 verdict
- 规则能清楚写成 `trade on / trade off`：它只是在原 setup 之上回答“这次 flip 是否真的 close-confirmed、要不要再等第 2/3 根”，不是新的独立 alpha；
- 源码里的关键规则足够清楚，且没有一眼可判死刑的 `lookahead / repaint / leakage`；
- 首轮实现便宜：只需要现有 `BTC/ETH/SOL 15m` cache，就能比较 `raw_trigger / close_confirmed_N1 / N2 / N3`；
- 但它现在仍只是 admitted，不是已验证 alpha；下一轮若 clean replication 发现改善只是靠大幅砍交易数、或对 `EMA / breakout-short` 不够共享，就应快速压回 `park / evidence pool`。

## 对交易台顺序的影响
- 当前最新 `Next 3` 应更新为：
  - `Run 1 = EMA due-check only`
  - `Run 2 = 若 Rank 73 已 guard-passed 且 EMA 仍 waiting_not_due，则立刻给它 1 次最小 clean replication`
  - `Run 3 = 只有 Rank 73 也给出 hard verdict 或 fresh source 这一层 exhausted 时，才回退到 Rank 35b > Rank 16b > tiny-live plumbing`
- 本轮后，`Scout Seat` 的合法头部已不再是 `Rank 72`，而是 `Rank 73 / PSAR close-confirmed follow-up gate`。

## 最小验证
- 已实际运行：
  - `python3 /root/clawd/jerry/momentum/scripts/build_rank73_psar_close_confirmed_followup_source_intake.py`
- 已确认输出文件存在：
  - `reports/artifacts/literature/scout_rank73_psar_close_confirmed_followup_source_intake_card.csv`
  - `reports/site/reading/repo_scout/rank73_psar_close_confirmed_followup_source_intake.html`
- 已确认 `TODO.md` 顶板写回成功。

## 风险 / 边界
- 这条线来自老 repo 的工程规则，不是高等级学术证据；值钱的是规则口径清楚，不是原仓库绩效可直接照抄。
- `N=2/3` 很容易只是“少做很多单，所以看起来没那么差”；若 retention 掉太快，就只配停在 shared follow-up veto。
- 这轮只做到 source intake + 两条轻量诚实守门，不展开 clean replication，也不顺手去开第二条 fresh source。

## 下一步建议
- 直接按顶板切到 **`Rank 73 minimal clean replication`**。
- 默认只比较 `raw_trigger / close_confirmed_N1 / N2 / N3` 四臂，不要把它扩成新的 PSAR 大研究。

## Commit hash
- 未提交。
- 原因：git 工作区存在大量与本轮无关的脏文件 / 未跟踪文件，当前不适合安全 selective commit。
