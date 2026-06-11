# 别把 cross-market intraday 动量当成单向放行：`leader impulse` 需要分层（low-z 跟随 / high-z 反转）
- 时间：2026-03-19 05:58 UTC
- 类型：论文 + 快速工程复核
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/cross-market/intraday/leader-laggard/continuation/failure/regime/filter/paper/crypto/15m
- 证据类型：论文证据 + 本地最小复核

## 1. 这次看了什么
这次主看 **Xu, Li, Singh, Li (2024)** 的 *Cross-Market Intraday Time-Series Momentum*（working paper），并用 **Li, Sakkas, Urquhart (2022)** 的 intraday TSMOM 证据做地基；同时在本地 `BTC/ETH/SOL` 15m perp 历史上做了一个 180d 快检，专门看“leader impulse 强度分层”对下一根跟随的影响。

## 2. 核心结论
- **一句话核心结论：** 对 15m 来说，cross-market leader 不是“越强越该追”——更像要做成一个**非线性 follow-up gate**：`low-z` 允许 continuation，`high-z` 倾向 veto/降权。
- **一句话说明它怎么证明：** 论文给出“跨市场日内 lead-lag”框架，本地快检进一步显示同一方向里存在强度分层：弱到中等冲击有延续，极端冲击更容易失效。
- 本地 180d 快检（ETH/SOL 作为 leader basket）里：
  - `low_z (<0.5)` 事件 `n=6557`，BTC 下一根同向率 **49.55%**（基线 **47.44%**，+2.11pct）
  - `high_z (>1.0)` 事件 `n=1787`，BTC 下一根同向率 **44.77%**（较基线 -2.67pct）
  - `high_z` 下行事件（更贴近 breakout-short）`n=925`，下一根同向率 **45.51%**（低于下行基线 **47.29%**）
- 同期 pairwise lead-lag 仍有正边：
  - `SOL→BTC` lead-edge ≈ **+0.0204**
  - `ETH→BTC` lead-edge ≈ **+0.0095**
  说明“有 lead-lag”，但不能忽略强冲击下的失败段。

## 3. 为什么和当前项目有关
- 对 `V3 final-verdict / breakout-short follow-up`：可直接把 `high_z leader impulse` 作为 continuation veto，减少“末端追击”。
- 对 `Fibonacci confirmation / retest_hold`：在 retest_hold 成立后，只在 `low_z` 或中性区放行加仓，`high_z` 只保留轻仓确认，避免“过冲后回吐”。
- 对 `EMA / PSAR raw alpha focus`：不改主触发，只加一层成本友好的 `size_mult`（例如 `1.0 / 0.6 / 0.2`），更符合“主信号 vs 风险覆盖层”分工。
- 这比继续微调单一参数更值钱：它是三条收口线都能共用的 follow-up/failure 过滤层。

## 4. 可复刻的最小实验
- 研究假设：`leader impulse` 分层后，三条线的 post-cost 指标会改善；尤其 `high_z` veto 能降低假延续。
- 一个可计算定义（15m）：
  - `leader_ret = mean(ret_ETH, ret_SOL)`
  - `leader_z = zscore_96(abs(leader_ret))`
  - `leader_valid = sign(ret_ETH)==sign(ret_SOL) & mean(|ret_ETH|,|ret_SOL|) > 1.2*|ret_BTC|`
  - gate：`low_z = leader_z < 0.5`，`high_z = leader_z > 1.0`
- 最小回测切口：BTC/ETH/SOL perp，近 120~180d，15m 产信号（breakout-short / fib retest / ema-psar），含手续费与滑点。
- 先看 3 个指标：`post_cost_return`、`false_follow_ratio`、`MAE<1R 占比`。
- 下一步怎么测（本轮明确动作）：
  1) 对三条线各跑 `baseline vs low_z_only vs high_z_veto` 三组；
  2) 先只动 gate，不动入场和出场；
  3) 若 `high_z_veto` 降低 `false_follow_ratio` 且不显著压缩 trade count，再进入 OOS。

## 5. 风险与保留意见
- Xu et al. 仍是 working paper；在不同市场结构下，lead-lag 强度可能漂移。
- 本地快检是“轻量诊断”，不是正式 replication：未做完整成本敏感性、未做 purged walk-forward。
- `z` 阈值（0.5/1.0）当前只是起步参数，不应直接生产化。
- 若后续 OOS 显示 `high_z` 并非稳定劣化区，这条规则要降级为“候选过滤层”。

## 6. 来源
1) Xu, D., Li, B., Singh, T., & Li, J. (2024). *Cross-Market Intraday Time-Series Momentum*. SSRN Working Paper.
- Venue: SSRN
- DOI: https://doi.org/10.2139/ssrn.4765613  （早期版本：10.2139/ssrn.4651331）
- Readable URL: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4765613
- Repo URL: N/A（论文）

2) Li, Z., Sakkas, A., & Urquhart, A. (2022). *Intraday time series momentum: Global evidence and links to market characteristics*. Journal of Financial Markets, 57, 100619.
- Venue: Journal of Financial Markets
- DOI: https://doi.org/10.1016/j.finmar.2021.100619
- Readable URL: https://www.sciencedirect.com/science/article/pii/S1386418121000064
- Repo URL: N/A（论文）

3) 本地快速复核（公开历史行情）
- 数据：`BTCUSDT/ETHUSDT/SOLUSDT` 15m perp 缓存（公开交易所行情）
- 口径：最近 180d；leader basket=`ETH+SOL`；`zscore_96(abs(leader_ret))`
- 结果文件：`reports/artifacts/literature/tmp_crossmarket_intraday_leadlag_nonlinear_quickcheck_180d.csv`
- Repo URL: N/A（本地复核脚本化统计）
