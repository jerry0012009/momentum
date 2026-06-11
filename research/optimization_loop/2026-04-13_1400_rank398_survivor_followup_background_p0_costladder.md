# bot3 optimization loop log — 2026-04-13 14:00 UTC

## 执行小点
- target: `Rank 398 / local-extrema branch-split long router (majors-only seed)`
- action: survivor 唯一 follow-up（`majors-only` 分支独立 `6/10/15 bps per-side` 成本阶梯 + horizon 稳健性；补 1 条 execution realism）

## 复核输入
- 指标文件：`reports/artifacts/quant_digests/2026-04-13_localextrema_probe_metrics.csv`
- 口径说明：原表 `avg_bps` 为 gross；本轮按 `per-side` 成本阶梯折算为 round-trip：
  - `6 bps/side -> 12 bps RT`
  - `10 bps/side -> 20 bps RT`
  - `15 bps/side -> 30 bps RT`

## 结果（majors-only，分支独立）
### BTC
- `15m / max_branch`：
  - `h=24`: gross `+35.05` -> net(`12/20/30`) = `+23.05 / +15.05 / +5.05` bps
  - `h=36`: gross `+19.58` -> net(`12/20/30`) = `+7.58 / -0.42 / -10.42` bps
- `15m / min_branch`：`h=24/36` 均显著负
- `5m` 两分支在 `>=12bps RT` 下均不稳定（`max` 为负，`min` 仅接近打平）

### ETH
- `15m / max_branch`：
  - `h=24`: gross `+63.27` -> net `+51.27 / +43.27 / +33.27`
  - `h=36`: gross `+9.29` -> net `-2.71 / -10.71 / -20.71`
- `15m / min_branch`：
  - `h=24`: gross `-43.36`（负）
  - `h=36`: gross `+35.57` -> net `+23.57 / +15.57 / +5.57`
- `5m / min_branch`：`h=36` 仍为正（net `+43.83 / +35.83 / +25.83`），但缺少第二 horizon 佐证

## 最小 execution realism 子检查（1 条）
- 检查点：`next-open` 成交假设下的滑点容忍区间是否足以覆盖常见撮合抖动。
- 结论：唯一具备双 horizon 连续为正的口袋仅剩 `BTC 15m max_branch`，且在 `h=36` 对应净边际仅 `+7.58bps RT`（约 `3.79bps/side` 额外容忍）；当成本升至 `10bps/side` 已转负。该容忍区间过窄，无法支撑“可稳定执行”的 admission 级别判断。

## 出口决策
- verdict: `background/P0`（不 `promote_P2`）
- 原因：本轮唯一 survivor follow-up 已用完；在要求的 `6/10/15 bps per-side` 成本阶梯与 horizon 稳健性下，majors-only 分支表现为强烈参数/成本敏感，未形成可进入 `P2` 的稳健可执行证据。

一句会改变系统认知的话：
`Rank 398` 的 majors-only 分支化优势仅在低摩擦窄窗成立，`10bps/side` 即出现关键 horizon 失稳，故 survivor 出口收口为 `background/P0` 并释放前排槽位。