# 2026-03-22 18:39 UTC · Rank 15 park reframe review (revisit)

## Scope
- Source rank: `Rank 15 / support-resistance regime-switch confirmation gate`
- Original authoritative verdict stays: `park / evidence pool`
- This round only asks: **在不推翻原 park 的前提下，Rank 15 是否值得派生出 1 条新的窄 reframe hypothesis**

## Why revisit Rank 15 (7-day rule note)
- `Rank 15` 上次已在 `2026-03-18 04:29 UTC` 做过 park-reframe，且结论是 `keep_park`。
- 按 7-day 规则，本应优先换别的 rank；但当前 `Rank 1~37` 的 parked 项在最近几天已基本轮过一遍，`Rank 15` 仍属于本轮转到的低频复核位，且它也是早期 `support/resistance` 线里最接近“看起来像还能再救一刀”的项目之一。
- 本轮复核的重点不是重开它，而是确认：**最近新增的 overlay / veto 类证据，是否真的给了 Rank 15 一个尚未被相邻分支消费掉的单轴新写法。**

## Read set
- required:
  - `docs/TODO.md`
  - `docs/PARK_REFRAME_QUEUE.md`
  - `docs/RECENT_PAPER_SEEDS.md`
  - `research/quant_digests/INDEX.md`
  - `research/park_reframe/INDEX.md`
- needed evidence:
  - `research/optimization_loop/2026-03-17_0126_rank15-clean-replication-park.md`
  - `research/park_reframe/2026-03-18_0429_rank15-park-reframe.md`
  - `reports/artifacts/scout_sr_regime_switch_15m/overall_summary.csv`
  - `reports/artifacts/scout_sr_regime_switch_15m/time_stability_drycheck.csv`
  - `reports/artifacts/scout_sr_regime_switch_15m/parameter_stability_drycheck.csv`
  - `reports/artifacts/scout_sr_regime_switch_15m/cross_asset_stability_drycheck.csv`
  - `reports/artifacts/scout_sr_regime_switch_15m/cost_trade_stability_drycheck.csv`
  - recent side evidence checked for overlap:
    - `research/quant_digests/2026-03-22_1826_longshort-crowding-gap-asymmetric-overlay.md`

---

## 1) 原 rank 为什么 park？
Rank 15 原始写法是 **support/resistance regime-switch confirmation gate**：从 `touch_or_cross` 出发，再往 `confirm1/2of3 outside`、`retest_hold_reclaim` 递进，想证明“加确认后，S/R regime switch 能变成可交易 setup”。

原始 park 理由仍然很清楚：
- 最不差主变体是 `retest_hold_reclaim @ 6bps/side`，但仍然只是 **少亏，不是存活**：
  - `mean_total_return ≈ -1.94%`
  - `positive_asset_ratio = 1/3`
  - `mean_trades = 13`
  - `mean_no_trade_ratio ≈ 81.73%`
- 四项轻稳定性检查继续一起 fail：
  - 时间稳定性：`1/3 positive buckets`
  - 参数稳定性：`0/5 positive neighbors`
  - 跨标的稳定性：`1/3 assets positive`
  - 成本稳定性：`0/4 cost levels positive`（`20bps ≈ -5.45%`）

=> 所以原 park 的审计意义不能动：**Rank 15 已经证明“加一层 S/R confirm/retest”并不足以把这条线救成可入板候选。**

## 2) 它更像 hard park 还是 soft park？
**偏 hard park。**

不是因为数值最差，而是因为它的失败形状已经比较“用尽了自然写法”：
- 放松一点，容易把噪音带回来；
- 收紧一点，又迅速退化成高 no-trade 的稀薄 pocket；
- 而且更像的旁支改写（zone / context / overlay）在相邻 ranks 里已经被消费过不少。

更直白地说：
- 原 Rank 15 不是“只差一个诚实小修补”；
- 它更像“最自然的 confirmation 改写已经试得差不多，剩下再改很容易滑向换壳续命”。

## 3) 有没有“可救信号”？
**只有很弱的可救信号，不足以单独再派生。**

弱信号在于：
- `retest_hold_reclaim` 确实比 `touch_or_cross`、`confirm1/2of3 outside` 少亏；
- 这说明“确认层”方向本身不是纯错。

但它仍不够升级成新的 reframe，原因有三层：
1. 这个 pocket 主要表现为 **少亏 + 少做**，而不是跨时间/参数/资产的稳定存活；
2. 最近新增证据里，更有价值的是 `crowding gap` 这类 **shared risk overlay** 读法，但那种变量并不是 Rank 15 这个 S/R regime-switch 主题的自然单轴延伸；
3. 若硬把 Rank 15 继续往 overlay 化改写，很容易和已存在的 `Rank 12b / 9b / 21b / 25b` 这批“把原始策略降级成 shared gate/overlay”的提案重叠，失去它自己的独立主题辨识度。

=> 本轮结论：**没有看到新的、独立且足够诚实的 salvage signal。**

## 4) 最值得改的唯一一刀是什么？
**本轮没有足够诚实的唯一一刀。**

表面上最像的方向有两种：
- 把单线式 `retest_hold` 继续改成更宽的 zone / context 表达；
- 把它从 standalone confirmation 改写成 shared veto / overlay。

但这两刀现在都不够干净：
- 第一刀本质上已被相邻 `support/resistance zone` 路线消费过；
- 第二刀虽然方向上“像现在 desk 常见答案”，但会把 Rank 15 的主题冲淡成泛用 overlay，和现有 queue 中多条派生假设高度重叠，不再是一个值得单独保留的新 hypothesis。

所以本轮最诚实的判断不是再发明一个 `Rank 15b`，而是承认：**当前没有剩下一条没被消费、且只改 1 轴的自然切口。**

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论：`keep_park`。**

原因：
- 原始 `park` 结论仍然有效，而且审计意义明确；
- 没有新的、能独立站住的单轴修改；
- 最近新增的 overlay 类证据更适合服务已冻结的 breakout / Fib / EMA-PSAR 主线，而不是给 Rank 15 再派生一个新壳。

---

## Final verdict for this round
- `verdict`: `keep_park`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `hard park`

## Minimal audit note
本轮不重开 `Rank 15`，也不推翻原 park。
本轮只确认一件事：**尽管 Rank 15 看起来像“确认层再修一点也许能救”，但截至目前，新的窄 reframe 仍不够诚实；最自然的近邻修改轴已经被相邻 S/R / regime / overlay 证据基本消费。**

## Git
- 本轮只做最小必要文档改动；不做 commit（工作区存在大量无关脏文件）。
