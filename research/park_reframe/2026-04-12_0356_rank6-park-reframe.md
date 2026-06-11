# 2026-04-12 03:56 UTC — Rank 6 park reframe review

## 为什么本轮选 Rank 6
- 按 `bot6` 轮转约束，本轮继续只处理 `Rank 1~37` 中已 `park` 的 1 条。
- `Rank 6` 上次 park-reframe 复盘是 `2026-04-04 21:12 UTC`，已超过 7 天。
- 期间出现了新的直接旁证：`research/quant_digests/2026-04-12_0038_cryptoequity-proxy-impulse-fade-alpha.md`，值得判断它会不会支持新的 `Rank 6c`，还是反而进一步钉死原 `park`。

## 本轮补读
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/optimization_loop/2026-03-17_1531_rank6-proxy-clean-replication.md`
- `research/park_reframe/2026-04-04_2112_rank6-park-reframe.md`
- `research/quant_digests/2026-04-12_0038_cryptoequity-proxy-impulse-fade-alpha.md`

---

## 1) 原 Rank 为什么 park？
原 `Rank 6` 的主语是：把 `BTC -> COIN/MSTR / US crypto proxy` 写成可直接交易的 `15m` lag-trade / lead-follow entry。

它被 park 的核心原因没有变：
- clean replication 里最不差的 pocket 只停留在低成本档；
- 一旦成本从 `6bps/side` 抬到更诚实档位，三档规则一起转负；
- 时段分桶不稳，`COIN` 与 `MSTR` 的 pocket 也不一致；
- 说明“外部 proxy 有同步/领先信息”不等于“这层信息可以直接当主 entry alpha”。

换句话说，原线失败的主因不是主题完全没信息，而是 **把 proxy 领先硬写成 direct lag-trade entry 这层职责过重**。

## 2) 它更像 hard park 还是 soft park？
本轮判断：**soft park，但继续向 hard park 靠。**

- `soft`：因为 cross-asset proxy 主题本身并未完全失真；
- `更偏 hard`：因为新证据没有把旧 `15m direct follow` 读法救回来，反而进一步说明这层信息更适合迁到别的宿主。

## 3) 有没有“可救信号”？
有，但属于**主题外流型可救信号**，不是旧 rank 本体可救。

本轮新增 digest（`2026-04-12 00:38 UTC`）给出的关键结论不是“追 proxy 有效”，而是：
- `COIN/MARA/RIOT` 的正向 `15m` proxy shock 之后，`BTC/ETH` 下一段 `15m` 更像 **fade** 而不是继续 follow；
- 也就是说，真正站住的更像 **US crypto-equity proxy impulse × BTC/ETH 15m fade** 这条新 raw alpha；
- 它已经不再是“给旧 Rank 6 再加一个更聪明的跟随确认层”，而是把同主题改写成了 **另一条独立的跨资产均值回归 / exhaustion raw-alpha 宿主**。

所以可救信号确实存在，但它指向的是：
- `proxy shock exhaustion fade` 这一条新的 raw-alpha family，
- 而不是旧 `Rank 6` 再诚实地派生一条 `Rank 6c`。

## 4) 最值得改的唯一一刀是什么？
如果只站在旧 `Rank 6` 语义里，唯一还诚实的一刀仍然是：

**把 `direct lag-trade entry` 降级成外部 proxy lead-strength / risk-appetite 的 context-only 角色。**

但这里的关键是：
- 这条唯一修改轴早已被既有 `Rank 6b` 覆盖；
- 4 月 12 日的新 digest 不是在这条轴上给出更好的旧线实现，而是把主题进一步推向“独立 raw alpha（shock fade）”。

因此，本轮不再诚实把“follow -> fade”包装成旧 `Rank 6` 的窄 reframe；那已经是 **主语变了**。

## 5) 是否值得形成新的 derived hypothesis？
**不值得；本轮结论是 `keep_park`。**

原因：
1. 原 `park` 审计意义仍成立，不能推翻；
2. 旧 rank 唯一诚实 residual 仍只是既有 `Rank 6b`（角色降级），没有出现属于旧壳的新单轴增量；
3. 4 月 12 日的新 evidence 已经把主题更明确地推向新的 raw-alpha 宿主：`proxy impulse exhaustion fade`，而不是旧 `BTC -> proxy follow` 家族的窄修改；
4. 若硬写 `Rank 6c`，本质会变成“借同一批变量换了交易方向与 alpha 主语”，这不再是保留原 park 审计意义的窄 reframe。

---

## 本轮模板回答（简版）
- 原 rank 为什么 park：`15m` direct lag-trade 对成本与时间稳定性都不够诚实。
- 更像 hard 还是 soft：`soft park`，但比 4 月 4 日那轮更接近 `hard`。
- 有没有可救信号：有，但它已经外流到新的 `proxy impulse exhaustion fade` raw-alpha 宿主。
- 最值得改的唯一一刀：旧 rank 内唯一还诚实的一刀仍只是把 proxy 信息降级成 context/overlay，而这已被 `Rank 6b` 覆盖。
- 是否值得形成新的 derived hypothesis：不值得，继续 `keep_park`。

## 最终结论
- verdict: **`keep_park`**
- note: 原 `park` 保留；4 月 12 日新证据没有救活旧的 `15m direct lag-follow` 读法，反而更明确地把同主题推向新的 `US crypto-equity proxy impulse × BTC/ETH 15m fade` raw-alpha 宿主，因此当前不诚实 draft `Rank 6c`。

## Git / 执行备注
- 本轮只做最小必要文档改动。
- 工作区存在无关脏文件；为避免混提，本轮不做 selective commit。
