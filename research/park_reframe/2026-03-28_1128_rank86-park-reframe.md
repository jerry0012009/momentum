# 2026-03-28 11:28 UTC｜bot6 park-reframe｜Rank 86

## 0) 本轮选择
- 按当前轮转，本轮回到 `Rank 50+` 段处理 1 条 parked rank。
- 选定：`Rank 86 / SignalPro penetration×ATR admission`。
- 选择原因：
  1. 近 7 天 `bot6` 尚未复盘过 `Rank 86`；
  2. 原始 park 原因很集中，主要是 **shared admission gate 在时间切片上站不住**；
  3. 之后出现了直接相关的新旁证：
     - `research/quant_digests/2026-03-22_0858_breakout-bar-conviction-gate.md`
     - `research/quant_digests/2026-03-23_0058_donchian-strength-short-admission-not-shared-gate.md`
  4. 这两条新证据刚好能回答：`penetration / ATR` 主题到底该彻底放弃，还是还能从原 Rank 86 里诚实抽出一条更窄的新假设。

## 1) 原 Rank 为什么 park？
原始 authoritative 证据见：
- `research/optimization_loop/2026-03-19_0940_rank86-signalpro-intake.md`
- `research/optimization_loop/2026-03-19_1011_rank86-clean-replication-keep-p1.md`
- `research/optimization_loop/2026-03-19_1037_rank86-time-stability-park.md`

原 Rank 86 被 park 的核心原因很明确：
- 它把 `penetration / ATR` 写成 **三条收口线共用的 shared admission gate**；
- 最小 clean replication 虽然一度在 pooled summary 上留下轻微改善，但改善主要集中在局部 pocket；
- 真正决定命运的时间稳定性检查里，这条线 **三桶不稳**：
  - `ema_psar_follow_short + pen_plus_atr`：前两桶略正，后桶重新转负；
  - `fib_retest_short + pen_plus_atr`：明显更像前段 pocket，而不是跨时间稳定的 shared gate；
  - `breakout_short + pen_plus_atr`：整体仍偏弱；
- 因此原 verdict 必须保留：
  - **把 penetration×ATR 当成 15m 全 desk shared admission gate，这条路已经被审计消费。**

## 2) 它更像 hard park 还是 soft park？
- **本轮判断：`soft park`，但偏硬。**

为什么不是 hard park：
- 被否掉的主要是 **角色层级**，不是变量本身；
- `penetration`、`ATR expansion` 这组信息并没有完全失效，只是 shared 写法过宽。

为什么又偏硬：
- 一旦继续沿原 Rank 86 的 shared-gate 方向续命，很容易再次回到“局部 pocket + 切样本美化”；
- 原始 clean replication 已经说明：这条线并不能诚实地同时服务 `breakout_short / Fib / EMA` 三条 lane。

## 3) 有没有“可救信号”？
- **有。**

但可救信号不是“把 shared gate 再调细一点”，而是：
- `2026-03-23_0058_donchian-strength-short-admission-not-shared-gate.md` 已直接给出更诚实的读法：
  - `penetration / ATR` 更像 **`breakout-short` 的 short-side admission / follow-up score**；
  - 不适合镜像扩展到 Fib / EMA long，也不该继续写成 shared conviction gate。
- `2026-03-22_0858_breakout-bar-conviction-gate.md` 则提供了相同方向的辅助证据：
  - “破得够不够像真突破”更像 breakout 事件本身的便宜判决层，而不是全 desk 通用 hard gate。

所以，真正留下来的残余信息不是：
- “原 Rank 86 还差一点就能救活”，

而是：
- “原 Rank 86 的变量主题仍有价值，但只适合被收缩成更窄、更 setup-specific 的 short admission 层”。

## 4) 最值得改的唯一一刀是什么？
- **唯一值得保留的一刀：把 `penetration×ATR shared admission gate` 改写成 `breakout-short 专用的 short-side admission score / veto`。**

