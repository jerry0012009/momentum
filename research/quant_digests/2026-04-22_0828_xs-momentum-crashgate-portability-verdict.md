# 别把“动量+崩盘过滤”当免费午餐：这份 2026 新仓库更该先回答的是「top-N 横截面动量在 5m/15m 先有没有正 edge，再谈 crash gate」

- 主题类型：`raw alpha`（带 `risk/filter` 组件）
- 基础 alpha：`cross-sectional momentum`（每根重排：做多过去 20 bars 动量最强且为正的 top-N 币）
- 是否可独立复现：`是`
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：`是`

## 0) 先说结论（给 desk 的一句话）
**这条线当前不该直接进实盘候选。** 在我们对 Binance 短周期口径的最小可复现迁移里，`top-N 动量` 本体先天偏弱且换手过高，`crash filter` 没有把它救回来；因此下一步要先改 alpha 壳（如中性化/降换手），不是继续在 crash 阈值上拧螺丝。

## 1) 这次为什么值得写（且不重复）
最近 intake 里有不少 `breakout / mean-reversion / stat-arb`，但**“动量本体 + 崩盘冷却”这类完整可执行壳**在近期池子里覆盖较少。这个 2026 新仓库给了一个非常明确的可复现结构：

- raw alpha：`20-bar` 横截面动量选强
- risk/filter：任一币种单根大跌触发全组合冷却若干 bars
- sizing：等权 top-N
- 执行：按 bar 级别重排与调仓

它的价值不在“观点新奇”，而在**结构清楚、可直接下最小实验**。

## 2) 来源与策略拆解（repo source audit）
本轮主来源：
- 仓库：`zwmjj/kuant-strategies`（2026）
- 文件：`strategies/crypto_advanced.py` 中 `CryptoMomentumCrashFilter`

可复现规则（按源码可直接还原）：
1. 计算 `mom = close.pct_change(20)`；
2. 非冷却期内，做多动量 top-N（且仅保留 `mom > 0` 的币）；
3. 若任一币种单根收益低于 `crash_threshold`（源码日频口径默认 `-15%`），触发全组合冷却 `cooldown_days`；
4. 冷却期内全部空仓，结束后恢复动量选强。

> 一句话核心结论：**这不是纯 filter 主题；它本体是 raw alpha（横截面动量），crash gate 只是风控门。**

> 一句话“它怎么证明”：**我们把 repo 规则迁移到 Binance 公共短周期数据，直接做 raw vs raw+crash gate A/B，对比成本后净值、回撤、换手与活跃率。**

## 3) 最小可复现实验（5m/15m portability probe）
### 3.1 数据与口径
- 数据源：Binance USDⓈ-M Futures 公共 klines（公开可得）
- 采样：近 `120d`
- 周期：`5m`、`15m`
- 标的：
  - `5m`：`ADA/AVAX/BNB/BTC/DOGE/ETH/LINK/SOL/XRP`（9 币）
  - `15m`：`BNB/BTC/ETH/SOL`（4 币）
- 执行假设：`t` 生成信号，`t+1` 生效（1-bar lag）
- 成本：round-trip `6 bps`（按换手扣减）

### 3.2 策略变体
- **raw**：`mom_window=20`，`top_n=4(5m)/3(15m)`，无 crash gate
- **raw + crash gate**：
  - `5m`: `crash_threshold=-2%`, `cooldown=5 bars`
  - `15m`: `crash_threshold=-3%`, `cooldown=5 bars`

### 3.3 结果（核心指标）
1) `5m`（9 币）
- raw：`gross -43.27%`，`net(6bps) -99.98%`，`MDD -99.98%`，`avg_turnover 0.375/bar`
- raw+crash：`gross -43.37%`，`net -99.98%`，几乎无改善

2) `15m`（4 币）
- raw：`gross -16.78%`，`net -88.16%`，`MDD -88.51%`
- raw+crash：与 raw 基本重合（本样本 crash 事件少，拦截不足）

### 3.4 desk 解释（人话版）
- 这版壳的问题不是“少一个更聪明 filter”，而是**alpha 本体 + 调仓频率组合太贵**；
- crash gate 只在少数极端时刻触发，**无法修复日常高换手侵蚀**；
- 因此当前最该改的是：
  - alpha 壳（如 long-short/中性化、信号稀疏化）
  - 调仓节奏（降换手）
  - 再谈 crash gate 参数。

## 4) 对当前素材池的意义（取舍）
- 这条线仍可留在研究池，但定位应调整为：
  - **保留 `crash gate` 作为共享风险组件**（可服务 trend / momentum 类书）
  - **暂不把“long-only top-N mom + 高频重排”当可交易主壳**

## 5) 下一步怎么测（直接可执行）
1. **先改本体再改过滤**：做 `long top-N / short bottom-N` 的 dollar-neutral 版本，对比 long-only。
2. **降换手实验**：把重排频率从“每 bar”降到“每 6/12 bars”，看成本后是否回正。
3. **crash gate 升级**：从绝对阈值改为 `vol-scaled`（如 `ret < -k * rolling_sigma`）并加 BTC 主导冲击确认。
4. **成本阶梯**：固定跑 `2/4/6 bps` 三档，先确认是否存在稳定的 post-cost 生存区。

## 6) 关键来源（含 DOI / URL）
1. **zwmjj (2026)**. *kuant-strategies*. GitHub Repository.  
   - Authors: `zwmjj`  
   - Year: `2026`  
   - Title: `kuant-strategies`  
   - Venue: `GitHub`  
   - DOI: `N/A`  
   - Readable URL: `https://github.com/zwmjj/kuant-strategies`  
   - Repo URL: `https://github.com/zwmjj/kuant-strategies`

2. **Moskowitz, T. J., Ooi, Y. H., & Pedersen, L. H. (2012)**. *Time Series Momentum*. *Journal of Financial Economics*.  
   - DOI: `10.1016/j.jfineco.2011.11.003`  
   - Readable URL: `https://www.sciencedirect.com/science/article/pii/S0304405X11002613`

3. **Liu, Y., Lu, X., & Wang, H. (2021)**. *Asymmetry, tail risk and time series momentum*. *International Review of Financial Analysis*.  
   - DOI: `10.1016/j.irfa.2021.101938`  
   - Readable URL: `https://www.sciencedirect.com/science/article/pii/S1057521921002458`

---

## 附：本轮实验文件
- `reports/artifacts/quant_digests/mom_crash_filter_probe_20260422/metrics.csv`
- `reports/artifacts/quant_digests/mom_crash_filter_probe_20260422/summary.json`
- 复用行情缓存：`reports/artifacts/quant_digests/bollinger_rsi_mr_probe_20260422/*.csv`
