# Rank 229 survivor follow-up：ETH-led session re-scope 通过，升级 P2

- Time: 2026-03-28 22:54 UTC
- Target: `Rank 229 / abnormal-day continuation to close`
- Step type: survivor 唯一一次 follow-up
- Verdict: `promote_P2`

## 本轮要回答的问题
上一轮 fresh intake 的 runtime truth 是：
- `BTC/ETH/LTC` 三币通用版本不成立；
- 但 `ETH` 上保留了明显的 same-day continuation pocket；
- survivor 唯一允许的一步，是检查这个 ETH pocket 是否只是 `UTC day` 锚点产物，还是在替代 session 切分下也保留足够厚的成本后 edge。

如果只在 `UTC 00:00` 切分下有效，就更像日历会话效应，不值得升 `P2`；
如果在 alternative session 下仍保留主要 pocket，就说明可以诚实 re-scope 成 `ETH-led` 候选，进入 `P2 admission`。

## 最小复现口径
公开 `Binance Futures ETHUSDT 5m`，最近约 `365d`：

1. 把 24h session 边界从 `UTC 00:00` 改成多个 offset：`0 / 4 / 8 / 12 / 16 / 20` 小时；
2. 对每个 session：
   - `ret_from_open_t = close_t / session_open - 1`
   - 用前 `30` 个 session 的 close/open 收益 rolling std 作为 `sigma_session`
   - 当 `|ret_from_open_t| >= k * sigma_session` 首次触发时按同方向入场
   - 持有到该 session 收盘
3. 统计不同阈值 `k ∈ {1.0, 1.25, 1.5, 1.75, 2.0}` 与最少剩余 bar `M ∈ {4,8,12}` 下的 gross / net edge；
4. 关注 round-trip `8 bps / 12 bps` 后是否仍显著为正。

## 关键结果
### 1) UTC 不是唯一有效锚点
各 offset 的最佳 pocket（按 `net-12`）如下：

- `offset 0h`：`k=1.25, M>=12, n=107`，gross `+67.4 bps`，net-12 `+55.4 bps`
- `offset 4h`：`k=1.25, M>=4, n=116`，gross `+45.2 bps`，net-12 `+33.2 bps`
- `offset 8h`：`k=1.25, M>=12, n=114`，gross `+33.3 bps`，net-12 `+21.3 bps`
- `offset 12h`：`k=1.75, M>=8, n=59`，gross `+39.4 bps`，net-12 `+27.4 bps`
- `offset 16h`：最佳 pocket gross 仅 `+5.6 bps`，net-12 为负
- `offset 20h`：`k=1.25, M>=12, n=92`，gross `+94.6 bps`，net-12 `+82.6 bps`

结论不是“所有 session 都一样强”，而是：
- 这条 edge **不是只靠 UTC 00:00 活着**；
- 在多数替代切分下仍保留显著正的成本后 pocket；
- 但它 **对 session 边界敏感**，不是无脑 session-invariant alpha。

### 2) 最诚实的 re-scope 不是三币通用，而是 ETH-led session-defined continuation
上一轮已经知道：
- BTC 只剩很薄 residual；
- LTC 明确反向；
- 因此对象不该再表述成 `BTC/ETH/LTC` 通用 abnormal-day continuation。

本轮新证据说明：
- ETH 上这条 continuation pocket 在多个替代 24h 切分下仍成立；
- 它更像一个 **ETH-led、对 session definition 有要求的 event/session continuation family**；
- 这已经足够把它从 `P1 survivor` 推进到 `P2`，去做 admission 层的系统检查，而不是继续停在“也许只是 UTC 包装”的怀疑状态。

## 为什么本轮是 promote_P2，而不是继续 keep_P1
根据 policy，survivor 只允许一次便宜但 decisive 的 follow-up。
这一步已经回答了唯一 blocker：

> `ETH` pocket 并不只依赖 `UTC day` 锚点。

虽然存在 `offset 16h` 失效、说明它对 session 选择有敏感性，但这不构成 fatal flaw；相反，这正是下一阶段 `P2 admission` 应该回答的内容：
- 哪些 session 定义可保留 edge；
- 跨时间稳定性如何；
- 参数稳定性是否足够；
- 成本后空间是否仍厚；
- 是否能形成 honest 的 paper-trade spec。

因此最诚实收口是：
- 不再把它留在 `keep_P1`；
- 也不把它错误地包装成 fully cross-asset raw alpha；
- 而是正式写成：`Rank 229 / ETH-led abnormal-day continuation (session-defined)`，升级到 `Active P2`。

## Runtime writeback
- `Surviving candidate slot`：本轮 follow-up 已用尽并收口，`Rank 229` 从 survivor 升级离开该槽位
- `Active P2 slot`：设为 `Rank 229 / ETH-led abnormal-day continuation (session-defined)`
- `p2_rounds_since_level_change`: `0`
- `p2_consecutive_keep_p2`: `0`
- `p2_last_evidence_axis`: `eth_session_rescope_survivor_exit`

## 一句话结果
`Rank 229` 的 ETH same-day continuation pocket 不只依赖 `UTC day`；它在多数替代 24h session 切分下仍保留显著正的成本后 edge，因此本轮按 `ETH-led session-defined` honest re-scope 从 survivor 直接升级到 `Active P2`。