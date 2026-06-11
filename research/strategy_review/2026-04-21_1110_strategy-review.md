# 2026-04-21 11:10 UTC strategy review

## Inputs checked
- Policy: `docs/BOT2_BOT3_POLICY.md`
- State: `docs/BOT2_BOT3_STATE.md`
- Repo status: `git -C /root/clawd/jerry/momentum status --short`（当前可见主要仍是工作区根目录历史未跟踪临时文件；`jerry/momentum` 本轮未见会改变前排结论的新代码改动）
- Recent optimization evidence:
  - `research/optimization_loop/2026-04-21_1106_cycle_item2_blocked_already_resolved.md`
  - `research/optimization_loop/2026-04-21_1034_rank431_survivor_followup_promote_p2.md`
  - `research/optimization_loop/2026-04-21_0858_rank431_cointegration_maker_timestop_pairs_keep_p1.md`
  - `research/optimization_loop/2026-04-21_0754_mefai_scalping_microtrend_volspike_freshintake_background_p0.md`
- Recent strategy review evidence:
  - `research/strategy_review/2026-04-21_0903_strategy-review.md`
  - `research/strategy_review/2026-04-21_0716_strategy-review.md`
- Recent intake sources checked:
  - `research/quant_digests/2026-04-21_1104_crossvenue-funding-spread-diptolerance-shell.md`
  - `research/quant_digests/2026-04-21_0946_hl-marketquality-shared-gate-overlay.md`
  - `research/quant_digests/2026-04-21_0842_btcimpulse-alt-reentry-fullstack-shell.md`
  - `research/park_reframe/2026-04-06_0606_rank27-park-reframe.md`

## 仅回答 4 个问题
1. `Paper launch queue` 是否非空？
- 是，非空。
- `connected_runner_live` 已有多条已接线对象；`current_target = none`，所以当前没有待补 runner / scheduler / first verified run 的 active `P3 launch wiring` 项。

2. 本轮 `fresh intake` 是什么？
- 当前前排第一动作不是 fresh intake，而是 `Rank 431 / cointegration maker-first + hard time-stop pairs` 的 `Active P2 admission`。
- 在它之后，本轮 fresh intake 重新改写为：
  - `research/quant_digests/2026-04-21_1104_crossvenue-funding-spread-diptolerance-shell.md`
  - `research/quant_digests/2026-04-21_0842_btcimpulse-alt-reentry-fullstack-shell.md`
  - `research/park_reframe/2026-04-06_0606_rank27-park-reframe.md`（conditional fresh intake）
- `Bybit positive funding decay` 与 `MEFAI microtrend` 都已在更早轮次收口 `background/P0`，不得继续占当前 fresh intake。

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 不适用为“待执行问题”，因为上一条 fresh intake `Rank 431` 的那唯一一次 survivor follow-up 已经完成，并已给出层级变化。
- 其 follow-up 结果明确是值得且已被诚实消费：`research/optimization_loop/2026-04-21_1034_rank431_survivor_followup_promote_p2.md` 已证明在 rolling pair admission + 最小 maker fill realism 下，`AVAX-SUI` 与 `NEAR-ATOM` 仍保留同向 after-cost pocket，因此对象已经从 survivor 升到 `Active P2`，不再停留在 follow-up 待决状态。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 有：`Rank 431 / cointegration maker-first + hard time-stop pairs`。
- 以目前 desk review 可见证据，它离 `P3` 最近，但还没到 bot2 必须直接越级推进 `P3` 的门槛。
- 原因：当前已经证明“不是单 pair lucky run”，但 admission 还没正面回答 recent 月份、参数稳定性、pair turnover / 失配现实后，是否仍没有单一 decisive honesty / execution blocker；因此本轮应先把它排成 `P2 admission / 出口决策首轮`，而不是继续开放式拖研，也不是过早回退 `P1/P0`。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Active P2 slot.current_target = Rank 431 / cointegration maker-first + hard time-stop pairs`
- `Fresh intake` / `Surviving candidate` / `Active P2` / `Paper launch queue` 当前前排对象均带正式 rank（或 fresh intake 仍未到需发 rank 的阶段）。
- 本轮无需补新的整数 `Rank`。

## P2 -> P3 兜底判断
- 本轮 desk review 没看到一个已经清楚达到“足够值得进入 paper trade / paper launch、且没有明显致命 honesty / execution 问题”的 `Active P2` 却仍被 bot3 漏升的对象。
- `Rank 431` 当前更像“离 `P3` 最近，但还差一次 admission 出口判断”；所以 bot2 这轮不直接把它改写进 `P3 / Paper launch queue`。
- 相反，bot2 已把它明确排成 **P2 admission / 出口决策首轮**，避免它被新的 intake 挤掉，也避免继续写成模糊开放式研究。

## State rewrite
已按 policy 默认顺序重写 `docs/BOT2_BOT3_STATE.md`：
1. `Rank 431 / cointegration maker-first + hard time-stop pairs`
   - 改成 `P2 admission / 出口决策首轮`
   - 明确 success criterion：直接回答离 `P3 / P1 / P0` 哪个出口最近；若 recent 切片、成本梯度、参数稳定性与最小 honesty / execution realism 都闭合，则允许 `promote_P3`
2. `research/quant_digests/2026-04-21_1104_crossvenue-funding-spread-diptolerance-shell.md`
   - 作为当前 fresh intake #1
3. `research/quant_digests/2026-04-21_0842_btcimpulse-alt-reentry-fullstack-shell.md`
   - 作为当前 fresh intake #2
4. `research/park_reframe/2026-04-06_0606_rank27-park-reframe.md`
   - 保留为 conditional fresh intake

同时把 `Fresh intake slot.current_target` 更新为当前轮真正的首条新 intake：
- `research/quant_digests/2026-04-21_1104_crossvenue-funding-spread-diptolerance-shell.md`

## 本轮结论
- queue 非空，但无 active P3 wiring。
- 前排主语已经切到 `Rank 431` 的 `Active P2`，且它离 `P3` 最近。
- stale 的 Bybit / MEFAI pending 项已被移出当前轮默认执行顺序。
- 本轮没有需要 bot2 直接越权强推 `P3` 的对象；但也没有允许 `Rank 431` 再被拖回模糊研究的空间。

## Tail step status
- homepage publish：`bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` 已作为独立命令尝试；本轮无输出后被 `SIGKILL`，按 policy 记为非阻断尾部失败，不回滚本轮 state/log。
- email notify：`python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot2-review] Rank431 转入P2 admission，前排已重排" --body-file /root/clawd/jerry/momentum/research/strategy_review/2026-04-21_1110_strategy-review.md` 已作为独立命令执行并成功发送到 `18810813576@163.com`。
