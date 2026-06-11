# Fresh intake log — major-lead first-slot return × follower close-slot continuation

- Time: 2026-04-07 18:40 UTC
- Target: `research/quant_digests/2026-04-07_1436_majorlead-closeslot-crossmarket-itsm-alpha.md`
- Slot before action: `Fresh intake`
- Action: first verdict

## What changed
`major-lead first-slot return × follower close-slot continuation` 已完成 first verdict：它没有提出独立于既有 `major-lead / leader-follower / cross-market ITSM` 家族的新 raw alpha 主语，核心仍是 `leader 先定方向、follower 在后段同向跟随`，只是把同一家族再次表述为 `session handoff / close-slot continuation`，因此本轮诚实收口为 `background / P0`，不进入 survivor，也不分配新 Rank。

## Why this is the right verdict
1. 这条 digest 直接复用了我们库里已存在的 2026-03-28 `leader-window-basket-itsm` 读法：主语仍是 `leader 首窗方向 -> basket / follower 尾窗同向`，并非新的 pocket。
2. 它的 crypto 翻译仍是标准 `major lead -> follower continuation`：只是在 `00:00 / 08:00 / 13:30 UTC` 这类 pseudo-session 锚点里观察同一家族的传播，而不是提出新的执行结构。
3. 文中虽然强调 `liquidity handoff / information continuity`，但这些更像已有 lead-lag 家族的条件说明或 filter 语言，不足以把对象升级成独立 raw alpha family。
4. 库里已经有 `leader-window basket ITSM`、`BTC shock -> alt follow-through`、`BTC tick impulse -> ADA catch-up` 等多条同家族对象；这篇没有压出新的可迁移 pocket、独立成本边界或新的可审计执行母板，因此不值得占用 survivor 资源。

## Runtime write-back
- `Fresh intake slot.latest_result` 更新为本对象的 `background / P0` 首判
- `Fresh intake slot.latest_result_record` 指向本日志
- `Background pool.latest_parked` 更新为本对象
- `Background pool.latest_parked_record` 指向本日志
- `cycle_plan` 第 1 条 `result/status` 回写为 `done`

## Reader-facing consequence
这条 digest 保留为 `major-lead / cross-market ITSM` 家族的参考证据，但不升级为独立前排候选，不进入 survivor，也不占用新的 Rank。