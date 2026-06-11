# 别把这份 2026 research repo 只读成“又一个 pairs notebook”：对 short-cycle desk，更该先拆的是「validation-ranked pair admission × gross-exposure-capped spread fade」这条完整 raw alpha 壳——而且 repo 自带的 `15m` cost rerun 里，它扣完 Roll slippage 之后还活着

- 时间：2026-04-15 03:36 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `config/default.yaml` + `src/crypto_trader/signals/pairs.py` + `src/crypto_trader/backtest/pairs_engine.py` + `src/crypto_trader/analysis/pairs_research.py` + `src/crypto_trader/backtest/slippage.py` + `data/processed/pairs/strategy/pairs_comparison_summary.csv` + `data/processed/costs/strategy_comparison.csv`）
- 主题类型：raw alpha
- 基础 alpha：**先找协整 pair，再对 `spread = y - beta*x` 做历史滚动 z-score；`|z|` 偏离够大就做 spread mean reversion，回到均值附近平仓。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/cointegration/walk-forward/validation-ranking/cost-aware-sizing/gross-exposure-cap/roll-slippage/binance-spot/15m/repo/cost/risk
- 证据类型：repo source audit + repo embedded results

## 1. 这次看了什么
这次主看的是一个 2026 GitHub research repo：

- **Author**：`Rah9742`
- **Year**：2026
- **Title**：`Crypto-Stat-Arb`
- **Venue**：GitHub repository
- **DOI**：N/A
- **Readable URL / Repo URL**：<https://github.com/Rah9742/Crypto-Stat-Arb>

先把 base alpha 说清楚：
> **这篇东西的 base alpha 不是“validation 排名”，也不是“成本模型”。它真正的 base alpha 仍然是 cointegrated spread mean reversion。**

但这份 repo 值得 intake 的地方在于：它没有停在“找一对协整资产然后画 z-score”，而是把一条更接近 production review 的完整壳补齐了——**rolling formation / zscore、状态机 entry-exit、cost-aware sizing、gross exposure cap、train-validation-test 排名、以及最终 cost rerun** 全都在同一套框架里。

## 2. 核心结论
1. **alpha 本体很朴素，但实现壳比大多数 pairs repo 完整得多。**  
   `generate_pair_signal_state()` 用的是历史口径状态机：`|z| >= entry` 开仓，`|z| <= exit` 平仓，额外还有 `stop_zscore` 和 `max_holding_period_bars`。

2. **它不是“拍脑袋挑最赚钱参数”，而是先过 validation/risk bar 再排名。**  
   `rank_validation_configurations()` 先筛：validation/test 不得爆仓、terminal equity 不能太低、drawdown 不能穿线、validation/test trade 数要够，然后再按 `validation_sharpe / test_sharpe / calmar / return / turnover / train-validation gap` 的加权分数排序。

3. **它不是只会固定满仓开 pair，而是做了简单但实用的 cost-aware sizing。**  
   `build_pair_target_notionals()` 会按 `expected_move / round-trip cost` 和 `|z|/entry_threshold` 缩放 gross target，不够划算时最小只给 `cost_aware_min_scale`。

4. **repo 给出的最终 chosen pair 是 `AVAXUSDT/ICPUSDT`，而且不是只在 in-sample 好看。**  
   `pairs_comparison_summary.csv` 第一名参数是：
   - formation window：`12096` bars
   - zscore window：`2016` bars
   - entry：`2.5`
   - exit：`0.25`
   - time stop：`48` bars
   - validation cumulative return：`+39.02%`
   - validation Sharpe：`1.87`
   - test cumulative return：`+31.74%`
   - test Sharpe：`1.34`
   - test trades：`23`
   - test avg holding：`47.39` bars

5. **更关键的是，repo 还有一层真正的 cost rerun，而不是只报 sweep 指标。**  
   `strategy_comparison.csv` 里，pairs 最终 rerun（`AVAXUSDT/ICPUSDT`，`15m`）结果是：
   - gross return：`+38.17%`
   - net return：`+25.74%`
   - total transaction cost：`1242.89 USDT`
   - turnover / initial capital：`140.75x`
   - net Sharpe：`1.18`
   - net max drawdown：`-30.31%`

一句话结论：
> **这份 repo 最值得 desk 学的，不是“协整 spread 可以均值回复”这种老话，而是：如何把一条 pairs raw alpha 做成一套带 validation 证据门槛、成本缩放和 gross exposure 约束的完整研究壳。**

它主要靠什么证明？
> **靠源码里的历史口径实现 + sweep 排名表 + 单独 cost rerun 表，而不是只靠 README 口号。**

