# 别把 BTC 大阴大阳后的反手只当老派均值回归：这篇 2021 论文更值得 desk 先测的是「极端 bar 反打」raw alpha

- 主题类型：raw alpha
- 基础 alpha：**做反向**——上一根 BTC bar 若出现足够大的单根涨跌（尤其是 `5m` 的极端尾部、或 `4h` 的大级别冲击），下一根按相反方向开仓，持有 1 根同周期 bar 后平仓。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1. 为什么这轮值得写
这不是“又一篇泛泛的反转论文”。它的 base alpha 很清楚：**极端单根收益后的下一根反向 markout**。而且它不是只给相关性，还给了可直接交易的最小骨架：`event definition -> next-bar entry -> one-bar exit -> threshold sweep -> fee sanity check`。

对当前 short-cycle desk 的价值在于两点：
1. 它给了一个非常干净的 **time-series raw alpha baseline**，不是 filter 也不是解释型综述；
2. 它天然贴着 crypto 的 liquidation / overreaction 机制，后面无论接 `liquidation map`、`OI/funding crowding`、还是 `maker/taker execution veto`，都很好拆组件。

更关键的是：这条线不必被误读成“全天候 15m fade”。我这轮最小 transfer check 的结论更像是：**常态 15m 不诚实，真正有味道的是 `5m` 极端尾部反打，以及更稀疏但更干净的 `4h` 冲击后回摆。**

## 2. 论文在讲什么
### Source
- **Authors**: Giacomo De Nicola
- **Year**: 2021
- **Title**: *On the Intraday Behavior of Bitcoin*
- **Venue**: *Ledger*, Vol. 6, pp. 58–80
- **DOI**: `10.5195/LEDGER.2021.213`
- **Readable URL**: <https://doi.org/10.5195/LEDGER.2021.213>
- **PDF URL**: <https://ledger.pitt.edu/ojs/ledger/article/download/213/212>
- **Repo URL**: 未见官方 repo

### 原论文数据与方法
- **数据源**：Bitstamp BTC/USD 1 分钟数据（Kaggle 镜像，由 Mark Zielinski 上传）
- **样本期**：`2015-03-01` ~ `2018-06-27`
- **更新频率**：1 分钟，再聚合到 `5m / 15m / 30m / 1h / 2h / 4h / 1d`
- **最小策略**：
  - 若上一根 return 为大阳线，则下一根做空；
  - 若上一根 return 为大阴线，则下一根做多；
  - 持有 1 根同周期 bar；
  - 只在 `|r_{t-1}| >= k·σ` 时触发，`k` 从 `0σ` 到 `6σ` 扫。

## 3. 论文里最该记住的数字
### 3.1 先看一阶自相关：中等周期居然还是负的
论文 Table 3 给出的 BTC 一阶收益自相关：
- `5m`: **-0.1016**
- `15m`: **-0.0575**
- `1h`: **-0.0557**
- `2h`: **-0.0858**
- `4h`: **-0.0564**

这点很关键：对传统市场来说，分钟级负自相关常常能被 bid-ask bounce 解释掉；但到了 `1h / 2h / 4h` 还显著为负，就更像 **overreaction + liquidation cascade 后的回摆**，而不是纯微观结构噪音。

### 3.2 越极端的 bar，反打越强
论文 Table 4 显示：阈值越高，下一根反向相关越强。几个最有代表性的点：
- `5m`：从 `0σ` 的 **-0.1027**，一路加深到 `6σ` 的 **-0.2186**
- `1h`：从 `0σ` 的 **-0.0557**，到 `5σ` 的 **-0.1863**
- `2h`：从 `0σ` 的 **-0.0858**，到 `6σ` 的 **-0.4010**

翻成人话：**不是所有下跌/上涨都值得反打；真正有 edge 的，是“冲过头”的那种 bar。**

### 3.3 论文里的最小策略，per-trade 毛收益并不小
论文 Table 5（未计手续费）的 mean per-trade profit：
- `5m, 6σ`: **0.30% / trade**
- `15m, 6σ`: **0.28% / trade**
- `1h, 6σ`: **0.58% / trade**
- `2h, 6σ`: **1.81% / trade**

作者的结论很直接：**高阈值、大时间框架的 shock-reversal，不像纯学术相关性，更像可交易 inefficiency。**

## 4. 我做的当前 transfer check：2024-01 至 2026-03 的 Binance BTCUSDT perp
### 数据口径
- **数据源**：Binance Futures 公共 K 线 API
- **标的**：`BTCUSDT perpetual`
- **样本期**：`2024-01-01 00:00 UTC` ~ `2026-03-26 14:00 UTC`
- **公开性**：完全公开可拉
- **更新频率**：`5m / 15m / 4h`
- **实验口径**：
  - 先算 rolling 30-day sigma；
  - 若上一根 bar 的 `|ret| >= k·rolling_sigma`，则下一根做反向；
  - 持有 1 根同周期 bar；
  - 成本只做简单 round-trip sanity check：`2 / 4 / 10 bps`。
- **artifact**：`reports/artifacts/quant_digests/btc_intraday_jump_reversal_transfer_20260326_1407/key_transfer_rows.csv`

