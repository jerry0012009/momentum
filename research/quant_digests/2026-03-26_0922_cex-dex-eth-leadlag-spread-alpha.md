# 别把 ETH 的 CEX/DEX price discovery 只读成市场结构：更该先测的是「Binance 冲击 → Uniswap 5m 补动」same-asset relative-value raw alpha
- 时间：2026-03-26 09:22 UTC
- 类型：论文
- 主题类型：raw alpha
- 基础 alpha：同资产跨 venue lead-lag；当 Binance 先走、DEX 当下跟得不够时，后续 1 根 `5m` 上存在 DEX 补涨补跌
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / relative-value / lead-lag / price-discovery / cex / dex / eth / uniswap / binance / intraday / 5m / 15m / event-driven
- 证据类型：论文证据 + 公共数据最小快检

## 1. 这次看了什么
主线是 **Plazuelo Pascual, Tardón Rubio, Toro Cebada, Hernando Veciana (2025), _Price Discovery in Cryptocurrency Markets_**。它对 desk 最值钱的读法，不是“CEX 更有效”这句结构判断，而是：**既然 ETH 在 Binance 往往先动，能不能把 DEX 的滞后补动写成短持有 relative-value raw alpha**。我又用 **Binance `ETHUSDT` 公共 `5m` K 线 + GeckoTerminal 的 Uniswap WETH/USDT 公共 `5m` OHLC** 做了一个最小快检，确认这条线在当前数据上仍然像是可测的 pocket，而不只是旧样本故事。

## 2. 核心结论
- **一句话结论**：这篇材料更值得 intake 的不是“CEX/DEX 谁更先进”，而是 **CEX 冲击后 DEX 的短时补动**，这是可直接写成入场/出场/成本口径的 same-asset raw alpha。
- **一句话它怎么证明**：论文用 Binance vs Uniswap 的 **cointegration + Hasbrouck information share + Gonzalo-Granger + Hayashi-Yoshida** 做长期与事件窗分析；我这边再用当前公开 `5m` 数据做了一个轻量 shock→catch-up 快检。
- 论文长期样本里，ETH **centralized market information share 约 0.982–0.999**，DEX 只有 **0.001–0.018**；不是“五五开”，而是明显由 CEX 主导价格发现。
- 在论文的高波动事件窗里，这种主导关系仍在：例如 **2024-03-05**，CEX 的 Hasbrouck share 约 **0.959/0.966**，Hayashi-Yoshida **LLR=1.86**，说明不是只在平静期成立。
- 但论文也提醒：**不要把它天真写成 DEX 现货双边 arb 印钞机**。同样在 `2024-03-05`，作者估算 gas 后最优案例也只有 **+$0.11**，全窗口平均反而约 **-$45.3**，说明执行成本会直接吃掉表面价差。
- 我用当前公开 `5m` 数据做的最小快检（2026-03-22 至 2026-03-26 UTC）里，若定义“Binance `5m` 冲击 z>2 且 DEX 当根少跟至少 30%”为事件，共得到 **22 个 pocket**；其中 **95.5%** 的事件在下一根 `5m` 上 DEX 继续朝 Binance 冲击方向补动，**平均 signed next-bar move ≈ 16.4 bps**，且 **next-bar spread close ratio 中位数约 49%**。这说明对 desk 来说，先别急着做链上双腿，先把它当 **可验证的 lead-lag raw alpha 口袋** 更合理。

