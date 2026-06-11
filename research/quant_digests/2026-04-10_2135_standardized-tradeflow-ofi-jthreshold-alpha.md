# 别把这份 2026 OFI repo 只读成 HFT 课堂作业：对 short-cycle desk，更该先测的是「standardized trade-flow imbalance × J-threshold entry」，但必须把 inventory/exit 从 alpha 里拆开

- 时间：2026-04-10 21:35 UTC
- 类型：2026 GitHub repo（`README.md` + `Order_Flow_Imbalance.ipynb`）+ Binance Futures 公共 `aggTrades / 1m klines` portability probe
- 主题类型：raw alpha
- 基础 alpha：**极端化、标准化后的 aggressive trade-flow imbalance（OFI / signed trade flow）在接下来超短窗口内仍能预测同向价格漂移；真正该交易的是“强信号 entry”，不是无止境累积 inventory。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha/microstructure/order-flow/OFI/trade-flow/j-threshold/inventory-cap/latency/adverse-selection/btc/perpetual/1s/1m/3m/repo/public-data/cost/risk
- 证据类型：repo notebook 明确结论 + Binance 公共实时/近实时数据 portability probe

> 先回答一句：**这篇东西的 base alpha 是什么？**
>
> **base alpha = “标准化 aggressive flow 极值会在接下来极短时间里继续推动价格沿同方向漂移”。**
>
> 也就是：不是 VWAP 回归，不是 pairs，不是 filter；它本体就是一条 **microstructure directional raw alpha**。

## 1. 这次看了什么
这次我选的是 GitHub 新仓库：

- **Grant Reed (2026)**
- **_Testing Order Flow Imbalance in Bitcoin Markets_**
- **Venue**：GitHub research notebook / repo
- **DOI**：无
- **Readable URL**：<https://github.com/grantreed1/Crypto-Order-Flow-Imbalance>
- **Notebook URL**：<https://github.com/grantreed1/Crypto-Order-Flow-Imbalance/blob/main/Order_Flow_Imbalance.ipynb>
- **Repo URL**：<https://github.com/grantreed1/Crypto-Order-Flow-Imbalance>

它的核心不是“又一个 OFI 能预测收益”的老话，而是把一个很容易写歪的 HFT 主题拆成两层：

1. **entry alpha 是真的**：标准化后的 signed trade flow 对超短 forward return 有预测力；
2. **但如果把 entry alpha 直接升级成持续加仓 book，风险会吞掉你**：repo 里最大问题不是 entry 无效，而是**没有正式 exit logic**，最后让 inventory risk 把 alpha 变成 drawdown 机器。

这正好适合当前 desk：
- 我们需要补的是 **可独立复现的 raw alpha**；
- 但同时也要区分 **alpha 本体** 和 **execution / risk shell**；
- 这份 repo 给的不是完整 production strategy，却给了一条很清楚的 **entry alpha 原型**。

## 2. 这份 repo 里，最值得拿走的不是“OFI 有用”，而是 3 个具体设计
### 2.1 信号不是原始 signed flow，而是“先去极值、再标准化”的 trade flow
repo 的预处理很明确：

- 先统一数量口径（连 Deribit inverse contract 都做了单位归一）；
- 再计算 `signed_qty`；
- 再做过去 `τ` 窗口的 rolling signed flow；
- 再做 **1%/99% winsorization**；
- 最后用 rolling mean/std 做 **z-score standardization**。

翻成人话：
**它不是在赌“某一笔大单”本身，而是在赌“当前这段 aggressive flow 相对最近分布有多极端”。**

这比直接拿净主动买量做阈值更像一个可迁移的 desk 信号，因为它自动适配了不同时段的成交活跃度。

### 2.2 repo 的交易壳不是每根都做，而是只做 `|β × flow_z| > J`
它先用 train set 拟合：

`predicted_return = β × trade_flow_z`

然后只在预测回报绝对值超过动态阈值 `J` 时出手。`J` 不是拍脑袋固定值，而是由目标参与率（例如 top 5%、10%、20%）反推出来。

