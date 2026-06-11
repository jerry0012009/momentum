# 别先迷信深度学习：这份 2026 repo 里更适合 desk 先测的是「perp rich spread fade × positive funding admission」
- 时间：2026-04-11 05:13 UTC
- 类型：GitHub repo + 公共数据快检
- 主题类型：raw alpha
- 基础 alpha：**当 perp 相对 spot 明显偏贵时，做 `short perp + long spot` 等待价差回归；若同时 funding 为正，则在等待均值回归时还多了一层 carry 补贴**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（**repo 原型壳完整**，但**当前 OOS 证据不足以直接上生产**）
- 主题标签：carry / funding / basis / delta-neutral / spread-mean-reversion / short-perp-long-spot / binance / btc / 5m / 15m / repo / cost / risk
- 证据类型：仓库源码与内置报告 + 公共数据快检

## 1. 这次看了什么
主线材料是 **MengerWen (2026), _Deep Learning-Based Delta-Neutral Statistical Arbitrage on Perpetual Funding Rates_** 这个 GitHub 仓库。

它的 headline 是“深度学习 + delta-neutral funding arbitrage”，但对我们当前 desk 来说，真正值得先 intake 的不是 LSTM 本身，而是 repo 里那条**更朴素、也更可快速复现**的 raw alpha：

> **`combined_funding_spread`：perp 相对 spot 偏贵（spread z-score 高）时做 `short perp + long spot`；如果 funding 还是正的，就把它当更强 admission。**

翻成人话：**你不是在赌方向，而是在赌“perp 的高溢价会回一点”，同时如果资金费率还是正的，你在等待期间还有机会拿到 carry。**

这比“再训一个更复杂模型”更适合当前阶段，因为：
- base alpha 说得清；
- entry / exit / cost / sizing 壳在 repo 里都已经写出来了；
- 我们可以直接把它映射到 `5m / 15m` 做最小 portability probe，而不必先复刻完整 ML 训练流水线。

## 2. 核心结论
- **一句话核心结论：** 这份 repo 最值得 desk 先拆的，不是深度学习预测器，而是 **`perp rich spread fade + positive funding admission`** 这条 delta-neutral raw alpha 壳；它在逻辑上成立、在公共数据上也能看到短周期 spread convergence，但**短周期 gross edge 目前明显小于 taker/taker 成本，必须把 execution 重新设计成 maker-assisted 或 funding-window-aware 才有希望活下来**。
- **一句话证明方式：** 我先读 repo 里已经提交的 baseline / backtest / robustness 文档与报告，再用 Binance 公共 `spot klines + futures klines + fundingRate` 对 BTC 做 `5m/15m` portability probe，发现 **spread rich 之后的确有稳定回归**，而 **positive funding 会小幅增强这条回归**；但 repo 自带的 base-cost OOS 结果说明，**如果你按“小时级、低频触发、直接吃 taker 成本”的方式做，edge 还不够厚**。
- repo 自带的几组关键数：
  - 数据覆盖：`2021-01-01` 到 `2026-04-07`，共 `46,152` 根小时 bar，`3,092` 次 funding event。
  - 数据统计：平均 funding event 约 **`+1.04 bps`**，绝对 spread 的 `95%` 分位约 **`10.04 bps`**。
  - OOS robustness（`BTCUSDT 1h`，base cost=`5 bps taker + 3 bps slippage + $2 gas`）：
    - `combined_funding_spread`：**7 笔交易，累计回报 `-0.2328%`，净 PnL `-232.8 USD / 100k`**。
    - `logistic_regression`：**3 笔交易，累计回报 `-0.1050%`**。
    - `lstm`：**0 笔交易**，说明不是“深度学习自动更强”，而更像阈值/标签太苛导致没有交易。
- Binance 公共 BTC portability probe（近 `60d`）：
  - **`15m`**：若 `spread_z_96 > 1.5`，未来 `4h` 平均 spread convergence 约 **`+1.43 bps`**；若再要求 `funding > 0`，升到 **`+1.55 bps`**，命中率约 **`94.9%`**。
  - **`5m`**：若 `spread_z_96 > 1.5 且 funding > 0`，未来 `1h` 平均 convergence 约 **`+1.20 bps`**，未来 `2h` 约 **`+1.25 bps`**。
- 真正该学到的是：**这条 raw alpha 有，但不是“直接 taker/taker 就能收钱”的那种厚边。** 对短周期 desk，它更像：
  1. 一个**可独立复现的 spread-fade alpha 核**；
  2. 一个**给已有 basis/carry 壳做 entry timing 的 admission**；
  3. 一个**适合 funding window 前后做 execution 优化**的 slow-to-fast bridge。

