# 别把这份 2026 walk-forward crypto stat-arb repo 只读成日频 Kraken 回测：对 short-cycle desk，更该先测的是「short-half-life liquid-alt pair admission × 15m spread z-score fade」这条 raw alpha

- 时间：2026-04-13 16:59 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `cryptoarb/pairs.py` + `cryptoarb/signals.py` + `cryptoarb/config.py`）+ Binance USDⓈ-M `15m` public-data portability probe
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/walk-forward/engle-granger/half-life/rolling-ols/zscore/liquid-alt/binance-perpetual/15m/5m/repo/public-data/cost/risk
- 证据类型：源码规则 + 公共数据 first verdict

- 主题类型：raw alpha
- 基础 alpha：**先在 liquid perp universe 里做“短半衰期协整 pair 准入”，再对通过准入的 spread 做 rolling-OLS `z-score` 回归交易；本体不是单币方向，而是两条腿相对错位后的收敛。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1. 先把一句话说清楚：这篇东西的 base alpha 是什么？

> **base alpha = short-half-life cointegrated spread mean reversion。**

这份 repo 表面上像一个“带 walk-forward 回测、但近年 OOS 结果并不好看”的日频 stat-arb 工程；真正对我们 desk 有价值的，不是它在 Kraken `1d` 上那条负收益净值，而是它把一条 **pairs raw alpha 完整壳** 拆得足够清楚：

1. 先做相关性 + Engle-Granger + half-life 的 pair admission；
2. 再用 rolling OLS 估 hedge ratio，构造动态 spread；
3. 最后在 `|z|` 足够大时做 fade，在 `|z|` 收回时退出，并给 stop / cost / vol-scaling 留了明确接口。

翻成人话：
- 不赌 `DOGE` 或 `AVAX` 单边涨跌；
- 而是赌 **两条强相关腿之间的错位会收敛**；
- 贵的一腿空、便宜的一腿多；
- 等相对关系回去就平仓。

所以这不是 `filter / overlay`，它本体就是一条 **可独立交易的 relative-value raw alpha**。

## 2. 这次看了什么

### 主来源（repo）
- **作者：** Atharva Joshi（GitHub: `atharvajoshi01`）
- **年份：** 2026
- **标题：** *crypto-stat-arb*
- **Venue：** GitHub repository
- **Repo URL：** <https://github.com/atharvajoshi01/crypto-stat-arb>
- **Readable URL：** <https://github.com/atharvajoshi01/crypto-stat-arb/blob/main/README.md>
- **创建/最近更新：** `2026-04-13` 创建；`2026-04-13T16:54:13Z` pushed
- **关键文件：**
  - README：<https://raw.githubusercontent.com/atharvajoshi01/crypto-stat-arb/main/README.md>
  - Pair discovery：<https://raw.githubusercontent.com/atharvajoshi01/crypto-stat-arb/main/cryptoarb/pairs.py>
  - Signal generation：<https://raw.githubusercontent.com/atharvajoshi01/crypto-stat-arb/main/cryptoarb/signals.py>
  - Config：<https://raw.githubusercontent.com/atharvajoshi01/crypto-stat-arb/main/cryptoarb/config.py>

### 方法地基（paper）
- **Engle, Robert F., & Granger, Clive W. J. (1987).** *Co-integration and Error Correction: Representation, Estimation, and Testing.* *Econometrica*.
- **DOI：** <https://doi.org/10.2307/1913236>
- **Readable URL：** <https://www.jstor.org/stable/1913236>

### 本轮自建 probe
- 宽宇宙扫描：`reports/artifacts/quant_digests/2026-04-13_crypto-stat-arb-15m-transfer/pair_scan_wide_30d.csv`
- 候选 pair：`reports/artifacts/quant_digests/2026-04-13_crypto-stat-arb-15m-transfer/candidate_pairs.csv`
- 信号摘要：`reports/artifacts/quant_digests/2026-04-13_crypto-stat-arb-15m-transfer/signal_probe_summary.csv`
- 成本阶梯：`reports/artifacts/quant_digests/2026-04-13_crypto-stat-arb-15m-transfer/cost_ladder_summary.csv`

## 3. 一句话核心结论 + 一句话证明方式

### 一句话核心结论
> **这份 repo 最值得 desk 接的，不是它 README 里那条日频负收益曲线，而是“short-half-life pair admission × 15m spread fade”这条完整 raw alpha 壳；它在宽 liquid-alt 宇宙里能筛出一小撮可交易 pocket，但只有低摩擦版本能过线。**

### 一句话证明方式
> **证明不是靠 README 自夸，而是靠源码拆解 + Binance USDⓈ-M `15m` 公共数据快检：20 个 liquid alt / major perp 里，190 个组合最终只有 8 对通过“短半衰期协整”准入；再加成本后，`4 bps` 仍有 4 对为正，`8 bps` 只剩 3 对勉强为正，`12 bps` 全灭。**

