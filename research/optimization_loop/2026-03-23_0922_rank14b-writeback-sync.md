# 2026-03-23 09:22 UTC · Rank 14b / family-level decisive cut writeback sync

## 本轮按顶板顺序执行

### Run 1 · TRADING DESK BOARD
- 已读取 `docs/TODO.md` 顶部 `TRADING DESK BOARD`
- `Paper / 待开启自动运行 = empty`
- 未见顶板定义的真实 interrupt
- 因此本轮路径 = **Scout**

### Run 2 · 主点
- 认领 `Next 3 bot3 runs / Run 1` 指向的 `Rank 14b`
- 但该条要求的最小实验动作（family-level decisive cut）已在上一轮完成，当前最有杠杆、可验证、可交付的小步是：**把这条结论正式写回顶板与 reader-facing 页面，避免 bot3 继续在同一 P1 上空转**

### Run 3 · 紧邻子点
- 只推进 1 个紧邻子点：把 `Rank 14b` 的 family-level 结果落成一个可读页面
- 不新开 `Rank 125 / 112 / 111` 的实验
- 不再给 `Rank 14b` 加新阈值/新 setup

## 本轮实际动作
1. 新增 reader-facing 页面：
   - `reports/site/reading/repo_scout/rank14b_family_level_breadth_cut.html`
2. 更新顶板 authoritative 口径：
   - `Active Scout 排序` 中 `Rank 14b` 改为 `P1 / keep_P1 / family-level evidence strengthened / budget used / not default primary`
   - `Next 3 bot3 runs / Run 1` 改为：`Rank 14b` 已完成 family-level decisive cut，下一轮默认应切到 `Rank 125 / 112 / 111` 中最有杠杆的一条
   - `最近关键 evidence` 新增 `2026-03-23 09:22 UTC` 的 `Rank 14b` writeback 记录

## 核心结论（本轮不重跑，只做 authoritative sync）
- `Rank 14b` 已经摆脱“只是 raw_trigger 偶然 pocket”的怀疑：
  - `raw_trigger @ 6bps`: `-16.36 -> +3.80 bps`
  - `close_confirmed_n1 @ 6bps`: `-22.70 -> +4.44 bps`
  - `close_confirmed_n2 @ 6bps`: `-30.62 -> +7.31 bps`
  - `close_confirmed_n3 @ 6bps`: `-30.56 -> +8.51 bps`
- 但它仍不够 shared deployable：
  - `trade_retention` 仍只有 `57%~60%`
  - `ETH` 在所有相邻变体里依旧是持续拖累
  - `15bps/side` 全部仍为负；`10bps/side` 只有 `close_confirmed_n3` 勉强 `+0.50 bps`
- 因此 authoritative 口径固定为：
  - **`Rank 14b = P1 / keep_P1 / family-level evidence strengthened / not default primary`**

## 轻量 scorecard
- `usefulness = medium_to_high`
- `time_stability = weak`
- `cross_asset_stability = weak`
- `cost_trade_stability = weak_to_medium`
- `deployability = low`
- `recommended_action = keep_P1`
- `why_now = 防止 bot3 继续在已完成 decisive cut 的 P1 候选上打转，并把结论同步到读者入口与顶板`
- `main_weakness = ETH drag + retention still only 57~60% + high-cost instability`

## reader-facing 落点
- 页面：`reports/site/reading/repo_scout/rank14b_family_level_breadth_cut.html`
- 顶板：`docs/TODO.md`

## 本轮交付
- 日志：`research/optimization_loop/2026-03-23_0922_rank14b-writeback-sync.md`
- 页面：`reports/site/reading/repo_scout/rank14b_family_level_breadth_cut.html`
- 顶板 authoritative sync：`docs/TODO.md`
