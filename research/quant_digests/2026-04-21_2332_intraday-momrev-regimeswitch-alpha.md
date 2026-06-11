# 别把 Wen et al. (2022) 只读成“crypto 日内可预测性论文”：对 short-cycle crypto desk，更该先拆的是「recent-return continuation × jump/liquidity/event regime switch」这条 raw alpha

- 时间：2026-04-21 23:32 UTC
- 类型：2022 论文 audit（ScienceDirect 摘要/导言片段 + Crossref 元数据 + DuckDuckGo/EconPapers 摘要片段）
- 主题类型：raw alpha
- 基础 alpha：`最近一小段收益对下一小段收益有预测力；平稳时更像 continuation，但在大跳跃 / 事件 / 流动性扰动下容易切到 reversal`
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否（论文给的是可交易 predictability 证据，不是完整交易壳）
- 主题标签：raw-alpha / single-asset / intraday / momentum / reversal / regime-switch / jump / liquidity / event / bitcoin / eth / ltc / xrp / 1m / 3m / 5m / 15m
- 证据类型：论文证据（高频样本 + 条件分层）

## 1) 这次 intake 的核心（先回答 base alpha）

这篇东西最值钱的，不是“crypto 里既有动量也有反转”这句大白话，而是：

> **同一个 recent-return alpha，会随 market state 切换符号。**

也就是：平时你可以把“最近几根很强/很弱”先当成 **continuation 候选**；但一旦碰到 **大 intraday jump、FOMC、流动性恶化或异常事件窗口**，同一类 recent-return 信号就更该怀疑它会不会转成 **exhaustion fade / reversal**。

对我们 desk，这比再抄一个裸 momentum 公式更有用，因为它天然就是一条 **可拆成 raw alpha + regime router** 的短周期主线。

## 2) 核心结论

- 论文报告：**crypto 日内收益存在可预测性，而且不是单一方向，而是 momentum 与 reversal 都会出现。**
- 主样本使用 **Bitcoin 高频数据，覆盖 2013-03-03 到 2020-05-31**；摘要片段还指出，这种现象也能在 **Ethereum、Litecoin、Ripple** 等活跃币上看到。
- 这种 predictability **会随条件变化**：在 **large intraday price jumps、FOMC announcement、liquidity levels、COVID-19 outbreak** 下，模式会发生变化。
- 对短周期实战的真正启发不是“永远追”或“永远反着做”，而是：**先把 recent return 当 base alpha，再用事件/跳跃/流动性做方向路由。**

## 3) 为什么和当前项目有关

当前 `momentum` 已经积累了不少 breakout / trend / pairs / funding / relative-value 壳，但“**同一个短窗收益信号何时追、何时反着做**”这层还值得补。

这篇论文的价值在于它刚好补这个缺口：

- 它给的是 **短周期 raw alpha 母体**，不是纯解释型综述；
- 它天然可接我们现在的 **regime/filter/overlay** 框架；
- 它和现有 `1m/3m/5m/15m` 数据口径高度兼容，不需要先等另类数据权限。

一句话核心结论：**recent return 在 crypto 短周期里不是没用，而是会随 market state 从 continuation 切到 reversal。**

一句话证明方式：**作者用 Bitcoin 长样本高频数据做条件分层，比较不同 jump / event / liquidity 环境下的日内 predictability 模式。**

## 3.5) 策略拆解（必填）

- 方向属性：顺势 + 逆势（条件切换）
- 基础 alpha：`recent intraday return -> next-window return`
- regime：`normal / jump / event / low-liquidity`
- filter / veto：`大跳跃后禁追；FOMC 窗口禁裸 momentum；低流动期提高阈值`
- risk / sizing / execution overlay：`信号强度分档仓位 + event window size-down + time-stop + cost gate`

## 4) 可复刻的最小实验

先别追论文里的全部设定，直接做一个能在本周给 first verdict 的最小版：

- **研究假设**
  - 在 `BTC/ETH/SOL` 的 `5m` 数据上，最近 `3~6` 根 bar 的累计收益对下一段 `2~4` 根 bar 仍有预测力；
  - 但若当前 bar 属于 **异常 jump / FOMC 前后窗口 / 低流动分位**，则 continuation edge 会减弱，甚至翻成 reversal。
- **可计算定义**
  - `r_past = close_t / close_{t-k} - 1`
  - `jump_flag = |ret_1bar| > rolling_sigma * z`
  - `liq_flag = quote_volume` 或 `成交笔数/成交额` 落入低分位
  - router：
    - `normal regime`：顺 `sign(r_past)` 做 `2~4` bar continuation
    - `jump/event/low-liq regime`：反 `sign(r_past)` 做 `1~3` bar fade
- **最小回测切口**
  - 资产：`BTCUSDT / ETHUSDT / SOLUSDT` perpetual
  - 周期：先 `5m`，再映射到 `15m`；若有余力，再压到 `1m/3m`
  - 样本：近 `90~180d`
  - 成本：双边 fee + 2 档滑点假设
- **最该先看 2 个指标**
  - 成本后收益 / Sharpe（先看 alpha 有没有净边）
  - regime 分层后的 trade count 与 hit-rate（先看“追”和“反”是不是被 router 真正分开）

## 5) 风险与保留意见

- 这篇论文是 **predictability 研究**，不是已经给好 entry/exit/sizing 的实盘系统；要自己补完整交易壳。
- 目前拿到的是摘要/导言与元数据证据，不是全文逐段细读；因此这里更适合做 **first intake**，不宜过度细化到作者未明说的参数。
- 24/7 crypto 的 microstructure 与 2013~2020 早期样本差异很大，结论迁到今天时必须先过 **recent sample + cost** 检验。
- FOMC 这类宏观事件对 BTC 比对小币更强；alt 上可能更需要 `BTC lead / market-beta` 过滤。

## 6) 下一步怎么测

直接做一个 **mom-vs-fade regime router baseline**：

1. 在 `BTC/ETH/SOL 5m` 上先估 `r_past(15m/30m)` 对 `r_future(10m/20m)` 的分层条件期望；
2. 用 `jump_flag + low_liq_flag + macro_event_window` 把样本切成 `continuation` 与 `fade` 两组；
3. 对比三套壳：`always momentum` / `always reversal` / `state-routed hybrid`；
4. 只要 hybrid 在成本后明显优于前两者，就值得进下一轮 admission。

## 7) 来源（按可追溯口径）

1. **Wen, Z., Bouri, E., Xu, Y., & Zhao, Y. (2022). _Intraday return predictability in the cryptocurrency markets: Momentum, reversal, or both_. The North American Journal of Economics and Finance, 62.**
   - DOI: `10.1016/j.najef.2022.101733`
   - Readable URL: `https://www.sciencedirect.com/science/article/pii/S1062940822000833`
   - DOI URL: `https://doi.org/10.1016/j.najef.2022.101733`

2. **Wen, Z., Bouri, E., Xu, Y., & Zhao, Y. (2022). SSRN working-paper version.**
   - DOI: `10.2139/ssrn.4080253`
   - Readable URL: `https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4080253`

3. Metadata / abstract-supporting sources used in this intake:
   - Crossref: `https://api.crossref.org/works/10.1016/j.najef.2022.101733`
   - Search snippet / abstract mirror evidence: `https://econpapers.repec.org/RePEc:eee:ecofin:v:62:y:2022:i:c:s1062940822000833`
