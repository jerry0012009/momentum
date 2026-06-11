# 2026-04-18 01:01 UTC bot2 strategy review

## Inputs checked
- Policy: `docs/BOT2_BOT3_POLICY.md`
- State: `docs/BOT2_BOT3_STATE.md`
- Repo status: `git status --short --branch`（仍主要是历史遗留未跟踪临时文件；本轮不把这些噪音当排班依据）
- Recent optimization loop:
  - `2026-04-18_0054_pathshape_downtrend_freshintake_background_p0_concentration.md`
  - `2026-04-18_0007_stablecoin_microdepeg_freshintake_background_p0_feefloor_fillrealism.md`
  - `2026-04-17_2336_correlationranked_pairs_freshintake_background_p0_singlepair_reality.md`
  - `2026-04-17_2310_rank4_freshintake_background_p0_pairs_residual_absorbed.md`
  - `2026-04-17_2238_rank25c_conditional_freshintake_background_p0_consumed.md`
  - `2026-04-17_2213_rank14b_conditional_freshintake_background_p0_consumed.md`
  - `2026-04-17_2159_rank57_freshintake_background_p0_compression_residual_replay_closed.md`
  - `2026-04-17_2132_rank101_freshintake_background_p0_holdquality_note_absorbed.md`
- Recent strategy review:
  - `2026-04-18_0013_strategy-review.md`
  - `2026-04-17_2246_strategy-review.md`
  - `2026-04-17_2141_strategy-review.md`
  - `2026-04-17_2101_strategy-review.md`
- Additional fresh-intake sources consulted for this rewrite:
  - `research/quant_digests/2026-04-17_2350_us-session-crosssectional-reversal-alpha.md`
  - `research/quant_digests/2026-04-17_2257_btcbetaneutral-residual-reversal-basket-alpha.md`
  - `research/quant_digests/2026-04-18_0049_auction-profile-poc-lvn-shell.md`
  - `research/quant_digests/2026-04-17_2114_deribit-polymarket-terminalprob-rv-alpha.md`

## 四个问题（本轮结论）
1. `Paper launch queue` 是否非空？
   - 结论：**否**。
   - `current_target = none`；`connected_runner_live` 虽非空，但这些对象都已完成 dedicated runner + scheduler + first verified run，不属于待接线 queue。

2. 本轮 `fresh intake` 是什么？
   - 结论：**`research/quant_digests/2026-04-17_2350_us-session-crosssectional-reversal-alpha.md`。**
   - 原因：`path-shape downside continuation` 已在 `2026-04-18_0054` 被 first verdict 诚实收口到 `background/P0`，因此前排 fresh intake 顺位自然切到 `US-session cross-sectional intraday reversal`。

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
   - 结论：**不值得。**
   - 上一条 fresh intake 是 `path-shape downside continuation`；最新收口结论已经很清楚：after-cost 可见价值几乎完全依赖单一 `SOL 15m short` pocket（`net6=+1.43bps/笔`），但同形状 gate 在 `BTC/ETH/BNB 15m short` 全部为负，且一抬到 `8bps` 即转负、按月份与顺序分段也不稳，所以不该占用 survivor 那唯一一次 follow-up。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
   - 结论：**不存在。**
   - `Active P2 = none`；最近一次 active P2 出口仍是 `Rank 417` 的 `one-time P2->P1 re-scope`，但它已经退出 active 槽位，不构成本轮待裁决对象。

## Rank 合规检查
- 当前前排对象（`Paper launch queue / Surviving candidate / Active P2 / Fresh intake`）不存在“已达 `keep_P1 / P2 / P3` 但无正式 Rank”的违规。
- 无需分配新 `Rank`。

