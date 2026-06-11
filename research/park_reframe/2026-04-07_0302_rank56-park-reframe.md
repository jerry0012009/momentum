# 2026-04-07 03:02 UTC · Rank 56 park reframe

## 本轮范围与选择
- 本轮只复盘 1 条 parked rank。
- 按 `PARK_REFRAME_QUEUE` 当前轮转规则，`50~79` 仍是默认优先段；近 7 天里 `50/51/52/54/55/57/58/59/60/61/62/65/67/73/79` 已被覆盖，`Rank 56` 近 7 天未被 `bot6` 复盘，因此本轮认领它。
- 保留原 `park` verdict 的审计意义；不改 `docs/TODO.md` 顶部排班。

## 原 rank 为什么 park
`Rank 56 / liquidation-map path overlay` 的原始读法，不是把 liquidation map 当独立方向引擎，而是把它降级成 `15m` 三条既有 setup（`ema_psar_long / fib_retest_long / breakout_short`）的 shared path overlay：
- 顺势 fuel 明显时放行或倾斜；
- 反向 trap 更近时 veto / 降仓；
- 固定比较 `base / binary_path_gate / size_tilt`，执行冻结为 `next-bar open + no-overlap + hold 8 bars`。

它被 park 的原因很集中：**overlay 角色并没有在最小 clean replication 里证明出稳定增量。**
- `ema_psar_long`：`base≈+1.63%`，`gate≈+0.74%`，`size≈+1.69%` —— 只有 size 轻微不差，但不够形成清楚增量；
- `fib_retest_long`：`base≈+0.03%`，`gate≈-0.22%`，`size≈-0.04%` —— 基本没有帮助；
- `breakout_short`：`base≈-2.49%`，`gate≈-2.02%`，`size≈-2.85%` —— 只是少亏，不像可诚实复用的 queue-facing overlay。

所以原 park 不是因为“liquidation / cluster 主题彻底没信息”，而是因为：
- **原版 `15m shared path overlay` 这层职责没站住**；
- 改善要么太薄，要么更像砍样本/轻微路径修饰，而不是清楚、可迁移的增量层。

## 它更像 hard park 还是 soft park
我把 `Rank 56` 归为：
- **`soft park`，但对原 `15m shared path overlay` 读法已明显偏硬。**

原因：
- 主题本身还有 residual value；cluster / stop / liquidation path 并没有被彻底判死。
- 但对“把它挂在既有 `15m` setup 上做 shared gate / size tilt”这个原角色，clean replication 已经给过很直接的负面审计。

换句话说：
- 对 **原角色**：已经接近 hard park；
- 对 **cluster path 主题本身**：仍保留 soft residual，但更像应该迁到别的宿主。

## 有没有“可救信号”
有，但可救信号已经明显**外流**，不再像原 Rank 56 的窄内部修补：

1. `2026-04-03_1425_hyperliquid-public-trigger-cluster-alpha.md` 给出了更清楚的新旁证：
   - 真正更自然的主语，不是 `15m` shared overlay；
   - 而是 **公开 trigger / liquidation cluster 邻域上的 `1m/3m/5m` event-driven continuation**。
2. 这份新 digest 还明确写了：
   - `15m` 更像管理层 / 二次确认层；
   - cluster 本身更适合做分钟级 raw alpha，而不是继续当三条老 setup 的共用 gate。
3. 这正好解释了原 Rank 56 为什么 replication 很别扭：
   - 不是 cluster 主题完全失效；
   - 而是**被放在了错误的职责层与时间尺度**。

所以，可救信号是存在的；但它更像“主题迁移到新的 raw-alpha family”，不是“原 Rank 56 再磨一刀就能活”。

## 最值得改的唯一一刀是什么
**唯一还值得保留的一刀**可以表述为：

> 把 `15m shared liquidation-map path overlay` 改写成 `1m/3m public trigger-cluster approach continuation` 事件主语。

翻成人话：
- 不再先有 `EMA / Fib / breakout`，再问前方路况；
- 而是先有 **cluster 邻域 + 同向逼近 + 微冲击 follow-through** 这个事件，直接交易“向 cluster 打过去”的分钟级 continuation。

但这也是本轮不直接 draft 新假设的核心原因：
- 这刀虽然只有一个主轴（**角色+时间尺度一起迁移到 event host**），
- 却已经不太像原 Rank 56 的“窄 reframe”，而更像一个新的 raw-alpha 宿主。

## 是否值得形成新的 derived hypothesis
**本轮不直接 draft `Rank 56b`；更诚实的是记为 `soft_reframe_candidate`。**

原因：
1. 原 Rank 56 的失败点已经很清楚：`15m` shared overlay 角色不成立；
2. 新证据给出的最自然去向，是 `1m/3m/5m` 的 public trigger / liquidation cluster event-driven continuation；
3. 这条线虽然和 Rank 56 同主题，但已经不是“保留原宿主，只微调一刀”的那种窄救法；
4. 现在若硬写一个 `Rank 56b`，很容易把“新分钟级 raw alpha family”误伪装成“旧 overlay 的小修小补”，不诚实。

因此，本轮最稳妥的结论是：
- 保留原 `park`；
- 承认它是 `soft park`；
- 把“cluster 主题更适合迁到分钟级 event-driven 宿主”记成候选方向，但暂不升格成 queue-facing derived hypothesis。

## 本轮固定回答
1. 原 rank 为什么 park？
   - 因为最小 clean replication 已经证明：`liquidation-map` 作为 `15m` shared path overlay，对 `ema/fib/breakout` 三条 setup 没给出稳定、可迁移的增量。
2. 它更像 hard park 还是 soft park？
   - `soft park`，但对原 `15m` shared overlay 读法已明显偏硬。
3. 有没有可救信号？
   - 有；但 residual 已明显外流到 `1m/3m/5m` 的 public trigger / liquidation cluster event-driven continuation 主题。
4. 最值得改的唯一一刀是什么？
   - 把 `15m shared path overlay` 改写成 `1m/3m public trigger-cluster approach continuation` 事件主语。
5. 是否值得形成新的 derived hypothesis？
   - 暂不值得；本轮只记为 `soft_reframe_candidate`。

## 本轮结论
- `source_rank`: `Rank 56`
- `status`: `soft_reframe_candidate`
- `original verdict kept`: `park`
- `park 倾向`: `soft park，但对原 15m shared overlay 读法已明显偏硬`
- `note`: 原 `park` 保留；原 rank 的 blocker 不是 cluster 主题完全没信息，而是其 `15m` shared path overlay 角色没站住。2026-04-03 的 public trigger / liquidation cluster 新证据说明，该主题更像应迁到 `1m/3m/5m` 的 event-driven continuation raw-alpha 宿主，而不是直接诚实派生成 `Rank 56b`。

## 备注
- 本轮只更新 `research/park_reframe/`、`research/park_reframe/INDEX.md`、`docs/PARK_REFRAME_QUEUE.md`。
- 未改 `docs/TODO.md` 顶部排班。
- 默认不做 commit：工作区长期存在大量与本轮无关的既有脏文件，为避免混提，本轮只做最小必要文件改动与邮件摘要。
