# 别把这份 Binance 新币做空 repo 只读成“日线回测”：对 short-cycle desk，更该先测的是「listing-phase overheat × 15m fade short」这条 raw alpha

- 时间：2026-04-13 00:23 UTC
- 类型：2025/2026 GitHub repo source audit（`README.md` + `config.py` + `run_full_backtest.py` + `get_binance_new_contracts.py` + `binance_new_contracts_2025.json`）+ Binance USDⓈ-M `15m` public-data portability probe
- 主题标签：raw-alpha/single-asset/mean-reversion/listing-phase/new-listing/overheat-short/perpetual/funding-admission/high-percentile/extreme-reversal/binance/15m/repo/public-data/cost/risk
- 证据类型：repo 源码证据 + 公共数据 portability probe

- 主题类型：raw alpha
- 基础 alpha：**新上市 perp 在上线后最初几天常出现 attention / leverage / funding 共振驱动的过热上冲；当价格重新打到近 72h 极高分位、且 funding 仍为正时，随后 `4h~24h` 更像回落而不是继续单边抬升。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1. 先把一句话说清楚：这篇东西的 base alpha 是什么？

> **base alpha = 新上市 perp 的早期过热回落（listing-phase overheat short）。**

翻成人话：
- 币刚上线，注意力最强、杠杆最拥挤、funding 往往偏正；
- 如果上线后第 `3` 天附近又冲到近几天的高分位，很多时候不是新趋势起点，而是末端过热；
- 这时去追多，容易买在 attention peak；
- 反过来做 **extreme fade short**，更像一条能独立成策略的 raw alpha。

所以它不是：
- 纯 regime 注释；
- 只服务别的 alpha 的 overlay；
- 也不是“新币危险所以别碰”的风险常识。

它本身就能写成：
- 明确 universe；
- 明确 entry；
- 明确 exit；
- 明确 funding / listing-window admission；
- 明确 sizing / cost / veto。

## 2. 这次看了什么

主材料是一个很新的 GitHub 仓库：

### 主来源（repo）
- **Author / owner handle：** `frozen-cherry`
- **Year：** 2025/2026
- **Title：** *Binance Futures Short Strategy Backtester*
- **Venue：** GitHub repository
- **DOI：** N/A
- **Repo URL：** <https://github.com/frozen-cherry/binance-futures-short-strategy>
- **Readable README：** <https://raw.githubusercontent.com/frozen-cherry/binance-futures-short-strategy/main/README.md>
- **Key source files used this round：**
  - <https://raw.githubusercontent.com/frozen-cherry/binance-futures-short-strategy/main/config.py>
  - <https://raw.githubusercontent.com/frozen-cherry/binance-futures-short-strategy/main/run_full_backtest.py>
  - <https://raw.githubusercontent.com/frozen-cherry/binance-futures-short-strategy/main/get_binance_new_contracts.py>
  - <https://raw.githubusercontent.com/frozen-cherry/binance-futures-short-strategy/main/binance_new_contracts_2025.json>
- **Repo metadata：** created `2025-12-17T16:02:48Z`，updated `2026-04-02T00:26:33Z`，stars `39`

README 的 headline 很直白：
- 它直接做的是 **Binance 新上线合约的早期做空回测**；
- 宣称 2025 年新合约样本里，日线版参数能跑出不错的累计收益；
- 而且不是只给故事，`config.py`、`run_full_backtest.py`、`get_binance_new_contracts.py` 已经把关键组件都写出来了。

对我们 desk 来说，这个 repo 的价值不在于“日线回测赚了多少”，而在于它给了一条很清楚的 raw alpha 原语：

> **listing attention squeeze 不是只能回避，也可以被反着交易。**

## 3. repo 真正实现了什么

源码逻辑非常简单，没有故弄玄虚：

### 3.1 入场条件
repo 默认参数：
- `DAYS_AFTER_LISTING = 3`
- `LOOKBACK_DAYS = 3`
- `PRICE_PERCENTILE = 95.0`
- `MIN_FUNDING_RATE = 0.0`

翻译一下就是：
1. 上线至少满 `3` 天；
2. 当前价格处于过去 `3` 天高点分布的 `95%` 分位以上；
3. 最近 funding 仍为正；
4. 满足就开空。

