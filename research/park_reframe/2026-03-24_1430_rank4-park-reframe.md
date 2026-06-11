# 2026-03-24 14:30 UTC · Rank 4 park reframe review

## Scope
- Source rank: `Rank 4 / crypto pairs trading / stat-arb`
- Original authoritative verdict stays: `park / evidence pool`
- This round only asks: **在不推翻原 park 的前提下，2026-03-24 新出现的 pairs 证据，是否值得让 Rank 4 再派生一个新于 `Rank 4c` 的窄 reframe（例如 `Rank 4d`）**

## Read set
- required:
  - `docs/TODO.md`
  - `docs/PARK_REFRAME_QUEUE.md`
  - `docs/RECENT_PAPER_SEEDS.md`
  - `research/quant_digests/INDEX.md`
  - `research/park_reframe/INDEX.md`
- recent park-reframe logs:
  - `research/park_reframe/2026-03-24_1227_rank24-park-reframe.md`
  - `research/park_reframe/2026-03-24_1027_rank36-park-reframe.md`
  - `research/park_reframe/2026-03-24_0820_rank22-park-reframe.md`
- needed evidence:
  - `research/optimization_loop/2026-03-16_1508_rank4-pairs-clean-replication-park.md`
  - `research/park_reframe/2026-03-22_2241_rank4-park-reframe.md`
  - `research/quant_digests/2026-03-24_0153_hf-pairs-threshold-governance-not-dogma.md`
  - `research/quant_digests/2026-03-24_1424_rl2-pairs-dynamic-scaling-fullstack.md`

## Why revisit Rank 4 despite the 7-day preference
- `Rank 4` 在 2026-03-22 已被 bot6 复盘过，按规则本应优先看别的。
- 但今天又新增了两条直接相关的新证据，而且都不是在重复讲 `spread z-score overlay`：
  - `2026-03-24_0153_hf-pairs-threshold-governance-not-dogma.md`
  - `2026-03-24_1424_rl2-pairs-dynamic-scaling-fullstack.md`
- 所以这轮要回答的是：**这些新证据会不会把原 Rank 4 从“soft park + 仅剩 Rank 4c overlay salvage”推进成新的窄派生，还是只会再次证明 pairs 主题若要活，更像一条新的 full-stack raw-alpha family。**

## 1) 原 rank 为什么 park？
原 `Rank 4` 被 park 的原因没有变化：
- 作为 **direct pairs-trade / stat-arb 主策略** 时，三组主 pair 都一起为负；
- clean replication 的 frozen-beta z-score spread first pass：
  - `BTC/ETH`：`trade_count = 83`，`cumulative_net_return ≈ -12.42%`
  - `BTC/SOL`：`trade_count = 117`，`cumulative_net_return ≈ -22.91%`
  - `ETH/SOL`：`trade_count = 127`，`cumulative_net_return ≈ -27.77%`
- 后续 `Rank 4b` 虽一度把部分 pair 拉回轻微正 pocket，但 time stability 一补，最近 tercile / 最新月份又一起转负；
- 因此原 desk 审计结论很清楚：**继续把 spread 偏离写成 standalone pairs alpha，这条路应继续 park。**

翻成人话：
- `pairs / spread` 这组变量不是完全没信息；
- 但原 Rank 4 那种“少数 pair + frozen beta + 固定 z-score 开平”写法，不够诚实地支撑可交易 alpha。

## 2) 它更像 hard park 还是 soft park？
**这轮仍然更像 `soft park`。**

原因：
- hard 的部分没变：原 Rank 4 当 direct-entry pairs alpha，应继续关闭；
- soft 的部分也没变：今天的新证据不是在说“pairs 全死了”，而是在说 **真正能活的更像完整治理后的 raw-alpha family**，而不是原始 Rank 4 这条窄写法。

所以它不是 hard park，因为主题本身还活；
但也不是“马上可救”，因为主题活着，不等于原 rank 值得再派生 `Rank 4d`。

## 3) 有没有“可救信号”？
**有，但更像“主题未死”的可救信号，不像“原 Rank 4 可再切一刀”的可救信号。**

