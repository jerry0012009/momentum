# 2026-04-17 16:06 UTC｜bot6 park-reframe｜Rank 23

## 0) 本轮选择
- 选定：`Rank 23 / volatility regime mid-band / cost-survival gate`
- 轮转说明：近期 `50+` 与 `80~110` 已连续覆盖，本轮回到 `1~24`；`Rank 23` 上次 bot6 复盘是 `2026-04-10 10:16 UTC`，本次正好跨过 7 天窗口，且有 4/16~4/17 新证据可对照，不属于无新意重复复盘。

## 1) 原 rank 为什么 park？
原 `park` verdict 不变。

根据 `2026-03-17_0503_rank23-clean-replication-park.md`，原线被压回 `park` 的决定性原因仍是：
- 它没证明自己能作为 **standalone 15m shared entry gate** 成立；
- `rv_midband_q20_80`、`rv_midband_q30_70` 两个主近邻在 `BTC/ETH/SOL` 上仍全部成本后为负；
- `time stability=0/3`、参数近邻最优仍为负、`10/15/20bps` 成本阶梯继续恶化；
- 所以问题不是“阈值再调一下就会转正”，而是 **把 realized-vol mid-band 放在了错误职责层**。

翻成人话：
- 它可能留下了一点“何时更难做”的信息；
- 但没有证明自己能独立决定“这根 15m bar 该不该做”。

## 2) 它更像 hard park 还是 soft park？
- **本轮判断：`soft park`，但比 4 月 10 日那轮更接近 `hard park with consumed residual`。**

原因：
- 软的一面：`vol / liquidity / tradeability` 主题本身当然没有失效；
- 硬的一面：新证据进一步说明，真正有价值的并不是旧 Rank 23 这条 `mid-band gate` 写法，而是更上位的 **liquidity-adjusted / regime-scaled raw-alpha 或 execution overlay** 宿主。

## 3) 有没有“可救信号”？
- **有，但可救信号继续远离旧 Rank 23 本体。**

这次主要对照的新增旁证：
- `research/quant_digests/2026-04-16_0639_liquiditybeta-armagarch-ts-alpha.md`
  - 新证据保留下来的主语不是“中波动带 allow/deny gate”，而是 **liquidity-adjusted return sign** 这条更完整的时序 raw alpha；
  - volatility / liquidity 信息在这里扮演的是建模主语或风险缩放层，而不是一个薄的 shared mid-band gate。
- `research/quant_digests/2026-04-17_0439_regimeaware-xsmomentum-btcvol-overlay.md`
  - 新证据也在把 `BTC realized vol / dispersion` 往 **veto / size-down / exposure-scaling** 的角色上推；
  - 这再次说明：状态层若还有 residual，更像服务于一个已成立 base alpha，而不是单独扛 entry gate。

所以，`Rank 23` 还能留下的“可救信号”依然只有：
- 波动 / 流动性 / market-quality 信息确实会影响成本生存；
- 但这更像 **tradeability / execution / exposure scaling family** 的语义残留，不像值得继续以 `Rank 23b` 名义 queue-facing 存活的对象。

## 4) 最值得改的唯一一刀是什么？
**唯一还诚实的一刀，仍只有：把 standalone `realized-vol mid-band gate` 彻底降级成 shared tradeability / execution veto-or-size-down overlay。**

也就是：
- 不再让它自己决定开仓；
- 只在别的 base alpha 已触发时，额外判断当前是否处在高摩擦 / 高脆弱 / 低性价比的执行区间；
- 第一刀如果未来真要测，也只能是 `baseline vs veto-only / size-down-only`，不能偷带第二轴。

## 5) 是否值得形成新的 derived hypothesis？
- **本轮结论：`keep_park`。**

原因：
1. 原 `park` 审计对象是 `standalone realized-vol mid-band shared gate`，这个失败没有被推翻；
2. 4/16~4/17 新证据没有把它拉回原主题，反而继续把 residual 上移到更完整的 `liquidity-adjusted raw alpha / vol-scaled overlay` 宿主；
3. 若现在硬写 `Rank 23b`，大概率只是把“tradeability 语义残留”误包装成 queue-facing 候选；
4. bot6 这轮最诚实的动作仍然是保留原 `park` 审计意义，而不是再 draft 一个名不副实的 `23b`。

## 6) 小结
- 原 rank 为什么 park：因为 standalone `mid-band gate` 在收益、时间、参数、跨资产、成本五层都没站住。
- 更像 hard 还是 soft：`soft park`，但比上次更接近 `hard with consumed residual`。
- 有没有可救信号：有，但只剩 tradeability / liquidity / vol-scaling 语义，不再属于旧 gate 本体。
- 最值得改的一刀：降级成 shared execution-veto / size-down overlay。
- 是否值得形成新的 derived hypothesis：**现在不值得**。
- `trade on`：利用波动/流动性状态，少在执行最差窗口里硬做薄 edge。
- `trade off`：它不再是旧 Rank 23 的 queue-facing gate，而且很容易退化成“砍单美化”。

## 7) 本轮结论
- `keep_park`
- 补充口径：`soft park，但比 4 月 10 日那轮更接近 hard with consumed residual；4 月 16~17 日新增的 liquidity-adjusted / BTC-vol scaling 证据继续说明，Rank 23 若还有 residual value，也更像新的 liquidity-aware raw-alpha / execution overlay 宿主，而不是足以再诚实派生旧 Rank 23 的 Rank 23b。`

## 8) 文件动作
- 新增：`research/park_reframe/2026-04-17_1606_rank23-park-reframe.md`
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`
- 未改：`docs/TODO.md`

## 9) commit
- 默认不做 commit。
- 原因：工作区存在大量与本轮无关的历史脏文件 / 未跟踪文件；本轮只做最小必要文档改动。
