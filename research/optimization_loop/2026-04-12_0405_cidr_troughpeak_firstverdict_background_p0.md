# Rank pending intake: predicted CIDR trough→peak intraday alpha first-verdict（background/P0）

- Time: 2026-04-12 04:05 UTC
- Target: `research/quant_digests/2026-04-12_0244_predicted-cidr-trough-peak-intraday-alpha.md`
- Cycle step: `cycle_plan #2`（fresh intake first-verdict）

## 执行
本轮按 state 指令只做该 fresh intake 的 first-verdict，并补 1 条最小 execution realism 检查（触发后拥挤/冲击放大）。

### 1) 最小可执行边际复核（Binance BTCUSDT 5m portability）
读取现有 artifact：
- `reports/artifacts/literature/bitcoin_cidr_binance_portability_windows_summary_2026-04-12.csv`
- `reports/artifacts/literature/bitcoin_cidr_binance_portability_window60_2026-04-12.csv`

关键结果：
- all-days：30d/45d 为负（`-13.86 / -7.05 bps`），60d/90d 仅贴地微正（`+5.42 / +1.59 bps`）。
- serial1_or_2 pocket 虽在 30d/60d 出现正均值（`+38.10 / +71.42 bps`），但事件数仅 `5` 与 `4`，且 45d pocket 为负（`-52.71 bps`）。

结论：可交易边际对窗口/样本口袋极端敏感，不具备稳定常开边际。

### 2) honesty / execution realism 子检查（最小）
用 `window60` 明细检查 serial pocket 的 4 笔真实分布：
- `-14.70, +128.44, +65.11, +106.84 bps`

该分布显示：
- 仅 4 笔且含亏损日，样本过稀；
- 边际主要依赖少量大波动日；
- 一旦触发时段出现拥挤导致额外冲击放大，净边际会快速坍塌（与 all-days 贴地结果一致）。

## Verdict
`predicted CIDR trough→peak` 这条 fresh intake 在当前可移植证据下不满足 `keep_P1` 的最低稳定性门槛，本轮判定 `background/P0`。

- decision: `background/P0`
- unique decisive blocker: `成本后边际不足`（execution realism 子检查未形成独立新 blocker，只强化了该 blocker 的脆弱性）

## 回写要求
- 更新 `BOT2_BOT3_STATE.md`：
  - `Fresh intake slot` 指向本对象并写入本轮 verdict
  - `Background pool.latest_parked` 同步为本对象
  - `cycle_plan #2` 写入 result 并置 `done`
