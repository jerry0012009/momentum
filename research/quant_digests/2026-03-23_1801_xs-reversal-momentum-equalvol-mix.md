# 别把横截面反转和动量当互斥派别：这份 2025 新 repo 更值得先复现的是 `short-horizon reversal + slow momentum` 的 equal-vol raw alpha 组合
- 时间：2026-03-23 18:01 UTC
- 类型：2025 GitHub 新仓库 + 近 5 年文献地基
- 主题类型：raw alpha
- 基础 alpha：横截面市场中性多空——短期超跌/超涨做反转，较慢相对强弱做延续，再按等波动混合
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-sectional/relative-value/reversal/momentum/equal-vol/risk-parity/market-neutral/cost/repo/paper/crypto/5m/15m
- 证据类型：工程经验（开源回测/稳健性/走前检验）+ 文献地基

> 先回答 base alpha：这篇东西不是 filter，也不是“把两个信号随手平均”。它的 base alpha 是**横截面 market-neutral 多空**：短周期吃相对过度反应回归，慢周期吃相对强弱延续；两条 sleeve 低相关，所以能被组合成一条更像可部署策略的 raw alpha。

## 1. 这次看了什么
这次主看的是 2025 新仓库 **`ccollins80/crypto-stat-arb`**。它不是又一篇“只给一条信号”的 repo，而是把完整流程都摆出来了：
- cross-sectional reversal sleeve
- cross-sectional momentum sleeve
- mixed portfolio（50/50 / static opt / equal-vol）
- cost sensitivity
- alpha vs BTC
- walk-forward OOS

对我们当前 desk 真正值钱的点在于：**我们今天已经连续补了不少单腿 raw alpha；这份材料刚好补“怎么把 raw alpha 组合成可部署组合骨架”这一层**，而且不是围着 breakout/retest 内循环打转。

## 2. 核心结论
- 这不是“反转 or 动量二选一”，而是**短反转 + 慢动量**这两条原始 alpha 可以并存，且在 market-neutral 口径下彼此几乎不相关。  
- repo README 给出的核心结果里，**reversal 与 momentum 的相关性约 `-0.008`**，这正是组合层最有价值的证据。  
- 单腿也不是空话：repo 报告 **Reversal net Sharpe ≈ `1.77`**，**Momentum net Sharpe ≈ `1.32`**。  
- 真正值得先抄的是组合层：**Equal-Vol mix 的 walk-forward OOS Sharpe ≈ `2.52`**，且作者声称在 **20 bps** 成本下 Sharpe 仍约 **`2.1`**。  
- 这说明它不是“再找一个小信号”，而是**可直接落地为 entry / exit / sizing / risk / cost 的完整 market-neutral 策略骨架**。  
- 一句话核心结论：**对当前 short-cycle desk，更值钱的不只是再收一条单腿 alpha，而是学会把“快反转”和“慢动量”做成低相关、成本诚实、可组合的双 sleeve 结构。**
- 一句话证明方式：**repo 已给出稳健性、成本敏感性、alpha-vs-BTC 与 walk-forward OOS，说明这不是纸上谈兵的参数截图。**

## 3. 为什么和当前项目直接相关
### 3.1 它服务于当前 raw alpha 素材池，而不是偏题
当前 `momentum` desk 最近几篇 digest 已经连续补了：
- XS momentum
- residual mean reversion
- lead-lag continuation
- pairs / stat-arb
- cluster deviation stat-arb

这篇东西仍然值得插队一次，因为它不是偏离 raw alpha，而是把**“raw alpha 怎么组合成实盘可部署骨架”**这件事讲清楚：
- 反转 sleeve：高换手、快回归
- 动量 sleeve：低换手、慢延续
- equal-vol 混合：降低单腿 path dependency

### 3.2 它比继续补一个 filter 更值钱
如果今天继续补 filter / regime / veto，边际价值未必高于继续补 raw alpha。这个主题之所以过线，是因为它本身就是：
1. **可独立复现的 raw alpha**；
2. **可直接落地完整策略**；
3. **还能服务我们已经积累的多条单腿 alpha 的组合工程。**

