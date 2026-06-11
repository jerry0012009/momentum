# 别把这篇 2024 *Mathematics* 论文只读成 AI 分类器：对 short-cycle desk，更该先测的是「cointegration spread mean reversion × GA 优化 triple-barrier 入场筛单」这条完整 raw alpha

- 时间：2026-04-04 20:28 UTC
- 类型：2024 开放获取论文（DOAJ 摘要页 + OpenAlex 元数据）+ 本地 `15m` portability probe
- 主题类型：raw alpha
- 基础 alpha：**基础 alpha 不是机器学习本身，而是 cointegrated pair spread 在极端偏离后存在可交易的均值回归；论文真正新增的是：先用 GA 优化的 triple-barrier 标签，把“哪次偏离更值得做”单独学出来。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/cointegration/triple-barrier/genetic-algorithm/adaboost/admission-layer/veto/filter-as-part-of-alpha/crypto/15m/5m/3m/1m/paper/public-data/cost/risk
- 证据类型：paper 摘要页 + 元数据 + 本地轻量迁移检验

## 1) 这次看了什么
这次主线看的是：

- **Ning Fu, Min-Gu Kang, Joongi Hong, Suntae Kim (2024), _Enhanced Genetic-Algorithm-Driven Triple Barrier Labeling Method and Machine Learning Approach for Pair Trading Strategy in Cryptocurrency Markets_, Mathematics.**
- DOI：`10.3390/math12050780`
- 可读页面：<https://doaj.org/article/786d82c1b7034df5b5ec7a8bc8fb9f05>
- DOI URL：<https://doi.org/10.3390/math12050780>
- Repo URL：**未找到作者公开仓库**（GitHub exact-title repo search 为 `0 results`）

这篇东西对我们有价值，不是因为它又往 pairs trading 上糊了一层 AI，而是因为它很明确地把一个 desk 真会遇到的问题拆了出来：

> **不是每次 spread 偏离都值得做。**

pair mean reversion 这条 base alpha 大家都知道；真正难的是：
- 哪些偏离只是“继续发散的开始”；
- 哪些偏离才是“值得吃回归”的 dislocation；
- 如果要把这件事做成 `1m/3m/5m/15m` 的真策略，应该把这个判断层放在哪。

这篇 paper 的答案是：
**用 triple-barrier 先给交易事件打标签，再用 GA 优化标签口径，最后用分类器决定这笔 pair dislocation 到底该不该做。**

---

## 2) 先回答一句：这篇东西的 base alpha 是什么？
**base alpha = cointegrated spread 的均值回归。**

翻成人话：
- 不是赌 BTC/ETH 单边涨跌；
- 不是拿 ML 直接猜价格；
- 而是先承认这仍然是一条经典 **pairs / stat-arb / relative-value** 交易，吃的是“相对价格偏离后回到均衡”的钱；
- 机器学习做的不是替代 alpha，而是给这条 raw alpha 加一层 **trade / no-trade veto**。

所以在我们的框架里，这篇东西应该归类成：
**raw alpha（pairs mean reversion）**，不是纯 filter / regime / overlay。

原因很简单：
如果拿掉 pair spread 这条底层均值回归，分类器本身并不产生 alpha；它只是帮助这条 alpha 少做一些烂单。

---

## 3) 为什么这轮值得写，而不是继续补别的 pairs shell
最近素材池里，pairs 类原型已经不少：
- cointegration admission；
- z-score fade；
- Hurst / OU / half-life admission；
- stop-loss / time-stop / percentile entry；
- clustering / graph matching / market-factor neutralization；
- ML filter / repo shell。

但仍然有一个空档没有补得很清楚：

> **“同样一条 spread 偏离，哪些该做，哪些该放掉？”**

这篇 paper 的增量恰好在这里：
1. **把标签工程放到前台。** 不是随便拿 future return 做回归，而是用交易逻辑定义 label。
2. **把 barrier 参数本身也当成要优化的对象。** 这比“先拍脑袋定止盈止损，再训练模型”更像真实 desk 流程。
3. **把 aggressive / defensive 两套标签分开。** 论文明确区分 `HRHP`（高风险高收益）与 `LRLP`（低风险低收益）两类目标，这一点很适合我们 desk 后面拆成两个 deployment 档位。

也就是说，这轮写它，不是因为我们缺一个新的 spread alpha headline；而是因为我们缺一个**能接在 raw alpha 后面、真正决定“要不要做这笔 spread”**的 admission layer 模板。

---

