# 别把 Tadi & Kortchemski (2021) 只读成“又一个配对交易论文”：对 short-cycle crypto desk，更该先拆的是「dynamic cointegration admission × half-life-aware spread fade」这条 raw alpha 壳
- 时间：2026-04-21 22:32 UTC
- 类型：论文（arXiv / journal metadata）+ Binance USDⓈ-M public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：先用动态 cointegration / hedge ratio 找到相对稳定的两腿价差，再在 spread z-score 明显偏离时做均值回归；half-life 不直接产生方向，但决定更合适的 formation 窗口、持有时长和 admission
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：pairs / stat-arb / relative-value / cointegration / half-life / mean-reversion / admission / 5m / 15m / Binance USDⓈ-M
- 证据类型：论文证据（摘要+元数据）+ public-data first probe

## 1. 这次看了什么
这次看的是 **Masood Tadi, Irina Kortchemski (2021), _Evaluation of dynamic cointegration-based pairs trading strategy in the cryptocurrency market_**。这篇东西最值钱的，不是“cointegration 这三个字”，而是它把 **pair alpha 的 admission layer** 讲得更像完整策略：pair 不是一次性挑完就不动，而是随窗口重估；而 OU half-life 不是装饰指标，而是拿来约束 formation / holding horizon 的。

## 2. 核心结论
- **一句话核心结论**：这篇东西真正可迁移到我们 desk 的，不是“配对本身”，而是 **用 half-life 把 pair admission、lookback、timeout 连成一条因果链**。
- **一句话证明方式**：作者用 minute-binned crypto 数据，结合 cointegration 检验、OU half-life 和更接近盘口可成交的执行假设，比较不同设定下的收益与回撤，而不是只做静态 z-score 教科书回测。
- 从 abstract 看，论文强调三件事：动态 cointegration、half-life 选窗、以及考虑 best bid/ask 与 signal-to-fill gap 的更现实执行；这比很多只写 `|z|>2` 的 pairs 模板更接近 desk 可复现对象。
- 我用 Binance USDⓈ-M `8` 个 liquid majors 做轻量 portability probe，拿 top-corr pairs 比较 **固定 `96` bars** vs **从 `48/72/96/144` 中按 half-life 选更匹配窗口**：
  - `15m`：固定窗 gross 约 `-0.75 bps/笔`，动态窗转成 `+0.19 bps/笔`，但仍远低于四腿 taker 成本
  - `5m`：固定窗 gross 约 `+3.66 bps/笔`，动态窗约 `+3.64 bps/笔`，有 gross edge，但仍不够覆盖保守成本
  - 动态窗下较厚的 pocket 出现在 `DOGE/ADA`、`ADA/LINK` 这类 alt-alt pair，而不是传统大币 pair
- 所以更像真的 desk 结论是：**half-life-aware admission 有帮助，但帮助主要体现在“少做不该做的 pair / 用更合适的 timeout”，还不够把短周期 pair MR 直接推成 standalone taker alpha。**

## 3. 为什么和当前项目有关
这篇和当前 `momentum` 主线直接相关，因为它补的是我们最近在 raw alpha 池里还缺的一块：**不是再找一个新的 pair entry 公式，而是把 relative-value MR 的 admission / holding 规则变得更因果、更可迁移。** 这能直接服务后续 pairs、basket residual、PCA residual、basis spread 这几条线。

## 3.5 策略拆解（必填）
- 方向属性：pairs / stat-arb / relative-value / mean reversion
- 基础 alpha：spread 偏离后的中枢回归
- regime：只在 cointegration / half-life 落在可交易区间时开机
- filter / veto：`|z|` 入场阈值、half-life 过长或过短 veto、pair admission 动态重估
- risk / sizing / execution overlay：beta 对冲、half-life-aware timeout、四腿成本门槛、maker-first 或至少 delayed-fill realism

## 4. 可复刻的最小实验
- **研究假设**：对 short-cycle crypto，pairs alpha 的主要增益不在“更复杂入场”，而在 **dynamic admission + half-life-aware timeout**。
- **可计算定义**：rolling OLS hedge ratio；formation 窗口在 `48/72/96/144` bars 中选与估计 half-life 更匹配的一档；`|z|>=2` 入场，`|z|<=0.5` 或 `2×half-life` timeout 出场。
- **最小回测切口**：Binance USDⓈ-M `BTC/ETH/BNB/SOL/XRP/DOGE/ADA/LINK`，先跑 `15m/5m`，按 top-corr pairs 做 first verdict。
- **先看指标**：`gross/net bps per trade`、`timeout rate`；若 gross 连 `8~12 bps` round-trip 都够不到，就别急着往 live 推。

## 5. 风险与保留意见
这轮 paper 侧我拿到的是摘要与元数据，不是全文逐表复核，所以不应把论文中的全部绩效数字当成已验证事实。另一个更关键的问题是：**short-cycle perp 的四腿摩擦太重**。即使 dynamic admission 把 `15m` 从负的 fixed baseline 拉到微正 gross，当前也更像“pair selection / timeout module”，而不是可直接独立上线的主 alpha。

## 6. 来源
- Tadi, M., & Kortchemski, I. (2021). *Evaluation of dynamic cointegration-based pairs trading strategy in the cryptocurrency market*. *Studies in Economics and Finance*.
- DOI: `10.1108/SEF-12-2020-0497`
- Readable URL: `https://arxiv.org/abs/2109.10662`
- Journal URL: `https://doi.org/10.1108/SEF-12-2020-0497`
- 本地 artifacts：
  - `reports/artifacts/quant_digests/dynamic_cointegration_halflife_summary_2026-04-21.csv`
  - `reports/artifacts/quant_digests/dynamic_cointegration_halflife_pairs_2026-04-21.csv`
  - `reports/artifacts/quant_digests/dynamic_cointegration_halflife_trades_2026-04-21.csv`