## 3. 为什么和当前项目有关
- 这不是又回到 breakout / retest 内循环，而是明确补充 **same-asset relative-value / stat-arb** 素材池。
- 它和我们最近写过的 **BTC futures→spot**、**ETF→BTC** lead-lag 一样属于“谁先动、谁后补”的家族，但这里换成 **CEX vs DEX**，补齐了跨 venue 价格发现这一支。
- 对当前 `1m/3m/5m/15m` 研发最实用的 desk 化读法是两层：
  - **双 venue 账户可做完整 raw alpha**：long lagging DEX / short leading CEX（或反向）；
  - **CEX-only desk 可先当 shared gate**：当 DEX 明显未补完时，不急着追反向，先等补动或拿来确认 leader 冲击是否还在扩散。

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / lead-lag
- 基础 alpha：Binance 先动后的 Uniswap 滞后补动
- regime：ETH 波动抬升、CEX 冲击足够大、DEX 当根未同步、美国时段或风险事件窗口优先
- filter / veto：leader shock 必须 `z > 2`；DEX 同根跟随不足至少 `30%`；若预估毛边际不足覆盖 gas / fee / slippage / MEV，则 veto
- risk / sizing / execution overlay：默认 dollar-neutral；先做 `1 x 5m` 或 `1–3 x 1m` 短持有；spread 回补 `50%~80%` 即止盈；leader 反向或 spread 继续恶化到入场阈值 `1.5x` 止损；若无法稳定控 gas/MEV，则退化为 CEX-only 确认层而非双腿执行

## 4. 可复刻的最小实验
- **研究假设**：当 Binance `ETHUSDT` 在最近 1 根 `5m` 内先产生异常冲击，而 Uniswap WETH/USDT 当根少跟至少 `30%` 时，DEX 会在下一根 `5m` 出现同方向 catch-up。
- **公开数据源**：Binance Spot `ETHUSDT` 公共 `5m klines`；GeckoTerminal Uniswap WETH/USDT 公共 `ohlcv/minute?aggregate=5`。这两路都不需要私有数据库，适合先做最小实验。
- **最小信号定义**：
  1. `r_cex = log(close_cex_t / close_cex_{t-1})`，`r_dex = log(close_dex_t / close_dex_{t-1})`
  2. 事件触发：`z(r_cex, 96) > 2` 且 `abs(r_cex - r_dex) > 0.3 * abs(r_cex)`，并且 `sign(r_cex) = sign(r_cex - r_dex)`
  3. 入场：做 `long lagging leg / short leading leg`；若先只做单腿验证，则先测 DEX 下一根 `5m` 的 signed return
- **出场/风控**：下一根 `5m` 先平；或 spread 回补 `>=50%` 平；若下一根 leader 反向则立即止损
- **先看指标**：`next-bar signed bps`、事件 hit rate、成本后正收益占比；第二层再看美盘 vs 亚盘、高 gas vs 低 gas、v2 vs v3、`5m` vs `1m`

## 5. 风险与保留意见
- 论文主样本里对 ETH 用的是 **Binance vs Uniswap v2**，我这里的快检为了可得性与流动性，先用 **当前更易拿的 GeckoTerminal v3/聚合 OHLC**；这不是论文逐表复现，只能算 desk 化 sanity check。
- 真正做双腿执行时，**gas、MEV、链上确认延迟、池深变化** 都可能让纸面 edge 消失；所以第一轮应优先做“信号是否存在”，不要先假设一定能吃到链上价格。
- 这条线的更稳妥落地方式，往往不是 always-on，而是 **只做冲击足够大、滞后足够明显、成本还没把 edge 吃光的 pocket**。

## 6. 来源
1. **Plazuelo Pascual, J., Tardón Rubio, C., Toro Cebada, J., & Hernando Veciana, Á. (2025). _Price Discovery in Cryptocurrency Markets_. arXiv working paper.**
   - DOI：无
   - Readable URL：https://arxiv.org/abs/2506.08718
   - PDF URL：https://arxiv.org/pdf/2506.08718.pdf
2. **GeckoTerminal API（Uniswap WETH/USDT 公共 OHLC）**
   - URL：https://api.geckoterminal.com/api/v2/networks/eth/pools/0x4e68ccd3e89f51c3074ca5072bbac773960dfa36/ohlcv/minute?aggregate=5&limit=1000
3. **Binance Spot API（ETHUSDT 公共 K 线）**
   - URL：https://api.binance.com/api/v3/klines?symbol=ETHUSDT&interval=5m&limit=1000
