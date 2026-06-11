# bot3 optimization loop log — 2026-04-16 01:11 UTC

## 执行小点
- cycle_plan item 1
- target: `Rank 417 / cointegration-first pair admission × no-stop intraday spread fade (Asia gate: UTC 0/5/6)`
- action: P2 admission（出口优先）——一次性补齐 `cross-asset/time/parameter` 稳健性并做最小 execution realism 核对（检查是否由少数 pair/长持仓尾部驱动）

## 结果摘要（会改变系统认知）
`Rank 417` 在既有 `Asia UTC 0/5/6` 门控下费后总体仍为正（`net8=+12.01bps`），但 alpha 主要由少数 pair 集中贡献且高 `|z|` 分层不稳，当前仅剩一个 decisive blocker：`cross-asset concentration` 尚未通过，因此本轮结论为 `keep_P2`（唯一 blocker 已明确）。

## 核心证据
数据源：
- `reports/artifacts/quant_digests/2026-04-15_cointegrationfirst_nostop_t2_probe_trades.csv`

口径（保持不变）：
- `t+2` 入场延迟
- round-trip 成本 `4/6/8bps`
- Asia 仅保留 UTC `0/5/6`，EU/US 不变

门控后总体：
- `n=78`（EU 36 / US 26 / Asia 16）
- `net4/net6/net8 = +20.01/+16.01/+12.01bps`

### 1) cross-asset stability（本轮核心）
- pair 级 `net8` 贡献：
  - `SOLUSDT-XRPUSDT`: `+615.03bps`
  - `XRPUSDT-LTCUSDT`: `+407.00bps`
  - `ETHUSDT-BNBUSDT`: `-542.34bps`
  - `ETHUSDT-LTCUSDT`: `-23.20bps`
- 集中度：top1 pair 贡献占总净收益约 `65.7%`，top2 贡献已超过总净收益（说明其余 pair 合计拖累）。
- 压力测试（去掉 top1）后仍正但明显降至 `net8=+5.36bps`，显示当前组合可交易性对少数 pair 较敏感。

### 2) time stability
- 按日桶：15 个桶中正收益占比 `66.7%`，`net8` 区间 `[-95.25, +91.79]bps`
- 按周桶：3 个桶中 2 个为正，存在一周显著回撤（`-19.43bps`）

### 3) parameter stability
- `|entry_z|` 三分位：
  - 低/中分位 `net8` 为正（`+15.24/+21.70bps`）
  - 高分位 `net8` 转负（`-0.92bps`）且持仓更长（`hold_p50=60.5 bars`）
- 结论：参数层在高阈值区域不稳，和集中风险一致。

## 最小 honesty / execution realism 核对
- 未放宽任何假设；仅在既有交易明细上做聚合切片。
- 持仓尾部仍偏长（`hold_bars p90≈84.9`, `max=159`），与 no-stop 结构一致；该点作为风险注记保留，但本轮唯一 decisive blocker 仍定义为 `cross-asset concentration`（因为其直接决定可复制性与组合鲁棒性）。

## 本轮执行结论
- verdict: `keep_P2`
- unique_decisive_blocker: `cross-asset concentration not yet resolved (alpha heavily relies on a small subset of pairs while some ETH-leg pairs remain structurally negative)`
- status: `done`

## 尾部执行状态（非阻断）
- homepage publish：待尾部命令执行。
- 邮件通知：待尾部命令执行。
