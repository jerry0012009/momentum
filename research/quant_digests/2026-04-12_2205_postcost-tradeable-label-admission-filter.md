# 别再用 gross spread/funding 直接开仓：这份 2026 repo 更值得 desk 复用的是「post-cost tradeable label」这层 admission filter
- 时间：2026-04-12 22:05 UTC
- 类型：GitHub repo + 公共数据快检
- 主题类型：filter
- 基础 alpha：**服务的 base alpha 是 `perp rich spread fade + funding carry` 这类 delta-neutral relative-value 交易：当 perp 相对 spot 偏贵时做 `short perp + long spot`，等待价差回归，并让 funding 作为 carry 补贴；这篇笔记讨论的不是 alpha 本体，而是“这笔 trade 扣完成本后到底值不值得做”的 admission 层**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：filter / admission / post-cost-label / funding / basis / delta-neutral / relative-value / spread-mean-reversion / binance / btc / 15m / 5m / repo / cost / risk
- 证据类型：仓库源码与内置报告 + 公共数据快检

## 1. 这次看了什么
主线材料仍来自 **MengerWen (2026), _Deep Learning-Based Delta-Neutral Statistical Arbitrage on Perpetual Funding Rates_** 这个 GitHub 仓库，但这次不重复讲它上次那条 raw alpha 壳，而是单独拎出 repo 里**对当前 desk 更通用、也更值得复用**的一层：`post-cost tradeable label`。

翻成人话，它回答的不是“这笔 trade gross 有没有正收益”，而是：

> **如果我在 `t` 看到一组 funding / spread / vol / liquidity 特征，并在下一根才进场，这笔 delta-neutral 交易在未来 `H` 小时里，扣完手续费、滑点、gas 之后，净收益有没有超过可交易门槛？**

这比直接拿 `spread_z > 1.5`、`funding > 0` 就开仓更适合我们现在的短周期素材池，因为 desk 里很多 relative-value / pairs / funding / basis 线索，最大的问题都不是“有没有一点回归”，而是**那点 gross edge 根本不够填摩擦成本的坑**。

## 2. 核心结论
- **一句话核心结论：** 这份 repo 最值得 desk 先复用的，不是深度学习模型，而是 **“先把 future net return after cost 做成标签，再用它决定 trade on / trade off”** 这层 admission filter；对短周期 funding / basis / pairs 素材池，这往往比继续调模型更值钱。
- **一句话证明方式：** 我先读 repo 的 `labels.md`、`labels/default.yaml`、`labels/generator.py`、`signals.md` 与 robustness summary，再用 Binance 公共 `spot/perp 15m klines + fundingRate` 做最近 `90d` 的最小快检，验证“gross 上看着有一点 edge”的 spread/funding 条件，在 repo 默认成本口径下几乎全部会被 after-cost 标签否掉。
- repo 这层 label 的默认定义非常明确：
  - 方向默认是 `short_perp_long_spot`
  - `t` 时刻看到特征，**下一根 bar 才进场**，避免同 bar 泄漏
  - 默认看 `8h / 24h` 两个 horizon
  - `tradeable` 阈值是 **未来净收益 `> 5 bps`**
  - 默认成本模型约等于 **`34 bps`**：`4 × (5 bps taker + 3 bps slippage) + $2 gas / 10k notional ≈ 34 bps`
- repo 自带 OOS robustness 给的最有用数据点，不是 DL 比规则更强，而是 **阈值越严，少做烂交易越重要**：
  - `combined_funding_spread` 在 base 测试里 **7 笔交易，累计回报 `-0.2328%`**；
  - 同一策略把 `min_signal_score` 提到 `1.0` 后，最佳阈值情景的累计回报收敛到 **`-0.0664%`**；
  - `lstm` 测试期 **0 笔交易**，反而说明“after-cost 标签 + 高门槛”会天然把可交易样本压得很稀疏。
- 我做的 Binance `BTCUSDT` 近 `90d`、`15m` 快检也支持这一点：
  - 若只看 base alpha 方向（`spread_z_1d > 1` 且 `funding > 0`），未来 `8h` 的**平均 gross** 只有 **`+1.80 bps`**；
  - 全样本平均 gross 更只有 **`+0.48 bps`**；
  - 但一旦套进 repo 默认 **`34 bps`** 成本口径，样本内 **`0 / 872`** 个 bar 能达到 `tradeable > 5 bps`；
  - 即使看我定义的简单 top-score decile，也还是 **`0% tradeable`**。  
  这正是这层 label 存在的意义：**别把“有一点回归”误判成“可以交易”。**

## 3. 为什么和当前项目有关
这篇东西和当前 `momentum` desk 的关系很直接，因为我们最近 intake 的很多 raw alpha，本质上都属于“gross edge 很薄、成本/执行决定生死”的家族：
- funding / basis / spot-perp / perp-perp relative value
- pairs / spread fade / residual fade
- maker-first OFI / quote skew / fair-value gap

这些方向常见的误判是：
1. 先看见均值回归；
2. 再把它当 alpha 成立；
3. 最后才发现净收益根本不够。

而 `post-cost tradeable label` 正好把这个顺序倒过来：
- 先把 future net return after cost 显式写出来；
- 再问这笔 trade 有没有资格进入候选集；
- 最后才谈模型、排序、仓位和执行。

对当前 desk，它更像一层**shared admission filter**，可同时服务：
- `perp-quarter residual gap`
- `cross-venue basis differential`
- `stacked z-score pairs`
- `PCA / OU residual fade`
而不是只服务一个单独仓库。

