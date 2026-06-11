# 2026-03-26 04:40 UTC｜bot6 park-reframe｜Rank 52

## 0) 本轮选择
- 按当前轮转，继续优先看 `Rank 50+`，且避开最近 `7` 天内已被 `bot6` 复盘过的条目。
- 选定：`Rank 52 / trade-flow imbalance veto`。
- 选它的原因：
  1. 原始 `park` 原因很集中，主要是 **flow gate 没把假突破压到足够低，且并不是靠极端 retention 才失败**；
  2. 过去两天出现了高度相关的新旁证：
     - `research/quant_digests/2026-03-24_1216_orderflow-xs-imbalance-cost-cliff.md`
     - `research/quant_digests/2026-03-25_0318_single-asset-microstructure-taker-alpha.md`
     - `research/quant_digests/2026-03-25_2227_portable-microstructure-reversion-basket.md`
  3. 这些新证据刚好能回答：**order-flow / taker-pressure 主题到底只是原 Rank 52 没调好，还是它本来就更像另一条 raw-alpha family，而不是 15m shared veto。**

## 1) 原 Rank 为什么 park？
原始结论见：
- `research/optimization_loop/2026-03-18_0950_rank52-trade-flow-intake.md`
- `research/optimization_loop/2026-03-18_1011_rank52-clean-replication-park.md`

原 Rank 52 被 park 的核心原因很明确：
- 它把 **signal 前最后 5 分钟主动成交失衡** 写成了 `ema_pullback_long / breakdown_reclaim_short` 的 shared veto；
- 但最小 clean replication 下，主读法 `breakdown_reclaim_short + opposite_flow_veto @ 6bps` 仍然是：
  - `mean_total_return ≈ -2.73%`
  - `positive_asset_ratio = 0/3`
  - `mean_trade_count_retention ≈ 81.90%`
  - `mean_false_break_or_hold_4bars_rate ≈ 85.65%`
- 也就是说，问题不是“它太严格把交易全砍没了”，而是：**保留了大多数样本后，flow veto 依然没有把 outcome 推过门槛**；
- long 侧更差，说明它也不是一个对称、可共享的 long/short 通用 gate。

所以原 `park` verdict 必须保留：
- **原 Rank 52 不适合继续被读成 `15m setup` 的 shared trade-flow veto。**

## 2) 它更像 hard park 还是 soft park？
- **本轮判断：`soft park`，但偏硬。**

为什么不是 hard park：
- 新证据很清楚地说明 **order-flow / taker-pressure 主题本身没死**；
- 死掉的是它被塞进原 Rank 52 那种 `15m setup 前最后 5 分钟 flow 方向一致才放行` 的角色。

为什么又偏硬：
- 这条线如果继续沿着“shared veto / shared gate”往前推，几乎必然会滑回 wording 调整；
- 近期新证据已经把残余价值明确吸走到 **独立 microstructure raw-alpha family**，而不是留在原 rank 内部等待 `52b`。

## 3) 有没有“可救信号”？
- **有，但不是原 Rank 52 这层角色上的可救。**

本轮最关键的新证据有三点：
1. `2026-03-24` 的 digest 已经说明：**横截面 taker-flow 失衡本身可以形成短周期 raw alpha 毛边**，只是有明显成本断崖；
2. `2026-03-25 03:18` 的 digest 又把它进一步收敛成：**单资产 OFI + VWAP pressure 是可独立交易的超短周期 directional raw alpha**；
3. `2026-03-25 22:27` 的 digest 则把同一主题 desk 化成：**更适合 `1m/3m` 的跨资产 microstructure reversion basket**。

翻成人话：
- **flow 有信息，这点是肯定的；**
- 但它更像一条要自己当 alpha 的 `1m/3m` 家族，或者 execution/micro-timing 层；
- **不是** 一个能诚实拯救原 `15m shared veto` 写法的残余小修补。

## 4) 最值得改的唯一一刀是什么？
如果以后还要再碰这个主题，唯一值得保留的一刀只能是：

**把 `setup 前最后 5m same/opposite flow veto`，改写成 `1m/3m independent microstructure alpha / micro-timing family`，不再继续写成 15m shared gate。**

但这也是本轮不 draft 的关键：
- 这已经不是在原 Rank 52 上切一条窄 reframe；
- 而是在承认 **主题应该整体换角色、换时钟、换研究家族**；
- 更像 `new family / new intake`，而不是 `Rank 52b`。

## 5) 是否值得形成新的 derived hypothesis？
- **本轮结论：`keep_park`。**

原因：
1. 原 Rank 52 的 clean replication 已经把 shared veto 这条路审计得很清楚：不是 retention 不够，而是 outcome 本身不行；
2. 最新证据支持的是 **microstructure pressure 作为 raw alpha**，不是继续在 `15m setup gate` 里打磨；
3. 如果现在硬写 `Rank 52b`，大概率只会变成“把原本该独立立项的 micro alpha 换皮写回原 rank”，不够诚实，也会稀释原 `park` 的审计意义。

## 6) trade on / trade off（why-not-draft）
若未来真要重开，这条主题更诚实的交换应是：
- `trade on`：承认 taker-flow / VWAP pressure 在 `1m/3m` 上有独立可交易信息，可做单资产 directional micro alpha 或跨资产 reversion basket；
- `trade off`：放弃“它应该服务现有 15m breakout / retest / EMA setups 的 shared veto”这一原读法，并接受它对执行、容量、成本更敏感。

但这已经超出 bot6 本轮“从原 rank 再切一条 queue-facing 窄派生”的边界；当前最诚实动作仍是 **保留 park**。

## 7) 本轮结论
- `keep_park`
- 补充口径：`soft park，但偏硬；Rank 52 的 trade-flow imbalance veto 仍应维持 park。近两天的新 microstructure 证据说明 flow 主题未死，但它更像独立的 1m/3m raw-alpha / execution family，而不是原 Rank 52 可再诚实派生的 Rank 52b。`

## 8) 文件动作
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`
- 未改：`docs/TODO.md`

## 9) commit
- 本轮默认不做 commit。
- 原因：当前工作区共享脏文件很多，只做 park-reframe 最小必要改动，避免混提。
