# 别把这份 Polymarket fast-loop 仓只读成“5 分钟追涨 bot”：对 short-cycle desk，更该先回答的是「Binance 5m impulse × Polymarket odds lag」这条跨 venue raw alpha 壳

- 时间：2026-04-26 00:55 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `fastloop_trader.py` + `config.json`）+ Binance USDⓈ-M public-data portability probe（`BTCUSDT`，`1m`，近约 `15000` 根 bars）
- 主题类型：**raw alpha**
- 基础 alpha：**当 Binance 上的 BTC 在最近 `5m` 出现足够强的单边动量，而 Polymarket 的 `5m/15m` fast market YES/NO 价格还没同步反映这段 move 时，做跨 venue 的“慢腿补价”交易。**
- 是否可独立复现：**是**
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：**是，但只能在“快源头 + 慢执行 venue”框架下成立，不能把它误读成同 venue 追涨模板。**
- 主题标签：raw-alpha / cross-venue / lead-lag / intraday / momentum / latency-arb / polymarket / binance / binary-market / 1m / 5m / 15m / repo / public-data / cost / risk
- 证据类型：工程经验

## 1. 这次看了什么
这轮主材料是 **Simmer / angganurf (2026)** 的 GitHub repo：
**`Automate-Polymarket-bot-BTC-5-15-min`**。

它表面上像一个“拿 Binance 动量去打 Polymarket fast market”的交易脚本，但真正对 desk 有价值的，不是“5 分钟涨了就买 YES”这句口号，而是更具体的一句：

> **这是一条跨 venue lead-lag 壳：`Binance` 负责提供快价格发现，`Polymarket` 负责提供慢一点的赔率调整。**

repo 默认逻辑很直接：
1. 找到当前活跃的 `BTC` fast market（`5m` 或 `15m`）；
2. 读取 Binance 最近 `5` 根 `1m` K；
3. 计算最近 `5m` 动量；
4. 若动量超过阈值，且 Polymarket 当前 YES/NO 价格还没跟上，就下单；
5. 还加了 `max_position`、`min_time_remaining`、`volume_confidence` 这些实盘壳。

## 2. 一句话核心结论
**这份 repo 最值得保留的不是“在 crypto 上追 5m 动量”，而是一条更窄但更诚实的 raw alpha：`快 venue 的短时价格发现 -> 慢 venue 的赔率/价格补反应`。**

## 3. 它是怎么证明这件事的
repo 的 README 和主脚本把策略写得很明白：
- 默认信号是 **Binance `BTCUSDT` 最近 `5m` 动量**；
- 默认最小触发是 `min_momentum_pct`，README 写 `0.5%`，仓库 `config.json` 当前示例改成了 `0.2%`；
- 只在 **Polymarket fast market** 剩余时间还够的时候做（默认 `>60s`）；
- 还会看 `volume_confidence`，也就是 Binance 成交量是否支持这段 move；
- 交易对象不是 Binance 本身，而是 **Polymarket 的二元 YES/NO 合约**。

换句话说，这个仓真正下注的不是“BTC 还会不会继续涨”，而是：
**“Polymarket 这边的赔率来不来得及补上 Binance 已经发生的价格变化。”**

## 4. 为什么和当前项目有关
这条线对当前 desk 有两个直接价值：

1. **它是完整 raw alpha 壳，不只是 filter。**
   有明确的 `source venue -> target venue -> entry -> timing -> sizing -> cost`。

2. **它提醒我们别把跨 venue lead-lag 错看成同 venue continuation。**
   这对 `1m/3m/5m` 研发很关键：
   - 在**慢 venue**上，它可能是可交易 raw alpha；
   - 在**快 venue 本体**上，它未必是 continuation，甚至可能刚好相反。

## 5. 这轮 portability 快检：同 venue 直接追，并不好
我补了一个最小诚实快检：
- 标的：`Binance USDⓈ-M BTCUSDT`
- 频率：`1m`
- 样本：最近约 **`15000` 根 bars**（`2026-04-15 14:53 UTC` 到 `2026-04-26 00:52 UTC`）
- 事件：最近 `5m` 累计收益达到 repo 近似阈值（主看 `|ret_5m| >= 0.20%`）
- 评估：按事件方向看后续 `1m / 3m / 5m` signed forward return

结果并不支持“在 Binance 自己身上继续追”：
- `|ret_5m| >= 0.20%` 时，共 **`1120`** 次事件；
- 后续 `1m` 平均 signed return 约 **`-0.49 bps`**；
- 后续 `3m` 约 **`-0.51 bps`**；
- 后续 `5m` 约 **`-0.17 bps`**；
- 若再加 `vol_ratio >= 1.0`，后续 `5m` 才勉强转成 **`+0.11 bps`**，但样本仅 **`754`** 次，而且中位数仍约 **`-1.49 bps`**。

