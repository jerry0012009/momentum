# Rank 293 / near-expiry IV spike × 1m liquidity sweep → short vertical credit spread — survivor follow-up closes to background/P0

- Time: 2026-04-02 13:34 UTC
- Executor: bot3 auto loop
- Source digest: `research/quant_digests/2026-04-02_0936_ivspike-sweep-creditspread-options-alpha.md`
- Prior state: `Surviving candidate slot`
- Verdict: `keep_P1 after follow-up -> background/P0`
- Level change: survivor slot -> background pool

## What this follow-up had to answer
唯一允许的 survivor follow-up 问题很明确：

> 在连续 near-expiry chain 样本下，扣除双腿 half-spread + taker fee + 现实成交惩罚后，`IV spike + 1m sweep -> same-expiry short vertical credit spread` 是否仍有正净期望？

## What I checked
使用 Delta Exchange 公共 API 做最小 execution-realism 快检：

1. `GET /v2/products`：确认 `BTC` 次日到期（`2026-04-03 12:00:00Z`）的 near-expiry option chain 仍足够完整；
2. `GET /v2/tickers`：抽取 near-ATM strikes 的当前 bid/ask / IV / OI；
3. `GET /v2/history/candles`：检查代表性 option symbols 的 `1m` 成交稠密度，判断是否存在可支撑连续事件验证的真实交易流。

## Evidence that changes the verdict
### 1) 近 ATM 200 点宽度 credit spread 的入场 credit，几乎全被双腿 half-spread 吃掉
在 `spot ≈ 66103`、`2026-04-03` 到期链上，代表性 200 点 vertical 的当前可成交 entry credit 与 half-spread penalty 如下：

#### Call credit spreads
- `66000 / 66200`：entry credit `49.0`，mid credit `100.5`，half-spread penalty `51.5`
- `66200 / 66400`：entry credit `48.0`，mid credit `99.0`，half-spread penalty `51.0`
- `66400 / 66600`：entry credit `35.0`，mid credit `85.5`，half-spread penalty `50.5`
- `66600 / 66800`：entry credit `26.0`，mid credit `75.5`，half-spread penalty `49.5`

#### Put credit spreads
- `66400 / 66200`：entry credit `51.0`，mid credit `103.5`，half-spread penalty `52.5`
- `66200 / 66000`：entry credit `46.0`，mid credit `98.0`，half-spread penalty `52.0`
- `66000 / 65800`：entry credit `44.0`，mid credit `95.5`，half-spread penalty `51.5`
- `65800 / 65600`：entry credit `30.0`，mid credit `81.0`，half-spread penalty `51.0`

这意味着：
- 只按“卖短腿 bid、买保护腿 ask”入场时，**当前可拿到的净 credit 只有 `26~51` 点**；
- 但仅双腿 half-spread 这一个 friction 档，已经在 **`49~53` 点** 量级；
- 这还**没加 taker fee、撤单重挂、双腿不同步、退出时再付一次 spread**。

换成人话：repo 里看起来像“收 `40% credit` 就走”的盈利壳，在真实可成交 quote 下，**入场第一步就已经把大半甚至全部边际优势交给盘口了**。

### 2) 代表性 near-expiry option symbols 的 1m 成交极稀疏，不像能稳定承载这条事件驱动 alpha
`history/candles` 快检显示：
- `P-BTC-66000-030426`：最近约 24h 有 `710` 根 `1m` bars，但只有 `2` 根非零成交、其余 `708` 根为零成交；
- `C-BTC-66000-030426`：最近约 24h 只有 `1` 根非零成交 bar；
- `P-BTC-66500-030426`：最近约 24h 只有 `1` 根非零成交 bar；
- `C-BTC-66500-030426`：最近约 24h `0` 根 bar。

这直接打到 survivor follow-up 想回答的问题：
- 当前 public path 下，不仅没有看到“连续 near-expiry 触发后可稳定成交”的证据；
- 相反，代表性链上更像是**大部分时间没有成交流、只能盯 quote 幻觉做故事**。

### 3) 所以当前 decisive blocker 不是“还差一点回测”，而是 execution realism 本身
这轮 follow-up 本来就不该继续讲 `0DTE theta` 或 `IV mean reversion` 机制故事；真正要看的，是 **这条结构在现实双腿成交下还剩不剩净 edge**。

当前答案偏负面：
- 可成交 entry credit 已接近或低于双腿 spread 惩罚；
- 成交流又明显稀疏；
- 因此在不额外假设 maker 优先成交、quote 改善、私有成交优化器的前提下，**现有 public-data / public-quote 证据不足以支持它作为可持续 short-cycle raw alpha 存活**。

## System-changing conclusion
`Rank 293` 的 survivor follow-up 已经收口：当前真正的 decisive blocker 就是 **双腿 execution realism**，而不是再补一轮泛泛的 options 机制描述。基于现有公开链路下 near-expiry chain 的宽 spread 与极稀疏成交，`IV spike + 1m sweep -> short vertical credit spread` 暂时不能诚实地证明成本后仍有正净期望，因此 **不升 `P2`，并在 survivor 预算用尽后回 `background/P0`**。

## Why this is not a block / not a P2
- 不是 `blocked`：已经拿到了会改变层级判断的 decisive evidence；
- 不是 `P2`：当前没有理由继续把它留在前排 admission，只会继续重复“期权理论上可能有 edge”的低杠杆叙述；
- 也不是 `P2->P1 re-scope`：并没有出现一个唯一明确的新 scope（例如稳定 maker venue、固定做市权限、不同产品壳）足以支持一次合法 re-scope，所以不走回退重写路线。
