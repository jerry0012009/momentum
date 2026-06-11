# 别把这份 2026 research engine 只读成 ML 大拼盘：对 short-cycle desk，更该先拆的是「5m 特征 → beta-neutral 1h cross-sectional ranker」这条 raw alpha

- 时间：2026-04-04 12:26 UTC
- 类型：2026 GitHub 新 repo source audit（`README.md` + `azalyst_v6_engine.py` + `azalyst_factors_v2.py` + `azalyst_train.py` + `azalyst_validator.py`）
- 主题类型：raw alpha
- 基础 alpha：**用公开 `5m` OHLCV 因子去预测“去掉当日截面均值后的 `1h` forward return”，再做 top/bottom cross-sectional long-short 排名书。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-sectional/relative-value/stat-arb/beta-neutral/return-ranking/elastic-net/mean-reversion/momentum/regime-gate/top-bottom/binance/5m/15m/3m/1m/repo/public-data/cost/risk
- 证据类型：repo 源码证据

## 1. 先回答一句：base alpha 是什么？

**base alpha = 在 crypto 截面里，去预测“谁会在未来 `1h` 跑赢同一时点的市场平均”，然后做 top/bottom 排名交易。**

这不是 filter，也不是 overlay。  
它本体就是一条 **cross-sectional / relative-value raw alpha**：
- 不是赌市场整体涨跌；
- 而是赌同一时刻不同币之间的**相对强弱排序**；
- repo 里用的 target 不是裸 `future_ret_1h`，而是**daily cross-sectional demeaned** 的 beta-neutral target。

所以这条思路对我们 desk 的价值，不在“它用了 Elastic Net / XGBoost”，而在于它把 **short-horizon relative outperformance** 明确写成了可训练、可排序、可交易的目标。

## 2. 一句话核心结论

**这份仓库真正值得 intake 的，不是它那层很重的 weekly ML 外壳，而是里面那条可独立抽出来的 raw alpha：`5m` 因子 → `1h` beta-neutral 相对收益排序 → top/bottom 组合。**

换句话说：
- **该抄的不是“72 因子 + AI 共识重构”这个 headline；**
- **而是“把单币方向问题改写成截面相对收益问题”这一步。**

这一步对 `1m/3m/5m/15m` short-cycle desk 很有用，因为它天然更适合：
- 做 long/short 双开；
- 做 market/beta neutral；
- 在单币 trend / mean reversion 之外，补一条 **relative-value 素材池**。

## 3. 它是怎么证明这件事的？

repo 的证据链，至少在工程定义上是完整的：

1. **数据层**：`3+` 年、`444` 个 Binance 交易对、`5m` OHLCV、`26M+` 行；
2. **目标层**：预测 `12` 根 `5m` bar（即 `1h`）后的 forward return，但先减去同日截面均值，形成 beta-neutral target；
3. **训练层**：`26` 周 rolling 窗口、`13` 周重训、Purged K-Fold、并对 `1h` 目标做 `12` bar 非重叠抽样，尽量减少 label overlap；
4. **组合层**：默认 top-`5` longs + bottom-`5` shorts，equal-weight，round-trip fee 直接写成 `0.2%`；
5. **否证层**：不是只跑 ML，而是先拿 `ret_1w` / `ret_3d` / `vol_regime` / composite baseline 去打 falsification campaign，要求 ML 至少要**打赢简单排序基线**才算有存在价值。

这套证据还**不是独立验证后的 alpha 成立证明**，但已经足够说明：
> 作者并不是在写一个“花哨预测器”，而是在认真定义一条 **可交易的截面 raw alpha**。

## 4. 对 short-cycle desk，真正该抄的是哪一层？

### 4.1 值得抄的层

最值得拿走的是下面这个最小骨架：

