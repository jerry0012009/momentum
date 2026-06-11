# Rank 177 / funding-boundary-post-settlement-spread-alpha — survivor follow-up 收口（park_to_background）

- 时间：2026-03-26 04:01 UTC
- 对象：`Rank 177 / funding-boundary-post-settlement-spread-alpha`
- 轮次角色：bot3 auto optimization
- 动作类型：survivor follow-up（唯一一次）
- 结论：**park_to_background**

## 本轮只回答一个问题
`post-settlement long richest funding / short cheapest funding spread` 这条 funding-boundary event-driven relative-value 骨架，在 **major perp 高流动性币池**、`top1/top3/top5` 排名、`+0m/+1m/+3m` 入场口径下，扣除保守成本后，是否仍保有诚实可交易净边；以及 alpha 到底来自 `spread` 还是某一侧单腿。

答案：**当前不够诚实，不升 P2；应收口停在 background pool。**

## 本轮最小诚实快检怎么做的
- universe：12 个高流动性 Binance USDT perp 主流币
  - `BTC/ETH/BNB/SOL/XRP/ADA/DOGE/LINK/AVAX/LTC/DOT/BCH`
- 样本：最近 21 天、`00/08/16 UTC` 主 funding 结算事件，共 **63** 个事件；其中能完整对齐 funding + `1m` 价格的有效样本约 **25** 个
- 交易表达：
  - `top1/top3/top5 richest vs cheapest` 等美元 spread
  - 同时拆出 `long richest only` 与 `short cheapest only`
- 口径：比较 `entry +0m/+1m/+3m`，持有 `15m/60m`
- 成本：保守按 pair all-taker round-trip **16 bps** 扣减

## 结果摘要
### 1) spread 本体在高流动性主流币池里几乎没有净边
所有 `top1/top3/top5 × +0m/+1m/+3m × hold 15m/60m` 的组合里：
- **gross spread** 大多只在 `-3.9 ~ +2.1 bps` 附近；
- 扣除 **16 bps** 保守成本后，**全部为负**；
- 最好的也只是：
  - `top1, +1m, hold15m`：gross **+2.12 bps**，net **-13.88 bps**
  - `top5, +0m, hold15m`：gross **+1.26 bps**，net **-14.74 bps**
- `60m` 口径没有重现 digest 里那种夸张延续；在主流币池里反而多数组合为轻微负值。

### 2) alpha 并不来自稳定的 market-neutral spread，而更像偶发的单腿噪声
方向拆分后：
- `long richest only` 常常是小幅正，但不稳定；
- `short cheapest only` 多数口径要么为负、要么贡献很弱；
- 也就是说，先前 digest 里看上去像 `rich-vs-cheap spread` 的东西，在主流币池里**没有稳定落成双腿都能支撑的 relative-value alpha**。

例子：
- `top1, +0m, hold15m`：
  - long richest **+7.60 bps**
  - short cheapest **-7.50 bps**
  - spread 只剩 **+0.05 bps**
- `top3, +0m, hold15m`：
  - long richest **+8.21 bps**
  - short cheapest **-5.82 bps**
  - spread **+1.20 bps**
- `top5, +3m, hold60m`：
  - long richest **+3.79 bps**
  - short cheapest **-10.24 bps**
  - spread **-3.22 bps**

### 3) 即便只看 funding-gap 前 25% 最大的事件，仍然过不了成本线
极端 funding gap 事件确实略有改善，但仍不够：
- `top1, +0m, hold15m`：gross **+9.51 bps**，net **-6.49 bps**
- `top1, +1m, hold15m`：gross **+10.33 bps**，net **-5.67 bps**
- 其余大多仍在 **-12 ~ -19 bps net** 区间

这说明：即便承认“极端事件里有些价差延续”，它也还没有被证明能在主流高流动性池里，诚实地长成一个可推进到 P2 admission 的可交易 spread skeleton。

## 为什么这轮不做 re-spec，而是直接 park
这轮没有出现一个**唯一明确且高杠杆的 re-scope 方向**。

如果把它硬改成：
- 只做单腿 richest continuation，或
- 回到小币 / 极端币 funding crowding 题材，或
- 只做 gap 前 10~25% 极端事件

那已经不再是当前 survivor 被保留的那条 **`post-settlement rich-vs-cheap funding spread`** 骨架，而是在改写成别的对象。按 policy，这种情况下最诚实的动作不是勉强保留，而是把当前对象收口放回 background pool。

## 本轮改变的系统认知
**Rank 177：在 major perp 高流动性币池里，`post-settlement long richest funding / short cheapest funding spread` 没有重现可扣成本的稳定净边，且 alpha 不来自稳健的双腿 spread，因此本轮 survivor follow-up 收口为 `park_to_background`，不升 P2。**
