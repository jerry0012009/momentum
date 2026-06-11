# 2026-04-15 21:09 UTC · Rank 54 park reframe review

## Scope
- Source rank: `Rank 54 / LVN rejection + POC acceptance gate`
- Original authoritative verdict stays: `park / evidence pool`
- This round only asks: **在不推翻原 park 的前提下，4 月上旬新增的 `dual-LVN range reversion` / `POC-proximal price-CVD absorption` 证据，是否足以让 Rank 54 再诚实派生一条新的窄 reframe hypothesis。**

## Why this rank this round
- 按 `bot6` 轮转，本轮仍优先看 `50~79` 号段。
- `Rank 54` 上次 park-reframe 复盘是 `2026-04-03 22:33 UTC`，已超过 `7` 天。
- 它属于典型“volume-profile 语义本身可能有信息，但旧 shared gate 写法主要靠砍样本/砍到无交易”的 parked rank，适合低频复盘。
- 这几天最相关的新旁证是：
  - `research/quant_digests/2026-04-13_0940_midpoint-split-dual-lvn-range-reversion-alpha.md`
  - `research/quant_digests/2026-04-05_1755_poc-cvd-absorption-alpha.md`

## Read set
- required:
  - `docs/TODO.md`
  - `docs/PARK_REFRAME_QUEUE.md`
  - `docs/RECENT_PAPER_SEEDS.md`
  - `research/quant_digests/INDEX.md`
  - `research/park_reframe/INDEX.md`
- needed evidence:
  - `research/optimization_loop/2026-03-18_1104_rank54-source-intake-guard-passed.md`
  - `research/optimization_loop/2026-03-18_1135_rank54-clean-replication-park.md`
  - `research/park_reframe/2026-04-03_2233_rank54-park-reframe.md`
  - `research/quant_digests/2026-04-13_0940_midpoint-split-dual-lvn-range-reversion-alpha.md`
  - `research/quant_digests/2026-04-05_1755_poc-cvd-absorption-alpha.md`

---

## 1) 原 rank 为什么 park？
原 `Rank 54` 被 park 的主因没有变化：**shared `lvn_rejection + poc_acceptance` gate 一旦写到足够“题面正确”，交易基本被砍光，剩下的改善不具备 queue-facing 可交易性。**

最小 clean replication 的关键结果：
- 主读法 `breakdown_reclaim_short + lvn_rejection_plus_poc_acceptance @ 6bps/side`
  - `mean_total_return ≈ 0.00%`
  - `positive_asset_ratio = 0/3`
  - `mean_trades = 0.0`
  - `mean_trade_count_retention = 0.00%`
- 相邻没那么严格的 `ema_pullback_long + lvn_rejection`
  - `mean_total_return ≈ +1.40%`
  - `positive_asset_ratio = 1/3`
  - `mean_trade_count_retention ≈ 22.45%`

也就是说，旧 Rank 54 留下的不是一个还能继续细修的 shared acceptance gate，而是：**一旦把 POC acceptance 真当 hard confirm，就几乎只剩 sample veto。**

## 2) 它更像 hard park 还是 soft park？
**本轮仍读作 `soft park`，但比 4 月 3 日那轮更接近 hard。**

为什么还保留一点 soft：
- `LVN / POC / volume-profile` 这组变量本身没有被审计打死；
- 4 月新增旁证说明 volume-profile 主题仍能在别的壳里留下 pocket。

为什么继续向 hard 靠：
- 旧 Rank 54 的 blocker 已经非常具体：不是参数没调好，而是 **shared gate 角色不成立**；
- 最贴题的 `poc_acceptance` 一上去就 `0` 笔交易，说明问题不是“还差一点实现”，而是职责摆错；
- 留下的正 pocket 只在更宽松的 `lvn_rejection only` 上，而且仍只有 `1/3` 资产为正、retention 很薄。

## 3) 现有证据里是否存在“可救信号”？
**有可救信号，但它更像把主题外流到新的 volume-profile raw-alpha 宿主，而不是救活旧 Rank 54。**

### 可救信号 A：dual-LVN range reversion
`2026-04-13_0940_midpoint-split-dual-lvn-range-reversion-alpha.md` 更支持：
- 把 `LVN` 直接当作 entry anchor；
- 主语是 `range-reversion raw alpha`，不是 shared acceptance gate；
- `ETHUSDT 15m` 的 gross pocket 说明“薄区回摆”这个大主题还有信息。

### 可救信号 B：POC-proximal price/CVD absorption
`2026-04-05_1755_poc-cvd-absorption-alpha.md` 更支持：
- `POC` 更像 HTF 母信号 / raw-alpha anchor；
- `15m` 更适合做 child execution，而不是把 `POC acceptance` 写成旧 base setup 的通用 allow/deny gate。

### 关键审计点
这两条新证据都说明：
- `volume-profile` 主题没有死；
- 但它活下来的方式是 **raw alpha / HTF anchor / child execution**；
- 不是旧 Rank 54 的 `shared lvn_rejection + poc_acceptance gate`。

## 4) 最值得改的唯一一刀是什么？
**如果硬要保留唯一一刀，最值得改的是：把 `POC/LVN` 从 shared gate 降级/改写成单资产 `range-reversion / absorption` 的 primary anchor。**

但这正是本轮不 draft 的原因：
- 一旦这么改，主语已经从“给别的 setup 做 gate”变成“自己就是 alpha”；
- 这不是旧 Rank 54 壳里的一条窄实现修正，而是换了宿主职责；
- 它更像新的 intake family，不是诚实的 `Rank 54b`。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论：`keep_park`。**

理由：
1. 原 `park` blocker 仍在，且已更清楚：旧 Rank 54 的 shared gate 写法会直接坍缩成零交易或极薄 retention；
2. 新证据支持的是 `dual-LVN range reversion` / `POC absorption parent signal` 这类新 raw-alpha 宿主；
3. 若现在硬写 `Rank 54b`，本质是在把“新宿主”包装成“旧 gate 的窄 reframe”，审计上不诚实。

## 6) trade on / trade off 怎么读？
本轮不新增派生，只保留审计式复述：

- `trade on`：
  - 原 Rank 54 留下的一点 residual，只够说明 **volume-profile 变量仍值得保留在研究池**；
  - 尤其是 `LVN` 可作为薄区回摆 anchor，`POC` 可作为母级公允锚。
- `trade off`：
  - 一旦把它写到更有效，通常就会滑向“single-asset range-reversion raw alpha”或“1H parent -> 15m child execution”；
  - 那时得到的已不是 shared gate，而是另一条新 family；
  - 因此不应再挂在 `Rank 54b` 名下。

---

## Final verdict for this round
- `verdict`: `keep_park`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park，但比 2026-04-03 那轮更接近 hard`

## Minimal audit note
本轮不重开 `Rank 54`，也不新增 `Rank 54b`。

更诚实的记录是：**4 月新增的 dual-LVN / POC absorption 证据，继续说明 volume-profile 主题仍有信息；但它救活的是新的 single-asset range-reversion / HTF-anchor raw-alpha 宿主，而不是旧 Rank 54 的 shared `LVN rejection + POC acceptance` gate。**

## Git
- 本轮只做最小必要文档改动；未做 commit。
- 原因：共享工作区存在大量与本轮无关的未跟踪脏文件，不适合安全 selective commit。
