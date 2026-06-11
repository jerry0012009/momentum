# 2026-04-11 08:18 UTC · Rank 12 park reframe

## Selected rank
- `Rank 12`
- selection note: 本轮按 `Rank 1~37` 的 parked rank 低频轮转处理，优先避开最近 `7` 天内刚复盘过的条目。`Rank 12` 上次 bot6 复盘是 `2026-04-03 17:51 UTC`，已超过 7 天；同时 4 月上旬新增了 `POC / absorption / HTF anchor` 旁证，适合再判断一次：这些新证据是否足以在既有 `Rank 12b` 之外，再诚实派生新的窄 reframe。

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- recent park-reframe logs:
  - `research/park_reframe/2026-04-11_0535_rank21-park-reframe.md`
  - `research/park_reframe/2026-04-11_0306_rank11-park-reframe.md`
  - `research/park_reframe/2026-04-11_0032_rank25-park-reframe.md`
- needed evidence:
  - `research/optimization_loop/2026-03-17_0011_rank12-clean-replication-park.md`
  - `research/park_reframe/2026-04-03_1751_rank12-park-reframe.md`
  - `research/optimization_loop/2026-03-30_0721_rank12_zone_persistence_gate_not_frontslot.md`
  - `research/optimization_loop/2026-04-09_0811_rank12b_fresh_intake_background_absorbed.md`
  - `research/quant_digests/2026-04-05_1755_poc-cvd-absorption-alpha.md`

## 1) 原 rank 为什么 park？
原 `Rank 12` 被 park 的原因没有变化：它把 **averaged support/resistance zone + context** 写成一条可以直接承担 `15m` 入场职责的 standalone entry skeleton，但 clean replication 已经把这条主体审计成 post-cost 不够厚、也不够稳。

冻结版关键结果（`BTC/ETH/SOL 120d 15m`, `next-bar open`, `1 ATR stop`, `2 ATR target`, `8-bar time stop`, `6bps/side`）：
- `winner_variant = averaged_zone_context_gate`
- `mean_total_return ≈ -4.34%`
- `positive_asset_ratio = 1/3`
- Light Stability Pack 四项全 fail：
  - 时间稳定性：`0/3 positive buckets`
  - 参数稳定性：`0/5 configs positive`
  - 跨标的稳定性：`1/3 assets positive`
  - 成本稳定性：`0/4 cost levels positive`

翻成人话：
- 原问题不是“zone 参数还没调到位”；
- 而是 **averaged zone + context 自己当 entry alpha** 这件事没有形成足够诚实的 strategy body；
- 所以原 `park` 的审计意义必须保留：失败对象是旧 `Rank 12` 的 standalone zone-entry 角色，不是 `S/R / zone / anchor` 主题整体死亡。

## 2) 它更像 hard park 还是 soft park？
**本轮仍读作 `soft park`，但比 4 月初更接近 hard park。**

为什么还不是 hard park：
- `S/R / zone` 主题本身没有彻底死；
- 它仍可能作为 `quality gate / anchor / mother signal` 提供信息量；
- 这也是为什么早先会收敛出既有 `Rank 12b`。

为什么又明显更偏 hard：
1. 原线唯一诚实修改轴早已收敛到 `Rank 12b`；
2. `2026-03-30` 已明确判过：`Rank 12b` 不构成新的 front-slot fresh intake；
3. `2026-04-09` 又进一步把这条 residual 收口为 `background / P0`：不是因为主题没价值，而是因为这条 residual 已被既有 queue-only proposal 完整承载，不应反复伪装成新 intake。

所以，对 **旧 Rank 12 本体** 的读法已经更接近 hard；只是在大主题层面，仍保留一层 `soft park` 式 residual 记账。

## 3) 有没有“可救信号”？
**有，但新信号并没有生成新的 `Rank 12c`；它只是进一步证明：如果 zone / anchor 主题还值得追，宿主也应该更上移。**

