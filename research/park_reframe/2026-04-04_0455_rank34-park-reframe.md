# 2026-04-04 04:55 UTC — Rank 34 park reframe revisit

- source rank: `Rank 34 / chip-distribution trapped-holder reclaim / winner-ratio gate`
- current authoritative verdict in `docs/TODO.md`: `park / evidence pool`
- this round verdict: `keep_park`
- original park verdict kept: `yes`
- prior derived candidate already on queue: `none`

## 1) 为什么这轮选 Rank 34
- 本轮按用户要求回到 `Rank 1~37` 已 park 区间；
- 近 7 天里 `Rank 34` 没有被重复复盘，满足低频复看约束；
- 它的 park 原因审计边界一直很清楚：不是 entry 小瑕疵，而是核心 proxy 本身 assumptions-sensitive；
- 最近新增的 `rolling POC / value-area displacement` 证据（见 `2026-04-03_2224_poc-valuearea-fill-sanity-alpha.md`）与 Rank 34 同属 volume-profile / inventory-anchor 主题，正好可以回答：这是不是给 Rank 34 留下了一个诚实的窄 reframe 入口。

## 2) 原 Rank 为什么 park
原 Rank 34 被 park 的核心原因不是“收益略差”，而是：
**它的 edge 主要寄生在 synthetic shares / turnover anchor 的乐观写法上。**

原 clean replication 已经把这个点审计得很清楚：
- `raw_baseline` 在 `6bps/side` 下三资产均值约 `-7.38%`，base line 本身不成立；
- 表面最好看的 `chip_cost_reclaim` 只在 `conservative anchor` 下好看：
  - `mean_total_return ≈ +18.14%`
  - `positive_asset_ratio = 3/3`
- 但切到更中性或更激进 anchor 后迅速退化：
  - `neutral anchor @ 6bps`：均值仍勉强为正，但 `positive_asset_ratio` 已掉到 `1/3`；
  - `aggressive anchor @ 6bps`：均值直接转成明显负值；
- 成本再提高到 `15~20bps`，就连 conservative pocket 也站不稳。

所以原 rank 被 park，不是因为“筹码/套牢盘故事完全没直觉”，而是因为：
**交易结论过度依赖一个很难诚实冻结的持仓分布代理。**

## 3) 它更像 hard park 还是 soft park
这轮我仍判断：**更像 hard park。**

理由：
- blocker 在核心 explanatory variable，而不只是阈值/exit/过滤层；
- 最好看的结果始终依赖最保守、也最容易“看起来合理”的 anchor 写法；
- 一旦把假设放宽，跨资产稳定性和成本生存线就明显塌掉。

如果勉强说它有 soft 的一面，也只剩：
- conservative anchor 下确实留下过正 pocket；
- 这说明“库存拥挤 / trapped-holder reclaim”这类市场直觉并非完全虚无。

但这点 soft 成分不足以改变总判断，因为 pocket 的成立条件本身就不够诚实。

## 4) 有没有“可救信号”
**有很弱的可救信号，但不够形成新假设。**

唯一还能算信号的是：
- conservative anchor 下 `chip_cost_reclaim` 与 `chip_cost_reclaim_plus_winner_ratio` 都留下过正 pocket；
- 最近新增的 `rolling POC / value-area displacement` 证据也说明，volume-profile / inventory-anchor 主题本身还在别的宿主里有信息量。

但这组“可救信号”并不是 Rank 34 本体被救，而更像说明：
1. **主题还活着，宿主不对**——新 evidence 更像新的单资产 raw-alpha / feature family；
2. **旧 proxy 仍不诚实**——Rank 34 依赖的是 synthetic shares / turnover anchor，不是更直接的 price-volume displacement；
3. **角色错位已很严重**——如果要保留主题，最好是另开新 family，而不是从旧 Rank 34 硬切一条“看起来像同一条线”的 34b。

所以它的“可救信号”更像是：
- 这个主题值得在别处继续研究；
- 但不值得再从原 Rank 34 里派生一个 queue-facing reframe。

## 5) 最值得改的唯一一刀是什么
如果非要保留唯一主修改轴，我认为仍只有这一刀：

**把 `chip-distribution reclaim` 从可交易 trigger 降级成离线 crowding/context 证据层，而不是继续当 15m 可执行 gate。**

也就是：
- 不再让它决定 bar-level allow/deny；
- 只把它当成一种解释拥挤度、库存压力或背景接受度的附属注释。

但问题也很明显：
- 这已经不像 bot2 值得入板的窄 reframe；
- 它没有形成一个新的、可直接 clean replication 的 queue-facing hypothesis；
- 而且最近新证据的真正去向，是 `POC / value-area displacement` 这一类新的 raw-alpha / feature family，不是旧 Rank 34 的 proxy 继续 overlay 化。

因此：
- 这条唯一一刀可以作为研究口径保留；
- 但不值得升级成新的 derived hypothesis。

## 6) 是否值得形成新的 derived hypothesis
**不值得。**

原因：
- 原 `park` verdict 的审计意义依然很强，没必要推翻；
- 近期新增的 volume-profile / POC 证据并没有修复 Rank 34 的 assumptions-sensitive proxy，反而进一步说明：若主题还值得追，应该在新宿主里追；
- 当前若硬写 `Rank 34b`，大概率只是把旧 proxy 改名后继续讲一遍，审计价值很弱。

所以本轮最终结论仍是：`keep_park`。

## 7) 本轮回答（按要求汇总）
- 原 rank 为什么 park：因为 edge 高度依赖 `synthetic shares / turnover anchor` 的乐观写法，跨 anchor / 跨成本后很快失真；
- 它更像 hard 还是 soft：`hard park`；
- 有没有可救信号：有一点，说明 volume-profile / inventory-anchor 主题在别的宿主里还有信息量，但不足以救回旧 Rank 34；
- 最值得改的唯一一刀：把 `chip-distribution reclaim` 降级成离线 crowding/context 证据层；
- 是否值得形成新的 derived hypothesis：`不值得`；
- 本轮最终结论：`keep_park`。

## 8) 对 queue 的实际含义
- `Rank 34` 继续留在 `park / evidence pool`；
- 本轮不新增 `Rank 34b`；
- 默认不改 `docs/TODO.md` 顶部排班。

## 9) 文件与提交说明
- 本轮只更新本日志、`research/park_reframe/INDEX.md`、`docs/PARK_REFRAME_QUEUE.md`；
- 未做 git commit：工作区存在大量与本轮无关的脏文件，当前不适合安全地 selective commit。
