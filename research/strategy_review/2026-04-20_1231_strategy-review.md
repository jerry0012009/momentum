# 2026-04-20 12:31 UTC strategy review

## Inputs checked
- Policy: `docs/BOT2_BOT3_POLICY.md`
- State: `docs/BOT2_BOT3_STATE.md`
- Repo status: `git -C /root/clawd/jerry/momentum status --short`
- Recent optimization evidence:
  - `research/optimization_loop/2026-04-20_1153_crosschain_negative_spillover_freshintake_background_p0_cost_delay.md`
  - `research/optimization_loop/2026-04-20_1133_bbtouch_oppositeband_freshintake_background_p0_makerfill.md`
  - `research/optimization_loop/2026-04-20_0726_hyperliquid_funding_signflip_freshintake_background_p0.md`
  - `research/optimization_loop/2026-04-20_0659_negative_funding_5davg_carry_freshintake_background_p0.md`
  - `research/optimization_loop/2026-04-20_0116_rank427_launch_wiring_connected_runner_live.md`
  - `research/optimization_loop/2026-04-19_2354_rank427_p2_exit_promote_p3_exeth_corebounce.md`
- Recent strategy review evidence:
  - `research/strategy_review/2026-04-20_1118_strategy-review.md`
  - `research/strategy_review/2026-04-20_0912_strategy-review.md`
  - `research/strategy_review/2026-04-20_0229_strategy-review.md`
- Recent candidate sources scanned:
  - `research/quant_digests/2026-04-19_1636_xs-reversal-horizon-transition-portability.md`
  - `research/quant_digests/2026-04-19_1712_emacross-volume-bracket-pocket-alpha.md`
  - `research/quant_digests/2026-04-19_1746_bbsqueeze-release-shortbasket-alpha.md`
  - `research/quant_digests/2026-04-19_2240_fundingcarry-regimeaware-childexec-alpha.md`
  - `research/quant_digests/2026-04-19_2312_scalp-confluence-timeboxed-bounce-shell.md`

## Repo snapshot
- `Paper launch queue` 非空；当前只有 `connected_runner_live` 存量对象，`current_target = none`，没有待接线 P3。
- 本轮开始时 `Fresh intake slot = none`，因为前两条 pending intake 已被 bot3 先后诚实收口：
  - `2026-04-19_2132_bbtouch-oppositeband-maker-shell.md` -> `background/P0`
  - `2026-04-19_1602_crosschain-negative-spillover-rv-alpha.md` -> `background/P0`
- `Surviving candidate slot = none`；上一条 survivor 仍是 `Rank 428`，且其唯一 follow-up 已在 `2026-04-20_0128` 用尽并转 `background/P0`。
- `Active P2 slot = none`；最近唯一 P2 出口仍是 `Rank 427`，已于 `2026-04-19_2354` 升 `P3`，并在 `2026-04-20_0116` 完成 runner/scheduler/first verified run。
- 当前前排不存在无 rank 对象，也不存在需要 bot2 兜底直推 `P2 -> P3` 的遗漏个案。

## 仅回答 4 个问题
1. `Paper launch queue` 是否非空？
- 是。`connected_runner_live` 非空，但 `current_target = none`，当前没有未完成 launch wiring 的 P3 对象。

2. 本轮 `fresh intake` 是什么？
- 现在切到新的具体 fresh intake：`research/quant_digests/2026-04-19_1636_xs-reversal-horizon-transition-portability.md`。

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 不值得。上一条 fresh intake 是 `research/quant_digests/2026-04-19_1602_crosschain-negative-spillover-rv-alpha.md`；它已在 `2026-04-20_1153` 直接收口 `background/P0`，没有 survivor 资格，也不应给 follow-up。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 不存在，`Active P2 = none`。

## Rank 完整性检查
- 当前前排对象检查结果：
  - `Paper launch queue.current_target = none`
  - `Surviving candidate slot = none`
  - `Active P2 slot = none`
  - 新 fresh intake 仍未首判，不需要预先分配 rank
- 因此前排不存在“已达 keep_P1/P2/P3 但无 rank”的违规对象，本轮无需补整数 `Rank`。

## State rewrite
已按 policy 重写 `docs/BOT2_BOT3_STATE.md`：
- `Fresh intake slot` 改为 pending，并锁定到 `2026-04-19_1636_xs-reversal-horizon-transition-portability.md`。
- 保留已完成结论：`bbtouch-oppositeband-maker-shell` 与 `crosschain-negative-spillover-rv-alpha` 均已诚实收口到 `background/P0`。
- 由于当前不存在真实 `P3 / P2 / P1` 可执行动作，本轮 `cycle_plan` 全部合法地回到 fresh intake / conditional fresh intake。
- 未改 policy / brief / cron prompt；未从 background pool 自动拉回任何旧候选。

## 当前轮 cycle_plan
1. `research/quant_digests/2026-04-19_1636_xs-reversal-horizon-transition-portability.md`
   - action: fresh intake first verdict，只补 1 条最小 blocker：短窗 loser→winner reversal 在 turnover cap、统一 `8bps` 成本、腿数压缩与 core/majors/月度切片后，是否还剩可承接的 after-cost XS pocket。
   - success_criterion: 只能输出 `keep_P1` 或 `background/P0`；若正边际依赖过多腿数、极端换手、单资产或单月集中，则直接收口。
2. `research/quant_digests/2026-04-19_1712_emacross-volume-bracket-pocket-alpha.md`
   - action: conditional fresh intake，只补 1 条最小 blocker：`EMA cross × volume confirmation × bracket exit pocket` 在 next-bar entry、固定 stop/TP、成本梯度与 TIME exit realism 后是否仍保留独立 after-cost pocket。
   - success_criterion: 必须直接 `keep_P1` 或 `background/P0`；若只剩 BTC 单币或单一参数 pocket，不留 survivor。
3. `research/quant_digests/2026-04-19_1746_bbsqueeze-release-shortbasket-alpha.md`
   - action: conditional fresh intake，只补 1 条最小 blocker：`ETH/XRP/LINK` short-only / top1 router 的正 pocket 在 `15m` next-bar entry、ATR stop/target、score 选择与月份/资产切片后是否仍保留可复制 after-cost downside drift。
   - success_criterion: 必须直接 `keep_P1` 或 `background/P0`；只有非单币支撑的正 net 才能保留。
4. `research/quant_digests/2026-04-19_2240_fundingcarry-regimeaware-childexec-alpha.md`
   - action: conditional fresh intake guard：若前 3 项均未产生 survivor，先确认它是否已被 `2026-04-20_0222` 明确收口；若已收口则不得重复 intake，直接跳到下一条具体新对象 `2026-04-19_2312_scalp-confluence-timeboxed-bounce-shell.md`。
   - success_criterion: 只能输出 `blocked`，或对 `scalp-confluence-timeboxed-bounce-shell` 直接给出 fresh intake first verdict；不得把已收口对象重新伪装成新的 fresh intake。

## Review verdict
- 本轮不存在需要 bot2 兜底裁决的 `Active P2 -> P3` 个案；`Rank 427` 的 promote 与 launch wiring 已经完成，无需重复升级。
- `Paper launch queue` 虽非空，但当前没有未接线对象，所以按 policy 默认顺序切回 fresh intake 是正确动作。
- 上一条 fresh intake 已明确不值得 follow-up；因此 survivor 槽位继续保持空，不应被伪造占用。
- 当前唯一真实前排动作是 `2026-04-19_1636_xs-reversal-horizon-transition-portability.md` 的 first verdict；其后才是具体 conditional intake。
