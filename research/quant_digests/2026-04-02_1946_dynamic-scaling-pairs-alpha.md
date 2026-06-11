# 别把这篇 2024 *Journal of Risk and Financial Management* 论文只读成 RL 黑盒：对 short-cycle desk，更该先测的是「cointegration spread × zone-conditioned dynamic scaling」这条完整 pairs raw alpha
- 时间：2026-04-02 19:46 UTC
- 类型：2024 *Journal of Risk and Financial Management* 开放获取全文（arXiv HTML / DOI）+ 2025 GitHub replication repo audit（`README.md`）
- 主题类型：raw alpha
- 基础 alpha：当两条价格序列的相对价差（spread）短时偏离其协整/稳定关系后，后续存在向均值收敛的压力；alpha 本体仍是 **pairs / stat-arb 的 spread mean reversion**，不是 RL 本身。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/cointegration/spread-zscore/dynamic-scaling/position-sizing/market-neutral/1m/3m/5m/15m/paper/repo/public-data/cost
- 证据类型：论文全文（主证据）+ replication repo（工程辅助证据）

## 1. 这次看了什么
### 一句话核心结论
**这篇材料真正值得 intake 的，不是“RL 能不能赢传统方法”这个 headline，而是它把一条本来就成立的 pairs raw alpha，推进成了带 `entry / exit / sizing / cost / risk` 的完整策略卡：spread 偏离负责入场，zone-conditioned dynamic scaling 负责“仓位跟机会质量走”。**

### 一句话它为什么适合当前 desk
我们最近已经积累了不少 **pairs 的 entry / threshold / veto** 壳子，但 `FACTOR_BACKLOG` 里明确还缺 **position sizing** 这块；这篇正好补的是 **“同一条 pairs alpha，别只做二元开/平仓，还要让仓位强弱跟 spread 质量联动”**。

## 2. base alpha 是什么
这次的 **base alpha 很清楚**：

1. 先找统计关系稳定的两条价格序列；
2. 用 OLS/协整关系估 hedge ratio，得到 spread；
3. 把 spread 做成 rolling z-score；
4. spread 偏离过大时，做多低估腿、做空高估腿；
5. 等 spread 回归、仓位逻辑反转、或风险层触发时退出。

翻成人话：**不是赌某个币单边涨跌，而是赌“两样本来该一起走的东西，被短时拉太开以后，会往中间收”。**

所以这轮主题虽然来自 RL 论文，但定位仍然是：
- raw alpha：**cointegration / stable-spread mean reversion**
- sizing overlay：**仓位不是只开 0 或 1，而是随 spread 机会质量动态放大/缩小**
- risk layer：**交易成本惩罚 + close zone 平仓 + 少做无意义调仓**

## 3. 为什么这轮值得写
### 3.1 它和最近 intake 不重复的地方，不在“又一个 pairs”
最近 digest 里已经有：
- `rolling beta spread z-score fade`
- `dynamic coint spread × percentile threshold`
- `BTC anchor × OU fade`
- `microprice / OBI veto pairs`

这些大多在补 **pair selection / spread construction / threshold / filter / exit**。但这篇更稀缺的地方是：
**它直接讨论“同样的 spread alpha，为什么仓位要分强弱，而不是永远满仓 / 半仓 / 固定手数”。**

### 3.2 这很贴合当前 learning progress
`RESEARCH_AUTOMATION_BRIEF` 明确要求持续补 `mean reversion / relative value / stat-arb / pairs`；
`FACTOR_BACKLOG` 又点名了 `ATR position sizing` 仍是 `SCOPED`。这篇虽然不是 ATR sizing，但它提供了另一条更贴近 pairs 的 sizing 思路：
**让仓位跟 spread 所处 zone、当前偏离程度、已有持仓一起决定。**

### 3.3 它适合 desk 的读法，不是先上 RL 训练，而是先抽出最小可复现骨架
对 short-cycle desk，最值得先拿走的不是 A2C 训练流程，而是这条朴素翻译：
- spread 偏得越深，允许仓位越大；
- spread 只是在临界区，就轻仓试；
- 已有仓位时，只增减差额，不要每根 bar 全量翻来翻去。

也就是说，**先做 deterministic / discretized dynamic scaling shell，再决定要不要上 RL。**

