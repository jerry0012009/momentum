# 2026-03-28 09:22 UTC · Rank 24 park reframe review

## 本轮对象
- `Rank 24 / trend regime filter / trend-strength-over-noise gate`
- 选择原因：
  - 仍属于 `Rank 1~37` 已 `park` 条目；
  - 虽然 `2026-03-20` 已复盘过一次，但这次有一条相对直接的新旁证：`2026-03-28_0521_xs-momentum-inversevol-lowsentiment-alpha.md`；
  - 需要确认这条新证据会不会把原来的“环境层主题”推进成一个新的窄 reframe，还是只会再次证明它更适合待在上位 raw-alpha family。

## 原 rank 为什么 park
根据 `research/optimization_loop/2026-03-17_0549_rank24-clean-replication-park.md`：
- `baseline_mtf`、`trend_regime_default`、`stricter_trend_threshold`、`stricter_regime_score` 在 `6bps/side` 下全部仍为负；
- 最好的 `stricter_trend_threshold` 也只是把亏损收窄到约 `-9.81%`，`positive_asset_ratio` 仍只有 `1/3`；
- 时间桶里有零散正 pocket，但没有跨资产、跨时间都可复用的稳定 pocket；
- 参数邻域没有给出稳定平台；
- 成本从 `10/15/20bps` 继续恶化。

翻成人话：它证明了“环境过滤并非完全没信息”，但没证明“这条 filter 自己足够变成可上桌候选”。

## hard park 还是 soft park
- 结论：**soft park，但比 3 月 20 日那次更偏硬。**

原因：
- 它不是纯硬失败，因为 filter 的确能少亏；
- 但它的残余价值越来越像“该服务别的 alpha 家族”，而不是继续给 `Rank 24` 自己写一个新 queue-facing 派生。

## 现有证据里有没有“可救信号”
有，但依然不够形成新的独立派生：

1. `2026-03-24_1030_market-percentile-tsmom-state-alpha.md`
   - 新增的是 **市场分位状态 TSMOM 本体**；
   - 它说明“市场状态”可以是完整 raw alpha 骨架；
   - 但这更像把环境信息**上移成独立 alpha family**，不是救 `Rank 24` 这种旧 filter 写法。

2. `2026-03-28_0521_xs-momentum-inversevol-lowsentiment-alpha.md`
   - 这条证据更明确：
     - alpha 本体 = momentum；
     - overlay = inverse-vol sizing；
     - gate = low-sentiment / high-sentiment regime。
   - 它确实再次证明“低情绪/低 crowding 环境”有信息；
   - 但也同时把角色边界写得更清楚：**sentiment / regime 更像 gate，不像独立 entry alpha。**

所以这次的新证据不是把 `Rank 24` 救活，而是更清楚地说明：
- 这条线若还有价值，也更像上位 raw-alpha family 的 gate；
- 而这种改写方向，已经被 `Rank 9b / Rank 21b / Rank 25b` 一类现有派生基本吸收。

## 最值得改的唯一一刀是什么
如果硬要留一刀，唯一还诚实的改单轴仍然是：

- **把 standalone trend regime filter 彻底降级成 shared sentiment / state allow-deny gate，而不是独立候选。**

但这刀现在不值得再单列一个 `Rank 24b`，因为：
- 它与 `Rank 21b`（daily sentiment-extremity shared risk overlay）语义重叠极高；
- 与 `Rank 9b / Rank 25b` 也都属于“把环境层降级成 shared gate”的同类消费方向；
- 新证据没有给出 `Rank 24` 专属、尚未被这些近邻提案吸收的唯一新轴。

## 是否值得形成新的 derived hypothesis
- 结论：**不值得。**
- 本轮最终 verdict：**`keep_park`**

原因：
- 原 `park` 结论仍有审计意义，不能因为环境层主题在别处活下来，就反向改写成“Rank 24 其实差一点就成”；
- 新证据只进一步强化了角色分工：**market state / sentiment 更像 gate，不像旧 Rank 24 这种 standalone filter candidate**；
- 再写一个 `Rank 24b`，大概率只是重复排队，而不是新增 genuinely verdict-changing 的窄假设。

## 本轮模板回答
1. **原 rank 为什么 park？**
   - 因为 clean replication 下虽能少亏，但始终没形成跨资产、跨时间、跨成本仍能成立的稳定 pocket。
2. **它更像 hard park 还是 soft park？**
   - `soft park`，但比上次更偏硬。
3. **有没有可救信号？**
   - 有，主要是“低情绪 / 市场状态有信息”；但这些信号更适合服务上位 raw-alpha family，不足以救回原 Rank 24。
4. **最值得改的唯一一刀是什么？**
   - 把 standalone trend regime filter 彻底降级成 shared sentiment / state allow-deny gate。
5. **是否值得形成新的 derived hypothesis？**
   - 不值得。
6. **为什么不 draft `Rank 24b`？**
   - 因为这条改单轴已经被 `Rank 21b / 9b / 25b` 等近邻提案基本吸收，新证据没有提供属于 `Rank 24` 自己的独特新轴。

## 文件影响
- 更新 `docs/PARK_REFRAME_QUEUE.md`：只追加一条最近复盘记录；
- 更新 `research/park_reframe/INDEX.md`：追加本轮索引；
- 不改 `docs/TODO.md` 顶部排班；
- 不新增 `Rank 24b`。

## Git / 提交
- 本轮未提交。
- 原因：`git status --short | wc -l = 3775`，工作区存在大量与本轮无关的脏文件，不适合安全混提；本轮只做最小必要文件改动。