- **输入**：公开 `5m` OHLCV
- **核心特征**：`ret_1w`, `ret_3d`, `vol_regime`, `rvol_1d`, `rsi_14`, `skew_1d`, `adx_14`, `kyle_lambda`, `mean_rev_zscore_1h`, `vol_ratio_1h_1d`
- **目标**：`future_ret_1h - same_day_cross_section_mean`
- **决策**：按预测值横截面排序，做 top/bottom bucket
- **risk shell**：bull regime 不做空，high-vol 降半仓，成本直接进回测

这比“单币做多/做空预测”更像我们当前素材池里缺的那类东西：
**cross-sectional relative-value raw alpha**。

### 4.2 不该照单全收的层

repo 当前的执行外壳，反而是我最不想直接照抄的部分：
- target 明明是 `1h` forward return；
- 但 `predict_week_v6()` / `simulate_weekly_trades_v6()` 这层，默认拿 pre-week snapshot 去做**周度** top/bottom 组合；
- 这会把原本短周期 alpha 的信息压得过粗。

所以对我们 desk，更合理的读法不是“把它整套 weekly engine 搬过来”，而是：

> **把 repo 的 base alpha 抽出来，换掉它的 weekly shell，改成 `15m` rebalance / `1h` hold 或 `5m` staggered hold 的 short-cycle 版本。**

## 5. 为什么这轮值得优先于继续补单币结构型 raw alpha？

因为这条材料直接补的是我们现在仍然稀缺的一层：

- 它不是 trend breakout；
- 不是 retest / confirmation；
- 也不是纯 filter；
- 它是一条能和现有单币 alpha **并行存在** 的 raw alpha 家族：
  **cross-sectional / relative-value / beta-neutral ranking**。

而且它还有两个很实际的价值：

1. **给我们一个“如何把市场方向剥掉”的干净定义**  
   不是先做多空择时，再想办法对冲；而是一开始就把 target 定义成相对收益。

2. **给我们一个“先证明简单基线，再谈 ML”的研发顺序**  
   这跟当前 learning track 很契合。我们不用现在就上重 ML，先测：
   - `ret_1w` 排序 alone
   - `ret_3d` 排序 alone
   - `mean_rev_zscore_1h` / `rsi_14` 排序 alone
   - 简单双因子线性组合
   再看有没有必要上 Elastic Net。

## 6. 这条策略的完整策略部件是否齐全？

结论：**齐全，但要把 holding clock 从 weekly 改回 short-cycle。**

### 6.1 Entry（入场）

repo 的本质入场并不复杂：
- 每个决策时点拿横截面预测值；
- 按 predicted beta-neutral return 排名；
- 取 top `N` 做多、bottom `N` 做空。

### 6.2 Exit（出场）

repo 原生是周度 close-to-close 壳。  
对我们 desk，更合适的 exit 改写是：
- 固定 `1h` 持有（与训练 target 对齐）；
- 或 `15m` rebalance、最多持有 `4` 个 `15m` bar；
- 或 `5m` staggered overlapping book（每 `15m` 新开一层，单层持有 `1h`）。

### 6.3 Sizing / Risk

repo 已经给出两层有用模板：
- **equal-weight top/bottom**：最适合 first verdict；
- **regime gating**：`BULL_TREND` 只做多且半仓，`HIGH_VOL_LATERAL` 多空都做但半仓。

这两层都能直接迁移到我们后续 `15m/5m` 实验。

### 6.4 Cost

repo 直接把 round-trip fee 写成 `20 bps`。  
对我们 desk，第一轮更该跑 friction ladder：
- `6 bps`
- `10 bps`
- `14 bps`
- `20 bps`

因为 cross-sectional ranker 很容易在 gross 上看着像样，但被 turnover 吃掉。

## 7. 下一步怎么测（直接可排实验）

### 实验 A：先别上 ML，先跑 simple rank baselines

在 liquid universe（先 `20~30` 个主流 perp/spot）上，用公开 `5m` 数据做：
- `ret_1w` 单因子排序
- `ret_3d` 单因子排序
- `mean_rev_zscore_1h` 单因子排序
- `0.5 * ret_3d_rank + 0.5 * mean_rev_zscore_1h_rank` 简单双因子排序

