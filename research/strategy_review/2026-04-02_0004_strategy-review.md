# Strategy Review — 2026-04-02 00:04 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

## 本轮只回答 4 个问题

1. `Paper launch queue` 是否非空？
- 否。`current_target = none`。
- 现有 `connected_runner_live` 为 `Rank 200 / 201 / 213 / 229`，其中最新记录明确写明 `Rank 229` 已完成 wiring，queue 头已清空。

2. 本轮 `fresh intake` 是什么？
- `research/quant_digests/2026-04-01_2322_24h-xs-reversal-dispersion-turnover-shell.md`
- 它已在 runtime state 中首判为 `Rank 285`，结论是：
  - 已具备可独立审计的 cross-sectional mean-reversion raw alpha skeleton；
  - 也有明确的 `top-liquid perp + lower-turnover execution shell` transfer path；
  - 但目前硬证据仍停留在日频 Binance spot OOS repo 与待测 perp transfer path，故当前只到 `keep_P1`，不直升 `P2`。

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 不值得再给新的 follow-up 预算。
- 上一条 fresh intake 是 `Rank 284 / ADF+Johansen dual-test rolling-beta spread z-score fade pairs`。
- 最近优化记录与当前 state 都已写明：它唯一一次 survivor follow-up 已完成并耗尽，结论是 repo 仍有 `silent ADF-only fallback` 与 spread/residual 口径不够干净的问题，且没有 liquid perp intraday clean-room after-cost 存活证据，因此已经 `drop_to_background / P0`。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 当前不存在明确 `Active P2`，`current_target = none`。
- 最近被清出的 `Rank 276` 已在 `time stability` 轴上直接收口为 `drop_to_background / P0`，因此当前没有需要 bot2 兜底直推 `P3` 的活跃 P2 对象。

## Rank 完整性检查
- 当前前排对象检查结果：
  - `Surviving candidate = Rank 285`
  - `Paper launch queue current_target = none`
  - `Active P2 = none`
- 不存在“前排对象无正式 rank”的冲突，因此本轮无需补新 rank。

## 本轮排班重写原则
- 依 policy 默认顺序扫描：`P3 handoff > P2 admission/promote/park > P1 唯一一次诚实检查 > fresh intake > P0`
- 当前无 `P3` queue 头、无 `Active P2`，因此唯一真实前排动作是：`Rank 285` 的 survivor follow-up。
- 由于已有 survivor 前排锁定，新的 fresh intake 不得排在它前面。

## 写回结果
- 已重写 `docs/BOT2_BOT3_STATE.md` 的 `cycle_plan`：
  1. `Rank 285` survivor follow-up（唯一一次诚实检查，直接回答能否升 `P2`）
  2. `adjacent-maturity calendar spread` fresh intake
  3. `BTC reference copula pairs mispricing` fresh intake
  4. `microprice + OBI veto pairs` fresh intake

## 结论
- 当前 runtime truth 很简单：
  - `Paper launch queue` 为空；
  - 当前 fresh intake 是 `Rank 285`；
  - 上一条 fresh intake `Rank 284` 不再值得 follow-up；
  - 当前没有 `Active P2`；
  - 因此前排资源必须先给 `Rank 285` 的唯一 survivor follow-up，而不是继续把新的 intake 排到前面。
