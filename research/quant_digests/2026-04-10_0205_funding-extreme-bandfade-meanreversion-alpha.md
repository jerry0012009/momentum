# cross-exchange funding extreme × band-stretch fade shell
- 时间：2026-04-10 02:05 UTC
- 类型：GitHub repo source audit + Binance USDⓈ-M `5m/15m` portability probe
- 主题类型：raw alpha
- 基础 alpha：`extreme funding crowding × price stretch snapback`（极端 funding 代表拥挤持仓，若同时出现价格带外伸展，更容易短线回归）
- 是否可独立复现：是（可先用 Binance 单 venue funding 代理复现，再决定是否接 AiCoin 跨所加权 funding）
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / mean-reversion / funding / carry / positioning / perp / crowding / Bollinger / RSI / 5m / 15m / repo
- 证据类型：工程经验 + 公开数据 portability probe

## 1. 这次看了什么
这次主看 **enuno (2026) 的 GitHub 仓库 `hyperliquid-trading-firm`** 里 `skills/AIcoin-CoinOS/aicoin-freqtrade/strategies/FundingRateStrategy.py`。它不是把 funding 当“慢频 carry 收益”去拿，而是把 **极端 funding** 读成 **拥挤持仓过热/过冷的 crowding proxy**：当 funding 已经极端、价格又同时冲出 `BB(20,2)`、`RSI(14)` 也到极值，就去做一笔 **反身性 fade**。

源码给的是完整壳：`1h` 级别、可做多可做空、`BB20/2 + RSI14 + funding_threshold=0.013`（即约 `1.3bps` 的 funding 极值门槛），`price < lower band & RSI<35 & funding<-thr` 做多，反向条件做空；出场是回到 `bb_mid` 或 `RSI` 回到中性，另带 `minimal_roi` 与 `-12% stoploss`。高价值点不是它那张偏 swing 的 hyperopt ROI 表，而是：**把 funding 从“收 carry”改读成“做 crowding fade 的 regime-aware raw alpha”**。

## 2. 核心结论
- **一句话核心结论：** 这份 repo 最值钱的不是 funding carry，而是 **`funding 极端 + 价格带外伸展` 比裸 `BB+RSI` 反转更像能活下来的 `5m` crowding-fade raw alpha**。
- **一句话证明方式：** 我先审源码拿到可执行规则，再用 Binance 公共 funding + perp K 线做 `BB+RSI` 基线 vs `+ funding extreme gate` 的同壳对照。
- repo 原始设定本质是：**funding 负责回答“这波 stretch 有没有 crowding 背书”，BB/RSI 负责回答“价格是不是已经冲得够远可以 fade”**。这比把 funding 单独当方向信号要靠谱得多。
- 本地 `15m` 六个 liquid majors（`BTC/ETH/SOL/XRP/ADA/DOGE`，近约 `120d`）里，裸 `BB+RSI` 壳约 `1756` 笔、gross 约 `-8969bps`；加 funding extreme gate 后只剩 `155` 笔、gross 转成约 `+579bps`，但粗扣每笔 `8bps` round-trip 后仍约 `-661bps`。**结论：15m 上 gate 能去噪，但还不够让这条线稳过成本。**
- 本地 `5m`（近约 `90d`）更像 fast lane：裸 `BB+RSI` 壳约 `4072` 笔、gross 约 `+6619bps`，但扣 `8bps`/笔后约 `-25957bps`；加 funding gate 后只剩 `285` 笔、gross 约 `+4606bps`，扣成本后约 **`+2326bps`**，平均约 **`+16.2bps/笔 gross`**。**结论：对我们 desk，更像先上 `5m`，不要先上 `15m`。**
- `5m` 正贡献主要集中在 **ETH / ADA / DOGE**：粗扣 `8bps` 后约分别剩 `+1353 / +1076 / +720bps`；`BTC / XRP` 仍偏弱，说明这条线更像 **alt-perp crowding fade**，不是全市场统一模板。
- 公开 Binance 单 venue funding 的正 funding 上沿通常只到约 `0.7~1.0bps`，比 repo 默认 `1.3bps` 更温和；也就是说 **AiCoin 跨所加权 funding 可能比单所 funding 更极端、更有信号密度**。当前 portability probe 是保守口径，不是满配复刻。