### 3.2 出场条件
repo 默认：
- `TAKE_PROFIT_PCT = 30%`
- `STOP_LOSS_PCT = 15%`
- `MAX_HOLDING_DAYS = 30`

也就是：
- 有很大的止盈空间，承认新币跌起来会很猛；
- 止损也放得较宽，承认新币波动极大；
- 超时退出，避免无限拖单。

### 3.3 这条 alpha 为什么成立
repo 的隐含假设其实很朴素：
- 上新初期 attention 过强；
- 新币 perp 更容易出现 crowding / overpricing / positive funding；
- 当价格再次回到近几天极高位置时，买盘边际质量下降；
- 后面常见的是回吐、不是稳态趋势延续。

这跟常规大币 `15m` 动量不是一回事。它更像：
- **事件驱动**
- **短寿命 pocket**
- **交易窗口只发生在上市后的最初几天**

所以它天然适合当一条独立素材，而不是再被塞回 generic trend / breakout 桶里。

## 4. 对 short-cycle desk，最值得做的不是日线照抄，而是把它翻成 `15m` 版本

如果直接照 README 的日线口径，我们能得到的只是：
- “新币后面常跌”这个大方向；
- 但对 `5m/15m` desk 来说太慢，也太粗。

真正该测的是：

> **当新上市 perp 在第 3 天附近又冲到近 72h 极高分位、且 funding 仍为正时，后面 `4h / 12h / 24h` 的 short-horizon 回落是否已经足够明显？**

如果答案是“是”，这题就不是低频叙事，而是一条可以被压进 `15m` 执行层的 raw alpha。

## 5. public-data portability probe：`15m` 版不但没塌，反而很像能直接立项

### 5.1 数据口径
我这轮没复刻 README 的日线总收益，而是做了更 desk 化的最小实验。

#### 数据源
- **listing universe：** repo 自带 `binance_new_contracts_2025.json`
- **价格：** Binance USDⓈ-M public `fapi/v1/klines`
- **funding：** Binance USDⓈ-M public `fapi/v1/fundingRate`

#### 频率与窗口
- K 线频率：`15m`
- 每个 symbol 只看：**上市后前 10 天**
- signal warm-up：前 `72h`

#### 事件定义
在任一 `15m` bar：
1. 当前时刻距离上市至少 `72h`；
2. 当前 close ≥ 过去 `72h` 高点分布的某个高分位（我测了 `95% / 97.5% / 99%`）；
3. 最近一笔 funding > `0`；
4. 视为一个 short event。

#### 本地 artifacts
- `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-13_newlisting-short-meanreversion-alpha/new_listing_short_probe.py`
- `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-13_newlisting-short-meanreversion-alpha/event_summary.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-13_newlisting-short-meanreversion-alpha/event_panel.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-13_newlisting-short-meanreversion-alpha/trade_summary.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-13_newlisting-short-meanreversion-alpha/trade_panel.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-13_newlisting-short-meanreversion-alpha/trade_summary_by_symbol.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-13_newlisting-short-meanreversion-alpha/fetch_status.csv`

### 5.2 样本说明（重要）
脚本请求了前 `180` 个 2025 上新合约；其中前半段抓取正常，后半段 Binance API 开始返回 `403`，所以这轮 quick probe 实际成功拿到：
- **`88` 个 symbol** 的 `15m + funding` 数据；
- event study 覆盖 `39~55` 个 symbol（按阈值不同）；
- strategy shell 覆盖 `43~59` 个 symbol（按参数不同）。

所以这轮证据是：
- **足够说明方向值不值得立项；**
- 但还不是全年完整 census 终版。

## 6. 先看最关键的问题：这条 base alpha 在 `15m` 上还成立吗？

答案很明确：**成立，而且是越极端越强。**

### 6.1 事件研究：不是“第 3 天后继续涨”，而是“第 3 天极端上冲后更容易跌”

#### 阈值 = 95% 分位
- `4h` forward short return：
  - 事件数：`1479`
  - 覆盖 symbol：`55`
  - 平均：**`+1.07%`**
  - 胜率：**`63.15%`**
  - t-stat：`7.70`
- `12h` forward short return：
  - 平均：**`+2.05%`**
  - 胜率：**`61.53%`**
  - t-stat：`9.56`
