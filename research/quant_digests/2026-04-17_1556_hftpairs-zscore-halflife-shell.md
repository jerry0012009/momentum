# 别把这份 2026 HFT 仓只读成“低延迟工程”：对 short-cycle desk，更该先拆的是「半衰期约束配对价差 z-score 回归」这条 raw alpha
- 时间：2026-04-17 15:56 UTC
- 类型：GitHub
- 主题类型：raw alpha
- 基础 alpha：**cointegration/pairs spread 在短窗 z-score 极值后向均值回归**（`z>|entry|` 入场，`z→0` 离场）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / pairs / stat-arb / mean-reversion / zscore / half-life / execution / cost / 1m / 5m / 15m
- 证据类型：工程实现 + public-data portability probe

## 1) 这次看了什么
先答一句 **base alpha 是什么**：这份仓的 alpha 本体不是“C++ 低延迟”，而是 **配对价差偏离后回归**。

本轮主看 2026 新仓 `SamarthChaudhary-22/Crypto_Stat-Arb_HFT_Model`（Python 研究层 + C++ 执行层），重点读了：
- `README.md`
- `analyzer.py`（相关性/协整/半衰期筛选）
- `optimizer.py`（`window / entry_z / exit_z / stop_z` 网格）
- `fix_strategies.py`
- `strategies.json`

## 2) 核心结论
- **一句话核心结论：** 这仓里最该保留的是「`half-life bounded pairs` + `z-score spread fade`」这条 raw alpha；低延迟执行是放大器，不是 alpha 本体。
- **一句话证明方式：** 仓内用协整+半衰期做候选筛选、再用参数网格做 spread 回归回测；我又用 Binance USDⓈ-M 公共 `5m` 数据做了可迁移快检。
- 仓内信号壳很清楚：
  - 入场：`z > entry_z` 做空 spread；`z < -entry_z` 做多 spread；
  - 离场：`z` 回到 `exit_z` 附近；
  - 风控：`stop_z`；
  - 参数：`window/entry/exit/stop` 可网格化。
- 但仓里也有一个实盘风险点：`optimizer.py` 在“找不到正收益参数”时仍会写默认参数进 `strategies.json`，所以 **必须额外加 admission gate**（否则容易把“可运行”误当“可交易”）。
- 我补的 portability probe（120 天，3 组配对）显示：
  - 总计 `4,646` 笔，**单笔 gross 平均约 `+4.24 bps`**；
  - 扣 pair roundtrip `8/12/20 bps` 后，aggregate net 分别约 `-1.74 / -3.60 / -7.32`（spread-return 口径）；
  - 说明这条边当前更像 **需要更强执行/过滤的 raw alpha 壳**，不能直接当纯 taker baseline 上线。

## 3) 为什么和当前项目有关
这题和当前 desk 的短周期主线直接相关：
- 属于 `raw alpha`（pairs/stat-arb/relative value），不是纯解释型材料；
- 能直接落到完整策略组件：entry/exit/sizing/risk/cost；
- 与现有 1m/3m/5m 研发节奏兼容：先在 `5m` 验证可迁移，再压到 `1m/3m` 做执行生存测试。

## 3.5) 策略拆解（必填）
- 方向属性：相对价值 / 统计套利（market-neutral）
- 基础 alpha：`spread z-score extreme -> mean reversion`
- regime：仅保留“协整稳定 + 半衰期不过长”的 pair（`half_life <= threshold`）
- filter / veto：
  - `std_spread` 过低不做；
  - `entry_z` 分层（只做更极端尾部）；
  - `no profitable params -> reject`（不接受默认兜底参数直接上线）
- risk / sizing / execution overlay：
  - 波动归一（`size ~ target_risk / spread_vol`）
  - `stop_z` + `max_hold`
  - 成本阶梯（`8/12/20 bps`）
  - 先做 maker-first / passive leg，避免纯 taker 把 edge 吃光

## 4) 可复刻的最小实验
**研究假设：** repo 的 z-score spread MR 在 Binance perp 的 `5m` 仍有 gross edge，但成本后需要更强 admission/execution 才能存活。

**可计算定义（本轮已跑）：**
- spread：`log(P1) - hedge_ratio * log(P2)`
- `window=12`（对应 60 分钟）
- `entry_z=2.0, exit_z=0.0, stop_z=4.0, max_hold=24 bars`

**最小回测切口（public data）：**
- 市场：Binance USDⓈ-M perpetual
- 周期：`5m`
- 样本：最近 `120d`
- 配对：`LINK/SOL`, `ENA/XRP`, `AXS/FIL`（采用 repo `strategies.json` 的 hedge ratio）

**先看 2 个指标：**
1. `gross_avg_per_trade` 是否显著高于费用门槛；
2. `net_after_cost` 在 `8/12/20 bps` 阶梯下是否仍为正。

**本轮结果（关键数据点）：**
- Aggregate：`4,646` 笔，`gross_avg_per_trade ≈ +4.24 bps`
- Cost ladder：`8bps -> -3.76bps/trade`，`12bps -> -7.76bps/trade`，`20bps -> -15.76bps/trade`
- Pair gross 单笔：`LINK/SOL +2.98bps`，`ENA/XRP +3.72bps`，`AXS/FIL +6.04bps`

## 5) 风险与保留意见
- 这轮是 transfer check，不是 walk-forward 生产级结论。
- repo 的 pair 发现与实盘执行存在“研究-生产”断层：如果 admission gate 不硬化，默认参数会引入伪可行 pair。
- 对短周期而言，交易成本与成交路径决定生死：同样信号，taker-only 常常负；maker 优先和流动性窗口过滤很关键。

## 6) 来源
1. **Samarth Chaudhary（GitHub, 2026）. _Crypto_Stat-Arb_HFT_Model_.**
   - Repo URL: `https://github.com/SamarthChaudhary-22/Crypto_Stat-Arb_HFT_Model`
   - Readable URL: `https://github.com/SamarthChaudhary-22/Crypto_Stat-Arb_HFT_Model/blob/main/README.md`
   - 关键代码：
     - `analyzer.py`（协整 + 半衰期筛选）
     - `optimizer.py`（z-score 参数网格 + 默认兜底逻辑）
     - `strategies.json`（候选 pair 与 hedge ratio）

2. **Engle, R. F., & Granger, C. W. J. (1987). _Co-integration and Error Correction: Representation, Estimation, and Testing_. Econometrica.**
   - DOI: `10.2307/1913236`
   - Readable URL: `https://www.jstor.org/stable/1913236`

---
### 本轮产物
- Probe 脚本：`/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-17_hft_pairs_zscore_probe.py`
- Summary JSON：`/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-17_hft_pairs_zscore_probe.json`
- Pair 统计：`/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-17_hft_pairs_zscore_probe_pair_stats.csv`
- 逐笔明细：`/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-17_hft_pairs_zscore_probe_trades.csv`
- 抓取状态：`/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-17_hft_pairs_zscore_probe_fetch_status.csv`
