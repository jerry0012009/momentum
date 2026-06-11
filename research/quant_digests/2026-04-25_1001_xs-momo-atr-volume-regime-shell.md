# 别把这个 2026 新仓只读成“7 币横截面动量作业”：对 short-cycle crypto desk，更该先拆的是「24h relative-strength rotation × ATR/volume 确认 × daily regime sizing」这条完整 raw alpha 壳

- 时间：2026-04-25 10:01 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `step_1.py` + `strategy_report.html`）
- 主题类型：raw alpha
- 基础 alpha：**横截面相对强弱延续：同一时刻里，过去 `24h` 相对同篮子更强的币，下一小段更容易继续强；更弱的币，下一小段更容易继续弱。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（但当前 repo 还缺显式成本与更真实执行）
- 主题标签：raw-alpha/cross-sectional/relative-value/momentum/winner-loser/atr-expansion/volume-confirmation/regime-sizing/1h-parent/15m/5m/repo/public-data/cost/risk
- 证据类型：repo code + repo backtest report

## 1. 这次看了什么
这轮看的是 2026 GitHub 仓 **codein123-afk/Cross_Sectonal_Momentum_Cryptocurrency**。我主要审了：
- `README.md`
- `step_1.py`
- `strategy_report.html`

这不是单币趋势模板，也不是只讲 filter 的结构笔记，而是一个**能从信号一直落到仓位分配的横截面动量多空壳**：
1. 每小时对 7 个币做一次横截面排序；
2. 用过去 `24h` 收益减去同截面平均收益，得到 `relative_momentum`；
3. 做多前 2 名、做空后 2 名；
4. 只有在 **ATR 扩张 + 成交量确认** 同时成立时才开仓；
5. 再用一个 **daily regime score** 去动态放大顺势腿、缩小逆势腿；
6. 如果 `return_6` 和 `return_12` 同时转负，就把该币信号清零离场。

翻成人话：它不是“单币追涨”，而是**在一个固定币篮子里做 relative-strength rotation**，再用波动、量能和大盘状态控制什么时候更值得压仓。

## 2. 一句话结论
- **一句话核心结论：** 这个仓最值得 intake 的，不是某个花哨微结构特征，而是那条很清楚的 raw alpha——**`1h` 父层做 24h 横截面 winner/loser rotation，ATR/volume 负责确认，daily regime 负责多空倾斜与总风险投放。**
- **一句话证明方式：** README 先给出 train/val/test 全套业绩，`step_1.py` 再把 `entry / exit / sizing / lookahead control / rank construction` 明确写成可执行代码，而不是只留概念图。

## 3. 为什么这轮值得做
这题对当前 desk 有价值，不是因为它“收益看起来夸张”，而是因为它正好补了一个还值得继续积累的方向：**cross-sectional / relative-value raw alpha**。

相比继续围着单币 breakout/pullback 打转，这个仓更像一个可复用骨架：
1. **base alpha 很清楚**：relative strength continuation，不是模糊 filter；
2. **天然适合多空双开**：long winner / short loser，本身就比纯单边更 desk 化；
3. **父子周期拆法自然**：`1h` 排名决定谁值得关注，`15m/5m` 可再接更便宜的 child execution；
4. **组件边界清楚**：alpha、filter、regime、sizing、exit 都拆得开，适合后续 A/B test；
5. **数据公开可得**：Binance OHLCV 即可最小复现，不依赖私有源。

所以它不是“又一个学生回测”。它更像一个**可直接进复现池的完整 raw-alpha shell**。

## 3.5 策略拆解（必填）
- 方向属性：横截面 / 相对价值 / 动量延续
- 基础 alpha：过去 `24h` 相对同篮子更强的币继续强、相对更弱的币继续弱
- regime：用 `1d` 的 `20D MA` 扩散度（7 币里有多少在 MA20 上方）决定当前更偏 bull 还是 bear
- filter / veto：
  - `ATR(14) > ATR_baseline(20)`
  - `volume_ratio > 1`
  - long 只允许 rank `>=6/7`，short 只允许 rank `<=2/7`