### 可救信号 A：threshold / basket governance 说明 pairs 不是单一阈值神话
`2026-03-24_0153` 给出的重点是：
- 高频 pairs 的生死线不只在信号本身，而在 `entry/exit threshold × pair 篮子数量 × 成本治理`；
- 本地快检里，全 pair 平均会被成本吃掉，但 train 选前几对后，`15m` test 还能出现正 pocket；
- 这说明 pairs 主题更像“需要 honest basket governance”的策略家族，而不是原 Rank 4 那种固定三对、固定阈值就能讲完的线。

### 可救信号 B：dynamic sizing 说明 sizing 是风险预算层，不是原始 spread alpha 本体
`2026-03-24_1424` 给出的重点是：
- cointegration spread 均值回归仍可作为 base alpha；
- 但 `dynamic sizing / RL2` 更像风险预算与完整执行骨架，不应伪装成原始 spread 信号本体；
- 这进一步说明：若要重开 pairs，更像是另一条 `full-stack raw alpha` 新 family，而不是在原 Rank 4 上再补一个窄 overlay / sizing 轴就完事。

### 但为什么这还不够派生 `Rank 4d`？
因为它们共同指向的是：
- **要活的是“新 family 的完整骨架”**（threshold governance / basket governance / dynamic sizing / cost realism）；
- 不是“原 Rank 4 再加一个单一窄部件”就能诚实救活。

## 4) 最值得改的唯一一刀是什么？
**当前最值得保留的唯一一刀仍然是既有 `Rank 4c`，而不是新写 `Rank 4d`。**

也就是：
- 保留 `BTC-ETH spread z-score` 这一残余信息；
- 只把它当 `shared risk overlay / position-sizing gate`；
- 不再把它当 direct pair-entry alpha。

为什么不是新的单一修改轴？
- 如果写成“加 threshold governance”，那不是一刀，而是把 `entry / exit / basket / cost` 一起重写；
- 如果写成“加 dynamic sizing”，那也不是一刀，而是把完整 risk layer 偷渡进来；
- 这两种都更像新的 raw-alpha family intake，而不是 Rank 4 的窄 reframe。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论：`soft_reframe_candidate`。**

更准确地说：
- 原 `Rank 4` 的 `park` verdict 继续保留；
- 既有 `Rank 4c` 继续是当前唯一诚实的窄派生；
- 今天的新证据把 pairs 主题从“也许还能继续补 overlay”进一步推向：**更像一条需要单独 fresh intake 的 full-stack raw-alpha family**；
- 因此本轮不新增 `Rank 4d`，但会把 `Rank 4` 记成 `soft_reframe_candidate`：主题未死，只是已经超出原 rank 可窄救的边界。

## 6) trade on / trade off 结论
本轮**不形成**新的 `Rank 4d`。

更诚实的保留口径：
- `trade on`：pairs / stat-arb 主题本身仍值得继续研究，尤其是 `threshold governance + pair basket governance + dynamic sizing` 这条完整骨架；
- `trade off`：这些新增价值已经不再是原 Rank 4 的“唯一窄一刀”，而更像一条新的 full-stack raw-alpha family；若硬挂在 Rank 4 名下，会稀释原 park 的审计意义；
- 对原 Rank 4 来说，最值得保留的唯一窄修改轴仍只有 `Rank 4c`。

## Final verdict for this round
- `verdict`: `soft_reframe_candidate`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park`

## Minimal audit note
这轮新增的两条 pairs 证据没有推翻原 `Rank 4` 的 park。
它们只进一步说明：**pairs/stat-arb 主题若要重开，更像一条新的 threshold-governed / basket-governed / dynamically-sized raw-alpha family，而不是原 Rank 4 可以再诚实派生出一个新的 `Rank 4d`。**

## Git / write scope
- 本轮只做最小必要写入：本日志、`research/park_reframe/INDEX.md`、`docs/PARK_REFRAME_QUEUE.md`
- 默认不改 `docs/TODO.md`
- 未做 git commit：仓库当前存在大量与本轮无关的共享脏文件，避免混提
