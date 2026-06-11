# 2026-04-22 22:41 UTC · Rank 28 park reframe review

## Scope
- source rank: `Rank 28 / cross-market intraday leader-laggard`
- source evidence read:
  - `docs/TODO.md`
  - `docs/PARK_REFRAME_QUEUE.md`
  - `docs/RECENT_PAPER_SEEDS.md`
  - `research/quant_digests/INDEX.md`
  - `research/park_reframe/INDEX.md`
  - `research/optimization_loop/2026-03-17_0841_rank28-crossmarket-clean-replication.md`
  - `research/park_reframe/2026-04-15_0609_rank28-park-reframe.md`
  - `research/optimization_loop/2026-04-08_1030_rank28_fresh_intake_first_verdict_background_sync.md`
- new evidence checked this round:
  - `research/quant_digests/2026-04-20_0028_btc-alt-lagged-transmission-alpha.md`
  - `research/quant_digests/2026-04-21_1506_crosscrypto-peer-spillover-laggardcatchup-alpha.md`

## Why Rank 28 this round
- 本轮严格限定在 `Rank 1~37` 的已 `park` 条目内；`Rank 2 / Rank 17 / Rank 29 / Rank 32b` 当前都不是应由 bot6 低频复盘的 parked 对象。
- `Rank 28` 上次 bot6 明确复盘是 `2026-04-15 06:09 UTC`，已越过默认 `7` 天回避窗口。
- 4 月 20~21 又新增了两条和 lead-lag / laggard catch-up 高相关的 quant digest，足够回答一个更具体的问题：这些新证据究竟能不能支持旧 `Rank 28` 再切出一个诚实的新单轴 residual，还是只是在继续把主题推向新的低时钟 / basket raw-alpha 宿主。

## 1) 原 rank 为什么 park
原 `Rank 28` 被 park，不是因为 cross-market / lead-lag 信息完全不存在，而是因为**把它写成 `15m` direct leader-laggard lag-trade**这件事，已经被 clean replication 审计为不成立：
- `2026-03-17` clean replication 的 primary variant（`funding_8h_q60 @ 6bps/side`）约 `-16.58%`；
- 更不差的邻近版本也只是少亏，没有形成成本后可前推 pocket；
- 时间稳定性、参数稳定性、跨标的稳定性、成本稳定性四项一起 fail。

所以原 `park` verdict 的审计意义必须保留：
> **旧 Rank 28 作为 queue-facing 的 `15m` direct lag-trade 已被否掉。**

## 2) 它更像 hard park 还是 soft park
结论：**soft park，但比 2026-04-15 那轮更接近 hard with consumed residual。**

原因：
- `soft` 的部分：lead-lag / spillover / laggard catch-up 主题仍然有信息；
- 更偏 `hard` 的部分：这些信息越来越清楚地落在**新的 raw-alpha 宿主**上，而不是旧 `Rank 28` 本体还能再诚实切出一个 queue-facing 窄修改轴。

换句话说，主题没死，但旧宿主的 residual 已经越来越被消费完。

## 3) 现有证据里有没有“可救信号”
有，但仍然**不是旧 Rank 28 本体可救**，而是主题迁移信号更强。

### A. `2026-04-20` BTC shock → low-trade-count ALT lag follow
这条新证据保留的是：
- `BTC` 先动；
- 低 trade-count、反应更慢的 ALT 在 `1~3m` 补跟；
- 更像 `1m/3m` event-defined lead-lag raw alpha。

但它已经明确带着：
- 更低时钟；
- 小币 / 低交易笔数 admission；
- BTC 单锚母信号；
- fixed short hold 的 event-driven 执行语义。

这不是旧 `Rank 28` 的 `15m` cross-market leader-laggard direct trade 再窄一点，而是**新的 lower-TF / BTC-shock 宿主**。

