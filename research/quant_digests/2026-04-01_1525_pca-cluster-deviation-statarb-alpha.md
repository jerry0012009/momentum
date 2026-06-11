# 别把这份 2026 新 stat-arb repo 只读成“signed-graph 聚类作业”：对 short-cycle desk，更该先测的是「PCA residualized cluster deviation-to-mean」这条 raw alpha

- 主题类型：raw alpha
- 基础 alpha：PCA 去市场模态后的**簇内相对偏离均值回归**（cross-sectional / relative-value / stat-arb / mean reversion）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 时间：2026-04-01 15:25 UTC
- 类型：2026 GitHub 新仓库 source audit（`README.md` + `stat_arb/reporting/FINAL_REPORT.md` + `stat_arb/signals/cluster_deviation.py` + `stat_arb/run_phase1.py` + `stat_arb/backtest/costs.py` + GitHub API metadata）
- 主题标签：raw-alpha/cross-sectional/relative-value/stat-arb/mean-reversion/cluster-deviation/pca-residualization/market-neutral/signed-graph/sponge/binance/bybit/okx/15m/5m/3m/1m/repo/public-data/cost
- 证据类型：2026 GitHub 新仓库 source audit（核心策略文件 + 最终报告 + 仓库元数据）

## 1. 这次看了什么
这次主材料不是论文，而是一份 **2026-01-14 创建** 的 GitHub 新仓库：**Aroesler1 (2026), _crypto_stat_arb_**。repo headline 看起来像“signed graph clustering + SPONGE/BNC/spectral”的工程作业，但对我们 desk 真正更值得 intake 的，不是整套图聚类 headline，而是它在 `cluster_deviation.py` 里已经写成完整骨架的那条 **cluster deviation mean reversion raw alpha**：**先做 PCA 去市场模态，再按相关性把币分簇，然后在簇内做“落后者回归、领先者回吐”的 relative-value 交易。**

## 2. 先回答一句：这篇东西的 base alpha 是什么？
**base alpha 不是 clustering 本身，也不是 PCA 本身。**

它的 alpha 本体是：
- 先把整体市场共振拿掉；
- 再在相互更像的一组币里，盯住谁**相对簇组合跌多了 / 涨多了**；
- 然后做 **long cluster underperformers / short cluster outperformers** 的簇内均值回归。

翻成人话：
**这是一条“簇内相对偏离会回归”的 raw alpha。**

所以它是：
- `raw alpha`
- `cross-sectional / relative-value`
- `stat-arb`
- `mean reversion`

不是 filter，不是 regime，也不是只会服务别人的 risk overlay。

## 3. 为什么这轮值得写，而不是继续补一个只会服务别人的 gate
最近我们已经补了不少 carry / pairs / microstructure / breakout / liquidity overlay。当前还值得继续扩的，是**能独立成体系、又能比较快 desk 化的横截面 / stat-arb raw alpha**。这份 repo 值得进池，原因有三条：

1. **base alpha 很清楚。** 不是“复杂方法堆砌后再看有没有 edge”，而是明确的簇内 relative-value mean reversion。
2. **完整策略骨架已经齐。** repo 里已经给了 signal、walk-forward、turnover cap、cost sensitivity、market-neutral 检查。
3. **最适合 desk 的旁支已经自己浮出来了。** 源 repo 最能扛成本的，不是 baseline z-score，而是 `Strategy 2 (Cluster Deviation)`；这正好符合“不要被 headline 方法锁死，要抓最适合 desk 的旁支想法”这条当前原则。

## 4. 这次看的主来源
### 4.1 主来源（repo）
- **Author / Repo owner**：Aroesler1
- **Year**：2026
- **Title / Repo**：*crypto_stat_arb*
- **Venue**：GitHub repository
- **DOI**：N/A
- **Readable URL**：https://github.com/Aroesler1/crypto_stat_arb
- **Repo URL**：https://github.com/Aroesler1/crypto_stat_arb
- **GitHub metadata**：created `2026-01-14T00:21:27Z`，pushed `2026-01-14T00:30:21Z`

