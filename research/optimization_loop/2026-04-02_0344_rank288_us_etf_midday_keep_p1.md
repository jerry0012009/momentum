# bot3 optimization loop — Rank 288 first verdict

- Time: 2026-04-02 03:44 UTC
- Item: `research/quant_digests/2026-04-02_0158_us-etf-midday-momentum-pocket-alpha.md`
- Rank: `288`
- Outcome: `keep_P1`

## What was checked

按当前轮 `cycle_plan`，本轮只回答这一个 fresh intake 是否已经具备可独立审计的 intraday raw alpha skeleton：

- 对象是否有清晰主语：`IBIT / FBTC / ETHA / FETH`
- 时间 pocket 是否明确：`11:00–11:30 ET` signal，`11:30–12:00 ET` hold
- entry / exit / direction 是否已经能直接写成规则：regular-session ETF 横截面 momentum，或 `BTC complex vs ETH complex` 的 crypto RV 映射
- realism 边界是否已经写清：regular-session 成本较 AH 更诚实，但 crypto 映射侧仍需独立做 fee / delay / sizing 会计
- 这条主题是否只是 close-window 旧 pocket 改写：不是；它是 regular-session midday pocket，且 notebook 给出的日度 PnL 相关性与 close anchor 仅约 `0.014`

## Decision

结论是：这条 `US crypto ETF midday 30m momentum pocket` 已经具备**可独立审计的 raw alpha skeleton**，但证据层级目前仍主要停留在 notebook/source-audit 与作者给出的 window sweep / 组合相关性输出，尚未完成我们自己管线里的 clean-room ETF 复现，也未完成 `BTC vs ETH perp` 映射下的 post-cost / delay / sizing 诚实 admission。

因此本轮不给 `P2`，先记为 `keep_P1`。

## Why this changes runtime truth

这一步改变的系统认知是：

> `Rank 288 / US crypto ETF midday 30m momentum pocket` 不是 close-window 旧故事的重复，也不是只有概念词的 ETF commentary；它已经具备清晰 universe、固定 session pocket、明确 entry/exit、可公开取数的最小 transfer path，因此可以作为合法 fresh intake 留在前排进入唯一一次 survivor follow-up，但在完成 clean-room ETF 复现与 crypto 映射后的成本诚实检验前，还不够直接升 `P2`。

## Runtime updates required

- `Fresh intake slot`：写为 `Rank 288`，verdict=`keep_P1`
- `Surviving candidate slot`：切换为 `Rank 288`，保留唯一一次 follow-up 预算
- `cycle_plan` 当前项：标记 `done`

## Suggested honest follow-up axis for bot2

若 bot2 下一轮继续给这条 survivor 一次机会，唯一高杠杆 follow-up 应优先回答：

1. 这条 pocket 在我们自己的 ETF `5m/15m` clean-room 复现里是否还能保留净 alpha；
2. 映射到 `BTCUSDT vs ETHUSDT perp` 后，在 `30m/45m/60m` hold、`0/1/2 bar` delay 与现实 fee 下是否仍保留可执行 pocket。

若这一步做完仍只剩 notebook 局部表现、或 crypto 映射后被成本吃掉，则应直接收口，不继续拖长。\
