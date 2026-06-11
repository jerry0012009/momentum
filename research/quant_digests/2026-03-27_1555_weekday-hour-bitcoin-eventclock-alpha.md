# 别把 Bitcoin 的 weekday-hour 只当日历异象：这篇 2022 论文更该先测的是「固定弱时段 → 后续 4h short」event-clock raw alpha
- 时间：2026-03-27 15:55 UTC
- 类型：2022 Oeconomia Copernicana 开放获取文章页 / RePEc 摘要 + Binance Spot 公共 `1h` 最小 transfer check
- 主题类型：raw alpha
- 基础 alpha：`weekday × hour` 这个事件时钟里，某些固定弱时段之后的 1~4 小时存在可交易的方向延续；对当前 desk 最像完整策略的是「滚动识别最弱 weekday-hour 桶，在该时段结束后做 BTC 4h short」
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/event-clock/seasonality/weekday-hour/bitcoin/single-asset/time-of-week/schedule/1h/15m/5m/3m/paper/external-data/cost
- 证据类型：论文摘要页证据 + Binance Spot 公共 `1h` 最小 transfer check

## 1. 这次看了什么
这次看的是 **José Luis Miralles-Quirós & María Mar Miralles-Quirós (2022), _A new perspective of the day-of-the-week effect on Bitcoin returns: evidence from an event study hourly approach_**, 发表在 **Oeconomia Copernicana**。

先直接回答这篇东西的 **base alpha**：

> **不是“周一周二哪天更容易涨”这种日频结论，而是 Bitcoin 的 `weekday × hour` 事件时钟里，存在少数可交易的强/弱小时；其中更适合我们 desk 先落地的，是“滚动识别最弱 weekday-hour 桶，在其结束后做 1~4 小时 short”这一类稀疏时段策略。**

这轮我没顺利抓到 PDF 正文，只拿到了开放获取文章页、RePEc 摘要和参考文献页，所以论文证据强度低于“全文可读”的候选；但它有两个优点，仍值得进研究池：
1. **raw alpha 很清楚**，不是纯解释层；
2. 我可以立刻用 Binance 公共 `1h` 数据做一轮独立 transfer check，判断这条线今天还有没有 pocket edge。

## 2. 核心结论
- 论文不是按“自然日收盘”算日历效应，而是用 **Kraken 的 Bitcoin 小时收盘价，样本从 `2016-01` 到 `2021-12`**，把每个 `weekday × hour` 都当成单独事件来做。这个口径比传统 day-of-week 更适合 24/7 crypto。
- 论文方法分两步：先找 **显著的 weekday-hour 平均回报**，再看这些事件后的 **post-event cumulative returns**；作者明确写到，基于这些显著时段构造的策略 **Sharpe 能跑赢 buy-and-hold**。
- 我做的 Binance Spot `1h` transfer check（训练 `2024-03-27 ~ 2025-09-28`，测试 `2025-09-28 ~ 2026-03-27`）里，训练样本最弱的 5 个桶分别是：`Thu 19:00`（`-20.3 bps`）、`Fri 00:00`（`-14.5 bps`）、`Thu 13:00`（`-11.5 bps`）、`Fri 07:00`（`-9.2 bps`）、`Sat 01:00`（`-8.0 bps`）。
- 若只做这 5 个**负时段**，在测试样本里于该小时结束后 **short BTC 持有 4h**，结果是：**`129` 次事件、`+20.5 bps/event` gross、`53.5%` 胜率**；即便按 **`8 bps round-trip`** 粗扣成本，仍有 **`+12.5 bps/event`** 的剩余空间。
- 相比之下，把“最强时段 long + 最弱时段 short”直接拼成稀疏 `1h` schedule，测试期只有 **`+3.29 bps/active bar`**，说明这条线真正值钱的不是“全时段对称做”，而是 **只抓少数弱时段 pocket**。

## 3. 为什么和当前项目有关
这篇比继续补一篇泛 filter 更值得，原因很直接：

1. **它补的是 raw alpha 素材池里的 event-clock 家族。** 这和今天已经很多的 pairs / carry / lead-lag / XS reversal 不同，能给 desk 新的独立原型。
2. **它很好 desk 化到 `15m / 5m`。** 论文是 `1h` 事件时钟，但执行层完全可以转成：`15m` 上在选中时段结束后开仓，持有 `16` 根 `15m`；或 `5m` 上持有 `48` 根。
3. **它天然带“稀疏交易、低暴露时间”特征。** 如果 edge 只集中在少数 clock bucket，就没必要全天硬交易。
4. **它也能服务其他 raw alpha。** 就算后面发现 standalone short schedule 不够稳，这组弱时段也可以给 breakout / momentum / reversal 做 shared veto：在这些时段少追多、甚至反向看待短冲高。

