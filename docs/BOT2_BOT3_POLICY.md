# BOT2/BOT3 POLICY（manual-only）

> 这是 **固定 policy**。默认只允许人工修改。
> bot2 / bot3 **不得**在自动运行中改写本文件、相关 brief / operating card / cron prompt、或借日志倒推改 policy。
>
> **权威入口约定：**
> - 固定规则唯一来源：`docs/BOT2_BOT3_POLICY.md`
> - 运行状态唯一来源：`docs/BOT2_BOT3_STATE.md`
> - live cron payload 模板唯一来源：
>   - `docs/AUTO_OPTIMIZATION_CRON_PROMPT.txt`（bot3）
>   - `docs/BOT2_STRATEGY_REVIEW_CRON_PROMPT.txt`（bot2）
> - `docs/TODO.md` 只作 human-facing 项目板，不是 bot2 / bot3 的调度依据。
> - `docs/ROADMAP.md`、`docs/TODO_ARCHIVE_2026-03-24.md` 与旧报告只作长期/历史参考，不参与当前调度。

## 1) 当前唯一目标
1. 持续 intake 新策略 / 新论文 / 新 repo / 新 alpha；
2. 用最小但诚实的验证，快速回答它靠不靠谱；
3. 把真正存活的候选推进到 `P2 / pre-paper`，再推进到 `P3 / Paper launch queue`；
4. 完成 `P3 -> handoff` 后，默认先把对象推进到最小 `paper launch wiring`：必须包含 dedicated runner、scheduler 与首跑验证；只有 wiring 完成并写回 runtime 后，才默认退出 bot2 / bot3 责任范围。

## 2) 默认不做的事
- generic autonomous paper routine monitoring（但对已进入 `P3 / Paper launch queue` 且当前被认领为接线动作的对象，允许且要求完成 dedicated runner + scheduler + first verified run；wiring 完成后再由 dedicated runner/offload 层承担 routine refresh）
- interrupt / reserve / reserve watch
- diagnostic anchor / compare anchor
- tiny-live / live-shadow / routing dry-run / parity / continuity
- 为旧候选反复补不改变 verdict 的 compare / wording

## 3) 允许 bot2 / bot3 使用的运行槽位（固定）
只有 4 个：
1. `Paper launch queue`
2. `Fresh intake slot`
3. `Surviving candidate slot`
4. `Active P2 slot`

除此之外的旧候选，一律在 `Background pool`。

## 4) 硬定义
### Fresh intake
- 本轮新认领、此前不在当前运行槽位里的候选。
- 默认优先级最高。

### Surviving candidate
- **只能是上一条 fresh intake**。
- 最多只允许 **1 次** 最小 decisive follow-up。
- 这 1 次之后若仍未升级到 `P2`，默认移入 `Background pool`。

### Active P2
- 当前最接近 `Paper launch queue` 的候选。
- 默认同一时刻只保留 **1 条 active P2**；没有就写 `none`。
- `P2` 的默认目标不是长期停留，而是尽快完成一次 admission 判断：更偏向 `P3 / P1 / P0` 三选一。
- `P2` 的 admission 默认至少要覆盖这 5 类维度：
  1. `effectiveness / expected return`（含成本后口径）
  2. `cross-asset stability`
  3. `time stability`
  4. `parameter stability`
  5. `honesty / execution realism`（lookahead / repaint / leakage / friction realism）
- 若 admission 已基本补齐，或对象已经表现出“足够值得 paper trade、比较可能成型”，默认应更偏向 `P3`，而不是继续无限加检验项。
- `P2 -> P1` 不是常规退路，只在**存在明确 re-scope / re-spec 方向**时允许：
  - 例如改 `scope`、改 `regime`、改 `entry/exit`、改 `asset subset`、改 `execution assumption`
  - 不能只是“再看看 / 再补一点稳定性 / 再测一次”
- 同一策略默认**只允许 1 次**这样的 `P2 -> P1` 回退；若重新回到 `P2` 后仍不过关，默认更偏向 `P0`，除非用户明确要求 reopen。

### Background pool
- 历史 `P0/P1`、旧 rank、旧 compare/anchor/reserve 类对象都在这里。
- **不得自动回到前排**。
- 只有用户明确要求 `reopen` 某条旧候选时，才允许重新进入运行槽位。
- `Background pool guard` 默认只是**隐式护栏检查**：用于确认旧对象没有因为“最近日志很多 / artifact 很多 / 页面很多”而被误拉回前排。
- 默认**不要**把 `Background pool guard` 单独写成一个 `cycle_plan` 小点；只有在以下情况之一成立时，才允许把它显式排进当前轮：
  1. 已出现疑似自动 reopen / 槽位污染；
  2. 刚完成 `P3 handoff / sidecar offload / 前排对象切换`，需要做 **1 次** 收口巡检；
  3. 用户明确要求审计当前系统是否跑偏。

