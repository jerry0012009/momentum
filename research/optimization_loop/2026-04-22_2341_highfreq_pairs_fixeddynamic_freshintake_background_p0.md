# bot3 optimization loop — high-frequency fixed/dynamic threshold pairs fresh intake 收口 background/P0

- 时间：2026-04-22 23:41 UTC
- Cycle item: 2
- Target: `research/quant_digests/2026-04-22_2118_highfreq-pairs-fixeddynamic-threshold-alpha.md`
- Verdict: `background/P0`

## 本轮只执行的动作
只执行当前最前的 pending 小点：对 `selected pair + spread z-score + fixed/dynamic threshold fade` 做 fresh intake first verdict，最小 decisive blocker 只检查它是否相对已在 runtime 里存活/上线的 pairs family（尤其 `Rank 424 / 431`）留下了**可独立排队的新 after-cost pocket**，而不是旧 high-frequency threshold pairs 主题的 replay。

## 使用证据
- digest：`research/quant_digests/2026-04-22_2118_highfreq-pairs-fixeddynamic-threshold-alpha.md`
- 当前 probe 汇总：`reports/artifacts/quant_digests/hf_pairs_fixed_vs_dynamic_probe_summary_2026-04-22.csv`
- 对照 family：
  - `research/quant_digests/2026-03-26_0803_fixed-threshold-hf-pairs-spread-mr.md`
  - `research/optimization_loop/2026-04-21_2322_dynamic_cointegration_halflife_freshintake_background_p0.md`
  - `research/optimization_loop/2026-04-21_1306_rank431_p2_exit_promote_p3_recentslice_overlap.md`

## 最小 decisive 检查

### 1) 这不是新的 raw alpha 主语，而是 desk 已经 intake 过的高频 pairs threshold family 复述
这篇 digest 的核心对象仍是 `selected pair + spread z-score + threshold fade`。但这个 family 早在 `2026-03-26_0803_fixed-threshold-hf-pairs-spread-mr.md` 就已经被 desk 明确 intake：当时同一篇 2025 论文已经把 `15m/5m` high-frequency pairs、`fixed vs dynamic threshold`、以及 threshold 本身是 alpha 厚度的一部分写清楚。

因此本轮若想 `keep_P1`，必须证明它不是“把已经 intake 过的 threshold pairs 主题再写一遍”，而是 recent probe 真的留下**相对已知 family 更强、更独立的 after-cost pocket**。

### 2) recent probe 虽有 gross edge，但 strongest summary 仍更像 family tuning，而不是新的 front object
当前 summary：
- `15m fixed`: `65` trades，`avg_gross ≈ +8.81bps/笔`
- `15m dynamic`: `68` trades，`avg_gross ≈ +15.78bps/笔`
- `5m fixed`: `56` trades，`avg_gross ≈ +14.33bps/笔`
- `5m dynamic`: `52` trades，`avg_gross ≈ +9.34bps/笔`

即便先按 digest 自己采用的简化口径粗扣 `8bps round-trip`，留存也只是：
- `15m fixed ≈ +0.81bps/笔`
- `15m dynamic ≈ +7.78bps/笔`
- `5m fixed ≈ +6.33bps/笔`
- `5m dynamic ≈ +1.34bps/笔`

这说明它有可读的 gross/薄净边，但系统认知改变点主要是：**fixed 与 dynamic 的优劣受 pair/周期影响，并非论文 headline 可直接照搬。** 这更像 pairs family 的参数/threshold 设计提示，而不是足够独立的新队列对象。

### 3) pocket 也没有证明自己脱离已 live pairs family
本轮最厚 pocket 集中在：
- `15m dynamic`: `BTC/SOL`、`DOGE/LINK`、`BTC/ETH`
- `5m fixed`: `AVAX/LINK`、`DOGE/ADA`
- `5m dynamic`: `AVAX/LINK`、`SOL/LINK`

但这些 pair/pocket 没有形成相对已 live `Rank 424 / cointegration-first pair admission × strongest residual z-score spread fade` 与 `Rank 431 / cointegration maker-first + hard time-stop pairs` 的明显新宿主。它们更像是：
- 对现有 pairs family 提供“哪个 pair、哪个周期、fixed 还是 dynamic 阈值更厚”的 tuning 提示；
- 而不是额外创造一个值得前排排队的新 raw alpha 身份。

更关键的是，`2026-04-21_2322_dynamic_cointegration_halflife_freshintake_background_p0.md` 已经把同类问题诚实收口过一次：当 threshold/admission 改写只留下少数 alt-heavy pocket、但没扩展成相对 `Rank 424 / 431` 独立的 after-cost family 时，默认应作为 pairs family 组件信息吸收，而不是再前排保留一个新对象。本轮证据仍符合这一路径。

## 结果
`selected pair + spread z-score + fixed/dynamic threshold fade` 的 fresh intake first verdict 已诚实收口 `background/P0`：recent probe 虽在 `15m dynamic` 与 `5m fixed` 上留下 `+7.78bps/笔`、`+6.33bps/笔` 级别的薄 after-cost proxy，并显示 `fixed vs dynamic` 的优劣具有 pair/周期敏感性，但该对象并未证明自己超出 desk 已 intake 的 high-frequency threshold pairs family，也没有形成相对已 live `Rank 424 / 431` 可独立排队的新 after-cost pocket；因此它当前只保留为 pairs family 的 threshold / pair-pocket 调参提示，不进入 survivor。

## 回写
- `Fresh intake slot` 更新为本对象的 `background/P0` 收口结果
- `cycle_plan` item2 -> `status: done`
- `cycle_plan` item2 `result` 写回上述一句话结论
- `Background pool.latest_parked_record` 追加本日志

## 尾注
本轮有真实推进（完成了 pending 小点并形成新 verdict），后续按流程尝试：
1. best-effort 刷新首页
2. 发送中文邮件摘要
