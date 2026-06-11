# 别把这份 intraday crypto repo 只读成 close-reversal 笔记：对 short-cycle desk，更该先测的是「US ETF close-window BTC-vs-ETH relative-strength continuation」这条 cross-market raw alpha

- 研究时间：2026-04-01 17:20 UTC
- 主题类型：raw alpha
- 基础 alpha：美股上市 crypto ETF 在收盘前 / 收盘后 30 分钟形成的 **BTC complex vs ETH complex 相对强弱**，会在后续 `30m~60m` 延续；可直接映射成 `BTC perp vs ETH perp` 的 relative-value continuation。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 类型标签：raw-alpha/cross-market/relative-value/us-etf/btc-vs-eth/close-window/after-hours/momentum/yfinance/crypto-etf/ibti-fbtc-etha-feth/5m/15m/3m/1m/repo/public-data/cost

---

## 1. 这次看了什么

这次主材料仍来自 **BNeillDickey (2026)** 的 GitHub notebook：

- **Author / Year / Title / Venue**: BNeillDickey, 2026, *intraday-crypto-reversal-project*, GitHub research notebook
- **Readable URL**: https://github.com/BNeillDickey/intraday-crypto-reversal-project
- **Repo URL**: https://github.com/BNeillDickey/intraday-crypto-reversal-project
- **核心文件**: `Intraday_Crypto_Reversal_Project.ipynb`

但这轮不再重复前面已经 intake 过的 **spot crypto US-session reversal**，而是专门拎出 notebook 里另一条更适合 desk 的旁支：

> **US-listed crypto ETF 的 close-window / after-hours momentum。**

更准确地说，不要把它理解成“ETF 自己还能不能赚”。对我们更有价值的读法是：

- `IBIT / FBTC` 基本就是 **BTC beta 壳**；
- `ETHA / FETH` 基本就是 **ETH beta 壳**；
- 所以 notebook 的横截面 momentum，在这 4 个 ETF 上很大程度等价于：
  **BTC complex 是否正在持续跑赢 ETH complex，或反过来。**

这就能直接转译成 crypto desk 更熟悉的 trade：

- **long BTC perp / short ETH perp**
- 或 **long ETH perp / short BTC perp**

在一个很窄、很明确的 U.S. close / after-hours 时间 pocket 内，做短周期 relative-value continuation。

---

## 2. Base alpha 到底是什么

一句话先答：

> **base alpha 是 U.S.-listed crypto ETF 的 close-window / after-hours 相对强弱延续，不是 filter，不是解释变量。**

具体定义成 desk 可执行语言，就是：

1. 在纽约时间 `15:30–16:00` 或 `16:30–17:00`，观察 BTC ETF basket（`IBIT`,`FBTC`）与 ETH ETF basket（`ETHA`,`FETH`）谁更强；
2. 如果 BTC complex 明显更强，则下一段做 **BTC > ETH**；
3. 如果 ETH complex 明显更强，则下一段做 **ETH > BTC**；
4. 持有 `30m~60m`，不拖成隔夜宏观叙事。

翻成人话：

**不是赌“ETF 会带动 crypto”这种大而空的故事，而是赌一个很短的、可量化的资金接力：收盘前 / 收盘后先赢的那一边，下一段还会继续赢。**

---

## 3. 为什么它比继续补一个泛 filter 更值得

因为这次不是在补共享 gate，而是在补一条**能独立成策略卡**的 cross-market raw alpha：

- 有明确 **entry**（固定时间窗口后的 winner/loser）；
- 有明确 **exit**（下一段 `30m` 或 `60m`）；
- 有明确 **sizing**（BTC-vs-ETH dollar-neutral 或 beta-neutral）；
- 有明确 **risk shell**（只做固定 pocket，不做全天）；
- 有明确 **cost shell**（ETF 侧已有 7bps/side 假设，crypto 侧可重建 maker/taker ladder）。

而且它对当前 desk 的意义不是“再多一个美股相关 story”，而是：

- 给 `BTC-vs-ETH` 这条最容易落地的 RV 书补一个 **U.S. close pocket**；
- 给 `1m / 3m / 5m / 15m` 的 execution pipeline 补一个 **外部公开、低接入门槛、分钟级可取** 的 trigger；
- 给已有的 **QQQ/NVDA lead-lag** 之外，再补一个**更贴近 crypto underlier 本身**的美股侧 price-discovery 信号。

---

## 4. Notebook 里最重要的硬数据

### 4.1 数据面板

Notebook 直接拉了美股上市 crypto ETF：

- `IBIT`
- `FBTC`
- `ETHA`
- `FETH`

主面板范围：

- **日内 60m 面板**：`2024-02-26 → 2026-02-25`
- 面板大小：`8311 x 4`

补充验证：

- **5m pre/post market 面板**：约最近 `60d`
- 面板大小：`10385 x 4`
- 范围：`2025-11-28 → 2026-02-25`

