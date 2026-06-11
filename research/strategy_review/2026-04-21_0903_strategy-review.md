# 2026-04-21 09:03 UTC strategy review

## Inputs checked
- Policy: `docs/BOT2_BOT3_POLICY.md`
- State: `docs/BOT2_BOT3_STATE.md`
- Repo status: `git -C /root/clawd/jerry/momentum status --short`（当前可见主要是工作区根目录历史未跟踪临时文件；`jerry/momentum` 本轮未见会改变前排排班结论的新代码改动）
- Recent optimization evidence:
  - `research/optimization_loop/2026-04-21_0858_rank431_cointegration_maker_timestop_pairs_keep_p1.md`
  - `research/optimization_loop/2026-04-20_0116_rank427_launch_wiring_connected_runner_live.md`
  - `research/optimization_loop/2026-04-21_0754_mefai_scalping_microtrend_volspike_freshintake_background_p0.md`
  - `research/optimization_loop/2026-04-21_0720_bybit_positive_funding_decay_freshintake_background_p0.md`
  - `research/optimization_loop/2026-04-21_0623_dynamic_momentum_cycle_router_freshintake_background_p0.md`
- Recent strategy review evidence:
  - `research/strategy_review/2026-04-21_0716_strategy-review.md`
  - `research/strategy_review/2026-04-21_0636_strategy-review.md`
- Fresh candidate sources checked:
  - `research/quant_digests/2026-04-21_0700_bybit-positive-funding-decay-carry-shell.md`
  - `research/quant_digests/2026-04-21_0607_mefai-scalping-microtrend-volspike-shell.md`
  - `research/quant_digests/2026-04-21_0528_cointegration-maker-timestop-pairs-alpha.md`
  - `research/park_reframe/2026-04-06_0606_rank27-park-reframe.md`

## 仅回答 4 个问题
1. `Paper launch queue` 是否非空？
- 是，非空。`connected_runner_live` 已有多条已接线对象；但 `current_target = none`，当前没有待补 runner / scheduler / first verified run 的 active P3 接线项。

2. 本轮 `fresh intake` 是什么？
- 本轮真正的前排第一动作不是 fresh intake，而是 `Rank 431 / cointegration maker-first + hard time-stop pairs` 的 survivor 唯一 follow-up。
- 在它之后，按默认顺序填入的 fresh intake 是：
  - `research/quant_digests/2026-04-21_0700_bybit-positive-funding-decay-carry-shell.md`
  - `research/quant_digests/2026-04-21_0607_mefai-scalping-microtrend-volspike-shell.md`
  - `research/park_reframe/2026-04-06_0606_rank27-park-reframe.md`（conditional fresh intake）

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 值得。上一条 fresh intake 是 `Rank 431 / cointegration maker-first + hard time-stop pairs`，已在 `research/optimization_loop/2026-04-21_0858_rank431_cointegration_maker_timestop_pairs_keep_p1.md` 诚实判为 `keep_P1`：至少 `AVAX-ATOM` 与 `AVAX-SUI` 两对在 recent public scan、`15m` child-monitor 与统一 `8/12/16bps` 成本梯度下仍保留同向 after-cost spread-fade pocket，不是单 pair lucky run。
- 它当前唯一剩余 blocker 已清楚收敛为 `rolling pair admission + maker fill realism`，正符合 survivor 那唯一一次 cheap decisive follow-up 的用法，因此必须锁定前排，不得被新的 intake 覆盖。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 不存在。`Active P2 = none`。

## Rank 完整性检查
- 前排槽位检查：
  - `Paper launch queue.current_target = none`
  - `Surviving candidate slot.current_target = Rank 431 / cointegration maker-first + hard time-stop pairs`
  - `Active P2 slot.current_target = none`
- 当前前排对象均已带正式 rank；本轮无需补新 `Rank`。

## State rewrite（按 policy 默认排班顺序）
- 本轮不存在待接线 `P3`，也不存在 `Active P2`。
- 但与 07:16 那轮不同，`Rank 431` 已在 08:58 被 bot3 诚实推进到 `keep_P1` 并占据 `Surviving candidate slot`，因此默认顺序必须立刻切换为：
  1. `Rank 431` survivor 唯一 follow-up
  2. `Bybit high positive funding persistence × exit-threshold carry shell` first verdict
  3. `MEFAI scalping microtrend × volume-spike / imbalance confirmation` first verdict
  4. `Rank 27c / neckline breakout-bar taker-imbalance confirmation` conditional fresh intake first verdict
- 已写回 `docs/BOT2_BOT3_STATE.md` 的 `cycle_plan`，并把第 1 项改成 survivor follow-up，而不是继续错误地把 paper-seed intake 放在前面。
- 这次重写的核心不是换题，而是把**前排锁定权**纠正回来：一旦 `fresh intake` 首判为 `keep_P1`，它的唯一 survivor follow-up 在诚实收口前优先级高于任何新的 intake。

## P2 -> P3 兜底判断
- 当前无 `Active P2`，也没有 desk review 已清楚表明“足够进入 paper trade、但 bot3 尚未升级”的对象。
- `Rank 431` 目前还没有到 `P3`：它刚完成 first verdict，仍需那唯一一次 follow-up 来回答 `rolling admission + maker fill realism` 是否通过；因此本轮不存在需要 bot2 直接强推到 `P3 / Paper launch queue` 的候选。

## Tail step status
- homepage publish 需作为独立命令尝试：`bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`
- email notify 需作为独立命令尝试：`python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot2-review] Rank431 锁定 survivor 优先于新 intake" --body-file /root/clawd/jerry/momentum/research/strategy_review/2026-04-21_0903_strategy-review.md`
- 若 publish 失败，按 policy 记为非阻断尾部失败，不回滚本轮 state/log；email 若失败，也只记通知失败，不回滚本轮结论。