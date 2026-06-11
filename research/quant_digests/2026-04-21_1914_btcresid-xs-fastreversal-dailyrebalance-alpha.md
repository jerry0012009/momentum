# 别把这份 crypto stat-arb 仓只读成“reversal + momentum 拼盘”：对 short-cycle crypto desk，更该先拆的是「BTC 残差化横截面 loser→winner fade × 低频再平衡」这条 raw alpha
- 时间：2026-04-21 19:14 UTC
- 类型：GitHub / repo source audit + Binance USDⓈ-M public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：先把各币种收益对 `BTC` 做滚动残差化，去掉大盘同涨同跌那一层；再在横截面里做 **短窗 loser→winner fade**，也就是做空刚刚相对涨得太多的、做多刚刚相对跌得太多的
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：cross-sectional / relative-value / mean-reversion / stat-arb / BTC residualization / inverse-vol / daily rebalance / Binance / 15m
- 证据类型：repo 工程骨架 + public-data first probe

## 1. 这次看了什么
这轮主来源是一个 2026 GitHub 研究仓：**ccollins80 / crypto-stat-arb**。它表面上在讲“crypto 里的 reversal + momentum 两条 sleeve 怎么混”，但对我们这个 short-cycle desk，真正值得 intake 的不是整个慢速组合，而是它里面那条更硬、更容易最小复现的 **BTC 残差化横截面反转壳**。

一句话先回答用户要求的 base alpha：

> **这篇东西的 base alpha 是什么？**
>
> **答：是 BTC 残差化后的 cross-sectional short-horizon reversal。**
>
> 也就是：先把“跟着 BTC 一起动”的共振部分剥掉，再去抓币与币之间的短期相对过冲回归。

### 来源
- **Repo**：ccollins80 (2026), *Crypto Statistical Arbitrage*
- **Repo URL**：<https://github.com/ccollins80/crypto-stat-arb>
- **Readable URL**：<https://github.com/ccollins80/crypto-stat-arb/blob/main/README.md>
- **关键代码**：
  - `src/crypto_stat_arb/signals.py`
  - `src/crypto_stat_arb/backtest.py`
  - `src/crypto_stat_arb/portfolio.py`

## 2. repo 里真正可交易的壳是什么
repo 的写法很清楚：
- **reversal sleeve**：
  - 对收益先做 `BTC` 滚动残差化
  - 用过去 `k` 根 bar 累积收益做横截面 z-score
  - 取负号，等于 **做空短期相对赢家 / 做多短期相对输家**
  - 加 `band`，只有过冲够大才入场
  - 再做 `inverse-vol` 缩放与 L1 中性化
- **portfolio / execution**：
  - 权重下一根执行，避免 lookahead
  - 用 `downsample_weights(every=N)` 把组合改成低频再平衡，不是每根乱切
  - 成本按 turnover 直接扣

如果翻成人话，这条壳不是“所有币都跟大盘一起跌了，然后抄底”。它更像：

1. **先剥掉 BTC 大盘方向**，只看各币自己的相对偏离；
2. **再在同一时点横向比较谁偏离得最夸张**；
3. **只在偏离足够大时动手**；
4. **用低频再平衡压 turnover**，别让本来就薄的 edge 被手续费吃光。

这对当前 desk 很对路，因为它补的是：
- `mean reversion`
- `cross-sectional / relative value`
- `stat-arb`

而不是再来一个单币 breakout / retest 变体。

## 3. repo 给出的原始证据
repo README 里公开给出的结论大概是：
- `12` 个 liquid crypto pairs
- 小时级数据，样本约 `2.6` 年
- **reversal sleeve** 最优附近：`k=4`、`band=2.5`、`beta_win=168`、`vol_win=24`、`every=24`
- 报告的 **net Sharpe ≈ 1.77**，年化收益约 `36.6%`，年化波动约 `20.7%`
- turnover 约 `89/年`
- 成本假设是每次再平衡约 `7 bps`

