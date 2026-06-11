# 2026-04-12 14:01 UTC — Rank 9 park reframe review

## 为什么本轮选 Rank 9
- 本轮用户把范围明确钉在 `Rank 1~37` 的已 `park` 条目；因此不沿用 `50+` 优先。
- `Rank 9` 上次 bot6 park-reframe 是 `2026-04-04 23:33 UTC`，已超过 `7` 天窗口。
- 它同时满足两点：
  1. 原 rank 已有明确 authoritative `park` 审计结论；
  2. 既有 `Rank 9b` 已经把唯一诚实残余写成 queue-facing 提案，因此这轮很适合回答：**最近这段时间里，旧 Rank 9 是否还值得继续派生 `Rank 9c`，还是应该承认 residual 已经被消费完。**

## 本轮补读
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/park_reframe/2026-03-19_1750_rank9-park-reframe.md`
- `research/park_reframe/2026-03-28_2304_rank9-park-reframe.md`
- `research/park_reframe/2026-04-04_2333_rank9-park-reframe.md`
- `research/quant_digests/2026-04-02_2214_ema-rsi-regime-hierarchy-trend-alpha.md`

## 1) 原 Rank 为什么 park？
原 `Rank 9` 的问题，从来不是“regime / EMA(RSI) 主题完全没信息”，而是它被写成了一条 **standalone regime-switch indicator-stack entry**。

原 `park` 原因依然成立：
- clean replication 里，最不差的 `regime_gate_only` 在 `6bps/side` 下也只是 `mean_total_return≈-10.28%`，相对 baseline 只是少亏；
- 更重的 `regime_plus_psar_rsi` 直接退化到 `0 trade`；
- 时间、参数、跨标的、成本/交易数等稳定性检查一起失败。

所以它被 `park`，不是因为“判势”这个动作没意义，而是因为：
**把 regime-switch stack 当成一条独立可承压的交易骨架，这件事已经被审计掉了。**

## 2) 它更像 hard park 还是 soft park？
本轮判断仍是：**soft park，但比 4 月 4 日那轮又更偏硬一点。**

原因：
- 仍算 soft，是因为 `EMA(RSI)` / regime language 这个主题没有完全失效；
- 更偏硬，是因为这段时间并没有出现新的 decisive evidence，能把旧 Rank 9 从“shared veto residual”重新救回 queue-facing 的独立修改轴；
- 相反，现有最相关的新旁证仍然是 `2026-04-02` 那篇 hierarchy digest，而它支持的更像 **新的单资产 trend-shell / raw-alpha 宿主**，不是旧 Rank 9 再派生一刀。

## 3) 有没有“可救信号”？
有，但可救信号并没有新增，仍然只剩 **既有 `Rank 9b` 那一条残余**。

也就是：
- `EMA(RSI)` 更适合做 **asymmetric shared regime veto**；
- long-side continuation / retest 更像应该在 `ema_rsi7 > 60` 这类 uptrend 区间里放行；
- short-side setup 更适合在 `ema_rsi7 < 40` 一类 downtrend 区间里优先；
- 中性区更像 abstain / veto / half-size，而不是继续硬当 entry stack。

但这条“可救信号”不是新的。它已经被：
- `2026-03-19` 的 `Rank 9b`
- `2026-03-28` / `2026-04-04` 的两轮复盘
完整固定下来了。

换句话说：
**可救信号还在，但没有长出第二条新轴。**

## 4) 最值得改的唯一一刀是什么？
如果只允许一刀，答案仍然不变：

**把 standalone regime-switch stack，降级成 `EMA(RSI)`-based asymmetric shared regime veto。**

这就是既有 `Rank 9b`。

本轮没有看到比这更诚实、且仍属于旧 `Rank 9` 的第二刀：
- 若继续强调 hierarchy / trend-shell，那主语已经变成新的 raw-alpha 宿主；
- 若继续写 shared veto，本质上又只是把 `Rank 9b` 改写一遍。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。**

本轮最终结论：`keep_park`

原因：
1. 原 `park` verdict 的审计意义完全保留；
2. 原 Rank 9 唯一诚实的窄救法，已经被既有 `Rank 9b` 表达；
3. 最近这几天没有新的 decisive evidence，足以支持再派生 `Rank 9c`；
4. 如果现在硬写 `Rank 9c`，大概率只会变成：
   - 要么把 `Rank 9b` 换种说法重复一次；
   - 要么借新的 single-asset trend-shell 主题给旧 overlay 续命。

这两种都不够诚实。

## 简版回答
- 原 rank 为什么 park：因为 standalone regime-switch entry stack 在 post-cost 收益与稳定性上都不成立。
- 更像 hard 还是 soft：`soft park`，但继续向 hard 靠。
- 有没有可救信号：有，但仍只剩既有 `Rank 9b` 这一条 residual。
- 最值得改的一刀：仍然只是 `standalone stack -> EMA(RSI) asymmetric shared veto`。
- 是否值得形成新的 derived hypothesis：**否**。

## 最终结论
- verdict: **`keep_park`**
- note: 原 `park` 保留；`EMA(RSI)` 主题仍有 residual value，但这条 residual 已被既有 `Rank 9b` 完整覆盖，而近几天没有新的 decisive evidence 支持再诚实派生 `Rank 9c`。

## 文件/执行备注
- 本轮只做最小必要写回：本日志、`research/park_reframe/INDEX.md`、`docs/PARK_REFRAME_QUEUE.md`。
- 默认不改 `docs/TODO.md` 顶部排班。
- 工作区存在无关脏文件；本轮不做 selective commit。
