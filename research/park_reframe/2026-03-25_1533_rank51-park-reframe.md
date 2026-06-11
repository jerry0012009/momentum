# 2026-03-25 15:33 UTC — Rank 51 park reframe review

## 结论
- `source_rank`: `Rank 51`
- `verdict`: `keep_park`
- `original verdict kept`: `park`
- 一句话：**Rank 51 确实证明了 `session VWAP reclaim + breadth` 能减少一部分假防守，但它在 24/7 crypto 里更像“少做错单的 shared confirmation 残余”，不足以形成新的诚实窄派生；而且 2026-03-24 新出现的 `VWAP 偏离 + RSI 极值 + anti-trend veto` 证据更像另一条完整 raw-alpha family，不该硬写成 Rank 51b。**

## 为什么本轮看它
- 按 `bot6` 轮转，当前仍应优先看 `Rank 50+`。
- 最近 7 天内未见 `Rank 51` 的 park-reframe 复盘记录；最近被碰过的是 `Rank 50 / 53 / 67 / 92 / 101`，因此本轮换到同号段里尚未复盘的 `Rank 51`。
- `Rank 51` 属于那种“不是纯硬失败、而是有一点减错单痕迹”的 parked 条目，符合 bot6 优先看“有局部正 pocket / 单一 blocker”的筛选口径。

## 原 rank 为什么 park
根据 `research/optimization_loop/2026-03-18_0922_rank51-clean-replication-park.md`：
- `touch_only @ 6bps` 跨资产约 `-79.13%`，`false_retest_4bars_rate≈75.57%`，说明“只碰 VWAP”几乎全是噪声。
- 加 `reclaim` 后仍约 `-49.69%`，只是少亏，不是转正。
- 主读法 `touch_reclaim_plus_breadth @ 6bps` 虽把 `false_retest_4bars_rate` 压到约 `39.20%`，而且 `trade_count_retention≈39.10%`，没有直接稀到零；但跨 `BTC/ETH/SOL` 仍是：
  - `mean_total_return≈-43.79%`
  - `positive_asset_ratio=0/3`
  - 三段 `time-pocket` 全负
- 所以原 rank 被 park，不是因为“完全没信息”，而是因为它只做到**少犯错**，没做到**成本后可交易**。

## 它更像 hard park 还是 soft park
- 我这里给它的读法是：**soft park，但偏硬**。
- 软的部分在于：`VWAP reclaim + breadth` 确实有信息量，至少显著压低了假防守比例。
- 偏硬的部分在于：
  1. 跨资产没有一个正样本；
  2. 三个 time bucket 全负；
  3. 改善主要停留在“少亏”，而不是形成可独立承接的新 pocket。

## 有没有“可救信号”
有，但很弱，而且更像残余语义，不像可单独重开的新 rank：
1. **VWAP reclaim 本身比 touch-only 诚实得多**：说明“重新站回防守线”这件事比“只是碰到线”更重要。
2. **breadth 确实在压 false retest**：从约 `75.57% -> 39.20%`，这不是纯随机噪声。
3. 但这些信号共同指向的是：
   - 它更像一个 shared confirmation / defense 证据层；
   - 不是一条能单独升级成 queue-facing 新 hypothesis 的 alpha 线。

## 最值得改的唯一一刀是什么
如果非要写“唯一一刀”，最自然的一刀是：
- **把 `session VWAP defense` 从 continuation/retest 的 shared gate 读法，改写成“VWAP 偏离后的短周期均值回归 raw alpha”语义。**

但这里我**明确不 draft**，原因是：
- 这已经不是在拯救原 Rank 51 的 continuation-defense 叙事了；
- 它本质上是在切换到另一条新 family：`VWAP 偏离 + RSI 极值 + volume 脉冲 + anti-trend veto` 的完整 raw alpha。
- 这条新 family 已被 `research/quant_digests/2026-03-24_1558_vwap-rsi-antitrend-gated-meanreversion-raw-alpha.md` 更诚实地表述为 **独立 raw alpha**，而不是 `Rank 51` 的窄 reframe。

## 是否值得形成新的 derived hypothesis
- **不值得。**
- 本轮结论保持 `keep_park`。

### 为什么不值得硬写成 `Rank 51b`
1. **会推翻而不是保留原审计语义**
   - 原 Rank 51 的主题是 `session VWAP reclaim + breadth gate`，服务 continuation / retest。
   - 若改成 `VWAP deviation mean reversion`，主题已经从“防守确认层”切成“反向回归 raw alpha”，这不是窄 reframe，而是换题。

2. **残余价值已更适合被新 family 吸收**
   - 2026-03-24 的新 digest 已给出更完整、更诚实的写法：
     - alpha 本体 = `VWAP 偏离 + RSI 极值 + volume spike` 的短周期回归
     - gate 本体 = `15m anti-trend veto`
   - 这比从原 Rank 51 勉强扭出一个 `51b` 更自然。

3. **当前证据不支持“继续做 shared gate 还能救活”**
   - 原最优臂已经证明：就算 false retest 降下来了，收益还是深负；
   - 说明 blocker 不只是确认层太粗，而是**方向职责可能放错层**。

## trade on / trade off（仅作为 why-not 记录，不构成 draft）
- 如果硬写，会变成：
  - `trade on`: 用 VWAP 偏离做短周期均值回归，而不是 continuation defense
  - `trade off`: 放弃原 Rank 51 的防守确认叙事，转去另一条 raw-alpha 赛道
- 正因为这个 trade-off 已经超出“单轴窄修改”，所以本轮不应写成 derived hypothesis。

## 最终判断
- `Rank 51` 原 `park` verdict 应保留。
- 它更像 **soft park，但偏硬**。
- 存在的“可救信号”只够说明：
  - `VWAP reclaim` 比 `touch-only` 诚实；
  - `breadth` 能压假防守；
  - 但这还不足以让原 Rank 51 诚实派生出新的 `Rank 51b`。
- 更诚实的动作是：**承认这条残余信息已更像被新的 VWAP mean-reversion raw-alpha family 吸收，而不是继续给原 rank 续命。**

## 本轮文件改动
- 新增本日志：`research/park_reframe/2026-03-25_1533_rank51-park-reframe.md`
- 更新：
  - `research/park_reframe/INDEX.md`
  - `docs/PARK_REFRAME_QUEUE.md`

## git / 提交
- 本轮仅做最小必要文档改动。
- 默认不做 commit：工作区长期存在与本轮无关的脏文件，当前不适合安全 selective commit。
