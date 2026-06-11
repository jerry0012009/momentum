# 别把这份 2025 TS/XS repo 只读成周频配置练习：对 desk 更该先测的是「return × relative-volume」横截面动量 raw alpha
- 时间：2026-03-28 06:08 UTC
- 类型：2025 GitHub 新仓库 + notebook 输出审阅 + Binance Spot 公共 `15m` extended transfer check
- 主题类型：raw alpha
- 基础 alpha：**横截面 volume-adjusted momentum**——不是单纯看谁涨得多，而是看“谁的涨跌同时伴随相对放量 / 缩量偏离均值”，再做横截面多空；组合层再决定是否和 TS-MOM / BTC 做 blend
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-sectional/momentum/volume-adjusted/relative-volume/market-neutral/portfolio-blend/turnover/cost/binance/spot/15m/5m/1m/3m/repo
- 证据类型：GitHub notebook/README 证据 + Binance Spot 公共 `15m` extended transfer check

## 1. 这次看了什么
这次看的是 **Titouan Vasnier (2025), _Quant Research Project — TS & XS Momentum in Crypto Markets_** 这个 GitHub 仓库。先直接回答这篇东西的 **base alpha**：

> **不是“周频组合优化”，也不是“Sharpe 权重混合”。真正的 base alpha，是 `return × relative-volume` 这类 volume-adjusted momentum 信号。**

这个 repo 真正值钱的地方有两个：
1. 它把 **TS-MOM / XS-MOM / volume-adjusted weekly sleeve / BTC** 明确拆层；
2. 它自己演示了一次很重要的研究纪律：**same-bar 版本看起来极强，但那是 leakage；lagged realistic 版本才值得当真。**

## 2. 核心结论
### 2.1 一句话核心结论
**这份 repo 最值得 intake 的，不是“做一个周频 blended allocator”，而是把 `relative-volume × return` 变成一类可复用的 momentum 特征；但它在短周期上暂时不能裸搬，先得过成本和 cadence 生存线。**

### 2.2 它主要是怎么证明的
**作者用 2020–2025 的 10 个大币日频数据，先做 TS-MOM / XS-MOM，再构造 volume-adjusted weekly sleeve，并把它们与 BTC 做 OOS 组合比较，同时把 utopic same-bar 与 realistic lagged 版本并排展示。**

### 2.3 repo 里最值得 desk 记住的数字
基础设定：
- Universe：**10 个大币**（BTC、ETH、ADA、BNB、AVAX、LINK、AAVE、NEAR、SOL、XRP）
- 样本：**2020–2025**
- 训练 / OOS：**2020–2021 / 2022–2025**
- 费用：**20 bps / rebalance**

先看更诚实的 OOS：
- **TS-MOM**：Sharpe **0.890**，Vol **0.532**，MDD **-0.567**
- **XS-MOM**：Sharpe **0.724**，Vol **0.235**，MDD **-0.193**
- **Volume-adjusted weekly sleeve（lagged realistic）**：OOS Sharpe **0.813**，年化波动 **0.282**
- **Equal-Vol blend（WEEKLY + XS + TS-MOM + BTC）**：Sharpe **1.570**，Vol **0.173**，MDD **-0.172**
- 这个 Equal-Vol 组合对 BTC 的回归：**annualized alpha 24.5%**，**t-stat 2.612**，beta **0.137**

但 repo 里还有一组更重要的“反面教材”数字：
- **same-bar utopic weekly sleeve**：OOS Sharpe **2.415**
- **lagged realistic weekly sleeve**：OOS Sharpe **0.813**

翻成人话：

> **同一个想法，只因为把信号和执行放在同一根 bar，就能从“看起来像神”掉回“还算靠谱”。这比任何 fancy blend 都更值得 desk 记住。**

## 3. 为什么和当前项目有关
这篇值得进 digest，不是因为我们又缺一篇“动量母论文”，而是因为它补了一个当前 desk 还值得继续积累的特征家族：