- risk / sizing / execution overlay：
  - 信号 `shift(1)`，下一根 `1h open` 执行
  - bull 时放大 long、缩小 short；bear 时相反
  - 绝对权重归一化，控制 gross exposure 不超过 1
  - 当前 repo **未显式扣费、未做滑点、未做 maker/taker 分层**

## 4. repo 里最值得复用的 6 个点
1. **横截面动量定义很朴素**  
   不是复杂 embedding，也不是多层 ensemble，而是：
   - 每个币算 `24h return`
   - 减去当下 7 币平均 return
   - 再做 rank

   这类定义非常适合先做 desk 的最小验证。

2. **多空表达是相对价值而不是绝对看多**  
   `cross_rank >= 6` 才 long，`cross_rank <= 2` 才 short。说明作者押注的是**币与币之间的相对强弱延续**，不是“整个市场都在涨所以买一切”。

3. **ATR expansion 在这里是 confirmation，不是 alpha 本体**  
   `ATR > ATR_baseline` 的作用，是避免在没能量的横盘里硬追相对强弱。这一点对我们很重要：后续复现时，**不要把 ATR 误写成主 alpha**。

4. **volume confirmation 同样是 veto 层**  
   `volume_ratio > 1` 才允许信号成立。也就是“这个 winner/loser 排名最好有真实资金参与”，不是纯噪声抖出来的 rank。

5. **daily regime score 负责的是 sizing，不是选币**  
   代码里把 regime 前向填充到 hourly：
   - long 权重乘 `regime_score`
   - short 权重乘 `regime_score - 1`

   这相当于：bull 市更敢拿 long basket，bear 市更敢拿 short basket。这个设计很适合拆成通用 overlay。

6. **lookahead 控制是清楚的**  
   作者对 rolling 特征普遍做了 `shift(1)`，signal 本身又在回测时额外 `shift(1)`，执行收益使用下一根 open-to-open 变化。这个严谨度比很多“README 很热闹”的仓高不少。

## 5. 直接抄代码后，你真正得到的是什么
如果把这个仓拆成 desk 可复用组件，至少有 4 层：

### A. raw alpha 层
- `relative_momentum = return_24 - cross_sectional_mean(return_24)`
- 每小时 rank
- long top 2 / short bottom 2

这是本轮真正应该 intake 的核心。

### B. confirmation 层
- `ATR(14) > ATR_baseline(20)`
- `volume_ratio > 1`

这是在回答：**“这个横截面 winner/loser 排名，此刻值不值得追？”**

### C. regime / sizing 层
- `regime_score = fraction(coin close > 20D MA)`
- bull 偏多，bear 偏空，接近 `0.5` 时收缩总敞口

这层可复用于不止一个 alpha，不一定绑定横截面动量。

### D. exit 层
- 已实现：signal 失效 / `return_6<0 & return_12<0`
- 未实现：ATR trailing stop / time cap

这意味着 repo 已经不是“只有入场，没出场”的半成品，但出场层还远没到可实盘照抄的程度。

## 6. 3 个最关键的 repo 数字
直接记 3 个最有用的数就够了：
1. **Full-sample gross return：`+3,869%`**
2. **Test-period gross Sharpe：`2.81`**（README 给的未见样本阶段）
3. **Full-period Max Drawdown：`-62.4%`**

这些数说明两件事：
- 这不是“完全没 edge 的玩具”；
- 但它也远不是“拿来就能上线”的东西，尤其在**回撤、成本和执行真实性**上还有大坑。

## 7. 我对这个仓的判断：该 intake，但要降噪后再信
我会把它归为：**值得 intake 的完整 raw-alpha shell**，但不是“直接照抄上线”的候选。

原因很简单：
1. **优点是真的清楚**
   - base alpha 清楚
   - 规则能写成代码
   - 多空、确认、regime、exit 都有骨架
   - 最小复现实验门槛低

2. **问题也很清楚**
   - 只有 7 个币，截面太小
   - 固定 universe，且起点被 AVAX 上市时间锁死
   - 回测是 gross of cost
   - 下一根 open 执行对真实成交太乐观
   - `15m/5m` 特征虽然算了，但主策略并没真正用到 child execution