## 4. 为什么这轮值得写

虽然 index 里已经有很多 pairs / stat-arb digest，但这轮仍然有补充价值，原因在于它补的不是“又一篇 z-score 教程”，而是三件更贴近当前 desk 的东西：

1. **它是一个很新的完整工程壳。**
   - 不是只给 pair 名单；
   - 而是把 `pair discovery → signals → portfolio → risk → costs → walk-forward` 都写成模块。

2. **它的 README 很诚实。**
   - Kraken `2021-2026`、OOS `2025-02` 到 `2026-01`；
   - README 直接给出 `Annual Return -18.8%`、`Sharpe -2.56`，不是只贴最漂亮区间。
   - 对我们反而有价值，因为它逼着我们从“全市场长期壳”缩到“短周期可交易 pocket”。

3. **它天然适合做短周期 first verdict。**
   - admission 是统计准入；
   - execution 是 spread 偏离后的均值回归；
   - 公开 Binance perp K 线就足够做一版 `15m` 最小实验。

## 5. repo 真正提供了什么

### 5.1 Pair admission
`pairs.py` 这条链很清楚：
- 先做相关性预筛（默认 `min_correlation = 0.70`）
- 对候选 pair 做 Engle-Granger / ADF
- 再按 half-life 过滤（默认 `3 ~ 30`，repo 原语义是天）
- 最后按 ADF 统计量排序

对 short-cycle desk 来说，最该抄的不是默认“天”这个单位，而是：

> **先做准入，再做交易。**

也就是不要一上来对任意两条腿跑 z-score，而要先问：
- 它们最近是不是仍够相关？
- 残差是不是仍平稳？
- 回归速度是不是快到值得做短周期？

### 5.2 Signal 壳
`signals.py` 给的是很干净的最小规则：
- `z > +entry_z` → short spread
- `z < -entry_z` → long spread
- `|z| < exit_z` → flat
- `|z| > stop_z` → stop
- rolling window = `window_multiplier × half_life`

默认参数：
- `entry_z = 2.0`
- `exit_z = 0.5`
- `stop_z = 4.0`
- `window_multiplier = 2.0`

这个设计对我们尤其重要，因为它不是“拍脑袋固定 60 bars z-score”，而是把窗口长度和 **pair 自己的回归速度** 绑在一起。

### 5.3 完整策略外壳
`config.py` 还给了：
- 单 pair 权重上限
- gross exposure 上限
- taker fee / slippage 成本位
- portfolio / pair drawdown stop
- volatility scaling
- recoint frequency
- walk-forward train / test / step 切分

所以它不是只有 alpha 点子，而是一个 **可直接落地的 complete shell**。

## 6. public-data portability probe：落到今天 Binance `15m` 后还剩什么？

### 6.1 本轮最小实验口径
我没有照搬 repo 的日频 Kraken 口径，而是改成更适合 short-cycle desk 的版本：

- **市场：** Binance USDⓈ-M perpetual
- **周期：** `15m`
- **样本：** 最近 `30d`
- **Universe：** 20 个 liquid alt / major perp（含 `ETH/SOL/XRP/DOGE/ADA/LINK/AVAX/BNB/SUI/LTC/BCH/DOT/TRX/1000PEPE/WIF/AAVE/ETC/APT/NEAR/ATOM`）
- **Admission：**
  - pair 两腿 log-price 相关性 `> 0.85`
  - Engle-Granger ADF `p < 0.05`
  - half-life in bars 落在 `4 ~ 64`
- **Execution：**
  - rolling OLS hedge ratio
  - `entry = |z| > 2`
  - `exit = |z| < 0.5`
  - `stop = |z| > 4`
  - rolling window = `2 × half_life`
- **PNL 近似：**
  - 先做 beta-adjusted spread return
  - 再加 `4 / 8 / 12 bps` round-trip 成本阶梯

### 6.2 先记最重要的 4 个数

#### 数 1：`190` 个组合里，只有 `8` 对通过短周期准入
这说明 repo 这套东西如果直译到 `15m`，**不是“全市场到处都有 alpha”**，而是明显要靠 admission 层硬筛。

#### 数 2：最强 pocket 是 `LINKUSDT / AVAXUSDT`
- 相关性：`0.9661`
- ADF `p = 0.00056`
- half-life：`51.1` bars（约 `12.8h`）
- `30d` 内入场次数：`43`
- 毛 `avg bps/bar = +0.153`
- `4 bps` 成本后：`+0.092 bps/bar`，累计约 `+2.56%`
- `8 bps` 成本后：仍有 `+0.031 bps/bar`

这组是真正像 desk 可以先盯的 pocket：
- 不算超高频；
- 但回归速度已从“天级”压到了“半天级”；
- 成本不太高时还能活。

