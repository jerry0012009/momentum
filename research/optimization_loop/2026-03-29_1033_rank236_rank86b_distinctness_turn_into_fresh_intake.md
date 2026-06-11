# 2026-03-29 10:33 UTC — Rank 236 / Rank 86b distinctness check：转成正式 fresh intake

## 为什么这轮轮到它
- 按 `docs/BOT2_BOT3_STATE.md` 当前 `cycle_plan`，排在最前的 pending 小点是：
  - `research/park_reframe/2026-03-28_1128_rank86-park-reframe.md`
  - 任务：判断 `Rank 86b / breakout-short-specific short-side admission score-veto` 是否已经足够脱离旧 `Rank 86` 的 shared-gate 失败史，值得转成新的正式对象。
- 本轮严格只执行这一个小点，不改写排班顺序，也不额外展开 `Rank 96`。

## 读取的权威证据
1. `research/park_reframe/2026-03-28_1128_rank86-park-reframe.md`
2. `research/optimization_loop/2026-03-19_0940_rank86-signalpro-intake.md`
3. `research/optimization_loop/2026-03-19_1011_rank86-clean-replication-keep-p1.md`
4. `research/optimization_loop/2026-03-19_1037_rank86-time-stability-park.md`
5. `research/quant_digests/2026-03-23_0058_donchian-strength-short-admission-not-shared-gate.md`
6. `research/quant_digests/2026-03-22_0858_breakout-bar-conviction-gate.md`

## 本轮只回答一个问题
`Rank 86b` 是否已经是一个**足够独立、边界清楚、不会把旧 shared-gate 失败史偷渡回来**的新对象？

## 结论
- **结论：是，应该转成新的正式 fresh intake。**
- 正式编号：**`Rank 236 / breakout-short-specific short-side admission score-veto`**

## 为什么这次可以转正，而不是继续停在 park/reframe
### 1) 它和原 `Rank 86` 失败对象的主语已经变了
原 `Rank 86` 被 park 的原因不是“penetration / ATR 永远没用”，而是：
- 它被写成了 **`breakout_short + fib_retest_short + ema_psar_follow_short` 三条 lane 共用的 shared admission gate**；
- clean replication 后虽然局部 pocket 有改善，但时间切片不稳；
- 因而 **shared gate 这个角色定义** 已被审计失败。

`Rank 236` 不再主张 shared gate，而是明确收缩成：
- **只服务 `breakout-short`**；
- **只服务 short side**；
- **只做 admission score / veto**，不再伪装成全 desk 通用确认层。

这不是原对象的 wording 美化，而是对象边界本身换了：
`shared gate` → `breakout-short-specific short-side veto`。

### 2) 新旁证支持的正是这种“降级到 setup-specific”读法
`2026-03-23_0058_donchian-strength-short-admission-not-shared-gate.md` 给出的最关键结论是：
- `penetration / ATR` 在 15m 更像 **breakout-short 的 short-side admission / follow-up score**；
- 不该镜像扩展到 `Fib / EMA long`，也不该继续写成 shared conviction gate。

`2026-03-22_0858_breakout-bar-conviction-gate.md` 也在同一方向补强：
- breakout 发生当下的“破得够不够像真突破”，更像 **事件自身的便宜判决层**；
- 这种信息天然更适合接在 breakout 事件后，而不是升成全 desk 公共真理。

也就是说，新的证据不是“原 Rank 86 也许还能再救一点”，而是更明确地指出：
- **只剩一条值得测的窄刀：breakout-short 专用 short-side veto。**

### 3) 它和原失败史之间存在清楚的 trade-on / trade-off
`Rank 236` 的诚实定义已经足够清楚：
- `trade on`：`baseline breakout-short` 先触发，再额外读取 `penetration_strength = (channel_edge - close) / ATR`，只做 short-only 的阈值 veto / score。
- `trade off`：放弃原来“对 Fib / EMA 也成立”“可以当 shared admission layer”的宽主张；第一轮禁止顺手叠 Donchian width / candle quality / exit / sizing 第二轴。

这意味着它不是“同一个对象换个说法继续续命”，而是一个**约束更严、 claim 更窄、可被单轮 clean replication 直接证伪**的新 intake。

### 4) 它还没有被别的前排对象直接吸收
从当前引用材料看，`Rank 236` 的对象边界是：
- setup-specific：`breakout-short`
- side-specific：`short-only`
- role-specific：`admission score / veto`
- variable-specific：`penetration / ATR`

它不同于：
- 泛化的 breakout bar quality / candle-quality conviction gate；
- shared gate 类型对象；
- 原 `Rank 86` 的跨 setup 宽写法。

因此现在把它独立编号，比继续挂在 park/reframe 里更诚实，也更利于 bot2 后续只给它一轮最小 clean replication。

## 本轮 hard verdict
- **`Rank 236 / breakout-short-specific short-side admission score-veto`：转成新的正式 fresh intake**
- 不是 `keep_P1` / `P2` / `P3`；只是把 queue-only draft 正式转成可执行的新对象。
- 对旧对象的约束保持不变：
  - **`Rank 86` 继续维持 park/background，不得因此自动 reopen。**

## 对 runtime 的直接影响
1. 当前 pending 小点 3 应写成 `done`。
2. `Fresh intake slot` 应切换到：`Rank 236 / breakout-short-specific short-side admission score-veto`。
3. `Fresh intake slot.latest_result` 应明确：
   - 这条对象之所以值得正式 intake，不是因为原 `Rank 86` 被翻案；
   - 而是因为唯一存活的残余信息已经被诚实压缩成 `breakout-short` 专用、`short-only`、`penetration/ATR veto` 这一条单轴新对象。
4. `Surviving candidate slot` 与 `Active P2 slot` 本轮不改；因为本轮只做 distinctness / fresh-intake 转正，不做新对象的 first verdict。

## 备注
- 本轮没有重排 `cycle_plan`。
- 本轮没有为 `Rank 236` 做 clean replication，只完成“是否转成正式对象”的 distinctness 判决。
- 下一个 pending 小点仍是 `Rank 96` 的 conditional fresh intake distinctness check。