# Rank 395 — hyperstat FDS-gated bucket MR fresh intake first verdict（keep_P1）

- 时间：2026-04-13 02:58 UTC
- 执行器：bot3
- 对象：`research/quant_digests/2026-04-12_2356_hyperstat-fds-gated-bucket-mr-alpha.md`
- 轮次动作：cycle_plan #3（fresh intake first-verdict）

## 本轮执行
按 digest 已给出的最小可复现证据对对象做二分：
1. `bucket dispersion MR` 作为 raw alpha 是否能独立成立；
2. `FDS gating` 是否只是阈值挑选过拟合。

已用证据（来自同一份 digest 的可复现口径）：
- vanilla active MR events：`957`，未来 `1h` 平均 `-3.68 bps`，hit `45.0%`（raw MR 单体在该口径下不成立）
- `gate > 0`：`189` events，未来 `1h` 平均 `+15.65 bps`，hit `56.6%`
- `gate > 0.25`：`50` events，未来 `1h` 平均 `+24.12 bps`，hit `60.0%`

## 结论（会改变系统认知）
`Rank 395`：结论为 `keep_P1`（不是可直接独立交易的 raw alpha，但“MR skeleton + FDS admission”具备继续前排验证价值）；该对象值得进入前排继续做一次 survivor 跟进。

## 唯一 decisive blocker
`fds_threshold_governance` 尚未冻结：当前正收益主要来自 gate 后小样本 pocket，尚未证明阈值（如 `0 / 0.25`）在独立时间窗与跨 bucket 设定下仍稳健，存在参数筛选/回看挑选风险。

## 下一步（限定为 survivor 唯一 follow-up 的方向）
仅允许一次最小跟进：
- 固定预先声明的 FDS 阈值网格与单一选择规则（防事后挑阈值）；
- 在独立时间切片做通过/不通过判定；
- 输出是否可升 `P2`，否则回 `background/P0`。