### 4.1 结论先说
**这条 alpha 没死，但已经明显从“广谱反转”收缩成“只在尾部 event 里还值得动手”。**

### 4.2 当前最值得 desk 注意的三个数字
1. **`5m, 6σ` 极端 bar 反打**：
   - `n_trades = 403`
   - 毛收益 **`4.59 bps/trade`**
   - `4 bps` round-trip 下仍有 **`+0.59 bps/trade`**
   - 累计加总收益约 **`+0.024`**

2. **`5m, 5σ` 还不够**：
   - `n_trades = 727`
   - 毛收益 **`2.05 bps/trade`**
   - `4 bps` round-trip 后变成 **`-1.95 bps/trade`**

3. **`4h, 3σ` 稀疏但干净**：
   - `n_trades = 89`
   - 毛收益 **`10.08 bps/trade`**
   - `4 bps` round-trip 后仍有 **`+6.08 bps/trade`**
   - `10 bps` round-trip 下也几乎打平（**`+0.08 bps/trade`**）

### 4.3 哪些口径是负的
- `15m` 的 `1σ / 2σ / 3σ` 当前都不诚实：毛收益已接近 0 或直接转负，成本后更差。
- 这意味着：**别把这条线硬伪装成“15m always-on 主信号”。**

## 5. desk 化解读：它现在到底应该被当成什么
### 最诚实的定位
这条线现在更像两档东西：

#### A. `5m` 高频尾部 event alpha
- 只做 **极端 bar**，例如 `5m >= 6σ`
- 逻辑：单根冲击太猛，下一根出现短促回摆
- 优点：更贴近 short-cycle desk
- 缺点：edge 薄，**极依赖费率、滑点和触发稀缺性**

#### B. `4h` 中等频率 shock-reversal sleeve
- 逻辑：大级别 liquidations / overreaction 后，下一根回摆更稳定
- 优点：当前转移样本里更干净
- 缺点：交易稀疏，不是“高强度流水线 alpha”

换句话说，**paper headline 是“中等周期均值回归存在”，但对我们 desk 更值钱的落点其实是：`5m` 只做最尾部、`15m` 不要装、`4h` 可以保留成稀疏 event sleeve。**

## 6. 一个可直接落地的最小策略骨架
### 6.1 Entry
- 计算 `ret_{t-1}` 与 rolling `30d sigma`
- 若 `ret_{t-1} <= -k·σ`：下一根 bar close 做多
- 若 `ret_{t-1} >= +k·σ`：下一根 bar close 做空

### 6.2 Exit
- 固定持有 **1 根同周期 bar** 后平仓
- 不先加 trailing；先把“edge 是否真的只活 1 根”这件事看清楚

### 6.3 Sizing
- 默认 `vol-targeted`：`target_risk / realized_vol`
- 单次事件仓位 capped，避免在极端波动时被“看起来更强的 signal”反而放大爆仓风险

### 6.4 Risk / Cost
- `5m` 版本必须写死：
  - fee bucket（maker / taker 分开）
  - max spread
  - max slippage
  - consecutive event cooldown
- `4h` 版本必须补：
  - 周期内 funding carry
  - 大事件时段（CPI/FOMC）是否 veto

## 7. 下一步怎么测
### P0：先把它测成一个诚实的 event family，而不是一句“BTC 会反转”
1. **`5m` 阈值细扫**：测 `5σ / 5.5σ / 6σ / 6.5σ`，看 break-even fee 到底落在哪。
2. **entry timing**：比较 `next-close entry` vs `next-open entry` vs `next-30s VWAP`，别把论文的 bar-close 假设直接当可成交价。
3. **持有期**：固定比较 `1 bar / 2 bar / half-bar time stop`，验证 edge 是否只活在第一根。
4. **事件分层**：把触发事件按 `liquidation burst / funding extreme / OI expansion / session bucket` 分层，回答：
   - 哪类极端 bar 真的会回摆？
   - 哪类极端 bar 其实应该继续顺势？

### P1：别单独裸跑，尽快接 crypto 特有 veto / confirm
优先接三类公开可得数据：
- **liquidation heat / liquidation prints**：判断这根 bar 是“被强平打穿”还是“真信息驱动”
- **OI + funding**：区分拥挤挤仓式 spike vs 正常趋势延续
- **盘口厚度 / spread**：决定 5m 尾部反打是否还能吃到那 0~5bps 的薄 edge

### P2：扩成一个更像实盘的 raw alpha 组件
最值得继续的组合不是“把所有 bar 都反着做”，而是：
- `base alpha`: extreme-bar reversal
- `regime`: high leverage / crowding / cascade regime
- `execution`: maker-first or tight-spread-only
- `risk`: cool-down + stop-trading after repeated same-side bursts

## 8. 我对这条线的当前 verdict
**值得进入研究池，而且应该按 raw alpha 记账；但当前最诚实的版本不是 15m 全天候，而是 `5m` 尾部 event alpha + `4h` 稀疏冲击回摆 sleeve。**

如果只问一句“这篇东西今天对 desk 最有用的 base alpha 是什么？”——答案就是：

> **上一根 BTC bar 如果大到离谱，就反着做下一根；但只在真正的尾部事件上动手。**

这句话够简单，也够能复现。
