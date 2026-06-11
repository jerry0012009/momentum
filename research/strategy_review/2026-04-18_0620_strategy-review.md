# 2026-04-18 06:20 UTC bot2 strategy review

## Inputs checked
- Policy: `docs/BOT2_BOT3_POLICY.md`
- State before rewrite: `docs/BOT2_BOT3_STATE.md`
- Repo status: `git status --short --branch`
- Recent optimization loop:
  - `2026-04-18_0556_microprice_consensus_freshintake_background_p0_makerfill_realism.md`
  - `2026-04-18_0543_deribit_termskew_freshintake_background_p0_snapshot_only.md`
  - `2026-04-18_0431_multicoin_rsi_panicfade_freshintake_background_p0_exitrealism.md`
  - `2026-04-18_0352_rlpair_dynamicscaling_freshintake_background_p0_costrealism.md`
  - `2026-04-18_0322_auctionprofile_freshintake_background_p0_barprofile_proxy.md`
  - `2026-04-18_0309_vwapemabb_freshintake_background_p0_portability_cost.md`
- Recent strategy review:
  - `2026-04-18_0524_strategy-review.md`
  - `2026-04-18_0437_strategy-review.md`
  - `2026-04-18_0402_strategy-review.md`
  - `2026-04-18_0242_strategy-review.md`
- Current intake materials checked for this rewrite:
  - `research/quant_digests/2026-04-18_0431_rsi-breakout-trend-shell.md`
  - `research/quant_digests/2026-04-17_1556_hftpairs-zscore-halflife-shell.md`
  - `research/quant_digests/2026-04-18_0558_session-orb-widthgate-shell.md`
  - `research/quant_digests/2026-04-18_0621_funding-4h-context-divergence-overlay.md`

## Repo status note
- `git status --short --branch` 仍主要是 `/root/clawd` 工作区历史临时文件与资料文件未跟踪噪声；本轮不据此改 policy，也不把这些噪声当作排班依据。

## 四个问题（本轮只回答这四个）
1. `Paper launch queue` 是否非空？
   - 结论：**否**。
   - `current_target = none`；`connected_runner_live` 里的对象都已经是已接线完成对象，没有待补 dedicated runner / scheduler / first verified run 的前排 `P3`。

2. 本轮 `fresh intake` 是什么？
   - 结论：**`research/quant_digests/2026-04-18_0431_rsi-breakout-trend-shell.md`。**
   - 理由：上一轮前两条 pending intake（`Deribit term-skew risk-reversal`、`microprice imbalance consensus`）都已在最近 optimization loop 中直接收口 `background/P0`；当前没有 survivor / active P2 / P3 wiring 占位，因此队首自然切到 `trend-up RSI breakout × ATR trail`。

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
   - 结论：**不值得。**
   - 上一条 fresh intake（`microprice deviation × top-book imbalance consensus`）的决定性 blocker 已足够直接：公开 probe 里 strongest 也只有 `~0.5–1.4bps` 的 pre-cost mid drift，而 maker fill / queue priority / cancel-delay realism 一旦补上就不再像可交易 pocket。这个结论已经是 first-verdict 级收口，不该再浪费 survivor 槽位。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
   - 结论：**不存在。**
   - `Active P2 = none`。最近一次 active P2 仍是 `Rank 417` 的出口决策，但它已经完成 `one-time P2->P1 re-scope` 并退出 active 槽位，不构成本轮待裁决对象。

## Rank 合规检查
- 当前前排对象不存在“已达 `keep_P1 / P2 / P3` 但仍无正式 Rank”的违规。
- 无需补新 Rank。

## 排班判断
- 当前没有待接线 `P3`，没有 `Active P2`，也没有 survivor；按 policy，必须继续沿 fresh-intake 主线重写本轮 `cycle_plan`。
- 不允许自动把 background pool 旧对象拉回前排；本轮也没有显式排 `Background pool guard`。
- 前两项继续保留为真实推进动作：
  1. `trend-up RSI breakout × ATR trail`：队首 pending intake，且 verdict 关键只剩单一 `short-cycle transfer / cost-realism` 轴。
  2. `half-life bounded pairs z-score fade`：pairs 家族最近已经很拥挤，这条若连 `8/12/20bps` 和 `no-profitable-params` admission 风险都过不去，就该直接收口，避免再写低杠杆重复。
- 在前排链条已经诚实收口的前提下，剩余预算补两个新的具体 intake：
  3. `session opening-range breakout × box-width gate`：这是最新一条更像 raw alpha 壳的 repo；plain ORB 明确为负，但 `US session + 宽 box` 有薄 pocket，值一次最小 first verdict。
  4. `4H directional move × funding disagreement`：虽然它更像 overlay，但最新 digest 已把可迁移口径收敛到 BTC/ETH 的 anti-chase / fade 方向；可作为新的具体 intake 对象，而不是抽象“继续看 overlay”。

## cycle_plan rewrite（已写回 state）
1. `2026-04-18_0431_rsi-breakout-trend-shell.md`
2. `2026-04-17_1556_hftpairs-zscore-halflife-shell.md`
3. `2026-04-18_0558_session-orb-widthgate-shell.md`
4. `2026-04-18_0621_funding-4h-context-divergence-overlay.md`

并同步修正：
- `Fresh intake slot.current_target = research/quant_digests/2026-04-18_0431_rsi-breakout-trend-shell.md`
- `Fresh intake slot.source_record = research/quant_digests/2026-04-18_0431_rsi-breakout-trend-shell.md`
- 保持最新已完成 writeback 仍是 `microprice imbalance consensus -> background/P0`

## P2 -> P3 兜底裁判检查
- 本轮没有 `Active P2`，因此不存在 bot2 必须兜底直升 `P3 / Paper launch queue` 的对象。
- `Paper launch queue.current_target = none`，也不存在 queue 中待补 runner / scheduler / first verified run 的接线对象。
- 因此本轮**无需**直接把任何对象写入 `P3 / Paper launch queue` 或 handoff 路径。

## Files changed
- `docs/BOT2_BOT3_STATE.md`
- `research/strategy_review/2026-04-18_0620_strategy-review.md`

## Tail steps
- homepage 刷新：单独执行 `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`；若失败，按 policy 记为**非阻断尾部失败**。
- 邮件通知：无论 publish 成败，继续单独执行 `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot2-review] 切到 RSI breakout intake，补 ORB 与 funding-divergence" --body-file /root/clawd/jerry/momentum/research/strategy_review/2026-04-18_0620_strategy-review.md`。
