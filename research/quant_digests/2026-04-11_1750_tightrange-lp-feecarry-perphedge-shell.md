# 别把这篇 LP 论文只读成 IL 对冲：对 short-cycle desk，更该先测的是「tight-range LP fee carry × perp short hedge × band-recenter shell」

- 时间：2026-04-11 17:50 UTC
- 类型：2024 *Ledger* 论文页 + 开源 repo 交叉 + Uniswap / Binance 公共数据快检
- 主题类型：raw alpha
- 基础 alpha：**在高成交的稳定币交易对上做 tight-range concentrated liquidity，赚 swap fee；同时在 CEX 做对应数量的 perp short 把方向风险压平，价格出带后再做 band recenter / hedge refresh。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（**paper 偏原理，repo 已给出工程壳；真正难点在 gas / hedge turnover / 执行摩擦，不在“有没有信号”**）
- 主题标签：raw-alpha / carry / relative-value / liquidity-provision / concentrated-liquidity / impermanent-loss / delta-neutral / perp-hedge / rebalance / uniswap-v3 / binance / eth / usdc / 5m / 15m / repo / paper / cost / risk
- 证据类型：论文摘要页与参考链路 + 开源实现骨架 + 公共数据 feasibility probe

## 1. 这次看了什么
主材料是：

- **Basile Maire; Marcus Wunsch (2024)**
- **Title:** *Market Neutral Liquidity Provision*
- **Venue:** *Ledger*, Vol. 9
- **DOI:** `10.5195/ledger.2024.389`
- **Readable URL:** <https://ledger.pitt.edu/ojs/ledger/article/view/389>
- **DOI URL:** <https://doi.org/10.5195/ledger.2024.389>
- **Repo / implementation references actually used this round:**
  - DeFiNER: <https://github.com/jiaxiang-cheng/Hedging-Impermanent-Loss-in-Uniswap-V3>
  - hedged-lp-bot: <https://github.com/dkrizhanovskyi/hedged-lp-bot>
  - uniswap-delta-neutral-hedge-hft: <https://github.com/adradr/uniswap-delta-neutral-hedge-hft>

这篇 paper 表面上在讲的是：

> **如何把 Uniswap 集中流动性仓位，用 futures / options hedge 成 market-neutral。**

但对当前 short-cycle desk，更值钱的翻译不是“IL 数学很复杂”，而是：

> **这其实是一条完整的 carry / liquidity-provision raw alpha 壳：核心收入来自 LP fee，方向风险靠 perp short 对冲，`5m / 15m` 的角色不是预测涨跌，而是决定什么时候 recenter、什么时候 refresh hedge、什么时候干脆别做。**

一句话核心结论：

> **这篇东西最该带回来的，不是“IL 可以被优雅对冲”，而是「tight-range LP fee carry × CEX perp hedge」这条可独立复现的完整 raw alpha；当前 first verdict 不是 edge 不存在，而是 tight band 下 hedge / gas 周转太快，band 设计与摩擦控制决定生死。**

一句话证明方式：

> **我先读 paper article page 把 base alpha 与 hedge 结构钉死，再用 WETH/USDC 0.05% Uniswap 池的公开流动性 / 成交量快照，加上 Binance `ETHUSDT 5m + fundingRate`，检查 fee 池子够不够厚、hedge refresh 会不会太频繁、short hedge 当前是补贴还是拖累。**

## 2. 先回答最重要的一句：base alpha 到底是什么
这轮 base alpha 是清楚的，不该降级成 filter：

> **delta-neutral liquidity-provision fee carry**。

翻成人话：

- 你不是赌 ETH 一定涨或一定跌；
- 你是在一个高成交、高流动性的稳定币池里提供流动性，吃别人交易付的 fee；
- 同时你在 Binance 之类的 CEX 上做 token leg 的 short hedge，把方向风险尽量压平；
- 若价格离开带宽，就平旧带、重开新带、同步刷新 hedge。

所以它本质上更像：

- `carry / fee harvest`
- `relative-value / market-neutral`
- `execution-heavy raw alpha`

而不是：

- 纯 filter
- 纯 regime
- 纯“风险管理附件”

如果一定要给它找 desk 里的同类，它更接近：

> **“basis/funding/carry” 家族在 DEX 上的流动性提供版本。**

## 3. 原论文里，真正能拿走的不是学术词，而是一条完整策略骨架
paper 摘要页直接点了两件最关键的事：

1. **目标不是再讨论 IL 指标，而是构造 market-neutral LP strategy；**
2. **hedge 组合可以由 futures + options 构成，而且 futures contango 往往还能额外贡献 carry。**

对当前 desk，最实用的读法不是直接上最复杂的 delta-gamma hedge，而是分两层：

### 3.1 第一落点：先做最朴素的 perp-short delta hedge
- DEX 端：Uniswap v3 `WETH/USDC` tight-range LP
- CEX 端：Binance `ETHUSDT` perp short
- 目标：先把**方向 beta**压掉，保留 fee income

