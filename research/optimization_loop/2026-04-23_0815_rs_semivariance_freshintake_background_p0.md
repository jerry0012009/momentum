# bot3 optimization loop — rs semivariance downside continuation fresh intake -> background/P0

- Time: 2026-04-23 08:15 UTC
- Target: `research/quant_digests/2026-04-22_2310_rs-semivariance-downside-continuation-alpha.md`
- Action: fresh intake first verdict
- Verdict: `background/P0`

## Why this step was the current front pending item
`BOT2_BOT3_STATE.md` 当前 `cycle_plan` 的第一个 `pending` 小点就是这条 fresh intake，因此本轮只执行它，不重排后续小点。

## Minimal decisive blocker checked
目标问题不是再补一轮泛化对比，而是回答：

> `relative semivariance downside asymmetry × continuation` 是否真的留下了 **独立于现有 downside/trend family 的 after-cost continuation pocket**，并且不是 **单币 / 单月 lucky-run**？

最便宜、最能改变结论的 honesty 检查是：
- 直接复核 digest 自带 artifacts；
- 看 strongest pocket 是否跨多个币、多个最近月份都仍保得住；
- 若 strongest 展示本身在月份切片上塌缩，就不再给 survivor 预算。

## Evidence reviewed
- Digest: `research/quant_digests/2026-04-22_2310_rs-semivariance-downside-continuation-alpha.md`
- Artifacts:
  - `reports/artifacts/quant_digests/rs_semivariance_shortprobe_20260422_2310/summary.csv`
  - `reports/artifacts/quant_digests/rs_semivariance_shortprobe_20260422_2310/basket_summary.csv`
  - `reports/artifacts/quant_digests/rs_semivariance_shortprobe_20260422_2310/sample_trades_q90_h8.csv`

## What changed system knowledge
表面 strongest summary 确实很好看：
- basket `q=0.95, hold=8`：`net6 ≈ +48.98bps/trade`
- symbol 级 `q=0.95, hold=8`：
  - `BTC ≈ +27.82bps/trade`
  - `ETH ≈ +42.36bps/trade`
  - `SOL ≈ +76.75bps/trade`

但最小 honesty 切片一做，结论明显收缩：

### 1) strongest story 主要靠最近单月/少数月份抬出来
对 artifact 里可直接复核的 `sample_trades_q90_h8.csv` 做月份切片后，`net6_bps/trade` 为：

- `BTCUSDT`
  - `2025-12: +38.03`
  - `2026-01: -81.75`
  - `2026-02: -83.54`
  - `2026-03: +6.55`
  - `2026-04: +121.10`
- `ETHUSDT`
  - `2025-12: +148.93`
  - `2026-01: -151.17`
  - `2026-02: -85.37`
  - `2026-03: +24.24`
  - `2026-04: +105.68`
- `SOLUSDT`
  - `2025-12: +55.30`
  - `2026-01: -130.86`
  - `2026-02: -85.00`
  - `2026-03: -15.60`
  - `2026-04: +49.53`

这说明 strongest continuation edge 没有表现成“最近多个相邻月份都同向成立”的稳定 pocket；相反，`2026-01/02` 在三币上都明显为负，而较亮眼的结果主要由 `2026-04` 与一部分 `2025-12` 抬起来。

### 2) 它更像 downside-state router，而不是新的独立 alpha 主语
当前可见价值更像：
- 把“高波动”拆成 `RS+ / RS-`，作为 downside state / short-bias gate；
- 帮现有 downside/trend family 识别什么时候更偏向 continuation；
- 但还没有证明它本身已经形成一个跨月稳定、可独立排队的 after-cost short shell。

### 3) 现成展示缺少“非单月 lucky-run”通过证据
cycle_plan 对 fresh intake 的门槛写得很清楚：
- 只有至少一个 **非单币、非单月 lucky-run** 的 after-cost pocket，才 `keep_P1`。

本轮最小 honesty 检查后，当前证据不满足这一门槛，因此不能给 survivor。

## Final result
`relative semivariance downside asymmetry × continuation` 已完成 first verdict 并收口 `background/P0`：虽然 digest strongest summary 在 `q=0.95, hold=8` 上给出看似很厚的 short continuation net edge，但最小月份切片显示 `2026-01/02` 在 `BTC/ETH/SOL` 上同时明显为负，正边际主要由 `2025-12/2026-04` 少数月份抬起，未通过“非单币、非单月 lucky-run”的独立 after-cost alpha 门槛；当前更适合作为 downside-state / trend-family router 提示，而不是新的前排对象。