## 4. 来源信息
### 论文来源
- **Authors：** Hongshen Yang, Avinash Malik
- **Year：** 2024
- **Title：** *Reinforcement Learning Pair Trading: A Dynamic Scaling Approach*
- **Venue：** *Journal of Risk and Financial Management*
- **DOI：** <https://doi.org/10.3390/jrfm17120555>
- **Readable URL：** <https://www.mdpi.com/1911-8074/17/12/555>
- **arXiv URL：** <https://arxiv.org/abs/2407.16103>
- **Fulltext URL：** <https://arxiv.org/html/2407.16103v2>

### 工程来源
- **Repo owner：** `FHLiang221`
- **Year：** 2025
- **Title：** `RL-Pairs-Trading-Replication`
- **Venue：** GitHub repository
- **Repo URL：** <https://github.com/FHLiang221/RL-Pairs-Trading-Replication>

## 5. 论文里真正有用的策略骨架
### 5.1 pair formation：先找“真的像一对”的资产
论文先用：
- Pearson correlation
- Engle–Granger cointegration

去筛 pair。样本里最强的一对是：
- **BTC-EUR vs BTC-GBP**
- `1m` 下相关性约 **0.8758**

这个具体标的不一定是我们 desk 最终要跑的对象，但它说明作者不是随便抓两条线做 z-score，而是先确认 **两腿的长期关系够稳定**。

### 5.2 signal：传统 pair trading 骨架并不复杂
论文在 rolling window 上计算 spread，然后用 z-score 分区：
- `Long Zone`：spread 明显低于均值 → 做多 spread
- `Short Zone`：spread 明显高于均值 → 做空 spread
- `Close Zone`：spread 回到中间 → 平仓

训练期网格搜索选出的最佳传统参数是：
- **open threshold = 1.8 z**
- **close threshold = 0.4 z**
- **window size = 900 bars**

这部分很重要，因为它说明：
**alpha 主体其实非常传统，创新点不在“发现了新 spread”，而在“怎么更聪明地管这笔 spread 仓位”。**

### 5.3 observation / action：dynamic scaling 才是这篇最该偷走的东西
论文给 RL agent 的核心观测不是一堆玄学 feature，而是很朴素的三样：
- `Position`
- `Spread`
- `Zone`

动作空间也很直白：
- `A ∈ [-1, 1]`
- 正值 = long leg
- 负值 = short leg
- 绝对值 = 仓位占组合资金的比例

最关键的不是这个公式本身，而是它背后的执行含义：
- **开仓**：从 0 到某个方向的目标仓位
- **调仓**：已有仓位时，只执行差额
- **平仓**：目标仓位回到 0

翻成人话：**不是每次信号来都“重新下一笔单”，而是把持仓当成一个连续变量去管理。**

### 5.4 reward shaping：它鼓励的是“少乱动、在对的 zone 做对的事”
论文把 reward 拆成三块：
1. **portfolio reward**：平仓后的真实盈亏
2. **action reward**：在对应 zone 做对动作时给奖励
3. **transaction punishment**：大幅改仓会被惩罚

对 desk 最有价值的不是 RL 术语，而是这句白话：
**pair trading 赚的是回归，不是手速；如果你每根 bar 都大幅换仓，手续费会把 edge 吃掉。**

## 6. 6 个最值得记住的硬数据点
1. **数据频率：** 论文主实验直接用 **1-minute** 数据。
2. **样本规模：** 抽象页给出 `n = 263,520`。
3. **训练 / 测试：** 形成期 `2023-10` 到 `2023-11`，测试期 `2023-12`。
4. **默认交易成本：** **0.02%**。
5. **传统方法表现：** 年化利润 **8.33%**。
6. **RL2（A2C）表现：** 年化利润 **31.53%**；在 `0.01%` fee 下累计利润 **33.99%**，`0%` fee 下累计利润 **80.92%**，说明这条 alpha 对费率极其敏感。

再补 2 个和执行更相关的数据：
- 传统法总动作数 **490**；
- RL2（A2C）总动作数 **229**，但平均盈利单更大，说明它的主要贡献之一不是“做更多”，而是**更克制地做更大的对的单**。

## 7. 对当前 1m / 3m / 5m / 15m 的可迁移结论
### 7.1 最适合先落地的，不是复刻 BTC-EUR/BTC-GBP，而是复刻“dynamic scaling shell”
原论文的 pair 选在 BTC 不同法币报价上；这对我们的 perp/major desk 不一定是最直接的交易对象。

