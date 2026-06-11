# 2026-04-07 04:20 UTC strategy review

## Scope
按 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md` 进行 40 分钟 desk review；本轮只重排 runtime state，不改 policy / brief / operating card / cron prompt。

## 先回答 4 个问题

### 1) `Paper launch queue` 是否非空？
**否。**

当前 `Paper launch queue.current_target = none`。`Rank 200 / 201 / 213 / 229 / 342` 都已经在 `connected_runner_live`，不是待接线队列成员；因此前排里没有需要继续做 `P3 launch wiring` 的对象。

### 2) 本轮 `fresh intake` 是什么？
**`research/quant_digests/2026-04-06_1020_volume-anomaly-bandfade-hmm-veto-alpha.md`。**

原因：当前不存在待接线 `P3`、也不存在 `Active P2`，但存在一个必须优先收口的 survivor（`Rank 354`）。按 policy，survivor 收口之后，fresh intake 才重新回到前排；在最近新 repo/paper/alpha 里，这条 `volume anomaly band-fade × HMM veto` 是最靠前、且还未被 first verdict 的具体对象。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得。**

上一条 fresh intake 是 `Rank 354 / BTC crowd-positioning fuel-cascade`，且当前已合法进入 `Surviving candidate slot`，`followup_budget_remaining = 1`。它之所以值得这唯一一次 follow-up，不是因为 README 收益看着亮眼，而是因为：

- 已经有独立 raw alpha 主语：`public positioning + OI -> squeeze/cascade/forced-liquidation fuel state`
- 数据口径公开可取，最小状态机已成形
- 唯一高杠杆问题很清楚：`PB14-L / PB12 / FLIQ-L` 中是否至少一个分支在诚实 `fee/slippage/funding` 口径下仍保留可迁移净边

这正符合 policy 对 survivor 唯一 follow-up 的定义：做一次最小 decisive check，然后直接决定 `promote_P2` 或 `background / P0`。

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**不存在。**

`Active P2 slot.current_target = none`。上一条 `Active P2`（`Rank 342`）已经在 2026-04-05 23:00 UTC 完成 `P2 -> P3` 出口决策，并在 2026-04-06 00:16 UTC 完成最小 wiring，正式进入 `connected_runner_live`。因此本轮没有任何对象停留在 `P2`。

## Rank/前排合法性检查
- `Surviving candidate slot = Rank 354`，有 rank，合法。
- `Paper launch queue.current_target = none`，无需补 rank。
- `Active P2 slot = none`，无需补 rank。
- 当前前排对象不存在“达到 keep_P1/P2/P3 但无正式 rank”的情况，因此本轮不需要补新 rank。

## 本轮排班判断
按 policy 默认顺序扫描：
1. `P3 handoff`：无待接线对象；跳过。
2. `P2 admission/promote/park`：无 `Active P2`；跳过。
3. `P1 survivor follow-up`：有，而且是当前最高优先级真实动作 → `Rank 354` 必须排第 1。
4. `fresh intake`：在 survivor 已诚实放到第 1 位后，用剩余预算补最近具体对象。

因此本轮将 `cycle_plan` 重写为：
1. `Rank 354 / BTC crowd-positioning fuel-cascade` survivor 唯一 follow-up，直接回答 `promote_P2` 还是 `background / P0`
2. `2026-04-06_1020_volume-anomaly-bandfade-hmm-veto-alpha.md` fresh intake
3. `2026-04-07_0333_crashtrim-volmanaged-xs-momentum-alpha.md` fresh intake
4. `2026-04-07_0241_halflife-kelly-coint-pairs-alpha.md` fresh intake

## 为什么不是别的排法
- 不能把新 intake 排到 `Rank 354` 前面：survivor 还没收口，前排锁定权仍在。
- 不能继续凭空写 `P3` 或 `P2` 动作：当前两个槽位都为空。
- 不能把 background pool 老对象拉回前排：policy 明确禁止自动 reopen。
- 不需要把 `Paper launch queue = none` / `Active P2 = none` 单独写成 cycle item：这些只是隐式状态检查，不占默认轮次。

## 运行态结论
本轮唯一需要写回的是 `cycle_plan` 重排；其余 runtime 槽位与 policy 一致，无需额外改写。

## 发布与通知
- 中文邮件已发送：主题 `[momentum-bot2-review] survivor收口优先，fresh intake后置`。
- 首页发布脚本已执行，但当前 cron 运行态无法使用 elevated 权限；脚本在 `sudo mkdir/install/chown` 步骤挂起后已终止，未能完成首页刷新。