### 3.2 第二落点：再补 gamma / convexity 修正
- 若 tight range 太窄、仓位 gamma 太大，单靠 delta hedge 会很快失真；
- 这时再考虑更复杂的期权 / power-perp / dynamic hedge。

这也是为什么这轮值得 intake：

> **它不是“纯理论 paper 很漂亮”，而是能被拆成一个先简后难的完整实验序列。**

## 4. 本地 quick probe：池子够不够厚，hedge 会不会太忙
本轮 artifacts：

- `/root/clawd/jerry/momentum/reports/artifacts/literature/uniswapv3_hedged_lp_probe_summary_2026-04-11.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/uniswapv3_hedged_lp_probe_band_resets_2026-04-11.csv`

### 4.1 数据口径
- **DEX 池子：** Uniswap v3 `WETH / USDC 0.05%`
  - pool address: `0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640`
  - source: GeckoTerminal public API
- **CEX hedge：** Binance `ETHUSDT` perp
  - `5m` K 线：最近 `1500` 根
  - funding：最近 `200` 个 `8h` 结算点

### 4.2 这轮最值得记住的 4 个数
1. **WETH/USDC 0.05% 池当前 reserve 约 `100.3M USD`，24h volume 约 `28.5M USD`。**
2. **按当前池子快照算的“naive full-TVL fee / day”只有约 `1.42 bps/day`。**
   - 翻成人话：底池很深、成交也不低，但如果你只是普通全范围 LP，fee 厚度其实没夸张到能无视成本。
3. **用 Binance `ETHUSDT 5m` 做静态 band reset 快检：**
   - `±1%` 带宽：约 **`4.85` 次 / 天** reset，median hold 约 **`3h`**；
   - `±2%` 带宽：约 **`1.97` 次 / 天** reset，median hold 约 **`12.0h`**。
4. **Binance `ETHUSDT` 最近 `200` 个 funding 点均值约 `-0.164 bps / 8h`，正 funding 占比约 `43%`。**
   - 对 short hedge 来说，这表示**最近样本里平均是“收 funding”，不是付 funding**。

### 4.3 结果怎么翻成人话
这组数最有价值的地方，不是告诉你“马上能赚多少”，而是把这条策略的矛盾点钉死：

- **池子是够深的；**
- **short hedge 最近甚至还能拿一点 funding 补贴；**
- **但 tight band 一旦太窄，recenter / hedge refresh 会变得非常忙。**

所以这条策略不是“没有 alpha”，而是：

> **alpha 在 fee carry 这一侧；死法在 gas、band 太窄、以及 CEX hedge turnover 太高。**

## 5. 为什么这轮值得做它，而不是继续补普通方向型 alpha
因为它补的是当前素材池里相对稀缺、但对实盘很有价值的一类：

1. **它是 raw alpha，不是解释性 overlay。**
   收益来源清楚：LP fee + 可能的 funding / contango 补贴。
2. **它能扩充我们对“carry”家族的理解。**
   以前更偏 `basis / funding / spot-perp`；这轮补的是 **DEX fee carry + CEX hedge**。
3. **它天然带完整策略壳。**
   - entry：何时 mint
   - exit：何时 burn / recenter
   - sizing：投多少 TVL、对多少 notional hedge
   - risk：band width、inventory drift、gas budget
   - cost：DEX gas + CEX fee + funding
4. **它和 `5m / 15m` 有明确映射。**
   不是拿低频宏观变量硬装成短周期信号，而是把 `5m/15m` 当作：
   - band breach 检查频率
   - hedge refresh 频率
   - liquidity / funding admission 刷新频率

## 6. 对当前 desk，最合理的策略拆解是什么
## 6.1 策略拆解（必填）
- 方向属性：market-neutral / carry / liquidity-provision / relative-value
- 基础 alpha：`tight-range LP fee carry with perp short hedge`
- regime：
  - 高成交、低 gas 干扰、池子深、funding 不逆风时更适合；
  - 大趋势单边 / 高频穿带环境更差。
- filter / veto：
  - `24h volume / reserve` 不够厚时不做；
  - funding 大幅转正且你是 short hedge 付费时降权；
  - 预估 reset frequency 太高时直接 veto。
- risk / sizing / execution overlay：
  - band width（`1% / 1.5% / 2%`）
  - hedge threshold / refresh cadence
  - gas cap / max resets per day
  - 单池 TVL cap / inventory drift cap

### 6.2 对 short-cycle desk 的正确落点
最合理的落点不是“把它硬说成 5m directional alpha”，而是：

> **把它当作一个用 `5m / 15m` 驱动的 fee-carry engine。**

也就是：
- `5m`：适合更敏感的 band breach / hedge drift 监控；
- `15m`：适合更稳的 recenter 决策；
- 真正的收益结算周期往往是 **多小时到多天**，不是“一根 K 线就见分晓”。

## 7. first verdict（当前）
这轮 first verdict 可以很明确：

