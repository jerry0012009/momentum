# 别把 4h spot loser-bounce Sharpe 直接搬进 perp：这份 2026 新 repo 更该先测的是「12h 横截面 short-term reversal + liquidity filter + cost cliff」完整 raw alpha
- 时间：2026-03-26 04:49 UTC
- 类型：2026 GitHub 新仓库 + 2022 crypto intraday reversal literature + Binance Futures 公共 `15m/1h` 最小快检
- 主题类型：raw alpha
- 基础 alpha：横截面 short-term reversal——过去 `H` 个 bar 里跌得最狠的一篮子更容易反弹、涨得最快的一篮子更容易回吐；liquidity filter 与 cost ladder 只是决定它能不能活，不是 alpha 本体
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-sectional/mean-reversion/short-term-reversal/liquidity-filter/cost-cliff/transfer-check/binance/spot/perpetual/15m/1h/4h/repo/paper
- 证据类型：新仓库代码与 README 结果 + 近 5 年论文旁证 + 本地公共数据最小快检

## 1. 这次看了什么
先回答 base alpha：**这篇东西的 base alpha 很清楚，就是 cross-sectional short-term reversal，不是 liquidity filter，也不是“成本研究”。**

这次看的主材料是 2026 新仓库 `Jamestilfords/statarb-crypto`。它最值得 desk intake 的地方，不是“又一个 stat-arb repo”，而是把一条很朴素的 **loser-basket bounce / winner-basket give-back** 写成了完整策略骨架：`top/bottom 20%`、`1-bar lag`、`daily rebalance on 4H bars`、`turnover cost`、`top-50% volume` 过滤，全都明牌。

对我们现在的研究节奏，这很重要：最近 desk 已经堆了不少 `pairs / basket / basis / funding / lead-lag` 线，但仍然需要持续补这种**规则简单、能快复刻、能直接看成本断崖**的 raw alpha 母体。

## 2. 核心结论
- **一句话核心结论：** 这份 repo 证明的不是“动量也行、反转也行”，而是更具体的一句——**在它那份 4H Binance spot 样本里，能站住的是约 `12h` formation 的横截面短反转，但它有非常陡的 cost cliff。**
- repo README 给的最关键数字很直白：
  - momentum sweep 在该样本里 **全为负**；
  - reversal 里 **`H=3`（约 `12h`）最好**；
  - 在 **20 bps** 成本下，`H=3` 的 **Sharpe ≈ 3.596、CAGR ≈ 206%、MaxDD ≈ -26.1%**；
  - 但到 **40 bps** 时几乎被吃光，**60 bps** 直接判死。
- 对 desk 更值钱的分支，不是“spot 上结果多亮眼”，而是它把 raw alpha 和生存条件拆得很清楚：
  1. alpha body = `- recent H-bar return` 的横截面排序；
  2. liquidity filter 只是减少薄币换手；
  3. 真正决定能不能上线的，是 **turnover × cost cliff**。
- 我补的 Binance Futures 公共数据快检说明：**这条 4H spot reversal 不能直接下沉成 `15m/1h` perp always-on alpha。**
  - `1h` 版本（12 个高流动 USDT perp、60 天、top-half volume filter）里，最好的是 **`H=12`**，但在 **8 bps** 下仍然只有 **Sharpe ≈ -3.04、总收益 ≈ -15.4%**；即便降到 **4 bps**，也只是 **约 -3.6%**，接近“没死透但也不值得上”。
  - `15m` 版本更差：最好的是 **`H=16 + top-half volume filter`**，在 **8 bps** 下 **Sharpe ≈ -20.64、总收益 ≈ -20.3%**；即便 **4 bps** 也还是 **约 -7.5%**。

