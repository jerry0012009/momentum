# 别把这个 Lévy/Hermitian lead-lag repo 只读成“followers 跟随 leaders”：对 short-cycle desk，更该先测的是「leader impulse × lagger-vs-leader spread catch-up」这条 relative-value raw alpha

- 时间：2026-04-12 14:36 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `levy.py` + `hermitian.py` + `trading_signal.py` + `portfolio.py` + `main.py`）+ Binance USDⓈ-M `15m/5m` public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：**Lévy lead-lag 分数高的一组资产更像“先动腿”，分数低的一组更像“后反应腿”；当 leaders 先走出一段，laggers 与 leaders 之间的相对价格会在接下来几根 bar 里部分回补。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha/cross-sectional/relative-value/lead-lag/levy-area/hermitian-clustering/leader-lagger/catch-up/spread/hyperliquid/binance-perpetual/5m/15m/repo/public-data/cost/risk
- 证据类型：GitHub repo 工程实现 + Binance 公共数据 first-verdict probe

## 1. 先把一句话说清楚：这篇东西的 base alpha 是什么？

> **base alpha = leaders 先动、laggers 后动，所以真正值得 desk 先测的不是“followers 同向追随”，而是 `leader impulse -> lagger-vs-leader spread close`。**

这一步必须先讲清。因为 repo README 的表述容易让人以为它在做“leaders 涨了就直接追 followers”。但按源码往下拆，真正更适合我们 desk 的 raw alpha 分支其实是：

- 先用 `levy.py` 对 rolling return path 算 pairwise lead-lag 分数；
- 用 `hermitian.py` / `trading_signal.py` 把资产分成更像 leaders 和 laggers 的两侧；
- 然后不要直接做单腿追随，而是把它改写成 **long laggers / short leaders**（leaders 上涨时），或反向做空 laggers / 做多 leaders（leaders 下跌时）的相对价值书。

翻成人话：

> 不是赌“落后腿会无脑追涨杀跌”，而是赌“先动腿和后动腿之间会出现一个短时错位，这个错位会回补”。

## 2. 这次看了什么

主来源是 **Mateo Fourquet (2026), _Crypto Lead-Lag Strategy_** 这个 GitHub repo：
- Repo URL：<https://github.com/mateofrqt/Crypto-LeadLag-Strategy>
- 无 DOI / 非正式论文，但有清楚的数学和代码骨架。

这轮重点看的不是 README 口号，而是 5 个真正决定可复现性的文件：
- `levy.py`：先把价格面板转成标准化收益，再算 pairwise Lévy area；
- `hermitian.py`：把反对称 lead-lag 矩阵嵌到 Hermitian 结构里做谱聚类；
- `trading_signal.py`：repo 实际 live 信号逻辑；
- `portfolio.py`：组合/风险壳；
- `main.py`：默认回测流程和窗口参数。

源码里最重要的 3 个可迁移点是：
1. **rolling_window = 30**；
2. **selection_percentile = 0.15**，也就是 leader / lagger 两端各取约前后 15%；
3. repo 默认 live 逻辑其实是：先看 leaders 最新一根平均回报的方向，再决定 followers 的交易方向。

## 3. 核心结论

- **一句话核心结论：** repo headline 的“followers directional catch-up”在 Binance `15m` 上不够好，但把它改写成 **lagger-vs-leader spread catch-up** 之后，至少能从负 edge 拉成小幅正的 raw alpha 候选。
- **一句话证明方式：** 我先按 repo 的 rolling Lévy score / top-bottom selection 逻辑，在 Binance USDⓈ-M `BTC/ETH/SOL/XRP/DOGE/BNB/ADA/LINK` 上做 `15m` 与 `5m` portability probe，再对比“followers 同向追随”与“long laggers / short leaders”的两种读法。
- **`15m` 直接照 repo 的 followers 同向追随书**：`4283` 个事件里，未来 `1/2/4` 根平均约 **`-0.54 / -0.91 / -0.48 bps`**，gross 累计约 **`-22.3% / -35.0% / -25.3%`**，说明这条直译版不过线。
- **改成 `15m` 的 lagger-vs-leader 相对价值书** 后，同样 `4283` 个事件里，未来 `1/2/4` 根平均约 **`+0.26 / +0.43 / +0.44 bps`**，gross 累计约 **`+11.35% / +19.10% / +18.21%`**；方向终于转正，但还远没厚到能轻松吃掉 taker 成本。
- **更自然的 `5m` 口径** 下，若再要求 leaders 当根绝对波动至少 **`30 bps`**，则 `170` 个事件里：
  - 未来 `15m`（3 bars）lagger-vs-leader spread 平均约 **`+2.06 bps`**，胜率 **`57.6%`**；
  - 未来 `30m`（6 bars）平均约 **`+2.90 bps`**，胜率 **`53.5%`**。
- 但即便这样，按双腿 round-trip **`4 / 8 bps`** 粗扣，仍然**没有稳定越过 taker friction**。所以这轮最诚实的结论不是“找到可直接上线书”，而是：
  - **raw alpha 本体有一点东西；**
  - **但现阶段更像 maker-first / execution-sensitive / threshold-gated 的 relative-value 候选。**

## 4. 为什么和当前项目有关

这轮值得 intake，不是因为它已经过线，而是因为它给 raw alpha 池补了一个我们最近还不够系统化的方向：