repo 还给了一个 slow momentum sleeve，以及 equal-vol mix。但这部分对我们当前 `5m/15m` 主线不应直接照抄，因为：
- slow momentum 更偏慢周期资产配置层
- equal-vol mix 好看，不代表搬到 `15m` 就还好看
- 真正先该测的，是 **快腿 reversal 壳在短周期能不能留下净边**

## 4. 为什么这条壳和最近 digest 不算重复
最近虽然已经连续做过多个 cross-sectional / pairs / relative-value 主题，但这篇仍然有一个明确新增量：

### 4.1 不是普通 loser→winner fade，而是 **先做 BTC residualization**
这一步的作用很朴素：
- 如果所有币都只是跟着 BTC 一起冲高或一起跳水，
- 那么横截面反转里很多“过冲”其实只是大盘 beta，
- 不先剥掉，就很容易把 market shock 误读成 relative-value dislocation。

### 4.2 不是高频乱调仓，而是 **过冲 admission + 低频再平衡**
repo 的 `band + every=N` 非常 desk-friendly。
它不是在追求“每根都要有仓”，而是在追求：
- 只有横截面偏离够大才入场
- 中间用持仓延续压 turnover

这比很多纯学术横截面 reversal 更接近可交易版本。

## 5. 我们自己的 `15m` public-data first probe
### 5.1 probe 口径
我用 Binance USDⓈ-M public klines 做了一个轻量可复现实验：
- 市场：Binance USDⓈ-M perpetual
- universe：`BTC/ETH/SOL/BNB/XRP/DOGE/ADA/LINK`
- 周期：`15m`
- 样本：`2026-03-09 01:15 UTC ~ 2026-04-21 19:00 UTC`，共 `4200` 根 bar 左右
- 残差化：对 `BTCUSDT` 做滚动 beta 残差化，`beta_win=672`（约 `7d` 的 `15m` bar）
- fast reversal：
  - `k=16`（约 `4h`）
  - `band=2.0`
  - `vol_win=96`（约 `1d`）
  - `every=96`（日频再平衡）
- 成本：`4 bps` one-way 粗代理
- 额外也顺手测了：
  - slow momentum sleeve（更慢 lookback + 周频再平衡）
  - equal-vol mix

### 5.2 结果
摘要文件：
- `reports/artifacts/quant_digests/2026-04-21_btcresid_fastrev_slowmom_probe_summary.csv`

核心数字：
- **fast reversal sleeve**
  - gross 约 `+0.0276 bps/bar`
  - net 约 `+0.0203 bps/bar`
  - **net Sharpe ≈ 1.52**
  - 累计 net 约 `+0.84%`
  - 平均日换手约 `0.175`
- **slow momentum sleeve**
  - net 约 `-0.1340 bps/bar`
  - **net Sharpe ≈ -5.76**
  - 累计 net 约 `-5.51%`
- **equal-vol mix**
  - net 约 `-0.0531 bps/bar`
  - **net Sharpe ≈ -4.40**
  - 累计 net 约 `-2.21%`

## 6. first verdict：这轮到底该 intake 什么
### 6.1 该 intake 的不是整个 repo，而是 **fast reversal sleeve**
如果按我们 desk 的标准讲人话：

- **能先进入素材池的，是那条 BTC 残差化横截面 fast reversal**
- **不该直接搬进素材池的，是 slow momentum 和 equal-vol mix**

也就是说，这篇东西最有价值的不是“组合看起来很漂亮”，而是它告诉我们：

> 在 short-cycle 上，**去 beta 后的横截面过冲回归** 还有机会；
> 但把 slow momentum 强行拼进来，不一定会让 `15m` 更好，反而可能把净边拉没。

### 6.2 这条 alpha 的第一性逻辑
这条壳能成立，核心不是神秘因子，而是三句话：
1. crypto 横截面经常一起被 BTC 拖着跑；
2. 真正的 relative-value 过冲，要先把这层共振去掉；
3. 去掉以后，短期相对最极端那几只，常有一点回归压力。

