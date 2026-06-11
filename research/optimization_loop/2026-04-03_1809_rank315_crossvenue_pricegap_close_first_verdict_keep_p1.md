# Rank 315 / cross-venue pricegap close alpha — fresh intake first verdict = keep_P1

- Time: 2026-04-03 18:09 UTC
- Target: `research/quant_digests/2026-04-03_1728_crossvenue-pricegap-close-alpha.md`
- Action: fresh intake first verdict
- Verdict: `keep_P1`
- Assigned Rank: `315`

## Why this changes runtime truth
这条对象不只是“历史上跨所套利存在过”的旧故事；当前 digest 已经把主语压缩得足够清楚：**同一 underlier 的 cross-venue spread close** 仍是独立 raw alpha，但在 2026 年 majors 上已明显被压成执行生意，真正还值得继续的主体更像 **alt / venue-specific dislocation × maker-first / inventory-aware shell**。

对 fresh intake first verdict 来说，这已经满足 `keep_P1` 的门槛：
1. **主语清楚**：不是一般性 market efficiency 叙事，而是 `long cheap venue / short rich venue` 的 same-underlier relative-value raw alpha。
2. **最小实验壳清楚**：文中已给出可复现的 `1m/3m/5m/15m` 触发/管理框架、明确的 z-score spread-close shell，以及本地 Binance/Bybit `1m` public-data portability probe。
3. **成本约束诚实**：digest 没有把 close-proxy gross pnl 误写成可交易净利，反而明确指出 `taker+taker` 基本可判死刑，当前是否可活主要取决于 maker/rebate/internal inventory。
4. **仍存在明确存活 pocket**：BTC/ETH 基本已被压扁，但 SOL/alt venue-dislocation 仍显示出继续检验的理由，因此不是直接 `background/P0`。

## What it is not yet
这轮还不够直接升 `P2`，因为当前证据主要停留在：
- public `1m` close-proxy 快检；
- majors vs alt 的粗粒度分层；
- 执行故事已被识别，但还没在更诚实的可交易口径下证明确有净后边际。

因此最诚实的 first verdict 不是 `promote_P2`，而是：

> `Rank 315`：cross-venue same-underlier spread-close 仍可作为独立 raw alpha 保留，但其当前可存活主体已经收缩到 `alt / venue pocket × maker-first / inventory-aware` 这类 execution-sensitive 子空间，因此本轮给 `keep_P1`，进入 survivor 的唯一一次 follow-up。

## Suggested one-shot survivor follow-up
唯一值得做的后续，不是再泛泛复读“跨所套利越来越难”，而是：
- 用统一成本口径，把 `BTC/ETH` 与 `SOL/alt`、以及 `maker+taker / maker+maker / taker+taker` 三类执行组合放到同一个最小 shell 里；
- 回答 `symbol × venue-pair admission layer` 下，是否真能筛出**仍有净后存活机会**的 pocket。

如果做不出明确可存活 pocket，应直接 `background/P0`；如果能在统一成本口径下筛出稳定可交易的 alt/venue bucket，再考虑升 `P2`。

## Result sentence
`Rank 315`：cross-venue same-underlier spread-close 在当前 desk 里仍是独立 raw alpha，但 majors 已明显被压成 execution 生意；由于 digest 已给出清楚主语、最小实验壳与至少一个仍可能存活的 alt / venue pocket，因此本轮分配正式 `Rank 315` 并首判 `keep_P1`。