### 4.2 这轮实际看的关键文件
- `README.md`
- `stat_arb/reporting/FINAL_REPORT.md`
- `stat_arb/signals/cluster_deviation.py`
- `stat_arb/run_phase1.py`
- `stat_arb/backtest/costs.py`

## 5. 这条 raw alpha 在代码里到底怎么定义
### 5.1 先做 cluster composite
`cluster_deviation.py` 先按 cluster 把币分组，然后为每个簇算一个组合收益：
- 默认是 **equal-weight composite**；
- 也支持 **inverse-vol composite**。

也就是说，先回答“这组相近币今天整体怎么走”。

### 5.2 再看单币相对簇组合的偏离
代码里核心定义非常直白：
- `deviation = token return - cluster composite return`
- 再把 deviation 在 `lookback=20` 上做累计
- 再在 `zscore_window=60` 上标准化成 z-score

这一步的直觉也很干净：
**不是看单币绝对涨跌，而是看它相对自己那一簇到底跑输了多少 / 跑赢了多少。**

### 5.3 入场方向就是典型簇内 relative-value MR
`generate_target_weights()` 里的规则几乎可以直接翻译成策略卡：
- `z < -entry_threshold`：做多簇内落后者
- `z > +entry_threshold`：做空簇内领先者
- 默认 `entry_threshold = 2.0`
- 先做 **cluster neutral**，再做 **dollar neutral**

翻成人话：
**簇内跌过头的，买；簇内涨过头的，卖；先在簇内配平，再在全组合层面配平。**

### 5.4 上游两层不是 alpha 本体，但很重要
repo 先做：
1. **PCA market-mode removal**：先把 PC1 / 市场共振剥掉；
2. **signed k-NN correlation graph + clustering**：再决定谁跟谁属于一个簇。

这两层不是 raw alpha 本体，但它们会直接决定：
- 你是在拿 market beta 偏离当 MR，还是在拿**真正簇内 idiosyncratic 偏离**当 MR；
- 你交易的是一堆胡乱拼在一起的币，还是**本来就更相近的一组币**。

## 6. 最值得拿走的硬数据点
### 6.1 repo 的数据规模不小，至少不是玩具样本
`FINAL_REPORT.md` 给出的口径：
- **样本期**：May 2023 ~ May 2025
- **交易天数**：`729` days
- **Universe**：`174` tokens
- **平均可交易数量**：`134` tokens

这至少说明：它不是在 5 个币上硬讲故事。

### 6.2 真正值得 desk 看的是 Strategy 2，而不是 baseline z-score
repo 自己的 best configuration 是：
- **Strategy 2 (Cluster Deviation)**
- **SPONGE k=3**
- **Net Sharpe @ 25 bps：1.76**
- **Ann. Return @ 25 bps：29.2%**
- **Net Sharpe @ 50 bps：0.24**
- **Ann. Return @ 50 bps：4.1%**
- **Break-even cost：54.2 bps**

这组数字为什么值钱？
因为它在告诉你：**同一个研究框架里，最能扛成本的不是 generic z-score，而是“相对簇组合偏离”的那条 raw alpha。**

### 6.3 市场中性不是口头说说
repo 最终报告里给了：
- **ETH beta：约 0.02**
- **PC1 beta：约 0.00**

这意味着它至少在回测口径上，不是靠赌市场方向赚钱，而更像一条真正的 market-neutral stat-arb。

### 6.4 baseline 也顺手给了一个反例
Phase 1 baseline 虽然 gross Sharpe 不差，但：
- **Gross Sharpe：2.69**
- **Net Sharpe @ 50 bps：-2.33**
- **Break-even：26.9 bps**

这恰恰强化了当前 desk 该拿走的结论：
**不要把整个 repo headline 当主角；真正值得转进 short-cycle 素材池的，是更能扛成本的 cluster deviation 旁支。**

