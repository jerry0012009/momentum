# 三 EMA 回调模板这次值得进下一手 clean replication：规则和 exit 都够清楚，先别急着直接 park
- 时间： 2026-03-17 18:06 UTC
- 类型：GitHub / repo source intake
- 主题标签：crypto/pullback/ema/repo/source-intake/scout
- 证据类型：repo source intake + 两条轻量诚实守门

## 1. 这次看了什么
这轮继续按 `Run 2 / Scout Fast Lane` 找新的 `paper / repo based` 外部 source，但只比较少数几条，避免又把 Scout 扩成大搜索。

我实际对比了 3 条来自 `fmzquant/strategies` 的 fresh repo source：
1. `EMA Pullback Strategy`
2. `Keltner Channel Pullback Strategy`
3. `VWAP Deviation Band and Volatility Filter Trading Strategy`

当前 desk 语境下，边际价值排序是：
- **第一：EMA Pullback Strategy** —— pullback 语义清楚，而且不只讲 entry，还给了 stop/target 框架；
- 第二：Keltner Channel Pullback —— 方向和回抽逻辑能写，但 exit / 持有单元还是偏松；
- 第三：VWAP deviation band + volatility filter —— 结构层太厚、session anchoring 太重，source intake 阶段就已经显得过拟合风险偏高。

所以本轮只正式认领第一条，并把它推进到 intake-stage hard verdict。

## 2. 为什么这轮轮到它
- `EMA` 仍是 `waiting_not_due`，当前不能在 `Run 1` 空转；
- `Rank 17 / Rank 2 / Rank 29` 仍属于 `P3 continuity`，当前没有新的真实 `append/review need`；
- 本地 shortlist 基本被打穿，`Rank 38 / Rank 39` 也已经如实给出 `park`；
- 因此现在更值钱的，不是继续补同义 tiny-live 文档，而是**从新的 repo source 里找 1 条真的更像下一手 clean replication 的候选**。

`EMA Pullback Strategy` 在这几条里边际价值最高，因为它至少同时满足：
1. pullback 不是纯故事，能写成 `trade on / trade off`；
2. 不是只有入场，连最基本的 `止损 = pullback swing`、`止盈 = 2R` 都给了；
3. 虽然不是原生 15m crypto 模板，但比 `Rank 39` 那种 `timeframe/exit/pyramiding` 全都松着的 source 更接近当前 fast lane 需要的冻结程度。

## 3. 先把规则翻成人话
这条策略的直觉很简单：
- 先用三条 EMA 分层看趋势；
- 只在大方向没有被破坏时，等一次顺势回调；
- 回调不能深到把更慢那条过滤 EMA 也打穿；
- 等价格重新站回短 EMA，再入场；
- 止损放在那次回调的低点/高点，止盈先用固定 `2R`。

翻成人话就是：
**不追已经拉开的趋势，而是等趋势里的第一次像样回踩，再赌一次顺势恢复。**

## 4. 两条轻量诚实守门
### 4.1 `trade on / trade off` 能不能写清？
能，最小读法可以先冻结成：
- **trade on（long）**：总体趋势仍偏多（可用 `price > EMA365` 近似），价格先上穿短 EMA，再回踩短 EMA 附近但**没有**深到中慢 EMA 过滤层，并在形成更高低点后重新站回短 EMA；
- **trade off（long）**：趋势过滤失效、回踩已经打穿过滤 EMA、或重新站回短 EMA这件事没有发生；
- short 端镜像处理。

第一道门 **通过**：它不是纯机制叙事，确实能翻成一笔笔的可执行交易。

### 4.2 有没有明显 `lookahead / repaint / data leakage`？
当前 source 描述里：
- 用的是固定周期 EMA；
- 回调 / 更高低点语义虽然比简单交叉更状态化，但没有看到明显依赖未来 bar 才能确认的结构线；
- stop / target 也不是靠未来极值倒推。