- `24h` forward short return：
  - 平均：**`+3.13%`**
  - 胜率：**`64.71%`**
  - t-stat：`12.38`

#### 阈值 = 97.5% 分位
- `4h`：**`+1.29%`**，胜率 `65.29%`，事件 `847`
- `12h`：**`+2.52%`**，胜率 `65.29%`
- `24h`：**`+3.72%`**，胜率 `66.35%`，t-stat `11.38`

#### 阈值 = 99% 分位
- `4h`：**`+1.57%`**，胜率 `67.75%`，事件 `400`
- `12h`：**`+3.12%`**，胜率 `67.75%`
- `24h`：**`+4.31%`**，胜率 `67.75%`，t-stat `8.84`

一句话总结：

> **这条线不是“越强越该追”，而是“越接近 72h 极端、越像末端过热”。**

而且很关键的一点是：
- `4h` 已经显著；
- `12h/24h` 更强；
- 说明这不是只能靠日线 holding period 才能看到的慢结论。

## 7. 再看完整策略壳：entry / exit / risk 能不能直接写出来？

我额外把它压成了一个很简单的 `15m` 交易壳：
- 入场：满足极端分位 + funding>0 就开空；
- 出场：`tp / sl / max hold` 三选一；
- 同时只持一笔；
- bar 内若止盈止损同 bar 触发，**保守地先算 stop**。

### 7.1 最像 first production candidate 的版本
我更喜欢这一档：
- `threshold = 99%`
- `tp = 8%`
- `sl = 6%`
- `max_hold = 48 bars = 12h`

结果：
- 交易数：`122`
- 覆盖 symbol：`43`
- 胜率：**`55.74%`**
- 平均单笔：**`+1.17%`**
- 中位数：**`+1.81%`**
- 累计：**`+142.36%`**
- 平均持有：`22.2` bars
- 出场构成：
  - 止盈：`36.07%`
  - 止损：`36.89%`
  - 超时：`27.05%`

这组数说明：
- 它不是靠极少数大赚单硬拉出来；
- 中位数也明显为正；
- 而且胜率没低到离谱，像一条真的能落地的策略壳。

### 7.2 更宽松版本也没塌
#### `threshold=97.5%`, `tp=8%`, `sl=6%`, `max_hold=12h`
- 交易数：`150`
- 覆盖 symbol：`49`
- 胜率：**`54.67%`**
- 平均单笔：**`+0.87%`**
- 累计：**`+131.07%`**

#### `threshold=95%`, `tp=8%`, `sl=6%`, `max_hold=12h`
- 交易数：`195`
- 覆盖 symbol：`59`
- 胜率：**`51.79%`**
- 平均单笔：**`+0.85%`**
- 累计：**`+165.60%`**

这说明：
- edge 不是只存在于一个窄参数点；
- 但**极端阈值更干净、均值更高**；
- 所以 প্রথম优先应该从 `99%` 那档开始，而不是一上来就求交易数最大化。

### 7.3 更长持有也还能活，但第一落点不一定要拖太久
#### `threshold=99%`, `tp=10%`, `sl=8%`, `max_hold=24h`
- 交易数：`90`
- 胜率：**`54.44%`**
- 平均单笔：**`+1.03%`**
- 平均持有：`43.4` bars

这说明：
- 24h 版也没崩；
- 但从 execution 角度，**12h 版更像 first lane**；
- 真到实盘，宁可先短持有 + 快复核，不必一开始就赌更长时间暴露。

## 8. 它和我们当前 short-cycle desk 的关系是什么

这题值得写，不是因为“又一个新币故事”，而是因为它正好补了我们当前素材池里相对缺的一块：

1. **它是 raw alpha，不是 filter。**
2. **它是事件驱动 mean reversion，不是又一条通用 breakout / momentum。**
3. **它天然带完整策略壳。**
   - listing-window
   - percentile extreme
   - funding admission
   - tp/sl/time stop
4. **它对 `15m` 是真能落地的。**
   - 不是只能日频看图说话；
   - 也不是只能挂在 4h/1d 因子层。
5. **它和当前 raw alpha 素材池直接互补。**
   - 我们已经有很多常规大币、pairs、basis、funding、OFI；
   - 这条补的是 **listing-phase event pocket**。