这点很重要，因为 OFI 这类东西最大的问题通常不是“完全没 edge”，而是：

> **如果你每根都做，噪音和成本会把 edge 吃光；只有把它压缩成极值 entry，才有交易意义。**

### 2.3 repo 最宝贵的 lesson 不是盈利截图，而是“entry alpha ≠ inventory policy”
repo 在 accounting 里显式加了 `max_inventory_limit`，因为作者自己也发现：

- 没有库存上限时，策略会在错误方向上不断累计仓位；
- 即便 signal 在 entry 端有效，也会因为没有 time-stop / flatten 机制而变成大回撤。

这对我们特别重要：
**这条线应该先被当作“entry alpha generator”，而不是直接当连续做市/持续持仓引擎。**

## 3. repo 原文最值得记住的几个数字
### 3.1 作者自己给的最强参数，不是最短窗，而是 `5s` lookback
repo notebook 的敏感性分析结论是：

- **10ms–100ms** lookback 一直亏；
- **`5s` lookback 最好**；
- 也就是说，这条 alpha 不是越快越好，而是需要一点点 flow 累积，才能把噪音压下去。

这很适合 desk 的现实世界：
你不一定要去卷纳秒；很多时候 **“足够快但不盲目超快”** 的窗口更能迁移。

### 3.2 动态阈值不是越极端越好；repo 结论反而偏中等参与率
作者对 `J-threshold` 的 sweep 结论是：

- **10%–20% participation** 最有效；
- 对应阈值大约在 **`0.35 ~ 0.55 bps`**。

翻成人话：
- top 1% 可能太稀、太容易受异常样本影响；
- 每根都做又太吵；
- **抓“够极端、但仍有足够样本数”的那层信号**，更像 production 思路。

### 3.3 repo 里的 alpha 很亮，但 risk profile 明显不合格
作者给出的完整回测里，最亮眼的是 OKX：

- **Net P&L：`$575,712`**
- **Maximum Drawdown：`-$1.2M`**

更狠的是，作者还给了无库存上限的对照：

- **uncapped drawdown：`-$62.3M`**

这几乎就是在明说：

> **edge 主要在 entry，坑主要在 exit / inventory。**

### 3.4 repo 不是“全市场无脑可搬”，它自己就承认 venue heterogeneity
repo 结论里还提到：

- 高流动 venue（尤其 **OKX / Binance**）上，β 更稳定；
- Binance 的 beta variation 约 **3%**，高流动 venue 大致在 **3%–12%** 区间；
- 数据稀疏的 venue（如 Deribit/Bitstamp）就明显不稳定。

所以这条线本来就更像：
**先在最深的 BTC 主战场做，再想办法横向扩。**

## 4. 为什么它和当前项目直接相关
### 4.1 它补的是 microstructure raw alpha，不是又一篇 overlay
当前 digest 池里已经有：
- OFI × quote-join flow-control shell
- VWAP 偏离 × OFI 纠偏 mean reversion
- adverse selection share / signed-flow continuation

这篇的新增价值在于：

- 它把 **trade-flow z-score → predicted return → J-threshold** 这条链写得很清楚；
- 它不是做均值回归，而是 **directional continuation on aggressive flow**；
- 它还顺手把一个经常被混淆的问题说透：
  - **entry alpha 有效**，
  - **不代表 inventory policy 合格**。

### 4.2 它天然更适合 `1s / 1m / 3m`，不适合硬装成 `15m` 主信号
这也是它对我们最有用的地方：

- 如果你想补 `5m/15m` 的主信号，这条线不该被包装成万能大周期策略；
- 但如果你想补 **超短执行型 alpha 素材池**，它非常合格；
- 尤其适合作为：
  - maker skew / quote-join veto 的方向输入；
  - 1m router 的 fast lane；
  - 事件型 breakout 后的 micro continuation trigger。

也就是说，它不是要替代所有 5m/15m 主题，而是补我们仍然缺的一块：
**极短 horizon 的 microstructure entry alpha。**

