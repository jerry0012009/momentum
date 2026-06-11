# 别把这份 Hyperliquid BB bot 只读成“布林带小机器人”：对 short-cycle desk，更该先拆的是「band-touch mean reversion × maker-first opposite-band exit」这条完整 raw alpha 壳——而源码已经比 README 更像 production shell

- 时间：2026-04-14 17:58 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `config/accounts.json` + `src/main.py` + `src/perps_trading.py` + `tests/test_signals.py` + `tests/test_exit_flow.py` + `tests/test_stop_logic.py` + `tests/test_pnl.py` + `test/compare_backtest_vs_live.py`）+ Binance Spot `5m/15m` public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：**价格触碰 Bollinger 外侧后，向对侧 band 回归的均值回复；EMA(200) 只负责顺大方向过滤，不是 alpha 本体。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/single-asset/mean-reversion/bollinger-band/ema-filter/maker-first/opposite-band-exit/breakeven-refresh/hyperliquid/binance-spot/binance-perpetual/5m/15m/repo/public-data/cost/risk
- 证据类型：源码规则 + public-data portability probe

## 1. 这次看了什么
主来源是 GitHub 仓库：
- **Author / Owner：** vitor-chagas
- **Year：** 2026
- **Title：** *dex-trading-bot*
- **Venue：** GitHub repository
- **DOI：** N/A
- **Readable URL：** <https://github.com/vitor-chagas/dex-trading-bot>
- **Repo URL：** <https://github.com/vitor-chagas/dex-trading-bot>

这份 repo 的价值，不只是“BB+EMA”这套老指标，而是它把一条 **真能下单的完整 MR 壳** 写得很细：限价进场、60 秒未成交撤单、止损、对侧 band 目标位、TP 漂移后的 break-even、maker/taker 费用、仓位 sizing、同向仓位上限、以及回测 vs live 对照脚本。

## 2. 核心结论
- **一句话核心结论：** 这份 repo 值得 intake 的不是 README 上那句 “BB(20,2)+EMA(200)” 本身，而是 **`band-touch mean reversion + maker-first execution + dynamic break-even TP refresh` 这条完整 raw alpha 壳**；它不像纯 filter，也不是只会讲故事的 demo。
- **一句话证明方式：** 我先做源码审计，确认 entry / exit / sizing / risk / fee 是闭环的；再把它的 core rules 按 repo 自带费率假设迁到 Binance Spot 公共 `5m/15m` 数据上，直接看 trades、胜率、净 bps/笔、stop / breakeven 占比。
- **base alpha 很清楚**：`price <= lower band & price > EMA` 做多，`price >= upper band & price < EMA` 做空；收益来自 **价格从 band 外侧向对侧 band 回归**，EMA 只是顺着长周期方向过滤逆势单。
- **这确实是完整策略壳，不是半成品**：`src/perps_trading.py` 里已经把 `60s pending limit`、`stop-market`、`opposite-band maker TP`、`TP 反穿 entry 时改成 break-even`、`same-direction exposure cap`、`min_band_width_pct` 过滤都写出来了；`test_signals / test_exit_flow / test_stop_logic / test_pnl` 也说明作者不是只写 README。
- **但 README 已经部分过时**：README 说“进场限价挂在 band level”，源码现在其实改成了 **直接用当前价格作为 maker/ALO 限价基准**，因为 band level 容易因为 stale 而触发 ALO rejection；也就是 repo 已经从“教科书 BB bot”往更像 production 的执行壳走了一步。
- **README 参数和 live 配置也不再一致**：README 还是 BTC `BB(20,2), SL 2.5%, target_risk 8%`；当前 `config/accounts.json` 里 active BTC 已变成 **`BB(10,1.8), SL 4.0%, target_risk 10%`**，而且同一账户还挂了 **12 个 active tokens**，`src/main.py` 会把资金按 active token 数自动平分，结果 BTC 实际 `capital_pct` 会被压到约 **8.33%**，不再是 README 里那种“单 BTC 重仓”口径。
- **本地 public probe 没有立刻塌掉**，这是它比很多近期壳更值钱的地方：按 repo `compare_backtest_vs_live.py` 的费率假设（maker `1bp`，stop taker `5bps`），过去约 `180d` 的 Binance Spot BTCUSDT 上，README canonical `5m` 壳得到 **468 笔 / 63.0% 胜率 / +29.13 bps/笔净值 / 持有中位 132.5 分钟**；`15m` 也还有 **172 笔 / 58.7% 胜率 / +26.60 bps/笔**。当前 active BTC 配置更激进：`5m` **954 笔 / +21.34 bps/笔**，`15m` **301 笔 / +35.14 bps/笔**。
- 真正值得盯的细节是 **breakeven bucket 很大**：`5m` canonical 约 **35.9%**、active config 约 **46.6%** 的平仓都是 break-even，这说明这条壳的 edge 不只是“赌对侧 band 一定打满”，而是 **用动态 TP refresh 把坏单尽量压到只亏手续费**。

