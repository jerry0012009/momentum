# 2026-04-18 01:50 UTC bot2 strategy review

## Inputs checked
- Policy: `docs/BOT2_BOT3_POLICY.md`
- State: `docs/BOT2_BOT3_STATE.md`
- Repo status: `git status --short`（仍主要是历史遗留未跟踪临时文件；本轮不把这些噪音当排班依据）
- Recent optimization loop:
  - `2026-04-18_0142_ussession_crosssectional_reversal_freshintake_background_p0_major_portability.md`
  - `2026-04-18_0054_pathshape_downtrend_freshintake_background_p0_concentration.md`
  - `2026-04-18_0007_stablecoin_microdepeg_freshintake_background_p0_feefloor_fillrealism.md`
  - `2026-04-17_2336_correlationranked_pairs_freshintake_background_p0_singlepair_reality.md`
  - `2026-04-17_2310_rank4_freshintake_background_p0_pairs_residual_absorbed.md`
  - `2026-04-17_2238_rank25c_conditional_freshintake_background_p0_consumed.md`
  - `2026-04-17_2213_rank14b_conditional_freshintake_background_p0_consumed.md`
  - `2026-04-17_2159_rank57_freshintake_background_p0_compression_residual_replay_closed.md`
- Recent strategy review:
  - `2026-04-18_0101_strategy-review.md`
  - `2026-04-18_0013_strategy-review.md`
  - `2026-04-17_2246_strategy-review.md`
  - `2026-04-17_2141_strategy-review.md`
- Additional fresh-intake sources consulted for this rewrite:
  - `research/quant_digests/2026-04-17_2257_btcbetaneutral-residual-reversal-basket-alpha.md`
  - `research/quant_digests/2026-04-18_0049_auction-profile-poc-lvn-shell.md`
  - `research/quant_digests/2026-04-18_0146_queue-depletion-refill-asymmetry-alpha.md`
  - `research/quant_digests/2026-04-17_2114_deribit-polymarket-terminalprob-rv-alpha.md`

## 四个问题（本轮结论）
1. `Paper launch queue` 是否非空？
   - 结论：**否**。
   - `current_target = none`；`connected_runner_live` 虽非空，但这些对象都已完成 dedicated runner + scheduler + first verified run，不属于待接线 queue。

2. 本轮 `fresh intake` 是什么？
   - 结论：**`research/quant_digests/2026-04-17_2257_btcbetaneutral-residual-reversal-basket-alpha.md`。**
   - 原因：`US-session cross-sectional intraday reversal` 已在 `2026-04-18_0142` 被 first verdict 诚实收口到 `background/P0`，因此当前前排 fresh intake 已自然切到 `BTC-beta-neutral residual loser-bounce basket`。

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
   - 结论：**不值得。**
   - 上一条 fresh intake 是 `US-session cross-sectional intraday reversal`；最新收口结论已经够清楚：repo 自带的 liquid-majors portability 检查显示，压到 `BTC/ETH/SOL/BNB` 后虽然 total TC 降到约 `47.5bps/day`，但 gross alpha 也同步塌到仅 `4.5bps/day`、低于 commission，本质上只是 spot 中小币拥挤/冲击环境里的薄 pocket，不该占用 survivor 那唯一一次 follow-up。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
   - 结论：**不存在。**
   - `Active P2 = none`；最近一次 active P2 出口仍是 `Rank 417` 的 `one-time P2->P1 re-scope`，但它已经退出 active 槽位，不构成本轮待裁决对象。

## Rank 合规检查
- 当前前排对象（`Paper launch queue / Surviving candidate / Active P2 / Fresh intake`）不存在“已达 `keep_P1 / P2 / P3` 但无正式 Rank”的违规。
- 无需分配新 `Rank`。