## 3. 为什么和当前项目有关
这条线对 `momentum` 当前阶段有直接价值，因为它补的是 **raw alpha 素材池里的“crowding-conditioned mean reversion”**，而不是又一个泛 filter：
- 它和我们前几轮的 funding carry / basis 线形成互补：**同样看 funding，一条是“收 carry”，另一条是“拥挤过头就 fade”**。
- 它很适合 desk 的 `1m/3m/5m/15m` 节奏：funding 是慢锚，`BB/RSI/stretch` 是快触发。
- 它天然能拆成两个组件：`base alpha = stretch fade`，`funding = crowding admission gate`；这比直接抄一整套黑盒更利于后续复现与组合。

## 3.5 策略拆解（必填）
- 方向属性：逆势 / crowding fade
- 基础 alpha：`极端 funding 下的价格过冲更容易短线回归`
- regime：perp 持仓明显拥挤、funding 达到符号极端时
- filter / veto：`BB(20,2)` 带外 + `RSI(14)` 极值；后续可再加“只做 alt、排除 BTC/XRP”或“只做 funding 绝对值前 decile”
- risk / sizing / execution overlay：next-bar open 入场；回到 `bb_mid` 或 `RSI≈50` 出场；先按 `8bps` round-trip 成本验活；若要实盘再加 funding 结算时点、持仓上限、单币 kill-switch

## 4. 可复刻的最小实验
- **研究假设：** `BB+RSI` 裸反转太容易被趋势碾；若只在 funding 极端时做，会把“普通回调”筛掉，留下“拥挤过冲后的 snapback”。
- **一个可计算定义：**
  - `stretch_long = close < BB20_lower and RSI14 < 35`
  - `stretch_short = close > BB20_upper and RSI14 > 65`
  - `funding_extreme_long = funding <= rolling_q05`，`funding_extreme_short = funding >= rolling_q95`
  - 入场：`stretch ∩ funding_extreme` 后下一根开盘
  - 出场：回到 `SMA20 / bb_mid` 或 `RSI` 回到 `50`，否则 `12` 根 bar time-stop
- **最小回测切口：** Binance USDⓈ-M `BTC/ETH/SOL/XRP/ADA/DOGE`，先跑 `5m` 近 `90d`，再跑 `15m` 近 `120d`；先用单 venue funding，后续再替换成跨所加权 funding。
- **最该先看 2 个指标：**
  1. `post-cost bps/trade`（别只看 gross）
  2. `trade_count retention`（gate 把多少噪音交易砍掉）

## 5. 风险与保留意见
- repo 真正依赖的是 **AiCoin 跨所 funding**；当前 portability 只用 Binance 单 venue funding，属于保守代理。
- funding 本身是慢变量，所以这条线更像 **gate + trigger** 的组合，不是逐 bar 独立主信号；别把它伪装成高频纯 price alpha。
- repo 的 `minimal_roi` 很 swing，**不建议原样搬到 short-cycle desk**；当前更该复用的是 entry logic 与 mean-revert exit 逻辑。
- `BTC / XRP` 转移效果偏弱，说明这条线不该无脑全市场铺开，最好先做 **alt-heavy universe** 或按 symbol 分层阈值。

## 6. 来源
1. **enuno. (2026). _hyperliquid-trading-firm_. GitHub repository.**
   - Repo URL: `https://github.com/enuno/hyperliquid-trading-firm`
   - Strategy file: `https://raw.githubusercontent.com/enuno/hyperliquid-trading-firm/main/skills/AIcoin-CoinOS/aicoin-freqtrade/strategies/FundingRateStrategy.py`
   - AiCoin integration README: `https://raw.githubusercontent.com/enuno/hyperliquid-trading-firm/main/skills/AIcoin-CoinOS/README.md`
2. **Binance USDⓈ-M public data / APIs**
   - Funding history: `https://fapi.binance.com/fapi/v1/fundingRate`
   - Perpetual klines: `https://fapi.binance.com/fapi/v1/klines`
3. **本地 portability artifact**
   - `reports/artifacts/literature/funding_meanreversion_gate_portability_2026-04-10.csv`