## 3. 为什么和当前项目有关
这轮值得进素材池，因为它满足你这轮最想要的那类候选：
1. **base alpha 说得清楚**：就是 band-touch MR，不是把 filter 伪装成 alpha；
2. **能直接落成完整策略**：signal、entry、exit、sizing、risk、cost 全有；
3. **适配当前短周期**：repo 原生就是 `5m`，而 `15m` transfer 也没有马上失真；
4. **能直接服务后续实盘组件拆解**：特别是 maker-first、pending-order cancel、dynamic TP refresh、break-even rescue 这些执行层细节。

## 3.5 策略拆解（必填）
- 方向属性：**single-asset / mean reversion / 双边可做**
- 基础 alpha：**`touch outer Bollinger band -> revert toward opposite band`**
- regime：**`EMA(200)` 方向过滤，只做顺长周期方向的反身回归**
- filter / veto：**`min_band_width_pct`、`max_same_direction`、60 秒未成交撤单、价格走远撤单**
- risk / sizing / execution overlay：**`target_risk_pct -> capital_pct`、stop-market、maker TP、TP 漂移时 break-even、ALO rejected 后 retry / GTC fallback**

## 4. 可复刻的最小实验 + 下一步怎么测
### 本轮最小实验
- 市场：Binance Spot `BTCUSDT`（按 repo 原设作为 signal source）
- 周期：`5m / 15m`
- 样本：最近约 `180d`
- 口径：
  - `readme_shell`: `BB(20,2), EMA(200), SL 2.5%`
  - `live_config_btc`: `BB(10,1.8), EMA(200), SL 4.0%`
  - 成本：entry maker `1bp`；target/breakeven exit maker `1bp`；stop exit taker `5bps`
- 产物：
  - 脚本：`reports/artifacts/quant_digests/2026-04-14_bandtouch_makerfirst_probe.py`
  - 汇总：`reports/artifacts/quant_digests/bandtouch_makerfirst_probe_summary_2026-04-14.csv`
  - 明细：`reports/artifacts/quant_digests/bandtouch_makerfirst_probe_detail_2026-04-14.csv`

### 下一步怎么测
1. **先补 60 秒 working-order fill simulator**：当前 public probe 用 bar-close 近似，会高估 post-only 成交质量；下一步要把 `ALO reject / retry / timeout cancel / price-moved-away cancel` 真正模拟进去。
2. **把 signal-source 与 execution-source 分开测**：repo 用 Binance spot 出信号、Hyperliquid perp 执行；下一步应加上 perp book / fee / fill proxy，确认 edge 不是被“signal spot, fill spot”高估出来的。
3. **分开验证 README canonical vs current live config**：现在最该 intake 的是 shell，不是参数；先确认 `20/2/2.5` 和 `10/1.8/4.0` 谁更稳，再决定要不要继续压 `1m/3m`。
4. **最后再加 overlay**：若 base shell 在 fill-aware 口径下仍成立，再补 funding / vol / session veto；别反过来先堆 filter。

## 5. first verdict
这份 repo **可以名正言顺地进 raw alpha / 完整策略壳素材池**。更诚实的读法不是“又一个 BB bot”，而是：

> **`band-touch mean reversion` 这条 alpha 本体清楚，源码已经把它包成了 maker-first、可回放、可实盘拆件的 production-ish shell；README 虽然有点过时，但这反而说明 repo 真在往可执行方向进化。**

当前最合理的落点不是直接信 README 年化，而是把它作为 **`5m native first`、可向 `15m` 平移、并且能继续拆 fill model 的完整 raw alpha 候选**。

## 6. 来源
- vitor-chagas. (2026). *dex-trading-bot*. GitHub repository.
  - Readable URL: <https://github.com/vitor-chagas/dex-trading-bot>
  - Repo URL: <https://github.com/vitor-chagas/dex-trading-bot>
- Key source files audited:
  - <https://raw.githubusercontent.com/vitor-chagas/dex-trading-bot/main/README.md>
  - <https://raw.githubusercontent.com/vitor-chagas/dex-trading-bot/main/config/accounts.json>
  - <https://raw.githubusercontent.com/vitor-chagas/dex-trading-bot/main/src/main.py>
  - <https://raw.githubusercontent.com/vitor-chagas/dex-trading-bot/main/src/perps_trading.py>
  - <https://raw.githubusercontent.com/vitor-chagas/dex-trading-bot/main/tests/test_signals.py>
  - <https://raw.githubusercontent.com/vitor-chagas/dex-trading-bot/main/tests/test_exit_flow.py>
  - <https://raw.githubusercontent.com/vitor-chagas/dex-trading-bot/main/tests/test_stop_logic.py>
  - <https://raw.githubusercontent.com/vitor-chagas/dex-trading-bot/main/tests/test_pnl.py>
  - <https://raw.githubusercontent.com/vitor-chagas/dex-trading-bot/main/test/compare_backtest_vs_live.py>
