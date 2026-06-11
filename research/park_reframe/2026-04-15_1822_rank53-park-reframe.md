# 2026-04-15 18:22 UTC · Rank 53 park reframe review

## Scope
- Source rank: `Rank 53 / close-confirmed CHoCH compression gate`
- Original authoritative verdict stays: `park / evidence pool`
- This round only asks: **在不推翻原 park 的前提下，4 月上旬新增的 `turning-point-confirmed continuation` / `pattern-shortlist × next-hour drift` 证据，是否足以让 Rank 53 再诚实派生一条新的窄 reframe hypothesis。**

## Why this rank this round
- 按 `bot6` 轮转，本轮仍先看 `50~79` 号段。
- `Rank 53` 上次 park-reframe 复盘是 `2026-04-02 04:56 UTC`，已超过 `7` 天。
- 它属于典型“结构语言看起来有点道理，但 clean replication 主要靠砍样本减亏”的 parked rank，适合低频复盘。
- 这几天最相关的新旁证是：
  - `research/quant_digests/2026-04-08_2041_dynamic-turningpoint-tsmom-alpha.md`
  - `research/quant_digests/2026-04-07_2117_candlestick-shorthorizon-pattern-alpha.md`

## Read set
- required:
  - `docs/TODO.md`
  - `docs/PARK_REFRAME_QUEUE.md`
  - `docs/RECENT_PAPER_SEEDS.md`
  - `research/quant_digests/INDEX.md`
  - `research/park_reframe/INDEX.md`
- needed evidence:
  - `research/optimization_loop/2026-03-18_1102_rank53-clean-replication-park.md`
  - `reports/artifacts/scout_rank53_close_confirmed_choch_15m/overall_summary.csv`
  - `reports/artifacts/scout_rank53_close_confirmed_choch_15m/asset_summary.csv`
  - `reports/artifacts/scout_rank53_close_confirmed_choch_15m/time_pocket_summary.csv`
  - `research/park_reframe/2026-04-02_0456_rank53-park-reframe.md`
  - `research/quant_digests/2026-04-08_2041_dynamic-turningpoint-tsmom-alpha.md`
  - `research/quant_digests/2026-04-07_2117_candlestick-shorthorizon-pattern-alpha.md`

---

## 1) 原 rank 为什么 park？
原 `Rank 53` 被 park 的主因没有变化：**结构 gate 确实能少亏一点，但主要靠大幅砍样本，且跨资产仍不过线。**

最小 clean replication 的关键结果：
- `breakdown_reclaim_short + liquidity_sweep_veto @ 6bps/side`
  - `mean_total_return ≈ -2.88%`
  - `positive_asset_ratio = 0/3`
  - `mean_trades ≈ 8.0`
  - `mean_trade_count_retention ≈ 39.97%`
- 对照 `breakdown_reclaim_short + base`
  - `mean_total_return ≈ -3.55%`
  - `mean_trades ≈ 20.3`

连相对更像“能救一下”的 `ema_pullback_long + liquidity_sweep_veto` 也只是：
- `mean_total_return ≈ +0.43%`
- `positive_asset_ratio = 1/3`
- `mean_trades ≈ 6.33`
- `trade_count_retention ≈ 37.73%`

也就是说，`Rank 53` 留下的不是可以直接重开的 shared failure gate，而是一个**只在极薄样本里偶尔少亏/微正的结构语义残片**。

## 2) 它更像 hard park 还是 soft park？
**本轮仍读作 `soft park`，但比 4 月 2 日那轮更接近 hard。**

为什么还不是纯 hard park：
- `confirmed close` 比 `wick/单次 sweep` 更诚实，这层结构语言本身没错；
- `ema_pullback_long` 上确实留下过一个薄薄的 long-side pocket。

为什么明显继续向 hard 靠：
- 这个 pocket 仍只对应 `1/3` 资产为正；
- `trade_count_retention` 已压到约 `38%`，高度像切样本美化；
- `breakdown_reclaim_short` 这条原本更贴题的 lane 依旧 `0/3` 为正；
- time pocket 没出现像样的、可单独保留的稳定翻正窗口。

## 3) 现有证据里是否存在“可救信号”？
**有可救信号，但它更像把主题外流到新的 structure-aware continuation raw-alpha family，而不是救活旧 Rank 53。**

### 可救信号 A：turning-point-confirmed continuation 主题没死
`2026-04-08_2041_dynamic-turningpoint-tsmom-alpha.md` 更支持：
- `局部 turning point 确认 -> 新 trend leg 短周期续行`
- 主语已经是 **raw alpha / primary trigger**，不是 shared CHoCH failure gate。

### 可救信号 B：pattern shortlist 也在支持“确认后 drift”
`2026-04-07_2117_candlestick-shorthorizon-pattern-alpha.md` 的有效名单，本质也在讲：
- 某些结构/形态确认后，下一小时仍有方向漂移。
- 这同样更像新的 pattern-conditioned drift alpha，而不是旧 Rank 53 的 shared veto 写法。

### 关键审计点
这两条新证据都说明：
- “结构确认后 continuation” 仍有信息；
- 但它们救活的是**新的 continuation 宿主**；
- 不是把 `Rank 53 / close-confirmed CHoCH compression gate` 重新变成一个诚实的 queue-facing reframe。

## 4) 最值得改的唯一一刀是什么？
**如果硬要保留唯一一刀，最值得改的不是继续打磨 shared CHoCH/sweep veto，而是把主语改成：只交易 `confirmed turning-point exceedance` 之后的 continuation。**

但这正是问题所在：
- 一旦这么改，它就不再是“给 base setup 加结构 gate”；
- 而是“把结构确认本身升格成 primary trigger / raw alpha”；
- 这已经超出 `Rank 53b` 的诚实边界，更像一个新的 family intake。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论：`keep_park`。**

理由：
1. 原 `park` blocker 仍在：改善主要来自大幅 retention 压缩，而不是跨资产/跨 pocket 的真实翻身；
2. 新证据支持的是更上位的 `turning-point / pattern-confirmed continuation` raw-alpha family；
3. 若现在硬写 `Rank 53b`，本质是在把“新的 primary-trigger 家族”包装成“旧 shared gate 的窄 reframe”，审计上不诚实。

## 6) trade on / trade off 怎么读？
本轮不新增派生，只保留审计式复述：

- `trade on`：
  - 原 Rank 53 仅剩的一点 residual，是一句很窄的话：**别把 wick / 单次 sweep 直接当成结构翻转，至少等 confirmed close。**
- `trade off`：
  - 一旦把它写到足够有效，通常就会滑向“只做结构确认后的 continuation raw alpha”；
  - 那时得到的已不是 shared gate，而是另一条新宿主；
  - 因此不应再挂在 `Rank 53b` 名下。

---

## Final verdict for this round
- `verdict`: `keep_park`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park，但比 2026-04-02 那轮更接近 hard`

## Minimal audit note
本轮不重开 `Rank 53`，也不新增 `Rank 53b`。

更诚实的记录是：**4 月上旬新增的 turning-point / pattern-confirmed continuation 证据，继续说明“结构确认后 drift”这个大主题仍有信息；但它救活的是新的 continuation raw-alpha 宿主，而不是旧 Rank 53 的 shared close-confirmed CHoCH / liquidity-sweep gate。**

## Git
- 本轮只做最小必要文档改动；未做 commit。
- 原因：共享工作区存在大量与本轮无关的未跟踪脏文件，不适合安全 selective commit。