### Rank identity
- 任何 `fresh intake` 一旦得到 `keep_P1` 或更高 verdict，必须获得一个唯一的正式 `Rank` 编号。
- 任何进入 `Surviving candidate slot`、`Active P2 slot`、`Paper launch queue` 的对象，都必须已经带有 `Rank`。
- `Rank` 是对象的 durable identity；repo 名、论文名、作者名只作为 alias，不得替代正式 rank。
- bot2 若发现前排对象无 rank，必须先补下一个未使用的整数 `Rank`，再重写 `BOT2_BOT3_STATE.md` 与 `cycle_plan`。
- bot3 若把 fresh intake 推进到 `keep_P1 / P2 / P3`，不得以无 rank 状态结束本轮；必须先写出正式 rank 再收工。

## 5) cycle_plan（bot2 给 bot3 的当前轮小步列表）
- `cycle_plan` 写在 `BOT2_BOT3_STATE.md`。
- 它是 **bot2 当前这一轮** 给 bot3 的结构化执行列表，不是长期 backlog。
- bot2 必须先按 authoritative priority ladder 从高到低扫描当前所有合法动作，再把**具体值得做的任务**填入本轮预算；不要输出抽象模板句子、空占位、或没有具体对象的泛任务。
- 默认写 **4 项**；必要时可写 **3~5 项**，且**前两项必须是会产生真实推进的动作**。
- 每一项只允许包含：
  - `target`
  - `action`
  - `success_criterion`
  - `result`
  - `status`
- `result` 必须是一句会改变系统认知的话，而不是空泛进度描述。
  - 好例子：
    - `Rank 152：缩版 first verdict 完成，保持 P1，不升 P2`
    - `market risk-on/off：完成 clean-room spec，进入 P1`
    - `Rank 151：admission passed，从 P2 升到 P3`
    - `Rank 145：证据不足，退回 background pool`
    - `Rank 158：P2 admission 未过，但已明确改成 ETH+SOL-only scope，回到 P1 做一次 re-scope 检查`
- `Paper launch queue = none`、`Active P2 = none` 这类**空槽确认**默认属于隐式状态检查，不应占用 bot3 的默认执行轮次；只有在刚发生 handoff / sidecar offload / 槽位污染怀疑时，才允许显式写成一个小点。
- `status` 只允许：
  - `pending`
  - `done`
  - `blocked`

## 6) bot2 默认排班顺序（authoritative）
当 bot2 重排当前轮 `cycle_plan` 时，默认按下面顺序思考：
1. **`P3 / Paper launch queue` 最小接线与 handoff（必须含 runner script、scheduler、首跑验证）**
2. **`P2 / Active P2` 的 admission / promote / park 决策**
3. **`P1 / Surviving candidate` 的那唯一一次便宜诚实检查**
4. **新的 `fresh intake`**
5. **只有当前前排链条已诚实收口后，才继续补更多 `fresh intake`**
6. **`P0 / Background pool` 只保留证据，不占默认主资源**

补充约束：
- **已有前排对象的收口，优先级永远高于新的发现。** 只要当前存在合法 `P3 / Active P2 / Surviving candidate` 动作，bot2 就不得把新的 `fresh intake` 排到它前面。
- 只有当 `P3 / P2 / P1` 都没有真实可执行动作，或它们已经在当前轮前部被诚实排入并等待 bot3 依次执行时，bot2 才能用剩余预算补新的 `fresh intake`。
- 一旦进入这个分支，bot2 **必须直接指定至少 1 条新的 fresh intake**，不得只写“切回 fresh intake”而不写对象；若预算仍有空位、且当前前排链条已诚实收口，也可以继续补其他具体 intake 对象。
- 新 fresh intake 的默认来源优先级：
  1. 最近新的 strategy repo / paper / alpha report
  2. `research/park_reframe/INDEX.md` 中的 `derived_hypothesis_drafted` 或 `soft_reframe_candidate`
  3. 其他最近 digest / literature shortlist