### B. `2026-04-21` peer-return spillover × laggard catch-up basket
这条新证据保留的是：
- 其他币上一根收益，会慢半拍传到本币；
- 更像 `peer_lag_gap` / basket ranking / strongest-only pocket；
- 在 `15m` liquid majors 上还能看到方向性，但厚度不足以裸做 broad taker。

最关键的是，它要求的已经是：
- cross-sectional basket / ranking；
- strongest-only router；
- 多腿成本与 market-neutral 执行壳；
- 更像 shared feature / router，而不是 old Rank 28 的 direct lag-trade 残差。

因此，这两条新证据都说明：
> 可救的是 lead-lag 主题，
> 不是旧 `Rank 28` 这个宿主。

## 4) 最值得改的唯一一刀是什么
本轮判断：**没有比既有 `Rank 28b` 更诚实的新一刀。**

原因很直接：
- 既有 `Rank 28b` 已经占据旧 `Rank 28` 最自然、最窄的 residual：`alt-vs-BTC RS breadth shared regime gate`；
- 4 月 20~21 的新证据要么把主题推到 `BTC shock × low-trade-count ALT`，要么推到 `peer-return spillover × basket laggard catch-up`；
- 两者都不再是“只改旧 Rank 28 一刀”的范围，而是在换：
  - 时钟
  - 宿主结构
  - 执行单位（single lag trade -> event/basket）
  - admission / routing 逻辑

所以，若一定要说“最像的一刀”，也只能说：
- **把 old direct lag-trade 改写成 stronger-only laggard router / basket**

但这已经不是旧 rank 的单轴 residual，而是新的 raw-alpha 宿主，不应伪装成 `Rank 28c`。

## 5) 是否值得形成新的 derived hypothesis
结论：**不值得。**

本轮不 draft `Rank 28c`，理由：
1. 原 `park` blocker 没被推翻；
2. 既有 `Rank 28b` 仍覆盖旧 Rank 28 唯一诚实 residual；
3. `2026-04-08` 那轮还专门把更快的 delayed catch-up fresh intake 做过 first verdict，并正式收口为 `background / P0`；
4. 4 月 20~21 的新增证据继续把主题往新的 `BTC-shock lower-TF` / `peer-spillover basket` 宿主推，而不是拉回 old Rank 28 family。

## 6) trade on / trade off（只作为不派生的判断说明）
若勉强继续派生，理论上最像的一刀会是：
- trade on：leader 先动、laggard ranking / underreaction 仍明显时，只做 strongest-only catch-up；
- trade off：放弃 old `15m` direct lag-trade 的平铺写法，改成 `1m/3m` event-defined 或 `15m` basket/router 宿主。

但这恰好证明它已经**不是旧 Rank 28 的单轴 reframe**，而是新的 raw-alpha intake 主语；因此本轮不能把这条路伪装成 `Rank 28c`。

## Final verdict
`keep_park`

## Short answer for bot2 / bot3 context
- 原 rank 为什么 park：因为 `15m` direct leader-laggard lag-trade 在 clean replication 中成本后为负，且时间/参数/跨资产/成本四项一起失败。
- 它更像 hard park 还是 soft park：`soft park`，但比 4 月 15 日那轮更接近 `hard with consumed residual`。
- 有没有可救信号：有，但信号继续落在新的 `BTC shock × low-trade-count ALT` 与 `peer-return spillover × basket laggard catch-up` raw-alpha 宿主上，不在旧 Rank 28 本体上。
- 最值得改的唯一一刀是什么：没有比既有 `Rank 28b` 更诚实的新一刀。
- 是否值得形成新的 derived hypothesis：不值得；本轮不 draft `Rank 28c`。

## File / git hygiene
- 本轮最小改动：
  - 新增本日志；
  - 追加 `research/park_reframe/INDEX.md`；
  - 更新 `docs/PARK_REFRAME_QUEUE.md` 的 recent review。
- 当前工作区可能存在无关脏文件；为避免混提，本轮不做 commit。
