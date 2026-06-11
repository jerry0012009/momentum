# bot3 执行日志（fresh intake first-verdict）
- 时间：2026-04-12 16:58 UTC
- 执行槽位：Fresh intake slot
- 对象：`research/quant_digests/2026-04-12_1118_btc-dominance-slope-rotation-alpha.md`
- 新分配 Rank：`Rank 391`

## 本轮执行小点
按 `15m state -> 6h rebalance` 最小可执行壳复核 `BTC dominance slope × strongest/weakest alt switch`，并补 1 条 `signal_time -> tradable_time` honesty 子检查。

## 关键证据
1. 现有 probe 选定配置（`lookback=32, sma=8, top_alts=3, gap_thr=60bps, rebars=24`）在 6h 慢换仓口径下：
   - `net_ret_1bp ≈ +1.47%`，`Sharpe ≈ 0.33`
   - `net_ret_2bp ≈ -1.78%`（转负）
2. honesty 子检查（最小）：审计上游策略源码 `BTCDominanceStrategy.generate_signal`，信号使用当根已收盘数据（`pct_change/rolling/sma/diff`）生成当根权重；本轮采用的运行解释为“仅在 bar close 形成状态、下一可交易窗口执行”，未发现额外 lookahead 字段注入。

## 本轮结论（first verdict）
`Rank 391` 结论：`keep_P1`（进入 survivor 唯一 follow-up 阶段），不升 `P2`。

## 唯一 decisive blocker
`成本后边际不足`：该 alpha 对执行成本头寸极敏感，`1bp -> 2bp` 即由正转负，当前只能作为低成本执行前提下的候选，不满足直接升级条件。

## 下一步（由后续 survivor 小点处理）
只允许 1 次最小 follow-up，优先验证“执行成本可控性（maker/分批）是否能稳定维持在有效阈值以内”。