# 别把这篇 2025 高频 pairs 论文只读成“crypto 也能做配对交易”：对 short-cycle crypto desk，更该先拆的是「fixed / dynamic threshold spread fade」这条 raw alpha

- 时间：2026-04-22 21:18 UTC
- 类型：2025 论文 abstract audit（Crossref/OpenAlex）+ Binance USDⓈ-M public-data portability probe（8 liquid majors，`15m/5m`）
- 主题类型：raw alpha
- 基础 alpha：**统计上更同步的一对币，短时 spread 偏离滚动均值足够远后，更容易回归；交易上对应 `short rich leg / long cheap leg` 的 pair-spread fade**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/fixed-threshold/dynamic-threshold/high-frequency/binance-perpetual/15m/5m/paper/public-data/cost/risk
- 证据类型：论文摘要证据 + public-data first probe

## 1) 这次看了什么

这轮看的是：

- **Authors**：Alireza Aghamohammadi, Hossein Dastkhan
- **Year**：2025
- **Title**：*Pair trading with high-frequency data in the cryptocurrency market*
- **Venue**：*China Finance Review International*
- **DOI**：`10.1108/CFRI-11-2024-0727`
- **Readable URL**：<https://www.emerald.com/insight/content/doi/10.1108/CFRI-11-2024-0727/full/html>

论文摘要里最有价值的不是“crypto market inefficient”这句大话，而是它把真正能落地测试的东西说得很清楚：

- 数据频率直接覆盖 `daily / 4h / 1h / 15m / 5m`
- 方法分成 `distance / cointegration / hybrid`
- 专门比较了 **fixed threshold vs dynamic threshold**
- 还做了 entry band、exit band、portfolio pair count 的敏感性分析

也就是说，它不是泛泛说“pairs 可以做”，而是在问：**同样是 spread fade，短周期里到底该用什么开仓阈值、平仓阈值、配对数和频率。**

## 2) 先回答一句：base alpha 是什么？

> **base alpha = high-frequency pair spread mean reversion。**

不是 regime，不是 filter，也不是 overlay。

更具体地说：
- 先找一对行为足够同步的币；
- 再盯它们的相对价差 / spread；
- 当 spread 偏离滚动中枢足够远时，做反向收敛；
- spread 回到中枢附近或时间走完就平。

所以这篇东西首先是 **pairs / relative-value raw alpha**。

## 3) 论文最值得记住的判断

根据摘要，作者给出的 headline 是：

- pair trading 在 crypto 各个时间框架都能做，但 **`15m / 5m` 这类高频窗口尤其活跃**；
- 在他们的样本里，**fixed threshold 的回报和 Sharpe 整体优于 dynamic threshold**；
- 他们不只测一种配对法，而是把 `distance / cointegration / hybrid` 三路都摆上台面。

**一句话核心结论：** 这篇论文真正值得 desk intake 的，不是“crypto 也能做 pairs”，而是“short-cycle pairs 的最小原型可以直接写成 `pair selection + spread z-score + threshold entry/exit`，并且 threshold 设计本身就是 alpha 厚度的一部分”。

**一句话证明方式：** 作者用 Binance top50 币，在 `2020 bull / 2021 stable / 2022 bear` 三段市场里，把多频率、多阈值、多方法做敏感性比较，结论来自实证回测对照，不是口头经验。

## 4) first probe：recent liquid-major transfer 仍有 gross edge，但 fixed vs dynamic 没完全照论文 headline 走

我先不做整篇论文复刻，而是做一个更贴当前 desk 的 portability probe：

- 标的：`BTC/ETH/SOL/XRP/DOGE/ADA/AVAX/LINK`
- 数据：Binance USDⓈ-M 公共 klines
- 频率：`15m` 与 `5m`
- pair selection：先在 formation half 按 **低 distance + 高 return corr** 选前 `6` 对
- trading rule：trade half 内对每对做 rolling-spread fade
  - `fixed`：`|z| >= 2` 开仓，回到 `|z| <= 0.25` 平仓
  - `dynamic`：开仓阈值改成过去 `96` 根 `|z|` 的 `90%` 分位
  - timeout：`15m=24 bars`，`5m=36 bars`

对应产物：
- `reports/artifacts/quant_digests/hf_pairs_fixed_vs_dynamic_probe_summary_2026-04-22.csv`
- `reports/artifacts/quant_digests/hf_pairs_fixed_vs_dynamic_probe_trades_2026-04-22.csv`
- `reports/artifacts/quant_digests/hf_pairs_fixed_vs_dynamic_probe_pairs_2026-04-22.csv`
- 脚本：`tmp/hf_pairs_fixed_vs_dynamic_probe.py`

最关键的数字：

