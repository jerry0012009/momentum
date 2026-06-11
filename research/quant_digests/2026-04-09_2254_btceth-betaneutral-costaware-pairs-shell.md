# 别把这份 BTC/ETH pairs repo 只读成 cointegration 课堂作业：对 crypto short-cycle desk，更该先测的是「spread fade × beta-neutral sizing / funding-aware cost shell」
- 时间：2026-04-09 22:54 UTC
- 类型：GitHub / source audit
- 主题类型：raw alpha
- 基础 alpha：BTC/ETH 协整 spread 偏离后的均值回归（cointegrated spread fade）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：pairs / stat-arb / relative value / mean reversion / beta-neutral / funding / cost / BTC / ETH
- 证据类型：工程经验 + repo source audit

## 1. 这次看了什么
这次看的是 `Bauch0430/crypto-pairs-trading-btc-eth`。我重点读了 `README.md`、`src/02_statistical_tests.py`、`src/03_strategy_engine.py`、`src/04_backtester.py`、`src/04b_backtester_beta.py`。这不是“再讲一遍 pairs 原理”的仓库，而是一份很适合 desk 拿来做 **成本诚实化 + sizing 对照** 的完整 BTC/ETH spread shell。

## 2. 核心结论
- **一句话核心结论：** 这份 repo 最值钱的不是“BTC/ETH 可以做 pairs”，而是它把一个老 raw alpha 明确拆成了 **signal 本体 vs sizing/cost/funding 壳**，并直接展示：**signal 不变，仓位方式一换，净 PnL 可以从 `-791.6 USD` 翻到 `+67.0 USD`**。
- **一句话证明方式：** README 给了同一套 entry/exit 信号下的对照：dollar-neutral 版本净 PnL 约 `-791.6 USD`，beta-neutral 版本约 `+67.0 USD`；源码还能对上 `β` 滚动估计、fee/slippage/funding 计入方式和状态机规则。
- 信号层很干净：`02_statistical_tests.py` 用 `1h` 数据生成 `rolling_beta`、spread、`adf_pvalue`、`median_half_life`；`03_strategy_engine.py` 只在 `|z| > 2.0` 且 `adf_pvalue < 0.05` 时开仓，`|z| < 0.5` 止盈，`|z| > 3.5` 止损，并在 **持仓时间 > `3 × median_half_life`** 时强制 time-stop。
- 最该抄的旁支不是“再加一个更花的均值回归指标”，而是 **beta-neutral sizing**：beta-neutral backtester 固定 BTC 目标名义敞口 `10,000 USD`，ETH 腿按滚动 `β` 调整，不再硬做双腿各 `5,000 USD`。这非常适合 BTC/ETH、BTC/SOL 这类高相关但 β 不稳定的 crypto pair。
- 成本模型也比常见 GitHub 作业诚实：`04b_backtester_beta.py` 里每腿 fee `0.06%`、slippage `0.02%`，而且 funding 直接并入净收益；README 汇总显示 beta-neutral 版本手续费仍有约 `-96.48 USD`，funding 约 `~-27 USD`，说明这条线不是“成本忽略后才成立”的幻觉。
- 但它也明确提醒：**raw alpha 还在，钱没赚到往往是壳层问题。** 对 short-cycle desk，这比再看一篇“pairs 有效”的泛论文更有用，因为它直接告诉你下一轮该先测 `hedge ratio / notional mapping / friction`，不是先继续炼 signal。

## 3. 为什么和当前项目有关
当前 desk 已经有不少 pairs / relative-value intake，但很多还停在“spread 有没有回归”这一步。这份 repo 的价值是把一个可独立复现的 raw alpha 再往前推半步：
- base alpha 仍是协整 spread fade；
- 但更适合我们 desk 的高价值旁支，是 **beta-neutral sizing + funding-aware post-cost accounting**；
- 这正好能服务于后续 `5m / 15m` 的 BTC/ETH、BTC/SOL、ETH/SOL spread 壳，而不是只在 1h 样本里做漂亮图。

所以这轮不是为了“再补一篇 pairs 入门”，而是为了补一个 **能直接提升 pairs admission / sizing / cost honesty** 的可复现组件。

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / market-neutral / mean reversion
- 基础 alpha：BTC/ETH 协整 spread 偏离后回归均值
- regime：`adf_pvalue < 0.05` 且 spread 仍有可交易 z-score 偏离
- filter / veto：`|z| > 2.0` 才开，`|z| < 0.5` 退出，`|z| > 3.5` 强制止损，持仓超过 `3 × median_half_life` 强制平仓
- risk / sizing / execution overlay：rolling `β` hedge ratio、beta-neutral notional mapping、每腿 `0.06%` fee + `0.02%` slippage、funding 并入净收益

## 4. 可复刻的最小实验
**研究假设：** 在 crypto pairs 上，short-cycle 成败经常不是由 spread signal 本身决定，而是由 **dollar-neutral vs beta-neutral sizing** 与成本记账方式决定。

**最小实验：**
1. 先只做 `BTC/ETH`，用 Binance 或 Bybit 公共 `15m` 数据替代 repo 的 `1h`；
2. 保留 repo 的骨架：rolling `β`、ADF、spread z-score、`entry=2.0 / tp=0.5 / sl=3.5`、time-stop=`3×median_half_life`；
3. 做两版完全同信号 A/B：
   - A：双腿固定等美元名义；
   - B：BTC 固定目标名义，ETH 腿按 rolling `β` 调整；
4. 手续费先按双腿 round-trip `16 bps` 起步，再单独记 funding。

**先看两项指标：**
- post-cost `bps/trade`；
- same-signal 条件下，beta-neutral 相对 dollar-neutral 的净收益差与最大回撤差。

## 5. 风险与保留意见
- 这份 repo 的主回测频率是 `1h`，不是直接为 `5m / 15m` 设计；它更像 **结构和记账壳**，不是现成可下场的 ultra-short strategy。
- BTC/ETH 本身是最“容易成立”的大对；若迁移到更快周期或更差流动性 pair，`β` 漂移、手续费、funding、借贷与最小下单量都会更伤。
- repo 的成功点偏“诚实的壳层对照”，不是证明 `ENTRY_Z=2.0` 这组参数在所有 venue/周期都稳。
- 如果 desk 后续把它压到 `5m`，最先该检查的不是 Sharpe，而是 `trade density × friction` 是否已经把 alpha 吃光。

## 6. 来源
- Bauch0430. (2026). *crypto-pairs-trading-btc-eth*. GitHub repository.
  - Repo URL: `https://github.com/Bauch0430/crypto-pairs-trading-btc-eth`
- Repo 内核心实现：
  - `src/02_statistical_tests.py`
  - `src/03_strategy_engine.py`
  - `src/04_backtester.py`
  - `src/04b_backtester_beta.py`
