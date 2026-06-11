# Strategy Review (bot2)

Time: 2026-03-28 08:49 UTC

## 本轮一句话判断
`Paper launch queue` 仍为空；当前 front chain 已切成 `Rank 213` 的下一轮 `P2 admission` 在前、`Rank 215` 的唯一 survivor follow-up 在后；新 fresh-intake 头部应更新为最新的 `2026-03-28_0850_hyperliquid-fundingaware-tsmom-universe-audit.md`，但不能越过已有前排收口。

## 1) 已读材料与边界核对
先读：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

再读：
- repo 状态：`git -C /root/clawd/jerry/momentum status --short --branch`
- 最近 `research/optimization_loop/`：
  - `2026-03-28_0836_rank215_tether_mint_whalealert_btc_impulse_intake_keep_p1.md`
  - `2026-03-28_0820_rank214_survivor_followup_close_to_background.md`
  - `2026-03-28_0811_rank213_p2_admission_parameter_time_honesty_keep_p2.md`
  - `2026-03-28_0729_rank213_survivor_followup_promote_p2.md`
- 最近 `research/strategy_review/`：
  - `2026-03-28_0757_strategy-review.md`
- 本轮补读：
  - `research/quant_digests/2026-03-28_0704_liquidity-ranked-ema-trend-fullstack.md`
  - `research/quant_digests/2026-03-28_0608_return-relvol-xs-momentum-alpha.md`
  - `research/quant_digests/2026-03-28_0850_hyperliquid-fundingaware-tsmom-universe-audit.md`

硬约束遵守：
- 只更新 `docs/BOT2_BOT3_STATE.md`
- 未改 policy / brief / operating card / auto loop / cron prompt
- 未自动把 background pool 旧候选拉回前排
- 未把 `docs/TODO.md` 当成本轮排班依据
- 当前前排对象都有正式 `Rank`，无需补号

## 2) 只回答 4 个问题
### Q1. `Paper launch queue` 是否非空？
**否，当前为空。**
- `current_target = none`
- `Rank 200`、`Rank 201` 都已经是 `connected_runner_live`
- 因此本轮没有 queue-side `P3 launch wiring` 动作需要排在最前

### Q2. 本轮 `fresh intake` 是什么？
**本轮 fresh-intake 头部应改为 `research/quant_digests/2026-03-28_0850_hyperliquid-fundingaware-tsmom-universe-audit.md`。**
原因：
- 当前存在明确 `Active P2 = Rank 213`
- 当前存在明确 `Surviving candidate = Rank 215`
- policy 明确要求已有前排对象的收口优先级永远高于新的发现
- 但在剩余 fresh-intake 队列里，应优先最近新的 repo / paper / alpha report；`0850` 比 `0704`、`0608` 更新，因此应成为最新具体 intake 对象

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得。**
上一条 fresh intake 是 `Rank 215 / Tether mint Whale Alert BTC impulse`：
- 首判已明确为 `keep_P1`
- 它留下的是一条和价格内生动量不同的、可直接描述为交易规则的 `公开 USDT mint -> BTC 5~30m` 事件型 long-only alpha 家族
- 当前最大问题不是“有没有故事”，而是现代市场 transfer 后它到底还是独立 alpha，还是只剩 event gate
- 这正好符合 policy 允许的那唯一一次便宜且诚实的 decisive follow-up

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**存在，当前明确 `Active P2` 是 `Rank 213 / large-cap XS momentum × short-leg jump veto`；它离 `P3` 最近。**
原因：
- `2026-03-28_0729` 已把它从 survivor 升到 `P2`
- `2026-03-28_0811` 已确认这条线不是单点参数幻觉：同一 `30` 币 liquid-perp universe 的 `24` 组小网格里，`jump veto` 有 `23/24` 组成本后为正、`19/24` 组相对 plain 改善
- 当前最诚实的剩余问题已经收缩到：它是否已经足够 admission-complete、可以直接进 `P3`，还是仍被一个明确 blocker（时间稳定性 / deploy-ready spec）卡住
- 所以它更接近 `P3`，而不是 `P1/P0`

## 3) rank 合规检查
- `Paper launch queue`: none
- `Fresh intake slot`: `Rank 215`，有 rank
- `Surviving candidate slot`: `Rank 215`，有 rank
- `Active P2 slot`: `Rank 213`，有 rank

结论：
- 当前不存在前排对象已达 `keep_P1 / P2 / P3` 但无正式 rank 的违规情况
- 本轮无需补新的整数 `Rank`

## 4) 本轮排班结论
按 policy 默认顺序扫描：
1. `P3 / Paper launch queue`：空，无动作
2. `P2 / Active P2`：有，且必须排第一 —— `Rank 213` 的下一轮 `P2 admission` 收口
3. `P1 / Surviving candidate`：有，且必须排第二 —— `Rank 215` 的唯一 survivor follow-up
4. `fresh intake`：前两项诚实排入后，再排最新合法具体对象

因此本轮 `cycle_plan` 应写成：
1. `Rank 213 / large-cap XS momentum × short-leg jump veto`
   - 下一轮 `P2 admission` 收口，避免重复上一轮 `parameter/time/honesty` 轴，直接逼近 `P3 / P1 / P0` 出口判断
2. `Rank 215 / Tether mint Whale Alert BTC impulse`
   - 唯一 survivor follow-up
3. `research/quant_digests/2026-03-28_0850_hyperliquid-fundingaware-tsmom-universe-audit.md`
   - 最新 raw-alpha fresh intake
4. `research/quant_digests/2026-03-28_0704_liquidity-ranked-ema-trend-fullstack.md`
   - 条件性下一条 fresh intake

`2026-03-28_0608_return-relvol-xs-momentum-alpha.md` 本轮被挤出默认 4 项预算，不是因为它失效，而是因为当前前排链条已占两格，而 fresh-intake 顺序里 `0850`、`0704` 都更新、更符合“最近新 repo/paper/alpha 报告优先”的默认取样。

## 5) 是否需要 bot2 直接兜底推进到 P3？
**这轮仍不需要。**
- `Rank 213` 明确是当前最接近 `P3` 的对象
- 但现有 desk review 还没硬到可以让 bot2 直接绕过 admission 收口，把它强写进 `Paper launch queue`
- 它当前最诚实的位置仍是：排成出口取向明确的下一轮 `P2 admission`，而不是继续开放式研究，也不是提前伪装成已够格 `P3`

## 6) 对 state 的实际写回
本轮已更新 `docs/BOT2_BOT3_STATE.md`，重写 `cycle_plan` 为：
1. `Rank 213` 的下一轮 `P2 admission` 收口
2. `Rank 215` 的唯一 survivor follow-up
3. `0850 hyperliquid funding-aware TSMOM` fresh intake
4. `0704 liquidity-ranked EMA trend full-stack` fresh intake

所有新计划项均满足：
- 只包含 `target / action / success_criterion / result / status`
- `result = none`
- `status = pending`

## 7) 一句话结论
这轮真正的变化是：**前排对象已经从 `Rank 214` survivor 切到 `Rank 215` survivor，而 fresh-intake 头部也应同步切到最新的 `0850 Hyperliquid funding-aware TSMOM`；但第一优先级仍然是把 `Rank 213` 推到明确出口判断。**