更具体地说：
- 不再把它接到 `Fib retest_hold` 与 `EMA/PSAR continuation`；
- 只在 `breakout-short` 事件已经触发后，额外计算 `penetration / ATR`；
- 第一刀先做最便宜的 strict A/B：
  - `baseline breakout-short`
  - `breakout-short + short_only_penetration_threshold`
- 不顺手加入第二轴（如 `Donchian width`、`body%/CLV`、新 exit、sizing 多档、second-layer regime）。

## 5) 是否值得形成新的 derived hypothesis？
- **本轮结论：`derived_hypothesis_drafted`。**

理由：
1. 不推翻原 park：原 Rank 86 作为 shared gate 的失败结论完整保留；
2. 新证据给出的不是泛泛“也许还能再试”，而是非常明确的单轴收缩：
   - 从 `shared gate` → `breakout-short specific short admission score`；
3. 这条轴没有被现有 `Rank 30b / 31b / 25c / 14b` 等提案直接吸收；
4. 写成 queue-only draft 后，`bot2` 在 fresh intake 不足时可以很容易判断：
   - 是否值得给它一轮 `source intake / clean replication next`。

## 6) Proposed derived hypothesis（queue-only draft）
- `proposed_rank`: `Rank 86b`
- `source_rank`: `Rank 86`
- `single modification axis`: `demote penetration×ATR from a shared admission gate into a breakout-short-specific short-side admission score / veto`
- `trade on`:
  - 不改 `breakout-short` 原始事件定义；
  - 只有当 `breakout-short` 已触发时，才额外计算最小版 `penetration_strength = (channel_edge - close) / ATR`（short 镜像口径）；
  - 第一轮优先只测 `baseline` vs `threshold_veto`（如 `strength >= 0.2 / 0.4 / 0.6` 的 frozen grid），按 `next-bar open + no-overlap`；
  - 只接 short lane，不接 `Fib / EMA`，不加 second-layer score。
- `trade off`:
  - 放弃“penetration×ATR 是三条收口线共用 admission layer”的原 Rank 86 读法；
  - 代价是：它不再是 shared gate，而且阈值改善可能仍然只是靠砍掉 weak shorts 美化；因此第一轮必须 strict A/B，并报告 `trade_retention`、`post-cost avg pnl`、`continue vs fail spread`，不能顺手偷带新 exit / 新 regime / candle-quality 第二轴。
- `why now`:
  - 原 Rank 86 已把 shared 写法时间不稳这一点审计清楚；
  - 但 2026-03-23 新 digest 又明确指出 `penetration / ATR` 的残余价值更像 `breakout-short` 专用 short admission，而不是 shared conviction gate；
  - 现在形成 `Rank 86b`，既保留原审计意义，也把唯一还值得测的一刀压缩成 bot2 可直接判断的短提案。
- `suggested_initial_state`: `source intake / clean replication next`

## 7) 本轮回答（按 brief）
- 原 rank 为什么 park？
  - 因为 shared gate 读法在时间切片上站不住，局部 pocket 改善不足以支撑全 desk 共用 admission 层。
- 它更像 hard park 还是 soft park？
  - `soft park`，但偏硬。
- 有没有“可救信号”？
  - 有；`penetration / ATR` 仍有信息，但只更像 `breakout-short` short-side admission score。
- 最值得改的唯一一刀是什么？
  - 从 `shared gate` 收缩成 `breakout-short-specific short admission / veto`。
- 是否值得形成新的 derived hypothesis？
  - 值得；本轮定为 `derived_hypothesis_drafted`，提案名 `Rank 86b`。

## 8) 本轮结论
- `derived_hypothesis_drafted`
- 补充口径：
  - **原 `Rank 86` 的 `park` 维持不变；**
  - 新增的只是 queue-only 的窄派生：`Rank 86b`。

## 9) 文件动作
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`

## 10) commit
- 本轮默认不做 commit。
- 原因：只做最小必要文档改动，且避免混入无关脏文件。
