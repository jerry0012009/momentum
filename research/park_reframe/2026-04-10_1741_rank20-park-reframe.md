# 2026-04-10 17:41 UTC · Rank 20 park reframe

## Selected rank
- `Rank 20`
- selection note: 属于 `Rank 1~24` 范围，且最近一次 `bot6` 复盘是 `2026-04-02 21:04 UTC`，已超过 7 天；本轮不碰近期刚看过的 `Rank 15 / 23 / 24`。

## Files reviewed
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/park_reframe/2026-04-02_2104_rank20-park-reframe.md`
- `research/optimization_loop/2026-03-17_0326_rank20-price-volume-divergence-park.md`
- `research/quant_digests/2026-04-08_2249_fillaware-ofi-flowcontrol-shell.md`
- `research/quant_digests/2026-04-10_0322_btcusdt-vwap-ofi-hysteresis-mr-shell.md`
- `research/quant_digests/2026-04-10_1122_toptrader-smartmoney-skew-continuation-alpha.md`

## 1) 原 rank 为什么 park？
`Rank 20 / price-volume divergence breakout filter` 原本想把“量价背离”写成一个可共享的 `15m breakout admission`。但原 clean replication 已把 blocker 审计得比较清楚：
- standalone / shared filter 口径下，post-cost 仍然偏负；
- 改善主要来自砍样本，而不是稳定抬高每笔质量；
- 真正留下的残余信息，更像“量价交互只该做很薄的 admission / sizing layer”，而不是一个足以独立站住的 queue-facing 策略。

所以原 verdict 被压回 `park`，同时只保留了一个更诚实的旧派生：`Rank 20b`（把它降级成 `volume-price interaction shared admission layer`）。

## 2) 它更像 hard park 还是 soft park？
本轮结论：**`soft park`，但比 4 月初更接近 `hard park`**。

原因不是“量价信息彻底没用”，而是：
- 原 Rank 20 的职责层基本已经被证伪；
- 唯一还算诚实的一刀早就收敛到既有 `Rank 20b`；
- 4 月以来的新证据继续把主题往更快、更局部、更 execution-aware 的宿主外流，而不是支持再从旧 Rank 20 里切出一条新的 queue-facing 单轴假设。

## 3) 现有证据里有没有“可救信号”？
有，但很弱，而且**不是新的可救信号**。

仍然成立的只有这条老残余：
- 量价交互更适合做一个薄的 `admission / veto / sizing hint`，而不是 shared hard gate。

但 4 月 8~10 日的新 digest 给出的方向更像：
- `fill-aware OFI × quote-join flow-control shell`
- `VWAP 偏离 × OFI 纠偏 × 5m hysteresis mean-reversion shell`
- `top-trader skew extreme × 1h continuation`

这些证据的共同点是：
1. 主语已经从“15m 量价背离过滤器”变成 **更快的 microstructure / positioning raw alpha**；
2. 真正有信息的变量变成 **OFI、microprice、VWAP 偏离、top-trader skew、fill realism**；
3. Rank 20 原来的“price-volume divergence breakout filter”反而越来越像一个过粗、过上层的旧壳。

所以这里有“主题没死”的可救信号，但它更像**主题外流**，不是 Rank 20 本体可诚实续命。

## 4) 最值得改的唯一一刀是什么？
如果硬要救，**唯一还诚实的一刀仍然不变**：
- 继续把它留在既有 `Rank 20b` 语义里：`demote standalone price-volume divergence breakout filter into a volume-price interaction shared admission layer`

也就是说：
- 不再把它写成 standalone alpha；
- 不再要求它负责主触发；
- 只允许它作为现有 setup 的薄 admission / sizing 参考。

但这条唯一修改轴已经存在，且没有新的 decisive evidence 说明应该再切出 `Rank 20c`。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。最终结论：`keep_park`。**

原因：
- 原 park 结论没有被推翻；
- 旧 residual 已被 `Rank 20b` 吸收；
- 4 月新增证据并没有把 Rank 20 的旧壳救活，只是继续把“量价/流信息”推向更快的 raw-alpha / execution family；
- 若现在再派生 `Rank 20c`，大概率只是把已经外流的主题硬套回旧 rank，审计意义低于重复风险。

## 6) trade on / trade off（仅作不立项说明）
本轮不新 draft，但保留一句最小判断：
- `trade on`：量价信息若还有残余，仍只值得作为共享 admission / sizing 提示；
- `trade off`：放弃把它继续包装成一个 queue-facing 的 shared breakout filter，也不把近期 microstructure 新证据硬写回旧 rank。

## Bot6 verdict
- `verdict`: `keep_park`
- `original park verdict kept`: `yes`
- `park flavor now`: `soft park -> leaning harder`
- `new derived hypothesis`: `none`

## Writeback notes
- 本轮只做最小必要文档更新：新增本日志，更新 `research/park_reframe/INDEX.md` 与 `docs/PARK_REFRAME_QUEUE.md`。
- **未做 git commit**：当前工作区存在大量与本轮无关的脏文件（docs / artifacts / paper runners / systemd 等），不适合安全做 selective commit。