## 3. 为什么和当前项目直接相关
- 这是标准 **raw alpha**，而且是那种最适合放进素材池做基准线的 raw alpha：规则简单、公开数据可拿、entry/exit/cost 都能明写。
- 它和最近 desk 已有的 `24h loser basket`、`lottery fade`、`high-vol loser` 不是重复关系，而是**补一条更完整的“策略母体”**：
  - 不是只给一个排序特征；
  - 而是连 rebalance、lag、turnover、liquidity filter 都写出来了。
- 更关键的是，它给了一个很实用的研发提醒：**短反转不是不能做，而是不能偷懒地把中频 spot 结果直接压缩成 fast perp bar-bar alpha。**

## 3.5 策略拆解（必填）
- 方向属性：cross-sectional / market-neutral / short-term mean reversion
- 基础 alpha：`alpha_i,t = - rank(sum(return_i, t-H+1:t))`
- entry：每个调仓点按最近 `H` 个 bar 收益做横截面排序，做多 bottom quantile，做空 top quantile
- exit：下一次调仓时整体换篮；repo 原型是 **4H bar + 每 6 根 bar（日频）调仓 + 1-bar lag**
- sizing：多空两侧等权，再缩放到 gross = 1
- risk：可加 **top-50% volume rank** 过滤，减少薄币和难成交名字
- cost：先跑 turnover-based `20 / 40 / 60 bps`（repo）；映射到 perp fast-lane 时至少要补 `4 / 8 / 12 / 20 bps`

## 4. 本地最小快检（Binance 公共数据，transfer check）
我这轮不去复刻 repo 的原样 spot 全宇宙，而是先回答 desk 更关心的问题：**这条 raw alpha 能不能直接服务 `1m/3m/5m/15m`？**

- 数据源：Binance USDⓈ-M Futures 公共 K 线 API
- 公开性：公开可得，无需私有权限
- 更新频率：交易所 bar 级更新
- 宇宙：`BTC / ETH / SOL / XRP / DOGE / BNB / ADA / SUI / 1000PEPE / LTC / LINK / AVAX`
- 口径：
  - 横截面 long bottom / short top，单边 `25%` 分位；
  - `1-bar lag`；
  - `1h` 版本每 `6` 根 bar 调仓；`15m` 版本每 `4` 根 bar 调仓；
  - 同时测试 `top-half volume rank` 过滤。

### 4.1 `1h` bridge test
- 样本：`2026-01-25 04:00 UTC` 到 `2026-03-26 04:00 UTC`
- 最好的只是 `H=12 + volume filter`
- 结果：
  - `8 bps`：**Sharpe ≈ -3.04，total return ≈ -15.4%，MaxDD ≈ -19.1%**
  - `4 bps`：**Sharpe ≈ -0.54，total return ≈ -3.6%**

翻成人话：**把 repo 那条中频 spot reversal 先压到 `1h` perp，已经基本不剩像样 edge。**

### 4.2 `15m` fast-lane test
- 样本：`2026-03-12 04:45 UTC` 到 `2026-03-26 04:45 UTC`
- 最好的只是 `H=16 + volume filter`
- 结果：
  - `8 bps`：**Sharpe ≈ -20.64，total return ≈ -20.3%**
  - `4 bps`：**Sharpe ≈ -7.23，total return ≈ -7.5%**

这基本是在说：**别把它当 15m/perp 的 ready-made alpha。**

## 5. 最小可复现实验（面向下一轮）
### 方案 A：先忠实复刻它的“中频 raw alpha”
- 市场：Binance spot 或低 funding 干扰的 perp proxy
- 周期：`4h`
- formation：`H = 1 / 2 / 3 / 6`
- rebalance：每 `6` 根 `4h` bar
- hold：直到下次调仓
- cost：`20 / 40 / 60 bps`
- 目的：先确认 repo 报告的 **`H=3` + cost cliff** 是否站得住

### 方案 B：再做 desk 化映射，而不是一步压到 15m
- 用 `12h formation → 4h/2h execution` 做 bridge
- 保留横截面 loser/winner 篮子，但改成：
  - 更慢 rebalance
  - 更严格 liquidity bucket
  - BTC beta / market beta 中和
