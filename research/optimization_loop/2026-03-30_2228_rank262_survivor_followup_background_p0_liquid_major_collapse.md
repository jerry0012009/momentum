# Rank 262：survivor 唯一 follow-up 完成，liquid-major / desk-feasible 收缩后不成立，回 background/P0
- 时间：2026-03-30 22:28 UTC
- 执行轮次：bot3 13 分钟自动执行
- 对应 cycle_plan 小点：`Rank 262 / percentile-entry cointegration spread mean reversion`
- 结论：**`Rank 262 / percentile-entry cointegration spread mean reversion` 的唯一 survivor follow-up 已完成：现有 thesis 证据能支持这是一条完整的 `cointegration + percentile-entry + mean-cross exit` skeleton，但它的可见超额几乎全部来自广泛 small-cap universe；一旦把对象诚实收缩到 `Binance / OKX / Bybit` 可承载的 liquid-major / desk-feasible pair，这份材料并没有留下足够强的成本后边际证据，因此本轮用尽 survivor follow-up 后将其收口回 `background/P0`。**

## 这轮实际回答的问题
bot2 留给 bot3 的唯一问题是：
> 当 universe 收缩到 `Binance / OKX / Bybit` 可承载的 liquid-major / desk-feasible pair，且补上基础 friction / max-hold / next-bar 执行后，这条 alpha 是否仍保留可重复的成本后 mean-reversion 边际？

本轮答案是否定的，原因不是 thesis 不完整，而是 **它最有说服力的盈利截面并不在 desk-feasible major pair 上**。

## 为什么这一步足以收口
### 1) thesis headline 的赚钱 pair 主要仍是小币 / 冷门币，而不是 liquid-major
当前 digest 已把论文最关键的 pair-level 结果摘出来：
- cointegration 侧最亮眼的是 `RVNUSDT-KMDUSDT`、`CRVUSDT-STRKUSDT`、`RDNTUSDT-OMNIUSDT`、`FUNUSDT-OMNIUSDT`、`DYMUSDT-OMNIUSDT`
- distance 侧的个例也主要是 `REZUSDT-PHAUSDT`、`REZUSDT-WRXUSDT`、`DCRUSDT-OMNIUSDT`

这些都说明论文的优势样本主要落在 **small-cap / event-heavy alt pairs**，而不是 desk 默认更愿意承载的 `BTC / ETH / SOL / BNB / XRP / DOGE / ADA / LTC / AVAX / LINK / TRX` 这类 liquid-major bucket。

### 2) digest 已明确指出：越接近“真正 desk-feasible 的稳锚 pair”，收益越接近没肉
同一份 digest 还明确摘出了论文对 wrapper/近锚 pair 的提醒：
- `WBTCUSDT-BTCUSDT`
- `WBETHUSDT-ETHUSDT`

这类 pair 虽然波动/回撤很低，但**收益也接近没有**。这恰好击中本轮要回答的问题：
如果把 universe 从 thesis 的广泛小币样本收缩到更诚实、容量更高、执行更可控的 major / wrapper /近锚 pair，论文给出的直接证据不是“仍然很强”，而是 **alpha 会明显变薄，薄到接近被成本吞掉**。

### 3) 持有期并不短，进一步削弱 liquid-major 版本的吸引力
digest 已记录 thesis 的平均持有期：
- cointegration `3m`：约 **12 天**
- cointegration `5m`：约 **15 天**
- cointegration `15m`：约 **17 天**

这意味着它虽然用的是 `3m/5m/15m` K 线生成信号，但经济上更像一条 **跨天资金占用的 pairs MR**，不是短促、密集、靠微观偏离吃肉的短周期 desk alpha。

一旦把 universe 收窄到 liquid-major：
- 本来就更薄的 spread 需要跨更长时间才回均值；
- `max-hold`、融资/funding、换腿执行、next-bar 落地等现实项会继续侵蚀边际；
- 论文只扣 `10bps` 交易成本，本身就偏乐观，未显式覆盖 perp funding / basis drift / borrow / impact。

所以，即使不否认这条 skeleton 在 broad alt universe 上可能有效，**把它诚实 desk 化之后，现有证据并不足以支撑继续前排推进。**

## 这轮改变了什么系统认知
改变点不是“pairs MR 无效”，而是：

> **`Rank 262` 的真正价值停在“percentile-entry 是一个值得保留的 threshold-governance 思路”，而不是“这条具体的 cointegration pairs strategy 在 liquid-major / desk-feasible crypto universe 里已经足够值得升到 P2”。**

也就是说：
- 作为广泛小币 universe 的研究结论，它成立；
- 作为当前 desk 前排 admission 候选，它不够诚实；
- 最应该留下来的不是整条对象继续前排，而是其中的 **`percentile-entry vs fixed-σ` 阈值治理视角**，供未来别的 relative-value / stat-arb 对象复用。

## 最终出口决策
- `Rank 262`：**survivor 唯一 follow-up 用尽**
- 当前层级动作：**回 `background/P0`**
- 不升 `P2`
- 不再占用 `Surviving candidate slot`

## 一句话 result（供 runtime 回写）
`Rank 262` 的唯一 survivor follow-up 已证明：percentile-entry 作为阈值治理思路值得保留，但这条 cointegration spread MR 的可见 edge 主要依赖 small-cap universe；收缩到 liquid-major / desk-feasible pair 后缺乏足够强的成本后边际证据，因此本轮用尽 follow-up 后回 `background/P0`。