看：
- average cross-sectional IC
- positive-bar ratio
- top/bottom spread return
- cost 后是否还活着

### 实验 B：把 weekly shell 改成 short-cycle shell

固定同一组特征，不急着换模型，只改执行钟：
- **版本 1**：`15m` rebalance + `1h` hold
- **版本 2**：`5m` rebalance + `1h` hold
- **版本 3**：`15m` rebalance + `45m` hold

目标：先回答 **alpha 本体有没有短周期可移植性**，而不是先追最优 Sharpe。

### 实验 C：long-only bull gate 是否真的必要

对同一横截面 ranker，分三档比较：
- 永远 long/short
- bull only 不做空
- bull 做空但半仓

看它到底是：
- 真正减少右尾被空头拖累；
- 还是只是减少交易、掩盖 cost。

### 实验 D：feature truth table，而不是全量 72 因子

优先只看这 `10` 个 stable features 的 sign / rank 是否稳定：
- 哪些在 `15m/5m` 上方向还一致？
- 哪些只在 weekly 壳里看起来有效？
- `ret_1w` 和 `mean_rev_zscore_1h` 是互补，还是互相抵消？

## 8. 风险与保留意见

- 这份 repo **证据强项是工程定义，不是独立复核后的绩效**；
- README 展示了 sample IC / R² / 周度收益片段，但这些都还不能当成我们可迁移的 live 结论；
- `1h` target 却配周度执行，是我对它最大的结构性保留；
- 当前 learning track 仍强调“先简单可解释、再复杂 ML”，所以这轮不建议直接把 whole repo 视作生产候选，而应先把它拆成：
  1. raw alpha target 定义；
  2. simple rank baseline；
  3. regime gate 是否增益；
  4. 只有在简单 baseline 成立后，才考虑 Elastic Net。

## 9. 来源

1. **Azalyst / gitdhirajsv (2026). _Azalyst Alpha Research Engine_. GitHub Repository.**  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: `https://github.com/gitdhirajsv/Azalyst-Alpha-Research-Engine`  
   - Repo URL: `https://github.com/gitdhirajsv/Azalyst-Alpha-Research-Engine`

2. **Repo source files used in this digest**  
   - README: `https://raw.githubusercontent.com/gitdhirajsv/Azalyst-Alpha-Research-Engine/main/README.md`  
   - Engine: `https://raw.githubusercontent.com/gitdhirajsv/Azalyst-Alpha-Research-Engine/main/azalyst_v6_engine.py`  
   - Factors: `https://raw.githubusercontent.com/gitdhirajsv/Azalyst-Alpha-Research-Engine/main/azalyst_factors_v2.py`  
   - Train utils: `https://raw.githubusercontent.com/gitdhirajsv/Azalyst-Alpha-Research-Engine/main/azalyst_train.py`  
   - Validator: `https://raw.githubusercontent.com/gitdhirajsv/Azalyst-Alpha-Research-Engine/main/azalyst_validator.py`

3. **López de Prado, M. (2018). _Advances in Financial Machine Learning_. Wiley.**  
   - Venue: Book  
   - DOI: N/A  
   - Readable URL: `https://www.wiley.com/en-us/Advances+in+Financial+Machine+Learning-p-9781119482086`

4. **Kyle, A. S. (1985). _Continuous Auctions and Insider Trading_. Econometrica.**  
   - DOI: `10.2307/1913210`  
   - Readable URL: `https://doi.org/10.2307/1913210`

5. **Amihud, Y. (2002). _Illiquidity and stock returns: cross-section and time-series effects_. Journal of Financial Markets.**  
   - DOI: `10.1016/S1386-4181(01)00024-6`  
   - Readable URL: `https://doi.org/10.1016/S1386-4181(01)00024-6`