## 7. desk 角度最该偷的，不是“signed graph”四个字，而是这条更适合 short-cycle 的旁支读法
如果照论文/仓库 headline 去抄，你很容易把精力放在：
- SPONGE vs BNC vs signed spectral 哪个更强；
- k 取 3 还是 5 还是 6；
- 图聚类实现细节。

但对当前 desk，更值钱的读法是：

1. **raw alpha 本体**：簇内相对偏离均值回归；
2. **服务它的上游组件**：市场模态剥离 + cluster map；
3. **服务它的落地组件**：turnover cap + cost hurdle + cluster-neutral sizing。

换句话说：
**我们第一刀不一定要完整复刻 signed-graph clustering；更应该先测“residualized cluster deviation MR”本体在 `15m/5m` 有没有 edge。**

## 8. 对 `1m / 3m / 5m / 15m` 的 desk 化映射
### 8.1 先慢更新 cluster，再快交易 deviation
repo 是日频 walk-forward。迁到短周期时，更合适的不是“每根 bar 都重聚类”，而是：
- **cluster map 慢更新**：例如每 `4h / 1d` 重算一次；
- **deviation signal 快更新**：例如每 `5m / 15m` 计算一次簇内偏离 z-score。

这样更符合 short-cycle desk：
- cluster 负责定义“谁和谁是一组”；
- signal 负责定义“这一组里谁暂时跑偏了”。

### 8.2 一个诚实的 `15m` first-pass
建议第一刀先做：
- **Universe**：top `20~40` liquid perps
- **returns**：`15m`
- **market removal**：先用 `BTC` 或 equal-weight market proxy 做一阶 residualization；有时间再上 PCA
- **cluster map**：基于过去 `7~14` 天 residual return correlation，每 `1d` 更新一次
- **signal**：
  - `deviation_i = r_i - cluster_composite_i`
  - `cum_dev` 用最近 `4 / 8 / 12` 根 bar
  - `zscore_window` 先试 `32 / 64 / 96` 根
- **entry**：`|z| > 1.5 / 2.0 / 2.5`
- **exit**：回到 `|z| < 0.3 / 0.5` 或持有 `4 / 8 / 12` 根 bar

### 8.3 一个更快的 `5m` second-pass
如果 `15m` 有信息，再下钻：
- `5m` bar
- cluster 仍然慢更新，不要同步提速
- signal lookback 可试 `12 / 24 / 36` 根
- z-score 窗口可试 `96 / 144 / 288` 根
- 持有先试 `12 / 24 / 36` 根 bar

### 8.4 `1m / 3m` 更像 execution / refinement，不该当第一刀
`1m / 3m` 上当然也能做，但更适合作为：
- entry timing refinement
- maker/taker 决策
- microstructure veto

而不是一开始就把 raw alpha existence 判断丢进最脏的 execution noise 里。

## 9. 可以怎样直接落成完整策略骨架
### 9.1 Entry
- 先更新 cluster map
- 计算每个币对簇组合的 residual deviation z-score
- long 最负的 tail，short 最正的 tail
- 只在通过最小流动性 / 最小成交额门槛的币里开仓

### 9.2 Exit
第一版先别花：
- 回到 `|z| < exit_band`
- 或固定持有到 `max_hold`
- 或 cluster membership 变化时强制平仓

### 9.3 Sizing
先按三层写：
- **cluster-neutral**：每簇内多空先配平
- **portfolio-neutral**：全组合再做 dollar-neutral / beta-neutral
- **risk cap**：单币 notional cap、单簇 gross cap、全组合 gross cap

### 9.4 Risk
至少加四个：
1. **turnover cap**：repo baseline 里把 turnover 限在 `15%/day`，这层对短周期更重要
2. **cluster stability gate**：同一币频繁换簇时降权或禁做
3. **event veto**：上线/下线/重大公告 bar 附近不做 MR
4. **correlation breakdown kill-switch**：簇内平均相关性塌掉就停机

