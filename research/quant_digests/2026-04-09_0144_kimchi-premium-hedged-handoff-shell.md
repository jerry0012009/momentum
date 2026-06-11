# 别把这份 2026 韩国跨所 market-neutral 平台只读成“普通搬砖脚本”：对 short-cycle desk，更该先测的是 `negative KRW premium accumulation × positive-premium handoff exit`
- 时间：2026-04-09 01:44 UTC
- 类型：GitHub 仓库
- 主题类型：raw alpha
- 基础 alpha：同一币种的韩盘现货相对离岸永续出现**负溢价/低溢价**时做“韩盘现货多 + 离岸永续空”的对冲建仓，等待 premium 回归甚至转正后分批退出
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：relative-value / cross-market / kimchi-premium / spot-perp / delta-neutral / event-driven / 1m / 3m / 5m
- 证据类型：工程经验 / repo source audit

## 1. 这次看了什么
看的是 `sueun-dev/crypto-market-neutral-platform`。如果只看 README，很容易把它读成“跨所 cheapest-spot / richest-perp 搬砖”。但这次最该 intake 的，不是那条已经很熟的 basis 壳，而是仓库里单独拆出来的 **Korea redflag / exit workflow**：先盯 `KRW ask / USDTKRW / offshore perp bid` 算出的韩盘 premium，在韩盘相对便宜时做对冲建仓，等 premium 回归或转正后，把利润从韩盘退出腿兑现。

## 2. 核心结论
- 这份 repo 里真正新的 raw alpha，是 **negative KRW premium reversion**，不是方向预测。`premium_calculator.py` 直接把韩盘 ask、USDT/KRW、离岸 perp bid 拼成可交易 premium 指标。
- `hedge_bot.py` 明确把 entry / exit 写成完整壳：当 `premium <= -2.0%` 才开始建仓；单币上限 `3000 USD`，单次增量 `500 USD`；说明作者默认这是事件驱动的 premium 回归，而不是持续高频刷单。
- 出场也不是一句“等收敛”：`PROFIT_STAGES` 里给了 `0.5% / 2.1% / 3.2%` 三档止盈，对应 `50% / 10% / 100%` 退出，外加失败计数与对冲腿同步平仓逻辑，这就是完整策略，而不是因子备忘。
- 但它不是可直接迷信的参数真理：README 说海外 contango 例子看 `0.21%`，主配置却是 `0.15%`；`PROFIT_STAGES` 的注释与实际百分比还出现错位。结论不是“不能用”，而是**有清楚 alpha 壳，但复现前必须先审参数语义**。

## 3. 为什么和当前项目有关
这条线对我们有三个直接价值：
- 它补的是 **cross-market / relative-value / event-driven** raw alpha，而不是再做一遍 breakout 或普通 pairs；
- 数据公开、能落到 `1m/3m/5m`，很适合做最小实验；
- 它天然带着完整交易组件：signal、对冲、分批出场、失败重试、reduce-only unwind，都能直接拆成 desk 复现素材。

更直白地说：如果 desk 想补“不是单币趋势、也不是老式 z-score pairs”的 raw alpha，这种**韩盘/离岸同币价差回归**值得进池。

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / 跨市场 / delta-neutral
- 基础 alpha：韩盘现货相对离岸永续的 premium 从负值或低位向中性/正值回归
- regime：韩国本地需求升温、上币/转账预期、离岸 perp 可做空、USDT/KRW 口径稳定
- filter / veto：提币/入金状态异常、负 funding 过深、盘口太薄、韩盘溢价已过热、API/转账不可用
- risk / sizing / execution overlay：韩盘 spot 多 + offshore perp 空；`500 USD` 递增建仓；单币 `3000 USD` 上限；分档止盈；失败次数熔断；对冲腿同步 reduce-only 平仓

## 4. 可复刻的最小实验
- 研究假设：当 `kimchi_premium <= -2%` 时，随后 `1h ~ 3d` 内 premium 向 `0% ~ +3%` 回归的概率显著高于随机；若用离岸 perp 做空对冲，收益主要来自 premium 修复而不是币价方向。
- 一个可计算定义：
  `kimchi_premium_t = ((KRW_ask_t / USDTKRW_t) / offshore_perp_bid_t - 1) * 100`
- 最小回测切口：
  - 资产：`XRP / SOL / DOGE / USDC` 这类更容易出现韩盘挤压的标的；`BTC / ETH` 做对照组
  - 周期：先做 `1m` 事件流，再聚合到 `5m`
  - 样本：近 `90~180d`，优先覆盖韩国交易所上币、转账恢复、韩盘热度明显升温的窗口
  - 数据源：Upbit / Bithumb 现货报价、USDT/KRW 报价、Bybit / Gate / OKX / Binance perp bid 与 funding；这些都能用公开接口先做最小复现
- 先看 2 个指标：
  1. premium 从 `<= -2%` 回到 `0% / +0.5% / +2%` 的命中率与持有时长
  2. 费后、funding 后、转账假设后的净利润分布与最大不利扩张（premium MAE）

## 5. 风险与保留意见
- 这份仓库更像“流程写通了”的工程样板，不是已经证明稳健赚钱的论文证据。
- 真实难点不是公式，而是韩盘法币通道、提币限制、链上确认、汇率口径、以及对冲腿能否稳定减仓。
- premium 可能不是均值回归，而是**继续更负**：比如韩盘流动性抽干、离岸 squeeze、韩国本地风险偏好塌陷。
- 仓库里 README、config、注释之间有阈值不一致，复现时必须先统一参数真义，否则很容易“复现”出一个根本不是原意的系统。

## 6. 来源
- Sueun-dev. (2025/2026). *Crypto Market Neutral Platform*. GitHub.
  - Repo URL: `https://github.com/sueun-dev/crypto-market-neutral-platform`
  - README: `https://raw.githubusercontent.com/sueun-dev/crypto-market-neutral-platform/main/README.md`
- 核心实现：
  - `src/overseas_exchange_hedge/korea/redflag/core/premium_calculator.py`
  - `src/overseas_exchange_hedge/korea/redflag/core/hedge_bot.py`
  - `src/overseas_exchange_hedge/korea/redflag/config/settings.py`
  - `src/overseas_exchange_hedge/config.py`
  - `src/overseas_exchange_hedge/overseas/price_analyzer.py`
