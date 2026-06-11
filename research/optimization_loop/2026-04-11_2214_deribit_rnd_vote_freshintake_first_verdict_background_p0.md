# 2026-04-11 22:14 UTC — Deribit RND unanimous vote × BTC direction（fresh intake）first verdict

## 执行小点
- target: `research/quant_digests/2026-04-11_1826_deribit-rnd-vote-btc-direction-alpha.md`
- action: 执行 fresh intake first-verdict，检查 nearest-expiry RND vote 在 lag1 对齐与成本后是否保留可迁移净边际。

## 本轮最小 honesty / execution realism 子检查
我只做了一个最便宜、会改变结论的检查：**可审计 lag1 对齐是否已具备**。

- 现场拉取 Deribit `public/get_book_summary_by_currency?currency=BTC&kind=option`，确认链路确实可取到每个期权的 `creation_timestamp` 与 `mark_iv`。
- 但当前对象只有单次快照类 artifact（`deribit_rnd_signal_probe_2026-04-11.csv`），没有连续、可回放的 minute 级 signal→perp 对齐账本；因此无法在本轮给出“bar-close 后 lag1 入场”与“4/8/12bps 成本后净边际”是否仍成立的可审计答案。

## first verdict
- decision: `background / P0`
- decisive blocker（唯一）: **缺少可回放的 lag1 对齐执行账本，当前证据无法排除同帧取数/对齐导致的信号泄漏（honesty blocker）**。

## 结论影响
- 该对象保留为 options-side 外部特征想法，但不进入 survivor/P1。
- 不分配 Rank，不占用 P1/P2/P3 前排槽位。

## runtime 回写
- `cycle_plan` 第 1 项：`done`
- `Fresh intake slot`：更新为该对象 first verdict=`background/P0`，并把当前目标切换到下一待执行 intake。
- `Background pool.latest_parked`：记录本对象本轮收口结果。