## 3. 为什么和当前项目有关
这条线跟当前 desk 的关系很直接，因为它补的是一类我们明确想持续积累的 raw alpha：**carry / funding / basis / relative-value / delta-neutral**。

而且它不是纯概念评论，而是已经给出了完整的策略骨架：
- 信号层：funding / spread / regime
- 交易层：`short perp + long spot`
- 回测层：cost / hold window / signal off / max hold
- 稳健性层：cost sensitivity / holding sensitivity / feature ablation

对当前 `1m/3m/5m/15m` 研发，最重要的启发不是“照抄 1h BTC 课程项目”，而是把它**拆成更适合短周期的两层**：
- **base alpha**：perp-rich spread fade
- **secondary admission / carry booster**：positive funding

这就比“只把 funding 当情绪温度计”更实，也比“先训练模型再说”更接近 first verdict。

## 3.5 策略拆解（必填）
- 方向属性：market-neutral / relative-value / carry-enhanced mean reversion
- 基础 alpha：`perp rich spread fade`（perp 相对 spot 偏贵时，短 perp、长 spot，等价差回归）
- regime：
  - 优先高流动性大币（先从 `BTC` 起）
  - funding 为正时更顺手，因为 short perp 一侧有 carry
  - 更像围绕 funding anchor / basis anchor 的慢变量，不是裸方向信号
- filter / admission：
  - `spread_zscore_72h >= 1.5` 或短周期可替代为 `spread_z_96 >= 1.5`
  - `funding_rate_bps >= 1.0` / `funding > 0`
  - 可加 `positive_funding_regime == 1`
- entry / exit / sizing / risk / cost（repo 壳）：
  - entry：信号出现在 `t`，默认 `t+1` 开仓
  - exit：`signal_off` / `holding_window` / `maximum_holding`
  - sizing：fixed notional per leg（默认 `10,000 USD`）
  - risk：单策略单持仓、持有窗、可选止盈止损
  - cost：显式扣 taker fee / slippage / gas / friction

## 4. 可复刻的最小实验
### 4.1 repo 原始定义（我们真正该先复刻的部分）
repo 里最值得先照搬的，不是 DL，而是 rule baseline：
- `funding_threshold_2bps`
- `spread_zscore_1p5`
- `combined_funding_spread`

其中第三条最像完整 raw alpha：
- `funding_rate_bps >= 1.0`
- `spread_zscore_72h >= 1.5`
- `positive_funding_regime == 1`
- 方向固定：`short_perp_long_spot`

### 4.2 我这轮做的短周期 portability probe
- **数据源：** Binance 公共 API
  - Spot: `/api/v3/klines`
  - Perp: `/fapi/v1/klines`
  - Funding: `/fapi/v1/fundingRate`
- **标的：** `BTCUSDT`
- **窗口：** 近 `60d`
- **bar：** `5m` 与 `15m`
- **定义：**
  - `spread_bps = (perp_close - spot_close) / spot_close * 1e4`
  - `spread_z_96 = (spread_bps - rolling_mean_96) / rolling_std_96`
  - 信号：`spread_z_96 > 1.5`
  - admission：`funding > 0`
  - 评价：未来 `30m/1h/2h/4h` 的 spread convergence（`-Δspread_bps`，越大越好）

### 4.3 first verdict（当前）
- **raw alpha 本体是成立的：** 不管 `5m` 还是 `15m`，只要 perp 明显偏贵，后面大概率会有一点回归。
- **positive funding 不是 alpha 本体，而是 booster / admission：** 它能把 `15m` 的 `4h` mean convergence 从 **`+1.43 bps`** 提到 **`+1.55 bps`**。
- **但短周期 standalone 还不够厚：** `1.2~1.6 bps` 的 gross convergence，离 CEX 上双腿 taker round-trip 成本还差得很远。
- **所以更合理的 desk 读法是：**
  1. 把它先当 **maker-assisted / low-cost shell**；
  2. 或者把它放进 **8h funding-window carry 策略** 里做 timing，而不是硬包装成纯 `5m/15m` standalone 机器。

## 5. 风险与保留意见
- **repo 自带结果当前并不赚钱。** 这是好事，不是坏事：它提醒我们别把“有完整工程壳”误判成“已验证 alpha”。
- **LSTM 零交易本身就是结论。** 对这种 post-cost 稀疏标签问题，复杂模型很可能先把自己交易掉没了，不一定比简单规则更可用。
- **短周期 portability probe 只证明“有回归”，不证明“扣成本后可交易”。** 这两件事必须分开。
- **当前 probe 只做了 BTC。** 若要升级为 desk candidate，下一步至少要看 `ETH/SOL`，以及 spot-perp 执行深度、maker fill 与 funding 结算窗附近的表现。
- **双腿策略的最大坑不是信号，而是成本和执行。** 如果不重做 execution，你会在看起来“命中率很高”的 1bp 级 edge 上被手续费慢慢吃死。

