# 别把 on-chain flow 只当情绪看板：这篇 2024/2025 论文更该先复现的是「ETH 交易所净流入 → 后续 1~6h ETH 下行」raw alpha
- 时间：2026-03-25 08:05 UTC
- 类型：2024 arXiv 论文（2025 v2）+ 全文本地抽取 + desk 化策略拆解
- 主题类型：raw alpha
- 基础 alpha：**ETH 流入交易所**代表更直接的可卖出供给，后续 `1h / 2h / 3h / 4h / 6h` 的 ETH 收益更偏负；对 desk 来说，最直接的最小版本就是 **按小时聚合链上 ETH 交易所净流入做 ETH 短周期 short alpha**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/time-series/on-chain/eth/exchange-netflow/flow-pressure/event-driven/short-bias/usdt/liquidity/1h/5m/15m/external-data/paper
- 证据类型：论文全文抽取 + desk 化最小实验设计

> 先回答 base alpha：**这不是 filter，也不是 overlay。base alpha 就是“ETH 交易所净流入上升 → 未来 1~6 小时 ETH 更弱”**。同一篇论文里，`USDT` 交易所净流入更像 companion flow：它偏向给 BTC/ETH 带来短期买盘干粉，因此更适合拿来做 **regime / veto / pair-leg 修正**，而不是替代主 alpha 本体。

## 1) 这次看了什么
主线材料：
- **Yeguang Chi, Qionghua (Ruihua) Chu, Wenyan Hao (2024/2025)**
- **Title:** _Return and Volatility Forecasting Using On-Chain Flows in Cryptocurrency Markets_
- **Venue:** arXiv working paper / econ.EM
- **Readable URL:** `https://arxiv.org/abs/2411.06327`
- **PDF:** `https://arxiv.org/pdf/2411.06327`
- **DOI:** `10.48550/arXiv.2411.06327`

这篇东西最值钱的地方，不是“on-chain 很重要”这种大话，而是它给了一个很明确、可直接翻译成交易语言的结论：

1. **ETH 净流入交易所**，对应的是更直接的卖出意图；
2. 这个卖压在 **未来 1~6 小时** 上，对 ETH 回报有持续负向预测力；
3. 同时，论文还发现 **USDT 净流入交易所** 更像 buy-side dry powder，对 BTC/ETH 的短时回报反而偏正。

翻成人话就是：

- **ETH 往交易所冲**，更像有人准备卖 ETH；
- **USDT 往交易所冲**，更像有人准备拿稳定币去买币；
- 所以同样都叫“交易所净流入”，资产语义并不一样。

这正适合 desk：
- 主信号可以做成 **ETH directional short alpha**；
- 同篇材料顺手还能拆出一个 **USDT companion filter**，专门防止把“ETH 卖压”与“稳定币干粉入场”混在一起。

## 2) 核心结论
- **一句话核心结论：** 这篇 2024/2025 论文里，最值得我们先复现的不是笼统的 on-chain 解释，而是 **ETH 交易所净流入 → 未来 1~6h ETH 下行** 这条单资产、可独立交易的 raw alpha。
- **一句话 desk 读法：** 先把它做成 **小时级事件更新、分钟级执行的 ETH short alpha**；再用同文里的 **USDT 净流入** 去做 short-side veto / size-down / beta-hedge 调整。

3 个关键数据点：
1. **样本期：** `2017-12-16` 到 `2023-01-20`，检验未来 `1 / 2 / 3 / 4 / 6` 小时。
2. **ETH 主结论：** 在双变量模型里，ETH 净流入对 ETH 后续回报在 `1h / 2h / 3h / 4h / 6h` **全部显著为负**；对应 t 值大约是 **`-5.96 / -2.14 / -2.09 / -2.58 / -3.80`**。
3. **USDT companion 结论：** USDT 净流入对 BTC/ETH 后续回报主要在 `1h / 2h` **显著为正**；例如 ETH 那条在 `1h / 2h` 的 t 值大约是 **`5.98 / 2.90`**。

如果只看“显著性”而不做人话拆解，很容易写成一堆回归表。但 desk 真正在意的是：

- **ETH inflow = 可卖出筹码上所，偏 bearish；**
- **USDT inflow = 可买入干粉上所，偏 bullish；**
- 这两条可以在同一时点相互冲突，所以主 alpha 与 companion filter 必须拆开。

## 3) 为什么这轮值得排在前面
它比继续找一篇“解释为什么 crypto 会波动”的文章更值得，原因有三个：

1. **base alpha 非常清楚。**
   不是“市场状态可能影响收益”，而是 **ETH exchange netflow 对未来短时 ETH 回报有直接方向性**。

2. **天然适合 5m / 15m desk。**
   虽然原文预测频率是 `1h~6h`，但这并不妨碍用作分钟级执行：
   - 信号每小时更新一次；
   - 执行落在下一根 `5m/15m`；
   - 出场还是分钟级实现。

