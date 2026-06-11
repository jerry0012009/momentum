# bot3 execution log — item2 hl×pacifica net-apr carry fresh intake（background/P0）

- 时间：2026-04-16 06:55 UTC
- cycle_plan item: 2
- target: `research/quant_digests/2026-04-16_0538_hlpacifica-netapr-volumefilter-carry-shell.md`
- action: fresh intake first-verdict（统一 `t+2 + 4/6/8bps` + Asia/EU/US 口径）并补 1 个最小 execution realism/honesty 子检查

## 本轮执行

基于 intake 自带快照与本轮最小 honesty 子检查（funding 口径可移植性）做收口：

1. intake 快照（`hl_pacifica_probe_20260416_0536`）里，双边有 funding 的 `13` 个符号仅 `ETH` 通过 `net_apr>=5% + Pacifica 24h vol>=50M` 联合门槛；`SOL` 仅差一档流动性（约 `49.04M`）。
2. 在该快照中，候选已呈现明显单资产集中（可交易池接近单点），不满足跨资产可复制要求。
3. 最小 honesty/execution realism 子检查（artifact 见下）确认：跨 venue funding spread 若未先统一 funding interval 与年化口径，容易把“时钟/单位差异”误计为 alpha；该对象当前仍缺可直接支持统一 `t+2 + 4/6/8bps` + 分时段费后稳健性的最小可执行证据。

## 关键产物

- intake snapshot（既有）：
  - `reports/artifacts/quant_digests/hl_pacifica_probe_20260416_0536/funding_volume_probe.json`
- 本轮 honesty 子检查：
  - `reports/artifacts/optimization_loop/2026-04-16_hlpacifica_netapr_portability_honesty_20260416_065525.json`

## first verdict

`net APR carry × volume filter` 这条 HL×Pacifica fresh intake 在当前统一口径下未形成跨资产可复制、可诚实执行的费后证据（候选集中到单一 ETH，且 funding 时钟/年化口径仍待先行统一）；本轮收口为 `background/P0`（不进入 survivor，不分配 Rank）。
