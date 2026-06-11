# 2026-04-18 00:13 UTC bot2 strategy review

## Inputs checked
- Policy: `docs/BOT2_BOT3_POLICY.md`
- State: `docs/BOT2_BOT3_STATE.md`
- Repo status: `git status --short`（仍主要是历史遗留未跟踪临时文件；本轮不把这些噪音当排班依据）
- Recent optimization loop:
  - `2026-04-18_0007_stablecoin_microdepeg_freshintake_background_p0_feefloor_fillrealism.md`
  - `2026-04-17_2336_correlationranked_pairs_freshintake_background_p0_singlepair_reality.md`
  - `2026-04-17_2310_rank4_freshintake_background_p0_pairs_residual_absorbed.md`
  - `2026-04-17_2238_rank25c_conditional_freshintake_background_p0_consumed.md`
  - `2026-04-17_2213_rank14b_conditional_freshintake_background_p0_consumed.md`
  - `2026-04-17_2159_rank57_freshintake_background_p0_compression_residual_replay_closed.md`
  - `2026-04-17_2132_rank101_freshintake_background_p0_holdquality_note_absorbed.md`
  - `2026-04-17_2109_rank5_freshintake_background_p0_sameclock_residual_absorbed.md`
- Recent strategy review:
  - `2026-04-17_2246_strategy-review.md`
  - `2026-04-17_2141_strategy-review.md`
  - `2026-04-17_2101_strategy-review.md`
- Additional fresh-intake sources consulted for this rewrite:
  - `research/quant_digests/2026-04-17_2056_pathshape-downtrend-continuation-alpha.md`
  - `research/quant_digests/2026-04-17_2350_us-session-crosssectional-reversal-alpha.md`
  - `research/quant_digests/2026-04-17_2257_btcbetaneutral-residual-reversal-basket-alpha.md`
  - `research/quant_digests/2026-04-17_2114_deribit-polymarket-terminalprob-rv-alpha.md`

## 四个问题（本轮结论）
1. `Paper launch queue` 是否非空？
   - 结论：**否**。
   - `current_target = none`；`connected_runner_live` 虽非空，但这些对象都已完成 dedicated runner + scheduler + first verified run，不属于待接线 queue。

2. 本轮 `fresh intake` 是什么？
   - 结论：**`research/quant_digests/2026-04-17_2056_pathshape-downtrend-continuation-alpha.md`。**
   - 原因：`Rank 57 -> Rank 14b -> Rank 25c -> Rank 4 -> correlation-ranked pairs -> stablecoin micro-depeg` 已在最近 runtime 中按顺序诚实收口 `background/P0`，没有形成新的 survivor / P2；因此当前前排 fresh intake 已自然切到 `path-shape downside continuation`。

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
   - 结论：**不值得。**
   - 上一条 fresh intake 是 `stablecoin micro-depeg fade × 1 tick take-profit`；00:07 UTC 的 first verdict 已确认它在最小 `queue/fill + fee-floor realism` 下 `gross≈+0.886bps/笔`、`1.0bps` round-trip 即转负，而且 repo 还把非零 fee 视作停机条件，因此不拿 survivor 槽位。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
   - 结论：**不存在。**
   - `Active P2 = none`；最近一次 P2 出口仍是 `Rank 417` 的 `one-time P2->P1 re-scope`，但它已退出 active 槽位，不构成本轮待裁决对象。

## Rank 合规检查
- 当前前排对象（`Paper launch queue / Surviving candidate / Active P2 / Fresh intake`）不存在“已达 `keep_P1 / P2 / P3` 但无正式 Rank”的违规。
- 无需分配新 `Rank`。

