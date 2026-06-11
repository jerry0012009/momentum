# 2026-04-21 11:52 UTC strategy review

## Inputs checked
- Policy: `docs/BOT2_BOT3_POLICY.md`
- State: `docs/BOT2_BOT3_STATE.md`
- Repo status: `git -C /root/clawd/jerry/momentum status --short`（当前可见仍主要是工作区根目录历史未跟踪临时文件；`jerry/momentum` 本轮未见会推翻前排判断的新代码提交）
- Recent optimization evidence:
  - `research/optimization_loop/2026-04-21_1148_rank431_p2_admission_round1_keep_p2_single_durable_pair_blocker.md`
  - `research/optimization_loop/2026-04-21_1034_rank431_survivor_followup_promote_p2.md`
  - `research/optimization_loop/2026-04-21_0858_rank431_cointegration_maker_timestop_pairs_keep_p1.md`
- Recent strategy review evidence:
  - `research/strategy_review/2026-04-21_1110_strategy-review.md`
  - `research/strategy_review/2026-04-21_0903_strategy-review.md`
- Current intake sources checked:
  - `research/quant_digests/2026-04-21_1104_crossvenue-funding-spread-diptolerance-shell.md`
  - `research/quant_digests/2026-04-21_0842_btcimpulse-alt-reentry-fullstack-shell.md`
  - `research/park_reframe/2026-04-06_0606_rank27-park-reframe.md`

## 仅回答 4 个问题
1. `Paper launch queue` 是否非空？
- 是，非空。
- `connected_runner_live` 已有多条已接线对象；`current_target = none`，说明当前没有待补 runner / scheduler / first verified run 的 active `P3 launch wiring` 项。

2. 本轮 `fresh intake` 是什么？
- 本轮前排仍先处理 `Rank 431 / cointegration maker-first + hard time-stop pairs` 的 `Active P2` 出口决策。
- 当前真正的 fresh intake 顺位是：
  - `research/quant_digests/2026-04-21_1104_crossvenue-funding-spread-diptolerance-shell.md`
  - `research/quant_digests/2026-04-21_0842_btcimpulse-alt-reentry-fullstack-shell.md`
  - `research/park_reframe/2026-04-06_0606_rank27-park-reframe.md`（conditional fresh intake）

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 上一条 fresh intake 是 `Rank 431`。
- 这个问题已经被诚实消费完：值得，而且那唯一一次 follow-up 已经执行并完成层级变化。
- 证据见 `research/optimization_loop/2026-04-21_1034_rank431_survivor_followup_promote_p2.md`：rolling admission + 最小 maker fill realism 后，至少 `AVAX-SUI` 与 `NEAR-ATOM` 两对保留同向 after-cost pocket，因此它已从 survivor 升到 `Active P2`，不再停留在 follow-up 待决状态。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 有：`Rank 431 / cointegration maker-first + hard time-stop pairs`。
- 以当前 desk review 可见证据，它仍然离 `P3` 最近，但 bot2 这轮还不能直接兜底把它推进 `P3 / Paper launch queue`。
- 原因：`research/optimization_loop/2026-04-21_1148_rank431_p2_admission_round1_keep_p2_single_durable_pair_blocker.md` 已经把 blocker 收敛成单一问题——`cross-pair durability`。当前稳定费后边际主要由 `NEAR-ATOM` 承担，`AVAX-SUI` 去掉少数高贡献日后转弱；这说明它不是开放式研究问题了，而是一个明确的出口决策问题。
- 因此它最近的出口仍是 `P3`，但本轮必须先完成一次 **P2 出口决策次轮**：若 recent 月份与 pair-level 稳定性还能证明至少两对 durable pocket，就 `promote_P3`；否则默认 `background/P0`，仅在存在唯一明确新 spec 时才允许一次性 `P2->P1 re-scope`。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Active P2 slot.current_target = Rank 431 / cointegration maker-first + hard time-stop pairs`
- `Fresh intake` / `Surviving candidate` / `Active P2` / `Paper launch queue` 当前前排对象均有正式 rank（或 fresh intake 仍未到需分配 rank 的阶段）。
- 本轮无需补新的整数 `Rank`。

## P2 -> P3 兜底判断
- 本轮 desk review 没看到一个已经清楚达到“足够值得进入 paper trade / paper launch、且没有明显致命 honesty / execution 问题”的 `Active P2` 却仍被 bot3 漏升的对象。
- `Rank 431` 的 admission 现在已经不是开放式探索，而是单 blocker 收口；但在当前证据下，还不能说它已明确跨过 `P3` 门槛。
- 所以这轮 bot2 不直接越级把它写进 `P3 / Paper launch queue`；相反，必须把它排成 **P2 出口决策次轮**，避免第三次模糊 `keep_P2`。

## State rewrite
已按 policy 默认顺序重写 `docs/BOT2_BOT3_STATE.md` 的当前轮 `cycle_plan`：
1. `Rank 431 / cointegration maker-first + hard time-stop pairs`
   - 改成 `P2 admission / 出口决策次轮`
   - 明确 success criterion：这轮必须直接输出 `promote_P3`、`background/P0` 或一次性明确 `P2->P1 re-scope`，不得再写成开放式 `keep_P2`
2. `research/quant_digests/2026-04-21_1104_crossvenue-funding-spread-diptolerance-shell.md`
   - 作为当前 fresh intake #1
3. `research/quant_digests/2026-04-21_0842_btcimpulse-alt-reentry-fullstack-shell.md`
   - 作为当前 fresh intake #2
4. `research/park_reframe/2026-04-06_0606_rank27-park-reframe.md`
   - 保留为 conditional fresh intake

## 本轮结论
- queue 非空，但无 active P3 wiring。
- 当前前排主语仍是 `Rank 431` 的 `Active P2`，而且它离 `P3` 最近。
- 但在单一 `cross-pair durability` blocker 尚未关闭前，bot2 这轮还不能直接替 bot3 兜底推 `P3`。
- 相反，本轮已经把它明确排成 **出口决策轮**，防止它继续停在模糊 admission 里。

## Tail step status
- homepage publish：待本轮尾部独立命令执行。
- email notify：待本轮尾部独立命令执行。
