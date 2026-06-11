# 2026-04-20 12:41 UTC — Rank 6 park reframe review

## 为什么本轮选 Rank 6
- 本轮继续只处理 `Rank 1~37` 中已 `park` 的 1 条。
- `Rank 6` 上次 park-reframe 复盘是 `2026-04-12 03:56 UTC`，已超过 `7` 天。
- 期间出现了新的更贴题旁证：`research/quant_digests/2026-04-20_0028_btc-alt-lagged-transmission-alpha.md`。需要判断它会不会支持新的旧线窄 reframe，还是进一步把原 `park` 钉死。

## 本轮补读
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/optimization_loop/2026-03-17_1531_rank6-proxy-clean-replication.md`
- `research/park_reframe/2026-04-12_0356_rank6-park-reframe.md`
- `research/park_reframe/2026-04-04_2112_rank6-park-reframe.md`
- `research/quant_digests/2026-04-20_0028_btc-alt-lagged-transmission-alpha.md`
- `research/quant_digests/2026-04-19_0224_crossmarket-intraday-tsmom-breadth-basket-alpha.md`

---

## 1) 原 Rank 为什么 park？
原 `Rank 6` 的主语是：把 `BTC -> COIN/MSTR / US crypto proxy` 写成可直接交易的 `15m` lag-trade / lead-follow entry。

它被 park 的核心原因仍然没变：
- clean replication 里只在最低成本档留下薄 pocket；
- 成本从 `6bps/side` 往更诚实档位一抬，三档规则一起转负；
- `COIN` 与 `MSTR` 的 time-bucket 表现不一致，中段 pocket 也不稳；
- 说明“外部 proxy 先动”不等于“这层信息足以直接当 queue-facing 主 entry alpha”。

更直白地说：原线失败的主因不是外部 proxy 完全没信息，而是 **把 proxy 领先硬写成 `15m` direct lag-follow entry，这层职责过重**。

## 2) 它更像 hard park 还是 soft park？
本轮判断：**`soft park`，但比 4 月 12 日那轮更接近 `hard`。**

- 仍算 `soft`：因为 lead-lag / price-discovery 主题本身没有完全失真；
- 更接近 `hard`：因为新增证据继续表明，真正还活着的是更快、更窄、更偏 raw-alpha 的宿主，而不是旧 `15m` direct follow 读法。

## 3) 现有证据里有没有“可救信号”？
有，但仍然是**主题外流型可救信号**，不是旧 rank 本体可救。

本轮最关键的新旁证是 `2026-04-20_0028_btc-alt-lagged-transmission-alpha.md`：
- 它支持的是 **`BTC 先动 × 低交易笔数 ALT 在接下来 1~3m 延迟补跟`**；
- 它的主战场是 `1m/3m`、低 trade-count ALT、spot / 更轻执行环境；
- 它描述的是 **信息传导延迟 raw alpha**，不是 `BTC -> COIN/MSTR` 这类 US crypto-equity proxy 的 `15m` 直跟随。

这条新 evidence 的意义不是“旧 Rank 6 只要再改聪明一点就能救活”，而是：
- lead-lag 主题确实还有 residual；
- 但 residual 更像 **新的 faster-clock BTC→ALT catch-up raw-alpha family**；
- 已经不诚实再包装成 old `Rank 6` 的 `Rank 6c`。

`2026-04-19_0224_crossmarket-intraday-tsmom-breadth-basket-alpha.md` 也提供了一个辅助收口：
- cross-market 同步信息若有价值，更像 `15m` broad-breadth long basket 这种完整 continuation shell；
- 也不是旧 `Rank 6` 那种单条 proxy 领先、单名 lag-follow entry 的语义。

## 4) 最值得改的唯一一刀是什么？
如果只站在旧 `Rank 6` 语义里，唯一还诚实的一刀仍然只有：

**把 `direct lag-trade entry` 降级成外部 lead-strength / risk-appetite 的 context-only 角色。**

但关键在于：
- 这条唯一主修改轴已经被既有 `Rank 6b` 消费；
- 本轮新证据没有给出“旧壳内更好的同轴实现”；
- 它给出的其实是另一个宿主：`BTC shock × low-trade-count ALT delayed follow`。

所以本轮不应把“外部 proxy lead-follow”再硬切一刀，而应承认：**旧 rank 的唯一诚实 residual 仍只到 `Rank 6b` 为止。**

## 5) 是否值得形成新的 derived hypothesis？
**不值得；本轮结论是 `keep_park`。**

原因：
1. 原 `park` 审计意义仍成立，不能推翻；
2. 旧 rank 唯一诚实 residual 仍只是既有 `Rank 6b`，没有出现属于旧壳的新单轴增量；
3. 4 月 20 日的新 lead-lag 证据虽然更强，但它支持的是 `1m/3m` 低流动性 ALT catch-up raw alpha，不是旧 `BTC -> US proxy follow` 语义；
4. 若硬写 `Rank 6c`，本质会变成“借同一类 lead-lag 题材，换标的、换时钟、换 alpha 主语”，这已不是保留原 `park` 审计意义的窄 reframe。

---

## 本轮模板回答（简版）
- 原 rank 为什么 park：`15m` direct lag-follow 对成本、跨标的与时间稳定性都不够诚实。
- 更像 hard 还是 soft：`soft park`，但比 4 月 12 日更接近 `hard`。
- 有没有可救信号：有，但它外流到新的 `BTC shock × low-trade-count ALT delayed follow` raw-alpha 宿主。
- 最值得改的唯一一刀：旧 rank 内唯一还诚实的一刀仍只是把 proxy 信息降级成 context/overlay，而这已被 `Rank 6b` 覆盖。
- 是否值得形成新的 derived hypothesis：不值得，继续 `keep_park`。

## 最终结论
- verdict: **`keep_park`**
- note: 原 `park` 保留；4 月 20 日新增的 BTC→低交易笔数 ALT 延迟跟随证据继续说明 lead-lag 主题仍有信息，但它救活的是新的 faster-clock raw-alpha family，而不是旧 `Rank 6 / BTC->US crypto proxy 15m direct follow` 读法，因此当前不诚实 draft `Rank 6c`。

## Git / 执行备注
- 本轮只做最小必要文档改动。
- 工作区存在大量无关脏文件；为避免混提，本轮不做 selective commit。
