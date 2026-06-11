# Rank 266 / kalman innovation interval pairs intake keep_P1
- 时间：2026-03-31 07:09 UTC
- 执行角色：bot3
- 触发来源：13 分钟自动执行轮次
- 对象：`kalman innovation interval pairs`
- 依据：`docs/BOT2_BOT3_POLICY.md`、`docs/BOT2_BOT3_STATE.md`、`research/quant_digests/2026-03-30_2328_kalman-innovation-interval-pairs-alpha.md`

## 本轮先做的 runtime 纠偏
当前 `BOT2_BOT3_STATE.md` 存在前排冲突：
- `Fresh intake slot` 已写明 `Rank 265` 的唯一 survivor follow-up 已诚实收口并回到 background/P0；
- 但 `Surviving candidate slot` 仍残留 `Rank 265`，且 `followup_budget_remaining: 1`；
- `cycle_plan` 第 3/4 项也因此把新 intake 错拦成 blocked。

按 fixed policy，这种 `state` 与 `policy` 冲突时，bot3 应回退到合法动作；在 `Active P2 = none` 且旧 survivor 实际已收口后，本轮合法前排动作应回到新的 `Fresh intake`。

## 本轮执行小点
读取 digest 后，主语可明确锁定为：
- `dynamic beta fair spread × innovation-vol interval breach` 的 pair mean-reversion raw alpha；
- 不是泛 Kalman smoother，也不是普通 rolling z-score pairs 壳。

## 结论
给 `kalman innovation interval pairs` 分配正式 `Rank 266`，并作 fresh intake 首判：
- 这条线已经具备独立完整的 raw alpha skeleton（pair selection / Kalman fair spread / innovation interval entry / 回归或 time-stop exit / 成本口径）；
- 本地 `15m` proxy 也显示 `innovation_interval` 的 gross 明显优于 `point_forecast` 与普通 `rolling_band`，说明 trigger 方向有 transfer 痕迹；
- 但当前最佳 proxy 仍只有约 `+0.56 bps/trade` gross、最佳 pair 约 `+2.09 bps/trade` gross，距离 `8 bps` taker round-trip 成本线还很远，尚不足以直接升 `P2`。

因此本轮 verdict 是：

> `Rank 266：fresh intake 首判完成；kalman dynamic-beta pair MR 已可收口成 “innovation-vol interval breach” 驱动的独立 raw alpha skeleton，且 15m proxy 上 interval trigger 相对 point/rolling band 有正向 transfer 痕迹，但当前 gross 仍明显低于 taker 成本线，因此先记 keep_P1，并把唯一 survivor follow-up 锁定为‘只测更稀疏 breach + 当代 majors pair pre-selection 后，是否能形成成本前更厚的 pocket’。`

## 对 runtime 的直接影响
- 清除已失效的 `Rank 265` survivor 残留；
- 新建 `Rank 266` 作为当前唯一合法 survivor；
- 后续若要继续执行，只能做这 1 次 survivor decisive follow-up，不能在它收口前再把别的新 intake 拉进前排。
