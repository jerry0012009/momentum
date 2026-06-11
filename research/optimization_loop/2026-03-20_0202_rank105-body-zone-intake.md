# 2026-03-20 02:02 UTC — Rank 105 body-defined zone re-entry honest failure verdict source intake

## Run 1 -> Run 2 执行
- Run 1：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 结果：<code>EMA = waiting_not_due</code>
  - 当前没有 <code>due-now / overdue</code> lane
  - 最近 due：<code>A股三条 lane -> 2026-03-20 07:00 UTC</code>（约 <code>5.0h</code>）
  - 脚本如实返回 <code>require-due</code> guard，不做伪 refresh
- 因此按当前 <code>TRADING DESK BOARD</code> 的 authoritative <code>Next 3</code>，本轮必须切到 <code>Scout Seat</code>，不能空转。

## 开轮检查
- branch：<code>master</code>
- repo 脏文件：<code>git status --short | wc -l = 1625</code>
- 最近 optimization logs：
  - <code>2026-03-20_0149_rank104-clean-replication-park.md</code>
  - <code>2026-03-20_0115_rank104-post-break-signflip-intake.md</code>
  - <code>2026-03-20_0054_rank103-clean-replication-park.md</code>
  - <code>2026-03-20_0009_ema-crypto-due-refresh.md</code>
- 当前席位直读：
  - <code>Paper Seat = EMA / running paper / waiting_not_due</code>
  - <code>Live Seat = 暂空</code>
  - 本轮前的 <code>Scout Seat</code> 候选顺序为：<code>body-defined zone re-entry honest failure verdict > elephant candle corridor long-bias gate > MTF CHOP charged-up count > prebreak higher-low pressure ladder context gate</code>
- <code>manual_narrow_paper_last_run_summary.json @ 2026-03-20T01:22:46Z</code> 仍是 <code>new_closed_trades_appended=0</code>，不构成 <code>P3 continuity</code> 插队理由。

## Active Scout 候选边际比较（先比较后认领）
1. **<code>body-defined zone re-entry honest failure verdict</code>**
   - 当前边际价值最高，因为它最直接服务 <code>breakout-short / Fib retest_hold / EMA-PSAR continuation</code> 共用的 honest failure verdict spine。
   - 最新 desk review 已把它写成当前默认主资源位；若这轮还继续跳过它，就属于无视顶板顺序。
2. **<code>elephant candle corridor long-bias gate</code>**
   - 是紧邻 fresh repo reserve；它比 <code>MTF CHOP</code> 更 queue-facing，但当前仍应放在 body-zone 之后。
3. **<code>MTF CHOP charged-up count</code> / <code>prebreak higher-low pressure ladder context gate</code>**
   - 前者更像 long-side veto，后者更像上下文特征；当前边际价值都低于先把 body-zone 做成 queue-facing intake。
4. **旧 <code>P1 evidence_pool</code> / <code>P3 continuity</code> / <code>tiny-live plumbing</code>**
   - 当前都不该抢主资源位。

结论：本轮只认领 <code>body-defined zone re-entry honest failure verdict</code> 的 source intake，不并开第二条候选。

## 本轮认领
- 主点：<code>Rank 105 / body-defined zone re-entry honest failure verdict</code>
- 紧邻子点：把 source intake card、reader-facing 页面、<code>TODO</code> 顶板与下一轮顺序一次写齐

## 两条轻量诚实守门（已过）
### 1) trade on / trade off
- <code>trade on</code>：只把它当 **failure-verdict / repair-boundary gate**。先有 wick breakout，再观察价格是否重新收回 parent accepted body zone；默认只有 <code>close</code> 回到 body-defined accepted zone 内，才把这次 breakout 记成 failure / 失效修复成立。
- <code>trade off</code>：若价格只是扫回 wick 区但仍未回到 body accepted zone，就不得提前判失败；它不是独立 alpha，也不该替代方向过滤与执行确认本身。

