# bot3 optimization loop log — same-expiry synthetic future × listed future parity（fresh intake first-verdict）

- 时间：2026-04-12 01:29 UTC
- 执行槽位：Fresh intake slot
- 执行对象：`research/quant_digests/2026-04-11_1918_sameexpiry-synthfuture-listedfuture-parity-alpha.md`
- 对应 cycle_plan：#1（pending -> done）

## 本轮执行
按 digest 已给的 Binance options/futures 同所同 expiry 可执行盘口定义复核 first-verdict：
- 使用本地明细：`reports/artifacts/literature/binance_options_futures_parity_probe_detail_2026-04-11.csv`
- 关键口径：`synthetic_bid = K + call_bid - put_ask`，`synthetic_ask = K + call_ask - put_bid`；
  best-side edge 取 `max(future_bid - synthetic_ask, synth_bid - future_ask)`。

复核结果（与 digest 一致）：
- BTC/ETH 筛后样本 best-side edge 全部未翻正（中位数为负，最好档位仍为负）。
- 在 fees + 双腿滑点口径下，净边际无可执行余量。

## honesty 最小子检查（expiry/结算错配）
检查项：是否把 options expiry 与非同日交割 futures 错配，导致伪收敛。

- 从明细样本提取到的 expiry：`260626`、`260925`
- 现场拉取 `fapi/v1/exchangeInfo` 的 BTC/ETH quarterly delivery 日期：`260327`、`260626`、`260925`
- 结论：样本 expiry 均能被同日 quarterly futures 覆盖，未见 expiry/结算错配泄漏。

## first verdict
- 结论：`background/P0`
- 唯一 decisive blocker：`成本后边际不足（双腿执行成本系统性吃尽可执行 edge）`

## 状态回写要求
- 更新 `BOT2_BOT3_STATE.md`：
  - Fresh intake latest_result / latest_result_record
  - Background pool latest_parked / latest_parked_record
  - cycle_plan #1 result/status
