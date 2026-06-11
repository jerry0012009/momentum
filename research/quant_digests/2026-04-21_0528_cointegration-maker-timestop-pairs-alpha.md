# 别把这个“10 天都没平掉一笔”的新 repo 只读成失败案例：对 short-cycle crypto desk，更该先拆的是「cointegration spread fade × maker-first × half-life time-stop」这条完整 raw alpha 壳
- 时间：2026-04-21 05:28 UTC
- 类型：GitHub / repo source audit + Binance USDⓈ-M public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：同一组液态 alt perp 里，先找 **cointegration 通过** 的配对；当残差 spread 的平滑 z-score 偏离过大时，做 spread 回归（`z>=+2` 做空 spread，`z<=-2` 做多 spread）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：pairs / stat-arb / relative-value / cointegration / mean-reversion / maker-first / time-stop / Binance USDⓈ-M / 15m / 1h
- 证据类型：工程经验 + repo live artifact + public-data first probe

## 1. 这次看了什么
这次看的是 2026 GitHub repo **Passive-Income-Engineering / pairs-bot**。它不是泛泛讲 pairs，而是把 Binance USDⓈ-M 的一版完整实盘壳直接摊开：`1h` 扫描固定 10 币 universe，Engle-Granger `p<=0.01`，OU half-life `<=168h`，`|z|>=2` 入场，默认 `z` 过零止盈，`|z|>=3.5` 结构破坏止损，`3×half-life` time-stop，双腿都走 maker limit + 30 秒超时处理。最有价值的是：repo 公开承认它 **live 跑了 10 天、零个完整 round-trip**，这反而比“只晒漂亮回测”更适合拿来做 desk 化拆解。

## 2. 核心结论
- 这条东西的 **base alpha 很清楚**：不是“pair trading 概念”，而是 **cointegrated perp spread 的 z-score mean reversion**。
- repo 已经给出一版可直接落地的完整壳：entry / exit / sizing / maker execution / structural-break stop / funding-drag veto 都写清了，所以它不只是 filter，而是完整 raw alpha 候选。
- 我用 repo 同一 10 币 universe（`ETH/SOL/ADA/AVAX/NEAR/DOT/LINK/POL/ATOM/SUI`）做 Binance public quick probe，最近 `1000` 根 `1h` 里能稳定过筛的主要是 3 对：`AVAX-ATOM (p≈0.0002, half-life≈15.7h)`、`AVAX-SUI (p≈0.0016, half-life≈17.7h)`、`ADA-DOT (p≈0.0044, half-life≈28.2h)`。
- 对这 3 对按 repo 口径做 `1h` synthetic spread 回测，`zero-cross` exit 并不天然不可达：`AVAX-ATOM` 约 `20` 笔、均值 `+117.4 bps/spread-trade`、胜率 `85%`；`AVAX-SUI` 约 `19` 笔、均值 `+80.8 bps`；`ADA-DOT` 约 `8` 笔、均值 `+73.6 bps`。
- 把同一思路压到 `15m` child monitoring 仍有 pocket：`AVAX-ATOM` `13` 笔、均值 `+38.0 bps`；`AVAX-SUI` `17` 笔、均值 `+45.6 bps`；`ADA-DOT` `11` 笔、均值 `+16.7 bps`。若按四腿 maker-ish 粗扣 `8~16 bps`，前两对仍明显为正，第三对只剩薄边。
- 反而是更“温柔”的 `|z|<=0.5` 提前止盈，在这组样本里大多 **缩短持有但也明显砍掉利润**；所以这轮更像是：**先别急着把 zero-cross 一刀砍掉，真正该优先补的是 rolling pair admission + fill realism + live timeout discipline。**

## 3. 为什么和当前项目有关
这条线直接扩充的是 **pairs / stat-arb raw alpha 素材池**，而且比“又一个 cointegration 教科书”更有 desk 价值：
- 标的就是公开可拿的 Binance USDⓈ-M perp；
- 可以天然映射到我们常用的 `15m / 1h` 研究节奏；
- repo 已把最麻烦的实盘坑暴露出来：maker 挂单、腿风险、time-stop、funding drag、state reconciliation；
- 因此它适合进入后续 **复现 / paper / live shell** 候选池，而不是只停在文献层。

## 3.5 策略拆解
- 方向属性：相对价值 / pairs / stat-arb / 均值回复
- 基础 alpha：cointegrated spread 偏离过大后向均值回归
- regime：仅在 `p<=0.01` 且 `half-life<=168h` 的 pair admission 下启用
- filter / veto：funding drag 不得吞掉预期 gross 的过半；非通过配对不交易
- risk / sizing / execution overlay：`BASE_NOTIONAL` 对 A 腿定仓、B 腿按 log-beta 对冲；`|z|>=3.5` 结构止损；`3×half-life` time-stop；双腿 maker-first + fill-timeout + reduce-only close

## 4. 可复刻的最小实验
**研究假设**：真正可迁移的不是“任意配对都能回归”，而是 **少数当前仍 cointegrated 的 alt-perp pair** 在 `1h` 发现、`15m` 监控下还能给出可交易的 spread 回归。

**最小实验**：
1. 固定 repo universe 10 币；
2. 每日或每 `3d` 只重估一次 cointegration / beta / half-life，避免每根 bar 过拟合重刷 pair；
3. 入场：`|z_smooth|>=2`；
4. 出场对照：`zero-cross` vs `|z|<=0.5` vs `time-stop only`；
5. 成本：先做 `8 / 12 / 16 bps` 四腿 maker-ish friction ladder；
6. 统计 pair 级别的 `trade_count / win_rate / timeout_rate / stop_rate / net bps`。

## 5. 这轮我保留的判断
这篇东西值得进研究池，不是因为它“已经实盘成功”，而是因为它把一条 **可独立复现、可直接落地完整策略** 的 pairs alpha 壳写得很诚实。当前 public probe 的读法不是“repo live 失败所以 raw alpha 不存在”，而是：**alpha 只存在于很窄的当前 pair pocket，真正的生死线在 admission 稳定性与 maker 执行，而不只是 z-score 入场公式。**

## 6. 下一步怎么测
- 先做 **rolling pair admission backtest**：每日重估 top pairs，避免用整段 hindsight 固定 `AVAX-ATOM / AVAX-SUI`。
- 补 **fill realism**：把 GTX 未成交、单腿成交、30s timeout、re-post 次数写进回测，不要只看 spread 理论回归。
- 做一版 **15m monitor / 1h discovery** baseline：`1h` 决定 pair 与 beta，`15m` 只负责监控 exit / veto / re-entry。
- 若这版过线，再考虑把 `funding drag threshold` 从 veto 升级成 pair ranking 特征，而不是先上更复杂 ML。

## 7. 来源
- Passive-Income-Engineering (2026), **pairs-bot**. GitHub repo. Repo URL: <https://github.com/Passive-Income-Engineering/pairs-bot>
- Source audit files: `README.md`, `pairs_scanner.py`, `pairs_bot.py`
- GitHub metadata URL: <https://api.github.com/repos/Passive-Income-Engineering/pairs-bot>
- 本地 artifacts:
  - `reports/artifacts/quant_digests/2026-04-21_pairsbot_probe.py`
  - `reports/artifacts/quant_digests/pairsbot_scan_1h_2026-04-21.csv`
  - `reports/artifacts/quant_digests/pairsbot_trade_summary_1h_2026-04-21_costladder.csv`
  - `reports/artifacts/quant_digests/pairsbot_transfer_summary_15m_2026-04-21_costladder.csv`
