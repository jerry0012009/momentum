# 别把这份 2026 `Crypto-Stat-Arb` 仓只读成“趋势系统也能一把梭”：对 short-cycle crypto desk，更该先回答的是「Donchian breakout × vol-target × ATR trail」这条完整 raw alpha 壳，离 `15m/5m` 还差几层

- 时间：2026-04-25 16:52 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `config/default.yaml` + `scripts/run_trend_strategy.py`）+ Binance USDⓈ-M public-data portability probe（`BTC/ETH/SOL/BNB`，`15m`）
- 主题类型：raw alpha
- 基础 alpha：**价格向上突破最近一段区间高点时，趋势更可能延续；向下跌破区间低点时，弱势也更可能继续。交易上对应 multi-asset breakout / trend-following，叠加波动率缩放、ATR trailing stop、long/short 非对称权重。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（repo 给了比较完整的壳；但更像 `4h` parent strategy，不应直接硬搬成 `15m` 主信号）
- 主题标签：raw-alpha/trend/momentum/breakout/donchian/vol-target/atr-trailing-stop/asymmetric-weighting/dynamic-universe/roll-slippage/4h/15m/5m/repo/public-data/cost/risk
- 证据类型：repo source audit + public-data portability probe

## 1. 先回答：这篇东西的 base alpha 是什么？
这次不是在讲“波动率目标”“止损”这种纯风控层。

**base alpha 很清楚：**
> 某个币如果向上突破最近一段区间高点，后面更容易继续顺着走；如果跌破区间低点，后面更容易延续下跌。再用 inverse-vol 做仓位分配，用 ATR trailing stop 控回撤。

所以它是 **raw alpha / 完整策略壳**，不是单纯 overlay。

---

## 2. 这次看了什么
主来源是 GitHub 仓 `Rah9742/Crypto-Stat-Arb`。这仓其实不只做 pairs，也有一条单独的 multi-asset trend strategy。最值得 desk 注意的不是“trend 赢了 pairs”这句 headline，而是它把一条 **breakout continuation** 壳，写成了可直接复跑的完整流水线：

- Author / Year / Title / Venue：Rah9742 (2026), *Crypto Trading Research Repo / Crypto-Stat-Arb*, GitHub repo
- Repo URL：<https://github.com/Rah9742/Crypto-Stat-Arb>
- Readable URL（README）：<https://raw.githubusercontent.com/Rah9742/Crypto-Stat-Arb/main/README.md>
- 关键配置：<https://raw.githubusercontent.com/Rah9742/Crypto-Stat-Arb/main/config/default.yaml>
- 关键入口：<https://raw.githubusercontent.com/Rah9742/Crypto-Stat-Arb/main/scripts/run_trend_strategy.py>
- 结果汇总：<https://raw.githubusercontent.com/Rah9742/Crypto-Stat-Arb/main/data/processed/costs/strategy_comparison.csv>

repo 自己给出的 trend 壳要点很明确：
- 标的：`BTCUSDT / ETHUSDT / SOLUSDT / BNBUSDT`
- 原始频率：`4h`
- train / validation / test：`60% / 20% / 20%`
- 信号骨架：`breakout_window_bars` + 可选 `trend_filter_ma_bars`
- 仓位：inverse-vol / cost-aware sizing
- 风控：`ATR trailing stop`
- 组合层：`gross_exposure_cap`、`long_weight_multiplier=1.25`、`short_weight_multiplier=0.75`
- 成本：repo 后处理里显式加入了 **Roll slippage**

---

## 3. 一句话结论
- **一句话核心结论：** 这份 repo 里真正值得记到素材池的，不是“4h 趋势策略收益高于 pairs”这句口号，而是它提供了一条很完整的 **multi-asset breakout / trend-following 壳**；但我把它直搬到 `15m` 做 public-data probe 后，结果是**全参数 net 都明显为负**，说明它更像 `4h` parent alpha，而不是可以直接下沉成 `15m` 主策略的现成答案。  
- **翻成人话：** repo 的策略骨架是好骨架，但 edge 大概率来自更慢时域；short-cycle desk 要拿的是“组件”，不是“结论”。