数据源是公开可得的 `yfinance` / Yahoo Finance prepost bars，门槛极低。

### 4.2 主策略窗口：收盘前 30m → 收盘后 60m

Notebook 的 primary ETF window 是：

- **signal**：`15:30–16:00`（纽约时间）
- **hold**：`16:00–17:00`

结果：

- **ETF close-window reversal**: `SR = -7.01`（500 days）
- **ETF close-window momentum**: `SR = 3.29`（500 days）

这很关键：

> **在 ETF 这条支线上，close-window 有效读法不是 reversal，而是 momentum。**

也就是说，别把前面 spot crypto 的 close-window fade 机械平移过来；
同一个 U.S. session，**ETF 这边表现出来的是“强者继续强、弱者继续弱”**。

### 4.3 分 BTC / ETH complex 看，效果没塌

更关键的是，分资产壳之后信号没有消失：

- **BTC ETFs post-launch momentum SR = 3.72**（500 days）
- **ETH ETFs post-launch momentum SR = 4.17**（398 days）

这说明它不是靠某一只 ETF 的 idiosyncratic 噪声堆出来，
而更像是 **同一 underlier complex 的系统性延续**。

### 4.4 全窗口 sweep：最强 pocket 在 after-hours

Notebook 对三个 session zone 一共扫了 **612** 组窗口 / mode 组合。

Top pocket：

- **after_hours / ALL / 16:30–17:00 signal / 17:00–17:30 hold / momentum / SR = 8.62 / 494 days**

其他高分 pocket：

- `17:30–18:00 -> 18:00–18:30`, momentum, `SR = 7.97`
- `15:30–16:00 -> 16:00–17:00`, momentum, `SR = 3.29`
- `11:00–11:30 -> 11:30–12:00`, momentum, `SR = 2.91`

但 notebook 也非常诚实：

> **Best after-hours SR 8.62 ← TC may be understated in AH**

所以正确读法不是“8.62 直接上实盘”，而是：

- after-hours pocket 很可能真有 alpha；
- 但 ETF 真实 AH spreads 可能让 paper SR 被高估；
- 对 crypto desk 来说，真正该做的是把这条信号**转到流动性更连续的 BTC/ETH perp** 上复核。

### 4.5 5m 验证：最强 after-hours pocket 没有完全塌掉

Notebook 又用约最近 60 天的 `5m` pre/post market 数据，对最强 pocket 做了更细粒度验证：

- **AH best (60m top)** `16:30–17:00 -> 17:00–17:30`
  - momentum `SR = +2.37`
  - reversal `SR = -6.87`
  - `n = 56 days`
- **Anchor close-momentum** `15:30–16:00 -> 16:00–17:00`
  - momentum `SR = +1.60`
  - reversal `SR = -7.95`
  - `n = 58 days`
- **AH alt** `16:00–16:30 -> 16:30–17:00`
  - momentum `SR = -0.60`
  - reversal `SR = -7.88`
  - `n = 58 days`

这组结果最重要的不是绝对数值，而是：

1. **最强 pocket 在 5m 上仍然为正，并且仍是 momentum 读法；**
2. 不是所有 after-hours pocket 都有效，说明它不是“只要美股收盘就乱冲”这么粗；
3. alpha 很可能集中在**更窄、更靠后的 after-hours 接力窗口**。

---

## 5. 这条 alpha 怎么转成 crypto desk 的最小可交易版本

### 5.1 最 deskable 的转译：BTC-vs-ETH perp relative-value

不要直接照搬 ETF 横截面四资产权重。

更适合我们 desk 的转译是：

- 定义 BTC ETF basket return：`r_BTCETF = mean(r_IBIT, r_FBTC)`
- 定义 ETH ETF basket return：`r_ETHETF = mean(r_ETHA, r_FETH)`
- 定义相对强弱：`spread_sig = r_BTCETF - r_ETHETF`

交易规则：

- 若 `spread_sig > q`：做 `long BTC perp / short ETH perp`
- 若 `spread_sig < -q`：做 `long ETH perp / short BTC perp`
- 若 `|spread_sig| <= q`：不做

这里的 `q` 不要先拍死，先用历史分位数：

- `60%`
- `70%`
- `80%`
- `90%`

### 5.2 时间 pocket 先只测两档

第一阶段别扫太多：

**Pocket A（anchor）**
- signal: `15:30–16:00 ET`
- hold: `16:00–17:00 ET`

**Pocket B（best AH）**
- signal: `16:30–17:00 ET`
- hold: `17:00–17:30 ET`

再映射到 crypto bar：

- `5m`：最自然
- `15m`：能先测 alpha existence
- `3m / 1m`：只做 execution refinement，不要一开始就上

### 5.3 sizing / risk / cost 壳

