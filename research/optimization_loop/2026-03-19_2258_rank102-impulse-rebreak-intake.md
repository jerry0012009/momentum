# 2026-03-19 22:58 UTC — Rank 102 retest 后重破 impulse extreme continuation gate source intake

## Run 1 -> Run 2 执行
- Run 1：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 结果：`EMA = waiting_not_due`
  - 当前没有 `due-now / overdue` lane
  - 最近仍是 `Crypto 1d+1wk` 进入 `due_soon`
- 因此按当前 desk 顶板，本轮合法主动作必须切到 `Scout Seat / Rank 102`，不能空转，也不能提前并开 clean replication。

## 开轮检查
- repo 工作区仍有大量与本轮无关的既有脏文件；本轮不混提、不清理。
- 当前分支：`master`。
- 最近 optimization logs 仍是：
  - `2026-03-19_2233_rank101-volume-drydown-clean-replication.md`
  - `2026-03-19_2212_rank101-volume-drydown-intake.md`
  - `2026-03-19_2200_rank100-fib-depth-clean-replication.md`
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json` 最近一次仍未出现新的 `P3 status-changing event`，因此本轮不回头挤占 `P3 continuity` 预算。

## Active Scout 候选边际比较（先比较后认领）
1. **`Rank 102 / retest 后重破 impulse extreme continuation gate`**
   - 当前顶板已明确把它排在 fresh source pool 第一位；上一轮 `Rank 101` clean replication 已如实压回 `park / evidence pool` 后，本轮默认主资源位就该切到它。
   - 它直接服务当前三条主线都缺的那层：**回踩之后，到底有没有快速重夺前一段 impulse 极值**；这比只看“回到 level 附近”更贴执行确认。
2. **`Rank 103 / confirmed extremum honest fib anchor`**
   - 仍是 reserve；只有当 `Rank 102` intake 直接 hard-fail / exhausted，才轮到它。
3. **`post-break sign-flip density` / `tiny-live plumbing`**
   - 当前都不该抢占本轮主资源位。

结论：本轮只认领 `Rank 102` 的 `source intake + 两条轻量诚实守门`，不并开第二条候选。

## 本轮认领
- 主点：`Rank 102 / retest 后重破 impulse extreme continuation gate`
- 紧邻子点：把 verdict、reader-facing 页面、`TODO` 顶板更新一次写齐

## 本轮交付（deployable artifact）
- source intake card：
  - `reports/artifacts/literature/scout_rank102_impulse_rebreak_continuation_source_intake_card.csv`
- reader-facing 页面：
  - `reports/site/reading/repo_scout/rank102_impulse_rebreak_continuation_source_intake.html`
- 参考 digest（已存在）：
  - `research/quant_digests/2026-03-19_2154_orb-impulse-rebreak-followthrough-gate.md`
  - `reports/site/reading/quant_digests/2026-03-19_2154_orb-impulse-rebreak-followthrough-gate.html`

## 两条轻量诚实守门（已过）
### 1) trade on / trade off
- `trade on`：只把它当 **breakout-short / Fib retest_hold / EMA-PSAR continuation 共用的 continuation confirmation gate**，不是把 ORB 原策略整套搬进来。冻结骨架是：先出现 breakout 与 retest，然后记录 `retest 前那段 impulse 的极值`；只有 retest 之后 `N` 根内（默认先看 `<= 6 bars`）**收盘价重破该 impulse extreme**，才允许放行。
- `trade off`：如果只是 retest 到位、但迟迟不能重破前高/前低，或者所谓改善只来自 session/样本挑选而不是这层确认本身，就不得升格；更不能把 `NY ORB` 时段假设原封不动偷渡成 24/7 crypto 主信号。

### 2) lookahead / repaint / leakage
- repo 代码把状态机拆成 `breakout -> wait >= 5 bars -> retest -> break within 6 bars`，并使用当下已形成的 `impulse_high_up / impulse_low_dn` 与当前 bar 的 `close/high/low` 判定；这一层本身可以 clean-room 化成因果规则。
- desk 迁移时必须统一冻结到 `signal 当根及之前数据 + next-bar open + no-overlap`；不得把 retest 之后未来是否 eventually 延续、未来更高/更低极值、或 session 结束后的路径反灌回当前 gate。

## 当前硬结论
**`Rank 102 = guard-passed / admit_to_clean_replication_queue`**。

## 证据摘要（source intake 级）
- repo 证据：`orb-backtester` 的状态机并不满足于“碰回 breakout level”；它明确要求 retest 之后再去破 `impulse_high_up / impulse_low_dn`，而且要落在有限确认窗内（`candlesToWait=5`、`breakCandles=6`）。
- 本地代理快检（来自 digest）也说明这层确认值得进下一轮：在 `BTC/ETH/SOL 15m 120d` 的代理样本里，能完成 `impulse re-break` 的 retest 事件只占约 `24.9%`，但通过确认组 `4-bar median signed return≈+43.8bps`，未通过组约 `-6.7bps`；`4-bar` 失效率约 `2.3% vs 38.8%`。
- 更诚实的 desk 读法：它当前更像 **shared continuation gate**，不是独立 alpha，也不是 live challenger。

## 对 Next 3 的直接影响
- `Run 1 = EMA due-check only（继续盯 Crypto 1d+1wk due_soon）`
- `Run 2 = 若 EMA 仍 waiting_not_due，则给 Rank 102 1 次最小 clean replication`
- `Run 3 = 若 Rank 102 clean replication 直接 hard-fail / exhausted，则切 Rank 103 / confirmed extremum honest fib anchor 的 source intake；只有 fresh source 这一层也 exhausted，才允许再比较 post-break sign-flip density > tiny-live plumbing`

## 边界与验证
- 仅做最小必要 intake + 守门，不重跑重型下载。
- 不触发 `P3 continuity`，也不提前把 `Rank 103` 并开。
- 工作区有大量本轮无关脏文件，未做 commit。
