# 2026-04-18 04:02 UTC bot2 strategy review

## Inputs checked
- Policy: `docs/BOT2_BOT3_POLICY.md`
- State: `docs/BOT2_BOT3_STATE.md`
- Repo status: `git status --short`（仍主要是历史遗留未跟踪临时文件；本轮不把这些噪音当排班依据）
- Recent optimization loop:
  - `2026-04-18_0322_auctionprofile_freshintake_background_p0_barprofile_proxy.md`
  - `2026-04-18_0309_vwapemabb_freshintake_background_p0_portability_cost.md`
  - `2026-04-18_0255_deribit_polymarket_terminalprob_freshintake_background_p0_halflife.md`
  - `2026-04-18_0240_queuedepletion_freshintake_background_p0_cost_after_fill.md`
  - `2026-04-18_0225_auctionprofile_freshintake_background_p0_barprofile_proxy.md`
  - `2026-04-18_0158_btcbetaneutral_residual_reversal_freshintake_background_p0_frictionthreshold.md`
- Recent strategy review:
  - `2026-04-18_0242_strategy-review.md`
  - `2026-04-18_0150_strategy-review.md`
  - `2026-04-18_0101_strategy-review.md`
  - `2026-04-18_0013_strategy-review.md`
- Additional fresh-intake sources consulted for this rewrite:
  - `research/quant_digests/2026-04-18_0356_rl-pair-dynamic-scaling-statarb-alpha.md`
  - `research/quant_digests/2026-04-17_2024_multicoin-rsi-panicfade-shell.md`
  - `research/quant_digests/2026-04-17_1936_deribit-termskew-riskreversal-alpha.md`
  - `research/quant_digests/2026-04-17_1835_microprice-imbalance-consensus-mm-shell.md`

## 四个问题（本轮结论）
1. `Paper launch queue` 是否非空？
   - 结论：**否**。
   - `current_target = none`；`connected_runner_live` 虽非空，但这些对象都已经完成 dedicated runner + scheduler + first verified run，不属于待接线 queue。

2. 本轮 `fresh intake` 是什么？
   - 结论：**`research/quant_digests/2026-04-18_0356_rl-pair-dynamic-scaling-statarb-alpha.md`。**
   - 原因：前一轮 cycle_plan 里的前排 intake 已被 bot3 继续消费：`Deribit terminal probability vs Polymarket binary price`、`trend-up VWAP reclaim × lower-band pierce`、`auction-profile value-area re-entry × LVN traverse shell` 都已 first-verdict 收口 `background/P0`，因此当前 fresh intake 已自然切到最新的 `RL pair dynamic scaling / excursion-aware sizing`。

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
   - 结论：**不值得。**
   - 上一条 fresh intake 是 `trend-up VWAP reclaim × lower-band pierce`；最新 first verdict 已经够清楚：`BTC/ETH/SOL 5m` portability 下它暴露为 asset/side-selective 薄 pocket，统一 `4bps` 后 `BTC` 双边已转负、`8bps` 后只剩 `SOL short` 的薄余量，不该占用 survivor 那唯一一次 follow-up。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
   - 结论：**不存在。**
   - `Active P2 = none`；最近一次 active P2 出口仍是 `Rank 417` 的 `one-time P2->P1 re-scope`，但它已经退出 active 槽位，不构成本轮待裁决对象。

## Rank 合规检查
- 当前前排对象（`Paper launch queue / Surviving candidate / Active P2 / Fresh intake`）不存在“已达 `keep_P1 / P2 / P3` 但无正式 Rank”的违规。
- 无需分配新 `Rank`。

## 关键判断
- 当前没有待接线 `P3`，没有 `Active P2`，也没有 survivor 需要收口；所以本轮必须继续沿 fresh-intake 主线排班。
- 由于前一版 cycle_plan 已被 bot3 基本消费完，bot2 现在要做的不是重复抄旧计划，而是把 runtime truth 重写到新的前排对象上。
- 新 front slot 先给 `RL pair dynamic scaling / excursion-aware sizing`，理由很直接：它是最新 digest，base alpha 仍是清楚的 `pairs/stat-arb spread mean reversion`，而 bot7 明确把真正值得测的旁支压缩到了一个单一问题——**spread 偏得更深时，值得不值得加仓**。这很适合做 first verdict，因为 blocker 也集中：gross 改善是否在统一双腿成本后仍足以支撑前排。
- 第二顺位我放 `major-coin oversold panic fade × hard stop / fixed TP`。它和最近过密的 pairs / options / microstructure 题材不同，能补单资产 plain MR baseline；但 repo 的 `+6% TP` 对短周期太不 desk，因此 first verdict 应只围绕 `exit realism / major-only admission` 做诚实裁决。
- 第三顺位放 `near-vs-far risk-reversal term-skew spread`。这条 options RV 题材足够 distinct，也有完整四腿壳；但当前 live 证据还主要停在 snapshot 级正 edge，决定性 blocker 很集中：**多腿可成交性 + half-life**。
- 第四顺位放 `microprice deviation × top-book imbalance consensus`。这条线的 base alpha 很清楚，但当前 strongest mid-drift 仍只是 `~0.5–1.4bps` 的 pre-cost 量级；因此它适合放在 conditional intake 的后位，由 bot3 只补一个 `maker fill / queue-latency` blocker 来收口。
- 我刻意没有把任何 background pool 里的旧对象自动拉回前排，也没有把 `Background pool guard` 单独排成 cycle_plan 小点。

## cycle_plan rewrite（本轮执行）
已重写 `docs/BOT2_BOT3_STATE.md`，使当前轮保持 4 个合法 pending 小点：

1. `2026-04-18_0356_rl-pair-dynamic-scaling-statarb-alpha.md`
2. `2026-04-17_2024_multicoin-rsi-panicfade-shell.md`
3. `2026-04-17_1936_deribit-termskew-riskreversal-alpha.md`
4. `2026-04-17_1835_microprice-imbalance-consensus-mm-shell.md`

并同步更新：
- `Fresh intake slot.current_target = research/quant_digests/2026-04-18_0356_rl-pair-dynamic-scaling-statarb-alpha.md`
- `Fresh intake slot.latest_result` 追加了 `trend-up VWAP reclaim × lower-band pierce -> background/P0`
- `Background pool.latest_parked` / `latest_parked_record` 追加了 `vwap-ema-bb` 的 parked 结论

每项都严格只保留：
- `target`
- `action`
- `success_criterion`
- `result = none`
- `status = pending`

## P2 -> P3 兜底裁判检查
- 本轮无 `Active P2`。
- 因此不存在“desk review 已清楚表明对象足够值得进入 paper trade / paper launch，但 bot3 尚未升级”的兜底升 `P3` 场景。
- 本轮无需把任何对象直接写入 `P3 / Paper launch queue` 或 handoff 路径。

## Files changed
- `docs/BOT2_BOT3_STATE.md`
- `research/strategy_review/2026-04-18_0402_strategy-review.md`

## Tail steps
- homepage 刷新：按要求单独执行 `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`；若失败，按规则记为**非阻断尾部失败**，不回滚本轮 state / log / cycle_plan。
- 邮件通知：无论 publish 是否成功，均继续单独执行 `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot2-review] 切到 RL pairs sizing intake 并补三条新 front" --body-file /root/clawd/jerry/momentum/research/strategy_review/2026-04-18_0402_strategy-review.md`。
