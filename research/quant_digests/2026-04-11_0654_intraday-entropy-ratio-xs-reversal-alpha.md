# 别把这篇 2026 entropy 论文只读成 portfolio selection：对 short-cycle desk，更该先测的是「low-EntR structured loser-bounce」这条 cross-sectional raw alpha

- 时间：2026-04-11 06:54 UTC
- 类型：2026 *Computational Economics* 开放获取全文 + 原文 Table 4/5/6/7 + Binance USDⓈ-M `5m/15m` portability probe
- 主题类型：raw alpha
- 基础 alpha：**做多“最近一个 session 里跌了、但路径不算乱”的币，做空“最近一个 session 里涨了、且单位熵回报最高”的币；本质是 `return / intraday entropy` 排序驱动的 cross-sectional mean reversion / relative-value alpha。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-sectional/relative-value/mean-reversion/entropy/information-theory/structured-selloff/loser-bounce/market-neutral/session-book/binance-perpetual/5m/15m/paper/fulltext/public-data/cost/risk
- 证据类型：论文全文证据 + 公共数据 portability probe

## 1. 这次看了什么
主材料是：

- **David Neděla; Aleš Kresta (2026)**
- **Title:** *Applicability of Intraday Entropy for Trading During Regular Market Hours*
- **Venue:** *Computational Economics*
- **DOI:** `10.1007/s10614-026-11347-2`
- **Readable URL:** <https://link.springer.com/article/10.1007/s10614-026-11347-2>
- **PDF URL:** <https://link.springer.com/content/pdf/10.1007/s10614-026-11347-2.pdf>
- **Repo URL:** 无公开 repo

这篇 paper 表面上是在讲“entropy 能不能辅助 portfolio preselection”，很容易被读成一篇慢频组合构建文章。

但对我们 desk 更值钱的翻译，其实是：

> **不是所有 loser 都值得抄底；更该优先捞的是“跌了，但 intraday path 没那么乱”的 structured loser。**

也就是把作者的 `EntR = return / normalized intraday entropy`，读成：

> **`低回报 × 低熵` 代表 selloff 更结构化、噪声更少、下一期更可能出现 relative bounce。**

一句话核心结论：

> **别把这篇 paper 只读成 entropy 版 Sharpe ratio；对 short-cycle desk，更该先测的是「low-EntR losers → next-session relative reversal」这条横截面 raw alpha。**

一句话证明方式：

> **原文用 S&P 500 `1m` 数据做“收盘后按 EntR 排名、下个交易日开盘买入/收盘卖出”的完整策略；我再用 Binance USDⓈ-M majors 的公开 `5m/15m` 数据，分别测 session-to-session 版本和更激进的 bar-by-bar 压缩版，看这条线在 crypto 里到底更像可交易 alpha，还是只是好看的解释变量。**

## 2. 先回答最重要的一句：base alpha 到底是什么
这轮 base alpha 是清楚的，不需要硬掰成 filter：

> **cross-sectional structured loser-bounce** —— 上一个 session 里，**跌得最狠但 intraday entropy 还偏低** 的资产，下一期更容易相对反弹；相反，**涨得最多且单位熵回报最高** 的资产，下一期更容易相对回吐。

这不是单纯的：

- 只看谁跌得多；
- 也不是只看谁波动小；
- 更不是单纯 risk overlay。

它真正做的是：

> **用 entropy 把“有结构的价格路径”与“纯噪声乱晃”区分开，再对 return 做质量分层。**

所以它归类为 **raw alpha** 是成立的。

## 3. 原论文里，真正可拿走的是完整策略壳，不只是一个新指标名词
作者的策略定义很完整：

1. 对每只股票，在日内 `1m` returns 上算 Shannon entropy；
2. 把 entropy 按 `log(g)` 做归一化，得到 `Sh`；
3. 计算当日 `EntR = r_t / Sh_t`；
4. **收盘后**挑选 `EntR` 最低的 `v` 只股票；
5. **下个交易日开盘买入、收盘卖出**，等权持有；
6. 显式计入 **`1bp/day`** 比例交易成本。