## 4) 论文里最有用的东西，不是模型名，而是标签工程
根据 DOAJ 摘要页，论文主链路是：

1. 做 crypto pair trading；
2. 用 **改造后的 triple barrier labeling** 给候选交易事件打标签；
3. 用 **Genetic Algorithm** 优化 barrier 配置；
4. 产出两类标签：
   - `HRHP` = High Risk, High Profit
   - `LRLP` = Low Risk, Low Profit
5. 再用 **AdaBoost classifier** 预测未来交易行为 / 是否值得做。

摘要里最关键的数字有 4 个：
- 样本训练区间：**2017-11-09 ~ 2022-08-31**
- 样本测试区间：**2022-09-01 ~ 2023-12-01**
- `HRHP` 标签训练出来的模型，**盈利能力提升 51.42%**
- `LRLP` 标签训练出来的模型，**最大回撤（MDD）降低 73.24%**

这 4 个数字已经足够说明它不是“又一篇泛泛 AI trading 论文”：
它讨论的是非常具体的交易问题——**同一个 pair shell，可以做成 aggressive 赚钱版，也可以做成 defensive 控回撤版。**

这对短周期 desk 很重要，因为我们后面落地时完全可以拆成：
- `research mode`：多保留事件，追求样本密度；
- `live mode`：更强调 veto，优先控回撤。

---

## 5) 对 short-cycle desk，真正该抄的是哪条策略骨架

### 5.1 Admission：pair shell 还是老老实实从 spread 出发
先别把 paper 读成“分类器直接做交易”。
它可迁移的前提是：
**你本来就有一条可解释的 pair spread shell。**

最小落地建议：
- universe：`BTC/ETH/SOL` 起步，再扩到 top-liq perp；
- pair admission：`Engle-Granger / Johansen + residual ADF + rolling beta stability`；
- sampling：主线先做 `15m`，再下探 `5m/3m`；
- candidate event：只在 `|z| >= z_entry` 且不是连续重复触发时生成候选交易事件。

也就是说：
**模型的输入不该是“任意时刻的价格”，而该是“已经满足 pairs alpha admission 的候选事件”。**

### 5.2 Labeling：先把“值得做的交易”定义清楚
这是 paper 最值钱的部分。

对我们 desk 来说，triple barrier 可以这样移植：
- 上障碍：spread 朝均值回归到某个 profit target；
- 下障碍：spread 继续发散到 stop level；
- 时间障碍：超过 `N` 根 K 线还没完成预期，就强制平仓 / 视作低质量事件。

然后把 barrier 参数本身交给网格或 GA 去找，不要手写死：
- `z_entry`
- `z_tp`
- `z_sl`
- `max_hold`
- `cooldown`
- `vol-scaled or fixed barrier`

这一步的意义不是“让优化器替你找圣杯”，而是：
**让标签更贴近真实执行目标，而不是用一个与交易脱节的未来收益回归目标。**

### 5.3 Model：它更像 admission/veto，不像主 alpha
论文里用的是 **AdaBoost classifier**。

对我们 desk，这个选择反而是好消息：
- 不是非得上复杂深度学习；
- 说明先用结构化特征 + 小模型就能工作；
- 更适合 `1m/3m/5m/15m` 这类需要快迭代、快解释、快修 bug 的研发节奏。

第一版特征完全可以先用这些：
- `entry_z`, `abs_z`, `dz`
- spread slope / residual momentum
- rolling beta drift
- rolling correlation
- 两腿 realized vol ratio
- 两腿 volume ratio
- session bucket / funding state / basis state

重点不是“模型多强”，而是：
**模型只回答一个问题——这次 spread dislocation 值不值得做？**

### 5.4 Execution：paper 的核心价值是少做烂单
最适合我们的执行读法不是“模型发 BUY/SELL/HOLD”，而是：

1. 先由 pair shell 生成候选 spread trade；
2. 分类器给出 `take / skip` 或 `aggressive / defensive`；
3. 只有过线的事件，才进入真实下单；
4. 未过线的事件直接 veto。

也就是：
**分类器应该是 admission layer，不要让它反客为主变成整个策略。**

### 5.5 Exit：仍然优先用显式规则，不要全交给模型
最小实盘化建议：
- TP：`z` 回到 `0.5 ~ 1.0` 区间，或 spread hit fixed target；
- SL：`z` 继续发散到 `3.0 ~ 4.0`；
- time stop：`8 ~ 24` bars；
- emergency veto：波动/成交突然塌缩时直接减仓或平仓。

