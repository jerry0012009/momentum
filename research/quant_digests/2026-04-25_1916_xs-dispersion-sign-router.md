# 2026 新 repo：别把横截面动量/反转写死成单边信仰——更像一条 `dispersion sign router`
- 时间：2026-04-25 19:16 UTC
- 类型：GitHub / 研究回测仓
- 主题类型：raw alpha
- 基础 alpha：横截面过去一段时间的强弱排序；**分散度高时更像 winner continuation，分散度低时更像 loser→winner fade**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：cross-sectional / relative-value / momentum / mean-reversion / dispersion / sign-router / 15m / 5m / repo / public-data / cost / risk
- 证据类型：工程经验

## 1. 这次看了什么
看的是 `prams2104/crypto-momentum-backtest`（2026-02 更新）的完整研究仓：它不是只做“动量有没有效”，而是把 `20d xs momentum`、`1d xs reversal`、train/validation/OOS、transaction cost、dispersion regime 一起放进同一个可复跑框架里。

## 2. 核心结论
- 这仓最值钱的地方，不是“20 日动量”本身，而是提醒我们：**同一个 past-return 排名信号，符号可能随横截面分散度切换**。
- 作者日频结果里，`20d momentum` 在训练期年化 alpha 约 `36.2%`、`t-stat=2.02`，但验证/OOS 明显失效；相反 `1d reversal` 在 OOS 年化 alpha 约 `73.0%`、`t-stat=4.64`，却被高换手完全吃掉。
- repo 给出的关键解释是：2023 后横截面 dispersion 约收缩 `38%`，winner/loser 拉不开，动量 edge 跟着塌。
- 我补的 Binance USDⓈ-M `15m` portability probe（12 个 liquid majors，`24h` rank，7d rolling median dispersion split）里：**高 dispersion 子样本** 做 xs momentum 平均 gross 约 `+0.75 bps/bar`，但 net 约 `-0.67 bps/bar`；**低 dispersion 子样本** 做 xs reversal 平均 gross 约 `+2.48 bps/bar`、net 约 `+0.25 bps/bar`。
- 翻成人话：市场横截面如果“强弱差距很大”，更容易顺着强弱做；如果大家都挤成一团、分不太开，反而更像短期反弹/回吐游戏。

## 3. 为什么和当前项目有关
这和 `momentum` 当前主线直接相关，因为它不是又一个抽象 regime 讨论，而是在回答：**同一个 xs raw alpha，到底该顺着做还是反着做**。这比继续堆一个新 filter 更值钱——它直接扩充了 short-cycle 的 `cross-sectional / relative-value` 素材池。

## 3.5 策略拆解（必填）
- 方向属性：横截面 / 相对价值
- 基础 alpha：按过去 `N` 根收益对币池做 rank；买强卖弱（momentum）或买弱卖强（reversal）
- regime：横截面分散度（过去 `N` 根收益在币池内的离散程度）
- filter / veto：仅在 dispersion 明显高/低于 rolling 中位数时启用对应符号；中间区间可空仓
- risk / sizing / execution overlay：top/bottom 分组等权，next-bar 执行，按 turnover 扣成本；若要实盘，优先加流动性门槛和 child execution，避免高换手把 gross edge 吃光

## 4. 可复刻的最小实验
- 研究假设：`24h xs rank` 在 `15m` 上不是固定 momentum 或固定 reversal，而是由 rolling dispersion 决定符号。
- 一个可计算定义：`signal = close/close.shift(96)-1`；`dispersion = std(signal across universe)`；`dispersion > rolling_median(7d)` 做 winner-minus-loser，反之做 loser-minus-winner。
- 最小回测切口：Binance USDⓈ-M `BTC/ETH/BNB/SOL/XRP/DOGE/ADA/AVAX/LINK/DOT/UNI/LTC`，`15m` 主回测，再下沉到 `5m` 做 child execution。
- 最该先看：`gross/net bps per bar`、`turnover`；第二眼看 `high-disp` 与 `low-disp` 的 trade count 是否足够稳定。
- 下一步怎么测：先做 `24h / 12h / 6h` lookback × `15m/5m` 执行网格，再加 `dispersion tercile + liquidity veto + cooldown`，确认是否能把当前 low-disp reversal 的微弱 net edge 放大，而不是只在 gross 上好看。

## 5. 风险与保留意见
- 这类 xs sign router 最大问题不是“信号看不懂”，而是**换手太高**；repo 自己就展示了 gross alpha 能被成本直接打穿。
- 我这次 probe 仍是简化版：只做 top/bottom 等权、固定成本，没有 maker/taker、冲击和借券/资金费率细化。
- `dispersion` 很可能不是唯一 regime 变量，后面还该和 liquidity、相关性、funding crowding 一起做联合门控；否则容易把一次阶段性 market structure 误当长期规律。

## 6. 来源
- Pramesh / `prams2104`. (2026). *crypto-momentum-backtest*.
  - Readable URL: `https://github.com/prams2104/crypto-momentum-backtest`
  - Repo URL: `https://github.com/prams2104/crypto-momentum-backtest`
- 辅助文件：
  - `README.md`
  - `01_data.ipynb`
  - `02_signals.ipynb`
  - `03_backtest.ipynb`
- 本地 artifact：
  - `reports/artifacts/quant_digests/2026-04-25_dispersion_router_probe_summary.csv`
