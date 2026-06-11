# 2026-04-15 03:55 UTC · Rank 56 park reframe

## 本轮范围与选择
- 本轮只复盘 1 条 parked rank。
- 按 `PARK_REFRAME_QUEUE` 轮转，当前仍优先 `50~79` 段；`Rank 56` 上次由 bot6 复盘是 `2026-04-07 03:02 UTC`，已超过 7 天，可合法低频重看。
- 保留原 `park` verdict 的审计意义；不改 `docs/TODO.md` 顶部排班。

## 原 rank 为什么 park
`Rank 56 / liquidation-map path overlay` 原本不是独立 raw alpha，而是把 liquidation / cluster path 降级成 `15m` 既有 setup（`ema_psar_long / fib_retest_long / breakout_short`）的 shared gate / size tilt。

它被 park 的原因很集中：最小 clean replication 已经把原角色的 blocker 审计清楚。
- `ema_psar_long`：`base≈+1.63%`，`gate≈+0.74%`，`size≈+1.69%`
- `fib_retest_long`：`base≈+0.03%`，`gate≈-0.22%`，`size≈-0.04%`
- `breakout_short`：`base≈-2.49%`，`gate≈-2.02%`，`size≈-2.85%`

结论不是“cluster 主题彻底没信息”，而是：**原 `15m` shared path overlay 职责没站住。**

## 它更像 hard park 还是 soft park
- **`soft park`，但比 4 月 7 日那轮更接近 hard。**
- 对 `cluster / liquidation path` 主题本身，仍有信息残留；
- 但对“把它挂在旧 `15m` setup 上做 shared overlay”这个原写法，已越来越接近 hard park。

## 有没有可救信号
有，但可救信号继续外流，而且比 4 月 7 日那轮更明确：

1. `2026-04-03` 的 `hyperliquid-public-trigger-cluster-alpha` 已经说明，cluster 更自然的宿主是 **`1m/3m/5m` event-driven continuation raw alpha**，不是旧的 `15m` shared gate。
2. `2026-04-06` 的 `btc-positioning-fuel-cascade-alpha` 与 `2026-04-13` 的 `crowdedlong-fragility-cascade-alpha` 进一步把同主题往 **拥挤仓位 -> forced unwind -> continuation** 这类 raw-alpha 宿主上推，而不是往旧 Rank 56 的 overlay 角色上补强。
3. 换句话说，主题还有信息，但信息更像在 **新的拥挤/cluster 事件宿主** 里活着，而不是还能诚实回流到 old Rank 56。

## 最值得改的唯一一刀是什么
如果只保留唯一一刀，它仍然只能是：

> 把 `15m shared liquidation-map path overlay` 改写成 `1m/3m public-trigger / crowding-cluster approach continuation` 的事件主语。

但这刀现在已经更像**迁移宿主**，不是 old Rank 56 内部的窄修补。

## 是否值得形成新的 derived hypothesis
- **本轮结论：`keep_park`。**
- 不再维持 4 月 7 日那种“保留 soft reframe 候选”的宽松口径。

原因：
1. 原 rank 的 blocker 没被推翻；
2. 新证据不是在修复 old Rank 56，而是在持续证明“cluster / crowding / cascade”应迁到新的 event-driven raw-alpha family；
3. 若现在硬 draft `Rank 56b`，会把一个新宿主误包装成 old overlay 的窄 reframe，不诚实。

## 本轮固定回答
1. 原 rank 为什么 park？
   - 因为 clean replication 已明确显示：`liquidation-map` 作为 `15m` shared gate / size tilt，没有给三条既有 setup 提供稳定、可迁移的增量。
2. 它更像 hard park 还是 soft park？
   - `soft park`，但比上次更接近 hard；对原 `15m` overlay 读法已接近 hard park。
3. 有没有可救信号？
   - 有；但都在外流到 `1m/3m/5m` 的 public-trigger / crowding-cascade event-driven raw-alpha 宿主。
4. 最值得改的唯一一刀是什么？
   - 把 `15m shared path overlay` 改成 `1m/3m` 的 cluster-approach continuation 事件主语。
5. 是否值得形成新的 derived hypothesis？
   - 不值得；本轮只保留原 `park`，不给出新的 `Rank 56b`。

## 本轮结论
- `source_rank`: `Rank 56`
- `status`: `keep_park`
- `original verdict kept`: `park`
- `park 倾向`: `soft park，但比 4 月 7 日那轮更接近 hard`
- `note`: 新增 crowded-positioning / fragility-cascade 证据继续说明 cluster 主题仍有信息，但它救活的是新的 event-driven raw-alpha 宿主，而不是旧 Rank 56 的 `15m` shared path overlay，因此当前不诚实 draft `Rank 56b`。

## 备注
- 只做最小必要文件改动：本轮日志、`research/park_reframe/INDEX.md`、`docs/PARK_REFRAME_QUEUE.md`。
- 未改 `docs/TODO.md` 顶部排班。
- 未做 commit：git 工作区存在大量与本轮无关的既有脏文件，避免混提。