## 3.5 策略拆解（必填）
- 方向属性：cross-sectional / relative-value / market-neutral
- 基础 alpha：
  - fast sleeve：短期横截面过度反应后的相对回归
  - slow sleeve：较慢横截面相对强弱延续
- regime：横截面分化足够大、但不是极端单边全市场 beta 碾压时更友好
- filter / veto：流动性门槛、异常事件 blackout、极端 funding/basis 拥挤 veto、残差化基准失真停机
- risk / sizing / execution overlay：
  - sleeve 内 dollar/beta neutral
  - sleeve 间 equal-vol / risk parity
  - 换手上限
  - 成本梯度审查
  - 对小币加 participation cap

## 4. repo 里最值得抄的不是哪条腿，而是“组合骨架”
### 4.1 Reversal sleeve 的读法
repo 给的 reversal 配置读法非常清楚：
- 短 lookback（`k=2~4`）
- 强 banding（`2.0~2.5`）
- 每日调仓
- BTC residualization

这条腿服务的是**相对过度反应回归**。对 crypto 来说，它更像：
- 适合做在横截面离散度抬升、但个币噪声还没高到完全不可交易的时候；
- alpha 半衰期更短，必须严查 turnover 和冲击成本；
- 不能指望它单腿长期无脑承载全部仓位。

### 4.2 Momentum sleeve 的读法
repo 的 momentum 不是“再来一个短周期追涨”，而是：
- 长 lookback（约 `7~21` 天量级）
- 低频调仓（约 `14~30` 天量级）
- 极低换手
- 更偏 cost-resilient

这条腿服务的是**相对强弱延续**，本质上是给组合提供一个更慢、更稳、更不吃交易摩擦的 raw alpha 支柱。

### 4.3 为什么 equal-vol mix 才是 desk 最该先测的 branch
如果只抄 repo headline，很容易把重点放在“哪条腿 Sharpe 更高”。
但对我们 desk 更有价值的 branch 是：
**用 equal-vol 把快反转和慢动量绑成一条可部署策略。**

原因很直接：
1. 两条腿相关性接近 0；
2. 一条高换手、一条低换手，摩擦暴露不同；
3. 一条吃回归、一条吃延续，path dependency 不同；
4. 组合后更像“完整 desk 组件”，而不是单一因子赌局。

## 5. 对 1m / 3m / 5m / 15m 的真实关系
这里要诚实：**repo 原始口径是 hourly，不是原生 1m/3m/5m 高频脚本。**
所以更合理的 desk 落地方式不是硬装成逐根 1m alpha，而是：

- **15m：第一优先最小实验层**
  - 直接把 hourly 参数按时间长度缩放到 15m；
  - 或保留 1h 信号、在 15m 执行/风控层落地。  
- **5m：第二层增频层**
  - 不是先重写 alpha 逻辑，而是先验证 15m 通过后，能否把执行拆细、把成交改善吃出来。  
- **1m / 3m：高强度版本，不应先做主验证**
  - 这层更像 execution refinement / microstructure enhancement，而不是第一轮 yes/no verdict。

也就是说：**它和当前 short-cycle desk 有直接关系，但入口应是 15m first，而不是假装它天生就是 1m 主信号。**

## 6. 可复刻的最小实验（下一步怎么测）
**研究假设**：在 Binance 永续高流动币池里，`fast XS reversal + slow XS momentum` 的 equal-vol mix，在 15m 口径下仍能维持比单腿更好的 post-cost Sharpe，并保持接近市场中性。

### 6.1 最小实验定义
1. **Universe**：Binance USDT-M perp Top 20~30（按近 30d 成交额），剔除稳定币映射资产。  
2. **Bar**：先做 `15m`。  
3. **Residualization**：先对 BTC 做 rolling beta 残差化；可附加 ETH 版本做稳健性。  
4. **Fast reversal sleeve**：
   - lookback `k_rev ∈ {8, 16}`（约 2h / 4h）
   - band `∈ {2.0, 2.5}`
   - rebalance `every=96`（日级）