## 5. 我做的 public-data portability probe：先问“这条 OFI 还能不能在 Binance 公共流里站住”
### 5.1 Probe A：尽量贴近 repo 原味的 native probe（`aggTrades`）
数据源：
- Binance Futures 公共 `aggTrades`
- 标的：`BTCUSDT`
- 样本：最近约 **20,005** 笔聚合成交
- 时间窗：**2026-04-10 20:58:21 ~ 21:32:59 UTC**

实现口径：
- 用 `m` 字段把成交方向改写成 aggressive buy/sell 的 `signed_qty`；
- 过去 **`5s`** rolling signed flow；
- 做 **1%/99%** winsorize + rolling z-score；
- 用前 **40%** 拟合 `β`，后 **60%** 测试；
- 只做 top participation 的 `|β × flow_z|` 极值信号。

结果（本地文件：`/root/clawd/jerry/momentum/reports/artifacts/literature/ofi_jthreshold_binance_probe_summary_2026-04-10.csv`）：

- **top 5%** 信号：
  - 信号数：`601`
  - 平均 signed PnL：**`+0.549 bps / signal`**
  - 胜率：**`62.4%`**
- **top 10%** 信号：
  - 信号数：`1,202`
  - 平均 signed PnL：**`+0.434 bps / signal`**
  - 胜率：**`62.9%`**
- **top 20%** 信号：
  - 信号数：`2,404`
  - 平均 signed PnL：**`+0.436 bps / signal`**
  - 胜率：**`63.2%`**

这说明两件事：
1. repo 那条“标准化 flow 极值有方向性”的说法，在最近公共流里**没有死**；
2. 但 edge 的量级仍是 **sub-1bp**，所以这更像 **maker / queue-sensitive alpha**，不是随便 taker 往上冲就能赚钱。

### 5.2 Probe B：把它压到 desk 更常用的 `1m / 5m` 频率看会怎样
我又做了一个更 desk-friendly 的 transfer：

- 数据源：Binance Futures 公共 `1m klines`
- 用 `taker_buy_base_volume` 构造 bar-level signed flow proxy：
  - `signed_flow = 2 * taker_buy_base - total_volume`
- 先看 `1m -> next 1m`
- 再看 `5m -> next 5m`

结果：

#### `1m` transfer（近 `1500` 根）
- **top 10%** 信号：
  - 信号数：`90`
  - 平均 gross signed return：**`+0.674 bps / trade`**
  - 胜率：**`61.1%`**
- **top 5%**：`+0.493 bps`
- **top 20%**：`+0.479 bps`

#### `5m` transfer（由同一批 1m 聚合）
- **top 10%** 信号：**`-6.65 bps / trade`**
- **top 5%**：**`-3.19 bps / trade`**
- **top 20%**：**`-3.40 bps / trade`**

### 5.3 这个 probe 最重要的结论
一句话：

> **这条 alpha 在 native 超短频仍像 directional edge，但一旦压到 `5m`，至少在这个公共 proxy 上已经不再像同一条东西。**

所以对当前 desk，最诚实的定位应该是：
- `1s / trade-time / 1m`：可以继续测
- `5m / 15m`：不要硬装主 lane

## 6. 这条东西最适合怎么 desk 化
### 6.1 不要直接复制 repo 的 inventory accumulation
最容易犯的错是把它写成：
- 有正向 predicted return → 持续加同向仓位

这正是 repo 自己用大回撤演示过的坑。

更合理的第一版应该是：
- **entry-only alpha**
- 固定短持有
- 快速 flatten
- 强 inventory cap

### 6.2 一个更适合我们的最小策略壳
我会把第一版写成：

- universe：`BTCUSDT perp` 起步
- signal：`flow_z` 进入 top `5%~15%` 极值区
- entry：仅在 `predicted_return` 与 spread/fee/queue 条件同时满足时入场
- hold：`1s ~ 3m` 的 time-stop，而不是等反向信号无限持有
- exit：
  - 固定时钟平仓
  - 或 microprice / spread 恶化就撤
