# 别把这份 crypto momentum repo 只读成“扫涨幅榜追强势”：对 short-cycle desk，更该先测的是「ATR-switched price-velocity × volume-expansion breakout shell」
- 时间：2026-04-08 09:25 UTC
- 类型：GitHub / source audit
- 主题类型：raw alpha
- 基础 alpha：**顺势突破 / continuation**；更具体地说，是 **按市场 ATR 状态切换观察窗后，去抓短窗 price velocity 超阈值且成交量同步扩张的 breakout 延续**。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：trend / momentum / breakout / price-velocity / volume-expansion / ATR / regime-switch / execution / risk
- 证据类型：工程经验 / 源码证据

## 1. 这次看了什么
这次主看 **yeshunyi, _crypto-momentum-strategy_** 这份 GitHub repo。我没把它当“又一个追涨脚本”，而是直接按 desk 语言拆：**base alpha 不是简单涨幅榜，而是“市场越热，观察窗越短；在对应短窗里，价格速度进入有效区间、成交量同步放大、且不是极端过热时，去吃 breakout 后的继续走强”**。核心证据来自 `README.md`、`signal_generator.py`、`market_analyzer.py`、`momentum_strategy.py`、`risk_manager.py` 的 source audit，而不是只看 README 口号。

## 2. 核心结论
- **一句话核心结论：** 这份 repo 真正值得 desk 抄的，不是“追涨排行榜”，而是 **ATR 切换的短窗 velocity breakout + volume expansion + staged execution** 这条完整 raw alpha 壳。
- **一句话它怎么证明：** 源码把 entry/exit/risk 拆得很具体：`market_analyzer.py` 里先按市场 ATR 选 `15m/10m/5m` 观察窗与涨幅阈值；`signal_generator.py` 再要求 `momentum` 落在对应阈值带内、`volume_ratio > 1.5`、`RSI < 75`、且币种属于 top-3 热门板块；`momentum_strategy.py` 再做 `50%` 首单 + 突破前高后补 `50%`，并用分段止盈/止损收口。
- 代码里最值钱的 3 个具体数：**ATR<2% 时用 `15m` 窗口抓 `6%~10%` 涨速；ATR 在 `2%~5%` 时改成 `10m / 4%~8%`；ATR>5% 时再缩到 `5m / 3%~6%`**。这不是固定 lookback breakout，而是显式做 volatility-switched admission。
- entry 不是一把梭：首笔先上 `50%`，第二笔要等 **再破前高** 才补；profit target 取 `min(1.5 × ATR%, 10%)`，仓位初始止损写成 `-2%`，分三段在约 `0.8x / 1.0x / 1.2x` 目标位各卖 `30% / 30% / 40%`。
- 这条线和普通 Donchian 的差别在于：**它赌的不是“创 N 日新高”，而是“单位时间内的价格速度进入可交易区间后，短期资金还会继续推”**；volume ratio 与 RSI 更像 veto，不是 alpha 本体。

## 3. 为什么和当前项目有关
这条线对当前 `1m / 3m / 5m / 15m` desk 有直接价值：
- 它补的是 **单资产 raw alpha**，而不是又一个 filter-only 主题；
- 它和我们最近 intake 的相对价值 / pairs / basis 材料互补，能把 raw alpha 池重新往 **trend / breakout / continuation** 拉回来；
- 它比常见 breakout 更适合快实验，因为核心变量就 3 组：**观察窗、velocity threshold、volume expansion gate**；
- 更重要的是，源码已经把它拆成了可以移植的组件：`base alpha`、`regime switch`、`second-stage add-on`、`risk shell`。

## 3.5 策略拆解（必填）
- 方向属性：顺势 / breakout continuation
- 基础 alpha：ATR 切换后的短窗 price-velocity breakout
- regime：按市场 ATR% 决定用 `15m/10m/5m` 哪个窗口，以及对应的 momentum band
- filter / veto：`volume_ratio > 1.5`、`RSI < 75`、热门板块 top-3、非强熊市、黑名单约束
- risk / sizing / execution overlay：首单 `50%` + 突破前高再补 `50%`；初始止损约 `-2%`；目标位 `min(1.5 × ATR%, 10%)`；分段止盈 `30/30/40`；并发仓位受风控器限制

## 4. 可复刻的最小实验
**研究假设：** 短周期 crypto 的 breakout 不是固定 lookback 越短越好，而是 **观察窗和阈值要跟市场波动一起切换**；否则低波动期信号太慢，高波动期又全是噪音追涨。

**最小定义：**
1. 标的：Binance/OKX top 20 liquid perp，先测 BTC/ETH/SOL/BNB 四个大币，再扩成截面；
2. 主周期：`5m` 与 `15m`；更快版可把输入从 `1m` 聚合到 event window；
3. regime switch：用 BTC 或全市场中位数 `ATR%` 做状态；
4. signal：
   - 若 `ATR% < 2`：看近 `15m` 收益，入选区间 `6%~10%`；
   - 若 `2 ≤ ATR% ≤ 5`：看近 `10m` 收益，入选区间 `4%~8%`；
   - 若 `ATR% > 5`：看近 `5m` 收益，入选区间 `3%~6%`；
   - 同时要求 `volume_ratio > 1.5`、`RSI(14) < 75`；
5. 执行：先 `50%` 在下一根开盘入，余下 `50%` 仅在再破 signal bar 前高时加仓；
6. 出场：先照 repo 壳用 `-2%` stop + `min(1.5×ATR%,10%)` target，外加分段止盈；
7. 成本：至少打 `8 / 12 / 20 bps` 三档 round-trip，别把 README 风格策略当成免成本。

**先看两件事：**
- `post-cost expectancy / trade` 是否明显优于裸 `fixed-window breakout`；
- 假突破率是否因为 **stage-2 只在再破前高才补仓** 而显著下降。

## 5. 风险与保留意见
- 这是 **repo 源码证据**，不是论文证据；它更像可快速 intake 的工程原型，不是已经被长样本验证的硬结论。
- 当前审到的核心文件里，README 讲得更丰满（比如更泛的题材轮动叙事），但真正落地的 hard rule 主要还是 `ATR / volume / RSI / top sector / staged execution`；**不要把 README 里所有叙事都当成已接入数据流**。
- `6%~10% / 4%~8% / 3%~6%` 这种绝对涨速阈值对不同币种和不同交易所未必稳，落地时更建议先转成 **ATR multiple / volatility multiple**。
- repo 没有把 fee / slippage / queue position 写成正式成本模型，所以“是否可直接落地完整策略”我给 **否**；它更适合先做 raw alpha first verdict，再补 execution realism。

## 6. 来源
1. **yeshunyi. _crypto-momentum-strategy_. GitHub repository.**  
   Repo URL: `https://github.com/yeshunyi/crypto-momentum-strategy`
2. **核心源码：** `signal_generator.py` / `market_analyzer.py` / `momentum_strategy.py` / `risk_manager.py`  
   Raw URL base: `https://raw.githubusercontent.com/yeshunyi/crypto-momentum-strategy/main/`
3. **说明文档：** `README.md`  
   Raw URL: `https://raw.githubusercontent.com/yeshunyi/crypto-momentum-strategy/main/README.md`
