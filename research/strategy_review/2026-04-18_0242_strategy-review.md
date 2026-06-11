# 2026-04-18 02:42 UTC bot2 strategy review

## Inputs checked
- Policy: `docs/BOT2_BOT3_POLICY.md`
- State: `docs/BOT2_BOT3_STATE.md`
- Repo status: `git status --short`（仍主要是历史遗留未跟踪临时文件；本轮不把这些噪音当排班依据）
- Recent optimization loop:
  - `2026-04-18_0240_queuedepletion_freshintake_background_p0_cost_after_fill.md`
  - `2026-04-18_0225_auctionprofile_freshintake_background_p0_barprofile_proxy.md`
  - `2026-04-18_0158_btcbetaneutral_residual_reversal_freshintake_background_p0_frictionthreshold.md`
  - `2026-04-18_0142_ussession_crosssectional_reversal_freshintake_background_p0_major_portability.md`
  - `2026-04-18_0054_pathshape_downtrend_freshintake_background_p0_concentration.md`
  - `2026-04-18_0007_stablecoin_microdepeg_freshintake_background_p0_feefloor_fillrealism.md`
  - `2026-04-17_2336_correlationranked_pairs_freshintake_background_p0_singlepair_reality.md`
  - `2026-04-17_2310_rank4_freshintake_background_p0_pairs_residual_absorbed.md`
- Recent strategy review:
  - `2026-04-18_0150_strategy-review.md`
  - `2026-04-18_0101_strategy-review.md`
  - `2026-04-18_0013_strategy-review.md`
  - `2026-04-17_2246_strategy-review.md`
- Additional fresh-intake sources consulted for this rewrite:
  - `research/quant_digests/2026-04-17_2114_deribit-polymarket-terminalprob-rv-alpha.md`
  - `research/quant_digests/2026-04-18_0203_vwap-ema-bb-trendpullback-alpha.md`
  - `research/quant_digests/2026-04-18_0049_auction-profile-poc-lvn-shell.md`
  - `research/quant_digests/2026-04-17_2257_btcbetaneutral-residual-reversal-basket-alpha.md`

## 四个问题（本轮结论）
1. `Paper launch queue` 是否非空？
   - 结论：**否**。
   - `current_target = none`；`connected_runner_live` 虽非空，但这些对象都已完成 dedicated runner + scheduler + first verified run，不属于待接线 queue。

2. 本轮 `fresh intake` 是什么？
   - 结论：**`research/quant_digests/2026-04-17_2114_deribit-polymarket-terminalprob-rv-alpha.md`。**
   - 原因：`one-sided depth depletion × slow refill -> same-direction short drift` 已在 `2026-04-18_0240` 被 first verdict 诚实收口到 `background/P0`，因此当前前排 fresh intake 已自然切到 `Deribit terminal probability vs Polymarket binary price`。

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
   - 结论：**不值得。**
   - 上一条 fresh intake 是 `one-sided depth depletion × slow refill -> same-direction short drift`；最新收口结论已经够清楚：digest 自带 `~210s / 139 events` live probe 虽显示 queue depletion 后存在几秒级 signed drift，但 strongest bucket 也仅约 `ret5=+0.68bps / ret8=+0.82bps`，明显低于诚实 maker/taker 成本、队列时滞与排队失败门槛，不该占用 survivor 那唯一一次 follow-up。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
   - 结论：**不存在。**
   - `Active P2 = none`；最近一次 active P2 出口仍是 `Rank 417` 的 `one-time P2->P1 re-scope`，但它已经退出 active 槽位，不构成本轮待裁决对象。

## Rank 合规检查
- 当前前排对象（`Paper launch queue / Surviving candidate / Active P2 / Fresh intake`）不存在“已达 `keep_P1 / P2 / P3` 但无正式 Rank”的违规。
- 无需分配新 `Rank`。

## 关键判断
- 当前没有待接线 `P3`，没有 `Active P2`，也没有 survivor 需要收口；所以本轮必须继续沿 fresh-intake 主线排班。
- 当前 front slot 已经切到 `Deribit × Polymarket terminal-probability RV`，不能跳过它去追更新鲜的新题；按 policy，必须先把它压成 first verdict。
- 这条 cross-venue 概率错价线的 blocker 也已经足够集中：不是“repo 会不会算概率”，而是 **bundled evidence 只有极少交易样本，edge 到底能活多久、Polymarket 薄簿是否真能成交**。因此本轮 first verdict 应直接围绕 `edge half-life / fillability realism` 诚实裁决，而不是再散开去补更 fancy 的曲面细节。
- 第二顺位我放刚出的 `trend-up VWAP reclaim × lower-band pierce`。理由很直接：
  - 它是最新的 repo/alpha 报告；
  - 题材和最近密集的 pairs / carry / maker / prediction-market 叙事明显不同，能补当前池子里相对稀缺的 `trend-pullback continuation`；
  - 但它的决定性 blocker 也很集中——现有 portability 显示更像 `BTC long / SOL short` 的 asset-side selective pocket，而不是 broad-book alpha，所以只需要回答它是否足以诚实保留成独立 front object。