- `15m fixed`：`65` 笔，平均 **`+8.81 bps/笔`**，胜率 **`61.5%`**，累计 gross **`+5.73%`**
- `15m dynamic`：`68` 笔，平均 **`+15.78 bps/笔`**，胜率 **`66.2%`**，累计 gross **`+10.73%`**
- `5m fixed`：`56` 笔，平均 **`+14.33 bps/笔`**，胜率 **`73.2%`**，累计 gross **`+8.02%`**
- `5m dynamic`：`52` 笔，平均 **`+9.34 bps/笔`**，胜率 **`71.2%`**，累计 gross **`+4.86%`**

如果先粗扣一个 pairs 常见的 **`8 bps round-trip`**：

- `15m fixed` 还剩约 **`+0.81 bps/笔`**
- `15m dynamic` 还剩约 **`+7.78 bps/笔`**
- `5m fixed` 还剩约 **`+6.33 bps/笔`**
- `5m dynamic` 还剩约 **`+1.34 bps/笔`**

这轮最有意思的点反而是：**recent liquid-major transfer 没有完全复现论文摘要里“fixed 明显优于 dynamic”的 headline。**

- 在我这版简化口径里，`15m` 是 **dynamic 更强**；
- 但 `5m` 又回到 **fixed 更强**。

人话版结论：**这条 raw alpha 不是纸上谈兵，recent Binance liquid majors 上也还能看到 gross spread-fade；但 threshold 选法明显是 regime-sensitive 的，不能直接把论文 headline 当成永恒真理。**

## 5) 哪些 pair 更像 pocket

本轮 pocket 主要集中在：

- `15m dynamic`：`BTC/SOL`、`DOGE/LINK`、`BTC/ETH`
- `15m fixed`：`XRP/DOGE`、`BTC/ETH`
- `5m fixed`：`AVAX/LINK`、`DOGE/ADA`
- `5m dynamic`：`AVAX/LINK`、`SOL/LINK`

说明这条线不是“所有 majors 等权平铺都一样厚”，而是更像 **selected-pair router**：
先挑 pocket，再决定 fixed 还是 dynamic gate。

## 6) 为什么和当前 desk 有关

这篇值得进池子，有三个原因：

1. **它是标准 raw alpha，不是附属 filter**：pair selection + spread threshold + mean-reversion exit，本身就是完整交易骨架。  
2. **它天然贴 `5m/15m`**：不是硬把日频论文往短周期上压。  
3. **它能和我们现有 stat-arb 素材池互补**：最近写过很多 `cointegration / PCA residual / copula`，这篇额外提醒的是——**threshold 机制本身可能比“你用哪种 fancy pair selector”更先决定能不能活。**

## 7) 策略拆解（必填）

- 方向属性：relative-value / stat-arb / mean reversion
- 基础 alpha：`pair spread overextension -> convergence fade`
- regime：更适合在 pair 同步性仍高、波动未完全失控的窗口
- filter / veto：pair corr / distance / rolling spread stability / volatility cap / funding shock veto
- risk / sizing / execution overlay：按 pair 半衰期或 spread 波动做 sizing；优先 maker-first；超时强平，避免“假同步 pair”拖成趋势单边亏损

## 8) 下一步怎么测（明确动作）

1. **把 pair admission 升级成真 cointegration / hybrid A/B**：当前 probe 只做了 `distance + corr` 的 desk-friendly 近似，还没把论文三路方法完整拆开。  
2. **把 threshold 做成 grid**：`entry z = 1.5 / 2.0 / 2.5`，`exit z = 0 / 0.25 / 0.5`，看 edge 是来自更宽 entry，还是更快回中 exit。  
3. **单独做 pocket 跟踪**：优先盯 `BTC/ETH`、`AVAX/LINK`、`DOGE/LINK` 这些本轮更厚的 pair，不要一上来全池平铺。  
4. **补 funding / event veto**：如果 spread 扩张同时伴随 funding 或 news-driven 单边趋势，很多“回归”会被拖死，这类窗口该先禁做。  
5. **把 `15m parent` 接 `5m/3m child execution`**：父信号只负责告诉你哪对 pair 开始失衡，真正的入场尽量交给更细粒度 maker-first。  

## 9) 风险与保留意见

- 本轮拿到的是摘要级论文信息，不是全文复刻，**论文证据强度低于 full-text audit**；
- 我的 probe 只是一版 portability check，不等于完整复现作者的 `distance / cointegration / hybrid` 框架；
- gross 边虽然在，但 pair 交易最怕的是**同步关系失效**与**单边趋势把“价差”拖成新常态**；
- 若按更保守的四腿 taker 成本、借贷/资金占用、滑点冲击去扣，很多 pocket 会变薄。

## 10) 结论一句话

**这篇 2025 高频 pairs 论文最值得 desk intake 的，不是“crypto pairs 也能赚钱”这句废话，而是把 short-cycle stat-arb 清楚压缩成了一个能立刻测试的 raw alpha：`selected pair + spread z-score + threshold fade`；而我这轮 recent Binance probe 说明，这条线当前仍有 gross edge，但 `fixed` 还是 `dynamic` 更好，得按周期和 pair pocket 分开测，不能照搬 headline。**
