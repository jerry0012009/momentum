# 2026-04-12 23:50 UTC · Rank 4 park reframe review

## 本轮对象
- `Rank 4 / crypto pairs stat-arb`
- 原始结论保留：`park / evidence pool`
- 本轮输出：`keep_park`

## 为什么这轮看 Rank 4
- 在 `Rank 1~37` 已 `park` 条目里，最近 7 天几乎都已被 bot6 低频复盘过；`Rank 4` 虽在 `2026-04-10` 刚看过，但今天出现了**新的、足够相关的 pairs / stat-arb 证据**：
  - `2026-04-12_1738_distancefirst-intraday-pairs-alpha.md`
  - `2026-04-12_1935_majorpair-halflife-zscore-pairs-alpha.md`
  - `2026-04-12_2141_pca-extremeonly-residual-fade-alpha.md`
- 所以这轮只回答一件事：这些新证据有没有把旧 `Rank 4` 从 `keep_park` 推到值得再派生一条窄 reframe hypothesis。

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- recent park-reframe references:
  - `research/park_reframe/2026-04-12_2115_rank27-park-reframe.md`
  - `research/park_reframe/2026-04-12_1845_rank3-park-reframe.md`
  - `research/park_reframe/2026-04-12_1624_rank33-park-reframe.md`
- source / prior rank evidence:
  - `research/optimization_loop/2026-03-16_1508_rank4-pairs-clean-replication-park.md`
  - `research/optimization_loop/2026-03-16_1853_rank4b-time-stability-park.md`
  - `research/park_reframe/2026-04-10_2002_rank4-park-reframe.md`
- new evidence:
  - `research/quant_digests/2026-04-12_1738_distancefirst-intraday-pairs-alpha.md`
  - `research/quant_digests/2026-04-12_1935_majorpair-halflife-zscore-pairs-alpha.md`
  - `research/quant_digests/2026-04-12_2141_pca-extremeonly-residual-fade-alpha.md`

## 1) 原 rank 为什么 park？
原 `Rank 4` 被 park 的核心 blocker 仍然没变：把少数 major pair 的 spread z-score 直接写成 queue-facing standalone alpha，最小 clean replication 与窄重开都没站住。

原始 clean replication（`2026-03-16_1508_rank4-pairs-clean-replication-park.md`）关键结果：
- `BTC/ETH`: `trade_count=83`, `cumulative_net_return≈-12.42%`
- `BTC/SOL`: `trade_count=117`, `cumulative_net_return≈-22.91%`
- `ETH/SOL`: `trade_count=127`, `cumulative_net_return≈-27.77%`

后续最自然的 residual 也已被消费：
- `Rank 4b`：rolling beta / 窄 reframe 之后，time stability 仍不过线，最新 tercile / month 一起转负；
- `Rank 4c`：把 residual 收缩成 `BTC-ETH spread z-score` shared risk overlay，而不是 direct pair-entry alpha。

所以原 `park` 的审计意义仍然完整：
> 被否掉的是“旧 Rank 4 这层 direct pairs-trade 壳”，不是 relative-value / stat-arb 主题整体死亡。

## 2) 它更像 hard park 还是 soft park？
**本轮判断：仍是 `soft park`，但比 4 月 10 日那轮更接近 hard。**

原因：
1. soft 的部分在于：pairs / stat-arb 今天仍有大量新证据，说明主题持续活跃；
2. 但更接近 hard 的部分也更清楚：这些新证据已经不再支持“沿旧 Rank 4 再补一刀”，而是越来越明确地要求**换成新的 full-stack / basket / admission family**。

换句话说：
- 主题还活；
- 旧 `Rank 4` 这具壳子更不像还值得继续切出 `4d` 的宿主。

## 3) 有没有“可救信号”？
**有，但更像主题级可救信号，不像旧 rank 级可救信号。**

### 新证据留下了什么“可救信号”
1. `distance-first intraday pairs`
   - 指向的是：short-cycle pairs baseline 更该先从 `distance-first pair admission × spread fade` 开始；
   - 这改的是 pair admission / selection 层，不是旧 Rank 4 那种固定几对 + 固定 spread 直入。
2. `short-half-life major-pair z-score fade`
   - 指向的是：相关性不是主语，`half-life` 才更像 pairs 优先级排序器；
   - 这同样是在重写 admission layer，而不是给旧壳补一个小 filter。
3. `PCA extreme-only residual fade`
   - 指向的是：真正像可交易入口的，是 `factor-neutral residual extreme only`；
   - 主语已变成 basket / residual ranking / extreme pocket，不再是旧 Rank 4 的固定双腿 z-score。

### 为什么这些信号仍救不了旧 Rank 4
因为它们共同指向的是：
> pairs 主题若要活，更像 `dynamic pair admission × fast-reversion pocket × residual / spread fade shell` 这类新 family，
> 而不是继续给旧 `Rank 4` 加一层小补丁。

## 4) 最值得改的唯一一刀是什么？
如果今天还要给旧 `Rank 4` 回答“唯一最值得改的一刀”，答案仍然只能是：

> **保留既有 `Rank 4c` 这条 residual 读法：把 `BTC-ETH spread z-score` 只当 shared risk overlay / sizing gate，而不再当 direct pair-entry alpha。**

但这轮更关键的判断是：
- 这已经不是新的修改轴；
- 今天的新 evidence 并没有提供一个还属于旧 `Rank 4` 的、未被消费的单轴 reframe；
- 若硬写成 `distance-first` / `half-life-first` / `PCA extreme-only`，那已是**新的 raw-alpha family**，不是旧 rank 的诚实窄派生。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。本轮继续 `keep_park`。**

原因：
1. 原 `park` verdict 没有被推翻；
2. 原线最自然的 residual 已被 `Rank 4b / 4c` 消费；
3. 今天的新 evidence 继续把 pairs 主题抬升到新的 full-stack / basket / dynamic-admission family；
4. 对旧 rank 而言，没有出现一条仍属于旧宿主、且尚未被消费的唯一主修改轴。

## 单轮审查模板回答
### 原 rank 为什么 park？
因为最小 clean replication 在主要 pair 上一起偏负，而 rolling-beta 窄重开也被时间稳定性否掉；旧壳的 direct spread-entry 写法站不住。

### 它更像 hard park 还是 soft park？
`soft park`，但比 4 月 10 日那轮更接近 hard。

### 有没有“可救信号”？
有，但是主题级可救：distance-first、half-life-first、PCA residual extreme-only 都在说明 pairs 主题还能活；只是它们已经属于新的 family，而不是旧 Rank 4 本体可救。

### 最值得改的唯一一刀是什么？
仍只是既有 `Rank 4c`：把 `BTC-ETH spread z-score` 保留为 shared risk overlay / sizing gate，而不再当 direct entry alpha。

### 是否值得形成新的 derived hypothesis？
不值得。本轮继续 `keep_park`。

## Final verdict
- `keep_park`
- original verdict kept: `park`
- short note: `soft park，但比 4 月 10 日那轮更接近 hard；4 月 12 日新增的 distance-first / short-half-life / PCA extreme-only pairs 证据没有把旧 Rank 4 救回 queue-facing direct-entry，反而更明确地把 relative-value 主题推向新的 dynamic-admission / basket residual raw-alpha family，因此当前不诚实 draft Rank 4d。`

## File actions
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`
- 未改：`docs/TODO.md`

## Commit
- 本轮不做 commit。
- 原因：git 工作区存在大量与本轮无关的共享脏文件 / 未跟踪文件；本轮只做最小必要文档改动，避免混提。