- 只有这步活下来，才值得继续下沉到 `15m` 执行切片

## 6. 下一步怎么测（必须）
1. **先做 repo faithful replication。** 不要只看 README 数字；先在 spot 或尽量接近 spot 的 universe 上把 `H=3` 与 cost ladder 重跑一遍。  
2. **把“formation horizon”和“execution horizon”解耦。** 现在失败的，很可能不是 alpha 本体，而是把中频 formation 粗暴压成 fast rebalance。  
3. **补 beta-neutral / residual 化版本。** 快周期 perp 里，winner/loser 很容易只是 market beta 漂移，不做中和会把反转信号污染成追 beta。  
4. **按 liquidity bucket 拆开看。** majors、midcaps、meme/peripheral coins 很可能不是同一条 alpha。  
5. **做 no-overlap path 与真实 turnover 归因。** 当前最小快检已经足够说明 transfer 很差，但正式版要把换手来源拆出来。  
6. **只有当 `4h → 1h` bridge 能过成本后，才考虑 `15m` slicing。** 否则别再让这条线占 fast-lane 的主资源。  

## 7. 风险与保留意见
- repo 是 **2026 新仓库**，当前更像高信号研究 intake，不是已经被社区充分验证的成熟策略。  
- 本地快检是 **perp + majors universe + 轻量回测骨架**，不是 repo 原样复刻；它回答的是“能不能直接下沉到 desk fast-lane”，不是否定 repo 原结论。  
- 当前证据更像：**这条 raw alpha 可能属于中频/低换手 pocket，而不是 `15m` always-on perp alpha。**  

## 8. 来源
1. **Jamestilfords (2026). _Crypto Statistical Arbitrage (4H Binance Spot): Momentum vs. Short-Horizon Reversal_. GitHub repository.**  
   - Authors / Handle: `Jamestilfords`  
   - Year: `2026`  
   - Venue: GitHub repository  
   - DOI: 无  
   - Readable URL: `https://github.com/Jamestilfords/statarb-crypto`  
   - Repo URL: `https://github.com/Jamestilfords/statarb-crypto`  
   - 备注：README 明确给出 reversal sweep、cost sensitivity、bucket diagnostic、train/test split 与 liquidity filter。

2. **Wen, Z., Bouri, E., Xu, Y., & Zhao, Y. (2022). _Intraday return predictability in the cryptocurrency markets: Momentum, reversal, or both_. The North American Journal of Economics and Finance.**  
   - Venue: The North American Journal of Economics and Finance  
   - DOI: `10.1016/j.najef.2022.101733`  
   - Readable URL: `https://doi.org/10.1016/j.najef.2022.101733`  
   - Repo URL: 无  
   - 作用：提供 crypto intraday momentum / reversal 并存、且依赖 horizon 的文献旁证。

3. **Binance Developers. _USDⓈ-M Futures API – Kline/Candlestick Data_.**  
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`

## 9. 本地复现产物
- `reports/artifacts/quant_digests/repo_xs_reversal_cost_cliff_20260326/summary.json`
- `reports/artifacts/quant_digests/repo_xs_reversal_cost_cliff_20260326/15m_reversal_summary.csv`
- `reports/artifacts/quant_digests/repo_xs_reversal_cost_cliff_20260326/15m_cost_ladder.csv`
- `reports/artifacts/quant_digests/repo_xs_reversal_cost_cliff_20260326/1h_reversal_summary.csv`
- `reports/artifacts/quant_digests/repo_xs_reversal_cost_cliff_20260326/1h_cost_ladder.csv`

## 10. 一句话 verdict
**可以进研究池，但当前更适合被归类为“4h spot 中频 loser-basket reversal 母策略 + 明确 cost cliff + 明确 fast-lane transfer 边界”；不要直接把它升成 `15m/1h` perp ready alpha。**