## 6. 下一步怎么测
1. **先做 friction ladder，而不是先调模型。**
   - 直接把短周期 probe 扩成 `2 / 4 / 6 / 8 / 10 bps` round-trip 成本阶梯，先回答：这条 alpha 在什么成本档位才活得下来。
2. **把 `positive funding` 从“并列条件”改成分层 admission。**
   - 先比较：`spread_z only`、`spread_z + funding>0`、`spread_z + funding percentile` 三档。
3. **把 entry timing 拉到 funding window 附近。**
   - 例如只测 funding 前后 `±60m / ±120m` 的 spread fade，看 carry 与 convergence 能否叠加得更厚。
4. **补 execution 现实。**
   - 至少做三档：`taker/taker`、`maker/taker`、`maker/maker proxy`；否则短周期测试意义有限。
5. **扩资产，但先只扩到 majors。**
   - 下一轮优先 `ETHUSDT / SOLUSDT`，不要一开始就铺满长尾。
6. **如果要保留 ML，只让它做排序，不让它定义 base alpha。**
   - 这类主题里，ML 更适合做 `rank / veto / sizing`，而不是替代 `perp rich spread fade` 本体。

## 7. 来源
1. **MengerWen (2026), _Deep Learning-Based Delta-Neutral Statistical Arbitrage on Perpetual Funding Rates_**  
   - Venue: GitHub repository / course-project prototype  
   - DOI: N/A  
   - Readable URL: `https://github.com/MengerWen/Deep-Learning-Based-Delta-Neutral-Statistical-Arbitrage-on-Perpetual-Funding-Rates`  
   - Repo URL: `https://github.com/MengerWen/Deep-Learning-Based-Delta-Neutral-Statistical-Arbitrage-on-Perpetual-Funding-Rates`
2. **Repo docs / reports actually used in this round**
   - README: `https://raw.githubusercontent.com/MengerWen/Deep-Learning-Based-Delta-Neutral-Statistical-Arbitrage-on-Perpetual-Funding-Rates/main/README.md`
   - Baselines doc: `https://raw.githubusercontent.com/MengerWen/Deep-Learning-Based-Delta-Neutral-Statistical-Arbitrage-on-Perpetual-Funding-Rates/main/docs/baselines.md`
   - Backtest doc: `https://raw.githubusercontent.com/MengerWen/Deep-Learning-Based-Delta-Neutral-Statistical-Arbitrage-on-Perpetual-Funding-Rates/main/docs/backtest.md`
   - Robustness report: `https://raw.githubusercontent.com/MengerWen/Deep-Learning-Based-Delta-Neutral-Statistical-Arbitrage-on-Perpetual-Funding-Rates/main/reports/robustness/binance/btcusdt/1h/report.md`
   - Robustness summary JSON: `https://raw.githubusercontent.com/MengerWen/Deep-Learning-Based-Delta-Neutral-Statistical-Arbitrage-on-Perpetual-Funding-Rates/main/reports/robustness/binance/btcusdt/1h/summary.json`
   - Data-quality summary JSON: `https://raw.githubusercontent.com/MengerWen/Deep-Learning-Based-Delta-Neutral-Statistical-Arbitrage-on-Perpetual-Funding-Rates/main/reports/data_quality/binance/btcusdt/1h/summary.json`
3. **本地 portability artifacts**
   - `/root/clawd/jerry/momentum/reports/artifacts/literature/binance_btc_spread_funding_portability_probe_summary_2026-04-11.csv`
   - `/root/clawd/jerry/momentum/reports/artifacts/literature/binance_btc_spread_funding_portability_probe_detail_2026-04-11.csv`

## 8. 数据源 / 公开性 / 更新频率 / 最小复现实验口径
- **repo 主数据口径：** Binance `BTCUSDT` hourly spot + perpetual + funding history
- **本轮 portability 数据源：** Binance 公共 `spot/perp klines + fundingRate`
- **公开性：** 公开，无需 API key
- **更新频率：**
  - K 线可到 `5m / 15m`
  - funding 每 `8h` 结算，但可作为慢变量 forward-fill 到更短 bar
- **最小可复现实验口径：**
  - asset：`BTCUSDT`
  - bars：`5m / 15m`
  - signal：`spread_z_96 > 1.5`
  - booster：`funding > 0`
  - evaluation：future spread convergence at `30m / 1h / 2h / 4h`
  - cost：先做 `2~10 bps` friction ladder
  - verdict：先判断它是 standalone 还是更适合做 funding-window timing / maker-assisted shell
