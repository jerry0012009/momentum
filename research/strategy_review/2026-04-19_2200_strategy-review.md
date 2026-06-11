# 2026-04-19 22:00 UTC strategy review

## Inputs checked
- Policy: `docs/BOT2_BOT3_POLICY.md`
- State: `docs/BOT2_BOT3_STATE.md`
- Repo status: `git -C /root/clawd/jerry/momentum status --short && git -C /root/clawd/jerry/momentum log --oneline -5`
- Recent optimization evidence:
  - `research/optimization_loop/2026-04-19_2151_cycleplan_item1_blocked_stale_replay.md`
  - `research/optimization_loop/2026-04-19_2032_rank426_survivor_followup_background_p0_30m_1h_honesty.md`
  - `research/optimization_loop/2026-04-19_1951_supertrend_shortflip_freshintake_background_p0_timesymbol_concentration.md`
  - `research/optimization_loop/2026-04-19_1913_rank426_volume_switch_freshintake_keep_p1.md`
- Recent strategy review evidence:
  - `research/strategy_review/2026-04-19_2114_strategy-review.md`
  - `research/strategy_review/2026-04-19_1956_strategy-review.md`
- Fresh-intake source notes checked this round:
  - `research/quant_digests/2026-04-19_2019_highvol-selloff-bounce-5m-alpha.md`
  - `research/quant_digests/2026-04-19_1906_hl-xs-overextension-fade-alpha.md`
  - `research/quant_digests/2026-04-19_1815_fibmacd-shallowpullback-continuation-alpha.md`

## Repo status snapshot
- repo 工作区仍有大量历史未跟踪临时文件；按 policy 只把它们视为噪声，不把“文件多”误判成当前前排对象。
- 最近真正改变 runtime front slots 的证据仍是：
  1. `research/optimization_loop/2026-04-19_2032_rank426_survivor_followup_background_p0_30m_1h_honesty.md`：`Rank 426` survivor 唯一 follow-up 已诚实收口到 `background/P0`；
  2. `research/optimization_loop/2026-04-19_1951_supertrend_shortflip_freshintake_background_p0_timesymbol_concentration.md`：上一条 fresh intake 已直接收口到 `background/P0`；
  3. `research/optimization_loop/2026-04-19_2151_cycleplan_item1_blocked_stale_replay.md`：确认 state 里仍挂着一个已解决对象的 stale pending。
- `Paper launch queue` 非空，但只有 `connected_runner_live` 存量；当前没有待接线 `P3`。
- `Active P2 = none`，不存在需要 bot2 兜底直推 `P3` 的对象。

## 仅回答 4 个问题
1. `Paper launch queue` 是否非空？
- 是，非空。
- 但 `current_target = none`，说明当前没有未完成 wiring 的 `P3` 动作。

2. 本轮 `fresh intake` 是什么？
- 在清理掉 stale replay 后，本轮真实 `fresh intake` 应前移为：
- `research/quant_digests/2026-04-19_2019_highvol-selloff-bounce-5m-alpha.md`

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 不值得。
- 上一条 fresh intake 是 `research/quant_digests/2026-04-19_1932_hyperliquid-funding-signflip-shell.md`。
- `research/optimization_loop/2026-04-19_1951_supertrend_shortflip_freshintake_background_p0_timesymbol_concentration.md` 已给出 first verdict：表面 top1 short 仅薄正，`short-only top1` 复核后转负，且收益集中在 `2026-02` 与少数 alt；`2026-03/04` 已转负，因此不值得 survivor follow-up，已诚实收口 `background/P0`。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 当前不存在明确 `Active P2`。
- 因此本轮不存在需要 bot2 直接兜底改写到 `P3 / Paper launch queue` 的对象。

## Rank 完整性检查
- 当前前排对象没有无 rank 污染：
  - `Surviving candidate = none`
  - `Active P2 = none`
  - `Paper launch queue.connected_runner_live` 中对象均已有正式 `Rank`
- 因此本轮无需补新的 `Rank`。

## State rewrite
已按 policy 重写 `docs/BOT2_BOT3_STATE.md`：
- 清除 `cycle_plan` 里已解决却仍显示 pending 的 stale fresh intake；
- 把 `Fresh intake slot.current_target` 前移到 `2026-04-19_2019_highvol-selloff-bounce-5m-alpha.md`；
- 保持 `Surviving candidate = none`、`Active P2 = none`、`Paper launch queue.current_target = none` 不变；
- 将当前轮 `cycle_plan` 改为仅包含 3 条真实可执行 fresh intake：
  1. `2026-04-19_2019_highvol-selloff-bounce-5m-alpha.md`
  2. `2026-04-19_1906_hl-xs-overextension-fade-alpha.md`
  3. `2026-04-19_1815_fibmacd-shallowpullback-continuation-alpha.md`

## Why this cycle_plan is policy-consistent
- 当前没有待接线 `P3`、没有 `Active P2`、没有 survivor 锁定权对象，所以排班应诚实切到 fresh intake。
- 不再把已收口对象留在第 1 项制造伪 pending。
- 新 `cycle_plan` 只包含具体对象，不含背景池 guard、空模板、抽象泛任务。
- 没有把 background pool 旧候选拉回前排；3 个对象都来自最近尚未消费的新 digest。
- 当前 desk review 没看到任何“已足够 paper trade 但 bot3 尚未升级”的 `Active P2`，因此没有 bot2 必须直接改写 `P3` 的兜底场景。

## Review verdict
- `Paper launch queue` 非空，但当前没有待接线 `P3`。
- 本轮真实 `fresh intake` 已前移到 `2026-04-19_2019_highvol-selloff-bounce-5m-alpha.md`。
- 上一条 fresh intake `2026-04-19_1932_hyperliquid-funding-signflip-shell.md` 不值得 survivor follow-up，已收口 `background/P0`。
- 当前没有 `Active P2`；本轮 `cycle_plan` 应只保留真实可执行的 3 条 fresh intake。