但更值得迁移的是下面这层壳：
- pair 仍然由我们现有 shortlist 产生；
- spread 仍然用 rolling beta / OLS / OU 残差；
- **新增一层 zone-conditioned sizing**：
  - 浅偏离轻仓；
  - 深偏离加仓；
  - 回到 close zone 主动降仓；
  - 已有仓位只调差额。

### 7.2 周期优先级建议
- **15m：** 先验证 after-cost 是否真的改善 expectancy。
- **5m：** 再看 dynamic scaling 是否比 fixed-size entry 更能提高每笔盈亏比。
- **1m / 3m：** 只在 pair 足够稳、盘口成本足够低时再开；否则容易把“连续调仓”做成“连续交手续费”。

### 7.3 它服务于哪类 raw alpha
这篇不是独立的新世界观，而是一个能服务至少两类现有 raw alpha 的共享组件：
1. **cointegration / OU / z-score 类 pairs mean reversion**
2. **same-underlier cross-quote / cross-venue relative-value spread**

因此它虽然来自 RL 论文，但落到 desk 里，最现实的角色是：
**pairs raw alpha 的 sizing engine 升级件。**

## 8. 最小可复现实验
### 实验 A：先做非 RL 版 dynamic scaling ablation（最优先）
- **资产池：** 从我们已积累的 pairs 壳里挑 `3~5` 对最稳定的 liquid majors / same-underlier quote pairs
- **bar：** 先 `15m`，再 `5m`
- **spread：** rolling OLS hedge ratio + z-score
- **entry zone：** `|z| >= 1.5 / 2.0 / 2.5`
- **exit：** `|z| <= 0.25 / 0.5` 或 time stop
- **fixed-size baseline：** 每次进场固定 `1x`
- **dynamic-size 版本：**
  - `1.5 <= |z| < 2.0` → `0.33x`
  - `2.0 <= |z| < 2.5` → `0.66x`
  - `|z| >= 2.5` → `1.00x`
- **调仓规则：** 仅对目标仓位与当前仓位的差额成交
- **cost：** round-trip `10 / 20 / 30 / 40 bps`

先回答最关键的问题：
**同一条 pairs alpha，在不换 pair、不换 entry 的情况下，只改 sizing，after-cost 的 Sharpe / pnl per trade / turnover 会不会更好？**

### 实验 B：把 dynamic scaling 套到现有两条 pairs 壳上
优先拿这两类现成骨架做叠加：
1. `rolling beta spread z-score fade`
2. `dynamic coint spread × percentile threshold`

如果 dynamic sizing 只对其中一类有效，就说明它不是通用提升，而是**更适合某类 spread 形状**。

### 实验 C：再决定要不要上 RL
只有当 A/B 证明：
- fixed-size → dynamic-size 有稳定提升；
- 提升不是靠单个 pair；
- 提升能扛住 realistic fees；

才值得做简化版 RL / bandit / policy gradient。否则先停在 deterministic sizing 就够了。

## 9. 风险与局限
1. **论文的交易对象很特殊。** BTC-EUR/BTC-GBP 属于同一基础资产的不同法币报价，天然比普通跨币种 pairs 更稳，直接平移到 BTC/ETH 可能会降 edge。
2. **样本外长度不长。** 主测试期只有 `2023-12` 一个月，论文 headline 收益不该直接信。
3. **fee sensitivity 很高。** 从 `0.02%` 到 `0%`，结果差异非常夸张，说明如果交易成本控制不好，dynamic scaling 也救不了策略。
4. **别把 RL 当必要条件。** 对 desk 来说，先把 dynamic sizing 做成规则化壳子，通常比直接训练黑盒更可控。

## 10. 下一步怎么测
**下一步最该做的，不是复现 A2C，而是做一组非常干净的 ablation：同一批 pair、同一套 z-score entry/exit、同一套 cost，只比较 `fixed size` vs `zone-conditioned dynamic scaling`。**

如果结果成立，这篇就不是“又一篇 RL 论文摘要”，而是能直接进入我们 `5m/15m` pairs 策略池的一块实盘组件：
**先用传统 spread alpha 负责找机会，再用 dynamic scaling 决定这笔机会该上多大。**
