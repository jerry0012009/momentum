# perp funding vs dated basis carry shell
- 时间：2026-04-10 13:37 UTC
- 类型：GitHub repo + 本地复跑 / 快检
- 主题类型：raw alpha
- 基础 alpha：`正 funding 持续时，做 long spot + short perp 的 delta-neutral carry；若要比替代腿，则比较 perp funding carry 与 dated futures basis carry`
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：carry / funding / basis / delta-neutral / execution / cost / BTC / ETH / 15m / 8h
- 证据类型：工程证据 + 本地复跑 + 公共数据快检

## 1. 这次看了什么
看的是 `zwmjj/funding-rate-arb`（2026 GitHub repo）。我重点审了 `src/backtest.py`、`src/basis_trade.py`、`results/backtest_default_metrics.csv`、`results/basis_vs_funding_summary.csv`，并在本地直接跑了 `python3 src/backtest.py`。它最值钱的地方不是“funding 很高时价格会跌”，而是把 **carry 本体** 写成了完整可执行壳：`8h funding > entry` 开 `long spot + short perp`，`funding < exit` 平仓，成本先按双腿 taker round-trip `16bps` 扣掉。

## 2. 核心结论
- **一句话核心结论**：这份 repo 更适合我们 desk 当作一条独立的 `carry / funding / basis` raw alpha，而不是再把高 funding 硬读成短线反转信号。
- **一句话证明方式**：作者直接用 Binance `spot / perp / funding / quarterly futures` 历史数据做规则回测，并把 entry/exit 阈值、费用、暴露比例和季度期货对照都写出来了。
- repo 默认参数 `entry=1bp / exit=0.5bp / taker=4bps per side` 下，`BTC` 约 `16` 笔、暴露 `31.7%`、年化 `9.0%`、最大回撤 `-0.34%`、平均持有 `25d`；`ETH` 约 `12` 笔、暴露 `36.9%`、年化 `11.2%`、最大回撤 `-1.8%`、平均持有 `39d`。
- repo 自带 EDA 里，`BTC/ETH` 的 `8h` funding 均值约 `1.13 / 1.34 bps`，折年化约 `12.3% / 14.7%`，偏度约 `3.32 / 3.37`，负 funding 仅约 `13.5% / 13.1%`；说明 carry 主要来自少数高 funding 时段，不是全天候均匀收租。
- repo 的对照摘要里，`BTC` dated quarterly basis 平均只约 `4.26%` 年化，明显低于 repo 样本里的 `BTC funding carry 12.32%`；所以对当前 desk，更该先把 **perp funding carry** 当主书，quarterly basis 当替代腿/切换对照，而不是反过来。
- 我用 repo 自带原始 CSV 做了一个最小 sanity check：按 funding 分位分组后，`BTC` 的高 funding 组未来 `1/3/7` 个 `8h` spot 回报约 `+0.12% / +0.38% / +0.00%`，不是稳定负收益；`ETH` 的高 funding 组未来 `1/3/7` 个 `8h` 回报约 `+0.47% / +0.67% / +1.29%`。对我们最重要的含义是：**不要默认给 carry 书叠一个“高 funding 必反转”的方向 overlay。**

## 3. 为什么和当前项目有关
这轮虽然不是 `5m` 逐根方向信号，但它仍是当前优先级很高的 **raw alpha**，因为 `carry / funding / basis` 本来就是允许优先补齐的家族，而且这份 repo 给的是完整策略骨架，不是综述。对短周期 desk 的真正价值不在“把 8h 信号伪装成 5m alpha”，而在三点：
1. 给出一条可独立运行的低换手 raw book；
2. 让 `15m` 执行层去处理 funding 边界前后的开/平仓、滑点与替代腿选择；
3. 给现有 crowding / funding fade 线一个**正向 carry 对照组**，避免我们只研究“高 funding 该反着做”。

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / carry / delta-neutral
- 基础 alpha：`正 funding 持续 -> short perp earns carry against long spot`
- regime：`正 funding 占优、basis 未明显反向恶化、费用后仍有净 carry`
- filter / veto：`funding <= entry threshold`、`basis 过窄`、`预估成本吃掉 carry`、`季度合约相对更优时切腿`
- risk / sizing / execution overlay：`1:1 notionals`、暴露上限、funding boundary 前后 `15m` 执行、roll/再入场节奏、双腿 taker/slippage 成本校验

## 4. 可复刻的最小实验
- 研究假设：`perp funding carry` 在 BTC/ETH 上是独立 raw alpha，但信号频率是 `8h`，`15m` 的角色应是 execution / switch layer，而不是伪装成逐 bar 方向预测。
- 一个可计算定义：每个 `15m` bar 读取最近一次 funding 状态；若下一次可收 funding 的年化阈值折算后仍 `> 1bp / 8h`，开 `long spot + short perp`；若掉到 `< 0.5bp / 8h` 则平。再加一个 `basis_switch = quarterly_basis > perp_expected_carry + fee_buffer` 的替代腿判断。
- 最小回测切口：`BTC/ETH`，先用 Binance 公共 `spot / perp funding / quarterly futures`，样本先抓近 `12~24` 个月；信号按 `8h` 更新，但执行统一落到 funding 时间戳前后的 `15m` bar。
- 最该先看：`成本后年化 carry`、`capital utilization / 暴露比例`；第二组再看 `max drawdown`、`threshold flatness`、`perp vs quarterly` 切换前后增益。

## 5. 风险与保留意见
- 这不是 `1m/5m` 高频 alpha，若硬把它包装成逐 bar 信号，会失真。
- repo 的 basis 对照部分我本轮主要核对了源码与提交结果文件，没有在本机完整重跑 `ccxt` 拉取链路；因此 dated-futures 这块证据强度略低于 funding backtest 本体。
- carry 书最怕的是：资金费突然塌陷、双腿执行摩擦、借贷/划转成本、季度合约换月，以及“样本里 2021/2024 好、2025+ 变弱”的 regime 退化。
- 所以它更像 **独立低换手 carry sleeve**，不该替代现有 `5m/15m` trend / MR 主书。

## 6. 来源
- zwmjj. (2026). *funding-rate-arb*. GitHub.
  - Repo URL: `https://github.com/zwmjj/funding-rate-arb`
  - 审计文件：`src/backtest.py`、`src/basis_trade.py`、`results/backtest_default_metrics.csv`、`results/basis_vs_funding_summary.csv`
- 数据口径：Binance `spot / perpetual funding / quarterly futures`，repo 通过 `ccxt` 拉取并保存到 `data/raw/`
