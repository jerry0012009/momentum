# Rank 187 / BTCUSDT 15m late-session path-shape swing — P2 exit decision（promote_P3）

- Time: 2026-03-26 20:10 UTC
- Target: `Rank 187 / BTCUSDT 15m late-session path-shape swing`
- Step type: `P2 exit decision`
- Verdict: `promote_P3`

## 本轮只回答的问题
对冻结后的 canonical pocket `h32_k3`（`BTCUSDT 15m`、前 `8h` partial-day path shape、`60d lookback`、`k=3`、仅当 implied remainder path 仍指向更高 future max 时开 long），只回答唯一剩余 blocker：

**`predicted-max timing exit` 是否足够诚实、足够可执行，从而让 Rank 187 达到“值得进入 paper trade / paper launch queue”的门槛？**

## 已有 authoratitive evidence（本轮不重开新 spec）
前两轮 admission 已经回答：
- `effectiveness + cross-asset`：保留 `keep_P2`
- `time stability`：保留 `keep_P2`
- survivor follow-up 已回答：同一组 entry 换成 `EOD / hold 4 / hold 8 / hold 12` 后仍保留成本后正值，不是只靠单一 exit 偶然成立

其中已经写死的最关键对照是：
- canonical `predicted-max exit`：`18` 笔，gross `+0.499%/trade`，扣 `6bps` 后约 `+0.439%/trade`
- `hold-to-EOD`：扣 `6bps` 后约 `+0.174%/trade`
- `hold 4 bars`：扣 `6bps` 后约 `+0.107%/trade`
- `hold 8 bars`：扣 `6bps` 后约 `+0.182%/trade`
- `hold 12 bars`：扣 `6bps` 后约 `+0.137%/trade`

canonical trade ledger 还显示：
- `18` 笔交易全部天然 `non-overlap`
- exit 持有时长分布约 `35 ~ 62` 根 `15m` bars，median `55` bars，mean `50.6` bars
- 也就是说，这不是“依赖当根后验挑尖点”的同 bar 幻觉，而是一条**入场时就能同时产出方向判断 + 预定退出时点**的 late-session swing 计划

## 为什么这轮的 honesty / execution realism 结论是通过，而不是继续卡在 P2
### 1) `predicted-max timing exit` 不是未来信息回填
这条策略的 exit 不是“事后看真实最高点再回填成交”，而是：
- 在 entry 时刻，基于当时已知的 partial-day path
- 从过去 `60d` 最近邻路径推断一条 average remainder path
- 再从**这条当下即可得出的预测 remainder path**里读出预定退出时点

因此它本质上更像：
- `signal at t`
- `schedule exit at t + predicted_holding_time`

而不是：
- `signal at t`
- `after close choose the best exit retrospectively`

对 paper trade / paper launch 来说，这已经是可执行 spec，而不是不可交易的 hindsight label。

### 2) 即使把 exit 压成更笨的可执行近似，edge 也没塌
如果这条线只能在“模型精确猜中峰值 bar”时才赚钱，那 honesty blocker 就应继续成立。

但 survivor 那一轮已经回答过：
- 改成 `EOD`
- 改成固定持有 `4/8/12` bars

之后，成本后仍是正值。说明：
- path-state 提供的首先是**方向层** alpha；
- `predicted-max timing` 只是更好的执行翻译，不是唯一利润来源。

这点很关键：它把 `predicted-max exit` 从“不可执行的花哨研究动作”降成了“paper 阶段可跟踪、而且有 simpler fallback 的默认 exit”。

### 3) P2 已连续两轮 `keep_P2`，按 policy 本轮必须收口
当前 `Rank 187` 已经出现 `2` 次连续 `keep_P2`。按 policy，本轮不得再给第三次开放式 `keep_P2`。

出口三选一里：
- `drop_to_background`：不成立，因为 canonical pocket 仍有厚度，且 2026-02 / 2026-03 连续为正；
- `one-time P2->P1 re-scope`：不成立，因为当前并不存在唯一明确、必须回退到 P1 才能表达的 re-spec；策略对象本身已经足够冻结；
- `promote_P3`：成立，因为剩余 blocker 已被回答到足够 paperable。

## 最小 paper-launch spec（本轮写回 runtime 的 launch 读法）
**Rank 187 / BTCUSDT 15m late-session path-shape swing**

- market: `BTCUSDT`
- bar: `15m`
- observe: 当天前 `8h`（`32` 根 `15m` bars）
- model: `60d lookback + k=3 nearest-neighbor partial-day path shape`
- entry: 仅当 implied remainder path 仍指向更高 future max 时开 `long`
- primary paper exit: `entry 时即锁定的 predicted-max timing`
- executable fallback exits already sanity-checked: `EOD` / `hold 4` / `hold 8` / `hold 12`
- current admission reading: **single-asset BTC late-session path-state swing, suitable for paper launch queue; not yet a cross-asset general family**

## 为什么现在就该升 P3
更诚实的 deployment-facing 说法已经不是“它完美无缺”，而是：

> 这条线已经足够像一条可写进 paper queue 的单一策略对象：entry 可定义、exit 可预定、ledger non-overlap、成本后仍有厚度，而且 simpler executable exits 也保留正向 pocket。

也就是说，它已经达到：
- **值得进入 paper trade / paper launch**
- **比较可能成型**
- **没有明显致命 honesty flaw**

这正是 policy 要求 bot3 在本轮直接升级到 `P3` 的门槛。

## 本轮结论（一句话）
**Rank 187 / BTCUSDT 15m late-session path-shape swing 的 `predicted-max timing` 本质上是 entry 时即可锁定的退出计划，不是事后回填的 hindsight peak；再加上 `EOD / 4 / 8 / 12-bar` 可执行替代退出在成本后仍为正，因此当前唯一剩余 blocker `honesty / execution realism` 已通过，Rank 187 应直接从 `Active P2` 升级到 `P3 / Paper launch queue`。**