本轮最 relevant 的新增旁证是：
- `2026-04-05_1755_poc-cvd-absorption-alpha.md`

这条 digest 的关键信息不是“再给 Rank 12 叠一个 zone 细节”，而是：
- 真正可交易的 base alpha 更像 **`1H POC-proximal price/CVD absorption × 15m child execution`**；
- 也就是 `HTF anchor + absorption raw alpha shell`，而不是 `15m averaged zone + context shared gate` 的继续打磨；
- 它强调的是 `POC / anchor` 作为母信号或 raw-alpha 宿主，而不是旧 Rank 12 那种把 zone 直接写成 standalone entry skeleton 的职责。

这意味着：
- zone / anchor 主题仍然有信息；
- 但它更像被抬升到新的 `HTF-anchor / absorption / child-execution` 宿主；
- 而不是足以在既有 `Rank 12b` 之外，再诚实切出一条属于旧 Rank 12 的新单轴。

## 4) 最值得改的唯一一刀是什么？
**唯一最值得改的一刀没有变化，仍然只是既有 `Rank 12b`：**

> `demote standalone averaged support/resistance zone + context entry into a volume-weighted zone-persistence shared quality gate`

为什么本轮不是别的一刀：
- 新增的 `POC / absorption` 旁证虽然有价值，但它已经把主语改成 `HTF anchor raw alpha`；
- 若硬把这条新证据写成 `Rank 12c`，本质会变成：
  1. 换 anchor（averaged zone -> rolling POC）
  2. 换逻辑（quality gate -> absorption raw alpha / child execution）
  3. 换职责层（shared gate -> HTF mother signal）
- 这已经不是 bot6 允许的“唯一一刀”，而是多轴换壳。

因此，本轮最关键的判断反而是：
- 新证据没有提供第二条独立主修改轴；
- 它只是更明确地把 zone 主题从旧 Rank 12 的职责边界里推了出去。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论：`keep_park`。**

更精确地说：
- 原 `Rank 12 = park` 的审计意义保持不变；
- 既有 `Rank 12b` 继续是旧 rank 唯一诚实窄派生；
- 本轮新增的 `POC / absorption` 证据不足以再派生 `Rank 12c`。

原因有三层：
1. 原 rank 的失败结构没有被推翻；
2. 旧 residual 已被 `Rank 12b` 显式收敛，并在后续 fresh-intake 判断里被收口为 `background / P0`；
3. 新增证据真正支持的是新的 `HTF-anchor raw-alpha family`，不是旧 `Rank 12` 的同层修补。

## 6) 如果勉强往下写，trade on / trade off 会怎么变？
本轮不新增派生，因此这里只做审计式说明：

### trade on
- 如果将来还要保留 `Rank 12` 的残余价值，更诚实的做法仍然是：
  - 让 zone / persistence 只负责 `quality gate / anchor note / mother signal`；
  - 不再假装它能自己作为 `15m standalone entry alpha`。

### trade off
- 它不再是独立 entry skeleton；
- headline return 不一定明显改善，更多价值可能体现在 trade selection / anchor honesty；
- 若继续往 `POC + absorption + child execution` 方向推进，那已经更像新的 raw-alpha 宿主，不应挂回旧 `Rank 12` 名下续命。

---

## Final verdict for this round
- `verdict`: `keep_park`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park，但对旧 Rank 12 的 standalone zone-entry 读法已更接近 hard`

## Minimal audit note
本轮不推翻 `Rank 12` 的原 park，也不新增 `Rank 12c`。更诚实的记录是：**4 月上旬新增的 `POC / absorption` 证据，说明 zone / anchor 主题若还值得追，更像新的 `HTF-anchor raw-alpha / child-execution` 宿主，而不是足以在既有 `Rank 12b` 之外再为旧 Rank 12 派生新的单轴 reframe；因此旧 rank 保持 `keep_park`。**

## Git
- 本轮只做最小必要文档改动；未做 commit。
- 原因：git 工作区存在大量无关脏文件，当前任务不适合安全 selective commit。
