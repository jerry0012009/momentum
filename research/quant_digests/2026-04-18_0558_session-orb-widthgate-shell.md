# 别把这份 2026 Hyperliquid ORB 仓只读成“又一个开盘突破 bot”：对 short-cycle desk，更该先拆的是「session opening-range breakout × box-width gate」这条完整 raw alpha 壳

- 时间：2026-04-18 05:58 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `scripts/save_opening_range.py` + `scripts/autonomous_trade.py` + `FORTSCHRITT.md` + `ERKENNTNISSE.md`）+ Binance USDⓈ-M `15m` public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：**session opening-range breakout**——先用某个交易时段开头第一根 `15m` K 线定义 `high/low`，后续若价格越过区间上沿就顺势做多、跌破下沿就顺势做空，赌的是“开盘定价完成后，短窗内继续单边扩张”
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / breakout / intraday / session / opening-range / trend / continuation / box-width / risk-reward / Hyperliquid / Binance / 15m / 5m / repo / public-data / cost / risk
- 证据类型：仓库源码 + live-notes + public-data portability probe

先回答 base alpha：**说得清楚，而且是完整策略壳。**
这份仓库的母体不是“泛突破”，而是更具体的 **session ORB**：把东京 / 欧洲 / 美股活跃时段都当成伪“开盘”，先锁第一根 `15m` 的高低点，再在后面 `60~75` 分钟追随真正突破的一边。对我们 desk 来说，最值得保留的不是“每个 session 都机械追 breakout”，而是它天然给了一个 **完整可交易骨架**，而且很容易拆成：**session 选择 × box 宽度 gate × 固定 R multiple 出场**。

## 1. 这次看了什么
主来源：
- **作者 / 组织：** `fefotec`
- **项目：** `apex-trading-bot-template`
- **Repo URL：** <https://github.com/fefotec/apex-trading-bot-template>
- **关键文件：**
  - README：三段 session（Tokyo / EU / US）+ `max 1 trade per session`
  - `scripts/save_opening_range.py`：直接把第一根 `15m` candle 当 opening range box
  - `scripts/autonomous_trade.py`：突破入场、另一侧止损、默认 `2:1` R/R、kill switch
  - `FORTSCHRITT.md` / `ERKENNTNISSE.md`：作者后续已经开始意识到 **box 太宽/太窄、session 差异、crypto 不存在真正 cash open** 这些实盘问题

## 2. 核心结论
- **这不是只会讲方向的想法，而是完整壳。** entry / stop / TP / session router / per-session max trades / drawdown kill switch 都写出来了。
- **plain 版直接照抄不行。** 我用 Binance USDⓈ-M `BTC/ETH/SOL/AVAX 15m` 在 `2026-02-01 ~ 2026-04-18` 做最小 probe：896 笔，整体 **gross 约 `-5.65 bps/笔`**，扣 `8 bps` 后更差，说明“任何 session 都追第一段 breakout”大概率会被噪音吃掉。
- **但它不是完全没料。** 同一 probe 里，若只看 **US session 且 opening box 宽度落在该 session 最宽四分位**，约 74 笔，**gross 约 `+10.62 bps/笔`，胜率约 `55.4%`，粗扣 `8 bps` 后仍约 `+2.62 bps/笔`**。
- **EU session 更像 filter-driven pocket。** 若剔除最宽四分位，约 226 笔，**gross 约 `+2.93 bps/笔`**；还没过 taker 成本线，但已经说明 **box-width gate** 比“无脑三段都做”更值得留下。

一句话核心结论：**session ORB 本体不是新鲜事，但在 crypto 里，它更像“只有特定 session + 特定 box 宽度才活”的条件型 raw alpha，而不是全天候通用母版。**

一句话证明方式：**repo 给了完整规则，我再用公开 `15m` perp 数据把它翻成最小事件回测，结果显示 plain 版负、session+box gate 后局部转正。**