5. **Slow momentum sleeve**：
   - lookback `k_mom ∈ {336, 672, 1344}`（约 3.5d / 7d / 14d）
   - rebalance `∈ {288, 672, 1344}`（3d / 7d / 14d）
   - band `∈ {1.5, 2.0}`
6. **Portfolio**：
   - sleeve 内横截面 long-short 对冲
   - sleeve 间 equal-vol
   - gross leverage cap `1.5~2.0`
7. **成本**：至少显式测 `7 / 10 / 20 bps` 三档 round-trip proxy。  

### 6.2 先看哪 4 个指标
1. **Net Sharpe**：先判断组合层是否真的优于单腿。  
2. **Break-even bps**：确认 edge 是不是只活在零成本世界。  
3. **Turnover by sleeve**：看 reversal 是否把全部优势吃回给交易成本。  
4. **Beta / R² vs BTC**：防止“market-neutral”只是表面说法。  

### 6.3 最小 verdict 规则
- 若 equal-vol mix 在 `10 bps` 下仍优于两条单腿，且 beta 接近 0：**进下一轮 clean replication**。  
- 若 only gross 好看、net 被 reversal turnover 吃光：**降级成“组合层思路成立，但 fast sleeve 需重参数/换执行”**。  
- 若 momentum 单腿活、reversal 单腿死：**保留 slow sleeve，别强行捆绑。**

## 7. 风险与保留意见
- repo 当前证据主要来自作者的开源研究结果，我们还没做独立 clean replication。  
- 原始样本只有 **12 个 liquid pairs、约 2.6 年 hourly 数据**，regime 覆盖不算长。  
- 成本模型仍偏简化，真实 perp 交易还要加 funding、滑点、冲击和 participation 约束。  
- equal-vol mix 的漂亮结果，可能部分来自样本内资产池与残差化基准选择；必须做更换 universe / benchmark 的稳健性检查。  
- 对我们 desk 来说，最容易犯的错是：**看到 mixed Sharpe 高，就直接在 5m/1m 粗暴增频。** 正确做法应是先 15m 过诚实门，再谈 execution 下钻。

## 8. 来源
1. **ccollins80. (2025). _crypto-stat-arb_. GitHub repository.**  
   - Readable URL: https://github.com/ccollins80/crypto-stat-arb  
   - Repo URL: https://github.com/ccollins80/crypto-stat-arb
2. **Dobrynskaya, V. (2023). _Cryptocurrency Momentum and Reversal_. The Journal of Alternative Investments.**  
   - DOI: `10.3905/jai.2023.1.189`  
   - Readable URL: https://doi.org/10.3905/jai.2023.1.189
3. **Fieberg, C., Liedtke, A., Poddig, T., Walker, T., & Zaremba, A. (2025). _A Trend Factor for the Cross Section of Cryptocurrency Returns_. Journal of Financial and Quantitative Analysis.**  
   - DOI: `10.1017/S0022109024000747`  
   - Readable URL: https://doi.org/10.1017/S0022109024000747
4. **Repo internal result tables / README**（用于 Sharpe、相关性、成本敏感性与 OOS mixed portfolio 摘要）  
   - Readable URL: https://raw.githubusercontent.com/ccollins80/crypto-stat-arb/main/README.md  
   - Readable URL: https://raw.githubusercontent.com/ccollins80/crypto-stat-arb/main/notebooks/tables/01_performance_summary.csv  
   - Readable URL: https://raw.githubusercontent.com/ccollins80/crypto-stat-arb/main/notebooks/tables/02_alpha_vs_btc.csv  
   - Readable URL: https://raw.githubusercontent.com/ccollins80/crypto-stat-arb/main/notebooks/tables/04_cost_sensitivity_pivot.csv

## 9. 给这篇 digest 的一句落地结论
**如果今天只允许补 1 条更像“可部署策略”的新 intake，我会选这条：不是再争论“反转好还是动量好”，而是先在 15m 上诚实检验 `fast reversal + slow momentum + equal-vol` 这条 market-neutral 组合骨架到底能不能活。**