## 关键判断
- 当前没有待接线 `P3`，没有 `Active P2`，也没有 survivor 需要收口；所以本轮必须继续沿 fresh-intake 主线排班。
- 当前 front slot 已经切到 `BTC-beta-neutral residual loser-bounce basket`，不能跳过它去追更晚的新题；按 policy，必须先把它压成 first verdict。
- 这条 residual-reversal 线的 blocker 已经很集中：不是 base alpha 是否存在，而是 `5m/15m` portability 后 break-even 摩擦仍只有 `~2.4–2.9bps`，因此 first verdict 应直接围绕 `friction-threshold / execution realism` 诚实裁决，而不是再散开补别的轴。
- 第二顺位放 `auction-profile value-area re-entry × LVN traverse shell` 仍然合理：它是最新未消费的大主题之一，且和最近几天过密的 funding / pairs / maker 叙事区隔明显；决定性 blocker 也很集中——只要回答 bar-volume profile proxy 是否足以支撑可复算 edge，而不是分箱幻觉。
- 第三顺位我改成刚出的 `queue depletion × slow refill`，而不是继续把 `Deribit × Polymarket terminal-probability RV` 放得更靠前。原因是：
  - 它是更新鲜的 repo/paper/live-probe 组合；
  - 它和当前题池里已有的静态 OBI / maker skew 不同，更接近事件型 microstructure raw alpha；
  - blocker 很集中：只要回答这条线在 maker/taker 成本后究竟能不能留下正 edge，而不是停留在几秒级 directionality 故事。
- `Deribit × Polymarket terminal-probability RV` 继续保留为第 4 个 conditional intake。它仍是具体对象，但当前 bundled evidence 的决定性问题还是 edge half-life / fillability；在已有前三条更前排、更新鲜的对象前，不该再排得更靠前。
- 我刻意没有把任何已进 `background/P0` 的旧对象拉回前排，也没有把 `Background pool guard` 单独写成 cycle_plan 小点。

## cycle_plan rewrite（本轮执行）
已重写 `docs/BOT2_BOT3_STATE.md`，使当前轮保持 4 个合法 pending 小点：

1. `2026-04-17_2257_btcbetaneutral-residual-reversal-basket-alpha.md`
2. `2026-04-18_0049_auction-profile-poc-lvn-shell.md`
3. `2026-04-18_0146_queue-depletion-refill-asymmetry-alpha.md`
4. `2026-04-17_2114_deribit-polymarket-terminalprob-rv-alpha.md`

并同步保持：
- `Fresh intake slot.current_target` = `BTC-beta-neutral residual loser-bounce basket`
- `Fresh intake slot.latest_result` = `US-session cross-sectional intraday reversal` 已收口 `background/P0`
- `Fresh intake slot.latest_result_record` = `research/optimization_loop/2026-04-18_0142_ussession_crosssectional_reversal_freshintake_background_p0_major_portability.md`

每项都严格只保留：
- `target`
- `action`
- `success_criterion`
- `result = none`
- `status = pending`

## 为什么本轮这样排
- policy 的默认顺序是 `P3 > P2 > P1 > fresh intake > P0`；而当前 `P3 / P2 / P1` 都没有真实待执行动作，所以必须回到 fresh intake。
- 一旦切回 fresh intake，就必须给出**具体对象**；因此本轮直接用前排当前对象 + 最近、未被 runtime 消费、且不来自 background 自动 reopen 的 3 条具体候选填满预算。
- `BTC-beta-neutral residual reversal` 放第一，是因为它已经是当前 front slot；bot2 不能跳过它去追更新鲜发现。
- `auction-profile` 放第二，是因为它是当前最像“新主题母板”的未消费对象，决定性 blocker 也压缩得足够集中。
- `queue depletion × slow refill` 放第三，是因为它比 `Deribit × Polymarket` 更新鲜，且能更直接扩充当前 microstructure 素材池；本轮把它放到 `auction-profile` 之后、`Deribit × Polymarket` 之前，更符合“最近新 repo/paper/alpha 报告优先”的默认来源顺序。
- `Deribit × Polymarket` 放第四，作为仍然具体、但相对没那么新的 conditional intake 补位。

## P2 -> P3 兜底裁判检查
- 本轮无 `Active P2`。
- 因此不存在“desk review 已清楚表明对象足够值得进入 paper trade / paper launch，但 bot3 尚未升级”的兜底升 `P3` 场景。
- 本轮无需把任何对象直接写入 `P3 / Paper launch queue` 或 handoff 路径。

## Files changed
- `docs/BOT2_BOT3_STATE.md`
- `research/strategy_review/2026-04-18_0150_strategy-review.md`

## Tail steps
- homepage 刷新：按要求单独执行 `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`；若因 `/var/www` 写入、preflight、或需要 elevated 而失败，按规则记为**非阻断尾部失败**，不回滚本轮 review / state rewrite / log。
- 邮件通知：无论 publish 是否成功，均继续单独执行 `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot2-review] 切到残差反转 intake 并补队列耗尽题" --body-file /root/clawd/jerry/momentum/research/strategy_review/2026-04-18_0150_strategy-review.md`。