所以第二道门也**基本通过**：
- 目前没有一眼就能判死刑的 `lookahead / repaint / data leakage`；
- 真正需要回答的，已经不是“它有没有明显作弊”，而是“它值不值得拿下一轮 clean replication 预算”。

## 5. 为什么它比 Rank 39 更值得给下一手预算
和刚被压回 `park / source-template only` 的 `Rank 39 / StochRSI + EMA pullback` 相比，这条更值得继续一步，核心差在 3 点：

### 5.1 execution unit 更接近冻结
`Rank 39` 最大问题之一，是只有 `strategy.entry`，缺少明确 `hold / exit / overlap` 口径。
这条三 EMA 回调模板至少已经给出：
- 回调 swing 做 stop；
- `2R` 做第一版 take-profit。

这还不是完整 clean-room，但已经比“只有 entry，没有交易单元”诚实得多。

### 5.2 它更像当前 desk 真想测的“顺势回调恢复”
当前 desk 不缺“追突破”的模板，缺的是：
- 一条更接近 `trend continuation after pullback`、
- 又不需要堆太多厚过滤器的规则。

这条正好落在那个中间地带：
- 不是纯突破；
- 也不是厚重的多因子 regime machine；
- 而是一个可以直接拿去问“15m crypto 上，这种顺势回踩恢复到底有没有 pocket”的 source。

### 5.3 复杂度比 VWAP deviation band 那条低得多
同轮对比的 VWAP deviation source 自带：
- 会话锚定 VWAP
- 标准差偏差带
- H1/H2 / L1/L2 reversal 结构
- ATR 低波动过滤
- 多档出场 / 安全退出

它不是没价值，而是**在 source intake 阶段就已经太厚**。
当前 fast lane 更该先给那种“规则短、边界清、能快速 clean replicate”的候选预算。

## 6. 当前 hard verdict
### `Rank 40 / EMA pullback strategy`
- **当前 verdict：`admit_to_clean_replication_queue`**
- 还**不是** `paper candidate`
- 更不是 `narrow paper pilot`
- 只是说明：它比当前已 park 的 fresh source 更值得拿下一轮唯一一次最小 clean replication 预算

更直白地说：
- 这条线还远没被证明能赚钱；
- 但它已经够诚实，值得进入下一手最小 clean-room 验证；
- 当前比继续补 tiny-live 同义页，或者再给 `Rank 39` 近义冻结说明，更有边际价值。

## 7. 下一轮只允许做什么
若下一轮继续认领它，默认只允许 1 次最小 clean replication：
1. 固定 `BTC/ETH/SOL 120d 15m` cache；
2. 把 source 语义压成离散交易单元：`signal bar close -> next-bar open`；
3. 只比较一小组邻近参数（例如 `EMA 20/100/200`、`33/165/365`、和一个更短邻近组），不要扩成大网格；
4. 冻结 `no-overlap`；
5. 保留 source 原意的 `pullback swing stop + 2R take-profit`；
6. 先只回答四件事：`post-cost return / positive_asset_ratio / trade_count / time-pocket honesty`。

如果这一步出来后：
- 全面转负，或
- 只靠极端稀疏 trade count 勉强为正，
那就应快速压回 `park / evidence pool`，不要继续给 stability budget。

## 8. 当前边界
- 这不是说它已经适合上 paper；
- 也不是说原 source 就等于当前 desk 的最佳参数；
- 它只是当前 fresh source 里，**最像一条可以诚实回答 yes/no 的下一手 clean replication 候选**。

## 9. 来源
1. fmzquant/strategies
   - `EMA黄金交叉回调策略EMA-Pullback-Strategy`
   - raw: https://raw.githubusercontent.com/fmzquant/strategies/master/EMA%E9%BB%84%E9%87%91%E4%BA%A4%E5%8F%89%E5%9B%9E%E8%B0%83%E7%AD%96%E7%95%A5EMA-Pullback-Strategy.md
2. 同轮对照 source
   - `Keltner-Channel-Pullback-Strategy`
   - `VWAP-Deviation-Band-and-Volatility-Filter-Trading-Strategy`
