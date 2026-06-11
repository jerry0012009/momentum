# Rank 201 / UTC clock seasonality low-switch schedule — P2 admission promote P3

- 时间：2026-03-27 21:58 UTC
- 对象：`Rank 201 / UTC clock seasonality low-switch schedule`
- 本轮角色：bot3 对当前唯一 `Active P2` 做 admission 出口决策；必须在 `promote_P3 / one-time P2->P1 re-scope / drop_to_background` 中一次性收口，而不是继续开放式 `keep_P2`

## 结论
**单一正式 verdict：`promote_P3`。**

更准确地说，当前值得进入 `Paper launch queue` 的对象是：

> **8 币 perp 等权的固定 UTC 低切换 schedule：`20:00~21:59 UTC long`，`22:00~23:59 UTC short`，执行在 `15m` bar，上线候选先按静态 pocket desk sleeve 处理。**

这轮不再允许把它继续拖在开放式 `P2`。原因很简单：现有证据已经足够回答“它是否值得 paper trade / paper launch”。答案是 **值得**。

## Admission 五维收口

### 1) effectiveness / expected return
沿用 survivor 阶段已经确认过的 `8` 币 `15m` executable 口径（`BTC, ETH, SOL, BNB, XRP, DOGE, ADA, LINK`；样本 `2026-01-01` ~ `2026-03-26 UTC`）：

- 目标 schedule：`20~21 UTC long / 22~23 UTC short`
- 组合净后 cumret：`+18.8%`
- 组合日频 Sharpe：`2.96`
- 交易结构：每天固定 `3` 次仓位变化（long open、flip、flat）

成本梯度：
- `2 bps` 单边：净后 cumret `+27.0%`
- `4 bps` 单边：净后 cumret `+18.8%`
- `6 bps` 单边：净后 cumret `+11.2%`
- `8 bps` 单边：净后 cumret `+4.0%`
- `10 bps` 单边：净后 cumret `-2.7%`

所以这条线并不是“只在零成本才成立”的纸面 alpha；它在常见 perp desk 的中低成本区间仍可存活，只是明显 **不是 taker-heavy 任意成本都能扛**。

### 2) cross-asset stability
`4 bps` 单边下，8 个币都没有翻负：

- BTC：`+3.9%`
- ETH：`+16.1%`
- SOL：`+32.2%`
- BNB：`+6.5%`
- XRP：`+5.8%`
- DOGE：`+32.6%`
- ADA：`+30.9%`
- LINK：`+25.6%`

这回答了 admission 最关键的一条：它不是靠单一币或 BTC 一条腿硬撑出来的“伪跨资产”。

### 3) time stability
按月拆分，`4 bps` 单边下三个月都为正：

- `2026-01`：`+7.2%`
- `2026-02`：`+8.0%`
- `2026-03`：`+3.0%`

也就是说，当前收益并非只集中在一两周的偶然窗口；至少在当前最近一个季度里，它是持续贡献而不是单月爆点。

### 4) parameter stability
我补了与目标 pocket 相邻的几组最小邻域检查，避免把 admission 建立在“唯一一点点到为止”的脆弱参数上：

- `21 only long / 22~23 short`：净后 cumret `+9.6%`
- `20~21 long / 23 only short`：净后 cumret `+18.9%`
- `19~21 long / 22~23 short`：净后 cumret `+17.4%`
- `20 only long / 22~23 short`：净后 cumret `+10.9%`
- 只有 `20~21 long / 22 only short` 明显掉到接近失效：净后 cumret `+1.7%`

这说明它不是只靠某个单一 bar 的“尖点参数”活着；更诚实的系统认知是：

> **这条 alpha 的稳健部分在于“20~23 UTC 这段连续 pocket 存在一个低切换的 long-to-short 过渡结构”，而不是非得锁死在唯一字符串参数。**

同时也能看到：**short sleeve 只做 `22` 一小时会显著变差**，所以正式 paper 版不应随意把 short 半边压缩成 1 小时。

### 5) honesty / execution realism
这轮没有继续补华而不实的新维度，而是直接围绕现实执行边界收口：

- 使用的是公共 Binance perp `15m` 缓存，而不是 repo 自报净值截图；
- 规则是固定时钟开平仓，因果边界清楚，没有 lookahead；
- 成本按实际换仓次数扣除，不是假装只有开仓成本；
- 当前最真实的限制也很明确：这条 sleeve **对成本敏感**，更适合 maker-ish / mixed 执行，而不是高冲击 taker-heavy 裸跑。

所以它当然还不完美，但已经足够 honest 到可以进入 paper queue；不存在“必须再加一轮 admission 才敢决定”的单一决定性 blocker。

## 为什么这轮必须 promote_P3
### 不是继续 keep_P2
policy 已经写死：当 `P2` 结论达到“足够值得进入 paper trade / paper launch、比较可能成型、无明显致命问题”时，bot3 必须直接升级。

当前这条线已经满足：
- 有净后收益；
- 有跨资产存活；
- 有最近季度时间稳定性；
- 有相邻参数鲁棒性；
- 有清楚的执行与成本边界。

继续写 `keep_P2` 只会变成低杠杆拖延。

### 不是 one-time P2->P1 re-scope
不需要。当前并不存在唯一明确、必须退回去重写 scope 才能继续的 blocker。反而对象已经足够具体：
- 频率：`15m`
- 宇宙：8 币 perp 等权
- 时钟：`20~21 UTC long / 22~23 UTC short`
- 诚实边界：更适合 maker-ish / mixed cost

### 不是 drop_to_background
也不成立。若这轮出现的是“只在单月赚钱”“只靠 1 个币”“一换成本就死”“参数一挪就崩”，那才该 drop。当前都不是。

## 与 Rank 200 的关系
`Rank 201` 与 `Rank 200` 同属 clock/schedule family，但它们不是同一个对象：

- `Rank 200`：BTC-only、weekday-hour sparse weak buckets、monthly refresh、4h short
- `Rank 201`：8 币 cross-asset、daily fixed UTC pockets、低切换 long+short sleeves

因此更诚实的运行态应该是：
- `Rank 200` 保持 `connected_runner_live`
- `Rank 201` 作为新的 `P3 / Paper launch queue` 头部，进入最小 launch wiring

## 本轮改变系统认知的一句话
`Rank 201 / UTC clock seasonality low-switch schedule` 的 admission 已诚实收口：`20~21 UTC long / 22~23 UTC short` 在 `8` 币 perp `15m` 口径下不仅成本后仍为正，而且三个月持续为正、跨资产不过分依赖单币、邻近 pocket 也大体同向，因此它已经足够值得进入 paper trade / paper launch，本轮应直接从 `Active P2` 升入 `P3 / Paper launch queue`。
