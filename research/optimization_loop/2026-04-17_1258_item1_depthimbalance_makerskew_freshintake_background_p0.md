# 2026-04-17 12:58 UTC — depth imbalance → fair-value shift → maker quote skew shell（fresh intake）first verdict

## 执行小点
- target: `research/quant_digests/2026-04-17_0920_depthimbalance-maker-skew-mm-shell.md`
- action: fresh intake first-verdict（含最小 honesty / execution realism 子检查）

## 本轮最小检查（honesty / execution realism）
只保留 1 个最 decisive blocker：**maker fill realism**。

依据本轮 digest 已附 public-depth sanity probe（`reports/artifacts/quant_digests/2026-04-17_depth_imbalance_maker_skew_probe_summary.json`）：
- `5s`：high OBI `+0.589bps` vs low OBI `-0.797bps`
- `10s`：high OBI `+0.972bps` vs low OBI `-0.628bps`
- `20s`：high OBI `+0.638bps` vs low OBI `-0.205bps`
- 样本仅 `180s / 180` 个观测，且来自 `REST top20 depth` 秒级采样代理

这足以说明 **OBI→几秒级 mid 漂移方向性存在**，但还不足以支撑当前对象作为独立可交易 maker shell 保留前排：
1. 可见 edge 量级仍只有 `~0.6–1.0bps` 级别；
2. 当前证据口径还是 `mid-price markout`，不是可成交后的净改善；
3. 一旦把真实 maker 排队位置、missed fill、撤单/重挂延迟、被动单 adverse selection 加回去，现有毛边际大概率被吃掉；
4. 因此对本轮 first-verdict 来说，`REST depth 采样误差` 与 `spoof-cancel 污染` 都还不是最 decisive 的那一刀，真正决定是否能留在前排的是 **fill realism 下 edge 是否还够厚**；按现有证据，答案是否定的。

## first verdict
- decision: `background / P0`
- decisive blocker（唯一）: **公开 depth proxy 下可见的几秒级 OBI 边际只有约 `0.6–1.0bps`，尚未覆盖真实 maker fill / queue / cancel-delay 摩擦，因此不足以把该对象保留为独立前排候选。**

## 与现有对象关系
- 该对象更适合作为 microstructure execution / quote-leaning 组件参考，而不是新的独立前排策略对象。
- 这次 verdict 不否认 `OBI -> short-horizon drift` 这条 base alpha 本身存在；否定的是**在当前公开 proxy 与现实执行约束下，把它包装成独立 maker shell 候选继续占用 P1/P2 槽位**。
- 因此不分配新 Rank，不进入 survivor，不占用 P1/P2/P3。

## runtime 回写要点
- `Fresh intake slot`：本对象已完成 first verdict，结论 `background/P0`；fresh intake 顺位切换到下一条 pending intake。
- `Background pool.latest_parked`：追加本对象。
- `cycle_plan`：第 1 项标记 `done`，写入会改变系统认知的结果句。
