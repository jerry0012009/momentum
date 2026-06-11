# bot3 optimization loop — term-structure calendar spread keep_P1

- 时间：2026-03-24 07:45 UTC
- 路径判断：Scout
- 顶板动作：`Next 3 bot3 runs #1 = 重开 fresh intake`
- 本轮对象：term-structure calendar-spread reversion raw alpha
- intake 来源：`research/quant_digests/2026-03-24_0734_term-structure-calendar-spread-reversion-raw-alpha.md`

## 本轮只推进的 1 个主点
认领一条新的、可独立复现的 raw alpha：**BTC 近月/次季年化基差差值（term spread）极端偏离后的 calendar spread 回归**。

为什么这条线够资格进 fresh intake：
1. 不是 overlay，而是完整 raw alpha 本体：`entry / exit / sizing / risk / cost` 都能单独写清。
2. 来源合规：`2026` 新 repo + 近 5 年定价论文 + Binance 公共数据。
3. 与当前 desk 兼容：主信号可放在 `15m`，执行可下钻到 `1m/3m/5m`。

## 紧邻 1 个子点（最小诚实守门）
只补一刀最关键的 honesty 判断：**现有证据足够支持 `keep_P1`，但还不够直接升 `P2`**。

当前已知最硬证据：
- 本地快检样本：`2026-02-24 ~ 2026-03-24`，`BTCUSDT`，`15m`
- 信号：`|z(term_spread)| >= 2` 做回归，`|z| <= 0.5` 或 8 bars 退出
- 非重叠极端事件：`116`
- 2 小时内回归成功率：`94.0%`
- 最新快照：近月年化基差约 `9.15%`，次季约 `2.30%`，term spread 约 `-6.85pp`

但仍未过线的点：
- 目前只有“事件会回归”的证据，**还没有把它净值化成 post-cost non-overlap PnL**；
- README 的高 Sharpe/高回报口径还未独立复核；
- 交割合约切换 / DTE 假极值 / 执行成本，仍可能把表面 edge 吃掉。

## 本轮 verdict
**`keep_P1`**

一句会改变系统认知的话：
> term-structure calendar-spread reversion 已完成 fresh intake；当前结论是 `keep_P1`，因为它具备完整可交易骨架且 15m 极端 term spread 事件在近 30 天有 `94.0%` 的 2h 内回归，但还没过 post-cost PnL 诚实门槛。

## 简短 scorecard
- raw alpha 独立性：`通过`
- 可直接落地完整策略骨架：`通过`
- 公共数据最小复现：`通过`
- 成本后可交易性：`未证实`
- 当前 desk 动作：`keep_P1，保留唯一一次 decisive follow-up`

## 下一轮唯一合法 follow-up
只做一件事：把 `event reversion` 转成 **post-cost non-overlap PnL**，直接回答：`park / promote_P2`。

## 本轮写回
- 更新 `docs/BOT2_BOT3_STATE.md`
- 更新 `docs/TODO.md` 的当前项目状态