- 任何 `fresh intake` 一旦首判为 `keep_P1`，其唯一 `Surviving candidate` follow-up 在诚实收口前默认享有前排锁定权；bot2 不得让另一条新的 `keep_P1` 候选覆盖该 survivor 槽位。
- `Background pool guard` 默认作为隐式检查随当前轮排班一起被满足；若没有异常 reopen 风险，不要为了“证明 guard 仍然存在”而单独占用一个 bot3 轮次。
- 若某个 `P1` 已用完那唯一一次检查，bot2 默认应更偏向 `P2 / P0 / 切资源`，而不是继续拖长。
- 若某个 `P2` 连续 1~2 轮没有新增会改变级别的证据，bot2 默认应更偏向 `P3 / P1(仅在明确 re-scope 时) / P0`，而不是继续拖长。
- 若同一对象在进入 `P2` 后已经出现 **2 次连续 `keep_P2`**，则下一轮不得再安排第三次开放式 `keep_P2` admission；bot2 必须把该对象排成 **出口决策轮**，直接回答 `promote_P3 / drop_to_background / one-time P2->P1 re-scope` 三选一。
- 若上一轮 `P2` 小点的 evidence axis 与本轮候选 axis 相同，且上一轮没有造成层级变化，则默认视为低杠杆重复；bot2 不得继续按相同 axis 续写，除非能明确说明这是唯一剩余 blocker。
- 当某个 `P2` 已出现 2 次连续 `keep_P2` 时，`cycle_plan` 默认还应保留 **1 个 conditional fresh intake** 小点，避免前排被单一 `P2` 长时间独占。
- bot2 不得放任同一策略在 `P2 -> P1 -> P2 -> P1` 之间来回横跳；若已经发生过一次明确的 `P2 -> P1` re-scope 回退，则下一次 `P2` 失败默认更偏向 `P0`。

## 7) P2 -> P3 责任边界
### P3 handoff / launch wiring 的最低完成定义
- `handoff complete` 不是只写 queue-side 文档或 handoff packet；最低必须同时满足：
  1. dedicated runner script 已写出并落库；
  2. scheduler（`service/timer/cron` 之一）已安装并启用；
  3. 至少一次首跑验证成功，且产出 runtime artifact / status / ledger 之一；
  4. `BOT2_BOT3_STATE.md` 已明确写成 `connected_runner_live` 或同等语义，不能继续停留在模糊的 `queued_handoff_ready`。
- 因此，**写 runner 并运行** 本身就是 `P3 handoff / launch wiring` 的组成部分，不得再被表述成“queue 外部默认会自动发生的下游动作”。
- 若某个 `P3` 对象只有 handoff 文档、但还没有 runner / scheduler / 首跑验证，则默认仍视为 **接线未完成**；bot2 优先级上仍应把它排在 `Paper launch queue` 最前，而不是宣称已收口。

- **bot3 是 `P2 -> P3` 的主责执行者。** 当 bot3 正在执行 `P2 exit decision`，且结论已经达到“足够值得进入 paper trade / paper launch、比较有可能成型、无明显致命问题”时，bot3 应直接把对象升级到 `P3 / Paper launch queue`，不得因为还存在非致命不完美就继续拖在 `P2`。
- **bot2 是 `P2 -> P3` 的兜底裁判。** 若 bot2 在 desk review 中看到某个 `Active P2` 已经明显达到上述门槛，但 bot3 尚未升级，bot2 必须直接把 `state` 改写到 `P3 / handoff` 路径，不能把决定继续往后拖给 bot3；若对象已在 `P3` 但还没有 runner / scheduler / 首跑验证，bot2 也必须把该对象继续排成 `P3 launch wiring`，直到接线完成。
- 为避免互相甩锅：bot3 不得把“应该升 P3”的决定留给下一轮 review；bot2 也不得把“已经够格的 P3”继续排成开放式研究。

## 8) bot2 权限边界
bot2 每轮可以做的，只有：
- 读取 fixed policy
- 读取 / 更新 `BOT2_BOT3_STATE.md`
- 基于最近结果重排当前轮 `cycle_plan`
- 生成 strategy-review 日志

bot2 **不可以**：
- 改写 policy / brief / operating card / cron prompt
- 擅自新增运行槽位
- 擅自把 background pool 里的旧候选拉回前排
- 因为“最近日志很多”就把老候选解释成当前主线

## 9) bot3 兜底规则
如果当前 `state` 与本 policy 冲突，例如：
- `Surviving candidate` 不是上一条 fresh intake
- 某旧候选被自动拉出 `Background pool`
- 当前动作落到 interrupt / reserve / anchor / tiny-live
- 某 survivor 已超出 1 次 follow-up 预算

则 bot3 默认 **拒绝执行该歪路径**，直接回退到：
1. `Fresh intake`
2. 若有合规 `Active P2`，则做 `P2 admission`

## 10) 输出约束
- 内部日志：每轮都要有
- reader-facing 输出：只有出现以下之一时才强制要求
  - 新 intake
  - 新 verdict
  - 新层级变化（P1/P2/P3）
  - launch handoff 完成
- 若只是无效重读、无新结论或被 guard 拦下，允许只写内部日志，不强求再产一页新网页
