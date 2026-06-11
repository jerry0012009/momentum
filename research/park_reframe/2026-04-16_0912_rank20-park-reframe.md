# 2026-04-16 09:12 UTC · Rank 20 park reframe

## Selected rank
- `Rank 20`
- selection note: 属于 `Rank 1~24` 范围；虽然 7 天内看过一次，但这轮有 4 月 11~14 的新证据（stacked order-flow vote、spread-shock completion fade、small-flow/no-large-confirm divergence fade），因此不算无新证据重复复盘。

## Files reviewed
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/optimization_loop/2026-03-17_0326_rank20-price-volume-divergence-park.md`
- `research/park_reframe/2026-03-19_1539_rank20-park-reframe.md`
- `research/park_reframe/2026-04-10_1741_rank20-park-reframe.md`
- `research/quant_digests/2026-04-11_2010_stacked-orderflow-vote-shell.md`
- `research/quant_digests/2026-04-13_1523_spreadshock-imbalance-completion-mr-alpha.md`
- `research/quant_digests/2026-04-14_0006_smallflow-nolargeconfirm-fade-alpha.md`

## 1) 原 rank 为什么 park？
`Rank 20 / price-volume divergence breakout filter` 被 park 的原因已经很清楚：它把“量价背离 warning”写成了一个 `15m breakout` 家族里的共享过滤器，但 clean replication 没给出任何 admission 级证据。

原始 blocker：
- baseline `baseline_mtf_momentum @ 6bps/side`：`mean_total_return≈-38.69%`，`positive_asset_ratio=0/3`
- 主变体 `pvd_break24_delta0.5_warn3 @ 6bps/side`：`mean_total_return≈-39.22%`，`positive_asset_ratio=0/3`
- 时间稳定性 `0/3` 正桶；参数邻域仍整体为负；跨资产 `BTC/ETH/SOL` 全负；成本从 `6 -> 10 -> 15 -> 20bps` 只会更差。

所以原始 `park` 不是“样本太薄暂缓”，而是：**把 divergence warning 直接写成可共享 breakout filter，这个表达已经被审计否掉。**

## 2) 它更像 hard park 还是 soft park？
本轮判断：**`soft park`，但已比 4 月 10 日那轮更接近 `hard park with consumed residual`。**

原因：
- 旧 Rank 20 本体仍不该翻案；
- 唯一还算诚实的 residual 早已被既有 `Rank 20b` 吸收：把它降级成 `volume-price interaction shared admission layer`；
- 而 4 月 11~14 的新证据没有把这条 residual 重新拉回旧壳内，反而继续把主题推向更快、更局部、更 execution-aware 的宿主。

## 3) 有没有“可救信号”？
**有，但不是新的 queue-facing 可救信号。**

这轮新证据说明的不是“旧 Rank 20 还能切出 Rank 20c”，而是：
1. `2026-04-11 stacked-orderflow-vote-shell`：真正有信息的更像 `CVD trend + bar delta + large-trade bias` 这一类 `1m/3m` directional shell；`divergence / absorption` 更像 state-flip / exit helper，而不是 15m shared breakout filter。
2. `2026-04-13 spreadshock-imbalance-completion-mr-alpha`：更值钱的相位已经从“追 breakout 时看量价背离”外流到 `spread-shock completion -> fade` 的 microstructure raw alpha。
3. `2026-04-14 smallflow-nolargeconfirm-fade-alpha`：真正清楚的量价/流分歧 pocket 更像 `small-size taker surge × no-large-flow confirmation -> short-horizon fade`，落点是 `1m~5m` 的 raw alpha，而不是 15m breakout filter。

这些都说明：
- 主题没死；
- 但可救信息量已经不诚实地停留在旧 Rank 20 壳里；
- 它们救活的是**新的 microstructure / trade-size / adverse-selection raw-alpha family**，不是旧 Rank 20。

## 4) 最值得改的唯一一刀是什么？
**唯一还诚实的一刀仍然不变：继续只保留既有 `Rank 20b`。**

也就是：
- `single modification axis = demote standalone price-volume divergence breakout filter into a volume-price interaction shared admission layer`

但这一刀已经在 3 月 19 日起草过，之后也没有出现新的 decisive evidence 说明应该再切一条不同的 `Rank 20c`。本轮新增证据反而在继续削弱“shared admission layer 还值得 queue-facing 保持活跃候选”的必要性。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。最终结论：`keep_park`。**

原因：
- 原 `park` verdict 必须保留；
- 原 residual 已被 `Rank 20b` 消费；
- 4 月新证据虽然给了量价/订单流主题更多生命力，但生命力已经明显迁移到更快的 microstructure raw-alpha 宿主；
- 现在若硬写 `Rank 20c`，只会把已经外流出去的主题重新套回旧 rank，审计意义低、重复度高。

## 6) trade on / trade off（仅保留最小判断）
- `trade on`: 量价/流信息若还有残余，仍更适合在更快书里做 `1m/3m` raw alpha，或最多保留在既有 `Rank 20b` 的薄 admission 语义里。
- `trade off`: 放弃把近期 microstructure 新证据硬解释成旧 Rank 20 的延命材料，也不新增 `Rank 20c`。

## Bot6 verdict
- `verdict`: `keep_park`
- `original park verdict kept`: `yes`
- `park flavor now`: `soft park, but closer to hard with consumed residual`
- `new derived hypothesis`: `none`

## Writeback notes
- 本轮只做最小必要文档更新：新增本日志，更新 `research/park_reframe/INDEX.md` 与 `docs/PARK_REFRAME_QUEUE.md`。
- **未做 git commit**：当前工作区存在大量与本轮无关的脏文件，不适合安全做 selective commit。