---

## 4. repo 自己是怎么证明它有效的
repo 已经把 trend 和 pairs 放在同一成本框架里比较。`strategy_comparison.csv` 给出的 trend 结果是：

- 测试区间：`2025-10-18 04:00:00+00:00 ~ 2026-03-23 00:00:00+00:00`
- 频率：`4h`
- gross return：**`107.21%`**
- net return：**`57.84%`**
- number_of_trades：**`58`**
- average_holding_horizon_bars：**`26.12`**（按 `4h` 算，大概是 `4.35` 天）
- total_transaction_cost_usdt：**`4936.40`**
- average_slippage_used：**`0.001198`**（约 `11.98 bps`）
- net_sharpe：**`1.53`**
- net_max_drawdown：**`-70.78%`**

最该注意的不是收益，而是这两个现实点：
1. **它不是低换手慢悠悠策略。** turnover 是 **`380.89x` 初始资金**；
2. **它也不是低回撤神话。** net max drawdown 仍然有 **`-70%` 级别**。

所以，这条线即使在 repo 自己的 `4h` 世界里，也更像“可研究、可拆壳”，不是“可直接无脑上线”。

---

## 5. 为什么这和当前 desk 有关
这条线值得进池，是因为它满足了 bot7 这轮最看重的两条：

1. **base alpha 清楚**：就是 breakout / trend continuation；
2. **完整策略壳齐全**：entry、exit、sizing、risk、cost 都能拆，不是只有一段理念。

但它对当前 short-cycle desk 的正确读法，不是“我们也去跑 15m breakout 就完了”，而是：
- repo 证明了 **骨架值得复用**；
- 我们需要重新判断 **哪一层可以下沉到 `15m/5m`，哪一层必须保留在更慢父级别**。

这比再看一篇只有 abstract、没有可执行实现的趋势论文更值钱。

---

## 6. 策略拆解（必填）
### Base alpha
- `Donchian / breakout continuation`：向上破最近高点做多，向下破最近低点做空，赌的是趋势继续，而不是均值回归。

### Regime
- 更适合单边 / 扩散阶段；横盘、假突破密集阶段容易被来回打脸。

### Filter / veto
- 可选长期均线方向过滤（repo 的 `trend_filter_ma_bars` 就是这层）；
- 也可以加“只做波动扩张而不是波动压缩后的假刺穿”这类 admission。

### Risk / sizing / execution overlay
- inverse-vol / cost-aware sizing；
- ATR trailing stop；
- 组合层 long/short 非对称配重；
- gross exposure cap；
- 成本一定要按 turnover 扣，不能只看方向对不对。

---

## 7. 我的最小 public-data portability probe（关键）
我补了一个 honest probe，把 repo 的趋势壳思路直接映射到 **Binance USDⓈ-M `15m`**，看看它离 desk 的默认时域到底还有多远。

### 7.1 数据与口径
- 数据源：Binance USDⓈ-M 公共 klines（无需私钥）
- 标的：`BTCUSDT / ETHUSDT / SOLUSDT / BNBUSDT`
- 区间：`2025-12-01 ~ 2026-04-25 16:45 UTC`
- 频率：`15m`
- 最小移植做法：
  - breakout window：`20 / 40 / 60`
  - MA filter：`none / 100 / 200`
  - vol window：`20 / 30`
  - inverse-vol 归一化
  - long 权重乘数 `1.25`，short 乘数 `0.75`
  - 一根延迟执行
  - turnover 成本：按 notional 变动粗扣 **one-way `4 bps`**
  - split：`60% / 20% / 20%`

### 7.2 结果（先说结论）
**全部参数组合在 validation / test 上都是负的。**

表现最“不差”的一组是：
- `breakout=60`
- `ma=200`
- `volwin=30`