3. **旁支想法也很 desk-friendly。**
   同一篇材料里，`USDT` 流入不是抢主标题的 alpha，本质更像：
   - `short ETH` 的 veto / size-down 条件；
   - 或者把 naked short 改造成 **`short ETH / long beta-adjusted BTC`** 的 relative-value 版本。

也就是说，这不是“只会给你一个回归关系”的材料，而是能自然拆成：
- **raw alpha：ETH exchange inflow short ETH**
- **companion filter：USDT exchange inflow 过滤/稀释 short**
- **desk branch：ETH-vs-BTC beta-hedged flow spread**

## 3.5) 策略拆解（必填）
- 方向属性：single-asset / event-driven / flow-based / short-bias
- 基础 alpha：ETH 交易所净流入上升，意味着更直接的 sell pressure，后续 `1h~6h` ETH 收益偏负
- entry：
  - 每小时统计一次 `ETH_netflow_to_exchanges_usd`
  - 计算过去 `30d` 小时序列 z-score
  - 若 `z >= 2.0`，则在下一根 `5m` 或 `15m` bar 开始做空 `ETHUSDT perp`
  - **companion veto（可选）**：若同时 `USDT_exchange_netflow_z >= 1`，则不直接裸空，改为跳过或减半
- exit：
  - 第一版先测固定持有 `1h / 2h / 4h / 6h`
  - 第二版加早退：
    - `netflow_z` 回落到 `0` 以下；或
    - 价格反弹触及 `entry + 0.75 * ATR_1h`
- sizing：
  - 初版固定 notional
  - 二版按 `target_vol / realized_vol_24h` 做 inverse-vol sizing
  - 若 `USDT_flow_z` 与 ETH 流入同向冲突，size-down 到 `0.5x`
- risk：
  - 同一信号 `no-overlap`
  - 单次事件最多持有 `6h`
  - 宏观数据公布 / ETH ETF headlines / upgrade windows 单独打标
  - funding 已显著偏负时，不要把链上卖压和 perp crowded-short 叠到满仓
- cost：
  - 分钟级执行必须显式计入 taker fee + spread + slippage
  - desk 第一版可先用 **`15 bps round-trip`** 作为保守口径；如果后面确认只在大净流入极值上交易，再回头重估真实冲击成本

## 4) 这篇东西最该怎么读：把“资产语义”拆开，而不是把所有 inflow 都当一个方向
这篇论文真正有用的不是“on-chain flow 有预测力”，而是它提醒我们：

### 4.1 ETH inflow 和 USDT inflow，不是同一种东西
- **ETH inflow**：更像持币者把 ETH 送进可交易场所，卖压解释最直接；
- **USDT inflow**：更像稳定币干粉上所，后续可以转化成买盘；
- **BTC inflow**：在文中对 BTC 收益并不稳定，只有 `4h` 有一段正向关系，不适合当主线。

这意味着：
- 主 alpha 应该先围绕 **ETH inflow short ETH** 做；
- 不要把 `USDT inflow` 粗暴并入同一个“flow factor”；
- 反而更应该把 USDT 那条拿来问：**当前 ETH 卖压，会不会被 stablecoin 干粉部分对冲掉？**

### 4.2 desk 更值得偷的，可能是“冲突流”的处理
同一时点如果出现：
- `ETH inflow z` 很高（偏空）
- 但 `USDT inflow z` 也很高（偏多）

那么它对 naked short ETH 的含义就不再简单。

对 desk 来说，更值得测的不是“把两个信号线性加权”，而是三种离散处理：
1. **ETH inflow high & USDT neutral/low** → 允许做主 short；
2. **ETH inflow high & USDT high** → size-down 或不做；
3. **ETH inflow high & BTC flow neutral** → 优先测 `short ETH / long β·BTC`，把市场共振去掉。

这比把论文 headline 生搬硬套成“链上流入就做空/做多”要诚实得多。

## 5) 外部数据源、公开性与最小可复现实验口径
### 5.1 主 raw alpha 数据源（ETH leg）
- **数据源：** Ethereum 公链原始转账数据（native ETH + 交易所标注地址）
- **公开性：**
  - 链上交易本身公开可得；
  - 交易所地址标签可从公开标签源 / 研究社区标签 / Dune / Etherscan / Arkham 等做第一版近似
- **更新频率：** 实时链上；研究上先按 `1h` 桶聚合
- **最小可复现实验口径：**
  - 选一组交易所标签地址（先从 Binance / Coinbase / Kraken / OKX 开始）
  - 按小时统计 `inflow - outflow`
  - 换算成 USD 后做 rolling z-score
  - 与 `ETHUSDT perp` 的未来 `4 x 15m`、`8 x 15m`、`16 x 15m`、`24 x 15m` 回报做对齐

### 5.2 companion filter 数据源（USDT leg）
- **数据源：** 交易所标注地址收到的 USDT 转账（至少先从 Ethereum ERC-20 USDT 开始）
- **公开性：** 链上数据公开；多链合并版更快但通常要借助聚合商
- **更新频率：** 链上实时；研究上先按 `1h` 聚合
- **最小可复现实验口径：**
  - 先做 ETH 主 alpha，不强求第一轮就把 TRON/Omni/多链稳定币全吃下
  - companion filter 第一轮只用 **ERC-20 USDT exchange inflow** 就够了
  - 如果只用 ETH 链上的 USDT 就已经能明显区分 short 样本质量，再升级到多链

