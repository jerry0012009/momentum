# 2026-03-24 08:20 UTC｜bot6 park-reframe｜Rank 22

## 0) 本轮选择（为什么是 Rank 22）
- 本轮只处理 `Rank 1~37` 中已 `park` 的 1 条，不改 `TODO` 顶部排班，不替 `bot2 / bot3` 分配任务。
- 严格说，`Rank 22` 在最近 `7` 天内已经被 `bot6` 复盘过；正常应优先换别的。
- 但这次有两条更直接相关的新旁证：
  - `research/quant_digests/2026-03-23_0205_orb-phase-retest-score-not-hard-gate.md`
  - `research/quant_digests/2026-03-23_0031_caizongxun-hammer-engulf-retest-asymmetric-gate.md`
- 所以这轮只回答一件事：这些新证据，是否足以让原 `Rank 22 / up-down wave + MA20 persistence gate` 派生出一条新的窄 reframe hypothesis。

## 1) 原 Rank 为什么 park？
原始硬结论来自：
- `research/optimization_loop/2026-03-17_0437_rank22-clean-replication-park.md`
- `research/park_reframe/2026-03-20_1410_rank22-park-reframe.md`

原 Rank 22 的定义是：
- 保留 `baseline multi-tf momentum` 方向层；
- 只有当最近 4 根收盘连续站在 `MA20` 同侧，并满足 `upwave / downwave` 形态时才允许入场。

原 park 证据仍然很硬：
- 主变体 `updownwave_ma20` 在 `6bps/side` 下约 `-7.94%`，`positive_asset_ratio = 1/3`；
- 邻域最不差的 `MA15` 也只有约 `-3.26%`，只是少亏；
- 时间稳定性里 `bucket_2 ≈ -12.70%`，没有稳定覆盖；
- 跨资产只剩 `SOL` 单腿为正，`BTC / ETH` 都明显为负；
- 成本抬到 `10 / 15 / 20bps` 后继续恶化到约 `-27.51% / -46.17% / -59.98%`。

翻成人话：
- 原线失败的不是“恢复 / 持续性主题彻底没信息”；
- 而是**把 `up/down wave + MA persistence` 写成 standalone queue-facing gate 这版职责，不成立。**

## 2) 它更像 hard park 还是 soft park？
- **结论：仍更像 `soft park`。**

原因：
- `恢复 / 回踩后重新站稳 / 持续性确认` 这个主题本身没死；
- 但 Rank 22 这版把它写成“方向层 + 形态层一起直接放行”的方式，已经被审计成太粗；
- 它更像一个可能只适合服务 long-side recovery admission 的残余信号，而不是还值得单独挂号的一条完整线。

## 3) 有没有“可救信号”？
- **有，但仍然偏弱，而且更像在收紧角色，不像在打开新派生。**

这轮新增旁证真正增加的信息是：

### a) `orb-phase-retest-score-not-hard-gate`
它说明活下来的不是“conservative retest 自己单独扛逻辑”，而是：
- `breakout -> retest -> bounce` 三阶段状态机；
- 配合 `timeout / abort`；
- 再加一个廉价 `score` 来做质量分层。

这对 Rank 22 的启发不是“wave persistence 可以重回 standalone”，而是：
- 如果还要保留这类信息，更像该降级成 **recovery phase / bounce-quality admission layer**。

### b) `hammer-engulf-retest-asymmetric-gate`
它说明 `hammer / engulf` 这类回踩形态在 `15m` 上：
- 更像 **long-side 回踩质量门**；
- 不像对称共享 gate；
- 而且改善主要来自 long 侧，short 侧并不成立。

这与 Rank 22 自身留下的残余信息是同向的：
- 真正可能有一点点信息的，不是 `up/down wave` 作为完整开仓键；
- 而是 **long-side recovery / bounce 质量**。

## 4) 最值得改的唯一一刀是什么？
如果只保留一刀，本轮最诚实的唯一修改轴会是：

**把 `standalone up/down wave + MA persistence gate` 进一步降级成 long-side recovery phase admission layer（强调 bounce + timeout，而不是 standalone 入场）。**

也就是：
- 不再让 Rank 22 自己决定完整 entry；
- 只在已有 long 侧 setup 触发后，额外要求一次“先回踩、再收回、并在短窗口内保持”的 recovery 状态；
- 第一刀若真要测，也只能测 `baseline vs recovery-phase long admission`，不能顺手叠第二轴。

## 5) 是否值得形成新的 derived hypothesis？
- **不值得。**
- 最终 verdict：`keep_park`

原因：
1. 原 `park` 的主 blocker 没被推翻；
2. 新证据只是在继续说明：Rank 22 的残余价值更像 **long-side recovery admission**，不是 standalone gate；
3. 这条最自然的救法，和 `Rank 17` 已在跑的 `pullback recovery confirmation` 主旨高度重叠；
4. 同时又与近期 `EMA close reclaim`、`RSI state-machine admission`、`phase-state retest+bounce` 这些 digest 的 long-side admission 语言同向；
5. 现在硬写一个 `Rank 22b`，很大概率只是把同一主题换壳重讲，不够诚实，也会稀释原 `park` 的审计边界。

## 6) 本轮结论（按模板）
1. **原 rank 为什么 park？**
   - 因为 clean replication 后，它只是少亏，不是转正；跨资产、时间、参数、成本四个角度都不够诚实。
2. **更像 hard park 还是 soft park？**
   - `soft park`。
3. **有没有可救信号？**
   - 有；但它更像 long-side recovery / bounce-quality admission 残余信息，不像 standalone rescue。
4. **最值得改的唯一一刀是什么？**
   - 把 `up/down wave + MA persistence` 降级成带 `bounce + timeout` 的 long-side recovery phase admission layer。
5. **是否值得形成新的 derived hypothesis？**
   - 不值得。
6. **为什么不立 `Rank 22b`？**
   - 因为这条最自然的窄救法已被 `Rank 17` 与近期 long-side admission 系列 digest 大幅消费；现在再立新号，审计收益低于重复风险。

## 7) 允许的最终结论
- `keep_park`

## 8) 最小审计结论
- 原 `park` 保留；
- `Rank 22` 本轮仍读作 **soft park**；
- 2026-03-23 的 `phase-retest-bounce+score` 与 `hammer/engulf` 新证据，只进一步说明它的残余价值应被压到 long-side recovery admission 层，不足以单独派生 `Rank 22b`。

## 9) 相关证据锚点
- `research/optimization_loop/2026-03-17_0437_rank22-clean-replication-park.md`
- `research/park_reframe/2026-03-20_1410_rank22-park-reframe.md`
- `research/quant_digests/2026-03-23_0205_orb-phase-retest-score-not-hard-gate.md`
- `research/quant_digests/2026-03-23_0031_caizongxun-hammer-engulf-retest-asymmetric-gate.md`

## 10) Git
- 未 commit。
- 原因：workspace 仍存在大量与本轮无关的脏文件 / 未跟踪文件；本轮只做最小必要文档改动，不安全混提。
