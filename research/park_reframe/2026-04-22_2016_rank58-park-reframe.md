# 2026-04-22 20:16 UTC · Rank 58 park reframe review

## Scope
- Source rank: `Rank 58 / event-anchored VWAP hold-reclaim spine`
- Original authoritative verdict stays: `park / evidence pool`
- This round only asks: **在不推翻原 park 的前提下，近期新增的 VWAP / anchor 旁证，是否足以让 Rank 58 再诚实派生一个新的窄 reframe hypothesis。**

## Why this rank this round
- 按 `bot6` 轮转，当前默认仍优先 `Rank 50+`；`Rank 58` 上次复盘是 `2026-04-13 19:51 UTC`，已超过最近 `7` 天回避窗口。
- 相比继续重复近两天已覆盖的 `69/86` 等 50+ 条目，`Rank 58` 更符合“低频补看旧 parked rank”的节奏。
- 这轮有三条可直接对照的新增旁证：
  - `2026-04-09_2235_anchor-open-vwap-sigma-continuation-alpha.md`
  - `2026-04-18_0203_vwap-ema-bb-trendpullback-alpha.md`
  - `2026-04-19_0715_vwap-lowerband-persistent-placement-alpha.md`
- 真正要回答的是：**这些新证据是在救活 old Rank 58 的 shared event-anchored VWAP spine，还是继续把 VWAP / anchor 主题外流到新的 raw-alpha 宿主。**

## Read set
- required:
  - `docs/TODO.md`
  - `docs/PARK_REFRAME_QUEUE.md`
  - `docs/RECENT_PAPER_SEEDS.md`
  - `research/quant_digests/INDEX.md`
  - `research/park_reframe/INDEX.md`
- needed evidence:
  - `research/optimization_loop/2026-03-18_1505_rank58-source-intake.md`
  - `research/optimization_loop/2026-03-18_1524_rank58-clean-replication.md`
  - `research/park_reframe/2026-04-04_0924_rank58-park-reframe.md`
  - `research/park_reframe/2026-04-13_1951_rank58-park-reframe.md`
  - `research/quant_digests/2026-04-09_2235_anchor-open-vwap-sigma-continuation-alpha.md`
  - `research/quant_digests/2026-04-18_0203_vwap-ema-bb-trendpullback-alpha.md`
  - `research/quant_digests/2026-04-19_0715_vwap-lowerband-persistent-placement-alpha.md`

---

## 1) 原 rank 为什么 park？
原 `Rank 58` 想做的，是把 `VWAP` 从 session 锚点改成 **event anchor**，再让它横向服务 `breakout_short / Fib retest_hold / EMA-PSAR continuation` 三条 base setup，充当 shared `hold / reclaim spine`。

但最小 clean replication 的冻结结果到现在仍没有被推翻：
- `event_avwap_gate`
  - `mean_total_return ≈ -1.35%`
  - `positive_asset_ratio ≈ 44.44%`
  - `mean_trades ≈ 20.78`
  - `trade_count_retention ≈ 93.68%`
  - `false_follow_4bars ≈ 61.45%`
- 更紧的 `event_avwap_gate + 0.5ATR proximity`
  - `mean_total_return ≈ -0.37%`
  - `mean_trades ≈ 11.44`
  - `trade_count_retention ≈ 53.53%`
- time-pocket 也只有最后一段残留薄 pocket：
  - `bucket_1 ≈ -1.05%`
  - `bucket_2 ≈ -0.71%`
  - `bucket_3 ≈ +0.54%`

翻成人话：
- `event anchor` 确实比 `session anchor` 更诚实；
- 但它仍然没有把 shared hold/reclaim spine 做成足够稳定的 post-cost admission layer；
- 更紧 proximity 的改善又明显带上“砍样本减亏”的味道。

所以原 `park` verdict 不能动。

## 2) 它更像 hard park 还是 soft park？
**这轮仍读作 `soft park`，但比 4 月 13 日那轮更接近 `hard park with consumed residual`。**

为什么还不是纯 hard park：
- `VWAP / anchor` 主题本身没有死；
- 原 clean replication 至少证明 `event anchor > session anchor`，说明变量不是完全没信息。

