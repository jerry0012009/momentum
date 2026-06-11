# Minimum Regime Performance（MRP）durability gate：别只看总 Sharpe，先看策略最差 regime 能不能活（Alexander & Fabozzi, 2025）
- 时间：2026-04-11 10:22 UTC
- 类型：论文 + GitHub engineering bridge
- 主题类型：overlay
- 基础 alpha：`不是独立方向 alpha；它服务于现有 raw alpha（pairs / funding / basis / OFI / XS / carry）的 durability / go-no-go overlay，只回答“这条 alpha 在最差 regime 里还能不能活”`
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：overlay / go-no-go / durability / regime / strategy-decay / risk / validation / MRP / OOS / cost-stress / 5m / 15m
- 证据类型：论文摘要元数据 + publisher page abstract + repo source audit

## 1. 这次看了什么
这次主源不是再补一条新 raw alpha，而是补一个**更像“alpha 录取线”**的东西：

1. **Alexander, Nolan & Fabozzi, Frank J. (2025)**  
   *Measuring Strategy-Decay Risk: Minimum Regime Performance and the Durability of Systematic Investing*，*The Journal of Portfolio Management*。  
   它提出的核心量不是总 Sharpe，而是 **MRP（minimum regime performance）= 一条策略在不同历史 regime 中，最差那个 regime 的风险调整收益**。
2. **gencersarp/cryptoarb (2026)** 这份 repo 的工程桥接价值不在它某条 funding/basis 原始信号，而在它已经有一套很像 desk admission check 的 stop criteria：`OOS Sharpe ≥ 0.7`、`1.5× cost stress 仍要活`、`max DD ≤ 10%`、`单一 fold 不得贡献 >75% 正收益`。

把两者拼起来，值得 desk 先做的不是“再发明一个 durability 故事”，而是：**给现有 raw alpha 池补一层统一的 regime durability gate**，先筛掉那些“平均数好看、但只在一个 pocket 活着”的候选。

## 2. 核心结论
- 这篇东西的 **base alpha 不存在**；它本质上是 overlay，服务对象是现有 raw alpha。
- 论文给的最重要一句话非常实用：**长期 Sharpe 高，不等于最差 regime 也活得下来**。也就是说，策略可能“平均分好看”，但在最关键的坏环境里完全塌掉。
- MRP 的定义够朴素，适合立刻搬进我们现在的 `5m/15m` alpha intake 流程：
  - 先把样本切成几个有交易意义的 regime；
  - 算每个 regime 的 post-cost Sharpe / mean return / trade survival；
  - 取最差值作为 durability 下界；
  - 再决定这条 alpha 是 `GO / size-down / PARK / DROP`。
- 这比继续补第 N 条相似 funding / pairs 线索更值钱的原因是：**素材池现在已经不缺“想法”，更缺“谁值得先花复现时间”**。

## 3. 关键数据点（这轮最值得记住的 3 个数）
1. 论文定义：`MRP = min_risk_adjusted_return_across_regimes`，也就是**最差 regime 的风险调整收益**。  
2. `cryptoarb` repo 的 admission 风格阈值已经很接近 durability 思路：`OOS Sharpe ≥ 0.7`、`cost stress = 1.5×`、`max DD ≤ 10%`。  
3. 同 repo 还额外要求：**不能让单一 fold 贡献 >75% 的正收益**；这个约束本质上就是在防“只靠一个好口袋活着”的假稳健。

## 4. 为什么这轮值得做它，而不是再补一条 raw alpha
要先诚实回答用户给的那句内部问题：**它为什么比继续补 raw alpha 更值得？**

因为这轮边际价值更高的缺口，不是“再多一条候选线”，而是**把现有几十条短周期 raw alpha 拉进同一套 admission / ranking 框架**。如果没有这一层：
- pairs、funding、basis、OFI、XS reversal 都会继续各讲各的；
- 很容易把“均值不错但 regime 极不稳”的策略排到前面；
- 研发资源会浪费在那些只在单一样本窗活着的候选上。

所以它虽然不是 raw alpha，但它**直接服务 raw alpha 素材池的排序与淘汰**，不是泛风险闲聊。

## 4.5 策略拆解（必填）
- 方向属性：不是方向信号；属于 durability / admission / sizing overlay
- 基础 alpha：无；服务于现有 `pairs / funding / basis / OFI / XS / event-driven` raw alpha
- regime：由你定义并切样本，例如 `波动高低 / 流动性高低 / funding sign / 美盘时段 / jump day vs non-jump day`
- filter / veto：若某条策略的 `MRP < 0`，或最差 regime 的 post-cost trade survival 很差，则 veto / park
- risk / sizing / execution overlay：可把 `MRP` 映射成 `gross scaler`、`max concurrent positions`、`是否允许 live shadow`