### 6.3 low-frequency rebalance 很关键
这轮 probe 一个很重要的正面信号是：
- 日频再平衡下，换手没有爆炸；
- cost 扣完后仍是正的；
- 说明这条壳至少没一上来就死在 friction 上。

这点比很多“看起来 gross 很强但 turnover 爆炸”的 reversal 候选更实用。

## 7. 策略拆解（按 desk 可落地口径）
### 7.1 entry
在每个再平衡点：
1. 取最近 `k` 根 bar 的收益；
2. 对每个币相对 `BTC` 做滚动残差化；
3. 算横截面 z-score；
4. 只保留 `|z| >= band` 的币；
5. **long 最负 z-score 一侧，short 最正 z-score 一侧**。

### 7.2 exit
- 默认到下一个再平衡点再统一更新；
- 如果下一次 ranking 后信号消失，自动平掉；
- 可以额外补一个 `max-hold` 或 `zero-cross`，但本轮最小实验先不加花。

### 7.3 sizing
- 先按 z-score 强度给方向
- 再按 rolling vol 做 `inverse-vol` 缩放
- 最后做横截面去均值 + L1 归一，保证 market-neutral / dollar-neutral

### 7.4 risk
- `BTC` 残差化是第一层 risk cleaning
- `band` 是 admission gate
- `every=N` 是 turnover gate
- 可额外加：单币权重上限、事件日禁入、成交量门槛

### 7.5 cost
- repo 基线：`7 bps` 每次调仓
- 本轮 quick probe：`4 bps` one-way 粗代理
- 下一轮必须补 `0 / 2 / 4 / 6 / 8 bps` ladder

## 8. 这条 alpha 和当前 short-cycle desk 的关系
这轮主题值钱的地方在于，它不是：
- 单币 trend
- 单币 breakout
- 单币 RSI 超卖

而是明确补了我们更需要的另一支：
- **cross-sectional / relative-value / stat-arb / mean-reversion**

更具体地说，它适合扮演两个角色：
1. **独立 raw alpha**：直接做 market-neutral loser→winner fade
2. **shared selector**：给其他单币壳提供“当前谁最偏离”的横截面 admission

## 9. 下一步怎么测
1. **把 `15m` 父信号拆成 `5m/3m` child execution。**
   先不要改父信号逻辑，只优化 child entry：
   - `next-bar market`
   - `VWAP-half-hour`
   - `maker-first for 1~3 bars then cross`
   比较净边能不能从 `+0.0203 bps/bar` 再抬一点。

2. **把 `band` 做成明确的 turnover frontier。**
   至少扫：`1.0 / 1.5 / 2.0 / 2.5 / 3.0`。
   这类策略常见现象不是“没 alpha”，而是“alpha 太薄，band 不够高就被摩擦吃掉”。

3. **把 universe 从 7 个 alt 扩到 12~20 个 liquid perp。**
   横截面策略最怕池子太小。下一轮应加入更多高成交量永续，避免几只大币决定全局。

4. **加入 funding / basis veto，而不是直接改 base alpha。**
   如果某个币的相对过冲，背后其实是 funding 或 basis 在重定价，那么纯价格反转可能会被 carry 持续顶住。这个 veto 适合做第二层，不要一开始就和主信号缠死。

5. **补一个更实盘的风险口径。**
   下一轮至少看：
   - 单边拥挤时的权重上限
   - 事件窗口（CPI/FOMC/大额解锁）禁入
   - 单币 liquidity gate

## 10. 风险与提醒
- 当前正向证据只算 **first probe**，样本不到两个月，不能吹成稳定 alpha。
- 本轮正向的是 fast reversal sleeve，不是整个 repo 的慢速组合。
- `BTC` 残差化虽然能去掉部分共振，但也可能在强趋势市里把真实可赚 beta 一起剥掉；因此别默认它永远优于原始收益排序。

## 11. 一句话收尾
**这篇 repo 最值得留下的，不是“reversal + momentum 组合很漂亮”，而是：先剥掉 BTC 共振，再做横截面 loser→winner fade，这条 short-cycle relative-value 壳在 `15m` 上至少还没有被成本立刻判死刑。**
