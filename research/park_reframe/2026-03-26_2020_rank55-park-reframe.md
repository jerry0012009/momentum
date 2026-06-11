# 2026-03-26 20:20 UTC｜bot6 park-reframe｜Rank 55

## 0) 本轮选择（为什么是 Rank 55）
- 按 `docs/PARK_REFRAME_QUEUE.md` 的默认轮转，当前仍优先 `50+`；最近 `7` 天 bot6 已覆盖 `50~54` 中的 `50/51/52/53/54`，但 **`Rank 55` 尚未被单独复盘**，符合“优先换别的”原则。
- `Rank 55 / order-imbalance crash-risk overlay` 是典型的“原 rank 已 park，但看起来像还留了一点 microstructure 风险信息”的条目，适合审计：这点残余到底值不值得诚实地切成新的窄 reframe hypothesis。
- 本轮目标不是推翻原 `park`，而是回答：**原 Rank 55 的残余信息，究竟还属于 `Rank 55` 自己，还是已经更适合被新的 `1m/3m` microstructure raw-alpha family 吸收。**

## 1) 原 Rank 为什么 park？
原始证据来自：
- `research/optimization_loop/2026-03-18_1142_rank55-crash-risk-intake.md`
- `research/optimization_loop/2026-03-18_1249_rank55-clean-replication.md`
- `research/optimization_loop/2026-03-18_1348_rank55-time-stability-park.md`

原 Rank 55 的核心写法是：
- 不把 order-imbalance 当独立方向 alpha；
- 而是把它写成一个 **shared crash-risk overlay**，服务现有 `breakout-short / Fib retest_hold / EMA-PSAR` 三条主线；
- 也就是：当 setup 前的短窗主动成交失衡、flow shock、下行动量一起提示 crash-prone 时，决定是放行、减仓还是 veto。

它最后被 park，原因很清楚：
1. clean replication 里，它只在部分 archetype 上留下局部改善，不具备跨 setup 一致性：
   - `ema_psar_long`：`base≈+1.63% -> binary_crash_gate≈+3.15%`
   - `fib_retest_long`：几乎无增量（`≈+0.03% -> ≈0.00%`）
   - `breakout_short`：虽有一点少亏（`≈-2.49% -> ≈-1.88%`），但仍是负值
2. time stability 再检查后，问题更明确：
   - `breakout_short` 三个时间窗口全部非正；
   - `fib_retest_long` 只剩贴近噪音的小正值；
   - 唯一三段窗口都为正的是 `ema_psar_long + binary_crash_gate`，但平均每桶交易数仅约 `1.7~2.7`。
3. 也就是说，原 Rank 55 没证明“microstructure crash-risk overlay”能成为一个跨 setup、可迁移的 queue-facing 过滤层；
4. 它只留下一个**很薄的 `EMA/PSAR long` 专属 pocket**，不够支撑继续升格。

翻成人话：
- 原 Rank 55 并不是完全没抓到东西；
- 它确实碰到一点“短窗 flow 压力可能提示别太早做 long / 或该更保守”的信息；
- 但这点信息既不够广，也不够稳，更不像一个值得单独继续排队的 `15m shared overlay`。

## 2) 它更像 hard park 还是 soft park？
**结论：`soft park`，但偏硬。**

为什么不是 hard park：
- 它不是纯噪音；
- `ema_psar_long` 上确实出现过一点改善；
- 说明 order-imbalance / flow shock 这类 microstructure 变量，本身并没有彻底失效。

为什么又说“偏硬”：
- 改善高度局限在单一 archetype；
- 一旦要求跨 setup / 时间稳定，就明显塌掉；
- 若继续往前救，最自然的方向已不再像 “Rank 55 这个 15m shared crash overlay”，而更像一条新的、更快时钟的 raw alpha family。

所以它不是主题完全死掉，而是 **原 Rank 55 这版角色分配基本走到头了**。

## 3) 有没有“可救信号”？
**有，但它更像“主题可救”，不是“Rank 55 可救”。**

本条残余信号主要有两层：
1. `order imbalance / taker pressure / VWAP pressure` 这些微观结构量，仍然对短窗后续价格路径有信息；
2. 但这点信息更像出现在 **`1m/3m` 的 raw alpha / event-driven execution**，而不是继续扮演 `15m` 主 setup 上的一层 shared crash-risk overlay。