也就是说，这篇材料不是只有“因子解释”，而是已经给了：

- entry：下个 session 开盘
- exit：下个 session 收盘
- sizing：等权
- risk：分散持有 `v=5/10/15/20/25/30`
- cost：`1bp/day`

这也是我把“是否可直接落地完整策略”打成 **是** 的原因：

> **至少在研究壳层面，它已经是完整策略，不只是半句 intuition。**

## 4. 原文最硬的几条结果
### 4.1 EntR 不是花哨命名；它对 return-only 和 std-only 都有增量
论文样本：

- 标的：S&P 500 成分股
- 数据：Yahoo Finance 抓取的 `1m` intraday data
- 区间：`2023-07-11` 到 `2024-10-23`
- 交易时段：只看美股 regular hours (`09:30–16:00 EST`)

作者的强结果不是一句“entropy 有用”，而是：

1. **EntR preselection 明显优于 benchmark。**
   - Table 4（含交易成本）里，`S1-100, v=25` 的日均收益约 **`0.0525%`**，`M/CVaR ≈ 2.8143`，`final wealth ≈ 1.2030`；
   - 同表的 `S&P 500` 仅约 **`-0.0042%`**，`final wealth ≈ 0.9853`；
   - `1/n` naive 组合约 **`-0.0121%`**，`final wealth ≈ 0.9582`。
2. **EntR 比“只看 return / std”更强。**
   - Table 5（mean/std）含成本时，表现最好的 `v=30` 约 `final wealth ≈ 1.1160`；
   - 明显低于 Table 4 中 `EntR` 的较优版本（约 `1.2030`）。
3. **EntR 比“只捞 loser”也更强。**
   - Table 6（只按 mean 预选）最好的一档约 `final wealth ≈ 1.1773`；
   - 仍弱于 `EntR` 的稳定版本。
4. **bins 不是越多越好。**
   - Table 7 和正文结论都指向：**`40~70 bins` 最稳**；
   - 太少（`10/20/30`）估计太粗，太多（`80+`）则因样本内 returns 数不够而恶化。

翻成人话：

> **真正值钱的不是“entropy 也能解释市场”，而是它比“只看跌得多”更会挑 rebound 候选，比“只看波动低”更接近下一期可交易排序。**

## 5. 为什么这东西和当前 desk 有直接关系
我们现在不是缺“宏大解释”，而是缺：

- 能补 raw alpha 素材池的横截面骨架；
- 能很快做 public-data first verdict 的排序壳；
- 能服务 `mean reversion / relative value / cross-sectional` 线路的统一评分器。

这篇 paper 正好补这 3 个空位：

1. **它是 raw alpha，不是泛 filter。**
   排名结果本身就能形成多空 book。
2. **它天然兼容 mean reversion / relative-value desk。**
   因为它本质上是在问：
   > 同样都跌了，哪个更像“被结构化抛过头”，哪个只是噪声里瞎晃？
3. **它有天然的 short-cycle desk 化改造空间。**
   不必死守“美股隔夜开收盘”，完全可以改写成：
   - `UTC session → next session`
   - `8h pseudo-session → next 8h`
   - 或者给已有 XS sleeves 做 admission rank。

## 6. 本地 portability probe：在 Binance `5m/15m` 上，这条线到底像不像 crypto alpha？
我做了两层快检。

本地 artifacts：

- `/root/clawd/jerry/momentum/reports/artifacts/literature/intraday_entropy_probe_summary_2026-04-11.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/intraday_entropy_probe_detail_2026-04-11_5m.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/intraday_entropy_probe_detail_2026-04-11_15m.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/intraday_entropy_probe_path_2026-04-11_5m.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/intraday_entropy_probe_path_2026-04-11_15m.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/intraday_entropy_intrabar_probe_summary_2026-04-11.csv`

### 6.1 Probe A：保留 paper 的“session-to-session”骨架，只把 intraday 输入换成 `5m/15m`
设定：

