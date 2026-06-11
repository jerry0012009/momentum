# 2026-04-04 23:33 UTC — Rank 9 park reframe review

## 为什么本轮选 Rank 9
- 用户本轮把范围明确钉在 `Rank 1~37` 的已 `park` 条目；本轮据此不再沿用 `50+` 优先。
- `Rank 9` 上次 bot6 park-reframe 是 `2026-03-19 17:50 UTC`，已超过 7 天。
- 期间出现了新的相关旁证：`research/quant_digests/2026-04-02_2214_ema-rsi-regime-hierarchy-trend-alpha.md`，正适合回答一次：这些新证据是在继续支持旧的 `EMA(RSI)-based shared regime veto` 窄派生，还是已经把主题进一步外流到新的单资产 trend-shell raw-alpha 宿主。

## 本轮补读
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/optimization_loop/2026-03-16_2241_regime-switch-stack-intake.md`
- `research/optimization_loop/2026-03-16_2300_regime-switch-clean-replication-park.md`
- `research/park_reframe/2026-03-19_1750_rank9-park-reframe.md`
- `research/quant_digests/2026-04-02_2214_ema-rsi-regime-hierarchy-trend-alpha.md`

---

## 1) 原 Rank 为什么 park？
原 `Rank 9` 的原命题，是把 **regime-switch indicator stack / no-buy-downtrend gate** 写成一条可直接承担交易职责的 standalone entry / stack。

原 `park` 的 authoritative 原因没有变：
- `2026-03-16 23:00 UTC` 的 clean replication 里，最不差的 `regime_gate_only` 在 `6bps/side` 下也只是 `mean_total_return≈-10.28%`，相对 `ema_baseline≈-10.83%` 只是少亏，不够诚实；
- `constrained_no_buy` 并没有形成更干净的 desk 级改善；
- `regime_plus_psar_rsi` 甚至退化到 `0 trade`；
- `Light Stability Pack` 四项（时间 / 参数 / 跨标的 / 成本-交易数）一起 fail。

翻成人话：
不是 `EMA(RSI)` / regime 完全没信息，而是**把它写成一条独立、可承压的交易骨架**这层职责太重了，实验已经把这条读法审计掉了。

## 2) 它更像 hard park 还是 soft park？
本轮判断：**soft park，但比 3 月 19 日那次更偏硬。**

- 仍算 soft，是因为 regime / state-language 这个主题本身没有完全失效；
- 更偏硬，是因为后续新证据越来越不支持“shared regime veto 继续细磨”这条路，而是更支持把这类信息直接写进新的单资产 trend-shell / raw-alpha 宿主。

## 3) 有没有“可救信号”？
有，但本轮的可救信号主要是 **主题外流型**，不是旧 `Rank 9` 本体的新救法。

最 relevant 的新旁证是：
- `research/quant_digests/2026-04-02_2214_ema-rsi-regime-hierarchy-trend-alpha.md`

它给出的关键信息不是“再试一次 shared veto 也许就行”，而是：
1. `EMA(RSI)` 更像一个 **单资产趋势状态机 / hierarchical trend shell**；
2. 最自然的主语是 `uptrend-only trend admission + downtrend loss-protection`；
3. 这更像一条新的 **single-asset regime-conditioned trend raw alpha**，而不是继续服务 `EMA/PSAR continuation + Fib retest_hold + breakout-short` 的 shared asymmetric veto。

也就是说，可救信号还在，但它更像：
- 支持一个新的单资产 trend-shell family；
- 而不是支持在既有 `Rank 9b` 之外，再诚实派生一条 `Rank 9c`。

## 4) 最值得改的唯一一刀是什么？
若只看 `Rank 9` 自己，唯一还诚实的一刀**仍然只是既有那一刀**：

**把 standalone regime-switch stack 降级成 `EMA(RSI)`-based asymmetric shared regime veto。**

但这条唯一修改轴已经在 `Rank 9b` 中被完整保留并写进队列了。

本轮新增论文并没有提供第二条同样诚实、且仍属于旧 `Rank 9` 的主修改轴；它反而把主题继续上移为新的单资产 raw-alpha 宿主。因此本轮不再引入第二刀，也不做多轴扩写。

## 5) 是否值得形成新的 derived hypothesis？
**结论：不值得；本轮 `keep_park`。**

原因：
1. 原 `park` 审计意义仍成立，不能推翻；
2. `Rank 9` 唯一还诚实的窄救法，已经被既有 `Rank 9b` 消费；
3. `2026-04-02` 的新 `EMA(RSI)` hierarchy 证据，主语已经更像新的单资产 trend-shell raw alpha，而不是旧 shared veto 的再细化版本；
4. 若硬写 `Rank 9c`，本质上是在借新的 raw-alpha 宿主给旧 overlay / veto 读法续命，不够诚实。

---

## 本轮模板回答（简版）
- 原 rank 为什么 park：standalone regime-switch entry stack 在收益与稳定性上都不够诚实。
- hard/soft：`soft park`，但比上次更偏硬。
- 可救信号：有，但主要表现为 `EMA(RSI)` 主题外流到新的单资产 trend-shell / raw-alpha family。
- 最值得改的唯一一刀：仍只是既有 `Rank 9b` —— 从 standalone stack 降级成 asymmetric shared regime veto。
- 是否派生：否；不再额外派生 `Rank 9c`。

## 最终结论
- verdict: **`keep_park`**
- note: 原 `park` 保留；`EMA(RSI)` 主题仍有 residual value，但新增 hierarchy 证据说明它更像新的单资产 trend-shell raw-alpha 宿主，而既有 `Rank 9b` 已覆盖旧 rank 唯一诚实的窄 reframe，不足以再诚实派生 `Rank 9c`。

## Git/执行备注
- 本轮只做最小必要文档改动。
- 工作区存在无关脏文件；为避免混提，本轮不做 selective commit。