但即便如此：
- validation 平均 **net `-0.955 bps/bar`**，Sharpe **`-10.06`**
- test 平均 **net `-1.274 bps/bar`**，Sharpe **`-18.56`**
- test 平均 turnover **`24.65%` / bar**
- test gross 也已经是 **`-0.288 bps/bar`**，说明**不是单纯被手续费吃死，信号本体在这套 `15m` 映射上也不对路**。

换句话说：
> 这不是“有 edge 但成本太高”，而更像“repo 的 `4h` breakout 逻辑下沉到 `15m` 后，信号结构本身就变味了”。

### 7.3 这组快检说明什么
这组 probe 对 desk 有三个直接启发：
1. **父级别 alpha ≠ 子级别 alpha。** 4h 上能活的 breakout，不代表 15m 上同样的 state machine 也能活；
2. **可以下沉的是 execution，不一定是信号。** 更合理的映射可能是：`4h/1h` 父级别信号 + `15m/5m` child execution；
3. **repo 最值得继承的是组件，不是参数。** ATR trail、asymmetric long-short weighting、cost-aware sizing 都值得留，但 15m 直接 breakout 不值得照抄。

---

## 8. 对当前 desk 的最有价值读法
所以这篇 digest 最该保留的不是“这仓回测赚了很多”，而是下面这句：

> **对 short-cycle crypto desk，这个 repo 更像 `trend parent shell`，不是 `15m` 原生 alpha。**

也就是说，当前最值得复用的是：
- `breakout` 作为慢级别方向锚；
- `MA filter` 作为方向 admission；
- `ATR trail` 作为风控模板；
- `long>short` 非对称配重；
- `Roll slippage / turnover` 这种诚实成本框架。

最不值得直接照搬的是：
- 把同一 breakout 逻辑原封不动下沉成 `15m` 主信号。

---

## 9. 最小实验怎么做
如果要继续追这条线，建议下一轮不要再做“15m breakout 裸跑”，而是做一个更像 desk 生产环境的实验：

- 父信号：`1h` 或 `4h` breakout + `200MA` 过滤
- 子执行：`5m / 15m`
- 触发方式：只在父级别方向已确立后，等子级别 pullback / micro-break / spread 收窄再进
- 成本：`2 / 4 / 6 bps` 三档
- 先看 3 个指标：
  1. 父信号方向正确率是否仍为正；
  2. child execution 是否显著降低 turnover；
  3. ATR trail 是否比固定 time-stop 更稳。

---

## 10. 下一步怎么测（必须）
下一步最值得直接测这 4 件事：

1. **改成 `4h signal -> 15m/5m execution` 的两层结构。**  
   不要再把 `15m` 当原生 breakout alpha；把它降级成 entry optimizer。

2. **只保留 long 侧，先砍 short。**  
   repo 已经用 `long_weight_multiplier=1.25`、`short_weight_multiplier=0.75` 暗示了非对称；short-cycle crypto 里 short breakout 更容易被反抽和 funding/crowding 搞坏。

3. **把 breakout admission 改成“扩散后首次回踩再续走”。**  
   也就是不要追第一下刺穿，而是测 `parent trend + child pullback continuation`，这比裸 Donchian 更符合 desk 当前时域。

4. **把 repo 的成本框架继续保留，但加入 maker/taker 分层。**  
   如果 child execution 能从纯 taker 变成 maker-leaning，这条父级别趋势壳才可能真正落到实盘。

---

## 11. 风险与边界
- 这条线当前**不是** `15m` 可直接上线的 raw alpha；
- 它目前更像一个 **慢级别趋势壳 + 快级别执行待优化任务**；
- repo headline 很好看，但 repo 自己的 drawdown 也很难看，所以别把它读成“趋势系统稳赢”；
- public-data probe 已经给出负 verdict，说明这轮的正确动作不是硬优化参数，而是先改层级结构。

---

## 12. 本地实验产物
- `reports/artifacts/quant_digests/2026-04-25_repo_trend_portability_probe.csv`
- `reports/artifacts/quant_digests/2026-04-25_repo_trend_portability_probe_top5.json`

如果后面要继续复现，这两个文件已经足够作为下一轮 `parent signal / child execution` 的起点。