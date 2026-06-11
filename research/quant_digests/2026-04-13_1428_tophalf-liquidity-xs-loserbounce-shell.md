# 别把这份 2026 4H spot repo 只读成“动量 vs 反转 notebook”：对 short-cycle desk，更该先拆的是「top-half-liquidity XS loser-bounce」这条完整 raw alpha 壳——但 `5m/15m` taker 版远不过成本线

- 时间：2026-04-13 14:28 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `src/crypto_statarb.py` + bundled PDF report）+ Binance USDⓈ-M `15m/5m` public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：`做空过去 H 根横截面最强币、做多过去 H 根横截面最弱币，赌短周期 cross-sectional loser-bounce / winner-cooldown 会回归；liquidity top-half 只是 admission/filter，不是 alpha 本体`
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-sectional/relative-value/mean-reversion/liquidity-filter/volume-rank/top-half-admission/loser-bounce/winner-cooldown/market-neutral/cost-ladder/binance-perpetual/15m/5m/repo/public-data/cost/risk
- 证据类型：开源代码 + 自带报告 + 公共数据 portability probe

## 1. 这次看了什么

这轮主看的是 GitHub 仓库 **Jamestilfords / statarb-crypto (2026)**。它最表面的读法是：

> “一个 4H Binance spot 上的横截面 momentum vs reversal notebook。”

但真正更适合我们 desk 拿来拆的，不是“它也比较了 momentum”，而是这条更明确、也更可复刻的骨架：

> **base alpha = cross-sectional short-horizon reversal。**
>
> 每个 bar 按最近 `H` 根累计收益给币做横截面排序，**long 最弱的一档、short 最强的一档**，赌的是下一段短周期里 loser bounce / winner cooldown 的回归；`top-half volume rank` 只是降低薄币噪声与执行摩擦的 **filter**，不是 alpha 本体。

所以这轮它是：
- `raw alpha`
- 不是 `filter`
- 不是 `regime`
- 也不是单纯的 `risk overlay`

而且它还不是“只给一个信号名词”。repo 里把：
- signal 定义
- long/short 组合构建
- 1-bar lag
- turnover cost
- liquidity admission
- cost stress
都写成了比较完整的策略壳。

## 2. 一句话核心结论 + 一句话证明方式

### 一句话核心结论
> **这份 repo 确实给出了一条可独立复现、且接近完整策略壳的 cross-sectional reversal raw alpha；但把它压到今天的 Binance USDⓈ-M `15m/5m` taker 口径后，gross 虽仍为正，净后却很快被换手吃穿，说明它更像 maker / 低费率 / 降频版本的候选，而不是现成可上线的 taker 主策略。**

### 一句话证明方式
> **repo 自带 4H spot 回测里，`H=3` reversal 在 `20bps` 仍显著为正；我再用 Binance USDⓈ-M `15m/5m` 公开 K 线，先对更宽 liquid universe 做 unfiltered stress，再对 `12` 个 liquid majors 做 top-half-liquidity 版最小实验，看到 gross 上都还有边，但一加 `4~8bps` 成本几乎全部翻成深负。**

## 3. repo 里到底写了什么

### 3.1 alpha 定义非常清楚，不靠脑补
`src/crypto_statarb.py` 里核心定义基本已经把 base alpha 写死了：

- `reversal_score(rets, H) = -(rets.rolling(H).sum())`
- `make_long_short_weights(...)`：
  - long top `q` 分位
  - short bottom `q` 分位
  - 组内等权
- `backtest_unconstrained(...)`：
  - `1-bar lag`
  - 按 `turnover * cost_bps` 扣成本
  - 非 rebalance bar 持仓前推
- `make_long_short_weights_masked(...)`：
  - 只在 `tradable=True` 的资产上排名，作为 liquidity filter

翻成人话：

> **它不是预测绝对涨跌，而是在赌“横截面上刚刚最弱的会反弹，刚刚最强的会冷却”，然后做一个 equal-weight market-neutral spread。**