#### 数 3：`DOGEUSDT / SUIUSDT` 与 `DOGEUSDT / LTCUSDT` 也勉强存活
- `DOGE/SUI`：`4 bps` 后 `+0.069 bps/bar`，`8 bps` 后 `+0.013 bps/bar`
- `DOGE/LTC`：`4 bps` 后 `+0.066 bps/bar`，`8 bps` 后 `+0.013 bps/bar`

说明：
- 不止一组 pocket；
- 但 edge 很薄，明显只能在 **低摩擦 / 低冲击** 口袋里做。

#### 数 4：`12 bps` round-trip 下全部转负
这件事比任何单个好看的 Sharpe 都更重要：

> **这条线不是“随便 taker 一把都能吃到”的 broad alpha，而是“低摩擦 selective pairs pocket”。**

## 7. 这条线和已有 pairs digest 的差别在哪

这轮和 index 里已有的 pairs 主题相比，新增价值主要在三点：

1. **不是老论文或脚本，而是一个今天刚更新的完整 walk-forward 工程。**
2. **不是先讲最漂亮 pair，而是先接受 README 里的负 OOS，再反推哪些短周期 pocket 值得保留。**
3. **不是只讲“有无协整”，而是把“half-life 压到 bar 级别”当 admission 主条件。**

所以更准确的读法是：

> **这不是 another generic pairs note，而是一条“day-level stat-arb 工程 → short-cycle pocket 提炼”的迁移笔记。**

## 8. 策略拆解（entry / exit / sizing / risk / cost）

### 8.1 Entry
- Universe 先做 liquid perp 筛选
- pair admission：`corr > 0.85`、`ADF p < 0.05`、`half-life ∈ [4,64] bars`
- 通过后在 `15m` 上跑 rolling OLS spread
- `z > 2`：short spread
- `z < -2`：long spread

### 8.2 Exit
- `|z| < 0.5` 平仓
- `|z| > 4` 强平
- 可加 `time stop = 2 × half-life`

### 8.3 Sizing
- 先用 beta-neutral notional
- 组合层先做 equal-risk across active pairs
- 单 pair 上限建议保留 repo 的 `max_pair_weight` 思路

### 8.4 Risk
- pair break：滚动重做 admission，失效即踢出
- `pair drawdown stop`
- `portfolio drawdown stop`
- vol scaling 只在通过 first verdict 后再接，不要一开始用它美化一条本来不过线的 pair

### 8.5 Cost
- 必须用双腿 round-trip 成本
- 先跑 `4 / 8 / 12 bps` friction ladder
- 若 `8 bps` 已明显转负，默认不把它当 taker alpha 主线

## 9. 我对这条线当前的判断

### 当前判定
- **raw alpha 候选：是**
- **能否独立复现：能**
- **能否直接落地完整策略：能，但必须是 selective / low-friction 版本，不是 broad all-market taker 版**

### 该怎么放进素材池
优先级我会放在：
- **高于** 单纯 filter / overlay
- **低于** 那些在 `8~12 bps` 下仍稳健为正的强 edge
- 最合适的定位是：
  - **pairs raw alpha / complete shell / admission-first**

## 10. 下一步怎么测（必须项）

不要先做更复杂的 ML。先把下面这个最小实验做干净：

### 10.1 最小实验
**研究假设**
- 若先在 `15m` / `30m` 上滚动做 short-half-life admission，再只交易 `8 bps` 仍不转负的 pair，则少数 liquid-alt pairs 能形成可持续的 low-friction spread MR pocket。

**具体动作**
1. Universe 扩到 top `30~40` liquid perp
2. 每 `4h` 或每天重跑一次 admission
3. 先固定使用：
   - `corr > 0.85`
   - `ADF p < 0.05`
   - `half-life 4~64 bars`
4. 对 surviving pairs：
   - `15m` 做 entry / exit
   - `5m` 只拿来细化 exit，不拿来重新发现 pair
5. 成本固定先跑：`4 / 8 / 12 bps`

### 10.2 最该先看的 3 个指标
1. `8 bps` 后仍为正的 **surviving pair ratio**
2. **post-cost mean trade pnl**
3. **rolling positive-window ratio**（不是只看全样本）

### 10.3 如果要继续往 `1m / 3m` 走
我的建议不是把 admission 也压到 `1m / 3m`，而是：
- **admission 仍放 `15m / 30m`**
- **`1m / 3m` 只做 execution refinement / close-out timing**

原因很简单：
- 协整与半衰期判断本来就更怕噪声；
- `1m / 3m` 更适合决定“怎么退”，不适合决定“这对腿值不值得做”。

## 11. 一句话结论

> **把这份 2026 repo 读成 short-cycle desk 语言后，最值得保留的不是“日频 market-neutral 组合”这个大叙事，而是“short-half-life liquid-alt pair admission × 15m spread fade”这条 selective raw alpha 壳；它有 pocket，但 edge 很薄，必须先过低摩擦筛选。**