## 关键判断
- 当前没有待接线 `P3`，没有 `Active P2`，也没有 survivor 需要收口；因此本轮必须继续沿 fresh-intake 主线排班。
- 当前 front slot 已经不是旧 residual，而是最新尚未消费的 `path-shape downside continuation`。按 policy，必须先把它做成 first verdict，不能绕过去插入更新鲜对象。
- `path-shape downside continuation` 的可疑点非常集中：当前可见正 pocket 主要落在 `SOL 15m short`，因此最小 blocker 应直接围绕 `cross-asset / cost / execution realism` 下它是不是单一样本窗 luck，而不是泛泛再补论文解释。
- 只有当 item1 诚实收口且仍无 survivor / P2 时，才能继续补新的 fresh intake；本轮尾部因此直接选最近、尚未被 runtime 消费的新 repo/paper/alpha reports，而**不**回看已经进过 `background/P0` 的对象。
- 在当前候选里，最值得顺排的后三个是：
  1. `2026-04-17_2350_us-session-crosssectional-reversal-alpha.md`
     - 理由：主题是清楚的时间窗横截面反转 raw alpha，但 repo 自证的致命点也很集中——impact，而不是手续费；适合做一次便宜而决定性的 first verdict。
  2. `2026-04-17_2257_btcbetaneutral-residual-reversal-basket-alpha.md`
     - 理由：base alpha 很干净，且 portability probe 已把问题压缩到单一核心：这条线在 `5m/15m` 只剩 `~2.4–2.9bps` break-even 摩擦空间，最适合做一次 friction-threshold honesty 裁决。
  3. `2026-04-17_2114_deribit-polymarket-terminalprob-rv-alpha.md`
     - 理由：是当前研究池里比较新的 cross-venue event-probability RV 素材，但 bundled evidence 还停留在极少交易样本；最该回答的是 edge half-life / fillability 是否真的能撑起 desk 节奏。
- 我刻意没有把 `correlation-ranked pairs`、`stablecoin micro-depeg` 或更早的 maker/imbalance 残余继续挂在后面，因为它们已经在最近 runtime 中明确 first-verdict 收口到 `background/P0`；再排一次就会违反“不得自动把 background pool 旧候选拉回前排”。

## cycle_plan rewrite（本轮执行）
已重写 `docs/BOT2_BOT3_STATE.md`，使当前轮保持 4 个合法 pending 小点：

1. `2026-04-17_2056_pathshape-downtrend-continuation-alpha.md`
2. `2026-04-17_2350_us-session-crosssectional-reversal-alpha.md`
3. `2026-04-17_2257_btcbetaneutral-residual-reversal-basket-alpha.md`
4. `2026-04-17_2114_deribit-polymarket-terminalprob-rv-alpha.md`

并同步把：
- `Fresh intake slot.status` 改为 `open_pending_first_verdict`
- `Fresh intake slot.current_target` / `source_record` 切到 `path-shape downside continuation`
- `Fresh intake slot.latest_result` 保留对 `stablecoin micro-depeg` 的收口结论，并明确前排已切到 `path-shape downside continuation`

每项都按 policy 只保留：
- `target`
- `action`
- `success_criterion`
- `result = none`
- `status = pending`

## 为什么本轮这样排
- policy 明确要求：只要存在合法前排动作，就不得把新的 intake 排到它前面；当前前排唯一合法动作就是 `path-shape downside continuation` 的 first verdict。
- 在 `P3 / P2 / P1` 都为空时，bot2 需要用剩余预算补新的 fresh intake；但这些对象必须是**具体、未被 runtime 消费、且不来自 background 自动 reopen** 的候选。
- `US-session cross-sectional reversal`、`BTC-beta-neutral residual reversal`、`Deribit×Polymarket terminal-probability RV` 都属于最近新 repo/paper/alpha report，且 blocker 都已被各自 digest 压缩到单一 honesty / execution realism 轴，适合作为本轮尾部 intake。
- 这样排比继续在已收口对象上 replay 更诚实，也更符合默认来源优先级“最近新的 strategy repo / paper / alpha report”。

## P2 -> P3 兜底裁判检查
- 本轮无 `Active P2`。
- 因此不存在“desk review 已清楚表明对象足够值得进入 paper trade / paper launch，但 bot3 尚未升级”的兜底升 `P3` 场景。
- 本轮无需把任何对象直接写入 `P3 / Paper launch queue` 或 handoff 路径。

## Files changed
- `docs/BOT2_BOT3_STATE.md`
- `research/strategy_review/2026-04-18_0013_strategy-review.md`

## Tail steps
- homepage 刷新：按要求单独执行 `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`；若因 `/var/www` 写入、preflight、或需要 elevated 而失败，按规则记为**非阻断尾部失败**，不回滚本轮 review / state rewrite / log。
- 邮件通知：无论 publish 是否成功，均继续单独执行 `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot2-review] pathshape 前排接棒并切入三条新 intake" --body-file /root/clawd/jerry/momentum/research/strategy_review/2026-04-18_0013_strategy-review.md`。
