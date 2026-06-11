# 别把这篇论文只读成“pairs 老策略复读”：对 short-cycle crypto desk，更该先测「5m intraday mean reversion 是否真能跑赢日频」
- 时间：2026-04-23 22:10 UTC
- 类型：论文
- 主题类型：raw alpha
- 基础 alpha：pairs / stat-arb（distance + cointegration 的价差均值回归）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / mean-reversion / pairs / stat-arb / distance / cointegration / crypto / binance / 5m / 1h / daily / transaction-cost
- 证据类型：论文证据（OpenAlex 可重建摘要 + Crossref 元数据 + IEEE OA 元数据）

## 1. 这次看了什么
这次选的是 **Fil & Krištoufek (2020)**，论文 *Pairs Trading in Cryptocurrency Markets*（IEEE Access, DOI: `10.1109/ACCESS.2020.3024619`）。

它不是泛泛讲相关性，而是直接把 `distance` 与 `cointegration` 两类经典 pairs 方法，放到 **Binance 上 26 个高流动币**，比较 `5-minute / 1-hour / daily` 三个频率的结果。

## 2. 核心结论
- 一句话核心结论：**同样是 pairs，日频可能没 edge，但 5m 频率的 intraday 均值回归可能显著更强。**
- 一句话证明方式：作者在 26 个币、三种频率、两类方法上做回测，并明确比较基准与参数/成本敏感性。
- 摘要里的关键数字：
  - `daily` 的常见 distance 方法约 `-0.07%` 月收益；
  - 提升到 `5m` 后约 `+11.61%` 月收益；
  - 结论同时强调：结果对 **参数设定、交易成本、执行窗口** 很敏感。
- 读法重点：这篇不是在说“pairs 永远有效”，而是在说 **crypto 的可交易均值回归更可能在 intraday 出现，而不是在日频自动出现**。

## 3. 为什么和当前项目有关
这和你当前“补 raw alpha 素材池”的目标高度一致：
- 方向上补齐了 `mean reversion / stat-arb / pairs`，不是继续堆 trend/breakout；
- 频率上直接命中 `5m`（以及可下探 `1m/3m`）；
- 结构上可以自然拆成完整策略：`pair selection -> spread zscore entry/exit -> sizing -> cost/veto`。

## 3.5 策略拆解（必填）
- 方向属性：市场中性（long undervalued leg / short overvalued leg）
- 基础 alpha：配对价差的短周期均值回归
- regime：高噪声、低单边趋势窗口更友好；强单边趋势期容易持续偏离
- filter / veto：
  - cointegration p-value / rolling stability 不达标 veto；
  - 预计成本覆盖不足 veto；
  - 极端波动或流动性骤降 veto
- risk / sizing / execution overlay：
  - 组合波动目标化（vol-target）；
  - 单对仓位上限 + 组合净敞口约束；
  - 触发后分批成交，避免一次性冲击

## 4. 可复刻的最小实验
- 研究假设：`5m` 的 pairs spread（distance/cointegration）在币圈比 `1h` 和 `daily` 更容易产生成本后正期望。
- 一个可计算定义：
  1) 在 `BTC/ETH/BNB/SOL/XRP/ADA/DOGE/LTC` 中滚动选 top-k 高相关且协整稳定的候选对；
  2) 定义 spread：`s_t = log(P_A) - beta_t * log(P_B)`；
  3) zscore 入场：`z > +2` 做 `short spread`，`z < -2` 做 `long spread`；
  4) 出场：`|z| < 0.5` 或 `time stop`；
  5) 成本：双边 taker/maker 场景都测一遍。
- 最小回测切口：先做 `5m`（主）、`15m`（对照），样本 `最近 180d~360d`。
- 最该先看哪 1~2 个指标：
  - `成本后 avg bps/trade`
  - `5m 相对 1h/daily 的 uplift`
  若 5m uplift 不稳定或全靠少数 pair，先别扩规模。

## 5. 风险与保留意见
- 论文虽是 crypto 场景，但发表于 2020，交易所微观结构和手续费体系已变化，必须重估真实成本。
- pairs 在加密里常见“相关不协整”：相关高但价差不回归，容易形成慢性亏损。
- 高频 alpha 很容易被执行细节吃掉：延迟、滑点、成交回报偏差都会显著影响结果。
- 这条线最怕“过拟合 pair 选择窗口”，所以要做滚动 out-of-sample 与参数敏感性热图。

## 6. 来源
- Fil, M., & Krištoufek, L. (2020). *Pairs Trading in Cryptocurrency Markets.* IEEE Access, 8, 172644–172651.
- DOI: `10.1109/ACCESS.2020.3024619`
- Readable URL: `https://doi.org/10.1109/ACCESS.2020.3024619`
- Metadata URL: `https://api.crossref.org/works/10.1109/access.2020.3024619`
- Metadata URL（含 abstract_inverted_index）: `https://api.openalex.org/works/https://doi.org/10.1109/access.2020.3024619`