### 5.3 为什么这仍然算“可较快拿到”
- 原始数据公开；
- 真正的门槛不是获取，而是 **地址标签治理**；
- 所以它不像宏观低频数据那样只能当 overlay，反而可以作为 **小时更新、分钟执行** 的主信号。

## 6) 对 `1m / 3m / 5m / 15m` 的最小实验
### 6.1 第一版：先做最便宜的 directional short
- universe：`ETHUSDT perp`
- signal clock：每小时整点更新一次
- feature：`ETH_exchange_netflow_usd_z`
- trigger：`z >= 2`
- execution：下一根 `5m` 或 `15m` bar 开空
- holds：`1h / 2h / 4h / 6h`
- overlap：no-overlap
- cost：`15 bps round-trip`

### 6.2 第二版：把同文里的 USDT 结论拿来做 honest filter
- 在第一版上额外加入：
  - `USDT_exchange_netflow_z < 1` 才允许裸空；
  - 或者 `USDT_z >= 1` 时把仓位减半。

这一步的意义不是“多加一个 feature”，而是避免把两种语义相反的 inflow 混成一个大杂烩。

### 6.3 第三版：做 ETH-specific flow 的 relative-value 分支
如果发现：
- naked short ETH 对大盘 beta 太敏感；
- 但 ETH inflow 的边主要体现在 ETH 相对更弱；

那就改测：
- **short ETHUSDT / long β·BTCUSDT**
- 或者直接看 **ETHBTC** 的未来 `1h~6h` 表现。

这会更像 desk 真正能扩素材池的东西：
- 主 alpha 还是 ETH flow；
- 只是把市场方向从净敞口里拿掉。

## 7) 下一步怎么测（直接可执行）
1. **先只做 ETH 一条腿，不要一上来全资产全链路。**
   先确认 `ETH inflow z` 对 `ETHUSDT perp` 的 `4h / 6h` 有没有最基本的 sign consistency。

2. **把触发做成极值桶，而不是线性回归复读。**
   论文证明了 sign，不代表生产最优是线性；desk 下一步应优先做：
   - `z 2~3`
   - `z 3~4`
   - `z > 4`
   看 edge 是否在极端事件桶里集中。

3. **把 USDT flow 只当冲突过滤，不要过早当第二主信号。**
   先回答一个更小的问题：
   - 同样高的 ETH inflow，`USDT_z < 0` 的样本，是否比 `USDT_z > 1` 的样本更适合 short？

4. **测试 beta-hedged 版本。**
   若 directional short 的收益主要被大盘反抽洗掉，就把它改成：
   - `short ETH / long β·BTC`
   - 或 `short ETH / long market basket`
   看论文里的 ETH-specific flow 是否真正留下相对收益。

5. **检查 signal-to-fill decay。**
   这是这类 hourly external signal 最大的坑：
   - 如果 edge 在链上事件发生后的前 `10~20min` 就被 price 走完，15m 执行会很痛；
   - 所以必须把 entry 精细到 `1m / 3m / 5m` 做一次衰减曲线。

## 8) 风险与保留意见
- 论文是回归证据，不是 production-ready backtest；
- 论文里多条系数的**经济量纲不宜直接照抄**，更适合拿 sign / horizon / 资产语义做第一轮转译；
- `ETH inflow` 可公开复现，但**地址标签质量**会决定研究噪音；
- `USDT inflow` 若想做全链统一口径，数据工程会明显更重；
- 这条 alpha 的真实上限可能不是裸空 ETH，而是 **ETH-specific relative weakness**，所以 production 版很可能要落到 hedge 结构。

## 9) 来源
1. **Chi, Y., Chu, Q. (R.), & Hao, W. (2024/2025). _Return and Volatility Forecasting Using On-Chain Flows in Cryptocurrency Markets_. arXiv / econ.EM.**
   - Authors: Yeguang Chi; Qionghua (Ruihua) Chu; Wenyan Hao
   - Year: 2024 (v1), 2025 (v2)
   - Venue: arXiv working paper
   - DOI: `10.48550/arXiv.2411.06327`
   - Readable URL: `https://arxiv.org/abs/2411.06327`
   - PDF URL: `https://arxiv.org/pdf/2411.06327`
2. **本地全文抽取文件**
   - `/root/clawd/jerry/momentum/tmp/onchain_flows_2411.06327.pdf`
   - `/root/clawd/jerry/momentum/tmp/onchain_flows_2411.06327.txt`

## 10) 给当前 desk 的一句话结论
**这轮最值得先做的，不是把 on-chain flow 变成大而全特征库，而是先用最小工程量回答一个尖问题：`ETH exchange inflow spike` 能不能在 Binance `5m/15m` 执行里，留下 `4h~6h` 的 ETH short edge；如果能，再用 `USDT inflow` 去裁掉冲突样本。**
