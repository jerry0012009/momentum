# Strategy Review — 2026-04-06 05:14 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并复核：
- repo 状态：`git -C /root/clawd/jerry/momentum status --short`
- 最近 optimization：
  - `research/optimization_loop/2026-04-06_0509_rank347_adaptive_2sma_walkforward_first_verdict_keep_p1.md`
  - `research/optimization_loop/2026-04-06_0436_rank346_survivor_followup_fomc_followthrough_background_p0.md`
  - `research/optimization_loop/2026-04-06_0337_rank346_macro_impulse_sentiment_gate_first_verdict_keep_p1.md`
  - `research/optimization_loop/2026-04-06_0016_rank342_p3_launch_wiring_connected_runner_live.md`
- 最近 strategy review：
  - `research/strategy_review/2026-04-06_0409_strategy-review.md`
  - `research/strategy_review/2026-04-06_0300_strategy-review.md`
  - `research/strategy_review/2026-04-06_0155_strategy-review.md`
- 最近 digest / intake 候选：
  - `research/quant_digests/2026-04-06_0458_basis-relaxation-regimesized-funding-carry-alpha.md`
  - `research/quant_digests/2026-04-06_0424_funding-basis-persistence-deltaneutral-alpha.md`
  - `research/quant_digests/2026-04-05_2358_sar-perp-liquidity-veto-overlay.md`

## 只回答 4 个问题

### 1) `Paper launch queue` 是否非空？
- **否，当前为空。**
- `Paper launch queue.current_target = none`。
- `Rank 342` 已在 `research/optimization_loop/2026-04-06_0016_rank342_p3_launch_wiring_connected_runner_live.md` 完成 dedicated runner、scheduler 与首跑验证，并正式写回 `connected_runner_live`。
- 因此当前不存在 bot2 需要兜底继续推进的 `P3` 接线对象。

### 2) 本轮 `fresh intake` 是什么？
- **本轮 fresh intake 切到** `research/quant_digests/2026-04-06_0458_basis-relaxation-regimesized-funding-carry-alpha.md`。
- 原因：
  1. `Rank 347` 已完成上一条 fresh intake 的 first verdict，并已依法进入唯一 `Surviving candidate slot`；
  2. 当前没有 `P3` 与 `Active P2` 堵在前面；
  3. 最新且尚未首判的新对象里，`basis relaxation × regime-sized funding carry` 是最靠前、且主语清楚的 funding/basis raw alpha；
  4. 旧的 `SaR overlay` 仍可作为后续具体 intake，但不应压过更近的新 digest。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- **值得，而且它就是本轮前排第一优先级。**
- 上一条 fresh intake 是 `Rank 347 / adaptive 2-SMA walk-forward perp trend`。
- `research/optimization_loop/2026-04-06_0509_rank347_adaptive_2sma_walkforward_first_verdict_keep_p1.md` 已经明确：
  - 它不是旧 `AdaptiveTrend` 组合包装重复件；
  - 当前最关键缺口只剩 `BTC/ETH × 5m/15m × fixed-vs-walk-forward × slow-window` 的 after-cost 可迁移性；
  - 这正好符合 survivor 那唯一一次便宜而决定性的 follow-up 范围。
- 因此答案是：**值得，且必须先把这次 follow-up 用掉并给出 `promote_P2` 或 `drop_to_background` 的终局结论。**

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- **不存在。**
- `Active P2 slot.current_target = none`。
- 最近明确的 `Active P2` 仍是 `Rank 342`，但它已经完成 `P2 -> P3 -> connected_runner_live` 的完整收口。
- 因此当前没有需要 bot2 兜底裁判 `P3 / P1 / P0` 出口方向的滞留 `P2` 对象。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Surviving candidate slot.current_target = Rank 347`
- `Active P2 slot.current_target = none`
- 当前所有前排对象均已带 rank；不存在达到 `keep_P1 / P2 / P3` 但无 rank 的违规状态，因此本轮无需补发 rank。

## P2 -> P3 兜底裁判检查
- 本轮没有 `Active P2`。
- desk review 未发现任何“已经足够进入 paper trade、但 bot3 尚未升级”的漏判对象。
- 因此本轮不需要执行 `P2 -> P3` 强制写回；当前重点是先收口 `Rank 347` 的 survivor follow-up，再把 fresh intake 切到最新 funding/basis 线。

## cycle_plan 重写结果
按 policy 默认顺序：`P3 handoff > P2 admission/promote/park > P1 唯一一次诚实检查 > fresh intake > P0`。

当前合法前排链条为：
- `P3`: none
- `P2`: none
- `P1 survivor`: `Rank 347`

因此本轮排班必须先收口 `Rank 347`，然后才轮到新的 fresh intake。已将 `docs/BOT2_BOT3_STATE.md` 重写为：
1. `Rank 347 / adaptive 2-SMA walk-forward perp trend` survivor follow-up
2. `research/quant_digests/2026-04-06_0458_basis-relaxation-regimesized-funding-carry-alpha.md`
3. `research/quant_digests/2026-04-06_0424_funding-basis-persistence-deltaneutral-alpha.md`
4. `research/quant_digests/2026-04-05_2358_sar-perp-liquidity-veto-overlay.md`

### 为什么这么排
- `Rank 347` 是当前唯一 survivor，依法享有前排锁定权；在它那唯一一次 follow-up 收口前，不能让新的 `keep_P1` 候选覆盖 survivor 槽位。
- `basis relaxation × regime-sized funding carry` 是最新、主语清楚、且与现有前排不冲突的 funding/basis raw alpha，因此接管当前 fresh intake 槽位。
- `funding/basis dislocation persistence × delta-neutral carry` 同样新且具体，但主语与第 2 项不同，适合作为下一条明确 intake。
- `SaR overlay` 仍然值得保留为 conditional intake，但顺位应落后于最新两条 funding/basis 候选。

## 对 repo 状态的最小备注
- repo 中存在若干未跟踪临时文件与历史产物；按 policy，它们只构成环境噪音，不构成 reopen 旧候选或改变前排顺序的理由。

## 本轮一句话
当前没有 `P3`、也没有 `Active P2`；唯一必须先做的是把 `Rank 347` 的 survivor follow-up 诚实收口，然后把 fresh intake 切到最新的 `basis relaxation × regime-sized funding carry`，再依次处理 `funding dislocation persistence` 与 `SaR overlay`。
## 执行备注
- 中文邮件摘要已发送成功。
- `publish_homepage_index.sh` 在本轮 cron 运行环境中卡在 `sudo` 发布步骤；当前会话无 elevated 能力，因此首页发布到 `/var/www/momentum-report/index.html` 未能在本轮完成。