### 3.2 repo 自带结果为何值得看
README / 自带报告里给的 4H spot 结果是：

- universe：Binance USDT spot liquid names
- reversal lookback：`H ∈ {1,2,3,6}`
- rebalance：每天一次（4H bar 上 `rebalance_every=6`）
- cost：baseline `20bps`
- unfiltered best：**`H=3 (~12h)`**
- README 给出的 cost ladder（unfiltered `H=3`）：
  - `20bps`：**Sharpe 3.596 / CAGR 2.062 / FinalEquity 28.704x**
  - `40bps`：**Sharpe 0.159 / CAGR -0.004 / FinalEquity 0.989x**
  - `60bps`：**Sharpe -2.910 / CAGR -0.677 / FinalEquity 0.034x**

这组数最有价值的地方不是“4H spot 真好做”，而是它已经提前告诉我们：

> **这条 alpha 对 turnover / fee 极度敏感。**

也就是说，它天然就该被 desk 读成：
- **完整 raw alpha 壳**：是
- **可直接拿去做 taker**：不一定
- **必须先做 friction ladder**：是

## 4. 为什么它跟当前 desk 直接相关

### 4.1 它补的是我们此轮明确想补的 raw alpha 方向
这不是再回到单币 breakout / retest / shape-only 内循环；它补的是：

- `cross-sectional`
- `relative-value`
- `market-neutral`
- `short-horizon mean reversion`

这正是当前 intake 里要求主动补的家族。

### 4.2 它是少数把完整壳写得比较干净的 repo
这份 repo 对 short-cycle desk 的价值，不只是“反转因子存在”，而是已经把下面几层拆开了：

- alpha 本体：`xs loser-bounce / winner-cooldown`
- filter：`volume rank top-half`
- sizing：双边等权 gross-one
- execution：1-bar lag
- cost：turnover-based bps ladder

所以它不是“一个模糊灵感”，而是一个可以很快进入 **first verdict** 的完整壳。

### 4.3 它还能顺便回答一个很现实的问题
很多 short-cycle raw alpha 的死因不是没方向感，而是：
- gross 有一点
- turnover 更大
- net 立刻翻负

这份 repo 正适合拿来做这种边界判断。

## 5. 我做的 `15m/5m` 最小 portability probe

### 5.1 口径
为了回答“这条壳能不能压到我们 desk 的短周期上”，我把 probe 分成了两步：

**A. 先看 unfiltered gross / cost 边界（更宽横截面）**
- universe：`BTC/ETH/SOL/BNB/XRP/ADA/DOGE/LINK/AVAX/LTC/DOT/TRX/BCH/SUI/APT/NEAR/ETC/UNI/ATOM/XLM`
- 频率：`15m`（近 `90d`）
- 组合：每根 bar 横截面排序，`long bottom 20% / short top 20%`
- 目的：先回答“这条 raw alpha 在更宽 liquid universe 上，gross 还在不在”

**B. 再看 desk 更关心的 top-half liquidity admission**
- universe：`BTC/ETH/SOL/BNB/XRP/ADA/DOGE/LINK/AVAX/LTC/DOT/TRX`
- 频率：`15m`（近 `60d`）+ `5m`（近 `14d`）
- 信号：`reversal_score = -过去 H 根收益和`
- 版本：`top-half liquidity`（按 quote volume 排前 50%；在 12 币池里等价于约 6 个名字；为避免横截面塌缩，最小可交易资产数放宽到 `6`）
- 成本：`0 / 4 / 8 / 12 / 20 bps`

这两步合起来，分别回答：
1. **alpha 本体在更宽横截面上是不是还活着**
2. **把 liquidity admission 接回 desk 口径后，能不能救到净收益**

### 5.2 15m：gross 有，net 没有
#### A. 更宽横截面的 unfiltered quick stress（20 币、90d、平均 8 个 active names）
先看 alpha 本体，不加 liquidity admission 时，gross 其实是存在的：

