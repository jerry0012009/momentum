# 2026-03-19 20:19 UTC — Rank 12 park reframe

- source rank: `Rank 12 / averaged support/resistance zone + context gate`
- current authoritative verdict in `docs/TODO.md`: `park / evidence pool`
- this round verdict: `derived_hypothesis_drafted`
- original park verdict kept: `yes`

## 1) 原 Rank 为什么会 park
原 Rank 12 被 park，不是因为“支撑阻力 zone 完全没信息”，而是因为它被写成了 **standalone averaged-zone breakout / retest + context entry** 之后，收益和稳定性都不够诚实：

- `2026-03-17 00:11 UTC` 的 clean replication 里，最不差的 `averaged_zone_context_gate` 在 `6bps/side` 下也只有 `mean_total_return≈-4.34%`、`positive_asset_ratio=1/3`；
- `Light Stability Pack` 四项一起 fail：
  - 时间稳定性 `0/3 positive buckets`
  - 参数稳定性 `0/5 configs positive`
  - 跨标的稳定性 `1/3 assets positive`
  - 成本/交易数稳定性 `0/4 cost levels positive`
- 换句话说，它作为 **独立 breakout / retest 触发骨架**，既没把 post-cost expectancy 拉回正，也没留下足够干净的 cross-asset / cross-parameter pocket。

所以原 rank 应该继续保留 `park`：被审计否掉的是“averaged zone + context 本身就是一条可独立交易的 15m alpha”。

## 2) 它更像 hard park 还是 soft park
我把它判成 **soft park**。

原因：
- hard fail 的是它当 **standalone entry skeleton** 的角色；
- 但原证据没有把“zone 质量 / level 持久性”这种更窄、更上层的语义消费干净；
- 同主题的新旁证刚好出现：`2026-03-19 19:12` 的 digest 把 S/R 重新收敛成 **volume-weighted persistence shared quality gate**，这和 Rank 12 的主题是同一条线，但角色更窄、也更贴 desk。

## 3) 有没有“可救信号”
有，但只剩 **窄角色层** 的可救信号：

1. 原 Rank 12 里最有信息量的部分，不是 `single_line_break`，而是更靠后的 `averaged_zone_context_gate`，说明“把线位改成 zone、再加一点上下文”至少比裸 breakout 更接近问题核心；
2. 原 rank 虽然总体仍负，但它更像是在提醒：**真正缺的不是再找一条更花的 zone entry，而是先判断这个 zone 本身值不值得尊重**；
3. 最新 digest `2026-03-19_1912_volume-weighted-sr-persistence-gate.md` 给出的正是同主题、单轴、且更贴当前三条主线的改写：
   - 先给 zone 打 `persistence / quality` 分层；
   - 再把它当 breakout-short / Fib retest_hold / EMA-PSAR 的 shared admission / veto layer；
   - 不再让 S/R zone 自己直接负责开仓。

所以可救信号不是“Rank 12 差一点就能升格”，而是：**zone 主题可能还留在上层质量 gate 有用，只是不该继续写成独立 entry alpha。**

## 4) 最值得改的唯一一刀
**唯一修改轴：把 Rank 12 从 standalone averaged support/resistance zone + context entry，降级成 `volume-weighted zone persistence` shared quality gate。**

只改角色，不改主题：
- 不重写成新的 trigger family；
- 不同时偷带新 exit / new regime matrix / new execution layer；
- 只回答一件事：`zone_persistence_score` 能不能作为 shared allow/deny / sizing gate，降低假突破 / 假守住的 admission 错误。

## 5) 是否值得形成新的 derived hypothesis
**值得。**

原因：
- 原 `park` 结论依旧成立，不需要推翻；
- 现在已经能把剩余信息量写成一条足够窄的单轴假设；
- 这条假设和原 Rank 12 保持同一主题，只改角色；
- bot2 后续在 fresh intake 不足时，可以直接判断要不要把它当成 `Rank 12b` 式的新候选。

## 6) Derived hypothesis draft（供 bot2 后续判断是否入板）
- proposed_rank: `Rank 12b`
- source_rank: `Rank 12`
- status: `derived_hypothesis_drafted`
- single modification axis: `demote standalone averaged support/resistance zone + context entry into a volume-weighted zone-persistence shared quality gate`
- trade on:
  - 不再根据 `averaged_zone_break / averaged_zone_retest / context_gate` 自己直接开仓；
  - 先在预先冻结的 swing / Fib / breakout anchor 上生成候选 zone，再计算最小版 `zone_persistence_score`：`touch_count_lookback`、`zone_volume_pct`、`zone_width_atr_norm`、`retest_survival_rate`；
  - 只把它当 shared allow/deny / sizing gate：
    - `Fib retest_hold` 与 `EMA/PSAR continuation` 优先在 `mid/high persistence` zone 放行；
    - `breakout-short` 遇到 `high persistence` zone 时默认需要额外 `retest fail + 2-close confirm` 才放行，否则 half-size / veto；
    - 第一轮优先只测 `baseline vs persistence gate`，不偷带第二层 score stack。
- trade off:
  - 放弃“averaged S/R zone + context 本身就是完整 entry alpha”的原 Rank 12 读法，换取更诚实的 shared quality gate 角色；
  - 代价是它不再是独立策略，而且若 persistence 阈值过严，可能只是靠砍交易数美化结果，因此第一轮必须只测 gate 本身，不偷带新 trigger / exit / multi-layer regime。
- why now:
  - 原 Rank 12 已把 standalone zone-entry 这条路审计得很清楚：post-cost 仍负，稳定性四项全 fail；
  - 但失败点更像“zone 主题被放在了错误的职责层”，而不是“支撑阻力质量信息彻底没价值”；
  - `2026-03-19 19:12` 的新 digest 正好把同主题收敛成一条单轴、可 bot2 直接判断的 shared quality gate，所以现在值得保留一条 `Rank 12b` 窄派生提案。
- suggested initial state: `source intake / clean replication next`

## 7) 本轮结论
- 原 Rank 12 为什么 park：作为 standalone averaged-zone breakout/retest entry，收益与稳定性都不够诚实；
- 它更像：`soft park`
- 可救信号：有，但只剩 `volume-weighted zone persistence` 这一条窄角色线；
- 最值得改的唯一一刀：**降级成 shared quality gate**；
- 本轮最终结论：`derived_hypothesis_drafted`

## 8) 文件与提交流程说明
- 本轮只更新 `research/park_reframe/INDEX.md`、`docs/PARK_REFRAME_QUEUE.md` 与本日志；
- 默认不改 `docs/TODO.md` 顶部排班；
- 本轮未做 git commit：`git status` 显示工作区存在大量与本轮无关的脏文件，当前不适合安全地 selective commit。
