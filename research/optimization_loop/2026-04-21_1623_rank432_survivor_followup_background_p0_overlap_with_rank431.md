# Rank 432 / spread z-score fade × zero-cross exit × kill-switch — survivor 唯一 follow-up -> background/P0

- 时间：2026-04-21 16:23 UTC
- 执行者：bot3
- 对应 cycle_plan 小点：1
- target: `Rank 432 / spread z-score fade × zero-cross exit × kill-switch`

## 本轮只执行的动作
按当前 `cycle_plan`，本轮只做 `Rank 432` 的 survivor 唯一 follow-up：围绕唯一 blocker `distinctness / overlap`，检查它相对现有 `Rank 431 / cointegration maker-first + hard time-stop pairs` 是否真的留下新的退出/停机语义；若没有，则必须直接收口 `background/P0`，不能再开放式 `keep_P1/keep_P2`。

## 使用证据
### Rank 432
- `reports/artifacts/quant_digests/cointegration_zero_cross_summary_2026-04-21.csv`
- `reports/artifacts/quant_digests/cointegration_zero_cross_trades_15m_2026-04-21.csv`
- `reports/artifacts/quant_digests/cointegration_zero_cross_trades_5m_2026-04-21.csv`
- `research/optimization_loop/2026-04-21_1510_rank432_cointegration_zerocross_freshintake_keep_p1.md`
- `research/quant_digests/2026-04-21_1231_cointegration-zerocross-killswitch-alpha.md`

### Rank 431
- `research/optimization_loop/2026-04-21_0858_rank431_cointegration_maker_timestop_pairs_keep_p1.md`
- `research/optimization_loop/2026-04-21_1306_rank431_p2_exit_promote_p3_recentslice_overlap.md`
- `research/optimization_loop/2026-04-21_1408_rank431_p3_launch_wiring_connected_runner_live.md`
- `reports/artifacts/quant_digests/rank431_survivor_followup_proxy_summary_2026-04-21.csv`
- `reports/artifacts/paper_rank431_cointegration_maker_timestop_pairs/rank431_frozen_launch_spec.json`

## 最小 decisive 检查

### 1) `Rank 432` 没有留下新的 pair family，只是同一 spread-fade 家族的更宽、更弱表达
`Rank 432` 的 digest 自己已经把结论写得很清楚：当前真正活下来的不是“严格 cointegration pair admission”，而更像更宽的 `cross-alt ratio / spread MR` 家族；而 `Rank 431` 已经把这条 desk 化后的 pair-MR family 进一步收口成可上线的 `rolling pair admission + maker-first + hard time-stop` 宿主。

也就是说，`Rank 432` 留下的核心 pair pocket（`SOL/ADA`、`SOL/DOGE`、`XRP/AVAX` 等）并没有证明自己属于另一个全新家族；它只是把同一类 pair spread fade 放宽到“全池 z-score 偏离就做、zero-cross or timeout 再退”。

### 2) `Rank 432` 的所谓新增语义（zero-cross / kill-switch）没有证明能带来比 `Rank 431` 更好的可迁移价值
`Rank 432` 全池 summary：
- `15m all`: `1986` 笔，`gross_mean_bps=+2.70`，`net_mean_bps=-5.30`
- `5m all`: `2373` 笔，`gross_mean_bps=+4.10`，`net_mean_bps=-3.90`
- short-half-life 子集也仍为负：`15m=-4.58bps/笔`，`5m=-4.69bps/笔`

这说明：`zero-cross exit + account kill-switch` 这套语义，在当前 public portability 下并没有把同族 pair-MR 提升成更强的 desk host，反而停留在“全池 gross 为正、费后整体为负”的研究壳。

相比之下，`Rank 431` 已经完成更强的 family 收口：
- 先用 `rolling pair admission` 把 pair 宿主收窄到可解释对象；
- 再用 `maker-first + timeout-cross + hard time-stop` 把执行 realism 落到可验证的 paper runner；
- 最终已经完成 `P3 launch wiring`，并正式写成 `connected_runner_live`。

若 `Rank 432` 真有独立价值，本轮应当能证明：
- `zero-cross` 相对 `hard time-stop / structure stop` 带来跨 pair、跨窗口都更稳的退出增量，或
- `kill-switch` 提供了 `Rank 431` 现有 launch spec 中缺失的、可迁移且决定性的组合层新能力。

现有 artifact 并未给出这类证据；`kill-switch` 只停留在 repo 壳描述，没有生成新的 after-cost durability 证明；`zero-cross` 则直接绑定在一个整体费后为负的更宽 pair 池上。

### 3) 当前活下来的 pair 也没有形成相对 `Rank 431` 的明显独立宿主
`Rank 432` first verdict 里保留的 pair pocket 主要是：
- `15m`: `SOL/ADA`、`SOL/DOGE`、`BNB/LTC`、`DOGE/ADA`
- `5m`: `SOL/DOGE`、`SOL/AVAX`、`XRP/AVAX`、`SOL/LTC`、`XRP/ADA`

这些对象说明的是“mid-cap residual spread MR 还有 pockets”，但并没有说明 `zero-cross exit` 本身就是新的独立主语。它更像是在给 `Rank 431` 已落地的 pair-MR family 提供“还能继续扩 host set / exit variants”的背景研究素材，而不是值得再单独保留一个前排 rank。

更关键的是：`Rank 431` 已经在同一家族里完成过一次 admission / overlap / execution realism 收口，并最终只把 `NEAR-ATOM` 设为 core、`AVAX-SUI` 设为 watch。当前 `Rank 432` 若要继续前排存在，必须证明自己不是“同一家族另一层 z-score 壳的泛化重命名”。这一步没有做到。

## 结论
本轮 survivor 唯一 follow-up 的出口结论是：`background/P0`。

一句话说：

> `Rank 432` 没有证明 `zero-cross exit + kill-switch` 相对已 live 的 `Rank 431` 留下独立、可迁移的新增退出/停机价值；当前可见 pocket 仍只是同一 pair spread-MR family 的更宽、更弱表达，因此本轮不升 `P2`，直接收口 `background/P0`。

## runtime 写回要点
- `Surviving candidate slot.current_target -> none`
- `followup_budget_remaining -> 0`
- `cycle_plan` item1: `status=done`
- `cycle_plan` item1.result: `Rank 432` 的 survivor 唯一 follow-up 已收口：`zero-cross exit + kill-switch` 未证明相对 `Rank 431` 留下独立、可迁移的新语义，当前 pockets 仍属同一 pair-MR family 的更弱重复表达，因此本轮直接转入 `background/P0``

## 一句话结果（写回 state）
`Rank 432 / spread z-score fade × zero-cross exit × kill-switch` 的 survivor 唯一 follow-up 已诚实收口：它没有证明 `zero-cross exit + kill-switch` 相对已 live 的 `Rank 431 / cointegration maker-first + hard time-stop pairs` 留下独立、可迁移的新增退出/停机价值；当前 `SOL/ADA / SOL-DOGE / XRP-AVAX` 等 pockets 仍属于同一 pair-MR family 的更宽、更弱重复表达，因此本轮直接转入 `background/P0`。
