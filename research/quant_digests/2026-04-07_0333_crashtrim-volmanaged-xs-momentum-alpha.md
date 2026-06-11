# 别把 crypto 横截面动量直接判死刑：这篇 2025 FMPM 更该先测的是「winner-only / loser-short veto × vol-managed XS momentum」
- 时间：2026-04-07 03:33 UTC
- 类型：论文
- 主题类型：raw alpha
- 基础 alpha：大市值 crypto 的横截面动量（近期相对强者继续强、弱者继续弱）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：cross-sectional / momentum / relative-value / volatility-management / crash-risk / top30
- 证据类型：论文证据

## 1. 这次看了什么
读的是 **Klaus Grobys, James W. Kolari, Davide Scrimgeour (2025), _Cryptocurrency momentum has (not) its moments_**, 主题不是再争“crypto 到底有没有动量”这种空话，而是更具体地拆：**横截面动量到底是没 alpha，还是被尾部 crash 把统计结论冲坏了**。

## 2. 核心结论
- **一句话核心结论**：这篇论文更像在说——crypto 横截面动量未必失效，真正的问题是 **short leg 的极端尾部事件会把整条策略的表观显著性打穿**。
- 作者用 **top-30 市值币** 做横截面 quintile long-short：**1 个月 formation + 1 天 skip + 周度再平衡**。plain momentum 的平均周收益约 **0.71%**，但原始序列容易被尾部事件污染。
- 最关键的数据点：**一个 -255.28% 的单点观测，只占样本 0.24%，却贡献了 37% 的总复利收益影响**。也就是说，决定这条策略“看起来行不行”的，往往不是日常 alpha，而是极少数极端币种/极端周。
- 对极端观测做 trimming 后，zero-cost momentum 的平均周收益提升到 **1.33% ~ 1.51%**，对应 **t=2.63 ~ 3.94**，回到 **1% 显著**。
- 再加 volatility management 后，多数风险管理版本的平均周收益都明显高于 plain strategy；作者报告多数方案把平均周收益提升到 plain 的 **2 倍以上**，风险调整回归里的 alpha 约 **0.76% ~ 1.69%/week**。
- **一句话证明方式**：作者不是靠故事，而是靠 **更长样本 + top30 可交易宇宙 + trimming 检验 + vol-managed 对照 + 因子回归** 把“alpha 本体”和“尾部污染”拆开。

## 3. 为什么和当前项目有关
这篇对我们最有价值，不是因为它能直接照搬到 `15m`，而是因为它给了一个当前 desk 很缺的母体：**cross-sectional raw alpha 不是只有“排个名就上”，而是要先决定 short leg 要不要全开**。

当前 intake 里，结构突破、微观结构、pairs、carry 已经很多；但 **横截面动量 + 尾部治理** 这条线还缺一篇足够干净的论文地基。对短周期 desk 来说，真正值得复用的不是周频参数，而是这几个组件：
- `winner-only` 是否比硬做 WML 更稳；
- `loser-short veto` 是否能过滤最毒的 short leg；
- `single-name cap / target-vol` 是否该先于更复杂的机器学习加权；
- 判断策略生死时，要先拆 **alpha 本体** 和 **tail contamination**。

## 3.5 策略拆解（必填）
- 方向属性：横截面 / 相对价值
- 基础 alpha：过去一段时间相对更强的币继续跑赢，更弱的币继续跑输
- regime：论文未显式做 regime；desk 版可补 `broad risk-off / correlation spike / liquidation stress` 约束
- filter / veto：`loser-short veto`、极端单币事件 veto、listing-age / liquidity gate
- risk / sizing / execution overlay：target-vol、单币权重上限、child-order 分批换仓、成本阶梯

## 4. 可复刻的最小实验
- **研究假设**：short-cycle crypto 也存在可交易的横截面动量，但收益分布主要被 short leg 的极端事件扭曲。
- **可计算定义**：
  - Universe：Binance / Bybit top 20~30 liquid perps
  - Ranking：过去 `24h` 或 `8h` 收益率，`skip-last-1-bar`
  - Portfolio：long top 20%，short bottom 20%
  - 版本 A：plain long-short
  - 版本 B：winner-only
  - 版本 C：`loser-short veto`（若 funding 过热、liquidation cluster 过近、realized vol 过高则不做 short）
  - 版本 D：对 A/B/C 再加 `target-vol`（32/64/96 bars）
- **最小回测切口**：`2024-01-01` 以来，`15m` 生成组合，`5m` 执行；成本先跑 `5 / 10 / 15 bps` 三档。
- **最该先看**：
  1. post-cost Sharpe / return 是否还能活；
  2. 最差单币贡献、最差窗口、左尾分位是否主要来自 short leg。

## 5. 风险与保留意见
- 论文是 **周频 top30 大市值币**，不是 perp `5m/15m` 直接证据；迁移时要先过成本与容量。
- 这篇最强的启发来自 **distribution diagnosis**，不是直接给你 production-ready 参数。
- vol-management 虽然改善均值和回归 alpha，但作者也指出：**尾部风险没有因此彻底消失**；只缩仓，不等于修掉 crash source。
- 对 desk 来说，最危险的误读是：把这篇看成“crypto WML 有效/无效”的二元结论；更正确的读法是：**先测 alpha，再测 short leg 是否值得做满。**

## 6. 来源
- Grobys, K., Kolari, J. W., & Scrimgeour, D. (2025). *Cryptocurrency momentum has (not) its moments*. *Financial Markets and Portfolio Management*.
- DOI：`10.1007/s11408-025-00474-9`
- Readable URL：`https://doi.org/10.1007/s11408-025-00474-9`
- PDF URL：`https://link.springer.com/content/pdf/10.1007/s11408-025-00474-9.pdf`
- Metadata cross-check：Crossref / OpenAlex