## 3.5 策略拆解（必填）
- 方向属性：单资产、directional、event-clock、稀疏时段
- 基础 alpha：`weekday × hour` 的固定弱时段后，短窗收益存在可交易延续
- entry：用过去 `12~18` 个月 `1h` 数据滚动计算每个 `weekday-hour` 的均值与 t 值；选 bottom `3~5` 桶；在选中时段 **收盘后** 开始做空 BTC
- exit：优先测固定持有 `1h / 2h / 4h / 8h`；当前 transfer check 里 **`4h` 最像能过成本**
- sizing：先固定名义；二阶段再做 `inverse-vol` 或 `target-vol`，避免在高波动新闻窗过度放大
- regime：目前更像普通时钟效应，尚未证明必须依赖单独 regime；后续可叠 `RV / funding / macro calendar`
- filter / veto：FOMC / CPI / 非农等大事件前后、异常 gap、小样本新 regime 漂移时暂停；若最近 `N` 周该桶 t 值回到 0 附近则撤销
- risk / sizing / execution overlay：单笔只保留 1 个方向仓位；不叠加重叠信号；统一按 `4 / 8 / 12 bps round-trip` 做成本梯度；若改用 perp 需额外核算 funding

## 4. 可复刻的最小实验
### 最小实验 A：先复现 paper 的事件时钟骨架
- **研究假设**：少数 `weekday-hour` 弱桶在样本外仍保留方向信息，且弱桶后的 `2~4h` 比 `1h` 更容易过成本。
- **数据源**：Binance Spot `BTCUSDT` `1h` K 线（公开可得，REST API）；若要贴 desk，再下钻到 `15m / 5m` 执行。
- **最小口径**：
  1. 过去 `365~540` 天做训练；
  2. 计算 `dow × hour` 的 mean / std / t-stat；
  3. 选 bottom `k=3~5` 桶；
  4. 在这些桶结束后做空，比较 `hold=1/2/4/8h`；
  5. 成本至少跑 `4 / 8 / 12 bps round-trip` 三档。

### 最小实验 B：desk 化到 `15m / 5m`
- `15m` 版本：在选中小时结束后的第一根 `15m` 开仓，持有 `16` 根。
- `5m` 版本：同理持有 `48` 根，但必须单独核算滑点；不要偷拿 `1h` 成绩直接外推。
- 若要更稳，可把 raw signal 写成二元 gate：`selected_weak_hour = 1` 时，只允许 short 或下调 long size。

### 最小实验 C：避免纯时间过拟合
- 做 **rolling refresh**：每周或每月重算弱桶；
- 对照组必须包含：
  - 随机选 5 个 hour-bucket
  - 固定周五/周末 dummy
  - 只做 `hour-of-day` 不做 `weekday × hour`
- 只有当 `weekday × hour` 明显优于这些弱基线，才说明不是普通周末噪音。

## 5. 当前这条线怎么判断
我对这条线的当前判断是：

> **它值得作为 raw alpha intake 进入池子，但不该被误写成“全天有效的 calendar anomaly”。真正可交易的部分很稀疏，更像少数固定弱时段的 short pocket。**

换句话说：
- **能不能独立成策略？能。**
- **是不是已经证明适合全时段实盘？没有。**
- **当前最像哪种落地方式？** 先做 `BTC only` 的 sparse `4h short schedule`，再看能否扩展成 shared veto / scheduler。

## 6. 风险与注意事项
- 当前论文证据是 **article page / abstract-level**，不是我已完整读过全文 PDF；因此不应假装已经 paper replication 完成。
- 这类时钟效应最容易犯的错是 **时间切片过拟合**；必须用 rolling train / fixed OOS，而不是事后挑最好时段。
- 当前 transfer check 只在 **BTC 单资产 spot `1h`** 上做，尚未证明可平移到 perp、alt 或更快执行频率。
- `4h` 持有版本虽然 gross 更厚，但也更容易碰到宏观事件、Funding 窗口、周末流动性变化等外生扰动。

## 7. 来源与落地文件
1. **Miralles-Quirós, J. L., & Miralles-Quirós, M. M. (2022). _A new perspective of the day-of-the-week effect on Bitcoin returns: evidence from an event study hourly approach_. Oeconomia Copernicana, 13(3), 745-782.**
   - Venue: Oeconomia Copernicana
   - DOI: `10.24136/oc.2022.022`
   - Readable URL: https://journals.economic-research.pl/oc/article/view/2091
   - RePEc URL: https://ideas.repec.org/a/pes/ieroec/v13y2022i3p745-782.html
   - Repo URL: 暂未发现公开仓库
2. **Binance Spot API Docs — Kline/Candlestick Data**
   - Readable URL: https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#klinecandlestick-data
3. **本地最小实验产物**
   - `reports/artifacts/quant_digests/dayofweek_hourly_event_clock_20260327/summary.json`
   - `reports/artifacts/quant_digests/dayofweek_hourly_event_clock_20260327/top_negative_cells.csv`
   - `reports/artifacts/quant_digests/dayofweek_hourly_event_clock_20260327/hold_grid_test.csv`
   - `reports/artifacts/quant_digests/dayofweek_hourly_event_clock_20260327/test_signals.csv`