## 3. 为什么和当前项目有关
这条线对 `momentum` 的价值不在“再写一篇 breakout 教科书”，而在于它提供了一个很清楚的短周期交易骨架：
- raw alpha 本体：**开盘区间突破后的短窗延续**
- 可复用模块：**session gate、box-width gate、R-multiple 出场、每 session 只打一次**
- 和当前 desk 的关系：它很适合做成 **5m/15m intraday router**，而不是全天信号；也适合跟已有 trend / VWAP / RSI / volume 线组合，充当“什么时候值得追第一段单边”的触发器

## 3.5 策略拆解（必填）
- 方向属性：顺势 / breakout / 单资产
- 基础 alpha：session opening-range breakout
- regime：优先交易流动性集中、信息密度更高的 session（尤其 US）
- filter / veto：box-width 分位、是否同 bar 双向穿越、是否已有当 session 交易、是否遇到重大数据时段
- risk / sizing / execution overlay：另一侧 box 做 stop、固定 `2R` 或 split TP、按 box 风险定仓位、优先 maker/stop-limit 而不是裸 taker 追价

## 4. 可复刻的最小实验
- **研究假设：** crypto 的 ORB edge 不是“所有 session 都有”，而是集中在少数高信息流 session，且需要 box-width gate。
- **可计算定义：**
  1. session 开头第一根 `15m` bar 定义 `box_high / box_low`
  2. 后续 `60~75` 分钟首次突破上沿/下沿即入场
  3. `SL = box 另一侧`，`TP = 2R`，超时 `2h` 平仓
  4. 先按 session 分组，再按 `box_width_bps` 做分位切片
- **最小回测切口：** Binance / Hyperliquid 高流动 perp；`BTC/ETH/SOL/AVAX`；周期先跑 `15m`，再向 `5m` 做更细 opening box 与更紧执行。
- **最该先看：**
  - `gross/net bps per trade`
  - `session × box-width quantile` 的稳定性
  - `timeout rate`（这条线很高，说明很多单不是被打止盈，而是拖到失效）

## 5. 风险与保留意见
- 这条线**非常怕假突破**；plain 版一旦没做 session / box 过滤，很容易变成噪音收集器。
- 这次 probe 用的是 Binance USDⓈ-M `15m`，而仓库真实执行在 Hyperliquid；跨 venue 可迁移，但不能当作等价复现。
- 我这轮只做了最小规则翻译，**还没加入** repo 后续实盘里提到的 ATR / split TP / box 太窄 veto / 重大新闻回避，所以现在更像 first verdict，不是 final shell。
- 由于 ORB 属于“大家都知道”的形态，**执行摩擦和入场方式** 比日线级别策略更关键；若最后只能 taker 追 break，edge 很可能很快被吃干净。

## 6. 来源
- `fefotec`. `apex-trading-bot-template`. GitHub repo. 2026.
  - Repo URL：<https://github.com/fefotec/apex-trading-bot-template>
  - README：<https://github.com/fefotec/apex-trading-bot-template/blob/main/README.md>
  - `scripts/save_opening_range.py`：<https://github.com/fefotec/apex-trading-bot-template/blob/main/scripts/save_opening_range.py>
  - `scripts/autonomous_trade.py`：<https://github.com/fefotec/apex-trading-bot-template/blob/main/scripts/autonomous_trade.py>
  - `FORTSCHRITT.md`：<https://github.com/fefotec/apex-trading-bot-template/blob/main/FORTSCHRITT.md>
  - `ERKENNTNISSE.md`：<https://github.com/fefotec/apex-trading-bot-template/blob/main/ERKENNTNISSE.md>
- 本地 portability artifacts：
  - `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-18_session_orb_widthgate_probe.py`
  - `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-18_session_orb_widthgate_probe_summary.json`
  - `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-18_session_orb_widthgate_probe_trades.csv`
