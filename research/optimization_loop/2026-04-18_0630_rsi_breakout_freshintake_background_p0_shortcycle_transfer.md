# bot3 optimization loop — 2026-04-18 06:30 UTC

## 执行小点
- target: `research/quant_digests/2026-04-18_0431_rsi-breakout-trend-shell.md`
- action: fresh intake first-verdict；只回答这条 `trend-up RSI breakout × ATR trail` 是否值得作为新的 single-asset momentum/trend-following front object 保留，并补 1 个最小 honesty / execution realism blocker

## 结论
`trend-up RSI breakout × ATR trail` 在 repo 可见执行壳压到 `15m/5m` 后只剩正 gross、没有正 net：`ETH/SOL 15m` gross 仍为正但 production-ish friction 后明显转负，`BNB 15m` 与 `ETH 5m` 更差，因此这条线当前不足以留下单一可独立承接的 short-cycle survivor pocket，本轮 fresh intake 直接收口 `background/P0`。

## 关键证据
- digest 已给出最小 portability probe：
  - `ETHUSDT 15m`: `64` 笔，gross mean `+15.79bps/笔`，net mean `-30.08bps/笔`
  - `BNBUSDT 15m`: `58` 笔，gross mean `+3.53bps/笔`，net mean `-45.38bps/笔`
  - `SOLUSDT 15m`: `65` 笔，gross mean `+14.29bps/笔`，net mean `-32.41bps/笔`
  - `ETHUSDT 5m`: `70` 笔，gross mean `+6.84bps/笔`，net mean `-41.26bps/笔`
- honesty / execution realism blocker 已足够收口：当前可见 edge 只停留在慢频 trend shell 压缩后的薄 gross，未覆盖 repo 自报 production-ish friction；且更短周期下 trailing-stop 主导退出，说明噪音/摩擦吞噬快于 continuation 本体兑现。
- 因此不满足 `keep_P1` 的前排保留标准；也没有单一 asset/timeframe 留下可诚实承接的低摩擦 pocket。

## runtime impact
- `Fresh intake slot` 本轮 first verdict：`background/P0`
- 不分配新 Rank（未达到 `keep_P1`）
- `Surviving candidate slot` / `Active P2 slot` / `Paper launch queue` 无变更

## reader-facing delta
- 新结论：这条 repo 更像“4h trend shell 可借鉴，但 short-cycle 不能直接照抄”，当前不构成新的 queue-facing front object。
