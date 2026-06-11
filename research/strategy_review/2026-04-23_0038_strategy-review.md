# 2026-04-23 00:38 UTC — bot2 strategy review

Cron: `[cron:a3e89b2e-958f-4ad3-b625-c280a257b68a bot2-strategy-review-40m]`

## Inputs checked
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`
- `git status --short`
- recent `research/optimization_loop/`
- recent `research/strategy_review/`
- recent repo-side fresh candidates / park-reframe evidence as needed

## 只回答 4 个问题
1. **Paper launch queue 是否非空？**
   - 是，非空。
   - 当前 queue 里已有多条 `connected_runner_live`，最新明确收口的是 `Rank 434 / newlisting early-short bubble fade`，已完成 runner + scheduler + first verified run，不需要 bot2 再把它伪装成开放式研究。

2. **本轮 fresh intake 是什么？**
   - `research/quant_digests/2026-04-22_0958_perp-perp-funding-diff-zfade-shell.md`
   - 也就是 `cross-venue perp-perp funding spread z-score fade × child execution`。
   - 原因：当前 `P3 / P2 / survivor` 均已收口为空槽，上一条 fresh 已刚刚收口到 `background/P0`，而这条是仍未被消费、时间上靠前、且语义上仍是具体 raw alpha 壳的新 intake。

3. **上一条 fresh intake 是否值得那唯一一次 follow-up？**
   - 不值得。
   - 上一条 fresh intake 是 `rolling-OLS residual z-score fade × cost-aware sizing`，最新 first verdict 已诚实收口 `background/P0`：`15m` 只剩 `5` 笔且 `timeout=100%`，`5m` 虽有 `43` 笔但 `median gross < 0`、`timeout≈97.7%`，没有证明自然回中枢质量足以覆盖最小双腿成本；同时相对已 live `Rank 424 / 431` 没有拿出独立新增的 pairs shell 价值，所以**不配 survivor 唯一 follow-up**。

4. **当前是否存在明确 Active P2？若有，它离 `P3 / P1 / P0` 中哪个出口最近？**
   - 当前不存在明确 `Active P2`。
   - `Rank 434` 已由 bot2 在上一轮 review 兜底推进到 `P3`，且 launch wiring 已完成；因此当前 `Active P2 slot = none`，不存在再判断“离哪个出口最近”的对象。

## 本轮 state rewrite 决定
### 1) 不补新 rank
- 当前前排对象里没有无 rank 的 `Surviving candidate / Active P2 / Paper launch queue` 对象。
- 因此本轮不需要分配新整数 `Rank`。

### 2) 不把旧 park-reframe 候选硬拉回前排
- 旧 `Rank 74` 与 `Rank 89` 虽曾在早期 park-reframe 中被写成 `soft_reframe_candidate`，但后续更近的 park-reframe 记录已分别把它们收紧为：
  - `Rank 74`：`2026-04-18_0403_rank74-park-reframe.md` → `keep_park`
  - `Rank 89`：`2026-04-17_1810_rank89_freshintake_background_p0_failurefamily_overlap.md` + 原 park-reframe 语义已显示 distinctness 不足
- 按 policy，bot2 不得把 background / consumed residual 自动拉回前排，因此本轮不再沿用旧 cycle plan 里那两个 stale pending 项。

### 3) 重写 current cycle_plan
本轮前排链条已诚实收口，因此改为 3 个具体 fresh intake：
1. `2026-04-22_0958_perp-perp-funding-diff-zfade-shell.md`
2. `2026-04-22_0429_us-close-midcap-reversal-alpha.md`
3. `2026-04-22_0353_deribit-okx-option-quote-gap-shell.md`

重排逻辑：
- 当前无 `P3 wiring` 未完成对象；
- 当前无 `Active P2`；
- 当前无合法 survivor follow-up；
- 因此前排预算全部切回**仍未被消费、且对象具体**的新 fresh intake。

## 已写回 `BOT2_BOT3_STATE.md` 的要点
- `Fresh intake slot.current_target` 改为 `research/quant_digests/2026-04-22_0958_perp-perp-funding-diff-zfade-shell.md`
- `Fresh intake slot.source_record` 同步改为该文件
- `Fresh intake slot.latest_result` 保留上一条 `rolling-OLS residual z-score fade × cost-aware sizing` 收口 `background/P0` 的结论，但把“前排自然切到下一条 pending”更新为 **仍未被消费的 fresh intake `perp-perp funding spread z-score fade × child execution`**
- 删除旧 cycle plan 中对 `Rank 74 / Rank 89` 的 stale pending 排班，改为 3 条具体 fresh intake pending 项

## 尾部说明
- publish homepage：best-effort，失败不回滚本轮 review/state/log
- email：单独执行；若失败，仅记为通知失败，不回滚本轮 review/state/log