论文强调标签工程，但对我们 desk 来说，**交易出场仍要尽量显式、稳健、低解释成本。**

### 5.6 Sizing：天然适合双档位部署
这篇 paper 很适合拆成两个 sizing 档：

- `HRHP`：
  - 仅在强分数事件上放更大 size；
  - trade count 少，但容忍更高波动。
- `LRLP`：
  - 更像 risk-first 版本；
  - 允许更小收益目标，但优先压回撤。

desk 层面可直接落到：
- `p(size) = f(pred_prob, spread_vol, pair liquidity)`
- `gross cap per pair`
- `sector / underlier concentration cap`
- `daily loss throttle`

### 5.7 Cost：这类策略不能只看预测率
pair raw alpha 的坑一直都不是“有没有信号”，而是：
- 两腿点差；
- 吃单/挂单差异；
- rolling beta 造成的名义腿不对称；
- 高频重触发带来的 churn。

所以这个主题进研究池的前提，是把成本放到策略壳里，而不是写成 paper-summary 式“预测更准，因此可交易”。

最小成本建模建议：
- `round-trip spread cost`：先按 `8~20 bps` 场景化；
- taker/taker 与 maker/taker 分开；
- beta hedge 后两腿名义金额按真实 notional 计费；
- 把 skipped-trade 也记录下来，比较 **做 / 不做** 的真实差异。

---

## 6) 本地 `15m` portability probe：结论不是“直接赚钱”，而是“veto 层确实能明显减伤”
为了不只停在 paper 摘要，我做了一个很轻量的本地迁移检查，文件在：

- `reports/artifacts/quant_digest_2026-04-04_pair_label_gate/pair_label_gate_summary.csv`
- `reports/artifacts/quant_digest_2026-04-04_pair_label_gate/pair_label_gate_test_trades.csv`

### 6.1 实验口径（不是论文复刻，只测核心命题）
数据：
- workspace 里已有的 `BTCUSDT / ETHUSDT / SOLUSDT` 近 `365d`、`15m` K 线缓存
- 三组 pair：`BTC-ETH`, `ETH-SOL`, `BTC-SOL`

最小策略壳：
- rolling beta spread
- `|z| >= 2.0` 触发候选事件
- TP：`|z| <= 1.0`
- SL：`|z| >= 3.5`
- `max_hold = 24 bars`
- stylized round-trip cost：`8 bps`

标签与模型：
- label = 这笔候选事件在上述规则下 **净收益是否为正**
- 特征 = `entry_z / dz / spread slope / corr / vol ratio / rv ratio` 等结构化特征
- 模型 = `AdaBoost`
- 用训练集分位阈值得到 `take / skip`

### 6.2 本地结果
聚合结果（`ALL` 行）：
- 测试样本：**276** 笔候选事件
- 最终被模型保留：**111** 笔，占 **40.2%**
- baseline 全做的 net-loss proxy：**-151.31**
- veto 后 net-loss proxy：**-43.45**
- 损失缩窄约 **71.3%**
- MDD proxy 也从 **-150.59** 缩到 **-43.45**，缩窄约 **71.1%**
- baseline win rate：**12.0%**
- veto 后 win rate：**13.5%**

单对里相对最像样的是 `BTC-ETH`：
- AUC：**0.679**
- 只保留 **17.0%** 候选交易
- 平均单笔亏损 proxy 从 **-0.629** 收窄到 **-0.347**，约改善 **44.8%**

### 6.3 这组结果该怎么解读
这组快检**没有**证明“粗糙版 15m pair label gate 已经能直接实盘赚钱”；
它证明的是另一件更重要的事：

> **paper 的核心命题是对的——分类式 veto 层确实能明显少做烂单。**

但它也同时提醒我们：
1. **只靠粗糙 z-score shell + 简单标签，远远不够。**
2. 真正的 edge 很可能来自 **更好的标签设计**，而不是更复杂的模型。 
3. 这篇 paper 更像是在教我们怎么给 pairs alpha 做 admission layer，而不是给我们一个可直接照搬的成品参数表。

这反而是个好消息：
因为它说明后续要投入研发的重点非常明确——**标签口径、事件定义、成本壳、pair admission 稳定性**。

---

## 7) 这篇 paper 的限制，要先说清
### A. 目前我拿到的是高质量摘要与元数据，不是全文逐段审阅
这轮证据足够把主题纳入研究池，也足够支持“下一步怎么测”；
但如果要进入更高优先级复现，还是应该补一轮全文抓取/人工细读。

