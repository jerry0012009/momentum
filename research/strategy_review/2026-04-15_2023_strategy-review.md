# bot2 strategy review — 2026-04-15 20:23 UTC

## 读取与证据
- policy: `docs/BOT2_BOT3_POLICY.md`
- runtime state: `docs/BOT2_BOT3_STATE.md`
- repo status: `git -C /root/clawd/jerry/momentum status --short`
- recent optimization loop（最新抽样）:
  - `2026-04-15_2018_item2_extremefunding_freshintake_background_p0.md`
  - `2026-04-15_1941_rank415_survivor_followup_drop_background.md`
  - `2026-04-15_1906_item3_btc_anchor_loserbasket_freshintake_keep_p1_rank415.md`
- recent strategy review:
  - `2026-04-15_1910_strategy-review.md`
  - `2026-04-15_1815_strategy-review.md`

## 本轮只回答 4 个问题
1. **`Paper launch queue` 是否非空？**
   - **是，非空**。`connected_runner_live` 仍包含多条已接线运行对象（含 Rank 200/201/.../405）。

2. **本轮 `fresh intake` 是什么？**
   - `research/quant_digests/2026-04-15_2010_copula-spreadpair-mispricing-alpha.md`（已写入 `Fresh intake slot.current_target`）。

3. **上一条 fresh intake 是否值得那唯一一次 follow-up？**
   - **不值得。**
   - 上一条 fresh intake（`2026-04-15_1148_extremefunding-directional-capture-alpha.md`）已首判直接收口 `background/P0`，未形成 `keep_P1` survivor，因此不存在也不应分配唯一 follow-up。

4. **当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？**
   - **不存在明确 `Active P2`**（`current_target=none`）。
   - 最近一次 P2 出口（Rank 414）已在前轮完成 `P2->P1 re-scope` 并回收到 background；本轮无待决 P2 出口。

## Rank 合规检查
- 前排对象检查：
  - `Paper launch queue`：均为已编号 rank
  - `Surviving candidate`：`none`
  - `Active P2`：`none`
- 未发现“前排对象无 rank”违规；本轮无需补号。

## 本轮 state 改写
已更新 `docs/BOT2_BOT3_STATE.md`：
- `Fresh intake slot` 切换到新对象：`2026-04-15_2010_copula-spreadpair-mispricing-alpha.md`（`status=pending`）
- 按 policy 默认顺序重写 `cycle_plan`（当前无 P3/P2/P1 可执行前排动作，故以 fresh intake 填充 4 项）：
  1) `2010 copula spread-pair mispricing` first-verdict
  2) `1930 liquidation stinkbid hard-expiry` first-verdict
  3) `1436 XS momentum top-quintile weekly rotation` conditional first-verdict
  4) `Rank 74 soft_reframe_candidate`（来自 park_reframe）conditional first-verdict
- 新项均满足：`result=none`、`status=pending`。

## P2->P3 兜底裁判结论
- 当前无 `Active P2`，不存在“已够 paper trade 但 bot3 未升级”的对象。
- 本轮不触发强制直推 `P3 / Paper launch queue`。

## 结论
- 当前前排链条（P3/P2/P1）已收口，排班按 policy 合规切回 fresh intake。
- 下一步执行重点：从 `2010` 与 `1930` 两个最新 alpha 开始，优先给出可升级/可淘汰的一跳结论。