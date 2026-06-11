# 2026-03-27 21:02 UTC — Rank 12 park reframe review

- source rank: `Rank 12 / averaged support/resistance zone + context gate`
- current authoritative verdict in `docs/TODO.md`: `park / evidence pool`
- this round verdict: `keep_park`
- original park verdict kept: `yes`

## 1) 原 Rank 为什么会 park
原 Rank 12 被 park，不是因为“支撑阻力 zone 完全没信息”，而是因为它被写成 **standalone averaged-zone breakout / retest + context entry** 之后，收益和稳定性都不够诚实。

关键原始证据（`2026-03-17_0011_rank12-clean-replication-park.md`）：
- `winner_variant=averaged_zone_context_gate`
- `6bps/side` 下 `mean_total_return≈-4.34%`
- `positive_asset_ratio=1/3`
- Light Stability Pack 四项一起 fail：
  - 时间稳定性 `0/3 positive buckets`
  - 参数稳定性 `0/5 configs positive`
  - 跨标的稳定性 `1/3 assets positive`
  - 成本/交易数稳定性 `0/4 cost levels positive`

翻成人话：
- zone + context 比更裸的 line-break 版本“没那么差”；
- 但它仍然没把 post-cost expectancy 拉回正，也没留下足够干净的跨资产 / 跨参数 pocket；
- 所以原 `park` 结论必须保留：被否掉的是“averaged zone + context 本身就是一条可独立交易的 15m alpha”。

## 2) 它更像 hard park 还是 soft park
**更像 `soft park`，但这次比 2026-03-19 更偏硬一点。**

原因：
- 被否掉的是它作为 **standalone entry skeleton** 的角色，而不是 “S/R zone 主题完全没价值”；
- 但 2026-03-19 已经把它最自然、最诚实的一条残余信息量压缩成 `Rank 12b`：`volume-weighted zone persistence` shared quality gate；
- 过去 8 天里没有出现一条新的、足够独立的证据，能再从 Rank 12 身上切出第二条不重复的单轴。

所以它仍是 soft park，因为主题没死；但也更偏硬，因为 **唯一自然救法已经被 12b 消费掉**。

## 3) 有没有“可救信号”
**有，但不是新的。**

仍然成立的可救信号只有一条：
- zone 主题更像该被降级成 `quality / persistence gate`，而不是继续当 standalone trigger。

这条信号并不新：
- `2026-03-19_1912_volume-weighted-sr-persistence-gate.md` 已经把它写成 `volume-weighted zone persistence` shared quality gate；
- `docs/PARK_REFRAME_QUEUE.md` 中也已有 `Rank 12b`，而且角色、trade on / trade off、why now 都已经写清楚；
- 之后的新 `RECENT_PAPER_SEEDS.md` 与 `research/quant_digests/INDEX.md`，没有再出现一条更窄、且不和 `12b` 重叠的 S/R zone 新轴。

所以当前的“可救信号”不是“值得再派生一次”，而是：**继续承认 12b 已经吃掉了 Rank 12 剩余的唯一诚实残余。**

## 4) 最值得改的唯一一刀是什么
**唯一值得保留的一刀，仍然是：把 Rank 12 从 standalone averaged support/resistance zone + context entry，降级成 `volume-weighted zone persistence` shared quality gate。**

也就是说：
- 不再让 averaged zone 自己直接负责开仓；
- 改成给已有 breakout / Fib retest_hold / EMA-PSAR continuation 提供 allow/deny / sizing 质量层；
- 重点不是“再发明一个更花的 zone trigger”，而是先判断这个 zone 值不值得尊重。

但这刀 **已经存在**，就是 `Rank 12b`。本轮不诚实再写一个 `Rank 12c`。

## 5) 是否值得形成新的 derived hypothesis
**不值得。本轮结论：`keep_park`。**

原因：
1. 原 `park` 审计结论依旧成立，不需要推翻；
2. 唯一自然、单轴、且不推翻历史结论的改写，已经在 `Rank 12b` 中被完整记录；
3. 最近没有出现新的外部证据，足以支持一个不同于 `12b` 的第二条窄 reframe；
4. 若现在硬写 `Rank 12c`，大概率只是换一种措辞重复“zone quality / persistence gate”这同一刀。

## 6) 本轮最终回答
- 原 Rank 为什么 park：作为 standalone averaged-zone breakout/retest entry，收益与稳定性都不够诚实；
- 它更像：`soft park`，但比 2026-03-19 更偏硬，因为唯一自然救法已被 `12b` 消费；
- 可救信号：有，但不是新的，只剩 `zone persistence / quality gate` 这条已存在残余；
- 最值得改的唯一一刀：**仍是把它降级成 `volume-weighted zone persistence` shared quality gate**；
- 是否值得形成新的 derived hypothesis：**不值得**；
- 本轮最终结论：`keep_park`

## 7) Minimal audit note
本轮不是否定 `Rank 12b`，而是确认：
- `Rank 12` 的原始 park 仍然成立；
- `Rank 12b` 已经是这条线最诚实、最窄、且足够 bot2 直接判断是否入板的残余提案；
- 在没有新证据前，不应再从同一 source rank 继续派生新的 `12c`。

## 8) 文件与提交流程说明
- 本轮只更新 `research/park_reframe/INDEX.md`、`docs/PARK_REFRAME_QUEUE.md` 与本日志；
- 默认不改 `docs/TODO.md` 顶部排班；
- 本轮未做 git commit：工作区存在与本轮无关的脏文件，当前不适合安全地 selective commit。