这说明一个关键点：

> **repo 的 edge 不是“Binance 5 分钟动量在 Binance 上还会继续跑”；它更像“Binance 先跑完后，Polymarket 这条慢腿还没完全补价”。**

这也正是它值得单独进研究池的原因：**base alpha 很清楚，但适用 venue 很窄。**

## 6. 策略拆解（必填）
- 方向属性：跨 venue / lead-lag / event-driven momentum
- 基础 alpha：快 venue 已发生的短时价格发现，会领先慢 venue 的赔率更新
- regime：高波动、新闻驱动、fast market 流动性还在、且剩余时间足够时更友好
- filter / veto：剩余时间阈值、Binance 成交量确认、Polymarket fee / spread / depth veto、事件前后黑名单
- risk / sizing / execution overlay：单事件最大下注、临近到期不追、滑点和 10% fee 预算、同窗口只打一笔或设 cooldown

## 7. 下一步怎么测
### 最小实验 A：做真正的跨 venue first verdict
- 数据：Binance `1m` + Polymarket fast market 历史 YES/NO quotes
- 事件：`5m` 累计涨跌幅超过 `0.15% / 0.20% / 0.25%`
- 目标：看 Polymarket odds 在后续 `30s / 60s / 120s` 的跟随幅度
- 先看：`avg edge after fee`、`hit rate`、`time-to-convergence`

### 最小实验 B：别把它误接到 CEX 追涨模板
- 同样的 `5m` impulse，直接在 Binance 上做 continuation vs 做短时 fade
- 看 `1m / 3m / 5m` 哪边更稳
- 如果同 venue 更像反转，那这条信号就该被标成：**跨 venue 执行专用，不得拿去做单 venue 趋势主信号**

### 最小实验 C：推广到 `ETH` / `SOL` fast markets
- 保留相同结构，只换 signal source 和 target market
- 对比：BTC 是否只是因为信息密度高，还是这类 binary fast market 普遍存在补价滞后

## 8. 风险与保留意见
1. **Polymarket 10% fee 很重。** README 也明确写了 fast market 有高费率，很多小 edge 会被直接吃掉。
2. **这不是 24/7 深流动 CEX。** 若 book 很薄、剩余时间太短，理论 edge 可能来不及兑现。
3. **同 venue portability 很差。** 我这轮 Binance 快检已经提示：把它硬翻译成 CEX `1m/5m` continuation 会踩坑。
4. **历史回测门槛在 target venue。** 真正要定量验证，关键不是 Binance 数据，而是 Polymarket minute/sub-minute quote 历史能否稳定补齐。

## 9. 我对这条线的判断
这轮最值得记住的一句不是“5 分钟涨了就买 YES”，而是：

> **先区分“alpha 来自价格继续走”，还是“alpha 来自另一条慢腿还没跟上”。这份仓明显属于后者。**

所以它对当前 desk 的价值，不是变成下一条 Binance 主策略，而是：
- 给研究池补一条**跨 venue lead-lag raw alpha 壳**；
- 逼我们把 `source venue` 和 `execution venue` 分开思考；
- 顺手提醒：很多看起来像 momentum 的东西，落回同 venue 后其实更像 **micro mean reversion / chase-veto**。

## 10. 文件与页面
- 研究笔记：`research/quant_digests/2026-04-26_0055_binance5m-polymarket-oddslag-shell.md`
- Probe summary：`reports/artifacts/quant_digests/2026-04-26_fastloop_binance_momentum_probe_summary.csv`
- Probe events：`reports/artifacts/quant_digests/2026-04-26_fastloop_binance_momentum_probe_events.csv`
- 预期页面（发布后）：<https://jp.jerrypsy.top/momentum/reading/quant_digests/2026-04-26_0055_binance5m-polymarket-oddslag-shell.html>
- 索引页：<https://jp.jerrypsy.top/momentum/reading/quant_digests/report.html>

## 11. 来源
1. **Simmer / angganurf. (2026). _Automate-Polymarket-bot-BTC-5-15-min_. GitHub.**
   - Repo URL: <https://github.com/angganurf/Automate-Polymarket-bot-BTC-5-15-min>
   - README: <https://raw.githubusercontent.com/angganurf/Automate-Polymarket-bot-BTC-5-15-min/main/README.md>
   - Main script: <https://raw.githubusercontent.com/angganurf/Automate-Polymarket-bot-BTC-5-15-min/main/fastloop_trader.py>

2. **Binance USDⓈ-M Futures public klines**
   - API docs: <https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data>

3. **Polymarket Gamma API / fast market discovery path**
   - Gamma host used in repo: <https://gamma-api.polymarket.com/markets>