## 8.5 策略拆解（必填）
- 方向属性：单资产 / 事件驱动 / listing-phase extreme short
- 基础 alpha：新上市 perp 的 attention/funding 过热在极端高分位更容易回吐
- regime：仅在 **上市后前 `3~10` 天** 生效；离开这个窗口就不是同一条 alpha
- filter / veto：最近 funding 必须为正；后续应补 `min ADV / spread / quote continuity / launch announcement crowd` veto
- risk / sizing / execution overlay：固定止盈止损 + 时间止损；单币上限、同日上新批次上限、以及 maker/taker split execution 都应单列

## 9. 成本怎么读

这条线的好消息是：**gross edge 很厚**。

例如最好的一档：
- gross 平均单笔约 `+1.17%`

即使粗扣：
- round-trip taker fee + 一部分滑点 = `20~30 bps`

表面上仍然剩下：
- 约 `+0.87% ~ +0.97% / trade`

但这里绝不能过度乐观。因为真正的成本风险不是普通手续费，而是：
- 新币初期盘口跳档；
- wick 很长；
- intrabar gap 可能让你拿不到理想 stop / tp；
- 同一批新币上线时，相关性和 crowding 会一起升高。

所以最诚实的判断是：

> **这条 alpha 的 gross edge 明显大于普通 fee，但仍需要用 `1m / trade replay / spread snapshot` 去验证“能不能真实吃到”。**

也就是说：
- 它不像很多 `5m` 弱 edge alpha 那样，先天就被手续费掐死；
- 但也不能直接把 OHLC backtest 当成交真相。

## 10. 这题当前最合理的第一版策略长什么样

### 最小可执行版本
- **Universe：** Binance USDⓈ-M 2025+ 新上市合约
- **Signal TF：** `15m`
- **Warm-up：** 上市后先等 `72h`
- **Entry：**
  - 当前 `15m` close ≥ 过去 `72h` 高点的 `99%` 分位
  - 最近 funding > `0`
- **Side：** short only
- **Exit：**
  - `TP = 8%`
  - `SL = 6%`
  - `Time stop = 12h`
- **Sizing：**
  - 单笔固定风险 budget
  - 对高 ATR 新币做 vol-scaling
  - 单日同主题最多 `N` 笔，防止同批上新一起爆雷

### 为什么现在先不建议做 symmetric long
因为这轮证据支持的是：
- **extreme overheat short**
- 不是一般性的“新币双边波动策略”

也就是说当前最强的东西是：
- 极端高位 → short
- 不是极端低位 → long 的镜像对称。

## 11. 下一步怎么测

1. **补完全年 census，不要停在 88 个 symbol**
   - 这轮被 Binance `403` 截断；
   - 下一步改走 archive / 节流抓取，把 2025 全量新合约补齐。

2. **把 `15m signal -> 1m execution` 拆开**
   - 主信号保留在 `15m`；
   - entry execution 改用 `1m`：
     - 看首个反向确认 bar 再进；
     - 或做 `VWAP / micro pullback` 执行。

3. **做 cost realism**
   - 补 `best bid/ask` 或至少用 launch-phase spread proxy；
   - 单独测 `10 / 20 / 30 / 50 / 100 bps` 成本梯度。

4. **加 liquidity gate**
   - 不要把所有新币一锅端；
   - 先加最简单的 `quote volume / trade count / notional turnover` 下限；
   - 看 edge 是不是来自“可交易的新币”，还是来自“极难成交的鬼币”。

5. **测同批次上线的相关性风险**
   - 如果一天上了多只同风格币，信号可能不是独立样本；
   - 需要单日主题 cap / sector cap。

6. **做更诚实的 admission fork**
   - 当前 funding>0 已经有用；
   - 下一步可以测：
     - funding level bucket
     - launch 后累计涨幅 bucket
     - bar range / ATR bucket
   - 看究竟是“正 funding”有效，还是“极端 funding + 极端 stretch”才有效。

## 12. 一句话带走

> **这份 repo 最值钱的不是 README 里的日线累计收益，而是它暴露出一条很清楚、而且能压进 `15m` 的 raw alpha：新上市 perp 在第 3 天附近若再次冲到近 72h 极端高位、且 funding 仍为正，随后 `4h~24h` 更像回吐而不是继续涨；对 short-cycle desk，这条「listing-phase overheat short」值得直接立项。**
