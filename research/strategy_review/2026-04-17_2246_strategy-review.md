# 2026-04-17 22:46 UTC bot2 strategy review

## Inputs checked
- Policy: `docs/BOT2_BOT3_POLICY.md`
- State: `docs/BOT2_BOT3_STATE.md`
- Repo status: `git status --short --branch`（仍主要是历史遗留未跟踪临时文件；本轮不把这些噪音当排班依据）
- Recent optimization loop:
  - `2026-04-17_2238_rank25c_conditional_freshintake_background_p0_consumed.md`
  - `2026-04-17_2213_rank14b_conditional_freshintake_background_p0_consumed.md`
  - `2026-04-17_2159_rank57_freshintake_background_p0_compression_residual_replay_closed.md`
  - `2026-04-17_2132_rank101_freshintake_background_p0_holdquality_note_absorbed.md`
  - `2026-04-17_2109_rank5_freshintake_background_p0_sameclock_residual_absorbed.md`
  - `2026-04-17_2032_rank28_freshintake_background_p0_residual_absorbed.md`
- Recent strategy review:
  - `2026-04-17_2141_strategy-review.md`
  - `2026-04-17_2101_strategy-review.md`
  - `2026-04-17_1955_strategy-review.md`
- Additional evidence consulted for this rewrite:
  - `research/park_reframe/2026-04-16_0418_rank4-park-reframe.md`
  - `research/quant_digests/2026-04-17_2226_correlationranked-ratio-zscore-pairs-alpha.md`
  - `research/quant_digests/2026-04-17_2156_stablecoin-microdepeg-grid-shell.md`
  - `research/quant_digests/2026-04-17_2056_pathshape-downtrend-continuation-alpha.md`

## 四个问题（本轮结论）
1. `Paper launch queue` 是否非空？
   - 结论：**否**。
   - `current_target = none`；`connected_runner_live` 虽非空，但这些对象都已完成 dedicated runner + scheduler + first verified run，不属于待接线 queue。

2. 本轮 `fresh intake` 是什么？
   - 结论：**`Rank 4 / pairs threshold-governance / basket-governance residual`。**
   - 原因：`Rank 57 -> Rank 14b -> Rank 25c` 已在 21:59 / 22:13 / 22:38 UTC 按顺序诚实收口 `background/P0`，没有形成新的 survivor / P2；因此当前前排 fresh intake 已自然切到 `research/park_reframe/2026-03-24_1430_rank4-park-reframe.md`。

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
   - 结论：**不值得。**
   - 上一条 fresh intake 是 `Rank 25c`；它已被 `Rank 245` 的 intake + survivor A/B 诚实消费，最新 22:38 UTC 的 first verdict 再次确认它仍只是 shared HTF gate 的岗位重写，没有留下独立 after-cost breakout pocket，因此不拿 survivor 槽位。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
   - 结论：**不存在。**
   - `Active P2 = none`；最近一次 P2 出口仍是 `Rank 417` 的 one-time `P2->P1 re-scope`，但它已退出 active 槽位，不构成本轮待裁决对象。

## Rank 合规检查
- 当前前排对象（`Paper launch queue / Surviving candidate / Active P2 / Fresh intake`）不存在“已达 `keep_P1 / P2 / P3` 但无正式 Rank”的违规。
- 无需分配新 `Rank`。