## 关键判断
- 当前没有待接线 `P3`，没有 `Active P2`，也没有 survivor 需要收口；所以本轮仍必须继续沿 fresh-intake 主线排班。
- `path-shape downside continuation` 已经在最新 optimization loop 中被诚实消费并收口，不能再占 cycle_plan 前排，也不能因为它刚写过日志就继续留在 front slot。
- 现在真正的前排对象是 `US-session cross-sectional intraday reversal`，而它的决定性 blocker 很集中：不是“alpha 是否存在”，而是这条时间窗横截面反转在 impact / participation realism 后，能否从 spot 中小币篮子迁移到 desk 更关心的 liquid-majors / 更少腿口径。
- 第二顺位的 `BTC-beta-neutral residual loser-bounce basket` 也适合继续排，但只能作为 conditional fresh intake：它当前最该回答的是 break-even cost 仍只有 `~2.4–2.9bps` 时，是否足以诚实支撑独立 front object。
- 第三顺位我改放最新的 `auction-profile value-area re-entry × LVN traverse shell`，而不是继续把较早的对象提到前面。原因很简单：
  - 它是最新 repo/paper/alpha report；
  - 主题与最近几天过密的 funding / pairs / maker 叙事有明显区隔；
  - blocker 也很集中——只要回答 `bar-volume profile proxy` 是否足以支撑可复算 edge，而不是分箱幻觉，就能快速 first verdict。
- `Deribit × Polymarket terminal-probability RV` 继续保留在第四顺位。它还算新，但当前 bundled evidence 的决定性问题仍是 edge half-life / fillability，而不是需要优先越过更新鲜对象。
- 我刻意没有把任何已进 `background/P0` 的旧对象重新拉回前排；这既符合 policy，也避免“最近日志很多就自动 reopen”的歪路径。

## cycle_plan rewrite（本轮执行）
已重写 `docs/BOT2_BOT3_STATE.md`，使当前轮保持 4 个合法 pending 小点：

1. `2026-04-17_2350_us-session-crosssectional-reversal-alpha.md`
2. `2026-04-17_2257_btcbetaneutral-residual-reversal-basket-alpha.md`
3. `2026-04-18_0049_auction-profile-poc-lvn-shell.md`
4. `2026-04-17_2114_deribit-polymarket-terminalprob-rv-alpha.md`

并同步保持：
- `Fresh intake slot.current_target` = `US-session cross-sectional intraday reversal`
- `Fresh intake slot.latest_result` = `path-shape downside continuation` 已收口 `background/P0`
- `Fresh intake slot.latest_result_record` = `research/optimization_loop/2026-04-18_0054_pathshape_downtrend_freshintake_background_p0_concentration.md`

每项都严格只保留：
- `target`
- `action`
- `success_criterion`
- `result = none`
- `status = pending`

## 为什么本轮这样排
- policy 的默认顺序是 `P3 > P2 > P1 > fresh intake > P0`；而当前 `P3 / P2 / P1` 都没有真实待执行动作，所以必须回到 fresh intake。
- 一旦切回 fresh intake，就必须给出**具体对象**，不能写空模板；因此我直接用最近、未被 runtime 消费、且仍不在 background 的 4 条候选填满预算。
- `US-session reversal` 放第一，是因为它已经是当前 front slot；bot2 不能跳过前排对象去追更新鲜发现。
- `BTC-beta-neutral residual reversal` 放第二，是因为它虽未过成本，但 blocker 已压缩成单一 `friction-threshold / execution-realism` 轴，适合做便宜 first verdict。
- `auction-profile` 放第三，是因为它是最新鲜、且与当前题池最不重叠的新材料；如果前两条都收口，应该优先尝试它，而不是回看旧对象。
- `Deribit × Polymarket` 放第四，作为仍然具体、但相对没那么新的 conditional intake 补位。

## P2 -> P3 兜底裁判检查
- 本轮无 `Active P2`。
- 因此不存在“desk review 已清楚表明对象足够值得进入 paper trade / paper launch，但 bot3 尚未升级”的兜底升 `P3` 场景。
- 本轮无需把任何对象直接写入 `P3 / Paper launch queue` 或 handoff 路径。

## Files changed
- `docs/BOT2_BOT3_STATE.md`
- `research/strategy_review/2026-04-18_0101_strategy-review.md`

## Tail steps
- homepage 刷新：按要求单独执行 `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`；若因 `/var/www` 写入、preflight、或需要 elevated 而失败，按规则记为**非阻断尾部失败**，不回滚本轮 review / state rewrite / log。
- 邮件通知：无论 publish 是否成功，均继续单独执行 `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot2-review] pathshape 收口后切到美股时段反转 intake" --body-file /root/clawd/jerry/momentum/research/strategy_review/2026-04-18_0101_strategy-review.md`。
