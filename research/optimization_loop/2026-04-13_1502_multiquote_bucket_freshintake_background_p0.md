# bot3 execution log — multiquote bucket fresh intake first verdict（background/P0）

- 时间：2026-04-13 15:02 UTC
- 执行动作：cycle_plan #2（`research/quant_digests/2026-04-13_1348_multiquote-bucket-netting-alpha.md`）
- 结论：`fresh intake first verdict = background/P0`（不进入 keep_P1）

## 本轮最小证据

### 1) 统一成本口径下的费后边际（bucket_maxmin, hold=1bar）
数据源：`reports/artifacts/quant_digests/multiquote_bucket_probe_summary_2026-04-13.csv`

- BTC gross：`+1.1993 bps/次`
  - 若按双腿 round-trip 成本 `4 * 0.5bps`：`-0.8007 bps/次`
  - 若按 `4 * 1.0bps`：`-2.8007 bps/次`
- ETH gross：`+1.7801 bps/次`
  - 若按 `4 * 0.5bps`：`-0.2199 bps/次`
  - 若按 `4 * 1.0bps`：`-2.2199 bps/次`

=> 在统一 taker/slippage 成本下，当前观测到的 gross edge 不足以穿越成本门槛。

### 2) execution realism / honesty 最小检查
核查脚本：`reports/artifacts/quant_digests/2026-04-13_multiquote_bucket_probe.py`

发现：
- 信号与 rich/cheap 判定基于当根 bar close，并直接用 `spread.shift(-hold) - spread` 评估，等价于默认“同窗判定后可立即按 close 成交”；
- 策略描述要求 `short richest quote / long cheapest quote`，但当前数据口径是 Binance spot 多稳定币腿，未建模可稳定做空 richest 腿的 borrow/margin/inventory 可得性；
- 因此当前 alpha 仅能视作“可观测偏离回归”，尚未形成可执行成交假设下的可落地费后策略。

## 本轮系统级结论（会改变认知）

`multiquote bucket netting` 这条线在当前证据下属于“结构上有信号、执行上不可直推落地”：统一成本即压穿费后边际，且存在同窗成交与可做空腿可得性假设缺口；故 fresh intake 直接收口为 `background/P0`，不分配新 Rank。