## 关键判断
- 当前没有待接线 `P3`，没有 `Active P2`，也没有 survivor 需要收口；因此本轮必须继续沿 fresh-intake 主线排班。
- 但当前 front slot 不是新的 repo/paper，而是**已经被前序 runtime 顺排出来、尚未裁决的 `Rank 4` residual**；按 policy，必须先把这个前排对象诚实收口，不能绕过去直接插入更新鲜的新发现。
- `Rank 4` 的最新 park-reframe（`2026-04-16_0418_rank4-park-reframe.md`）已经把边界说得很硬：pairs 主题仍活，但真正可救的是新的 admission / basket / full-shell 宿主，而不是旧 `Rank 4` 的 direct spread-entry residual；因此本轮 item1 应直接围绕这个“旧 rank 还能否保留独立 front-slot”做 first verdict。
- 只有在 `Rank 4` 已诚实收口且仍无 survivor / P2 后，才允许用剩余预算回到**最近新的 repo/paper/alpha reports**。
- 在刚新增、且比继续翻 park-reframe 更值得补的具体对象里，本轮最值得排在后面的三个是：
  1. `2026-04-17_2226_correlationranked-ratio-zscore-pairs-alpha.md`
     - 原因：它正好承接 `Rank 4` 主题外流后的“新 pairs-family 宿主”，但 first verdict 必须先回答 pocket 是否只是 `ARB/OP 1m` 单点残差，不能偷渡成旧 Rank 4 reopen。
  2. `2026-04-17_2156_stablecoin-microdepeg-grid-shell.md`
     - 原因：base alpha 清楚、可落完整壳，但最小 honesty blocker 也很清楚——queue/fill + fee-floor realism；很适合做一次便宜而决定性的 first verdict。
  3. `2026-04-17_2056_pathshape-downtrend-continuation-alpha.md`
     - 原因：它给出了 `SOL 15m short` 的 after-cost pocket，但当前最需要的不是再讲论文，而是回答这是否只是单一标的样本窗 luck，还是足以保留独立 front-slot。
- 我**没有**把更多 park-reframe 残余继续顺排到 `Rank 4` 后面，因为当前 policy 的默认来源优先级已经切回“最近新 repo/paper/alpha report”，而且 `Rank 57 / 14b / 25c` 这条旧残余链刚被 runtime 连续消费完，再继续堆同类 residual 会变成低杠杆重复。

## cycle_plan rewrite（本轮执行）
已重写 `docs/BOT2_BOT3_STATE.md`，使当前轮只保留 4 个仍未被 runtime 消费、且顺序合法的 pending 小点：

1. `Rank 4` fresh intake first-verdict
2. `2026-04-17_2226_correlationranked-ratio-zscore-pairs-alpha.md` conditional fresh intake
3. `2026-04-17_2156_stablecoin-microdepeg-grid-shell.md` conditional fresh intake
4. `2026-04-17_2056_pathshape-downtrend-continuation-alpha.md` conditional fresh intake

每项都按 policy 只保留：
- `target`
- `action`
- `success_criterion`
- `result = none`
- `status = pending`

## 为什么本轮这样排
- `Rank 4` 必须在第一位，因为它是**当前前排唯一合法、且尚未收口的具体对象**；已有前排对象的收口优先级永远高于新的发现。
- `Rank 4` 之后，才轮到新的 fresh intake；此时默认来源优先级应回到最近新 repo/paper/alpha report，而不是继续把 background/park 残余拉回前排。
- `correlation-ranked pairs` 被放在 item2，不是为了重开旧 `Rank 4`，而是为了在 `Rank 4` 若被判回 background 后，直接测试它所指向的**新 pairs-family 宿主**是否值得占用前排。
- `stablecoin micro-depeg` 与 `path-shape downside continuation` 则分别代表：
  - 一个 execution-realism 很强、但 base alpha 极清楚的新 maker-ish 原料；
  - 一个有明确 recent pocket、但需要最小 portability / concentration honesty 检查的新 short-side 原料。
- 这比继续在今天已被消费的 `Rank 5 / 57 / 14b / 25c / 28 / 33 / 56 / 83 / 89 / 101` 上复读更诚实。

## P2 -> P3 兜底裁判检查
- 本轮无 `Active P2`。
- 因此不存在“desk review 已清楚表明对象足够值得进入 paper trade / paper launch，但 bot3 尚未升级”的兜底升 `P3` 场景。
- 本轮无需把任何对象直接写入 `P3 / Paper launch queue` 或 handoff 路径。

## Files changed
- `docs/BOT2_BOT3_STATE.md`
- `research/strategy_review/2026-04-17_2246_strategy-review.md`

## Tail steps
- homepage 刷新：按要求单独执行 `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`；若因 `/var/www` 写入、preflight、或 `SIGKILL` 失败，按规则记为**非阻断尾部失败**，不回滚本轮 review / state rewrite / log。
- 邮件通知：无论 publish 是否成功，均继续单独执行 `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot2-review] Rank4前排收口并切回新repo intake" --body-file /root/clawd/jerry/momentum/research/strategy_review/2026-04-17_2246_strategy-review.md`。