# Rank 273 — whitelist peer-divergence × half-life-gated spread fade：fresh intake 首判 `keep_P1`

- 时间：2026-03-31 21:00 UTC
- 对象：`whitelist peer-divergence × half-life-gated spread fade`
- 来源：`research/quant_digests/2026-03-31_2048_whitelist-peer-divergence-halflife-spread-fade.md`
- 结论：分配正式 `Rank 273`，fresh intake 首判 `keep_P1`，进入唯一 survivor follow-up；当前**不直升 `P2`**。

## 为什么给 `keep_P1`
这条线已经能诚实收口成独立的 pairs / stat-arb raw alpha skeleton：
- 白名单 peer bucket 明确，不是全市场乱扫 pair；
- spread 定义明确：`spread = price_B - beta * price_A`，并用 z-score 做极端偏离入场；
- gate 也明确：`corr >= 0.95`、`6 <= half_life <= 15`、双腿等美元、非重叠资产、单腿失败 rollback；
- exit / timeout / hard stop 边界也能直接落成策略骨架。

这说明它不是 repo 壳、也不是“泛 pairs bot”叙事，而是可审计、可独立复现的一条 raw alpha lane。

## 为什么现在还不能进 `P2`
当前证据还不足以回答它是否已经是 desk 可 admission 的 survivor：
1. digest 已明确指出 repo 中 `96 bars // 1 week of 15-minute snapshots` 是口径错误；`96` 根 `15m` 只等于 24 小时，不是 1 周；
2. 同一对象在 `96-bar` 与 `672-bar` 估计下，pair discovery 结果差异很大：前者当前 `0` 个合格 pair，后者才留下 `ARB/CRV`、`ARB/LINK`、`LINK/CRV` 三组；
3. 当前快检更像是“存在少量 shock-compression pocket”，还不是已经证明 after-cost 可稳定迁移的 admission 级证据；
4. digest 里对 `ARB/CRV` 的结果显示，较稳的是先压缩一段 spread，而不是稳定 full mean reversion；这意味着真正决定策略成败的还会是 exit 定义与成本实现，不宜凭 repo audit + 单次 proxy 快检直接升 `P2`。

## 本轮改变系统认知的一句话
`Rank 273`：`whitelist peer-divergence × half-life-gated spread fade` 已确认是可独立成立的 peer-bucket relative-value raw alpha skeleton，但当前最大信息增益仍在 clean-room 复现 `96 vs 672` lookback 修正后，bucket 内 pair search / signal density / after-cost pocket 是否仍成立，因此先记 `keep_P1`，不直升 `P2`。

## 唯一 survivor follow-up 应该回答什么
下一步唯一合法 follow-up 不该再做泛泛 repo 复述，而应直接回答：
- 在固定 peer buckets 下，`96 vs 672`（15m）与对应 `5m` lookback 修正后，合格 pair 数、去重后 signal episode 数、after-cost PnL 是否仍保留；
- `full reversion` vs `first compression` 两种 exit 口径里，哪一种才是诚实的可迁移 pocket；
- 若结果只剩极少数 pair（例如单一 `ARB/CRV`）和极薄 pocket，则 survivor 用尽后应回 background/P0，而不是拖入 `P2`。

## runtime 写回要点
- 正式分配 `Rank 273`
- Fresh intake slot 更新为该对象并写明首判 `keep_P1`
- Surviving candidate slot 更新为 `Rank 273`，保留唯一一次 follow-up 预算
- cycle_plan 第 1 项写成 `done`
