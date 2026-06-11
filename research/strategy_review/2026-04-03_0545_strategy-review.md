# Strategy Review — 2026-04-03 05:45 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并复核：
- repo 状态（`git status --short`；仅作状态参考，不反向改 policy）
- 最近 optimization 证据：
  - `research/optimization_loop/2026-04-03_0543_rank304_ema_obv_caution_first_verdict_keep_p1.md`
  - `research/optimization_loop/2026-04-03_0515_rank303_survivor_followup_background_p0.md`
  - `research/optimization_loop/2026-04-03_0450_rank303_realized_skewness_first_verdict_keep_p1.md`
  - `research/optimization_loop/2026-04-03_0403_rank302_survivor_followup_background_p0.md`
- 最近 strategy review：
  - `research/strategy_review/2026-04-03_0451_strategy-review.md`
  - `research/strategy_review/2026-04-03_0341_strategy-review.md`
  - `research/strategy_review/2026-04-03_0302_strategy-review.md`
- 最近新 repo/paper/alpha 报告：
  - `research/quant_digests/2026-04-03_0504_multivenue-coint-ml-filter-pairs-alpha.md`
  - `research/quant_digests/2026-04-03_0445_ema-obv-caution-atr-trend-alpha.md`
  - `research/quant_digests/2026-04-03_0355_same-underlier-multispread-optimizer-statarb.md`
  - `research/quant_digests/2026-04-03_0320_fundingstable-spotbasis-profitlock-alpha.md`

## Repo 状态摘要
- `Paper launch queue` 仍无等待接线对象；只有 `Rank 200 / 201 / 213 / 229` 处于 `connected_runner_live`。
- 当前工作区有大量未跟踪研究文件；按权限边界，本轮只改 `docs/BOT2_BOT3_STATE.md`，并新增本条 strategy review 日志。
- 最近 optimization 证据已表明：`Rank 303` 已按 survivor follow-up 诚实收口回 `background/P0`，`Rank 304` 已完成 fresh intake first verdict 并占据 survivor 槽位。

## 只回答 4 个问题

1) `Paper launch queue` 是否非空？
- 否。
- `Paper launch queue.current_target = none`。
- 当前没有等待 bot2 兜底推进到 wiring 的 P3 queue 头对象，因此本轮不触发 `P3 handoff` 小点。

2) 本轮 `fresh intake` 是什么？
- 当前前排 survivor 收口后，fresh intake 头应切到：
  - `research/quant_digests/2026-04-03_0504_multivenue-coint-ml-filter-pairs-alpha.md`
- 原因：`0445` 这条 `EMA trend shell × OBV caution veto × ATR trailing stop` 已经完成 first verdict 并成为 `Rank 304` survivor，不再属于 fresh intake；在不越过前排对象的前提下，剩余 fresh intake 应按最近且主语明确的新 repo/paper/alpha 顺序继续推进，而 `0504` 是当前最新的完整 raw-alpha desk 候选。

3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 值得。
- 上一条 fresh intake 是 `research/quant_digests/2026-04-03_0445_ema-obv-caution-atr-trend-alpha.md`，现已成为 `Rank 304`。
- `2026-04-03_0543_rank304_ema_obv_caution_first_verdict_keep_p1.md` 已明确给出 `keep_P1`：它相对普通单资产 EMA trend / breakout 家族的新增主语，不是“又一个均线趋势壳”，而是把 `OBV divergence + swing/ATR stretch` 组织成专门拦截追涨末端坏单的 `caution veto` 层，并允许 `ADX` 强趋势 override。
- 因此它依法值得那唯一一次 survivor follow-up；而且 follow-up 方向已经足够收敛：只需回答 `+ caution veto` 相对 baseline `EMA trend shell` 是否真能改善尾部亏损，而不是只减少 trade count。

4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 当前不存在明确 `Active P2`（`current_target = none`）。
- 最近一次 P2 出口仍是 `Rank 285` 的 `one-time P2->P1 re-scope`；此后没有新对象进入 `Active P2`。
- 因而当前不触发 bot2 作为 `P2 -> P3` 兜底裁判的强制升级动作。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Surviving candidate slot.current_target = Rank 304`
- `Active P2 slot.current_target = none`
- 当前前排对象均带正式 `Rank`，本轮无需补发新的整数编号。

## P2 -> P3 兜底裁判检查
- 当前没有 `Active P2`，因此不触发 bot2 直接把对象改写进 `P3 / Paper launch queue` 或 handoff 路径。
- 最近证据中也没有出现“desk review 已清楚表明足够进入 paper trade，但 bot3 尚未升级”的漏升案例。

## 本轮排班改写
按 policy 默认顺序，当前真实可执行动作应为：
1. `P1 / Surviving candidate`：先执行 `Rank 304` 的唯一一次 decisive follow-up。
2. `fresh intake`：只有在 `Rank 304` 已诚实收口后，才继续推进新的 intake。

据此，本轮 `cycle_plan` 已重写为：
1. `Rank 304 / EMA trend shell × OBV caution veto × ATR trailing stop`
2. `research/quant_digests/2026-04-03_0504_multivenue-coint-ml-filter-pairs-alpha.md`
3. `research/quant_digests/2026-04-03_0355_same-underlier-multispread-optimizer-statarb.md`
4. `research/quant_digests/2026-04-03_0320_fundingstable-spotbasis-profitlock-alpha.md`

重写理由：
- 当前前排唯一真实动作是 `Rank 304` 的 survivor 唯一 follow-up，不得让新的发现越过它。
- `Rank 304` 刚进入 survivor 槽位，依法拥有前排锁定权；在它收口前，不得让另一条新的 `keep_P1` 覆盖 survivor 槽位。
- 在 survivor follow-up 被诚实排到首位后，fresh intake 应切到当前最新且主语清楚的完整 raw-alpha 对象 `0504`，而不是继续保留已完成的旧项。
- 之后再按最近新材料顺序补 `0355` 与 `0320`，均为具体对象，而非抽象模板句子。

## 本轮写回内容
- 已更新：`docs/BOT2_BOT3_STATE.md`
- 已新增：`research/strategy_review/2026-04-03_0545_strategy-review.md`
- 未改动：policy / brief / operating card / auto loop / cron prompt

## 本轮改变系统认知的一句话
当前前排唯一必须先做完的动作是 `Rank 304` 对 baseline `EMA trend shell` 的 survivor 去重收口；只有它诚实出清后，`0504 multivenue cointegration + ML filter pairs shell` 才应成为本轮 fresh intake 头。