# 2026-04-18 07:21 UTC bot2 strategy review

## Inputs checked
- Policy: `docs/BOT2_BOT3_POLICY.md`
- State before rewrite: `docs/BOT2_BOT3_STATE.md`
- Repo status: `git status --short --branch`
- Recent optimization loop:
  - `2026-04-18_0710_hftpairs_zscore_freshintake_background_p0_cost_gate.md`
  - `2026-04-18_0630_rsi_breakout_freshintake_background_p0_shortcycle_transfer.md`
  - `2026-04-18_0556_microprice_consensus_freshintake_background_p0_makerfill_realism.md`
  - `2026-04-18_0543_deribit_termskew_freshintake_background_p0_snapshot_only.md`
  - `2026-04-18_0431_multicoin_rsi_panicfade_freshintake_background_p0_exitrealism.md`
  - `2026-04-18_0352_rlpair_dynamicscaling_freshintake_background_p0_costrealism.md`
- Recent strategy review:
  - `2026-04-18_0620_strategy-review.md`
  - `2026-04-18_0524_strategy-review.md`
  - `2026-04-18_0437_strategy-review.md`
  - `2026-04-18_0402_strategy-review.md`
- Current intake materials checked for this rewrite:
  - `research/quant_digests/2026-04-18_0558_session-orb-widthgate-shell.md`
  - `research/quant_digests/2026-04-18_0621_funding-4h-context-divergence-overlay.md`
  - `research/quant_digests/2026-04-18_0715_cvd-nonconfirm-extreme-fade-shell.md`
  - `research/quant_digests/2026-04-18_0508_partialmoment-tsmom-reversal-overlay.md`
  - `research/park_reframe/INDEX.md`

## Repo status note
- `git status --short --branch` 仍主要是 `/root/clawd` 工作区历史临时文件与资料文件未跟踪噪声；本轮不据此改 policy，也不把这些噪声当作排班依据。

## 四个问题（本轮只回答这四个）
1. `Paper launch queue` 是否非空？
   - 结论：**否**。
   - `current_target = none`；`connected_runner_live` 中列出的对象都已是接线完成对象，没有待补 dedicated runner / scheduler / first verified run 的 queue 前排。

2. 本轮 `fresh intake` 是什么？
   - 结论：**`research/quant_digests/2026-04-18_0558_session-orb-widthgate-shell.md`**。
   - 理由：上一轮队首两条 pending intake（`trend-up RSI breakout × ATR trail`、`half-life bounded pairs z-score fade`）已经分别在 `2026-04-18_0630...` 与 `2026-04-18_0710...` 收口为 `background/P0`；当前无 survivor / active P2 / P3 wiring，因此队首自然切到 ORB width-gate。

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
   - 结论：**不值得。**
   - 上一条 fresh intake 是 `half-life bounded pairs z-score fade`。最近 optimization loop 已把决定性 blocker 说清：aggregate gross 仅 `+4.24bps/trade`，统一双腿 `8/12/20bps` 后整体转负，且 repo 还有 `no-profitable-params` 默认兜底 admission 缺口；这已经足够 first-verdict 直接关掉，不该再占 survivor 槽位。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
   - 结论：**不存在。**
   - `Active P2 = none`。最近一次 active P2 仍是 `Rank 417` 的出口决策，但它已在 `2026-04-16_0309_rank417_p2_exit_rescope_to_p1_noeth_pairs.md` 完成 `one-time P2->P1 re-scope` 并退出 active 槽位，不构成本轮待裁决对象。

## Rank 合规检查
- 当前前排对象不存在“已达 `keep_P1 / P2 / P3` 但仍无正式 Rank”的违规。
- 无需补新 Rank。

## 排班判断
- 当前没有待接线 `P3`，没有 `Active P2`，也没有 survivor；按 policy 必须继续沿 fresh-intake 主线重写本轮 `cycle_plan`。
- 不允许自动把 background pool 旧对象拉回前排；本轮也没有显式排 `Background pool guard`。
- 前两项仍然必须是会造成真实推进的动作，因此安排为：
  1. `session opening-range breakout × box-width gate`：当前正式队首 fresh intake。
  2. `4H directional move × funding disagreement`：最新 digest 已把 `align` continuation 读法直接否掉，并把 candidate 收敛到 `BTC/ETH` anti-chase veto；值得一轮明确 first verdict，而不是继续留成抽象 overlay 口号。
- 在前排链条为空的前提下，用剩余预算补两条新的具体 intake：
  3. `price extreme × non-confirming CVD`：最新 repo/digest，且 first verdict 已经明确区分出 `30m strong divergence` 与裸 `15m` 主信号的差别，适合做一次最小 admission。
  4. `time-series momentum × partial-moment reversal veto`：虽然更像 overlay，但它至少有完整论文规则与轻量 portability probe；应尽快回答它在 crypto 下是否只配 `veto-only`，还是连队首研究池都不该占。
- 本轮没有 `Active P2` 达到 bot2 必须兜底直升 `P3` 的门槛，也没有 queue 内待补 wiring 的 `P3` 对象；因此不存在需要直接推进 `P3 / Paper launch queue` 的对象。

## cycle_plan rewrite（已写回 state）
1. `research/quant_digests/2026-04-18_0558_session-orb-widthgate-shell.md`
2. `research/quant_digests/2026-04-18_0621_funding-4h-context-divergence-overlay.md`
3. `research/quant_digests/2026-04-18_0715_cvd-nonconfirm-extreme-fade-shell.md`
4. `research/quant_digests/2026-04-18_0508_partialmoment-tsmom-reversal-overlay.md`

并同步修正：
- `Fresh intake slot.current_target = research/quant_digests/2026-04-18_0558_session-orb-widthgate-shell.md`
- `Fresh intake slot.source_record = research/quant_digests/2026-04-18_0558_session-orb-widthgate-shell.md`
- 保持最近已完成 writeback 仍是 `half-life bounded pairs z-score fade -> background/P0`

## P2 -> P3 兜底裁判检查
- 本轮没有 `Active P2`，因此不存在 bot2 必须兜底直升 `P3 / Paper launch queue` 的对象。
- `Paper launch queue.current_target = none`，也不存在 queue 内待补 runner / scheduler / first verified run 的接线对象。
- 因此本轮**无需**直接把任何对象写入 `P3 / Paper launch queue` 或 handoff 路径。

## Files changed
- `docs/BOT2_BOT3_STATE.md`
- `research/strategy_review/2026-04-18_0721_strategy-review.md`

## Tail steps
- homepage 刷新：单独执行 `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`；若失败，按 policy 记为**非阻断尾部失败**。
- 邮件通知：无论 publish 成败，继续单独执行 `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot2-review] 队首切到 ORB，补 CVD 与 partial-moment intake" --body-file /root/clawd/jerry/momentum/research/strategy_review/2026-04-18_0721_strategy-review.md`。