## 3. 为什么和当前项目有关
这份东西和当前 `momentum` 主线直接相关，因为它补的不是泛解释，而是 **可复现、可进素材池、可拆成实盘组件** 的 raw alpha 壳：

- 对 raw alpha 池：补的是 `pairs / stat-arb / relative-value / mean reversion`
- 对工程实现：补的是 `entry / exit / sizing / risk / cost` 一整条链
- 对实盘候选池：它比“只会给 z-score 的 pairs notebook”更接近可审阅对象

更现实一点说，最近 digest 里虽然 pairs 很多，但多数结论都落在：
- alpha 本体有点意思；
- 但 taker friction 把它吃掉；
- 或者 repo 只有 alpha，没有完整研究壳。

这次不太一样：
> **Rah 这份 repo 至少给出了一条成本后仍然为正的 `15m` 现成 rerun。**

当然也要留个心眼：`config/default.yaml` 顶部还有个 `interval: 4h  #15m` 的旧注释，说明配置说明和最终产物存在过漂移；真正可信的口径，要以 `strategy_comparison.csv` 里落下来的 `bar_frequency=15m` 和具体参数表为准。

## 3.5 策略拆解（必填）
- 方向属性：横截面 / 相对价值 / 均值回复
- 基础 alpha：协整 spread 偏离后的均值回复
- regime：仅在 pair 关系仍可用、validation/test 没有被风险门槛淘汰时才保留该配置
- filter / veto：validation evidence、risk-limit checks、trade-count / active-bars bar
- risk / sizing / execution overlay：cost-aware gross target、gross exposure cap、max live gross leverage、time stop、Roll slippage rerun

## 4. 可复刻的最小实验
### 研究假设
如果某对 liquid majors/alts 在滚动 formation 窗里仍维持较稳定的 cointegration / hedge ratio，那么 `15m` spread z-score fade 在加上最基本的 cost-aware sizing 和 gross cap 后，仍可能留下可交易净值曲线。

### 最小实验设计
先不要一上来就做全市场 pair search，直接做 4 步：

1. **`15m` 复刻 repo 口径**  
   - universe：先用 8~12 个 liquid contracts
   - formation：`84d / 126d` 两档
   - zscore window：`14d / 21d`
   - entry：`2.0 / 2.5`
   - exit：`0.25 / 0.5`
   - max hold：`24 / 48` bars
   - 先在 spot 或 same-venue perp 上复刻 `train / validation / test`

2. **`5m` 只做 execution translation，不改 alpha 本体**  
   保持 pair admission 和 signal state 在 `15m` 冻结，把执行拆到 `5m`：
   - `15m` 生成 state
   - `5m` 做被动 close-out / rebalance
   - 看成本是否能从 taker 壳再压一截

3. **`3m / 1m` 只测 exit microstructure，不要重做全套选 pair**  
   最先测的不是新 alpha，而是：
   - `1m/3m` 是否更适合做 partial exit / passive unwind
   - 是否能减少 repo 里已经很高的 turnover cost

4. **先做 friction ladder，再讨论扩大 universe**  
   最少给三档：`1 bps / 2 bps / 5 bps`，否则 pairs 研究很容易把 gross alpha 误当净 alpha。

## 5. 下一步怎么测
按当前 desk 价值排序，我会先测这三件事：

1. **把 repo 的 validation-ranked 壳迁到 Binance USDⓈ-M liquid majors**  
   不是为了复制 `AVAX/ICP` 本身，而是为了回答：这个 ranking + evidence bar 是否真能筛出更稳的 crypto perp pairs。

2. **把 `cost_aware sizing` 和 `fixed sizing` 做 A/B**  
   这是 repo 最值得偷的旁支之一。先看：在同一个 raw alpha 上，它到底是实打实改善净收益，还是只是缩了风险同时也缩了机会。

3. **把 `15m signal / 5m execution / 1m unwind` 拆层**  
   如果这套壳未来真要进实盘，最像 production 的路线不是把 alpha 硬压到 `1m`，而是让更快频率去服务退出、减仓、冲击控制。

## 6. 来源
1. **Rah9742. (2026). _Crypto-Stat-Arb_. GitHub repository.**  
   - Readable URL / Repo URL：<https://github.com/Rah9742/Crypto-Stat-Arb>
2. **Key source files audited**  
   - `config/default.yaml`  
   - `src/crypto_trader/signals/pairs.py`  
   - `src/crypto_trader/backtest/pairs_engine.py`  
   - `src/crypto_trader/analysis/pairs_research.py`  
   - `src/crypto_trader/backtest/slippage.py`
3. **Embedded result files used in this digest**  
   - `data/processed/pairs/strategy/pairs_comparison_summary.csv`  
   - `data/processed/costs/strategy_comparison.csv`
