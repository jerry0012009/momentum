# 别把这份 intraday crypto reversal notebook 只读成“spot 篮子 gross anomaly”：对 short-cycle desk，更该先测的是「US close pocket alt-loser bounce」这条 raw alpha
- 时间：2026-04-12 05:46 UTC
- 类型：GitHub / notebook source audit + public futures portability probe
- 主题类型：raw alpha
- 基础 alpha：在 `15:30–16:00 ET` 的 US close pocket 内，若液体 perp 篮子里出现明显相对落后者，下一段更像 **loser bounce** 而不是继续扩散；对当前 desk，最像可交易版本的不是 repo 原始“全篮子多空对冲”，而是 **只做 close-window 最弱一腿的单腿回补**。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：cross-sectional / mean-reversion / session-pocket / US-close / loser-bounce / ETH / SOL / BNB / XRP / Binance-perpetual / 15m / 60m / 90m
- 证据类型：工程证据（GitHub notebook）+ Binance USDⓈ-M public-data probe

## 1. 这次看了什么
这轮主看的是 GitHub notebook 项目 **BNeillDickey (2026), _intraday-crypto-reversal-project_**。它的 headline 是：把美股 intraday seasonality / institutional flow 文献那套框架，搬到 `24/7` crypto 上，专门测 `09:30 ET` 开盘窗与 `16:00 ET` 收盘窗附近的跨币种 intraday reversal / momentum。

先把 **base alpha** 说清楚：
> **不是“US session 很重要”这种泛叙事，而是：某个固定 session pocket 里的相对 loser / winner，后续 30~120 分钟会不会系统性反打或续行。**

repo 原始 notebook 用的是 `25` 个 Binance spot 币种、`15m` bar、按 `15:30–16:00 ET` 或 `09:30–10:00 ET` 做横截面 rank，再去测之后的持有窗。它最重要的价值，不是 headline 的高 gross Sharpe，而是它把 **session window → rank signal → hold window → 成本分解** 这条链路写完整了。

## 2. 核心结论
- **一句话核心结论：** repo 里真正值得 desk intake 的，不是“25 币 spot 篮子整本照抄”，而是从里面拆出的 **US close pocket loser-bounce**；而且在当前 perp portability 里，最干净的是 **long loser 单腿**，不是 `long loser + short winner` 的完整对冲书。
- **一句话证明方式：** 先看 notebook 自带的 `15m` rank-window backtest，再用 Binance USDⓈ-M 公共 `15m` kline 对 `BTC/ETH/SOL/BNB/XRP/DOGE` 做最小 public-only portability probe，比较 full basket、单腿、asset-side veto 与 cost ladder。
- notebook 原始结果里，`25` 币 spot close-window reversal 的 **gross test Sharpe ≈ 5.85**、gross alpha 约 **24.0 bps/day**，但 full TC model 会把它打穿，所以 repo headline 本身并不是当前最适合 desk 直接照搬的版本。
- 我这次在 `6` 个 liquid Binance perps 上重做最小 probe 后发现：**full basket 双腿 close-window reversal** 只剩 **`+4.03 bps/次` gross（16:15–17:15 ET）**，按 `8 bps` round-trip 已接近打平；但 **只做 loser-long 单腿** 则有 **`+8.11 bps/次` gross**。
- 再进一步做 asset-side veto：只在 close-window 最弱币属于 `ETH / SOL / BNB / XRP` 时进场，`2025-10-01 ~ 2026-04-12` 共 **`139` 次**事件里，
  - `16:15–17:15 ET`：**`+14.04 bps/次` gross**，胜率 **`63.3%`**；
  - 扣 `4 / 8 bps` round-trip 后仍约 **`+10.04 / +6.04 bps/次`**；
  - `16:15–17:45 ET` 更强，约 **`+19.39 bps/次` gross**，扣 `8 bps` 仍约 **`+11.39 bps/次`**。
- 反过来，**short winner 这条腿几乎没贡献**：在 `6` 币 full basket 上，`16:15–17:15 ET` 的 short-winner 基本约等于 **`0 bps`**。这说明对当前 desk，正确读法不是“做标准 market-neutral 双腿”，而是 **保留 raw alpha 的 loser-bounce 本体，把 short side 当成默认不启用的旁支。**

## 3. 为什么和当前项目有关
这条线值得进池，因为它同时满足当前优先级里最关键的几点：
1. **它是 raw alpha，不是 filter。** 进场、方向、持有窗都能单独定义；
2. **它直接映射到 `15m / 60m / 90m`。** 信号就在 `15m` bar 上，不需要低频外部数据硬装逐根 alpha；
3. **它补的是当前素材池里更少见的一类：session-pocket × cross-sectional loser-bounce。** 不是再讲 breakout / retest / funding 温度计；
4. **它允许很自然地拆成完整策略。** `entry / exit / sizing / cost / veto` 都很清楚；
5. **它和 notebook headline 有区别，但不是跑题。** 用户明确允许从论文 / repo 里抽一个更适合 desk 的旁支；这次最适合的旁支，就是把“full basket gross anomaly”拆成“single-leg alt loser bounce”。