### 9.5 Cost
repo 的 `costs.py` 用的是非常朴素的 **bps-per-side on turnover** 模型。对我们第一轮最小实验，至少要跑：
- `5 bps`
- `10 bps`
- `15 bps`
- `20 bps`
- `25 bps`

然后直接问一句：
**after-cost 的 break-even 在哪，edge 到底是 signal 来的，还是 turnover 没管住。**

## 10. 最小可复现实验（直接对当前 desk）
### 实验 A：先不复刻 signed graph，只测 raw alpha 本体
- **Universe**：Binance/Bybit/OKX top `20~30` liquid perps
- **Bar**：`15m`
- **Cluster**：先用 residual correlation + 层次聚类 / k-means 都行
- **Signal**：簇内 deviation z-score
- **Portfolio**：cluster-neutral long/short tails
- **回答问题**：不靠复杂图方法，簇内 deviation MR 本体还有没有 alpha？

### 实验 B：ablation ladder
固定同一 universe / cost / hold，只比较：
1. **纯 cross-sectional reversal**（不分簇）
2. **分簇但不 residualize**
3. **先 residualize 再分簇**
4. **再加 turnover cap**

这个实验最关键，因为它能直接回答：
**增量到底来自簇结构、市场模态剥离，还是只是 generic reversal。**

### 实验 C：slow-cluster / fast-signal 结构检验
- cluster 每 `1d` 更新一次
- signal 每 `15m` 或 `5m` 更新
- 对比 cluster 每 `4h` 更新一次

要回答的问题是：
**cluster map 需要多快更新？如果 cluster 比 signal 还快，是否只会制造 turnover 和噪音？**

## 11. 下一步怎么测
建议按这个顺序走：

1. **先做 `15m`、slow-cluster / fast-signal 的 first verdict**，不要第一刀就上 `1m`。
2. **先用简单 residual correlation clustering 做最小复现**，不要被 SPONGE/BNC 细节卡住。
3. **第一轮只跑三件事**：raw alpha existence、cost cliff、cluster stability。
4. **如果 `15m` 有 edge，再下钻 `5m`**；如果 `15m` 只有 gross 正、after-cost 死，就先回去降 turnover，不要急着提速。
5. **只有当 simple clustering 版已经说明 alpha 本体存在时**，才值得继续补 signed-graph / PCA 完整复刻。

一句话版：
**这条主题最值得先测的不是“复杂图聚类有没有学术美感”，而是“簇内 residual deviation MR 在 short-cycle perp 上，扣成本后到底能不能活”。**

## 12. 这条线当前的诚实边界
也要明确三条边界：

1. 源 repo 的主证据是**日频 low-cap crypto**，不等于 liquid perp `5m/15m` 会自动成立。
2. repo 的 cost model 仍然简化，真实短周期里滑点、资金费、冲击成本都可能更差。
3. 如果 cluster 关系不稳，或者市场在单边风险传染期，MR 很容易直接被拖成“抄底抄到半山腰”。

所以这轮正确定位是：
**高质量 raw-alpha intake candidate**，不是“已经可直接实盘”的结论。

## 13. 来源链接
- Repo：https://github.com/Aroesler1/crypto_stat_arb
- README：https://raw.githubusercontent.com/Aroesler1/crypto_stat_arb/main/README.md
- Final report：https://raw.githubusercontent.com/Aroesler1/crypto_stat_arb/main/stat_arb/reporting/FINAL_REPORT.md
- Cluster deviation strategy：https://raw.githubusercontent.com/Aroesler1/crypto_stat_arb/main/stat_arb/signals/cluster_deviation.py
- Phase 1 runner：https://raw.githubusercontent.com/Aroesler1/crypto_stat_arb/main/stat_arb/run_phase1.py
- Cost model：https://raw.githubusercontent.com/Aroesler1/crypto_stat_arb/main/stat_arb/backtest/costs.py
- GitHub API metadata：https://api.github.com/repos/Aroesler1/crypto_stat_arb