## 3.5 策略拆解（必填）
- 方向属性：不是独立方向 alpha；属于 relative-value / carry 类 raw alpha 的 admission filter
- 基础 alpha：`perp rich spread fade + funding carry`（更广义上是 cost-fragile 的 spread / basis / pairs raw alpha）
- regime：
  - spread 已明显偏离
  - funding 符号与交易方向一致
  - 更高流动性、较低冲击成本时才更可能被放行
- filter / veto：
  - 只在 `future_net_return_bps_H > min_expected_edge_bps` 时允许交易
  - `H` 可取 `1h / 4h / 8h / 24h`
  - `min_expected_edge_bps` 不是固定神数，应跟成本档位联动
- risk / sizing / execution overlay：
  - 用 label 先做 `go / no-go`
  - 再把预测净边际映射到 `size-up / size-down`
  - maker / taker 场景分别建标签，避免把执行假设写死

## 4. 可复刻的最小实验
### 4.1 研究假设
对 `5m / 15m` 的 funding / basis / pairs 类 raw alpha，**“future gross return > 0” 几乎没有研究价值，真正该先看的，是 `future net return after cost` 有没有超过最小可交易边际。**

### 4.2 最小实验口径
- **资产：** `BTCUSDT` 起步，再扩 `ETHUSDT / SOLUSDT`
- **bar：** `15m` 为主，必要时补 `5m`
- **方向：** 先只测 `short_perp_long_spot`
- **特征：** `spread_bps`、`spread_z`、`funding sign / bps`、简单波动与流动性分桶
- **标签：**
  - `1h / 4h / 8h` forward gross bps
  - `1h / 4h / 8h` forward net bps
  - `tradeable = net_bps > {0, 3, 5, 8}`
- **成本阶梯：** 至少做 `6 / 12 / 20 / 34 bps`
- **最先看的 2 个指标：**
  1. `tradeable_rate`
  2. `mean_net_bps conditional on raw-alpha admission`

### 4.3 当前 first verdict
- 这层 filter **值得立刻进入研究流程**；
- 不是因为它能凭空造出 alpha，而是因为它能快速筛掉一大批“gross 有点意思、net 完全不行”的假候选；
- 对短周期 relative-value desk，优先级其实很高，因为它直接节省后续 clean replication 的时间。

## 5. 风险与保留意见
- 这不是独立 raw alpha，不能拿它冒充 alpha 本体。
- 当前 repo 主要基于 `1h BTCUSDT`；搬到 `5m / 15m` 时，funding accrual 的时间对齐要更谨慎。
- 我这轮快检只做了 `BTCUSDT`，结论更像“为什么要先做 after-cost admission”，还不是跨资产定论。
- 如果成本模型设得过高，这层 label 可能把几乎所有样本都过滤光；但这往往不是 label 错，而是**策略本身没有厚到能承受现实执行**。
- 真正上 production 前，maker/taker、排队成交、funding 结算窗附近执行都要分开建模，不能只用一个统一成本常数糊过去。

## 6. 下一步怎么测
1. **先把现有 3 条 raw alpha 接上这层 label，而不是继续找第 4 条想法。**
   优先接：`deribit perp-quarter residual gap`、`cross-venue net carry differential`、`PCA residual fade`。
2. **把标签做成 friction ladder。**
   同一套 forward return，同步输出 `6 / 12 / 20 / 34 bps` 四档，别只看单一成本世界。
3. **把 maker/taker 分开。**
   `taker/taker` 标签适合做 hard veto；`maker/taker` 标签适合做更现实的 desk admission。
4. **扩到 ETH / SOL。**
   如果 majors 都过不了 after-cost 标签，长尾更没必要急着扩。
5. **如果之后要保留 ML，只让它学“净边际排序”，别替代 base alpha。**
   这类主题里，模型更适合做 `rank / veto / sizing`，不适合先定义方向本体。

## 7. 来源
1. **MengerWen. (2026). _Deep Learning-Based Delta-Neutral Statistical Arbitrage on Perpetual Funding Rates_. GitHub repository.**
   - Readable URL: `https://github.com/MengerWen/Deep-Learning-Based-Delta-Neutral-Statistical-Arbitrage-on-Perpetual-Funding-Rates`
   - Repo URL: `https://github.com/MengerWen/Deep-Learning-Based-Delta-Neutral-Statistical-Arbitrage-on-Perpetual-Funding-Rates`
2. **本轮重点读取的 repo 文档 / 源码**
   - `docs/labels.md`
   - `configs/labels/default.yaml`
   - `src/funding_arb/labels/generator.py`
   - `docs/signals.md`
   - `reports/robustness/binance/btcusdt/1h/report.md`
   - `reports/robustness/binance/btcusdt/1h/summary.json`
3. **本轮公开数据快检**
   - Binance spot klines: `https://api.binance.com/api/v3/klines`
   - Binance perpetual klines: `https://fapi.binance.com/fapi/v1/klines`
   - Binance funding history: `https://fapi.binance.com/fapi/v1/fundingRate`

## 8. 数据源 / 公开性 / 更新频率 / 最小复现实验口径
- **数据源：** Binance 公共 `spot/perp klines + fundingRate`
- **公开性：** 公开，无需 API key
- **更新频率：**
  - K 线：可直接取 `5m / 15m`
  - funding：`8h` 结算，短周期实验可按已知 funding 历史或窗口 proxy 对齐
- **最小复现实验口径：**
  - asset：`BTCUSDT`
  - bar：`15m`
  - raw-alpha 条件：`spread_z_1d > 1 且 funding > 0`
  - label：future `8h` net return after cost
  - verdict：先看 `tradeable_rate` 是否大于 0，再谈模型或更复杂 admission
