# 2026-04-21 03:27 UTC · Rank 15 park reframe

## Selected rank
- `Rank 15 / support-resistance regime-switch confirmation`
- 本轮输出：`keep_park`
- 原始结论保留：`park / evidence pool`

## 为什么这轮看 Rank 15
- 按 `bot6` 规则，本轮只处理 1 条已 `park` rank。
- `Rank 15` 上一次 park-reframe 复盘是 `2026-04-14 00:09 UTC`，刚好已越过最近 `7` 天默认回避线。
- 这期间出现了新的更贴题旁证：
  - `research/quant_digests/2026-04-18_0049_auction-profile-poc-lvn-shell.md`
- 需要回答：这条新增 auction-structure 证据，是否足以把旧 `Rank 15` 推向一个诚实的窄 reframe hypothesis。

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- recent park-reframe references:
  - `research/park_reframe/2026-04-20_1934_rank3-park-reframe.md`
  - `research/park_reframe/2026-04-20_1241_rank6-park-reframe.md`
  - `research/park_reframe/2026-04-20_0155_rank37-park-reframe.md`
- source / prior rank evidence:
  - `research/optimization_loop/2026-03-17_0126_rank15-clean-replication-park.md`
  - `research/park_reframe/2026-04-14_0009_rank15-park-reframe.md`
- new evidence:
  - `research/quant_digests/2026-04-18_0049_auction-profile-poc-lvn-shell.md`

## 1) 原 rank 为什么 park？
原 `Rank 15` 被 park 的核心原因没有变化：
- clean replication 已把最自然的确认层变体都跑过：`touch_or_cross_baseline / confirm1_outside / confirm2of3_outside / retest_hold_reclaim`；
- 即便相对最不差的 `retest_hold_reclaim`，在 `6bps/side` 下也仍是：
  - `mean_total_return ≈ -1.94%`
  - `positive_asset_ratio = 1/3`
  - `mean_no_trade_ratio ≈ 81.73%`
- Light Stability Pack 四项一起硬 fail：
  - 时间稳定性 `1/3` positive buckets
  - 参数稳定性 `0/5` positive neighbors
  - 跨资产稳定性 `1/3` positive assets
  - 成本稳定性 `0/4` positive cost buckets

翻成人话：
- 问题不是“确认还不够细”；
- 而是把 `support/resistance + regime switch + confirmation` 写成一条 queue-facing 独立 setup，本身就太宽、太粗、也不够稳。

## 2) 它更像 hard park 还是 soft park？
**本轮判断：更像 `hard park`。**

原因：
1. 原 rank 最自然的确认层微调已经被 clean replication 消费掉；
2. 剩余价值更像 `anchor / zone / acceptance quality` 语义，而不像独立 entry alpha；
3. 新证据进一步证明 auction / profile 主题若还活着，也要落在更具体的结构宿主，而不是旧 `Rank 15` 这条泛 S/R regime-switch gate。

## 3) 有没有“可救信号”？
**有主题级可救信号，但仍不是旧 Rank 15 本体被救活。**

这轮新增的 `auction-profile / POC / LVN shell` 证据说明：
- 真正值得保留的是更具体的 auction-market 语言：
  - `value-area re-entry -> POC` 回归腿
  - `LVN traverse` 穿越腿
- 这些主语都已经是：
  - 更明确的成交结构锚
  - 更完整的 entry/exit 壳
  - 更像新的 raw-alpha / shell family

它并没有把旧 `Rank 15` 救回成“单线 S/R + regime-switch confirm”这类 queue-facing 独立策略；
反而更明确地说明：
- `support/resistance` 主题仍有信息；
- 但值得交易的是 `POC / VA / LVN` 这种 auction-structure 事件；
- 不是旧 Rank 15 的抽象 S/R regime-switch 写法。

## 4) 最值得改的唯一一刀是什么？
如果今天仍要给旧 `Rank 15` 回答“唯一最值得改的一刀”，最诚实的表述只能是：

> **把泛化的单线 S/R regime-switch confirmation，降级成 auction-structure family 里的局部 acceptance / zone-quality 注释。**

但关键判断是：
- 这刀不是在救旧 `Rank 15` 的独立主语；
- 它只是继续把旧 rank 的残余信息并入更上位的 `auction-profile / anchor-quality` 宿主；
- 不足以形成一个 bot2 可独立判断是否入板的、distinct 的 `Rank 15b`。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。本轮继续 `keep_park`。**

原因：
1. 原 `park` verdict 的审计意义没变，不能被新壳重写；
2. 新 evidence 支撑的是新的 auction-profile raw-alpha / shell family，而不是旧 rank 的窄 reframe；
3. 若硬写 `Rank 15b`，本质会变成“借 S/R 旧标签去包装新的 POC/VA/LVN 宿主”，不够诚实；
4. 这条线当前更像 `hard park with residual externalized`，不是一个值得留在 queue 里的 soft reframe 候选。

## 单轮审查模板回答
### 原 rank 为什么 park？
因为 clean replication 已显示：无论是 outside confirm、双确认还是 retest reclaim，旧 Rank 15 在收益、稳定性、跨资产和成本上都没有站住；问题是角色过宽，不是确认还不够多。

### 它更像 hard park 还是 soft park？
`hard park`。

### 有没有“可救信号”？
有。auction-profile / POC / LVN 新证据说明 support/resistance 主题仍有信息；但它救活的是新的成交结构 raw-alpha 宿主，不是旧 Rank 15。

### 最值得改的唯一一刀是什么？
把泛 S/R regime-switch confirmation 降级成 auction-structure family 内的 acceptance / zone-quality 注释层。

### 是否值得形成新的 derived hypothesis？
不值得。本轮继续 `keep_park`。

## Final verdict
- `keep_park`
- original verdict kept: `park`
- short note: `hard park；4 月 18 日新增的 auction-profile / POC / LVN shell 证据继续说明 support/resistance 主题若还有信息，也应写成更具体的 auction-structure raw-alpha 宿主，而不是旧 Rank 15 的 standalone regime-switch confirmation，因此当前不诚实 draft Rank 15b。`

## File actions
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`
- 未改：`docs/TODO.md`

## Commit
- 本轮默认不做 commit。
- 原因：git 工作区存在大量与本轮无关的共享脏文件；本轮只做最小必要文档改动，避免混提。