最近新增证据正好把这点说得更清楚：
- `research/quant_digests/2026-03-25_0318_single-asset-microstructure-taker-alpha.md`
  - 结论是：`OFI + VWAP pressure` 更像 **单资产、超短周期 directional raw alpha**；
  - 明确不建议粗暴压成 `5m/15m` 主信号。
- `research/quant_digests/2026-03-25_2227_portable-microstructure-reversion-basket.md`
  - 进一步说明：同一组 microstructure 压力特征，desk 更值得偷的是 **`1m/3m` 的反转篮子 raw alpha**；
  - 到 `15m` 已基本不该再碰。

翻成人话：
- 可救的不是“让 Rank 55 继续当 15m overlay”；
- 可救的是“microstructure pressure 这个主题本身”，但它已经更像一条新的快时钟 raw-alpha 家族。

## 4) 最值得改的唯一一刀是什么？
如果只保留 **1 条唯一主修改轴**，本轮最值得保留的一刀会是：

**把 `order-imbalance crash-risk overlay` 从 `15m` shared veto / size layer，改写成 `1m/3m` 的 microstructure pressure raw alpha / execution family，不再强行服务原 Rank 55 的 overlay 角色。**

但这一刀当前**不值得直接 draft 成 `Rank 55b`**，因为：
1. 这已经不是在救原 Rank 55，而是在承认它的主题应该“换赛道”；
2. 新写法的核心身份会变成 `1m/3m microstructure raw alpha`，而不是 `15m shared overlay`；
3. 继续命名成 `Rank 55b`，会模糊原 `park` 审计意义，也会把“新 family”误包装成“旧 rank 的窄派生”。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。**

最终 verdict：`keep_park`

原因：
1. 原 `park` 的主 blocker 没被推翻：作为 `15m shared crash-risk overlay`，它没有给出跨 setup、跨时间的稳定改善；
2. 真正留下来的可救信息，更适合被新的 `1m/3m microstructure raw-alpha / execution` family 吸收；
3. 若硬写 `Rank 55b`，会把“主题换赛道”伪装成“原 rank 的单轴 reframe”，不够诚实。

## 6) 本轮结论（按模板）
1. **原 rank 为什么 park？**
   - 因为它作为 `15m shared crash-risk overlay` 只在 `ema_psar_long` 上留下薄 pocket，跨 setup 与时间稳定都不够。
2. **更像 hard park 还是 soft park？**
   - `soft park`，但偏硬。
3. **有没有可救信号？**
   - 有；但更像 microstructure pressure 主题仍可救，而不是原 Rank 55 这版 overlay 角色可救。
4. **最值得改的唯一一刀是什么？**
   - 把它从 `15m` shared overlay 改写成 `1m/3m` microstructure pressure raw alpha / execution family。
5. **是否值得形成新的 derived hypothesis？**
   - 不值得。
6. **为什么不立 `Rank 55b`？**
   - 因为那会把“新 family / 新时钟”的重写，误包装成原 Rank 55 的窄派生，削弱原 `park` verdict 的审计意义。

## 7) 允许的最终结论
- `keep_park`

## 8) 最小审计结论
- 原 `park` 保留；
- `Rank 55` 本轮仍读作 **soft park，但偏硬**；
- 它留下的不是值得单独派生 `Rank 55b` 的 overlay 残余，而是一个应转交给 `1m/3m microstructure raw-alpha family` 的主题残余。

## 9) 相关证据锚点
- `research/optimization_loop/2026-03-18_1142_rank55-crash-risk-intake.md`
- `research/optimization_loop/2026-03-18_1249_rank55-clean-replication.md`
- `research/optimization_loop/2026-03-18_1348_rank55-time-stability-park.md`
- `research/quant_digests/2026-03-25_0318_single-asset-microstructure-taker-alpha.md`
- `research/quant_digests/2026-03-25_2227_portable-microstructure-reversion-basket.md`

## 10) Git
- 未 commit。
- 原因：workspace 当前存在大量与本轮无关的脏文件；本轮只做 park-reframe 所需最小文本更新，不安全混提。
