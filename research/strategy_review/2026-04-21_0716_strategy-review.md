# 2026-04-21 07:16 UTC strategy review

## Inputs checked
- Policy: `docs/BOT2_BOT3_POLICY.md`
- State: `docs/BOT2_BOT3_STATE.md`
- Repo status: `git status --short`（当前主要是工作区根目录历史未跟踪临时文件；`jerry/momentum` 本轮未见需要改变排班结论的前排代码改动）
- Recent optimization evidence:
  - `research/optimization_loop/2026-04-21_0623_dynamic_momentum_cycle_router_freshintake_background_p0.md`
  - `research/optimization_loop/2026-04-21_0534_cttrend_xs_techstack_freshintake_background_p0.md`
  - `research/optimization_loop/2026-04-21_0512_volumeweighted_xs_momentum_avr_freshintake_background_p0_concentration.md`
  - `research/optimization_loop/2026-04-21_0442_hawkes_lob_excitation_freshintake_background_p0.md`
  - `research/optimization_loop/2026-04-21_0431_speed_volume_momentum_freshintake_background_p0_concentration.md`
- Recent strategy review evidence:
  - `research/strategy_review/2026-04-21_0636_strategy-review.md`
  - `research/strategy_review/2026-04-21_0456_strategy-review.md`
- Fresh candidate sources checked:
  - `research/quant_digests/2026-04-21_0700_bybit-positive-funding-decay-carry-shell.md`
  - `research/quant_digests/2026-04-21_0607_mefai-scalping-microtrend-volspike-shell.md`
  - `research/quant_digests/2026-04-21_0528_cointegration-maker-timestop-pairs-alpha.md`
  - `research/park_reframe/2026-04-06_0606_rank27-park-reframe.md`

## 仅回答 4 个问题
1. `Paper launch queue` 是否非空？
- 是，非空：`connected_runner_live` 里已有多条已接线对象；但 `current_target = none`，当前没有待补 runner / scheduler / first verified run 的 active P3 接线项。

2. 本轮 `fresh intake` 是什么？
- 在 `P3 / Active P2 / Surviving candidate` 均无真实可执行动作的前提下，本轮 fresh intake 重排为：
  - `research/quant_digests/2026-04-21_0700_bybit-positive-funding-decay-carry-shell.md`
  - `research/quant_digests/2026-04-21_0607_mefai-scalping-microtrend-volspike-shell.md`
  - `research/quant_digests/2026-04-21_0528_cointegration-maker-timestop-pairs-alpha.md`
  - `research/park_reframe/2026-04-06_0606_rank27-park-reframe.md`（conditional fresh intake）

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 不值得。最近一条 fresh intake 是 `dynamic momentum-cycle continuation × strongest-only router`，已在 `research/optimization_loop/2026-04-21_0623_dynamic_momentum_cycle_router_freshintake_background_p0.md` 诚实判为 `background/P0`；结论是 `5m strongest-only + 8bps` 下整体与 recent slice 费后为负，且残余主要集中在 `ETH` 单币，不满足 survivor follow-up 条件。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 不存在。`Active P2 = none`。

## Rank 完整性检查
- 前排槽位检查：
  - `Paper launch queue.current_target = none`
  - `Surviving candidate slot.current_target = none`
  - `Active P2 slot.current_target = none`
- 当前前排不存在缺 rank 对象；本轮无需补新 `Rank`。

## State rewrite（按 policy 默认排班顺序）
- 当前没有待接线 `P3`、没有 `Active P2`、也没有 survivor follow-up，因此合法动作全部来自 fresh intake。
- 结合最新 digest，到本轮为止最值得做的具体对象顺序是：
  1. `Bybit high positive funding persistence × exit-threshold carry shell` first verdict
  2. `MEFAI scalping microtrend × volume-spike shell` first verdict
  3. `cointegration maker-first + hard time-stop pairs` first verdict
  4. `Rank 27c / neckline breakout-bar taker-imbalance confirmation` conditional fresh intake first verdict
- 已写回 `docs/BOT2_BOT3_STATE.md`：
  - 将新出的 `2026-04-21_0700_bybit-positive-funding-decay-carry-shell.md` 提到本轮第 1 优先级；
  - 保留两条最新 digest 作为第 2 / 3 项；
  - 仅保留 1 条 conditional fresh intake，占用最后一个预算位；
  - 移除本轮不再优先的 `rank89` conditional item，避免在 recent repo/digest 仍充足时过早回退到 park reframe。

## P2 -> P3 兜底判断
- 当前无 `Active P2`，也没有 desk review 已清楚表明“足够进入 paper trade、但 bot3 尚未升级”的对象。
- 本轮不存在需要 bot2 直接强推到 `P3 / Paper launch queue` 的候选。

## Tail step status
- homepage publish（独立命令）已尝试：`bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`，最终 `SIGKILL`，按 policy 记为**非阻断尾部失败**，不回滚本轮已完成的 state rewrite / review log。
- email notify（独立命令）已完成：`python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot2-review] 前排空窗切换到三条新digest加一条park候选" --body-file /root/clawd/jerry/momentum/research/strategy_review/2026-04-21_0716_strategy-review.md`，已发送到默认收件人。