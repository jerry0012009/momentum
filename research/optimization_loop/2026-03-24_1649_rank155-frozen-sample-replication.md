# Rank 155 / Jamestilfords/statarb-crypto frozen-sample clean-room follow-up

- Time: 2026-03-24 16:49 UTC
- Slot: Surviving candidate follow-up
- Rank: 155
- Target: `Jamestilfords/statarb-crypto`
- Goal: 只花这唯一一次 follow-up，回答它的 4H reversal 结果在 `fixed universe / fixed date / fixed cost / 1-bar lag` 下是否能做出诚实的 clean-room replication。

## What I checked
1. 读取 repo README 与 `src/crypto_statarb.py`，确认作者公开的策略骨架确实是：
   - 4H bars
   - `start = 2023-01-01`
   - cross-sectional top/bottom `q=20%`
   - `rebalance_every = 6`（4H 上按日调仓）
   - `1-bar lag`
   - turnover-based transaction costs
   - optional top-50% volume liquidity filter
2. 读取 notebook 原始文件，确认作者公开运行时并没有把**冻结后的 universe 名单 / 本地 OHLCV cache / 精确样本切片**随 repo 一起固定下来；notebook 里只是当场按 24h quote volume 取 `top 80`，再做 `>=90% coverage` 过滤。
3. 用同一公开骨架回看 notebook 输出：作者那次运行打印的是 `kept assets: 46`、`close_px shape: (6570, 46)`、`rets shape: (6569, 46)`。
4. 再按作者公开规则重建当前 public sample（Binance spot USDT、`top 80`、`2023-01-01` 起、`>=90% coverage`、去 stable），发现**当前可得到的冻结 universe 只剩 37 个资产**，还没进入 alpha 回测之前，样本本身就已与作者公开主结果的 46 资产版本发生了实质漂移。

## Why this is decisive
这个 follow-up 的目的不是再问一句“README 看起来像不像真的”，而是回答：**这套 4H reversal 证据能不能在冻结样本下独立复现。**

当前答案是否定的，原因不是我没找到更多图，而是 repo 没有交付 clean-room replication 所需的关键冻结件：
- 没有作者当次运行的 `frozen universe tickers`
- 没有当次运行的 `cached OHLCV`
- 没有可直接复跑并锁定同一 sample 的 artifact
- 作者自己还在 README 里明确提醒：一旦重下 OHLCV 或重做 universe filter，最佳参数和表现会漂移

也就是说，这个项目最关键的 admission blocker 不是“可能还差一次参数补测”，而是**主结论对样本重建高度敏感，且 repo 没把样本冻结到足以做 clean-room 复现的程度**。在这种情况下，把它继续往 `P2` 推，会把前排资源押在一个不能独立锁样本的对象上。

## Verdict
本轮唯一 follow-up 已用完，结论是 **drop_to_background**。

不是说这条 4H reversal 一定是假的，而是：**在没有 frozen universe / cache 的前提下，它还不能通过我们要求的诚实复现门槛。** 对当前 bot2/bot3 主线来说，这已经足够构成决定性 blocker，不值得再占前排 survivor/P2 资源。

## Result sentence
`Rank 155 / Jamestilfords/statarb-crypto` 没有随 repo 固化可复现的 frozen universe / OHLCV cache；当前按作者公开规则重建样本时，kept universe 已从 notebook 里的 46 漂到 37，说明其 4H reversal 主结论尚不能做出诚实的 clean-room replication，因此本轮唯一 follow-up 收口为 `drop_to_background`。