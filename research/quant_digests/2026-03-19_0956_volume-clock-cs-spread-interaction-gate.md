# 别把 first-30m 冲击固定在 funding 时钟：`volume-spike market clock + CS spread×impulse` 更像 15m continuation shared gate
- 时间：2026-03-19 09:56 UTC
- 类型：论文 + 本地快检
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/intraday/volume-clock/liquidity/corwin-schultz/spread/continuation/filter/paper/crypto/5m/15m
- 证据类型：论文证据（可读全文）+ 工程快检（公开 OHLCV）

## 1. 这次看了什么
这次继续深读 **Shen, Urquhart, Wang (2022)**，但不复述 headline（“首段预测尾段”），而是抓它更贴 desk 的旁支：**crypto 不该先固定钟表开盘，而应先找“成交量时钟”；且可预测性和流动性状态（CS spread）有交互**。

## 2. 核心结论
- **一句话核心结论：** 对 5m/15m 来说，`固定时钟 first-30m` 更像粗糙近似；更值得先测的是 `volume-spike 定义开段 + spread×impulse` 的 shared gate。
- **一句话证明方式：** 论文用 BTC 分钟级数据做 IS/OOS 预测与机制检验，发现 intraday 关系在高成交/高波动更强，且 `spread×首段收益` 交互显著（支持 liquidity provision 解释）。
- 文中最值钱的数字（原文口径）：
  1. pooled 回归：首段→尾段斜率约 **0.968**（t≈**4.38**，R²≈**1.44%**）。
  2. 分组后：高成交日 R²≈**3.86%**；高波动日 R²≈**2.83%**（明显强于低组）。
  3. 机制检验：`spread×首段收益` 在 Panel D 的 t-stat 约 **8.85 / 8.18**，说明“流动性状态会放大或削弱延续性”。
- 本地快检（BTC/ETH/SOL，1826 天，5m perp -> 30m 聚合）显示：
  - 每日最大 30m 成交窗口**恰好落在 00/08/16 UTC** 的比例仅 **7.72% / 8.32% / 9.86%**；
  - 即使放宽到距锚点 ±60m，也仅 **33.02% / 35.05% / 34.99%**。
  - 这说明“把开段写死在 funding 锚点”会错过大量真实交易活跃窗口。

## 3. 为什么和当前项目有关
- **breakout-short follow-up**：可把“破位后是否追单”改成 `impulse 同向 + liquidity state 支持` 才放行，减少假延续。
- **Fib retest_hold**：当 `spread×impulse` 弱时，优先等回踩确认；强时可减少过度等待。
- **EMA/PSAR raw alpha**：把它们从“裸触发器”降级为“候选触发”，先过 shared gate 再决定 full-size / half-size / veto。

## 4. 可复刻的最小实验（下一步怎么测）
### 研究假设
`volume-clock + CS spread interaction gate` 相比 `fixed-clock gate`，能在 6~15 bps 成本下更好压缩 continuation failure，且不过度砍交易。

### 数据源（公开可得）
- 交易所 5m OHLCV（Binance/Bybit perpetual，CCXT 可拉）
- 公开性：公开市场数据；更新频率：5m

### 一个可计算定义（首版冻结）
1. 以天为单位，30m 聚合后取 `t* = argmax(volume_30m)` 作为 `volume-clock open`。
2. `impulse_vc = r(t*-30m, t*)`。
3. 用 Corwin-Schultz 估算 `CS_spread`（由相邻区间高低价构造），取 rolling z-score。
4. shared gate：
   - long only if `impulse_vc>0` 且 `CS_spread_z>q60`；
   - short 镜像；
   - 不满足则 `half-size` 或 `veto`（两臂都测）。

### 最小回测切口
- 标的：BTC/ETH/SOL
- 执行：15m `next-bar-open + no-overlap`
- 对照：`baseline` vs `fixed-clock gate` vs `volume-clock + spread×impulse gate`
- 成本：6/10/15 bps per side
- 先看：`post-cost expectancy`、`continuation failure rate(4~8 bars)`、`trade_count_retention`

## 5. 风险与保留意见
- 本地快检目前是**时钟分布证据**，不是收益因果；收益提升必须靠 A/B 回测确认。
- 论文样本主要到 2020，且核心是 BTC；迁移到现今 perp 与多币，需要重新做 OOS。
- `CS_spread` 是低频流动性代理，不等于真实盘口冲击成本；要避免过度解读。

## 6. 来源
1. **Shen, D., Urquhart, A., & Wang, P. (2022). _Bitcoin intraday time-series momentum_. Financial Review, 57(2), 319–344.**
   - DOI: `10.1111/fire.12290`
   - Readable URL: `https://doi.org/10.1111/fire.12290`
   - Fulltext PDF: `https://centaur.reading.ac.uk/100181/3/21Sep2021Bitcoin%20Intraday%20Time-Series%20Momentum.R2.pdf`
   - Repo URL: `N/A`
2. **Corwin, S. A., & Schultz, P. (2012). _A Simple Way to Estimate Bid-Ask Spreads from Daily High and Low Prices_. Journal of Finance, 67(2), 719–760.**
   - DOI: `10.1111/j.1540-6261.2012.01729.x`
   - Readable URL: `https://doi.org/10.1111/j.1540-6261.2012.01729.x`
   - Repo URL: `N/A`
3. **Gao, L., Han, Y., Li, S. Z., & Zhou, G. (2018). _Market intraday momentum_. Journal of Financial Economics, 129(2), 394–414.**
   - DOI: `10.1016/j.jfineco.2018.05.009`
   - Readable URL: `https://doi.org/10.1016/j.jfineco.2018.05.009`
   - Repo URL: `N/A`

---
快检数据文件：`reports/artifacts/literature/volume_clock_anchor_quickcheck_2026-03-19.csv`