- sizing：
  - 单次 clip 小
  - 总 inventory hard cap
  - 连续同向信号只允许小幅加码
- cost：
  - taker 视角单独记
  - maker / passive fill 单独记
  - 延迟与未成交率一定要显式建模

### 6.3 它服务于哪个更大的 raw alpha 组件？
如果把它放进更大的 stack，它最适合服务于：

- **microstructure directional continuation** 主 alpha；
- 或者服务于更上层的 breakout / impulse 策略，充当 **fast admission / execution router**；
- 但不适合作为中慢频 `5m/15m` 单独主信号长期裸跑。

## 7. 风险与保留意见
### 7.1 repo 数据不公开，公共 probe 只是 portability，不是 faithful replication
repo 本身用的是六家交易所的高频 trade data，且用了 Databento 本地 parquet；我这里只是验证：

> **这个“标准化 OFI × J-threshold”思想，能不能在公开数据上做出最小近似。**

答案是能，但不是 full replication。

### 7.2 公共 transfer 明确提醒：这条 edge 不是天然可压到 5m
这次最有价值的负结果其实是：

- `1m` 还有一点 gross edge；
- `5m` 已经不像。

这反而帮我们省时间：
**别把本来属于超短执行层的信号，硬塞进 5m/15m raw alpha 池。**

### 7.3 如果用 taker 视角，它很可能被成本吃掉
native / 1m probe 的 gross edge都不到 1bp 级别。
所以 production 前必须回答：

- 你是否真能拿到被动成交？
- 延迟后还有多少剩余 edge？
- 成交概率和 adverse selection 如何权衡？

否则这条线很容易变成“统计上显著，交易上不赚钱”。

## 8. 下一步怎么测
### 8.1 先做 faithful replication 的最小版
优先补齐 repo 的核心口径：
- BTCUSDT 一条线先跑全
- 5s flow / 1s horizon 对齐
- `target_participation = 5% / 10% / 20%`
- accounting 同时跑：
  - fixed holding flat model
  - repo 风格 inventory model
- 对比看：entry alpha 和 inventory risk 各自贡献多少

### 8.2 再做 production admission
如果 faithful replication 站得住，下一步最该看：
1. **maker fill-adjusted expectancy**
2. **latency shock 下 beta 是否崩**
3. **spread 扩张时 edge 是否反而更差**
4. **连续同向信号的边际信息增量**
5. **从 BTC 扩到 ETH/SOL 后，是否仍只有深流动主场才成立**

### 8.3 最值得做的 A/B
- `5s` vs `10s` flow window
- `1s` vs `3s` vs `10s` hold
- passive-only vs mixed maker/taker
- pure BTC vs BTC+ETH 两标的
- 裸 OFI vs OFI + spread veto vs OFI + queue imbalance veto

## 9. 一句话结论
**这份 2026 OFI repo 真正值得 desk 先复现的，不是“高频很赚钱”这句空话，而是：标准化 aggressive flow 的极值本身就是一条可独立复现的超短 directional raw alpha；但它应该被当成 entry alpha generator，而不是不设 time-stop 的连续 inventory engine。**

## 10. 来源
- Grant Reed. (2026). *Testing Order Flow Imbalance in Bitcoin Markets*.
- Venue: GitHub research repo / notebook
- DOI: 无
- Readable URL: <https://github.com/grantreed1/Crypto-Order-Flow-Imbalance>
- Notebook URL: <https://github.com/grantreed1/Crypto-Order-Flow-Imbalance/blob/main/Order_Flow_Imbalance.ipynb>
- Repo URL: <https://github.com/grantreed1/Crypto-Order-Flow-Imbalance>
- 本地 probe 结果：
  - `/root/clawd/jerry/momentum/reports/artifacts/literature/ofi_jthreshold_binance_probe_summary_2026-04-10.csv`
  - `/root/clawd/jerry/momentum/reports/artifacts/literature/ofi_jthreshold_native_probe_signals_2026-04-10.csv`