## 3.5 策略拆解（必填）
- 方向属性：cross-sectional / mean-reversion / session-pocket / single-leg
- 基础 alpha：`15:30–16:00 ET` 篮子最弱币在下一段出现 loser bounce
- regime：US close pocket；更像美股收盘相关的资金流/风险再平衡时段
- filter / veto：若最弱币是 `BTC` 或 `DOGE`，先 veto；第一版只做 `ETH / SOL / BNB / XRP`
- risk / sizing / execution overlay：固定 notional、单次只持 1 条腿、`60m/90m` 时间退出、成本梯度先测 `4 / 8 bps` round-trip

## 4. 可复刻的最小实验
### 研究假设
US close pocket 里的 **alt/ETH 相对 loser** 更容易在接下来 `60~90m` 回补，而 BTC / DOGE 这种“最弱者”更像噪声或不同状态，不该混做。

### 一个可计算定义
在 `BTC/ETH/SOL/BNB/XRP/DOGE` 六币篮子上：
1. 用 `15:30–16:00 ET` 的累计 `15m` log-return 做横截面排名；
2. 找当日 **最弱** 的一币；
3. 若该币属于 `{ETH,SOL,BNB,XRP}`，则在 `16:15 ET` 做多；
4. 分别在 `17:15 ET` 与 `17:45 ET` 时间退出；
5. 成本先测 `4 / 8 bps` round-trip。

### 最小回测切口
- 资产：`BTCUSDT / ETHUSDT / SOLUSDT / BNBUSDT / XRPUSDT / DOGEUSDT`
- 周期：`15m`
- 样本：本轮 public probe 先用 `2025-10-01 ~ 2026-04-12`
- 最该先看：
  1. `mean bps / trade`
  2. `cost ladder after 4/8 bps`

### 本轮建议先测哪版
先别扩 universe，也别急着双腿化。第一版就测：
- `signal`: close-window bottom-1 loser
- `asset veto`: 只允许 `ETH/SOL/BNB/XRP`
- `entry`: `16:15 ET`
- `exit A`: `17:15 ET`
- `exit B`: `17:45 ET`
- `sizing`: 单笔固定 notional，单日最多一笔

## 5. 风险与保留意见
- 这轮 portability probe 只有约 `6.5` 个月，不是长样本定论；
- 当前结果明显依赖 **asset-side admission**，说明它不是“任何 loser 都会 bounce”的粗糙规则；
- 该 pocket 可能受 ETF / 美股收盘 / 风险再平衡时段影响，后续如果 session microstructure 改变，edge 可能衰减；
- 现在只用 public `15m` kline，还没把真正的 book / taker flow / funding boundary / macro event veto 加进去；
- `17:45 ET` 看起来更强，但也要防只是把一部分隔夜/美股 after-hours 风险混进来，所以 `60m` 与 `90m` 要并行保留。

## 6. 最值得复用的点
最值得复用的不是 repo 里的 full basket gross SR，而是它的方法骨架：
**固定 session pocket → 横截面 rank → 明确分离 single-leg / double-leg / asset veto / 成本梯度。**
这套骨架后面也能拿去测别的 raw alpha：US open、ETF close、proxy 盘前后 handoff，都能用同样模板跑 first verdict。

## 7. 一句话结论
> 这份 notebook 真正适合当前 short-cycle desk intake 的，不是“25 币 spot close-window reversal”整本照抄，而是它里面更可交易的旁支：**US close pocket 的 alt-loser bounce。** 在 `6` 个 liquid Binance perps 的 public probe 里，只要把最弱币限制在 `ETH / SOL / BNB / XRP`，`16:15–17:15 ET` 已有约 `+14.04 bps/次` gross、`+6.04 bps/次`（按 `8 bps` round-trip）这一级别的最小可交易雏形。

## 8. 本轮产物
- 研究笔记：`research/quant_digests/2026-04-12_0546_us-close-altloser-bounce-alpha.md`
- Probe summary：`reports/artifacts/literature/us_session_xs_reversal_perp_probe_2026-04-12.csv`
- Asset/leg breakdown：`reports/artifacts/literature/us_session_xs_reversal_perp_asset_probe_2026-04-12.csv`
- Cost ladder：`reports/artifacts/literature/us_close_long_loser_costladder_2026-04-12.csv`
- Hold sweep：`reports/artifacts/literature/us_close_altloser_hold_sweep_2026-04-12.csv`

## 9. 来源
1. **BNeillDickey. (2026). _Intraday Crypto Reversal Project_. GitHub Notebook Project.**
   - Repo URL: `https://github.com/BNeillDickey/intraday-crypto-reversal-project`
   - Readable URL: `https://github.com/BNeillDickey/intraday-crypto-reversal-project`
   - 关键文件：`Intraday_Crypto_Reversal_Project.ipynb`
   - GitHub metadata：created `2026-03-09`, updated `2026-03-09`

2. **Binance USDⓈ-M Futures Public API**（本轮 portability probe 实际使用）
   - Kline / Candlestick Data: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`

3. **repo 内引用并作为机制地基的 intraday 文献线索**
   - Heston, Korajczyk, & Sadka (2010). *Intraday Patterns in the Cross-Section of Stock Returns*.
   - Bogousslavsky (2016). *Infrequent Rebalancing, Return Autocorrelation, and Seasonality*.
   - Gao, Han, Li, & Zhou (2018). *Market Intraday Momentum*.