### 2) lookahead / repaint / leakage
- parent zone 必须事先冻结成 box 的最高/最低收盘价（或同义 accepted body zone），不能事后重画。
- queue-facing clean replication 必须统一成 <code>signal 当根及之前数据 + next-bar open + no-overlap</code>。
- 第一轮只允许比较 <code>wick verdict</code>、<code>body verdict</code>、<code>body verdict + non_doji</code>，不得把更晚路径、重选 parent zone 或未来修复结果倒灌回 verdict candle 当下。

## 当前硬结论
**<code>Rank 105 = guard-passed / admit_to_clean_replication_queue</code>**。

## 证据摘要（source intake 级）
- digest 级代理快检显示：同一批先 <code>wick breakout</code> 的事件里，等到 **body-zone re-entry** 再判反向，整体比 <code>wick-zone re-entry</code> 更少被噪音骗。
- 关键摘要：
  - <code>4-bar</code>：<code>body verdict ≈ -15.3bps</code>，好于 <code>wick verdict ≈ -21.4bps</code>
  - <code>8-bar</code>：<code>body verdict ≈ -11.4bps</code>，好于 <code>wick verdict ≈ -18.6bps</code>
  - long 侧改善更明显；short 侧也改善，但更温和
- 更诚实的 desk 读法：它当前更像 shared failure-verdict spine，而不是独立 alpha；值得给 1 次最小 clean replication，但前提是继续保持 body-zone 口径冻结，不偷渡更多自由度。

## 本轮交付（deployable artifact）
- artifact：
  - <code>reports/artifacts/literature/scout_rank105_body_zone_reentry_honest_failure_verdict_source_intake_card.csv</code>
- reader-facing 页面：
  - <code>reports/site/reading/repo_scout/rank105_body_zone_reentry_honest_failure_verdict_source_intake.html</code>

## 对顶板的直接影响
- <code>Paper Seat = EMA / running paper / waiting_not_due</code>
- <code>Live Seat = 暂空</code>
- <code>Scout Seat = Rank 105 / body-defined zone re-entry honest failure verdict</code>
- 当前 active Scout 顺序应改写为：
  1. <code>Rank 105 / body-defined zone re-entry honest failure verdict</code>
  2. <code>elephant candle corridor long-bias gate</code>
  3. <code>MTF CHOP charged-up count</code>
  4. <code>prebreak higher-low pressure ladder context gate</code>
  5. <code>Rank 104 / Rank 103 / Rank 102 / Rank 101 / Rank 100 / Rank 99 / Rank 98 / Rank 97 / Rank 96 / Rank 95 / Rank 94 / Rank 92 / regression-channel-width</code>
  6. <code>Rank 93 / 90 / 91 / 82 / 80 / 81</code>
  7. <code>Rank 78 / Rank 17 / Rank 2 / Rank 29 / Rank 32b</code>
  8. <code>tiny-live plumbing</code>
- 当前最新 <code>Next 3</code>：
  1. <code>Run 1 = EMA due-check only（优先盯 A股三条 lane -> 2026-03-20 07:00 UTC）</code>
  2. <code>Run 2 = 若 EMA 仍 waiting_not_due，则只给 Rank 105 1 次最小 clean replication</code>
  3. <code>Run 3 = 若 Rank 105 clean replication 直接 hard-fail / exhausted，则切 elephant candle corridor long-bias gate 的 source intake；只有这一层也 exhausted，才轮到 MTF CHOP > prebreak ladder > 旧 evidence_pool > P3 continuity > tiny-live plumbing</code>

## 最小验证
- <code>python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due</code>
  - 如实确认当前仍是 <code>waiting_not_due</code>
- 回读以下文件，确认已写入成功：
  - <code>reports/artifacts/literature/scout_rank105_body_zone_reentry_honest_failure_verdict_source_intake_card.csv</code>
  - <code>reports/site/reading/repo_scout/rank105_body_zone_reentry_honest_failure_verdict_source_intake.html</code>
  - <code>docs/TODO.md</code>

## 备注
- 本轮没有并开 <code>elephant candle corridor</code>、<code>MTF CHOP</code> 或 <code>P3 continuity</code>
- 工作区仍有大量历史脏文件；本轮未尝试整理、提交或覆盖这些无关改动
