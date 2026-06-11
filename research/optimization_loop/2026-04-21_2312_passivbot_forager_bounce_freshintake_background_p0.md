# bot3 optimization loop — passivbot forager bounce fresh intake -> background/P0

- Time: 2026-04-21 23:12 UTC
- Cycle item: 1/4
- Target: `research/quant_digests/2026-04-21_2154_passivbot-forager-grid-bounce-alpha.md`
- Action: fresh intake first verdict for `volatility-forager × contrarian grid bounce capture`

## What I checked

按 cycle_plan 只补 1 个最小 decisive blocker：在 digest 原始 broad taker probe 之外，补做 `更严格 shock admission + symbol-router + 最小 maker-first fill realism`。

实现口径：
- Binance USDⓈ-M liquid majors，`5m/15m`，最近 `1500` 根
- forager router：`rr_mean` 横截面 `top1/top2/top3`
- stricter shock admission：`|ret_z| >= 2.0 / 2.25 / 2.5`
- minimal maker-first realism：不用 next-open 直接成交；改成下一根用 `3/5/8bps` 的更优限价挂单，只有该 bar 真实触达才算 fill
- exit 继续保持 digest 同类最小 baseline：`5m TP=15bps / SL=40bps / timeout=6`，`15m TP=25bps / SL=60bps / timeout=4`
- 统一 roundtrip 成本仍按 `8bps`

## Result

结论：`volatility-forager × contrarian grid bounce capture` 的 fresh intake first verdict 直接收口 `background/P0`；即使把 admission 收紧并加入最小 maker-first fill realism，留下的正 pocket 仍主要是 `15m LINK`，次级仅有 `5m DOGE/ADA` 的极薄单币结果，全部仍只出现在单一 `2026-04` 窗口，不能证明存在至少两个非单一幸运币/月份支撑的独立 after-cost bounce alpha。

## Key evidence

原 digest 基线：
- `5m ALL`: `316` 笔，`gross -2.96bps/笔`，`net8 -10.96bps/笔`
- `15m ALL`: `351` 笔，`gross -6.62bps/笔`，`net8 -14.62bps/笔`

最小 honesty 子检查后，能留下的 `n>=10` 正 net pocket 只有这些：
- `15m top3, z>=2.0, maker pullback 5bps`: `LINKUSDT` `n=16`, `net8 +5.93bps/笔`, `win 81.3%`
- `15m top3, z>=2.25, maker pullback 5bps`: `LINKUSDT` `n=11`, `net8 +3.50bps/笔`
- `15m top3, z>=2.5, maker pullback 5bps`: `LINKUSDT` `n=10`, `net8 +2.15bps/笔`
- `5m top2, z>=2.25, maker pullback 8bps`: `DOGEUSDT` `n=10`, `net8 +1.50bps/笔`
- `15m top2, z>=2.0, maker pullback 8bps`: `ADAUSDT` `n=49`, `net8 +0.96bps/笔`
- `5m top1, z>=2.0, maker pullback 8bps`: `ADAUSDT` `n=30`, `net8 +0.58bps/笔`

但这些 pocket 都没有通过本轮 success criterion：
1. 没有形成“至少两个非单一幸运币/月份”的 clean after-cost pocket；
2. 剩余厚度普遍很薄，除了 `15m LINK` 外都接近成本线；
3. `15m LINK` 本身也仍是单币、单窗口结果，更像 router hit，而不是 desk 现在要保留的独立 raw alpha；
4. 因此新增价值仍更偏向 Passivbot 的工程/执行壳提示，而不是可前排保留的 standalone bounce alpha。

## Runtime impact

- 本对象不保留 survivor，不分配 Rank。
- `Fresh intake slot` 按条件切到下一条：`research/quant_digests/2026-04-21_2232_dynamic-cointegration-halflife-admission-alpha.md`
- cycle item 1 标记为 `done`