- 第三顺位保留 `auction-profile value-area re-entry × LVN traverse shell`。它还没被 runtime 消费，且决定性 blocker 仍然清楚：只要回答 `bar-volume profile proxy` 是否足以支撑可复算 edge，而不是分箱幻觉，就能给出诚实 first verdict。
- 第四顺位放 `BTC-beta-neutral residual loser-bounce basket`，不是因为它更强，而是因为它仍是合法未消费候选；但它已被最近 fresh-intake 计划多次证明 blocker 高度集中于 `~2.4–2.9bps` 的超薄 break-even 摩擦，所以只适合排在更晚的 conditional intake。
- 我刻意没有把任何已进 `background/P0` 的旧对象重新拉回前排，也没有把 `Background pool guard` 单独写成 cycle_plan 小点。

## cycle_plan rewrite（本轮执行）
已重写 `docs/BOT2_BOT3_STATE.md`，使当前轮保持 4 个合法 pending 小点：

1. `2026-04-17_2114_deribit-polymarket-terminalprob-rv-alpha.md`
2. `2026-04-18_0203_vwap-ema-bb-trendpullback-alpha.md`
3. `2026-04-18_0049_auction-profile-poc-lvn-shell.md`
4. `2026-04-17_2257_btcbetaneutral-residual-reversal-basket-alpha.md`

并同步保持：
- `Fresh intake slot.current_target` = `Deribit terminal probability vs Polymarket binary price`
- `Fresh intake slot.latest_result` = `one-sided depth depletion × slow refill -> same-direction short drift` 已收口 `background/P0`
- `Fresh intake slot.latest_result_record` = `research/optimization_loop/2026-04-18_0240_queuedepletion_freshintake_background_p0_cost_after_fill.md`

每项都严格只保留：
- `target`
- `action`
- `success_criterion`
- `result = none`
- `status = pending`

## 为什么本轮这样排
- policy 的默认顺序是 `P3 > P2 > P1 > fresh intake > P0`；而当前 `P3 / P2 / P1` 都没有真实待执行动作，所以必须回到 fresh intake。
- 一旦切回 fresh intake，就必须给出**具体对象**；因此本轮直接用当前 front object + 最近未消费的新 alpha 报告填满预算。
- `Deribit × Polymarket` 放第一，是因为它已经是当前 front slot；bot2 不能跳过前排对象去追更新鲜发现。
- `VWAP/EMA/BB trend-pullback` 放第二，是因为它是当前最新且 distinctness 最强的新材料，决定性 blocker 也压缩得足够集中。
- `auction-profile` 放第三，是因为它虽稍早一拍，但仍未被 runtime 消费，且作为独立主题母板的价值判断仍未完成。
- `BTC-beta-neutral residual reversal` 放第四，是因为它依然是合法未消费对象，但相较前面三条更旧、且 blocker 已经被压缩到非常单一的超薄摩擦问题，优先级自然更低。

## P2 -> P3 兜底裁判检查
- 本轮无 `Active P2`。
- 因此不存在“desk review 已清楚表明对象足够值得进入 paper trade / paper launch，但 bot3 尚未升级”的兜底升 `P3` 场景。
- 本轮无需把任何对象直接写入 `P3 / Paper launch queue` 或 handoff 路径。

## Files changed
- `docs/BOT2_BOT3_STATE.md`
- `research/strategy_review/2026-04-18_0242_strategy-review.md`

## Tail steps
- homepage 刷新：按要求单独执行 `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`；若因 `/var/www` 写入、preflight、或需要 elevated 而失败，按规则记为**非阻断尾部失败**，不回滚本轮 review / state rewrite / log。
- 邮件通知：无论 publish 是否成功，均继续单独执行 `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot2-review] 切到 Deribit 概率错价 intake 并补趋势回踩候选" --body-file /root/clawd/jerry/momentum/research/strategy_review/2026-04-18_0242_strategy-review.md`。
