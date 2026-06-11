# 2026-04-20 01:55 UTC · Rank 37 park reframe review

## 本轮对象
- `Rank 37 / classic sparse TSMOM / own-past persistence pocket`
- 原始结论保留：`park / evidence pool`
- 本轮输出：`keep_park`

## 为什么这轮看 Rank 37
- `Rank 37` 上次 bot6 复盘是 `2026-04-13 02:21 UTC`，已超过最近 `7` 天默认回避窗口。
- 在 `Rank 1~37` 已 `park` 条目里，最近几天新增的最贴题证据主要集中在：
  - `2026-04-17_2056_pathshape-downtrend-continuation-alpha.md`
  - `2026-04-19_0016_intraday-extreme-return-router-alpha.md`
- 这轮只回答一件事：这些新证据有没有把旧 `Rank 37` 从 `keep_park` 推到值得再派生一条新的窄 reframe hypothesis。

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- recent park-reframe references:
  - `research/park_reframe/2026-04-19_2336_rank33-park-reframe.md`
  - `research/park_reframe/2026-04-19_2115_rank22-park-reframe.md`
  - `research/park_reframe/2026-04-19_1651_rank32-park-reframe.md`
- source / prior rank evidence:
  - `research/optimization_loop/2026-03-17_1717_rank37-clean-replication-park.md`
  - `research/park_reframe/2026-04-13_0221_rank37-park-reframe.md`
- new evidence:
  - `research/quant_digests/2026-04-17_2056_pathshape-downtrend-continuation-alpha.md`
  - `research/quant_digests/2026-04-19_0016_intraday-extreme-return-router-alpha.md`

## 1) 原 rank 为什么 park？
原 `Rank 37` 被 park 的核心 blocker 没变：把 crypto 动量写成 `15m` 上可直接交易的 **classic sparse own-past persistence pocket**，即使主动放慢、放稀、去 overlap，也没有站住。

原 clean replication（`2026-03-17_1717_rank37-clean-replication-park.md`）关键结果：
- `slow_12h_sign_hold_8h`：`mean_total_return≈-37.61%`，`positive_asset_ratio=0/3`
- `slow_4h_sign_hold_4h`：`mean_total_return≈-35.60%`，`positive_asset_ratio=0/3`
- `slow_4h_12h_agree_hold_8h`：`mean_total_return≈-35.24%`，`positive_asset_ratio=0/3`

也就是说：
- 失败点不是“太快、太密、太重叠”；
- 因为最自然的 `slow / sparse / no-overlap` 救法已经被原 rank 自己认真消费过；
- 但消费后，跨资产与 post-cost 仍然一起偏负。

所以原 `park` 的审计意义依然清楚：
> 被否掉的是“旧 Rank 37 这层 sparse own-past long/short persistence 壳”，不是 momentum / trend 主题整体死亡。

## 2) 它更像 hard park 还是 soft park？
**本轮判断：仍更像 `hard park`。**

原因：
1. 原 rank 最自然的一刀已经用过，而且没有留下足够诚实的独立 pocket；
2. 旧壳不是只差一个 lookback / hold 微调，而是整个 `own-past persistence pocket` 主语不够成立；
3. 最近新证据虽然继续证明“趋势 / continuation”主题还有信息，但宿主已经更不像旧 `Rank 37`。

## 3) 有没有“可救信号”？
**有，但仍更像主题级可救信号，不像旧 rank 级可救信号。**

### 新证据真正说明了什么
- `2026-04-17 path-shape downside continuation` 说明：
  - 值钱的信息不只是“过去跌了多少”，而是“这段下跌走得是否更单边、更贴近区间低点”；
  - 当前更像 `15m short downside continuation pocket`，且明显偏向 downside asymmetry。
- `2026-04-19 intraday extreme-return router` 说明：
  - 值钱的信息不在对所有币对称地交易 own-past persistence；
  - 更像 `strongest-only` 的 recent-shock continuation router，且收益主要由极端冲击驱动。

### 为什么这些信号仍救不了旧 Rank 37
因为两篇新证据共同把主语改写成了：
- **asymmetric downside continuation**
- **strongest-only router / extreme-only admission**

而旧 `Rank 37` 的主语是：
- **classic sparse own-past persistence**
- 默认 long/short 对称
- 更像普适、慢一点、稀一点的 continuation 口袋

这已经不是给旧 rank 补一层小 filter；
而是在把主题重写成 **新的 downside / router raw-alpha family**。

## 4) 最值得改的唯一一刀是什么？
如果今天还要给旧 `Rank 37` 回答“唯一最值得改的一刀”，最诚实的版本只能是：

> **放弃对称 own-past persistence 读法，把趋势残余收窄成 asymmetric strongest-only downside continuation router。**

但更关键的判断是：
- 这刀已经不是旧 `Rank 37` 的窄 reframe；
- 它把主语从“慢速 own-past persistence”换成了“极端 recent-shock / path-shape 定义的 downside continuation”；
- 因此它更像新的 raw-alpha family，而不是诚实的 `Rank 37b`。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。本轮继续 `keep_park`。**

原因：
1. 原 `park` verdict 没有被推翻；
2. 原线最自然的 residual 早已被 `slow / sparse / no-overlap` clean replication 消费完；
3. 新 evidence 确实说明 momentum / continuation 主题还有 edge，但这条 edge 已经明显迁移到新的 `downside continuation / strongest-only router` raw-alpha 主语；
4. 若硬写成 `Rank 37b`，会把一个新的 asymmetric router family 错包装成旧 rank 的小修小补，削弱原 `park` 审计意义。

## 单轮审查模板回答
### 原 rank 为什么 park？
因为在已经主动放慢、放稀、去 overlap 的 clean replication 后，三档最自然变体仍然全部跨资产转负，说明 own-past persistence pocket 本身不够成立。

### 它更像 hard park 还是 soft park？
`hard park`。

### 有没有“可救信号”？
有。最新 path-shape downside continuation 与 strongest-only extreme-return router 都说明趋势 / continuation 主题仍有信息；但它们救活的是新的 asymmetric downside / router raw alpha，不是旧 Rank 37 本体。

### 最值得改的唯一一刀是什么？
若硬改，只能把对称 own-past persistence 改写成 `asymmetric strongest-only downside continuation router`。

### 是否值得形成新的 derived hypothesis？
不值得。本轮继续 `keep_park`。

## Final verdict
- `keep_park`
- original verdict kept: `park`
- short note: `hard park；4 月 17~19 日新增的 path-shape downside-continuation 与 strongest-only extreme-return router 证据继续说明 trend / continuation 主题仍有信息，但它们救活的是新的 asymmetric downside / router raw-alpha family，而不是旧 Rank 37 的 sparse own-past persistence pocket，因此当前不诚实 draft Rank 37b。`

## File actions
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`
- 未改：`docs/TODO.md`

## Commit
- 本轮默认不做 commit。
- 原因：git 工作区存在无关共享脏文件；本轮只做最小必要文档改动，避免混提。
