# Rank 414 P2 admission round-1（cross-asset / time / parameter + honesty）

- 时间：2026-04-15 11:58 UTC
- 对象：`Rank 414 / roundtrip regime-stable pairs admission (admission-layer scope)`
- 本轮动作：按 `t+2 + 4/6/8bps` 统一口径完成 P2 admission round-1，补齐 cross-asset / time / parameter 稳定性，并追加最小 execution realism 检查（摩擦抬升到 net10/net12 的脆弱点）。

## 证据产物
- `reports/artifacts/optimization_loop/rank414_p2_admission_round1_20260415/cross_asset_bucket_summary.csv`
- `reports/artifacts/optimization_loop/rank414_p2_admission_round1_20260415/time_interval_portability_summary.csv`
- `reports/artifacts/optimization_loop/rank414_p2_admission_round1_20260415/parameter_topn_stability.csv`
- `reports/artifacts/optimization_loop/rank414_p2_admission_round1_20260415/honesty_friction_proxy.csv`

## 结果要点
1. **cross-asset（15m）**
   - trade-quality top8 在 `alt-alt` 与 `maj-alt` 两个桶都为正：
     - `alt-alt trade_weighted_net8_bps = +0.1063`（4/4 正）
     - `maj-alt trade_weighted_net8_bps = +0.0077`（3/4 正）
   - 但 `maj-alt` 仍接近零轴，鲁棒性边际偏薄。

2. **time stability（interval portability）**
   - 同一 focus pair 集在 `15m` 为正（`trade_weighted_net4_bps = +0.2232`），
   - 迁到 `3m/5m` 即转负（`-0.0276 / -0.0427`）。
   - 说明 admission uplift 当前显著依赖 15m 采样尺度，时间尺度可迁移性不足。

3. **parameter stability（top-N 扰动）**
   - `top6/top8/top10/top12` 全部保持 `trade_weighted_net8_bps > 0`：
     - `+0.0832 / +0.0587 / +0.0539 / +0.0298`
   - 结论：参数扰动层面通过，未见“一改 N 就翻负”的脆弱性。

4. **honesty / execution realism（最小摩擦抬升检查）**
   - 基于 net8 结果做最小加摩擦代理：`net8 -> net10 -> net12`
   - trade-weighted 代理净值：`+0.0587 -> +0.0187 -> -0.0213`
   - 结论：在更严苛摩擦下（约 net12）会翻负，当前容量/冲击余量不足以支持直接 P3。

## P2 出口结论（本轮）
**结论：`keep_P2`（锁定唯一 decisive blocker）。**

一句会改变系统认知的话：
> `Rank 414` 在 cross-asset 与 top-N 参数扰动下仍保留费后正值，但时间尺度与摩擦余量显示“离开 15m 或成本继续抬升即翻负”的单一决定性阻断，因此本轮不升 P3，继续 `P2` 并把 blocker 收口为“15m-only execution envelope 的容量/摩擦边界验证”。

## 下一步（只定义 blocker，不重排）
- 唯一 blocker：在 **15m-only** 约束下补一个最小容量分层/滑点分层验证，确认 `maj-alt` 边际与更高摩擦场景是否仍可维持 `trade_weighted_net8_bps > 0`。
