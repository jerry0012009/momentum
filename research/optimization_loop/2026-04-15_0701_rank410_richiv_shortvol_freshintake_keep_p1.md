# Rank 410 fresh intake — BTC rich-IV short-vol carry shell（keep_P1）

- 时间：2026-04-15 07:01 UTC
- 执行者：bot3
- 对应 cycle_plan 小点：#1 `research/quant_digests/2026-04-15_0538_richiv-shortvol-carry-alpha.md`

## 本轮执行
1. 复核 source digest 的最小可复现实证（`2026-04-15_ivrv_shortvol_probe_summary.json`）：
   - BTC `q70` rich-IV short-only（非对称）优于 repo 对称 long/short 壳（Sharpe `0.57` vs `0.17`）。
2. 在当前小点内补做一个最小 honesty/execution realism 子检查（只做会改变结论的一项）：
   - 新增 `t+2`（以一周滞后信号近似，避免同周确认即交易）+ 成本阶梯 `4/6/8 bps` 的最小重算，产出 `reports/artifacts/quant_digests/2026-04-15_ivrv_shortvol_t2_cost_probe.json`；
   - 结果（BTC rich-IV short-only）在 `41` 笔交易下保持费后正 pocket：
     - `4 bps`: avg `0.0567`, Sharpe `0.266`, win rate `70.7%`
     - `6 bps`: avg `0.0565`, Sharpe `0.265`, win rate `70.7%`
     - `8 bps`: avg `0.0563`, Sharpe `0.264`, win rate `70.7%`
3. honesty 口径结论：该 probe 的 `RV_forward` 为 `idx+1..idx+7` 严格前瞻窗口，且采用滞后信号后未见“同周确认直接成交”型 leakage；但仍是 DVOL proxy，不等价真实 option fill。

## 结论（first verdict）
`Rank 410 / BTC rich-IV short-vol carry shell`：`keep_P1`（已分配正式 Rank）。

一句改变系统认知的话：
> 在统一 `t+2` + `4/6/8 bps` 的最小可交易近似下，BTC rich-IV short-only 仍保留稳定费后正 pocket，说明该候选不是 repo 叙事噪音，可进入 survivor 的唯一一次低成本接续验证。

## 唯一 survivor follow-up blocker
把 DVOL proxy 升级为真实可交易腿：固定 `5d~9d` 到期 ATM straddle mid-IV，按 `5m` delta hedge（含 option spread + fee + perp hedge/funding）回放净值；若净费用后不再保留正 pocket，则回收至 background。

## 尾部执行状态（non-blocking）
- 首页刷新命令 `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` 在本轮执行中被 SIGKILL 终止；按 policy 记为非阻断尾部失败，不回滚本轮 verdict/state/log。
- 邮件通知命令已独立执行并发送成功。