- 标的：`BTCUSDT / ETHUSDT / SOLUSDT / XRPUSDT`
- 数据：Binance USDⓈ-M 公共 `klines`
- 窗口：近约 `75` 个 UTC 日
- 做法：
  1. 每个 UTC 日内，用 `5m` 或 `15m` bar returns 估 `Shannon entropy`；
  2. 计算当日 `EntR = session return / normalized entropy`；
  3. 下一 UTC 日做 **long 最低 EntR / short 最高 EntR**；
  4. 与简单 `loser - winner` 排名做对照。

结果反而挺干净：

- **`5m` 输入：** `low-EntR minus high-EntR ≈ +9.14 bps/day`，胜率约 **`56.0%`**，近样本累计约 **`+7.10%`**；
- **`15m` 输入：** `low-EntR minus high-EntR ≈ +10.84 bps/day`，胜率约 **`54.7%`**，近样本累计约 **`+8.47%`**；
- 对照组 **简单 `loser - winner` 只有约 `-0.46 bps/day`**，几乎没有 edge。

更关键的是：

- 单独 long 最低 EntR 这条腿在这段市场里仍是负的；
- 但它**比简单抄底 loser** 和 **比等权 market beta** 都少亏不少。

也就是说，这条线在 crypto 里的 first verdict 更像：

> **先做 market-neutral cross-sectional sleeve，会比 long-only 抄底更靠谱。**

### 6.2 Probe B：把它硬压成 bar-by-bar `15m/5m` 信号，结果就没那么惊艳
为了确认它是不是能直接塞进最短周期，我又做了更激进的压缩版：

- `15m`：过去 `24` 根（约 `6h`）算 rolling EntR，下一根或未来 `4` 根持有；
- `5m`：过去 `72` 根（约 `6h`）算 rolling EntR，下一根或未来 `3` 根持有；
- 仍然是横截面 `long lowest Entr / short highest Entr`。

结果：

- **`15m` next-bar**：`Entr low-high ≈ +1.18 bps`，胜率约 **`54.5%`**；
- **`5m` next-bar**：约 **`+0.43 bps`**，胜率约 **`53.4%`**；
- 但这两者和**简单 cumret loser-winner 排名几乎没拉开**（`15m` 对照约 `+1.29 bps`，`5m` 对照约 `+0.42 bps`）；
- 一旦把持有期拉长，`15m hold 4` 与 `5m hold 3` 都明显转负。

翻成人话：

> **这篇 paper 的 alpha 更像“session book / next-session cross-sectional sleeve”，而不是每根 bar 都能直接压榨的 ultra-short engine。**

这不是坏消息，反而很重要，因为它告诉我们：

- **可以收进 raw alpha 素材池；**
- 但别误读成“新一代 5m bar-by-bar 圣杯”。

## 7. 对当前 desk，最合理的落点是什么
最合理的不是把它当：

- 单币方向预测器；
- 或万能 risk filter；
- 或任何时候都能跑的高速引擎。

更合理的落点是：

> **一个 session-level cross-sectional mean reversion sleeve。**

具体说：

- **alpha 本体：** low-EntR vs high-EntR
- **更适合的结构：** dollar-neutral / beta-neutral long-short
- **更适合的更新频率：** `UTC 日`、`8h pseudo-session`、或至少 `4h` 级别，而不是每根 `5m/15m` bar
- **更适合的用途：**
  1. 独立的 session book
  2. 给已有 loser-bounce / XS reversal book 做 admission rank
  3. 给 pairs / relative-value book 做 cross-sectional side selector

## 8. 策略拆解（必填）
- 方向属性：cross-sectional / relative-value / market-neutral / mean reversion
- 基础 alpha：`long lowest EntR (low return, low entropy) / short highest EntR`
- regime：更适合分化明显、但不是全 market 一边倒 trend day 的阶段
- filter / veto：重大事件日前后 veto；极低流动性币剔除；避免 funding 结算瞬时噪声窗口
- risk / sizing / execution overlay：等权或波动倒数权重；每侧 `top1/top2/top3` 稀疏持仓；优先 maker-ish execution；总 book 做 beta / dollar neutral

## 9. 最小可复现实验
### 数据源 / 公开性 / 更新频率
- Binance USDⓈ-M `fapi/v1/klines`
- 公开可抓，无需私有 key
- `5m / 15m` 均可直接拿到

