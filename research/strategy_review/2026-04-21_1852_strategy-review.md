# 2026-04-21 18:52 UTC strategy review

## Inputs checked
- Policy: `docs/BOT2_BOT3_POLICY.md`
- State: `docs/BOT2_BOT3_STATE.md`
- Repo status: `git -C /root/clawd/jerry/momentum status --short`（仍有大量历史 `??` 未跟踪文件；本轮按约束只更新 `BOT2_BOT3_STATE.md` 与本日志）
- Recent optimization evidence:
  - `research/optimization_loop/2026-04-21_1830_connorsrsi_freshintake_background_p0.md`
  - `research/optimization_loop/2026-04-21_1623_rank432_survivor_followup_background_p0_overlap_with_rank431.md`
  - `research/optimization_loop/2026-04-21_1408_rank431_p3_launch_wiring_connected_runner_live.md`
- Recent strategy review evidence:
  - `research/strategy_review/2026-04-21_1734_strategy-review.md`
  - `research/strategy_review/2026-04-21_1602_strategy-review.md`
- Recent fresh-intake sources reviewed:
  - `research/quant_digests/2026-04-21_1842_marex-microsignal-maker-skew-alpha.md`
  - `research/quant_digests/2026-04-21_1817_regimeaware-xsmomentum-router-overlay.md`
  - `research/quant_digests/2026-04-21_1548_ichimoku-tenkankijun-cross-feetrap.md`
  - `research/quant_digests/2026-04-21_1506_crosscrypto-peer-spillover-laggardcatchup-alpha.md`

## 仅回答 4 个问题
1. `Paper launch queue` 是否非空？
- 否。
- `current_target = none`，且最近 queue 对象 `Rank 431` 已在 `research/optimization_loop/2026-04-21_1408_rank431_p3_launch_wiring_connected_runner_live.md` 完成 runner + scheduler + first verified run，runtime 已写成 `connected_runner_live`。
- 当前没有待接线 P3 对象。

2. 本轮 `fresh intake` 是什么？
- 本轮 front fresh intake 改为：`research/quant_digests/2026-04-21_1842_marex-microsignal-maker-skew-alpha.md`。
- 其后按最近新 repo/paper/alpha evidence 顺延为：
  1. `research/quant_digests/2026-04-21_1817_regimeaware-xsmomentum-router-overlay.md`
  2. `research/quant_digests/2026-04-21_1548_ichimoku-tenkankijun-cross-feetrap.md`
  3. `research/quant_digests/2026-04-21_1506_crosscrypto-peer-spillover-laggardcatchup-alpha.md`
- `research/quant_digests/2026-04-21_1718_connorsrsi-tripleextreme-router-alpha.md` 已在 18:30 收口为 `background/P0`，不再占用 front slot。

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 不值得。
- 上一条 fresh intake 是 `ConnorsRSI triple-extreme overshoot × cross-back exit`，已在 `research/optimization_loop/2026-04-21_1830_connorsrsi_freshintake_background_p0.md` 直接收口为 `background/P0`。
- 决定性理由已经充分：`15m/5m` broad-pool gross 只有约 `+2.19bps / +0.94bps`，strongest-only router 也只有约 `+5.73bps / +1.74bps` gross，统一 `8bps` 成本后没有留下至少两个同向 after-cost symbol pocket。
- 因此它不是 `keep_P1`，也不获得 survivor 唯一 follow-up。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 当前不存在明确 `Active P2`。
- `Rank 431` 已完成 `promote_P3 -> connected_runner_live`；`Rank 432` 已用完 survivor 唯一 follow-up 并转入 `background/P0`；最新 ConnorsRSI fresh intake 也已转入 `background/P0`。
- 因此本轮不存在需要 bot2 兜底推进到 `P3 / P1 / P0` 出口的 `Active P2`。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Active P2 slot.current_target = none`
- `Surviving candidate slot.current_target = none`
- 当前前排不存在达到 `keep_P1 / P2 / P3` 但尚未分配正式 `Rank` 的对象。
- 本轮无需补新的整数 `Rank`。

## P2 -> P3 兜底判断
- 本轮没有发现任何仍停留在 `Active P2`、但已清楚达到 paper-trade / paper-launch 门槛 yet 尚未升级的对象。
- 因此无需执行新的 `P2 -> P3` 兜底改写。

## State rewrite
已按 policy 重写 `docs/BOT2_BOT3_STATE.md`：
- `Fresh intake slot.current_target` 更新为 `research/quant_digests/2026-04-21_1842_marex-microsignal-maker-skew-alpha.md`。
- 保持 `Paper launch queue = none`、`Surviving candidate = none`、`Active P2 = none`。
- 将当前轮 `cycle_plan` 重排为 4 条具体 fresh intake，顺序严格遵循“前排已收口后再切回 fresh intake”的规则：
  1. `2026-04-21_1842_marex-microsignal-maker-skew-alpha.md`
  2. `2026-04-21_1817_regimeaware-xsmomentum-router-overlay.md`
  3. `2026-04-21_1548_ichimoku-tenkankijun-cross-feetrap.md`
  4. `2026-04-21_1506_crosscrypto-peer-spillover-laggardcatchup-alpha.md`

## 本轮结论
- 当前没有待接线 `P3`、没有 survivor、也没有 `Active P2`。
- 因此前排预算诚实切回 fresh intake，而不是继续围绕已收口对象做重复动作。
- 新一轮默认从 `micro_signal fair-value shift × maker-first quote skew` 开始，再依次审 `regime-aware XSM router`、`Tenkan/Kijun cross`、`peer-return spillover`。

## Tail step status
- homepage publish：已按独立命令尝试 `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`；进程长时间无输出未完成，已按非阻断尾部失败处理，不回滚本轮 state/log。
- email notify：已按独立命令成功执行 `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot2-review] fresh intake 切到 maker-skew" --body-file /root/clawd/jerry/momentum/research/strategy_review/2026-04-21_1852_strategy-review.md`。