建议第一版直接用最朴素的 relative-value 壳：

- **notional-neutral**：`|BTC leg| = |ETH leg|`
- 或 **vol-neutral**：按过去 `N=48` 根 `5m` realized vol 做反比缩放
- 每次只持有一段，不做滚动加仓
- 不跨过第二个时段，不讲 overnight 故事

成本先做三档：

- maker-ish: `2 + 2 bps`
- hybrid: `4 + 4 bps`
- taker-ish: `6 + 6 bps`

如果在 `4+4bps` 以上已死，就不要往后讲大故事。

---

## 6. 它和已有主线材料的区别

这条卡和我们已经做过的几类东西不同：

1. **不同于 US-session spot reversal**：
   - 那条是 spot crypto 自己在 U.S. session pocket 的横截面反转；
   - 这条是 ETF 侧 **relative-strength continuation**。

2. **不同于 QQQ/NVDA lead-lag**：
   - 那条是 broad tech / semis 对 crypto 的跨资产带动；
   - 这条更近一步，直接是 **crypto underlier 自己的股票化壳** 在带节奏。

3. **不同于纯 filter**：
   - 这里不是“只有满足条件才做别的 alpha”；
   - 它本身就能单独跑成 `BTC-vs-ETH` 的短周期 RV 策略。

---

## 7. 目前最该担心的坑

### 7.1 ETF after-hours 成本低估

这个 notebook 自己已经明说了：

- `SR = 8.62` 的 AH pocket，**TC 可能被低估**。

所以这条卡最危险的误读是：

> “ETF 回测这么好，直接按 ETF after-hours 去做。”

正确做法是：

- 把 ETF 视为 **信号源**；
- 把 perp 视为 **执行层**；
- 重新做 crypto 侧成本壳。

### 7.2 实际上只有两个 underlier

四个 ETF 名字看起来像横截面，
但本质只有两类 underlier：BTC 和 ETH。

所以不要把它误读成“大 universe cross-sectional strategy”；
它更像：

- **BTC vs ETH 的二元 relative-strength state machine**。

### 7.3 时间映射必须用纽约时区，不要偷懒写死 UTC

这条卡天然和 U.S. cash / after-hours 绑定。
如果直接写死 UTC，而不处理 DST，后面很容易把 pocket 对错。

---

## 8. 最小实验设计（直接给 bot / 研究脚本用）

### 8.1 数据

**公开可得**：

- ETF：Yahoo Finance / yfinance `5m`，`prepost=True`
- Crypto：Binance / Bybit / OKX perpetual `1m` 或 `5m`

### 8.2 信号

对每个纽约交易日：

1. 聚合 ETF bars 得到：
   - `r_BTCETF(sig_window)`
   - `r_ETHETF(sig_window)`
2. 计算：
   - `spread_sig = r_BTCETF - r_ETHETF`
3. admission：
   - 只有 `|spread_sig|` 超过 rolling `70%~90%` 分位才开仓

### 8.3 交易

- 若 `spread_sig > q`：`long BTC perp / short ETH perp`
- 若 `spread_sig < -q`：`long ETH perp / short BTC perp`
- `entry`: signal window 结束后的下一根 `5m`
- `exit`: 固定 `30m` 或 `60m`
- `stop`: 第一版先不要加 discretionary stop，先看 fixed-hold raw alpha 是否存在

### 8.4 输出指标

至少看：

- annualized Sharpe
- avg pnl per trade / per day
- hit rate
- max drawdown
- turnover
- cost sensitivity
- 按 pocket 分桶的 monotonicity

---

## 9. 下一步怎么测

1. **先做 transfer test，不要先做 full production backtest。**
   - 用 ETF `15:30–16:00` 和 `16:30–17:00` 两个 signal pocket，
   - 去打 `BTC perp vs ETH perp` 在后续 `30m/60m` 的收益差。

2. **先测 admission threshold，而不是先卷复杂 sizing。**
   - `|spread_sig|` 分位从 `60/70/80/90` 四档扫；
   - 看 edge 是否只在尾部 pocket 才存在。

3. **优先看 5m，再下钻 1m/3m。**
   - `5m` 用来验证 alpha existence；
   - `1m/3m` 只用来微调入场位置和 cost。

4. **做一个“ETF signal only / crypto execution only”的诚实版本。**
   - ETF 负责生成方向；
   - crypto perp 负责成交；
   - 别把 ETF 与 perp return 混在一起回测，避免把信号层和执行层搅糊。

---

## 10. 一句话结论

**这份 notebook 里更值得 desk intake 的，不是前面已经讲过的 spot close-window reversal，而是另一条可独立成卡的 cross-market raw alpha：用 U.S.-listed crypto ETF 在 close / after-hours 的 BTC-vs-ETH 相对强弱，去驱动后续 `30m~60m` 的 BTC-vs-ETH perp continuation。**