所以正确读法不是“这策略有 3869% 收益，快上”。而是：**这里有一条能明确写成 `alpha + filter + regime + sizing + exit` 的相对强弱壳，值得拿来做更诚实的短周期版本。**

## 8. 它和当前短周期 desk 的关系
如果把它压到我们更关心的 `15m/5m`，最自然的做法不是把所有东西都改成 `5m` 直接重跑，而是：

- **父层（1h）**：继续做横截面 rank，决定本小时最该关注的 long/short basket
- **子层（15m/5m）**：只负责找更便宜的入场/撤单/减仓点

也就是说，它更像：
- `1h` 决定**买谁 / 卖谁**
- `15m/5m` 决定**怎么更便宜地做进去**

这很符合我们 desk 目前的研究节奏：先把 alpha 本体说清，再把执行层接上。

## 9. 风险与保留意见
1. **样本太小。** 7 币横截面很容易被单个强趋势币主导。
2. **未扣成本。** 对 hourly 多空轮动策略来说，这不是小缺陷，是第一层生死线。
3. **胜率不到 50% 不算问题，但大回撤必须认真看。** 这说明策略更依赖赔率和持续暴露，而不是“高胜率舒服赚钱”。
4. **regime score 可能和简单 beta 曝险纠缠。** 它未必真是“高明的市场状态识别”，也可能只是顺着市场单边时把净敞口偏过去。
5. **退出规则还偏粗。** `6h/12h` 同转负的 deterioration exit 很朴素，可能需要 time-stop 或 child-level stop 来控尾部。

## 10. 下一步怎么测
只做 4 个最小实验，不要一上来大炼丹：

1. **先做更大的 liquid universe**  
   把 7 币扩到 Binance USDⓈ-M `20~30` 个高流动币，测试：
   - top/bottom `10% / 20% / 30%`
   - `lookback = 6h / 12h / 24h / 48h`
   先看 alpha 本体有没有随 universe 扩大而更稳定。

2. **把 repo 的 confirmation 拆开做 ablation**  
   跑四组：
   - raw rank only
   - rank + ATR
   - rank + volume
   - rank + ATR + volume

   这样才能知道 ATR/volume 到底是在抬 Sharpe、降 turnover，还是只是 sample-specific 装饰。

3. **做 `1h parent -> 15m/5m child` execution test**  
   父层只产出候选 long/short basket；
   子层再比较：
   - 下一根直接 taker
   - `15m` pullback 入场
   - maker-first + 超时转 taker

   先看 `8 / 12 / 20 bps` friction ladder 下还能不能活。

4. **单独审 regime overlay 是否真有贡献**  
   跑：
   - dollar-neutral constant gross
   - 有 regime bias 的 gross-one version

   若后者收益提升只是来自净 beta 暴露，那就别误判为“横截面 alpha 更强”。

## 11. 来源
- codein123-afk. (2026). *Cross-Sectional Momentum Crypto Strategy*. GitHub repository.
- Authors：GitHub user `codein123-afk`（未见真实姓名）
- Year：2026
- Title：*Cross-Sectional Momentum Crypto Strategy*
- Venue：GitHub
- DOI：N/A
- Readable URL: <https://github.com/codein123-afk/Cross_Sectonal_Momentum_Cryptocurrency>
- Repo URL: <https://github.com/codein123-afk/Cross_Sectonal_Momentum_Cryptocurrency>
- README: <https://raw.githubusercontent.com/codein123-afk/Cross_Sectonal_Momentum_Cryptocurrency/main/README.md>
- Source code: <https://raw.githubusercontent.com/codein123-afk/Cross_Sectonal_Momentum_Cryptocurrency/main/step_1.py>
- HTML report: <https://raw.githubusercontent.com/codein123-afk/Cross_Sectonal_Momentum_Cryptocurrency/main/strategy_report.html>

## 12. 这轮最该记住的一句话
**这仓最值钱的不是“7 币回测赚很多”，而是它把横截面 relative-strength alpha、ATR/volume veto、daily regime sizing 和基础 exit 骨架一次性放进了同一个可复现壳里。**
