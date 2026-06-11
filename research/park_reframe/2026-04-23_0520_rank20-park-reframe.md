# 2026-04-23 05:20 UTC · Rank 20 park reframe

## Selected rank
- `Rank 20`
- selection note: 本轮继续严格限定在 `Rank 1~37` 的已 `park` 条目内。`Rank 20` 上次复盘是 `2026-04-16 09:12 UTC`，虽仍接近 `7` 天窗口，但 4 月 20~22 又新增了两条更贴近 microstructure / order-flow 的 quant digest，可用于回答一个更具体的问题：这些新证据是否真的能把 old `Rank 20` 再诚实切出新的窄 residual，还是只是继续把主题外推到更快、更 execution-aware 的新宿主。

## Read set
必读：
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`

补充：
- `research/park_reframe/2026-04-16_0912_rank20-park-reframe.md`
- `research/optimization_loop/2026-03-17_0326_rank20-price-volume-divergence-park.md`
- `research/optimization_loop/2026-04-09_1115_rank20b_fresh_intake_background_absorbed.md`
- `research/quant_digests/2026-04-20_1945_hawkes-lob-excitation-baseimbalance-alpha.md`
- `research/quant_digests/2026-04-22_1634_ofi-kalman-maker-skew-alpha.md`

## 1) 原 rank 为什么 park？
原 `Rank 20 / price-volume divergence breakout filter` 的 `park` 理由没有变化：

- clean replication（`2026-03-17_0326_rank20-price-volume-divergence-park.md`）里，old Rank 20 想做的是把“breakout 时的量价背离 warning”写成 `15m breakout` 家族的 shared filter；
- 但这条表达没有拿到任何 admission 级证据，反而连 baseline 都没跑赢。

冻结审计结果仍然很清楚：
- baseline `baseline_mtf_momentum @ 6bps/side`：`mean_total_return≈-38.69%`，`positive_asset_ratio=0/3`
- 主变体 `pvd_break24_delta0.5_warn3 @ 6bps/side`：`mean_total_return≈-39.22%`，`positive_asset_ratio=0/3`
- 时间稳定性 `0/3` 正桶；参数邻域整体仍负；`BTC/ETH/SOL` 跨资产一起失败；成本从 `6 -> 10 -> 15 -> 20bps` 只会更差。

所以原 rank 被 park 的核心不是“实现还粗一点”，而是：

> **把 price-volume divergence 直接写成 `15m breakout` shared filter，这层主语已经被审计否掉。**

## 2) 它更像 hard park 还是 soft park？
**本轮判断：仍是 `soft park`，但比 2026-04-16 那轮更接近 `hard park with consumed residual`。**

为什么仍保留 `soft`：
- 量价/订单流分歧主题本身没死；
- 新证据继续说明“flow state + imbalance + markout”在更快时钟仍然有信息。

为什么更接近 `hard`：
- 这组信息已经越来越明显地活在 `1m/3m` microstructure raw-alpha / child-execution 宿主里；
- old `Rank 20` 唯一诚实 residual 早就只剩既有 `Rank 20b`，而 `Rank 20b` 又已在 `2026-04-09` first verdict 收口为 `background / P0 / absorbed`。

换句话说：
> 主题活着，但 old `Rank 20` 这具壳子里的 residual 已经越来越被消费完。

## 3) 有没有“可救信号”？
**有，但仍然不是 old `Rank 20` 级别的可救信号。**

### A. 4 月 20 日 Hawkes LOB 证据
`2026-04-20_1945_hawkes-lob-excitation-baseimbalance-alpha.md` 给出的最强启示是：
- 真正有信息的是 `event-time excitation state × base imbalance signed drift`；
- 这条 alpha 先回答“什么时候盘口进入高激发、可交易状态”，再回答“更可能往哪边动”；
- 它天然属于超短微结构层，而不是 `15m breakout` 上的 divergence warning。

这说明 flow / imbalance 主题若还值得追，更像：
- 新的 `1m/3m` event-time raw alpha；或
- 父策略底下的 urgency / admission / child-execution layer。

不是 old `Rank 20` 再切一个 `Rank 20c` 就能承接。

### B. 4 月 22 日 OFI / Kalman maker-skew 证据
`2026-04-22_1634_ofi-kalman-maker-skew-alpha.md` 进一步把方向说得更清楚：
- `OFI / microprice / fair-value skew` 的 edge 确实存在；
- 但它的更诚实岗位是 `maker-first quote skew + markout control + child execution`；
- 不适合伪装成新的 `5m/15m` 方向主信号，更不适合回头给 old `Rank 20` 续命。

这说明近期“量价分歧”的真正生存位置，已经从：
- `15m breakout filter`

外流到：
- `1m/3m microstructure raw alpha`
- `execution / markout / maker-skew overlay`

### 小结
所以本轮的真实回答是：
- **有可救信号，但是主题级可救，不是旧 rank 级可救；**
- 它们在继续证明“订单流 / imbalance / participation-quality 有信息”；
- 但这些信息已经不诚实地停留在 old `Rank 20` 的宿主里。

## 4) 最值得改的唯一一刀是什么？
**对 old `Rank 20` 来说，最值得改的唯一一刀仍然只有既有 `Rank 20b`，没有出现新的唯一主修改轴。**

也就是：
- `single modification axis = demote standalone price-volume divergence breakout filter into a volume-price interaction shared admission layer`

但这条轴已经：
1. 在 `2026-03-19` 被正式 draft 成 `Rank 20b`；
2. 在 `2026-04-09` 被 first verdict 判为 `background / P0 / absorbed`；
3. 被后续更快的 microstructure / execution 证据继续上移、继续吸收。

因此本轮不能诚实再写一个：
- `Rank 20c = Hawkes state version`
- `Rank 20c = OFI maker-skew version`

因为那已经不是 old `Rank 20` 的单轴窄 reframe，而是在换：
- 时钟
- 观测层级（bar -> L2/event-time）
- 执行语义（shared filter -> maker-first child execution / raw alpha）

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论：`keep_park`。**

原因：
1. 原 `park` verdict 没有被推翻；
2. 唯一诚实 residual 仍只到既有 `Rank 20b`；
3. `Rank 20b` 已经在 runtime 中被判为 `background / P0 / absorbed`；
4. 4 月 20~22 的新证据继续把量价/流主题推向新的 microstructure raw-alpha / child-execution 宿主，而不是把 old `Rank 20` 拉回 queue-facing。

## 6) 单轮模板回答
### 原 rank 为什么 park？
因为把 `price-volume divergence warning` 写成 `15m breakout` shared filter 后，clean replication 在 baseline、时间、参数、跨资产、成本五个维度一起失败，没有形成 admission 级证据。

### 它更像 hard park 还是 soft park？
`soft park`，但比 4 月 16 日那轮更接近 `hard park with consumed residual`。

### 现有证据里是否存在“可救信号”？
有，但只是主题级：新证据证明 flow / imbalance / markout 在 `1m/3m` microstructure 与 maker-first execution 层仍有信息，不是 old `Rank 20` 本体可救。

### 最值得改的唯一一刀是什么？
仍只有既有 `Rank 20b`：把 standalone divergence breakout filter 降级成 volume-price interaction shared admission layer。

### 是否值得形成新的 derived hypothesis？
不值得；本轮继续 `keep_park`。

## Final verdict
- `verdict`: `keep_park`
- `original_verdict_kept`: `park`
- `park_type_read`: `soft park，但比 2026-04-16 那轮更接近 hard park with consumed residual`
- short note: `4 月 20~22 的 Hawkes LOB excitation×base-imbalance 与 OFI/Kalman maker-skew 新证据继续说明：量价/订单流主题还活，但真正可救的是新的 1m/3m microstructure raw-alpha 或 child-execution 宿主，而不是旧 Rank 20 的 15m divergence breakout filter；旧 rank 的唯一诚实残余仍只到既有 Rank 20b。`

## Minimal audit note
本轮没有推翻原 `park`，也没有改写 `TODO`。只是进一步确认：
- 量价/订单流主题值得继续研究；
- 但应作为新的 microstructure / execution family 去追，而不是继续在 old `Rank 20` 名下硬切 `Rank 20c`。

## Git
- 未做 commit。
- 原因：工作区存在大量与本轮无关的共享脏文件 / 未跟踪文件；本轮只做最小必要文档更新与邮件交付，避免混提。