1. **raw alpha 新写法**：不是 plain return ranking，而是 **return × relative-volume**
2. **研究纪律样板**：同一 notebook 里清楚展示了 **same-bar leakage** 和 **lagged reality** 的差距
3. **组合层启发**：如果单条 sleeve 不够稳，可以在 alpha 之上再做 **equal-vol / SR-weighted blend**，而不是把 blend 误当 alpha 本体

也就是说，这份 repo 对当前 `momentum` 主线真正值钱的地方，是把下面三层拆清楚：
- **alpha 本体**：volume-adjusted momentum
- **portfolio layer**：equal-vol / SR-weighted blending
- **研究卫生**：strict lagging + turnover cost timing

## 3.5 策略拆解（必填）
- 方向属性：横截面 / 时间序列动量；对 desk 更建议先测 **横截面 long-short**
- 基础 alpha：`signal_i,t = return_i,t-lookback→t × relative_volume_i,t`
- entry：对每个 bar 先算过去 `k` 根收益，再乘相对放量偏离；横截面去均值后按符号或分位建多空
- exit：固定持有 `H` 根或到下一次 rebalance；rank 掉出时退出
- sizing：unit-`L1` / equal-vol；组合层可再做 sleeve blend
- risk：top-liquidity universe、单币权重上限、gross cap、cluster cap
- regime：当前看不出它天然需要低频 macro gate；更像是对 **liquidity / turnover** 敏感
- filter / veto：禁止 same-bar；对低成交 / 新上市 / coverage 不完整资产做 veto
- risk / sizing / execution overlay：lagged execution、turnover-cost ladder、rebalance cadence 下调、equal-vol blend

## 4. 最值得复用/复现的点
如果只从这个 repo 里偷一件东西，我不会先偷它的周频混合组合，而会先偷：

> **`relative-volume × return` 这个信号骨架。**

原因很简单：
- 它比 plain momentum 多了一层“成交确认 / 参与度偏离”信息；
- 又比纯 volume spike 更像真正的 alpha，而不是辅助 filter；
- 可以直接压缩到 `15m / 5m` 做 first verdict。

但如果只偷两件东西，我会把第二件也一起偷走：

> **禁止 same-bar，成本按 turnover 记。**

## 5. Binance Spot 公共 `15m` extended transfer check
我做了一个比“十天快检”更长一点的 `15m` transfer check，目的不是复现 repo 周频结论，而是看这类 feature 能不能往当前 desk 频率压缩。

### 5.1 检查口径
- 数据：**Binance Spot 公共 `15m` candles**
- 样本：**3000 根 `15m` bar**，约 **31 天**（2026-02-25 → 2026-03-28）
- Universe：先取 top-20 活跃 `USDT` 现货对，按覆盖率筛后保留 **16 个**
- 信号：过去 `k` 根收益 × 当前相对量能偏离 `((V - MA)/MA)`，横截面去均值后做 unit-`L1` 归一化
- 执行：**lag 1 bar**；降低换手后，按每 **16 根 `15m`（约 4h）** rebalance
- 成本：先看 **4 bps**

