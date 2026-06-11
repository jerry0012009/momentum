# 别把流动性扫单当“突破前固定流程”：在 15m 里，`sweep→breakout→retest` 更像超稀疏高门槛，不是三条收口线的默认共享入场键
- 时间：2026-03-19 19:45 UTC
- 类型：GitHub 仓库 + 本地代理快检
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/liquidity-sweep/retest/confirmation/scarcity-gate/repo/crypto/15m
- 证据类型：工程经验 + 本地最小复现实验

## 1. 这次看了什么
这次看的是 GitHub 仓库 **TheVision333/trading-bot**（2026，`wlb_signals.py`），核心是 `WLB-v2`：先要求区间内出现 wick sweep（但收盘没真正越界），再等放量突破，最后等回踩确认后入场。它不是“再加一个指标”，而是把 breakout path 写成了一个状态机：`pre-break liquidity sweep -> breakout confirm -> retest hold`。

## 2. 核心结论
- **这条链条在 15m 上最先暴露的是“极端稀疏性”。** 我用 `BTC/ETH/SOL, Binance 120d, 15m` 做最小代理快检：
  - baseline（`breakout_retest`）跨资产 `mean_trades=853.7`，`mean_total_return=-45.02%`，`mean_win_rate=39.14%`；
  - 加硬门槛（`sweep_breakout_retest`）后变成 `mean_trades=6.3`，`mean_total_return=-2.23%`，`mean_win_rate=34.44%`。
- **它确实大幅压住了“总亏损暴露”，但主要靠“几乎不交易”。** 交易保留率只有约 `0.74%`（`6.3 / 853.7`），属于典型的 scarcity gate：不是把坏单筛成好单，而是把绝大多数机会都砍掉。
- **两种口径都没把资产层面翻正（`positive_asset_ratio=0/3`）。** 所以当前不能写成“sweep 条件已证明有效 alpha”，更诚实的读法是：它可作为高置信度极窄模式的候选 veto / size-down 触发，但不该直接升级为三条线共享默认 gate。

## 3. 为什么和当前项目有关
一句话核心结论：**`sweep→breakout→retest` 对 `V3 breakout-short follow-up` 的价值更像“少做错”，不是“多赚到”。**

一句话证明方式：**同一份 15m 三资产样本里，硬性 sweep 先验把总亏损从 `-45.02%` 压到 `-2.23%`，但同时把交易机会压到只剩约 `0.74%`，且资产仍是 `0/3` 正收益。**

对三条收口线的对应关系：
1. `breakout-short follow-up`：可当“超高门槛 continuation 模式”的入场白名单；
2. `Fibonacci confirmation / retest_hold`：可作为 retest 前的可选先验（有 sweep 才允许 size-up）；
3. `EMA / PSAR raw alpha`：更像 session 级别的风险覆盖层，而不是逐笔默认触发条件。

## 4. 可复刻的最小实验
下一步不要直接把 sweep 写成 hard-required；先测三臂：
1. `breakout_retest_base`
2. `sweep_required_hard`
3. `sweep_soft_size_overlay`（无 sweep 也可做，但仓位减半；有 sweep 才满仓）

统一口径：`next-bar open | no-overlap | hold=8 bars | 6/10/15 bps`，先看：
- `mean_total_return`
- `trade_retention`
- `positive_asset_ratio`
- `time-bucket stability`

淘汰标准建议：若 `trade_retention < 20%` 且 `positive_asset_ratio` 仍 `< 2/3`，则不作为 shared gate，只保留在 evidence pool。

## 5. 风险与保留意见
- 本轮是代理快检，不是完整 clean replication；主要回答“这个想法在 15m 上会不会过稀疏”。
- 规则实现里仍有区间定义、volume 门槛、retest 容差等参数耦合，后续必须做邻域稳定性。
- 稀疏门槛策略容易出现样本外漂移；必须补 `rolling window` 与跨时段稳定性检查。

## 6. 来源
1. GitHub Repo
   - Author: TheVision333
   - Year: 2026（最近提交：2026-02-23）
   - Title: *trading-bot*（含 `WLB-v2 Elite — Wyckoff Liquidity Breakout + Retest`）
   - Venue: GitHub
   - DOI: N/A
   - Readable URL: https://github.com/TheVision333/trading-bot
   - Repo URL: https://github.com/TheVision333/trading-bot
2. 代码入口（仓库内）
   - `strategy/wlb_signals.py`
   - `strategy/retest_signals.py`
3. 本地快检 artifact
   - `reports/artifacts/quant_digests/wlb_sweep_retest_proxy_20260319/overall_summary.csv`
   - `reports/artifacts/quant_digests/wlb_sweep_retest_proxy_20260319/asset_summary.csv`