### B. 它解决的是“筛单”，不是凭空制造 alpha
若底层 pair shell 很差，label classifier 只能减少伤害，不能凭空把烂 alpha 变成好 alpha。

### C. 训练目标很容易被成本与样本不平衡扭曲
如果 label 没把成本、滑点、time-stop 真正纳进去，模型最后学到的很可能只是“哪些事件更极端”，而不是“哪些事件更值得做”。

### D. 在 `1m/3m` 上，事件密度与噪音都会更高
barrier 设计若不按波动与流动性缩放，很容易把模型训练成“全 skip”。

---

## 8) 下一步怎么测（直接可排）
### Phase 1：把 paper 主题变成 desk 可复现原型
先做一个最小研究任务：

1. **Universe**：`BTC/ETH/SOL/LTC/BNB/XRP` 等高流动 pair 候选
2. **Sampling**：先 `15m`，再迁到 `5m`
3. **Admission**：`EG/Johansen + residual ADF + rolling beta stability`
4. **Event trigger**：`|z| >= {1.8, 2.0, 2.2}`
5. **Barrier grid**：
   - `tp_z ∈ {0.5, 0.75, 1.0}`
   - `sl_z ∈ {3.0, 3.5, 4.0}`
   - `max_hold ∈ {8, 12, 16, 24}`
6. **Labels**：
   - `profit-first`（更接近 `HRHP`）
   - `drawdown-first`（更接近 `LRLP`）
7. **Models**：先只做 `Logit / XGBoost / AdaBoost`，不要一上来搞深网
8. **Metrics**：
   - take-rate
   - skipped-loss saved
   - selected-trade expectancy
   - selected subset MDD
   - turnover after veto

### Phase 2：明确它到底服务哪类部署
测完后不要只看收益，要回答两个更现实的问题：
- 它适不适合做 **research veto**（降低样本污染）？
- 它适不适合做 **live gate**（减少实盘烂单）？

### Phase 3：若 `15m` 成立，再下探 `5m/3m`
`1m` 先不急，先把：
- pair admission 重算频率；
- cost model；
- signal clustering / cooldown；
- 同 underlier 集中度；

这些东西补齐。否则 `1m` 很容易把策略变成 churn machine。

---

## 9) 本轮结论（短版）
这篇 2024 paper 值得进池，不是因为它又做了个“AI pair trading”标题党，而是因为它把一个真实而关键的问题讲清楚了：

> **pairs raw alpha 的关键增量，不一定是再换一个 spread 模型，而可能是把“哪次偏离值得做”这层 admission / veto 单独做出来。**

对当前 short-cycle desk，我会这样定位它：
- **主题类型：raw alpha**
- **基础 alpha：cointegrated spread mean reversion**
- **论文真正新增：GA 优化 triple-barrier 标签 + classifier veto**
- **最值得先复现的，不是模型名，而是标签工程与双档位部署（HRHP/LRLP）**

如果要排优先级：
这篇不是“今天就能上实盘”的成品，
但它非常值得作为 **pairs alpha admission layer** 的核心素材，进下一轮最小实验。

---

## 10) Sources
1. **Fu, N., Kang, M.-G., Hong, J., Kim, S. (2024). _Enhanced Genetic-Algorithm-Driven Triple Barrier Labeling Method and Machine Learning Approach for Pair Trading Strategy in Cryptocurrency Markets_. Mathematics.**  
   DOI: <https://doi.org/10.3390/math12050780>  
   Readable URL: <https://doaj.org/article/786d82c1b7034df5b5ec7a8bc8fb9f05>  
   Repo URL: not found in public exact-title GitHub repo search.

2. **Liang, Y., Thavaneswaran, A., Paseka, A., Qiao, W., Ghahramani, M., Bowala, S. (2022). _A Novel Optimal Profit Resilient Filter Pairs Trading Strategy for Cryptocurrencies_. 2022 IEEE 46th Annual Computers, Software, and Applications Conference (COMPSAC).**  
   DOI: <https://doi.org/10.1109/compsac54236.2022.00201>  
   用途：作为 crypto pairs 中“动态过滤 / 交易稳定性优先”的近邻参考，不是本轮主文。

3. **本地 portability probe artifacts**  
   - `/root/clawd/jerry/momentum/reports/artifacts/quant_digest_2026-04-04_pair_label_gate/pair_label_gate_summary.csv`  
   - `/root/clawd/jerry/momentum/reports/artifacts/quant_digest_2026-04-04_pair_label_gate/pair_label_gate_test_trades.csv`
