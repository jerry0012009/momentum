# Rank 21 park residual -> daily sentiment-extremity shared risk overlay stays park_reframe

- 时间：2026-03-30 02:53 UTC
- 当前执行小点：`Rank 21 park residual -> daily sentiment-extremity shared risk overlay`
- 对象主语锁定：`daily sentiment-extremity shared risk overlay`

## 本轮核对的直接依据
1. `docs/BOT2_BOT3_POLICY.md`
2. `docs/BOT2_BOT3_STATE.md`
3. `research/park_reframe/2026-03-20_0724_rank21-park-reframe.md`
4. `research/park_reframe/2026-03-28_1219_rank21-park-reframe.md`
5. `research/strategy_review/2026-03-30_0136_strategy-review.md`

## 本轮只回答的问题
`Rank 21b / daily sentiment-extremity shared risk overlay` 是否已经足够从原 `15m market risk-on/off gate` 的失败边界中独立出来，成为一条边界清楚、可单轮证伪、且不只是靠大幅砍单美化的 queue-facing 新对象。

## 直接结论
**还不够。继续留在 `park_reframe`，不进入前排。**

## 为什么这轮不能把它写成 fresh intake
### 1) 这条修改轴其实早已被写清
`Rank 21b` 的唯一改单轴在 `2026-03-20_0724_rank21-park-reframe.md` 就已经明确：
- 把 `standalone market risk-on/off regime gate`
- 降级成 `daily sentiment-extremity shared risk overlay`

这次轮到它，不是第一次发现新对象，而是要判断这条 residual 是否已获得足够新的、会改变层级的证据。当前答案是否定的。

### 2) 2026-03-28 的新增证据只是在强化“它是 overlay”，没有把它抬成独立对象
`2026-03-28_1219_rank21-park-reframe.md` 已经把新论文证据收口得很清楚：
- sentiment / risk-on-off 主题还活着；
- 但它更适合做上位 raw-alpha family 的 `gate / overlay`；
- 而不是自己成为 queue-facing standalone alpha 或 standalone admission gate。

也就是说，新证据的作用是**确认角色降级**，不是创造新 front-slot identity。

### 3) 目前没有看到“独立于上位 raw-alpha family”的最小可证伪 spec
要让它进入前排，至少得能回答：
- 它服务的是哪一条具体 raw-alpha family；
- overlay 只做什么（如 `size-down` / `stricter-confirm` / `veto`），不做什么；
- 它不是靠大幅砍单制造表面改善；
- 它与相邻的 low-frequency risk / sentiment overlay 提案边界如何切开。

当前材料还停留在主题层：`extremity` 值得当 overlay；但没有把“哪条上位 setup + 哪个最小 overlay 动作 + 怎样避免只靠砍单美化”压成一条新的 queue-facing 窄对象。

### 4) 因而它更像 `park residual note`，不是新的 front-slot candidate
在当前 policy 下，fresh intake 需要的是**单轮就能给硬结论的具体对象**。`Rank 21b` 现在仍更像：
- 对旧 `Rank 21` 的角色纠偏说明；
- 对其他 raw-alpha family 的低频 overlay 提示；
- 而不是一条已经能独立排进前排、并马上做最小 intake/证伪的对象。

## 会改变系统认知的一句话结果
`Rank 21 park residual -> daily sentiment-extremity shared risk overlay` 仍只是对原 `15m market risk-on/off gate` 的角色降级说明，尚未收敛成独立、可单轮证伪的 queue-facing 对象，因此继续留在 `park_reframe`，不进入前排。

## 本轮对 runtime 的影响
- `Fresh intake slot` 继续保持 `current_target: none`
- 仅将本轮 `cycle_plan` 对应小点收口为 `done`
- 不分配新 Rank，不触发层级迁移，不触发 P2/P3 相关动作

## Git
- 未提交。
- 原因：本轮仅做 runtime/log 收口。