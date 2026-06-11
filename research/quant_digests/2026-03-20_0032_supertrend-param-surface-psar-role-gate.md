# 别把 Supertrend / PSAR 当固定参数模板：15m 上先找“参数平原”，再决定它是入场键还是结构锚
- 时间：2026-03-20 00:32 UTC
- 类型：论文 + GitHub + 本地代理快检
- 主题标签：ema/psar/raw-alpha/supertrend/atr/parameter-surface/regime/filter/repo/paper/crypto/15m
- 证据类型：论文证据 + 工程经验

## 1. 这次看了什么
这轮主看 Abdul Rahman (2024) 的 Supertrend 参数优化论文（arXiv），并对其配套仓库 `Shafiq-Abdu/Supertrend-Strategy` 的思路做了一个 desk 口径的本地代理快检：直接在 Binance `BTC/ETH/SOL` 最近 120 天 `15m` 上扫 `ATR period × multiplier` 参数面，看它到底有没有“通用最优”，还是只能作为 `EMA / PSAR raw alpha focus` 的辅助层。

## 2. 核心结论
- **一句话核心结论**：在 15m crypto 里，Supertrend/PSAR 这类 ATR-trailing 信号更像“角色层（gate/anchor）”，而不是一组固定参数就能跨资产复用的主入场 alpha。
- **一句话它怎么证明**：论文里同一默认参数在不同资产表现分化、BO 最优参数不一致；本地快检在 `BTC/ETH/SOL 120d 15m` 也复现了同样的“参数异质性”。
- 论文给出的默认参数 `(15,3)` 并不稳：作者报告中五资产总览里，默认口径并非一致盈利，同时 BO 后各资产最优参数分别落在 `(20,4)/(14,5)/(5,1)/(19,3)/(14,4)`，本身就在说“别幻想单一参数统治全场”。
- 我们的本地代理快检（统一 `6bps/side`，long-short flip）里，三资产最佳参数也不一致：`BTC` 最优约 `(14,4)`、`ETH` 最优约 `(14,4)`、`SOL` 最优约 `(20,5)`；跨资产均值最高的是 `(20,5)`，但仍带明显资产分化。
- 对当前三条收口线最可复用的旁支不是“换一个 Supertrend 入场”，而是：**把 `ATR period × multiplier` 先做稳定性筛选，再把通过筛选的配置降级为 shared gate / exit anchor**，优先服务 `EMA / PSAR raw alpha`，并可旁路支援 `breakout follow-up` 与 `Fib retest_hold`。

## 3. 为什么和当前项目有关
- 这条题直接命中当前高权重主线 `EMA / PSAR raw alpha focus`：我们最近连续在做“确认层/否决层”，但对 PSAR/ATR 家族仍缺一层“参数稳定性诚实门”。
- 如果参数面本身没有平原、只有尖峰，那么把它当主触发会很容易 OOS 失真；但把它改造成 **regime gate / 结构锚 / 出场锚**，通常更符合 desk 的成本-稳定性约束。
- 它也能反哺另外两条线：
  - `breakout-short follow-up`：用 Supertrend side 只做 continuation allow/deny，而非直接开仓。
  - `Fibonacci retest_hold`：把 Supertrend side 当 retest 后续路径确认层，而非 Fib 本体替代。

## 4. 可复刻的最小实验
- **研究假设**：Supertrend 在 15m crypto 上“做主信号”不稳，但“做角色层（gate/anchor）”比“做主触发”更稳。
- **可计算定义**：
  - 先在训练段对 `period∈{7,10,14,15,20}`、`mult∈{2,3,4,5}` 计算参数面；
  - 定义 `stability_score = mean_post_cost_return × positive_asset_ratio ÷ (1 + flip_rate)`；
  - 仅保留 `top-k` 的“平原候选”（不是单点冠军）。
- **最小回测切口**：`BTC/ETH/SOL`，`15m`，`180d`（`120d train + 60d test`），统一 `6/10/15/20 bps per side` 成本梯度。
- **三臂对照**：
  1) `EMA/PSAR raw`（现有基线）；
  2) `EMA/PSAR raw + Supertrend side gate`（只做 allow/deny）；
  3) `EMA/PSAR raw + Supertrend exit anchor`（只改退出）。
- **先看 2 个指标**：`post-cost return`、`positive-asset-ratio`（辅看 `flip_count` 防过度交易）。

## 5. 风险与保留意见
- 论文证据强度一般：属于 thesis 型 arXiv 文稿，样本主要是股票日级数据，不是专门为 5m/15m crypto 设计。
- 仓库可复现性有帮助，但工程严谨度有限（notebook 驱动、指标口径需二次审计）。
- 本地快检是代理实验：仅 spot klines、未纳入 funding/basis/冲击成本，且当前仍是单轮参数快扫，不能替代完整 OOS 与 rolling 稳健性检验。

## 6. 来源
- Rahman, A. (2024). *Optimising Supertrend Parameters using Bayesian Optimisation for Maximising Profit and other metrics*. arXiv (q-fin.TR).
  - DOI: `10.48550/arXiv.2405.14262`
  - Readable URL: <https://arxiv.org/abs/2405.14262>
  - PDF: <https://arxiv.org/pdf/2405.14262.pdf>
- Shafiq-Abdu. (2024). *Supertrend-Strategy*. GitHub repository.
  - Repo URL: <https://github.com/Shafiq-Abdu/Supertrend-Strategy>
- 本轮 desk 代理快检数据与结果：
  - Artifact CSV：`reports/artifacts/quant_digests/supertrend_param_proxy_2026-03-20.csv`
  - Market data（公开可得）：Binance Spot Klines API（`https://api.binance.com/api/v3/klines`，15m）
