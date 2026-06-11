# 2026-04-23 10:58 UTC · Rank 52 park reframe

## Selected rank
- `Rank 52`
- selection note: 本轮继续按 `50+` 优先的低频轮转只处理 1 条 parked rank。`Rank 52` 上次 park-reframe 是 `2026-04-13 15:11 UTC`，已超过 `7` 天窗口；同时 4 月 20~22 又新增了更明确的 microstructure / execution 旁证，适合再回答一次：这些新证据是在救旧 `15m trade-flow imbalance shared veto`，还是继续把 flow 主题外流到新的更快宿主。

## Read set
必读：
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`

补充：
- `research/park_reframe/2026-04-13_1511_rank52-park-reframe.md`
- `research/optimization_loop/2026-03-18_1011_rank52-clean-replication-park.md`
- `research/quant_digests/2026-04-20_1945_hawkes-lob-excitation-baseimbalance-alpha.md`
- `research/quant_digests/2026-04-21_0946_hl-marketquality-shared-gate-overlay.md`
- `research/quant_digests/2026-04-22_1634_ofi-kalman-maker-skew-alpha.md`

## 1) 原 rank 为什么 park？
原 `Rank 52 / trade-flow imbalance veto` 的 `park` 理由没有变化：

- 它想把 **setup 前最后几分钟的主动成交失衡** 写成 `15m` 主线（尤其 `breakdown_reclaim_short` / `ema_pullback_long`）的 shared veto；
- 但最小 clean replication 已经把这条写法审计清楚：它没有形成 desk 口径下可部署的 queue-facing gate。

冻结结果仍然足够明确（`BTC/ETH/SOL 120d 15m`，`next-bar open`，`no-overlap`，`hold 8 bars`，`6bps/side`）：
- 主读法 `breakdown_reclaim_short + opposite_flow_veto`：
  - `mean_total_return ≈ -2.73%`
  - `positive_asset_ratio = 0/3`
  - `mean_trades ≈ 17.0`
  - `mean_trade_count_retention ≈ 81.90%`
  - `mean_false_break_or_hold_4bars_rate ≈ 85.65%`
- 对照 `ema_pullback_long + opposite_flow_veto`：
  - `mean_total_return ≈ -4.04%`
  - `mean_trade_count_retention ≈ 57.87%`
- time-pocket 也没有留下可 admission 的稳定 pocket。

所以 old `Rank 52` 被 park 的核心不是“flow 没信息”，而是：

> **把 trade-flow imbalance 降级成 `15m` shared veto 这层主语，已经被 clean replication 否掉。**

## 2) 它更像 hard park 还是 soft park？
**本轮判断：仍是 `soft park`，但比 2026-04-13 那轮更接近 `hard park with consumed residual`。**

为什么仍保留 `soft`：
- order-flow / imbalance / microprice 主题显然还活着；
- 新证据继续说明短窗 flow state 能预测超短 horizon drift 或至少能改善成交质量；
- 失败更像是宿主与职责层摆错，而不是 flow 本身失效。

为什么更接近 `hard`：
- 4 月 20~22 的新证据越来越一致地把这组信息放到 `1m/3m` microstructure raw-alpha、maker-skew child execution、或 market-quality veto 里；
- 它们几乎都不再支持 old `Rank 52` 的 `15m shared veto` 壳还能再诚实切出 `Rank 52b`。

一句话：
> 主题还活，但 old `Rank 52` 这具 shared-veto 宿主已经越来越接近 residual 被消费完的状态。

## 3) 有没有“可救信号”？
**有，但仍然只是主题级可救信号，不是旧 rank 级可救信号。**

### A. Hawkes LOB excitation × base imbalance
`2026-04-20_1945_hawkes-lob-excitation-baseimbalance-alpha.md` 给出的最强启示是：
- 真正有信息的是 `event-time excitation state × base imbalance signed drift`；
- 先回答“盘口是不是进入高激发、值得出手的状态”，再回答“更可能往哪边动”；
- 这天然属于更快的 microstructure raw-alpha / admission 层，而不是 `15m` bar-close shared veto。

这条证据说明：
- flow / imbalance 主题若还值得追，更像 `1m/3m` event-driven host；
- 不是 old `Rank 52` 再细修一个 `same_direction_flow_gate` 就能承接。

### B. OFI / Kalman fair-value skew × maker markout
`2026-04-22_1634_ofi-kalman-maker-skew-alpha.md` 进一步把岗位说得更清楚：
- OFI / microprice 的 edge 主要活在 `maker-first quote skew + markout control + child execution`；
- 它的诚实表达是 `fill quality / fair-value skew / short-horizon drift`；
- 不适合再回头包装成 old `Rank 52` 的 `15m` queue-facing shared veto。

这条旁证等于确认：
- trade-flow 主题没有死；
- 但更像 execution-aware alpha sleeve，而不是旧壳上的小补丁。

### C. market-quality gate 只强化“岗位迁移”，不强化旧壳
`2026-04-21_0946_hl-marketquality-shared-gate-overlay.md` 的意义在于：
- spread / impact / premium-tail / illiquidity 更适合作为 shared market-quality gate；
- 这说明微结构信息在更慢频主线里更自然的岗位，是 veto / size-down / universe filter；
- 但这类岗位已经比 old `Rank 52` 更泛、更靠 execution/quality，本身也不是它的窄 reframe。

### 小结
所以本轮真实答案是：
- **有可救信号，但这些信号在继续把 flow 主题往新的 microstructure raw-alpha / child-execution / market-quality family 推；**
- **没有任何新增证据把 old `Rank 52` 拉回成一个还值得继续派生的 `15m shared veto` 宿主。**

## 4) 最值得改的唯一一刀是什么？
**如果只回答唯一主修改轴，本轮最值得改的一刀仍然是：把 `15m trade-flow imbalance shared veto` 改写成更快的 event-time / maker-skew flow host。**

但这刀为什么仍然不诚实地属于 `Rank 52b`：
1. 它把职责层从 `shared veto` 改成了 `raw alpha / child execution host`；
2. 它把时间尺度从 `15m` 改到了 `1m/3m`；
3. 它把入场主语从 `base setup` 附件，改成了 `event-time excitation / OFI skew` 自己就是核心起点。

所以对 old `Rank 52` 来说，本轮**没有新的唯一主修改轴**；唯一“最值得改的一刀”已经越界到新的 family。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论：`keep_park`。**

原因：
1. 原 `park` verdict 没有被推翻；
2. 新证据没有把 old `Rank 52` 拉回 queue-facing `15m` shared veto；
3. 4 月 20~22 的新旁证都在继续说明：flow 主题若还有价值，更像新的 `1m/3m` microstructure raw-alpha / maker-skew execution / market-quality 宿主；
4. 若现在硬写 `Rank 52b`，本质是在借新宿主给旧 gate 续命，模糊原 `park` 的审计边界。

## 6) 单轮模板回答
### 原 rank 为什么 park？
因为把 `trade-flow imbalance` 写成 `15m` shared veto 后，clean replication 在收益、跨资产、假突破控制与 time-pocket 上都没有形成 admission 级证据。

### 它更像 hard park 还是 soft park？
`soft park`，但比 2026-04-13 那轮更接近 `hard park with consumed residual`。

### 有没有“可救信号”？
有，但只是主题级：Hawkes excitation、OFI maker-skew、market-quality overlay 都说明 flow / microstructure 仍有信息，不过它们更像新的 `1m/3m` raw-alpha / child-execution / quality 宿主，而不是 old `Rank 52` 本体可救。

### 最值得改的唯一一刀是什么？
概念上仍是“把 `15m trade-flow imbalance shared veto` 改写成更快的 event-time / maker-skew flow host”，但这已经不属于 old `Rank 52` 的诚实窄 reframe。

### 是否值得形成新的 derived hypothesis？
不值得；本轮继续 `keep_park`。

## Final verdict
- `verdict`: `keep_park`
- `original_verdict_kept`: `park`
- `park_type_read`: `soft park，但比 2026-04-13 那轮更接近 hard park with consumed residual`
- short note: `4 月 20~22 的 Hawkes LOB excitation×base-imbalance、OFI/Kalman maker-skew 与 market-quality overlay 新证据继续说明：flow / microstructure 主题还活，但真正可救的是新的 1m/3m microstructure raw-alpha、maker-skew child-execution 或 market-quality 宿主，而不是旧 Rank 52 的 15m trade-flow imbalance shared veto；当前不诚实 draft Rank 52b。`

## Minimal audit note
本轮没有推翻原 `park`，也没有改写 `TODO`。只是进一步确认：
- flow / microstructure 值得继续研究；
- 但应作为新的 microstructure / execution / market-quality family 去追，而不是继续在 old `Rank 52` 名下硬切 `Rank 52b`。

## Git
- 未做 commit。
- 原因：`git status --short` 显示工作区存在大量与本轮无关的共享脏文件 / 未跟踪文件；本轮只做最小必要文档更新与邮件交付，避免混提。