- `H=2`：**gross +0.71 bps/bar**, `avg_turnover 1.14`
- `H=4`：**gross +0.68 bps/bar**, `avg_turnover 0.84`
- `H=6`：**gross +0.62 bps/bar**, `avg_turnover 0.72`

但一旦加 taker 成本就迅速翻负：

- `H=4 @ 8bps`：**net -6.06 bps/bar**
- `H=6 @ 8bps`：**net -5.10 bps/bar**
- `H=8 @ 8bps`：**net -4.43 bps/bar**

所以第一层 verdict 很清楚：

> **alpha 本体没死，但 short-cycle taker 直译版已经被 turnover 压穿。**

#### B. desk 口径的 top-half liquidity admission（12 币、60d、平均 2 个 active names）
放宽最小资产数后，liquidity filter 不是没用——它在 gross 上甚至更顺：

- `H=8 @ 0bps`：**gross +0.69 bps/bar**, Sharpe **8.57**
- `H=6 @ 0bps`：**gross +0.66 bps/bar**, Sharpe **8.21**
- `H=3 @ 0bps`：**gross +0.55 bps/bar**, Sharpe **6.97**

但问题是 turnover 仍不低：

- `H=8`：`avg_turnover 0.85`
- `H=6`：`avg_turnover 0.92`
- `H=3`：`avg_turnover 1.22`

所以：

- `H=8 @ 4bps`：**net -2.72 bps/bar**
- `H=6 @ 4bps`：**net -3.01 bps/bar**
- `H=3 @ 4bps`：**net -4.34 bps/bar**
- `H=8 @ 8bps`：**net -6.13 bps/bar**

**结论：filter 能提高 gross 质量，但远不足以单独救 taker economics。**

### 5.3 5m：更像“gross 还行、摩擦更糟”
#### top-half liquidity（约 6 币、平均 2 个 active names）
`14d` probe 的 gross 结果也不是零：

- `H=1 @ 0bps`：**gross +0.255 bps/bar**, Sharpe **11.36**
- `H=12 @ 0bps`：**gross +0.135 bps/bar**, Sharpe **5.68**
- `H=3 @ 0bps`：**gross +0.117 bps/bar**, Sharpe **5.14**

但 `5m` 的核心问题更直白：**turnover 太大**。

- `H=1`：`avg_turnover 1.74`
- `H=3`：`avg_turnover 1.25`
- `H=12`：`avg_turnover 0.88`

因此一到 `4bps` 就明显不行：

- `H=1 @ 4bps`：**net -6.70 bps/bar**
- `H=12 @ 4bps`：**net -3.40 bps/bar**
- `H=12 @ 8bps`：**net -6.94 bps/bar**

**一句话：`5m` 比 `15m` 更像“有 gross、没执行空间”。**

## 6. 这轮最重要的判断

### 6.1 它是 raw alpha，而且是完整壳，不需要降级成 filter
这点要先说死：

> **base alpha 很清楚，就是 cross-sectional short-horizon reversal。**

所以它不是“只适合作为某个别的 alpha 的过滤器”的材料，而是一个：
- 可独立复现
- 可明确写出 entry/exit/sizing/risk/cost
- 能进入 replication 素材池

的 **完整 raw alpha shell**。

### 6.2 但 short-cycle 直译版只剩低摩擦口袋
repo 在 4H spot 日度 rebalance 上能活，一个关键原因是 **turnover 远低于我们 5m/15m 直译版**。

这轮 probe 的核心不是“alpha 完全失效”，而是：

- gross edge：**存在**
- filter 改善 gross：**存在**
- 但当前 `5m/15m` taker 版净后：**明显不行**

换句话说，它更像：
1. `maker-first` 候选
2. `更低 rebalance 频率` 候选
3. `更宽 alt universe` 候选
4. 或者 `shared cross-sectional rank feature`

而不是今天就能直接挂到 taker 主 book 上的策略。

