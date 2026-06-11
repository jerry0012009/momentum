# Rankless fresh intake：sign-aware XS momentum × ATR/volume gate -> background/P0

- 时间：2026-04-12 19:51 UTC
- 执行动作：`cycle_plan` 第 3 小点（fresh intake first verdict）
- 目标对象：`research/quant_digests/2026-04-12_1639_signaware-xsmomentum-atrvolume-alpha.md`

## 本轮最小证据
1. **成本后有效性（主结论轴）**
   - 依据 artifact：`reports/artifacts/literature/cross_sectional_momentum_repo_port_probe_2026-04-12_costladder.csv`
   - `15m + sign_aware_exit` 在 gross 下 `+0.627 bps/bar`，但平均换手约 `0.3056x/bar`。
   - 代入 round-trip `8 bps` 后，`net_mean_bps_per_bar = -0.5953`，`net_total_return_pct = -70.72%`。
   - 该口径下已不能支撑 `keep_P1`。

2. **honesty / execution realism 最小快检（delayed-confirmation / leakage）**
   - 复核 repo `step_1.py`：
     - 信号端使用 `combined_signal = signal.shift(1)`；
     - 收益端使用 `open.pct_change().shift(-1)`；
     - ATR / volume / rolling return 亦有 `shift(1)` 处理。
   - 结论：代码层未见“同 bar 读取未来值”的直接泄漏；本轮否决并非由 lookahead 伪像导致，而是**成本后边际不足**。

## first verdict
- 结论：`background/P0`
- 单一 decisive blocker：**成本后边际不足（高换手导致 friction 吞没 edge）**。
- 处理：不进入 `P1`，不分配 Rank，回收至 background。

## 对 runtime 的写回要求
- `Fresh intake slot.latest_result` 更新为本对象的 `background/P0` 结论。
- `Fresh intake slot.latest_result_record` 指向本文件。
- `Background pool.latest_parked` 更新为本对象及同一 blocker。
- `cycle_plan` 第 3 小点写回 `done`。
