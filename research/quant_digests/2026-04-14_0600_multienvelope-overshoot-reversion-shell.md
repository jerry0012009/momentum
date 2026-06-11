# 别把这份 mean-reversion bot 只读成“包络线回归小工具”：对 short-cycle desk，更该先拆的是「multi-envelope overshoot × average-return」这条完整 raw alpha 壳——但 repo 自带回测记账口径有明显 sizing bug，真正值得抄的是 shell，不是截图收益

- 时间：2026-04-14 06:00 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `config/config.yaml` + `src/strategy.py` + `src/backtester.py` + `src/risk_manager.py`）+ Binance USDⓈ-M `1h/15m/5m` public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：**价格相对短均线出现多层 envelope 过冲后，往均线回归的均值回复；risk manager 只是 overlay，不是 alpha 本体。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/single-asset/mean-reversion/envelope/multi-band/ladder-entry/average-return/sma/donchian/ema/risk-blocker/binance-perpetual/1h/15m/5m/repo/public-data/cost/risk
- 证据类型：源码规则 + public-data portability probe

## 1. 这次看了什么
主来源是 GitHub 仓库：
- **Author / Owner：** grantad
- **Year：** 2026
- **Title：** *crypto-bot*
- **Venue：** GitHub repository
- **DOI：** N/A
- **Readable URL：** <https://github.com/grantad/crypto-bot>
- **Repo URL：** <https://github.com/grantad/crypto-bot>

这份 repo 的价值，不在“包络线”这三个字本身，而在它把一条**完整可下单的 MR 壳**写得很清楚：`1h` 短均线、3 层 percent envelope、逐层加仓、回到均线就平、可选 jump close-all、session risk blocker、显式手续费。它很像一个能直接拿来做 short-cycle 改写的基础壳。

## 2. 核心结论
- **一句话核心结论：** 这份 repo 最值得 intake 的，是 **`multi-envelope overshoot -> average-return` 的完整均值回复壳**；真正适合 desk 的第一落点不是 repo 原生 `1h` 生搬硬套，也不是继续压到 `5m`，而是 **`15m` 级别的 wall-clock-scaled transfer**。
- **一句话证明方式：** 我先做源码审计，再把 repo 的核心规则单独迁到 Binance USDⓈ-M 公共 klines 上，分别测 `1h` 原样、`15m` 时间尺度平移、`5m` 继续下压三组口径，直接看 trade count、成本后 bps/笔、胜率和持有时长。
- 源码层面，**base alpha 很清楚**：`close` 的短均值（SMA/EMA/Donchian mid）给参考中枢，`high/low` 触到 `±7%/11%/14%` 包络就分层逆势进场，`close` 回到均值即平仓；stop-loss、close-all、risk manager 都是壳层，不是 alpha 本体。
- 但 repo 自带 backtest **不能直接信**：`src/backtester.py` 把 `capital_allocation / num_envelopes` 直接当成 `size` 传进持仓，再在 `TradeRecord.calculate_pnl()` 里用 `(exit - entry) * size` 记账；也就是说，**USD 资金被当成了数量单位**，headline PnL 口径明显失真。
- 我按“正确按名义本金记账”的方式重跑后发现，**repo 原生 `1h` 壳太稀疏**：`2025-10-01 ~ 2026-04-14` 的 Binance perp 上，BTC 只有 **1** 笔、ETH **2** 笔，虽然单笔 net 分别约 **+469.72 / +478.06 bps**，但显然不适合当前 short-cycle desk 当主线。
- 把它做成 **wall-clock-scaled `15m` 迁移**（BTC `24` bars、ETH `20` bars，对应同样的约 `6h/5h` 均值窗口；band 按 `sqrt(15m/1h)` 缩到 `3.5% / 5.5% / 7%`），形状反而更像我们要的：BTC **23** 笔、**+25.01 bps/笔**、**65.2%** 胜率、持有中位 **4.75h**；ETH **69** 笔、**+14.59 bps/笔**、**66.7%** 胜率、持有中位 **4.5h**。
- 继续压到 **`5m`** 后 edge 基本被噪音和成本吃掉：BTC **120** 笔只剩 **-0.27 bps/笔**，ETH **241** 笔约 **-3.50 bps/笔**。这说明这条壳 **更像 `15m` first lane / `1h admission × 15m execution` 候选，不像 broad `5m` taker book**。

## 3. 为什么和当前项目有关
这轮值得进素材池，不是因为它“又一个 MR repo”，而是因为它给的是**非常干净的完整 raw alpha 壳**：
- alpha 本体：价格过冲后回到均值；
- entry：多层 envelope 分批打；
- exit：回均值；
- sizing：按 envelope 层数均分；
- risk：stop-loss + session blocker；
- cost：开平手续费显式写出。

