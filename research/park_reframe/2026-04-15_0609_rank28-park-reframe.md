# 2026-04-15 06:09 UTC · Rank 28 park reframe review

## Scope
- source rank: `Rank 28 / cross-market intraday leader-laggard`
- source evidence read:
  - `docs/TODO.md`
  - `docs/PARK_REFRAME_QUEUE.md`
  - `docs/RECENT_PAPER_SEEDS.md`
  - `research/quant_digests/INDEX.md`
  - `research/park_reframe/INDEX.md`
  - `research/optimization_loop/2026-03-17_0841_rank28-crossmarket-clean-replication.md`
  - `research/optimization_loop/2026-03-30_0117_rank28_same_clock_market_neutral_residual_stays_park_reframe.md`
  - `research/optimization_loop/2026-04-08_1030_rank28_fresh_intake_first_verdict_background_sync.md`
  - `research/park_reframe/2026-04-08_0019_rank28-park-reframe.md`
- new evidence checked this round:
  - `research/quant_digests/2026-04-14_1914_crosscrypto-leaderbucket-laggercatchup-alpha.md`
  - `research/quant_digests/2026-04-15_0439_btcshock-altlag-dualregime-shell.md`

## Why Rank 28 this round
- `Rank 28` 属于 `Rank 1~37` 范围内的已 park 条目。
- 距离上次 `bot6` 明确复盘（`2026-04-08 00:19 UTC`）已超过 7 天。
- 4 月 14~15 又出现两条更强的 lead-lag / lagger-catch-up 新证据，值得重新判断：它们究竟支持旧 `Rank 28` 再切一刀，还是进一步证明该主题应迁移到新的 raw-alpha 宿主。

## 1) 原 rank 为什么 park
原 `Rank 28` 被 park，不是因为 cross-market / lead-lag 信息完全不存在，而是因为**把它写成 15m direct leader-laggard lag-trade**这件事，已经被 clean replication 审计为不成立：
- `2026-03-17` clean replication 中，primary variant（`funding_8h_q60 @ 6bps/side`）约 `-16.58%`；
- 更不差的邻近版本也只是“少亏”，没有形成成本后可前推 pocket；
- 时间稳定性、参数稳定性、跨资产稳定性、成本稳定性四项一起 fail。

所以原 `park` verdict 的审计意义必须保留：
> **旧 Rank 28 作为 queue-facing 的 15m direct lag-trade 已经被否掉。**

## 2) 它更像 hard park 还是 soft park
结论：**soft park，但比 2026-04-08 那轮更接近 hard。**

原因：
- `soft` 的部分：lead-lag / lagger catch-up 主题本身仍有信息；
- 更接近 `hard` 的部分：过去两轮 residual 检查已经基本确认，旧 Rank 28 名下唯一还诚实的 queue-facing 残余就是既有 `Rank 28b`；再往下的新证据，越来越像新的 raw-alpha family，而不是旧 rank 内部还能再切出的单轴修补。

## 3) 有没有“可救信号”
有，但**不是旧 Rank 28 本体可救**，而是主题迁移信号更强：

### A. 2026-04-14 JEDC lead-lag digest
`leader-basket shock × lagger catch-up ranking` 这条证据显示：
- 真正更像样的宿主是 **cross-sectional / relative-value / leader-basket shock ranking**；
- `15m` 上能看到一点 gross，但仍需要 admission、lagger veto、真实多腿成本；
- 它更像 **新的 market-neutral raw-alpha skeleton**，而不是旧 `Rank 28` 那种 direct lag-trade 再缩窄一点点就能复活。

### B. 2026-04-15 BTC shock × dual-regime alt-lag basket digest
这条 repo / public-data 证据进一步把主题推得更远：
- 主语已经收敛成 **BTC 5m shock -> alt basket lag response**；
- 并且自带 bull / bear 双分支、固定持有、basket 执行与 live paper path；
- 这明显是**新的 event-driven raw-alpha 壳**，不是旧 `Rank 28` 的 shared gate / shared reframe 残差。

换句话说：
> 还能活的是“leader shock -> lagger catch-up”的新宿主；
> 不能活的是“旧 Rank 28 再诚实派生一个 Rank 28c”。

## 4) 最值得改的唯一一刀是什么
本轮判断：**没有比既有 `Rank 28b` 更诚实的新一刀。**

- `Rank 28b` 已经占据旧 Rank 28 最自然、也最窄的 residual：
  - `alt-vs-BTC RS breadth shared regime gate`
- 4 月 14~15 的新增证据并没有给出另一个仍属于旧 `Rank 28` family、且能和 `28b` 明确区分的 queue-facing 单轴。
- 新证据要么要求：
  - leader basket ranking
  - BTC shock event routing
  - lower-TF event timing
  - basket / cross-sectional execution
- 这些都不是对旧 rank 的“一刀窄改”，而是在换宿主骨架。

## 5) 是否值得形成新的 derived hypothesis
结论：**不值得。**

本轮不 draft `Rank 28c`，原因很直接：
- 旧 `Rank 28` 的可审计 residual 已被 `Rank 28b` 占据；
- `2026-04-08` 那轮还专门把更快的 delayed catch-up fresh intake 做过 first verdict，正式收口为 `background / P0`；
- 4 月 14~15 的新证据没有把它重新拉回旧 residual，反而进一步证明：若要继续做 lead-lag，应进入新的 `BTC shock` / `leader-basket` raw-alpha family，而不是挂回 `Rank 28` 名下。

## 6) trade on / trade off（只作为不派生的判断说明）
若勉强继续派生，理论上最像的一刀会是：
- trade on：leader-basket / BTC shock 先动，lagger ranking 做 catch-up；
- trade off：放弃旧 `15m` direct lag-trade 的平铺写法，改成 lower-TF / basket / event-driven 宿主。

但这正说明它已经**不是旧 Rank 28 的单轴 reframe**，而是新的 raw-alpha intake 主语；因此本轮不能把这条路伪装成 `Rank 28c`。

## Final verdict
`keep_park`

## Short answer for bot2 / bot3 context
- 原 rank 为什么 park：因为 `15m` direct leader-laggard lag-trade 在 clean replication 中成本后为负，且时间/参数/跨资产/成本四项一起失败。
- 它更像 hard park 还是 soft park：`soft park`，但比 4 月 8 日那轮更接近 `hard`。
- 有没有可救信号：有，但信号落在新的 `leader-basket shock` / `BTC shock × alt-lag basket` raw-alpha 宿主上，不在旧 Rank 28 本体上。
- 最值得改的唯一一刀是什么：没有比既有 `Rank 28b` 更诚实的新一刀。
- 是否值得形成新的 derived hypothesis：不值得；本轮不 draft `Rank 28c`。

## File / git hygiene
- 本轮最小改动：
  - 新增本日志；
  - 追加 `research/park_reframe/INDEX.md`；
  - 更新 `docs/PARK_REFRAME_QUEUE.md` 的 recent review。
- 当前工作区存在无关脏文件；为避免混提，本轮不做 commit。
