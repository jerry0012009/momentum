# Rank 317 / Pacifica maker quote edge × Hyperliquid taker hedge — survivor follow-up verdict = background/P0

- Time: 2026-04-03 21:54 UTC
- Target: `Rank 317 / Pacifica maker quote edge × Hyperliquid taker hedge`
- Action: survivor one-shot follow-up / minimal maker honesty probe
- Verdict: `background/P0`

## Why this changes runtime truth
`Rank 317` 的唯一 survivor follow-up 已经用掉，而且这次补的不是又一轮 repo 叙事复述，而是直接按 repo 自己的 fee / target 口径去看公开盘口下是否真的存在可存活 pocket。结果显示：在 `BTC/ETH/SOL` 上，连 **未额外加入 fill probability、queue position、refresh/cancel friction、hedge slippage stress** 之前的 fee-adjusted top-of-book edge 都已经持续为负，因此这条对象当前不该继续占用 survivor 前排资源，最诚实的收口是直接回到 `background/P0`。

## What was checked
本轮直接用 repo 明示的公共 WebSocket 入口做统一最小壳抽样：
- Pacifica：`wss://ws.pacifica.fi/ws`，订阅 `{"method":"subscribe","params":{"source":"book","symbol":...,"agg_level":1}}`
- Hyperliquid：`wss://api.hyperliquid.xyz/ws`，订阅 `{"method":"subscribe","subscription":{"type":"l2Book","coin":...}}`
- 标的：`BTC / ETH / SOL`
- 时长：`35s`
- 频率：约每 `0.5s`
- 口径：
  1. `buy Pacifica / sell Hyperliquid`：`((HL_bid*(1-taker_fee) - PAC_ask*(1+maker_fee)) / (PAC_ask*(1+maker_fee))) * 10000`
  2. `sell Pacifica / buy Hyperliquid`：`((PAC_bid*(1-maker_fee) - HL_ask*(1+taker_fee)) / (HL_ask*(1+taker_fee))) * 10000`
  3. 费用取 repo 默认：`Pacifica maker 1.5bps`、`Hyperliquid taker 4bps`
  4. 同时检查 repo 目标 `profit_rate_bps = 15` 下是否出现任何 `>15bps` pocket

产物：`reports/artifacts/optimization_loop/2026-04-03_2154_rank317_pacifica_hl_maker_honesty_probe.json`

## Probe readout
### BTC
- `buy Pacifica / sell Hyperliquid`
  - samples: `70`
  - mean edge: `-5.04bps`
  - best observed edge: `-4.75bps`
  - `edge > 0 / 5 / 10 / 15bps` 占比：全部 `0%`
- `sell Pacifica / buy Hyperliquid`
  - mean edge: `-6.26bps`
  - best observed edge: `-5.95bps`
  - `edge > 0 / 5 / 10 / 15bps` 占比：全部 `0%`

### ETH
- `buy Pacifica / sell Hyperliquid`
  - mean edge: `-7.37bps`
  - best observed edge: `-5.99bps`
  - `edge > 0 / 5 / 10 / 15bps` 占比：全部 `0%`
- `sell Pacifica / buy Hyperliquid`
  - mean edge: `-4.60bps`
  - best observed edge: `-3.07bps`
  - `edge > 0 / 5 / 10 / 15bps` 占比：全部 `0%`

### SOL
- `buy Pacifica / sell Hyperliquid`
  - mean edge: `-4.26bps`
  - best observed edge: `-4.01bps`
  - `edge > 0 / 5 / 10 / 15bps` 占比：全部 `0%`
- `sell Pacifica / buy Hyperliquid`
  - mean edge: `-8.12bps`
  - best observed edge: `-6.62bps`
  - `edge > 0 / 5 / 10 / 15bps` 占比：全部 `0%`

## Honest interpretation
这轮已经足够回答 bot2 给 survivor 的唯一问题：

> 在 repo 明写的 `maker fee 1.5bps + taker fee 4bps + target 15bps` 口径下，`Rank 317` 当前公开可复现的 majors top-of-book 并没有出现任何可净正、更不用说可穿过 `15bps` target 的 pocket。

更关键的是，这里还没开始往更保守的方向加：
- Pacifica maker **fill probability**
- **queue position** 与 partial fill
- fill 后到 Hyperliquid hedge 的 **latency / slippage**
- quote refresh / cancel race 带来的额外摩擦

也就是说，当前最宽松、最有利于它存活的公开近似都已经不给正值；继续把它留在 survivor，只会变成对同一 evidence axis 的低杠杆重复，不诚实支持 `promote_P2`。

## Runtime consequence
因此本轮把 `Rank 317` 直接从 `Surviving candidate slot` 收口到 `background/P0`，并释放 survivor 槽位；当前前排只保留 fresh intake 头 `Polymarket final-window lag arb` 等待下一轮。若未来要 reopen，这条线需要的是独立于本轮的新证据——例如某些特定 symbol / session 的真实 rebate pocket 或可验证的 venue-specific fill advantage——而不是再做一轮相同 public TOB probe。

## Result sentence
`Rank 317`：唯一 survivor follow-up 已完成；按 repo 默认 `1.5bps maker + 4bps taker + 15bps target` 对 `BTC/ETH/SOL` 做的公共盘口 probe 在双向上都未观察到任何 fee-adjusted 正 edge，更不存在可穿过目标利润的 pocket，因此不诚实支持 `promote_P2`，本轮直接收口到 `background/P0`。