- 不是 breakout / trend / funding / basis；
- 而是 **cross-sectional lead-lag / relative-value catch-up**；
- 且结构很适合拆成：
  - `base alpha`：leader-lagger spread close
  - `filter`：只有 leader impulse 足够大才开
  - `execution`：更偏 maker / spread-close / inventory-aware，而不是无脑 taker

这很符合当前 desk 想补的：
**raw alpha 素材池要持续扩到 cross-sectional / relative-value / stat-arb，而不是只围着单资产形态打转。**

## 4.5 策略拆解（必填）

- 方向属性：横截面 / 相对价值 / lead-lag catch-up
- 基础 alpha：leaders 先走出冲击后，laggers 与 leaders 的相对价差在后续几根 bar 内部分回补
- regime：更像高联动、短时错位但未完全同步的 market state
- filter / veto：`|leader move|` 至少达到一档阈值（这轮 `5m` probe 里 `30 bps` 比无阈值更像样）
- risk / sizing / execution overlay：两端各取 `15%` 资产；按 `|levy_score|` 归一权重；future `15m/30m` time-stop；成本必须单独做 `4/8/12 bps` friction ladder；优先测试 maker-first / spread-close 执行，而不是默认双腿 taker

## 5. 可复刻的最小实验

### 研究假设
当 rolling Lévy score 把一组币识别成 leaders、另一组识别成 laggers 时，如果 leaders 本根已经先走出明显冲击，laggers 与 leaders 的 spread 在接下来 `15m~30m` 有回补倾向。

### 一个可计算定义
1. 用 `30` 根 rolling window 的标准化收益，算每对资产的离散 Lévy area：
   `0.5 * Σ(x_t * y_{t+1} - y_t * x_{t+1})`
2. 对每个资产取 row-mean score；
3. 取 top `15%` 作为 leaders，bottom `15%` 作为 laggers；
4. 若 leaders 当根均值回报 `> +30 bps`：做多 laggers、做空 leaders；若 `< -30 bps`：反向；
5. 持有 `3` 或 `6` 根 `5m` bar 后平仓。

### 最小回测切口
- 资产：`BTC/ETH/SOL/XRP/DOGE/BNB/ADA/LINK`
- 数据：Binance USDⓈ-M 公共 `5m` / `15m` klines
- 先看：
  1. `gross mean bps / trade`
  2. `4/8/12 bps` 成本后是否还活着

本地 artifacts：
- `/root/clawd/jerry/momentum/reports/artifacts/literature/hyperliquid_levy_leadlag_15m_probe_summary_2026-04-12.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/hyperliquid_levy_laggervsleader_15m_probe_summary_2026-04-12.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/hyperliquid_levy_laggervsleader_15m_threshold_summary_2026-04-12.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/hyperliquid_levy_laggervsleader_5m_threshold_summary_2026-04-12.csv`

## 6. 风险与保留意见

- 这不是正式同行评审论文，而是个人 GitHub repo；优点是代码清楚，缺点是外部实证约束弱。
- repo 的默认 live 方向其实更偏 **directional follower book**；这轮真正更有 desk 味的，是我额外拆出来的 **relative-value branch**，所以它属于“沿 source 派生的 desk 读法”，不是原仓库 headline。
- 这轮 public probe 用的是 Binance perp，不是 Hyperliquid 原生数据；因此它回答的是 **portability**，不是“repo 原市场已完整复现”。
- 现在最大问题不是有没有正号，而是 **gross 太薄**。所以它暂时不能被包装成完整 taker 策略，更像：
  1. maker-first 候选；
  2. 或现有 RV / stat-arb 书的 admission layer。

## 7. 一句话带走

**这个 repo 真正值得 desk 留下来的，不是“leaders 动了就追 laggers”，而是“leaders 先动后，lagger-vs-leader spread 有短时回补倾向”——但当前 public probe 还只够把它列进 raw alpha 池，不够直接过成本线。**

## 8. 下一步怎么测

1. **把执行从 taker 改成 maker-first**：只在 spread 继续拉开时挂回补方向，被动成交，检验 `0~2 bps` 成本世界是否能站住。  
2. **加第二层 gate**：除了 `|leader move| >= 30 bps`，再要求 `leader_score - lagger_score` 足够大，避免弱排序噪音。  
3. **缩窄 universe**：优先测试 `ETH/SOL/XRP/DOGE/ADA/LINK` 这类高 beta alt，不让 `BTC/BNB` 这种更像 market anchor 的腿稀释错位。  
4. **做事件簇去重**：连续多根触发只保留第一次，避免同一段冲击被过度重复记账。  
5. **补 Hyperliquid 原生验证**：若原市场 `5m` / `1m` 下 edge 更厚，再决定它是独立书还是 shared lead-lag gate。

## 9. 来源

### 主来源（repo）
- Mateo Fourquet. (2026). *Crypto Lead-Lag Strategy*. GitHub.
- DOI：无
- Readable URL / Repo URL：<https://github.com/mateofrqt/Crypto-LeadLag-Strategy>
- README：<https://raw.githubusercontent.com/mateofrqt/Crypto-LeadLag-Strategy/main/README.md>

### 本轮重点审计文件
- `levy.py`
- `hermitian.py`
- `trading_signal.py`
- `portfolio.py`
- `main.py`

### repo 在 README 中提到的相关方法线索
- Lévy-area / rough-path lead-lag detection
- Hermitian matrix clustering
- ARahimiQuant/lead-lag-portfolios（repo 在 README 中提到的启发来源）