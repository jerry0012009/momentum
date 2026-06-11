# 2026-03-25 00:55 UTC — Rank 34 park reframe revisit

- source rank: `Rank 34 / chip-distribution trapped-holder reclaim / winner-ratio gate`
- current authoritative verdict in `docs/TODO.md`: `park / evidence pool`
- this round verdict: `keep_park`
- original park verdict kept: `yes`
- prior derived candidate already on queue: `none`

## 1) 为什么这轮选 Rank 34
- 本轮仍受 `Rank 1~37` 范围约束；
- 近 7 天内这一区间的大多数 parked rank 都已被 `bot6` 触碰过，因此本轮退而选一个**审计边界清楚、但还没有派生 rank** 的旧项复核；
- `Rank 34` 上次 park-reframe 记录是 `2026-03-21 04:42 UTC`，不是今天刚复盘的条目；
- 这条线最适合回答一个很具体的问题：`synthetic shares / turnover anchor sensitivity` 这么重的 blocker，最近有没有新证据强到足以把它诚实地改写成一个窄 reframe。

## 2) 原 Rank 为什么会 park
原 Rank 34 被 park，不是因为 baseline 略亏，而是因为**核心结果对假设锚过敏**：

- 原始 `raw_baseline` 在 `6bps/side` 下三资产均值约 `-7.38%`，并不成立；
- 看似最好的主变体 `chip_cost_reclaim`，只有在 `conservative anchor` 下才显得漂亮：
  - `mean_total_return ≈ +18.14%`
  - `positive_asset_ratio = 3/3`
  - `mean_trades ≈ 101`
- 但一旦把锚放宽到更中性/更激进：
  - `neutral anchor @ 6bps`：`mean_total_return ≈ +13.72%`，但 `positive_asset_ratio` 直接掉到 `1/3`，中位数已转负；
  - `aggressive anchor @ 6bps`：`mean_total_return ≈ -18.62%`，`positive_asset_ratio = 1/3`；
- 成本再上去也很快塌：`conservative chip_cost_reclaim` 到 `15bps` 就只剩 `≈ -1.47%`，`20bps` 已明显转负。

所以原 rank 被 park 的真正原因不是“图形主题完全没故事”，而是：
**这条线的所谓 edge 主要寄生在对 synthetic shares / turnover anchor 的乐观写法上，离开那组假设就不稳。**

## 3) 它更像 hard park 还是 soft park
我这轮判断：**更像 hard park。**

原因：
- 它不是单一参数没调好，而是核心定义本身依赖一个难以诚实冻结的构造量；
- 最好看的结果来自最保守、也最容易“看起来合理”的 anchor 写法，而不是跨 anchor 稳定成立；
- 最近 desk 的新证据主流都在往 `raw alpha skeleton`、`cost governance`、`queue-facing admission/risk overlay` 收敛，并没有给 `chip-distribution trapped-holder reclaim` 这条线提供一个更诚实的低摩擦 proxy。

如果硬要说 soft 的一面，只剩下：
- `conservative anchor` 下确实留下了一个表面上的正 pocket；
- 但这个 pocket 一跨 anchor 就散，审计价值更像“提醒我们别被代理变量骗”，而不是可重开的策略种子。

## 4) 有没有“可救信号”
**有一丝，但不够形成新假设。**

唯一还能叫“可救信号”的，是：
- 在 `conservative anchor` 下，`chip_cost_reclaim` 与 `chip_cost_reclaim_plus_winner_ratio` 都留下了正收益、低假突破比率的 pocket；
- 说明“筹码拥挤/套牢盘重夺”这个直觉未必完全错。

但这丝信号很快被三个事实压掉：
1. **跨 anchor 不稳**：从 conservative 切到 neutral / aggressive，结论迅速恶化；
2. **成本不厚**：到 `15~20bps` 基本失真；
3. **代理量本身不诚实**：问题不在 entry/exit 太粗，而在核心 explanatory variable 就高度 assumptions-sensitive。

所以这里的“可救信号”更像一个研究提醒：
- 也许未来若有更可信的链上/订单流持仓分布代理，可以另开新 family；
- 但它不足以从原 Rank 34 里切出一个诚实的 `Rank 34b`。

## 5) 最值得改的唯一一刀是什么
如果非要保留唯一一刀，我认为只剩下这条：

**把 `chip-distribution reclaim` 从可交易 trigger 降级成离线 crowding/context 证据层，而不是继续当 15m 可执行 gate。**

也就是：
- 不再让它决定 bar-level allow/deny；
- 只把它当成一个“事后解释/背景拥挤度标签”，用于辅助理解已有 setup 的环境。

但这条一刀的问题也很明显：
- 一旦降到这种程度，它已经更像“解释变量再降级”，不是 bot2 值得入板的窄 reframe；
- 而且当前没有新的低假设代理去支撑它，仍然停留在旧的 assumption-sensitive 基础上。

所以：
- **唯一值得改的一刀我能写出来；**
- **但它还不值得升级成 derived hypothesis。**

## 6) 是否值得形成新的 derived hypothesis
**不值得。**

原因很直接：
- 原 `park` verdict 的审计意义非常强，完全没必要推翻；
- 最近新增的 quant digests 虽然很多，但主流是在讲 `pairs / stat-arb / raw mean-reversion / raw momentum skeleton / cost governance`，并没有给出一个新的、低假设依赖的 `chip-distribution` 可执行代理；
- 若现在硬写 `Rank 34b`，大概率只是把原来的 assumption-sensitive 变量换个名字继续讲一遍。

因此本轮最终结论仍是：`keep_park`。

## 7) 本轮回答（按要求汇总）
- 原 rank 为什么 park：因为 edge 高度依赖 `synthetic shares / turnover anchor` 的乐观写法，跨 anchor / 跨成本很快失真；
- 它更像 hard 还是 soft：`hard park`；
- 有没有可救信号：有一个很弱的 conservative-anchor pocket，但本质仍是 assumption-sensitive，不够诚实；
- 最值得改的唯一一刀：把 `chip-distribution reclaim` 从交易触发降级成离线 crowding/context 证据层；
- 是否值得形成新的 derived hypothesis：`不值得`；
- 本轮最终结论：`keep_park`。

## 8) 对 queue 的实际含义
- `Rank 34` 继续留在 `park / evidence pool`；
- 本轮不新增 `Rank 34b`；
- 默认不改 `docs/TODO.md` 顶部排班。

## 9) 文件与提交说明
- 本轮只更新本日志、`research/park_reframe/INDEX.md`、`docs/PARK_REFRAME_QUEUE.md`；
- 未做 git commit：工作区存在大量与本轮无关的脏文件，当前不适合安全地 selective commit。