### 6.3 “liquidity filter”别误读成万能修复器
这轮一个很有用的副结论是：

> **top-half liquidity filter 会提升 gross 质量，但如果同时把横截面压得太窄、而且换手没有同步大幅下降，它救不了成本。**

所以后续如果继续做这条线，应该把 liquidity filter 当成：
- admission quality 提升器
- 非 executable alpha -> executable alpha 的必要条件之一

而不是充分条件。

## 7. 下一步怎么测

这轮必须给明确 next step，我建议按下面顺序推进：

1. **先测“降频不降信号”**
   - 保留同一套 `xs reversal rank`
   - 但把 rebalance 改成 `每 2 / 3 / 4 根 bar` 才更新一次
   - 核心看：gross 掉多少、turnover 掉多少、net 能不能翻正
   - 这是当前最优先，因为 repo 原始胜点本来就部分来自更低换手

2. **把 universe 扩到 `30~50` 个 liquid alts，再重跑 top-half liquidity**
   - 现在 12 币池做 top-half，只剩约 6 个可交易名字，横截面太窄
   - 更合理的做法是：先扩大 universe，再做 top-half admission
   - 重点看：gross dispersion 是否放大，且 turnover 是否不同比例上升

3. **只在 rank 极端时入场，不要每根 bar 全量重排**
   - 例如只交易 `|rank z|` 或 `cross-sectional spread percentile` 最极端的一档
   - 目标是减少“轻微信号也强制换仓”的无效 churn

4. **把它改成 shared rank feature，接入别的 relative-value book**
   - 若完整壳始终过不了成本，可以降级为：
     - pair admission
     - basket admission
     - continuation / reversal router
   - 也就是：先保留 `xs reversal rank` 的信息量，不强求它单独做 book

## 8. 风险与保留意见

- 这轮 portability 只用了 `12` 个 liquid majors perpetual，**很可能低估** 这类策略在更宽 alt universe 上的横截面离散度。
- probe 用的是 public kline + 简化 turnover cost，没有模拟 maker queue、rebate、内撮、滑点异质性；对低摩擦账户来说，结论可能没这么悲观。
- `5m` 只看了近 `14d`，更像 quick first verdict，不是最终 OOS 认证。
- repo 原始环境是 spot `4H` + 日度 rebalance；把它压成 `5m/15m` 本来就是主动做高强度 stress，不应把 portability 失败误读成“原始 alpha 不存在”。

## 9. 本地 artifacts

- `reports/artifacts/quant_digests/xs_liquidity_reversal_probe_15m_2026-04-13.csv`
- `reports/artifacts/quant_digests/xs_liquidity_reversal_probe_5m_2026-04-13.csv`
- `reports/artifacts/quant_digests/xs_liquidity_reversal_tophalf6_probe_15m_2026-04-13.csv`
- `reports/artifacts/quant_digests/xs_liquidity_reversal_tophalf6_probe_5m_2026-04-13.csv`
- `reports/artifacts/quant_digests/xs_liquidity_reversal_probe_summary_2026-04-13.json`

## 10. 来源

1. **Jamestilfords (2026), _Crypto Statistical Arbitrage (4H Binance Spot): Momentum vs. Short-Horizon Reversal_**
   - Venue: GitHub repository / bundled report
   - DOI: N/A
   - Readable URL: `https://github.com/Jamestilfords/statarb-crypto`
   - Repo URL: `https://github.com/Jamestilfords/statarb-crypto`
   - Raw README: `https://raw.githubusercontent.com/Jamestilfords/statarb-crypto/main/README.md`
   - Core source: `https://raw.githubusercontent.com/Jamestilfords/statarb-crypto/main/src/crypto_statarb.py`
2. **Bundled report in repo**
   - `Report/Statistical Arbitrage in Cryptocurrencies (4H Bars).pdf`
3. **Binance USDⓈ-M public market data**
   - Klines: `https://fapi.binance.com/fapi/v1/klines`