### 5.2 结果
延长样本后，最好的那组已经不再像短样本那样好看：
- 最优口袋约为 **`k=24`, `maL=48`, rebalance=16 bars`**
- **gross mean：`+0.09 bps/bar`**
- **net（4 bps）：`-0.09 bps/bar`**
- **avg turnover：`0.044x/bar`**
- Sharpe proxy 约 **-0.89**，final equity **0.97x**

也就是说：

> **短样本里它看起来像能活，拉长到 31 天后，当前 Binance spot `15m` 口袋已经基本只剩 gross、成本后转负。**

这反而是个有价值的结论：这条线不是完全没信息，但当前更像 **feature 候选**，还不够资格直接升格成短周期 standalone alpha。

## 6. 风险与保留意见
1. **repo 主结果是日频/周频，不是 intraday 直接配方。**
2. **same-bar 版本非常误导。** 如果不把 timing 写死，很容易把 leakage 当 edge。
3. **短周期最大敌人还是 turnover。** 我把 cadence 放慢到 4h 重平衡后，当前 `15m` 仍过不了 4 bps。
4. **当前更适合把它当 feature family。** 直接裸做可能不够，和现有 XS momentum / volatility targeting / liquidity veto 组合反而更合理。

## 7. 可复刻的最小实验
### 最小实验 A：先把它当 feature，不当最终策略
- Universe：Binance / OKX / Bybit top `12~30` liquid perp 或 spot
- Bar：先从 **`15m`**，再下钻 `5m`
- Signal：`ret(k) × rel_volume(maL)`，`k ∈ {8, 16, 24, 32}`，`maL ∈ {k, 2k}`
- 组合：market-neutral XS long-short
- 成本：必须跑 **1 / 2 / 4 / 6 bps ladder**

### 最小实验 B：测“它能不能给已有 alpha 增强”
不要只测 standalone，也要测：
- plain XS momentum
- plain XS momentum × rel-volume gated
- plain XS momentum + rel-volume 作为第二特征线性组合

看它是：
- alpha 本体增强器
- 还是只是一层质量过滤器

### 最小实验 C：只在高流动性 + 低换手 pocket 测
既然当前瓶颈是换手，就别再把注意力先放到更长尾的币：
- 先限 top-10 / top-15 流动性
- 先测 `4h / 8h` cadence
- 先比较 spot 与 perp 哪边更能保住 net edge

## 8. 我对这条线的当前判断
我的判断是：**这篇值得进素材池，但当前更适合以“可复用特征家族”身份进入，而不是直接判成可上线的 `15m` 完整策略。**

更具体地说：
- **如果目标是补 raw alpha 素材池：** 合格，因为 `return × relative-volume` 是可独立复现的 raw alpha 候选
- **如果目标是补完整策略组件：** 也合格，因为它把 blend、成本、lagging 都讲清楚了
- **如果目标是当前 desk 的短周期 first verdict：** 当前 verdict 偏保守——先保留 feature，不急着升主策略

一句话总结：

> **这份 repo 真正值钱的，不是“周频混合后 Sharpe 1.57”，而是它把 `volume-adjusted momentum`、`same-bar leakage`、`turnover-cost reality` 三件事一次性讲透了；而我这边更长的 Binance `15m` 快检也提醒我们：这条线现在更像 feature，不像可直接上线的 standalone alpha。**

## 9. 来源与链接
### GitHub 主来源
- **Author:** Titouan Vasnier
- **Year:** 2025
- **Title:** _Quant Research Project — TS & XS Momentum in Crypto Markets_
- **Venue:** GitHub repository / research notebook
- **DOI:** 无
- **Readable URL:** https://github.com/TitouanVasnier/Quant-Research-Project-TS-VS-XS-Momentum-Crypto-Strategies
- **Repo URL:** https://github.com/TitouanVasnier/Quant-Research-Project-TS-VS-XS-Momentum-Crypto-Strategies
- **Notebook:** https://raw.githubusercontent.com/TitouanVasnier/Quant-Research-Project-TS-VS-XS-Momentum-Crypto-Strategies/main/Quant_Project_TS-XS_Momentum_Crypto_Strategies.ipynb
- **Write-up PDF:** https://raw.githubusercontent.com/TitouanVasnier/Quant-Research-Project-TS-VS-XS-Momentum-Crypto-Strategies/main/Quant_Project_WriteUp_Final.pdf

### 附加说明
- repo 的 strongest evidence 在于 **lagged weekly sleeve + OOS blend**，不是 same-bar utopic 结果
- 本文里的 Binance `15m` 检查只是 **extended transfer check**，不是完整复现，也不是上线前回测结论
- 对当前 desk，更值得先测的是：**把 `rel-volume × return` 接到现有 XS momentum baseline 上，看它是 alpha 增强器还是只是 filter**