> **这条 raw alpha 值得进池，但默认不能用“超窄带 + 高频重平衡”的想象去做。**

更具体地说：

- **有 alpha：** fee carry + 可能的 short-funding 补贴 本身是成立的；
- **有工程壳：** paper 给原理，repo 给执行骨架；
- **有现实约束：** 当前样本显示 `±1%` 带宽下 reset 约 `4.85/day`，这对 gas 和对冲成本太敏感；
- **更像 first lane 的形态：**
  - 先从 `±2%` 左右的更宽带做起；
  - 先用 perp-only delta hedge；
  - gamma hedge / options 以后再补。

对 desk 来说，最值钱的结论不是“paper 证明了 hedge 可行”，而是：

> **如果你想把它搬到实盘，第一件事不是优化预测器，而是先把 `fee density vs reset frequency vs hedge cost` 三角关系测清楚。**

## 8. 风险与保留意见
- **paper 的完整 hedge 组合并不便宜。** 摘要页已经点出：需要显著资本占用，不能把它想成零成本套壳。
- **本轮只做了 quick probe，不是完整 backtest。** 当前数值更像 feasibility check，不是 net PnL 结论。
- **GeckoTerminal 的 24h volume / reserve 只是单时点快照。** 真正实盘要看多日滚动分布，而不是只看一帧。
- **gas / MEV / 滑点可能比 CEX fee 更致命。** 这条路在链上最容易被低估的不是信号，而是交易摩擦。
- **perp short 只是先把 delta 压掉，不代表 gamma / convexity 问题自动消失。** tight band 越窄，这个问题越严重。

## 9. 下一步怎么测
1. **先做 band 宽度阶梯，而不是先追最窄带。**
   - 直接测 `±1% / ±1.5% / ±2% / ±3%` 四档：
   - 指标只看 5 个：`fee_bps/day`、`reset/day`、`hedge_turnover`、`funding_pnl`、`net_after_gas`。
2. **先做 perp-only delta hedge 的最小版。**
   - 先别一上来就加 options / squeeth；
   - 先证明“简单版能不能站住”。
3. **用 `5m` 监控、`15m` 决策。**
   - `5m` 看是否穿带、delta 是否漂太远；
   - `15m` 再决定是否真的 burn / remint，避免过度反应。
4. **把 funding 从“附带收益”单独拆账。**
   - fee income、perp hedge PnL、funding PnL、gas separately account；
   - 否则最后不知道真正赚钱的是哪一腿。
5. **先只做 `WETH/USDC 0.05%` 与 `ETHUSDT`。**
   - 不要一开始就扩多池、多链、多 venue。
6. **明确录取线。**
   - 若 `±2%` 仍然 reset 过快、net after gas 不稳定，就先别把它升成主策略，只保留为 carry / execution research lane。

## 10. 来源
1. **Maire, B., & Wunsch, M. (2024). _Market Neutral Liquidity Provision_. Ledger, 9.**
   - DOI: <https://doi.org/10.5195/ledger.2024.389>
   - Readable URL: <https://ledger.pitt.edu/ojs/ledger/article/view/389>
2. **Paper page references explicitly cited on article page**
   - Uniswap v3 whitepaper: <https://uniswap.org/whitepaper-v3.pdf>
   - BIS `Crypto Carry`: <https://www.bis.org/publ/work1087.pdf>
3. **Implementation references used this round**
   - DeFiNER: <https://github.com/jiaxiang-cheng/Hedging-Impermanent-Loss-in-Uniswap-V3>
   - hedged-lp-bot: <https://github.com/dkrizhanovskyi/hedged-lp-bot>
   - uniswap-delta-neutral-hedge-hft: <https://github.com/adradr/uniswap-delta-neutral-hedge-hft>
4. **Public data actually used in this round**
   - GeckoTerminal pool snapshot API (`WETH/USDC 0.05%`)
   - Binance Futures public `fapi/v1/klines`
   - Binance Futures public `fapi/v1/fundingRate`

## 11. 数据源 / 公开性 / 更新频率 / 最小复现实验口径
- **数据源：**
  - Uniswap pool snapshot / OHLC / tx stats（可用 GeckoTerminal / Dune / subgraph）
  - Binance `ETHUSDT` perp K 线与 funding
- **公开性：** 公开可得，无需付费数据即可做 first verdict
- **更新频率：**
  - DEX 池统计可做分钟级 / 小时级刷新
  - Binance 可直接做 `5m / 15m`
- **最小可复现实验口径：**
  - pool：`WETH/USDC 0.05%`
  - hedge：`ETHUSDT` perp short
  - bands：`±1% / ±1.5% / ±2% / ±3%`
  - monitor cadence：`5m`
  - decision cadence：`15m`
  - cost ladder：至少 `gas low/base/high` + `CEX fee maker/taker` + `funding`
  - verdict：先回答它是“可升级的 fee-carry alpha”还是“只在极低摩擦下才成立的研究型壳”