为什么又更接近 hard：
- 旧 Rank 58 留下的残余越来越不像一个独立 queue-facing reframe；
- 新增证据继续说明：一旦 VWAP 真有信息，它更像是**新的 primary raw-alpha 宿主的一部分**，而不是旧 Rank 58 这种跨三条 setup 的 shared spine。

## 3) 现有证据里是否存在“可救信号”？
**有，但它们更明显是在救活别的宿主，不是在救 old Rank 58 本体。**

### 可救信号 A：anchor-open displacement × session VWAP continuation
`2026-04-09` 的 digest 说明：
- 若某个 anchor session 开始后已出现超出 same-minute 常态波动的位移，
- 且价格仍站在 session VWAP 强侧，
- 后续更像 continuation pocket。

这条线保住的是 **anchor-open displacement 作为 primary trigger 的 session raw alpha**；
并不是 old Rank 58 那种“给别的 setup 再加一层 shared VWAP spine”。

### 可救信号 B：VWAP + EMA 更适合作为 trend-pullback raw alpha 的母体
`2026-04-18` 的 digest 说明：
- `EMA20/EMA50 + VWAP20` 先锁定局部趋势，
- 再把 `BB` 反向穿刺读成 trend 内 pullback exhaustion。

这里的 `VWAP` 也不是 shared gate，而是 raw-alpha 主语内部的一部分。

### 可救信号 C：lower-VWAP underpricing 仍有研究价值，但不足以救活 shared spine
`2026-04-19` 的 digest 又给出另一条相反方向的旁证：
- `lower-VWAP reclaim` 主题在 `5m/15m` 仍可研究，
- 但当前厚度不足，且更像需要额外外生 shock / panic host 才能抬厚。

这进一步说明：
- VWAP 变量若还有价值，也是在更具体的 long-MR / pullback / session-continuation raw-alpha 宿主里；
- 不在 old Rank 58 的 shared cross-setup spine 写法里。

## 4) 最值得改的唯一一刀是什么？
**唯一还值得保留的一刀，是把主语从“跨 setup 的 shared event-anchored VWAP spine”缩成“anchor-defined event/session 已启动后的单宿主 continuation / reclaim raw-alpha”。**

但这刀本身已经说明：
- 它不再是 `Rank 58b` 级别的窄 reframe；
- 而是在把 VWAP / anchor 主题彻底迁移到新的 raw-alpha 宿主。

也就是说，这轮最值得改的唯一一刀，**不是继续打磨 old Rank 58**；
而是承认 old Rank 58 的 residual 已外流。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。最终结论：`keep_park`。**

理由：
1. 原 `park` blocker 没被化解：作为 shared event-anchored VWAP spine，它仍未提供足够稳定的 post-cost 增量；
2. 近期新增的三条 VWAP / anchor 证据支持的是新的 session-anchor / trend-pullback / lower-VWAP raw-alpha 宿主，而不是旧 Rank 58 的 shared spine 写法；
3. 若现在硬写 `Rank 58b`，本质是在把“新的 raw alpha 宿主”误包装成“旧 rank 的窄 reframe”，审计上不诚实。

## 6) trade on / trade off
- `trade on`：保留一句最小审计信息——**anchor 比随意 session 更诚实，VWAP 更适合服务已经启动的具体事件/位移宿主。**
- `trade off`：一旦把它写得足够有效，它就会变成新的 raw-alpha 主语；这时它就不再属于 old Rank 58 的 shared spine 血缘。

---

## Final verdict for this round
- `verdict`: `keep_park`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park，但比 2026-04-13 那轮更接近 hard with consumed residual`

## Minimal audit note
本轮不重开 `Rank 58`，也不新增 `Rank 58b`。

更诚实的记录是：**4 月中下旬新增的 VWAP / anchor 旁证继续说明这个主题本身仍有信息，但它正在稳定外流到新的 session-anchor / trend-pullback / lower-VWAP raw-alpha 宿主，而没有把 old Rank 58 的 shared event-anchored VWAP hold/reclaim spine 写法救回 queue-facing 的窄派生。**

## Git
- 本轮只做 park-reframe 所需最小文本更新；不改 `docs/TODO.md`，不做混合提交。
- 当前共享工作区仍有与本轮无关的脏文件与未跟踪产物，因此不安全做 selective commit。
