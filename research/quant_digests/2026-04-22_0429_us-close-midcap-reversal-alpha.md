# 别把这份美股收盘窗口研究只读成“time-of-day 异象”：对 short-cycle crypto desk，更该先拆的是「US close-window loser→winner fade」这条 raw alpha
- 时间：2026-04-22 04:29 UTC
- 类型：GitHub
- 主题类型：raw alpha
- 基础 alpha：美股临近收盘的 30 分钟里先跌的中等流动性币，在接下来 45~60 分钟更容易反弹；同期先涨的币更容易回吐
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：cross-sectional / mean-reversion / time-of-day / US-session / close-window / relative-value / cost / risk
- 证据类型：工程经验 + 公开数据

## 1. 这次看了什么
读了 `BNeillDickey/intraday-crypto-reversal-project` 的唯一主文件 `Intraday_Crypto_Reversal_Project.ipynb`。它把问题讲得很直接：不要泛泛地说“crypto 有日内反转”，而是把窗口钉死到 **美股开盘 / 收盘附近**，做横截面 loser-long / winner-short，并显式带入 ADV 过滤和三段式交易成本。

## 2. 核心结论
- **一句话核心结论：** 这份材料最值钱的不是“time-of-day 叙事”，而是一个能直接落地的完整 raw alpha：`15:30–16:00 ET` 先跌的币，`16:15–17:00 ET` 更容易反弹，反之亦然。
- **一句话证明方式：** 作者用 15m Binance spot 历史数据、横截面分组、多窗口 sweep、ADV 过滤和交易成本压力测试，把“收盘窗口反转”与“早盘窗口”分开验证。
- Notebook 原文给出的 strongest claim 是：spot crypto 的 **close-window** 与 **morning-window** 都有 reversal，但 ETF 那边转成 momentum；这说明作者想抓的其实是 **机构流在不同市场结构里的不同传导方式**。
- 我用 Binance USDⓈ-M `15m` 近 `200` 个交易日做了 portability probe：**全大盘 10 币篮子**在 repo 原版 `16:15–17:00 ET` 持有窗下几乎没边，gross 仅约 `+0.06 bps/day`、Sharpe 约 `0.06`；但把 universe 收缩到 `ADA/XRP/DOGE/AVAX/LINK/LTC` 这类 **mid-cap 子集** 后，close-window reversal 明显变厚。
- 其中最干净的 pocket 是：`15:30–16:00 ET` 做信号、`16:00–17:00 ET` 立即持有，mid-cap `top1 loser vs top1 winner` 约 `200` 天样本下 **gross ≈ +3.48 bps/day、Sharpe ≈ 2.18、cum ≈ +7.14%**；若放宽到 `top2 vs top2`，仍有 **gross ≈ +2.18 bps/day、Sharpe ≈ 2.17**。
- 但这条边目前还只是 **gross edge**：如果按四腿 taker 粗算，常规 fee/slippage 很容易把它吃掉。所以它更像 **time-scheduled cross-sectional event router**，要配 maker-first、低冲击执行，不能直接当“无脑每天四腿打满”的主策略。

## 3. 为什么和当前项目有关
这条线和当前 desk 很贴，因为它不是又一个泛化“反转可能有效”的说法，而是把 **什么时候看、看谁、持有多久** 都写死了。对 `1m/3m/5m/15m` 研发来说，这种时间窗明确、资产池明确、可直接转成日内任务调度的 raw alpha，远比空泛 regime 讨论更能进入复现池。

更重要的是，这轮 portability probe 还给了一个很实用的 desk 化重读：**真正能搬过来的不是 broad basket close reversal，而是“mid-cap close-window relative-value fade”**。也就是说，它更适合当一个定时触发的横截面 router，再把 `1m/3m/5m` 用在 child execution，而不是要求所有 liquid majors 每天都照着做。

## 3.5 策略拆解（必填）
- 方向属性：横截面 / 相对价值 / 逆势
- 基础 alpha：US equity close-window 的 cross-sectional loser→winner fade
- regime：更偏美股时段活跃、且资金流容易挤压中等流动性山寨的时候
- filter / veto：ADV 下限、只做 mid-cap 子集、只取 top1 或 top2 极端分位、若窗口内波动/点差异常则 veto
- risk / sizing / execution overlay：long-short dollar-neutral、单日定时开平、maker-first 入场、`1m/3m/5m` TWAP/挂单退出、容量按窗口 ADV 缩放

## 4. 可复刻的最小实验
- 假设：`15:30–16:00 ET` 的相对强弱，在 crypto mid-caps 上会在随后的 `45~60` 分钟发生横截面反转。
- 定义：每天对候选池计算 `close-window return`，做 `long worst 1~2 / short best 1~2`，持有到 `17:00 ET`；先测 `16:00–17:00`，再测 `16:15–17:00`。
- 最小回测切口：Binance USDⓈ-M，`ADA/XRP/DOGE/AVAX/LINK/LTC`，`15m` bar，最近 `180~240d`；然后把信号触发后拆到 `5m/1m` 看 maker-first 能否保住 gross edge。
- 最该先看：`gross bps/day`、`Sharpe`，以及按 `2/4/6 bps` 单边 friction ladder 后的 survival；若净边仍薄，就把它降级成 router，而不是 standalone 主策略。

## 5. 风险与保留意见
- 这条信号对 **资产池选择** 很敏感：broad basket 几乎没边，mid-cap 才有口袋；所以最容易犯的错，就是把“局部 pocket”误读成“全市场稳定规律”。
- 它天然带强时间依赖，若交易所流动性结构或美股相关资金流变了，edge 可能会突然衰减。
- 目前 probe 只做了粗粒度 15m portability，还没把 funding、maker fill、排队失败、盘口冲击真正算进来；所以现在更像 **值得继续 admission check 的 raw alpha**，不是已可实盘确认的净利润策略。

## 6. 来源
- BNeillDickey. `intraday-crypto-reversal-project`.
- Repo URL: <https://github.com/BNeillDickey/intraday-crypto-reversal-project>
- Audited file: `Intraday_Crypto_Reversal_Project.ipynb`
- Related academic references cited in notebook: Heston, Korajczyk & Sadka (2010); Bogousslavsky (2016)
- Public data portability probe: Binance USDⓈ-M perpetual `15m` klines (`BTC/ETH/SOL/BNB/ADA/XRP/DOGE/AVAX/LINK/LTC`)
- Probe artifacts:
  - `reports/artifacts/quant_digests/us_session_xs_reversal_probe_summary_2026-04-22.csv`
  - `reports/artifacts/quant_digests/us_session_xs_reversal_close_daily_2026-04-22.csv`
  - `reports/artifacts/quant_digests/us_session_xs_reversal_morning_daily_2026-04-22.csv`
