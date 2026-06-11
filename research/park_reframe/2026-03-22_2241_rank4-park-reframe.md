# 2026-03-22 22:41 UTC · Rank 4 park reframe review (revisit)

## Scope
- Source rank: `Rank 4 / crypto pairs trading / stat-arb`
- Original authoritative verdict stays: `park / evidence pool`
- This round only asks: **在不推翻原 park 的前提下，2026-03-22 新出现的 `crowding gap` 旁证，是否值得让 Rank 4 再派生一个新于 `Rank 4c` 的窄 reframe（例如 `Rank 4d`）**

## Why revisit Rank 4 (7-day rule note)
- `Rank 4` 已在 `2026-03-18 21:45 UTC` 被 bot6 派生出 `Rank 4c`，按 7-day 规则本不该频繁回头看。
- 本轮允许低频复核，仅因为出现了新的近邻证据：
  - `research/quant_digests/2026-03-22_1826_longshort-crowding-gap-asymmetric-overlay.md`
- 这轮真正要回答的不是“Rank 4 要不要翻案”，而是：**这个新变量会不会打开第二条独立主轴，还是只会再次证明『原 pairs alpha 应继续 park，残余价值更像 shared overlay』。**

## Read set
- required:
  - `docs/TODO.md`
  - `docs/PARK_REFRAME_QUEUE.md`
  - `docs/RECENT_PAPER_SEEDS.md`
  - `research/quant_digests/INDEX.md`
  - `research/park_reframe/INDEX.md`
- recent park-reframe logs:
  - `research/park_reframe/2026-03-22_2041_rank16-park-reframe.md`
  - `research/park_reframe/2026-03-22_1839_rank15-park-reframe.md`
  - `research/park_reframe/2026-03-22_1633_rank14-park-reframe.md`
- needed evidence:
  - `research/park_reframe/2026-03-18_2145_rank4-park-reframe.md`
  - `research/optimization_loop/2026-03-16_1853_rank4b-time-stability-park.md`
  - `research/quant_digests/2026-03-18_1714_btc-eth-spread-zscore-risk-overlay.md`
  - `research/quant_digests/2026-03-22_1826_longshort-crowding-gap-asymmetric-overlay.md`

---

## 1) 原 rank 为什么 park？
原 `Rank 4` 被 park 的原因没有变化：
- 作为 **direct pairs-trade / stat-arb 主策略** 时，三组主 pair 都为负；
- 后续唯一允许的窄重开 `Rank 4b`（rolling-beta z-score spread）虽然短暂把 `BTC/SOL`、`ETH/SOL` 拉回轻微正 pocket，但 time stability 一补就塌：最近 tercile 与最新月份一起转负；
- 因此已经足够说明：**继续把 spread 偏离写成 standalone pairs alpha，这条路应继续保留 `park` 审计结论。**

翻成人话：
- `spread` 变量不是纯噪音；
- 但它不够诚实地支撑“直接做 pair trade”这件事。

## 2) 它更像 hard park 还是 soft park？
**仍然更像 `soft park`。**

- hard 的部分：原始 `Rank 4` 与 `Rank 4b` 作为 direct-entry pairs alpha 都应继续视为关闭；
- soft 的部分：它留下来的残余信息量，仍更像 `dislocation / crowding risk` 这类二阶状态，而不是零信息。

但本轮补充一个更重要的边界：
- 这份 soft park 的残余价值，当前已经主要收敛在既有 `Rank 4c` 那条角色降级上；
- 新证据若不能形成**独立于 `spread z-score risk overlay` 的唯一主修改轴**，就不该再写 `Rank 4d`。

## 3) 有没有“可救信号”？
**有，但只够再次证明“该做 overlay”，不够打开新的 Rank 4d。**

### 可救信号 A：`crowding gap` 再次证明“这类变量更像 overlay，不像方向键”
`2026-03-22_1826_longshort-crowding-gap-asymmetric-overlay.md` 的核心读法是：
- `Long/Short Ratio` 单点方向信息不稳定；
- `global-vs-top position crowding gap` 更像 **asymmetric veto / size overlay**；
- 它和 `spread z-score` 一样，都指向同一个 desk 结论：**跨主体错位/拥挤变量更适合放在 shared risk layer。**

### 可救信号 B：但这不是 Rank 4 的独立新轴
问题也正出在这里：
- `Rank 4c` 已经把原 Rank 4 最自然的 salvage 读法收紧成：`BTC-ETH spread z-score -> shared risk overlay / position-sizing gate`；
- 新的 `crowding gap` 虽然方向一致，但它换了变量来源与语义层（账户拥挤，而非价差失衡）；
- 若据此再派生 `Rank 4d`，本质上会变成：**从“spread dislocation overlay”跳到“position crowding overlay”**，这已经不是原 Rank 4 主题内的唯一窄一刀，而是借 Rank 4 的壳去写一条新的外部行为变量线。

### 可救信号 C：它更适合服务 desk 现有 shared overlay 池，而不是继续挂在 Rank 4 名下
所以这条新证据最诚实的落点是：
- 把它当成对既有 `Rank 4c` 的旁证：`pairs/stat-arb` 失败后，残余价值仍然更像 overlay；
- 而不是把 `crowding gap` 再命名成一个 Rank 4 的后继版本。

## 4) 最值得改的唯一一刀是什么？
**唯一最值得保留的一刀仍然不变：`Rank 4c`。**

也就是：
- 保留 `BTC-ETH spread z-score`；
- 只把它当 `shared risk overlay / position-sizing gate`；
- 不再把它当 direct pair-entry alpha。

本轮新增的 `crowding gap` 证据，并没有形成比 `Rank 4c` 更贴原 Rank 4 主题、且更独立的新一刀；它更像“同类角色结论的外部旁证”。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论：`keep_park`。**

更准确地说：
- 原 `Rank 4` 继续 `park`；
- 已起草的 `Rank 4c` 继续保留，且仍是最诚实的唯一窄派生；
- `2026-03-22` 的 `crowding gap` 新证据不足以再派生 `Rank 4d`。

---

## Final verdict for this round
- `verdict`: `keep_park`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park`

## Minimal audit note
本轮不推翻 `Rank 4` 的原 park，也不新增 `Rank 4d`。
更诚实的记录是：**`crowding gap` 新证据只会再次证明“pairs/stat-arb 主题残余价值更像 shared overlay”，但它不足以超出既有 `Rank 4c`，形成新的唯一主修改轴。**

## Git
- 本轮只做最小必要文档改动；不做 commit（工作区存在大量无关脏文件，避免混提）。