### 最小研究假设
> 在 crypto majors 的横截面里，最近一个 session 内 **低回报但低熵** 的币，下一 session 更容易相对反弹；而单纯“跌得最多”的 loser 并没有同样干净的 edge。

### 最小回测切口
- 宇宙：`BTC / ETH / SOL / XRP / ADA / DOGE / LINK / AVAX` 先做 majors + liquid alts 两层
- ranking 频率：先测 `UTC 日`，再测 `8h` pseudo-session
- 指标：
  - `session return`
  - `normalized Shannon entropy`
  - `EntR = return / entropy`
- 组合：
  1. `top1-bottom1`
  2. `top2-bottom2`
  3. `tercile long-short`
- 成本：先跑 `2 / 4 / 6 bps` friction ladder

## 10. 下一步怎么测
1. **先别继续压到每根 bar。**
   第一优先级是把 ranking 频率改成 `UTC 日 / 8h / 4h` 三档，而不是继续把它塞进 next-bar。
2. **做更大的币池，但保留 liquidity split。**
   先把 `BTC/ETH` 与 `SOL/XRP/LINK/AVAX/ADA/DOGE` 分开，看 edge 是否主要集中在 alt sleeve。
3. **显式比较 3 个对照组。**
   - `EntR low-high`
   - `plain loser-winner`
   - `low-vol loser-winner`
   这样才能确认 entropy 的增量到底来自“结构化路径”还是只是低波动 proxy。
4. **把 exit 从 next-session close 扩成 partial clip。**
   如果 alpha 真是 structured loser-bounce，更合理的出场未必是一次性平仓；优先测 `50% at half-session + 50% at session close`。
5. **跟已有 XS reversal sleeves 做 pairwise compare。**
   不是为了再造一个重复因子，而是要确认：这条线到底能不能替代“只看 loser rank”，或者至少能成为更好的 admission 层。

## 11. 我这轮的结论
如果只看原论文，会很容易得出一个平庸结论：

> entropy 可以帮助 portfolio selection。

但对我们 desk，更值钱的结论是：

> **EntR 真正像的是“structured loser-bounce”横截面 raw alpha。**

而本地 crypto quick check 给出的 first verdict 也挺明确：

- **session-to-session 版本值得继续测；**
- **bar-by-bar 压缩版暂时别高估；**
- **最自然的落点是 market-neutral XS sleeve，不是 long-only 抄底。**

所以这篇东西值得进研究池，但正确姿势不是“每根 5m bar 都按 entropy 冲”，而是：

> **先把它当成 session-level cross-sectional raw alpha / router，看它能不能稳定打赢 plain loser rank。**

## 12. 来源
- Neděla, David; Kresta, Aleš. (2026). *Applicability of Intraday Entropy for Trading During Regular Market Hours*. *Computational Economics*.
  - DOI: <https://doi.org/10.1007/s10614-026-11347-2>
  - Readable URL: <https://link.springer.com/article/10.1007/s10614-026-11347-2>
  - PDF URL: <https://link.springer.com/content/pdf/10.1007/s10614-026-11347-2.pdf>
  - Repo URL: 无公开 repo
- 本地 portability artifacts：
  - `/root/clawd/jerry/momentum/reports/artifacts/literature/intraday_entropy_probe_summary_2026-04-11.csv`
  - `/root/clawd/jerry/momentum/reports/artifacts/literature/intraday_entropy_probe_detail_2026-04-11_5m.csv`
  - `/root/clawd/jerry/momentum/reports/artifacts/literature/intraday_entropy_probe_detail_2026-04-11_15m.csv`
  - `/root/clawd/jerry/momentum/reports/artifacts/literature/intraday_entropy_probe_path_2026-04-11_5m.csv`
  - `/root/clawd/jerry/momentum/reports/artifacts/literature/intraday_entropy_probe_path_2026-04-11_15m.csv`
  - `/root/clawd/jerry/momentum/reports/artifacts/literature/intraday_entropy_intrabar_probe_summary_2026-04-11.csv`
