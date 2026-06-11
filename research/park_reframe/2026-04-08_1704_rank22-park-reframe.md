# 2026-04-08 17:04 UTC · Rank 22 park reframe review

## 本轮对象
- `Rank 22`
- 原对象：`up/down wave + MA20 persistence gate`
- 本轮结论：`keep_park`
- 原 `park` verdict：**保留，不推翻**

## 为什么这轮看它
- `bot6` 本轮只处理 1 条 parked rank。
- `Rank 22` 属于 `Rank 1~37` 的旧 parked 对象。
- 虽然它在最近 7 天内被复盘过，但这次不是无信息重复：4 月新增的几条短周期证据（尤其 `normalized cluster deviation × next-bar snapback`，以及前几日已出现的 `1h oversold volume-confirmed bounce`、`three-candle contrarian fade` 一类）继续把“下跌后修复”主题往**更快、更窄、更像独立 raw alpha** 的宿主推，而不是支持原 `wave + MA persistence gate` 继续诚实细切。

## 原 rank 为什么 park
根据 `2026-03-17_0437_rank22-clean-replication-park.md`，原 rank 被 park 的原因很明确：
1. 主口径 `MA20` 在 `6bps/side` 下仍约 `-7.94%`，没有过 admission。
2. 参数邻域里最不差的 `MA15` 也只是少亏，不是可部署 pocket。
3. 跨标的只剩 `SOL` 单腿为正，`BTC/ETH` 明显失守。
4. 成本从 `10 -> 15 -> 20 bps/side` 上抬后继续快速恶化，说明 edge 不厚。
5. 这条线更像“让 baseline 少亏一点的过滤器”，不像一条能独立站住的 alpha。

## 它更像 hard park 还是 soft park
- **结论：soft park，但已经很靠近 hard park。**
- 还没把它定成绝对 hard park 的原因，是原 clean replication 至少证明：
  - gate 确实能减少交易与减亏；
  - `SOL` 留过一条 long-side recovery pocket；
  - “下跌后修复”这个大主题本身没死。
- 但对 **原 Rank 22 的表达方式**（`wave + MA20 persistence gate`）来说，已经基本接近 hard：它没有留下足够清楚、足够独立、足够单轴的 residual。

## 现有证据里有没有“可救信号”
有，但很弱，而且**不该再记在 Rank 22 账上**。

### 可救信号
- 原 replication 里 `SOL` 这条 long-side pocket 说明“跌后修复”方向不是完全没信息。
- 近期新增的：
  - `2026-04-08_1358_normalized-cluster-deviation-snapback-alpha.md`
  - `2026-04-01_1747_1h-oversold-volume-bounce-alpha.md`
  - `2026-04-01_0528_three-candle-contrarian-tponly-alpha.md`
  都在强化同一个判断：**如果这类东西要活，更像是短窗 oversold / snapback / capitulation-fade raw alpha**。

### 但为什么仍不救 Rank 22
- 这些新证据的主语已经不再是 `wave + MA persistence gate`；
- 它们更像：
  - 更短 holding；
  - 更强事件锚；
  - 更像 reversal/snapback 本体，而不是 shared gate；
  - 更接近新宿主，而不是旧 rank 的窄 reframe。
- 继续从 Rank 22 派生，会变成把“跌后修复”这个大主题的新增证据，硬嫁接回一个已经被审计过的旧 gate 壳子里，审计上不诚实。

## 最值得改的唯一一刀是什么
如果硬要说唯一一刀，最像的是：
- **把慢速 `wave + MA persistence` 读法，收缩成“短窗 oversold/snapback 事件后的 next-bar 修复”**。

但这刀**不应该**被写成 `Rank 22b`，因为：
- 这已经不是在修原 rank 的职责；
- 而是在换主语、换交易形状、换持有逻辑；
- 本质上更像一个新的 raw-alpha family 宿主。

所以本轮的诚实结论不是 draft 新派生，而是承认：
- **Rank 22 本体没有值得继续保留的单轴 residual；真正活着的是它上游的大主题，并且那个主题已经外流到别的更快宿主。**

## 是否值得形成新的 derived hypothesis
- **不值得。**
- 本轮不形成 `Rank 22b`。

原因：
1. 原 rank 的 park blocker 没被推翻。
2. 最近新增证据虽然支持“跌后修复”主题仍有信息，但支持的是**更快、更独立的新 raw alpha 宿主**，不是原 rank 的窄 reframe。
3. 若此时再写 `Rank 22b`，很容易变成“拿新 family 的证据给旧 gate 续命”。
4. 这违反 bot6 的边界：保留 park 审计意义，而不是为了显得勤奋继续切分平行分支。

## trade on / trade off（仅作不立项说明）
本轮没有形成新的 derived hypothesis，因此不正式写 `trade on / trade off` 提案。

若仅作为审计备注：
- `trade on` 真正偏向的是 **short-window oversold snapback / capitulation-fade raw alpha**；
- `trade off` 的是原 `wave + MA persistence gate` 这套慢速 shared gate 语义。

但这组语义应当留在未来 fresh intake / 新宿主判断里，而不是挂回 `Rank 22` 血缘下。

## 最终结论
- 允许输出类型：`keep_park`
- 本轮最终结论：**`keep_park`**
- 一句话：
  - `Rank 22` 仍是 **soft park（偏硬）**；
  - 有可救信号，但救的是“跌后修复”这个更快 raw-alpha family，不是原 `wave + MA persistence gate`；
  - 因此本轮不 draft `Rank 22b`，继续保留原 `park` verdict。

## 本轮最小改动
- 新建本轮日志：`research/park_reframe/2026-04-08_1704_rank22-park-reframe.md`
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`
- 未改：`docs/TODO.md`

## Git / 提交
- 本轮默认不做 commit。
- 原因：任务要求是最小必要文件改动；且当前无需为了单条 `keep_park` 日志冒险混入无关脏文件。