对当前 `momentum` 项目，这比继续看“只有 filter 没有 alpha 本体”的材料更值钱，因为它能直接服务两件事：
1. 给我们补一条**简单、可解释、可迁移**的 single-asset mean reversion 壳；
2. 让我们明确看到：**`5m` 不是所有 raw alpha 都该硬压进去**，有些壳子的自然落点就是 `15m`，再由更快周期只负责 child execution。

## 3.5 策略拆解（必填）
- 方向属性：**single-asset / mean reversion / 双边可做**
- 基础 alpha：**`price far from short-term average -> snap back to average`**
- regime：**repo 原生没有强 regime gate；更像裸 MR 壳**
- filter / veto：**re-entry block、可选 price-jump close-all；后续可再叠 liquid-hours / volatility veto**
- risk / sizing / execution overlay：**3 层 envelope ladder、均值回归退出、40% stop-loss、session risk blocker、显式开平费；但 repo 自带 backtest 的 sizing 记账需先修正**

## 4. 可复刻的最小实验 + 下一步怎么测
### 本轮最小实验
- 市场：Binance USDⓈ-M perpetual
- 资产：`BTCUSDT / ETHUSDT`
- 样本：`2025-10-01 ~ 2026-04-14`
- 数据：公开 `1h / 15m / 5m` klines
- 口径：
  - `1h repo_exact`：原样 `avg_period = 6 / 5`，bands `7% / 11% / 14%`
  - `15m wallclock_scaled`：窗口放大 4 倍，bands 乘 `sqrt(15m/1h)`
  - `5m wallclock_scaled`：窗口放大 12 倍，bands 乘 `sqrt(5m/1h)`
  - 成本：开仓 `2 bps` + 平仓 `5 bps`
- 产物：
  - 脚本：`reports/artifacts/quant_digests/2026-04-14_envelope_shell_transfer_probe.py`
  - 汇总：`reports/artifacts/quant_digests/envelope_shell_transfer_probe_summary_2026-04-14.csv`
  - 明细：`reports/artifacts/quant_digests/envelope_shell_transfer_probe_detail_2026-04-14.csv`

### 下一步怎么测
1. **先修正 repo backtester 的数量单位**：`size` 应该是 `notional / entry_price`，不是直接拿 USD 资金当数量；不修这一步，就不要再讨论 repo 自带 Sharpe 或收益截图。
2. **把 `15m` 壳做 friction ladder**：先固定本轮 `3.5% / 5.5% / 7%`，测试 round-trip `4 / 8 / 12 bps` 三档，看 BTC/ETH 哪一档开始从正转负，再决定它更像 taker 还是 maker-first 候选。
3. **做 `1h admission × 15m child execution`**：保留 repo 的 `1h` envelope 触发为 admission，但让 `15m` 负责更细的成交与减仓，例如“第一根回到最外层 band 内侧的 bar 开始分批减仓”，看看是否能把极稀疏 `1h` 信号变成可交易的 `15m` 壳。
4. **最后才补 regime / veto**：如果要继续增强，优先试 `ATR/realized-vol` 过热 veto 或 funding 同向拥挤 veto；但别先把 overlay 伪装成 alpha，本体仍然是 envelope overshoot 的均值回复。

## 5. first verdict
这份 repo **值得留在 raw alpha 素材池**，但正确读法不是“拿它的 backtest 图直接信”，而是：

> **`multi-envelope overshoot -> average-return` 这条 MR 壳本身是清楚且可迁移的；native `1h` 太稀疏，broad `5m` 又太吵，当前最像样的落点是 `15m` 版，或者 `1h admission × 15m execution`。**

也就是说，这轮真正被 intake 的不是 repo 的绩效数字，而是一个**简单、完整、能快速做 first verdict 的 mean-reversion shell**。

## 6. 来源
- grantad. (2026). *crypto-bot*. GitHub repository.
  - Readable URL: <https://github.com/grantad/crypto-bot>
  - Repo URL: <https://github.com/grantad/crypto-bot>
- Key source files audited:
  - <https://raw.githubusercontent.com/grantad/crypto-bot/main/README.md>
  - <https://raw.githubusercontent.com/grantad/crypto-bot/main/config/config.yaml>
  - <https://raw.githubusercontent.com/grantad/crypto-bot/main/src/strategy.py>
  - <https://raw.githubusercontent.com/grantad/crypto-bot/main/src/backtester.py>
  - <https://raw.githubusercontent.com/grantad/crypto-bot/main/src/risk_manager.py>