## 5. 可复刻的最小实验
### 研究假设
对一条 `5m/15m` raw alpha，**最差 regime 的表现**比全样本均值更能决定它是否值得继续做 clean replication / live shadow。

### 最小实验口径
拿当前已经积累的 4 类原型各挑 1 条：
- pairs：如 `dynamic-hedgeratio` 或 `half-life-bounded spread fade`
- carry/funding：如 `funding extreme bandfade` 或 `spot-perp spread fade`
- microstructure：如 `tradeflow OFI` 或 `OBI quote skew`
- cross-sectional：如 `entropy loser-bounce` 或 `winner-only XS momentum`

然后对每条策略做同一套切分：
1. **波动 regime**：rolling RV 分成 low / mid / high 三档；
2. **流动性 regime**：spread 或成交额分三档；
3. **时段 regime**：Asia / Europe / US pocket；
4. **拥挤 regime**（若有 perp 数据）：funding sign × OI shock quadrant。

对每个 regime 计算：
- post-cost mean return
- post-cost Sharpe
- max drawdown
- trade count
- positive trade ratio

然后定义：
- `MRP_sharpe = min(Sharpe_by_regime)`
- `MRP_return = min(mean_return_by_regime)`
- `active_regime_ratio = profitable_regimes / total_regimes`

### 最实用的第一版 go/no-go 规则
对 short-cycle desk，我会先用非常朴素的一版：
- `GO`：`MRP_sharpe > 0` 且 `active_regime_ratio >= 0.6`
- `SIZE_DOWN`：`MRP_sharpe <= 0` 但全样本 Sharpe 仍明显为正
- `PARK`：只有 1~2 个 regime 赚钱，或 `单一 regime / 单一 fold` 贡献过高
- `DROP`：`MRP_sharpe << 0` 且成本一加就死

## 6. 对当前 short-cycle desk 的直接落地方式
最值得先落地的不是复杂统计，而是这 3 个动作：

### A. 在 first verdict 后立刻补一个 durability 页
现在很多 digest 停在“这个想法能测”。下一步应该统一补：
- `best regime`
- `worst regime`
- `MRP_sharpe`
- `single-pocket dependence`

### B. 把 MRP 接到仓位而不是只接到淘汰
同一条策略不一定非黑即白。更实用的是：
- `MRP 高` → 正常 gross
- `MRP 略负` → 降仓 / 只保留最稳 regime
- `MRP 很差` → 只保留 research，不进 live shadow

### C. 和现有 friction ladder 一起看
一条策略若：
- 全样本 Sharpe 看着不错；
- 但 `1.5× fee/slippage` 一加就死；
- 且 `MRP` 为负；

那它大概率不是“待优化 alpha”，而是**脆弱 alpha**。

## 7. 风险与保留意见
- 这篇 JPM 论文不是 crypto 专文；我们拿的是**方法迁移**，不是直接照搬结论。
- regime 切分本身也可能过拟合，所以第一版必须用**简单、少量、交易上讲得通**的 regime，而不是任意切 20 个桶。
- MRP 不能替代 raw alpha；它只负责回答“这条 alpha 的坏时候有多坏”。
- 如果样本交易数太少，MRP 会不稳；所以要加一个最低 trade-count 门槛。

## 8. 下一步怎么测
1. 先从现有 4 条代表性 alpha 开始，不要全池一起上。  
2. 每条 alpha 固定同一套 `5m/15m` 成本模型与 regime 切分。  
3. 产出一张统一表：`full-sample Sharpe / MRP_sharpe / profitable regime ratio / cost-stress survival / fold concentration`。  
4. 只要这张表一出，就能把下一轮 clean replication 顺序从“凭感觉”改成“先做 durable alpha”。

## 9. 来源
- Alexander, N., & Fabozzi, F. J. (2025). *Measuring Strategy-Decay Risk: Minimum Regime Performance and the Durability of Systematic Investing*. *The Journal of Portfolio Management*, 52(4), 198–219.
  - DOI: `https://doi.org/10.3905/jpm.2025.1.807`
  - Readable URL: `https://www.pm-research.com/content/iijpormgmt/52/4/198`
  - OpenAlex: `https://openalex.org/W7117551681`
- gencersarp. (2026). *cryptoarb*. GitHub.
  - Repo URL: `https://github.com/gencersarp/cryptoarb`
  - 关键文件：`README.md`、`config/main.yaml`、`strategies/spot_perp.py`、`strategies/perp_perp.py`、`strategies/basis_mean_revert.py`
