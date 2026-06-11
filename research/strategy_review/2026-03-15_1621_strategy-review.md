# 2026-03-15 16:21 UTC · Light Strategy Review

## 本轮一句话判断

这轮项目级排序仍然不变：`EMA = closest to paper`，`breakout = one_more_gate`，`Fibonacci = park`。但 **EMA 的 deployment-facing blocker 又收紧了一层**：bot3 已经真正交出了 `first-refresh delta` 与全 active `1d` lanes 的 daily refresh snapshot，所以当前最缺的已不再是 `queue / snapshot / verdict sync`，而是 **active 日频 refresh 数据能否稳定续跑**。因此本轮只做一个最小必要调整：把 EMA 下一步从“继续补 refresh 页面”收紧成 **先修 `Crypto-1d` 与 `贵州茅台-1d` 的 refresh 数据连续性**。

## 本轮先检查了什么

1. repo 状态与最近两条 optimization loop：
   - `2026-03-15_1548_ema-first-refresh-delta-top3.md`
   - `2026-03-15_1618_ema-daily-refresh-snapshot.md`
2. 当前 cron 状态：
   - `bot3-momentum-auto-opt-13m`：`lastRunStatus = ok`、`consecutiveErrors = 0`
   - `bot2-strategy-review-40m`：正常
   - `bot7-quant-digest-4h`：正常
3. `docs/TODO.md` 当前 deployment-facing EMA 剩余动作
4. `alpha_closure_board` 当前 admission 排位与 deployment ladder 口径

## 当前 strongest evidence

### 1) bot3 已把上轮要求的“真实 refresh 结果”交出来了

这轮最重要的事实是：bot3 并没有继续回去写近义 `queue / verdict sync`，而是给了两条真正更接近运行态的产物：
- `15:48`：`EMA top-3 first-refresh delta`
- `16:18`：`EMA all active 1d lanes daily refresh snapshot`

这说明上轮 bot2 的纠偏是有效的：EMA 已从“账本已开 + queue 已写死”，推进到了“同一张账本里出现真实 refresh 变化”。

### 2) EMA 当前最缺的 gate 已从“怎么记账”切换到“能不能持续续写”

`Q35` 与 `Q35b` 给出的最关键现实不是又多了一张表，而是：
- `创业板ETF 1d`：已有 `EMA BUY` + `long_open_since_2026-03-12`
- `美股 1d+1wk（日频）`：当前 `SELL / flat_3/3`
- `沪深300ETF 1d`：当前 `SELL / flat`

更重要的是全 active `1d` lanes 的 daily snapshot 把数据健康问题直接暴露出来：
- `live = 1`
- `cache fallback = 2`
- `data unavailable = 2`

其中两条 active 日频 lane（`Crypto-1d`、`贵州茅台-1d`）已经明确落成：
- `monitor_status = refresh_red_data_unavailable`
- `review_action = pause_refresh_fix_data_source`

这说明现在的主 blocker 已不再是“该不该继续做 paper/shadow 账本”，而是：**账本已经开始跑，但有两条 active lane 现在还续不起来。**

### 3) breakout / Fibonacci 的项目级位置没有发生足以改写排序的新变化

- **breakout**：当前仍是 `one_more_gate`；最近没有新的 `pure-test / down-tail` overturn evidence。
- **Fibonacci**：继续 archive。

因此这轮不需要重排三条线，也不需要把资源从 EMA 主线移开。

## 当前 weakest / should-park lines

1. **Fibonacci**：继续 archive，不抢资源。
2. **breakout same-sample retrospective slicing**：继续冻结；除非出现新的 forward / down-tail 命中。
3. **EMA 的近义 refresh 页面 / snapshot wording**：在 data continuity 还没修掉前，继续补这些页面的边际价值会明显下降。

## 本轮最小必要干预

### 只做 1 个动作：把 EMA 下一步收紧成“先修 refresh 数据连续性”

已在 `docs/TODO.md` 新增：

- `EMA：先修复 active 1d lanes 的 refresh 数据连续性（优先 Crypto-1d 与 贵州茅台-1d），不要在 data unavailable 还没清零前继续补近义 refresh 页面`。

目的很明确：
- 不改项目级总排序；
- 不改 cron；
- 不改 closure board 主文案；
- 只把 bot3 的下一步从“继续补 refresh 可见性”推进到“先把运行红灯清零”。

## 为什么这轮要动，而不是说“已经很好了先别动”

因为当前已经出现一个新的高杠杆 operational blocker：
- EMA 线确实是最接近 paper 的；
- 但既然现在已经真的开始写 refresh snapshot，那么 `data unavailable = 2/5 active daily lanes` 就不能再被当成“无伤大雅的实现细节”；
- 如果 bot2 这轮不把 TODO 收紧，bot3 很容易继续沿 `Q35 / Q35b / refresh wording` 再写一层说明，而不是优先修掉真正阻断连续 shadow/paper 续跑的问题。

所以这轮最有杠杆的小调整，就是：
**先把 active daily lanes 的数据连续性修掉，再继续谈更漂亮的运行页。**

## 下一步优先级 Top 1~3

### Top 1. EMA：修复 `Crypto-1d` 与 `贵州茅台-1d` 的 refresh 数据源连续性

目标：
- 让 active `1d` lanes 至少都能稳定写出 `data_health != refresh_data_unavailable`；
- 把当前 `pause_refresh_fix_data_source` 从红灯清掉；
- 然后再继续同一张账本的 market-close refresh / week-1 review。

### Top 2. EMA：在数据连续性恢复后，再继续真实 refresh / week-1 review

当前已经不缺 queue、snapshot 与首刷示例；真正下一层价值来自：
- 连续 refresh
- forward delta
- week-1 verdict

### Top 3. breakout：继续维持 `one_more_gate`，等待新的 forward / down-tail honesty

没有新证据前，不 reopen same-sample micro-slices。

## 本轮改动

- 已编辑 `docs/TODO.md`
  - 新增并前推：`EMA refresh 数据连续性修复（Crypto-1d / 贵州茅台-1d）`
- 新增 review 记录：
  - `research/strategy_review/2026-03-15_1621_strategy-review.md`
- 本轮不改：
  - `alpha_closure_board` 主排序
  - `bot2 / bot3 / bot7` cron 频率
  - breakout / Fibonacci 项目级 verdict

## 网页 / 表达建议

- 这轮不需要再改 closure board 主文案。
- 下一次值得改网页的条件不是“再写一张 refresh 页面”，而是：
  - `data unavailable` 从 `2` 清到 `0` 或明显下降；
  - 同一张 daily snapshot 能连续写出至少几轮真实 refresh。
- 在这之前，继续补“EMA 多接近 paper”的措辞，价值不高。

## cron / 节奏建议

- `bot2 40m`：不改
- `bot3 13m`：不改
- `bot7 4h`：不改

原因：
- 当前不是节奏问题；
- 是 **EMA 从 Step 3.x 往真正连续 shadow/paper 运行推进时，暴露出了数据连续性红灯**。

## paper trading admission verdict

- **closest to paper：EMA baseline family**
  - 当前最缺的 gate 已从 `paper spec / monitoring spec` 进一步收紧为：
  - **operational data continuity / refresh execution honesty**
  - 更具体地说：先把 active `1d` lanes 的 `data unavailable` 清掉，再继续看真实 refresh / week-1 review。
- **needs one more gate：support_breakout_v0**
  - 仍缺新的 `forward / pure-test / down-tail honesty`
- **park / archive：Fibonacci**

## 风险与不确定性

1. 当前两条 active lane 的数据断流，不代表策略失败；但它确实会阻断连续前瞻账本。
2. `fallback` 仍能暂时维持部分续写，但不应把 fallback 当成长期 deployment 正常态。
3. 若后续数据源修复后，EMA refresh 连续写几轮仍快速转弱，则下一个 gate 可能重新回到真正的 forward performance honesty，而不再是 data continuity。

## 本轮一句话结论（给 Jerry）

**EMA 现在已经不是“要不要开账本”的问题了，而是“账本已经在跑，但有两条 active 日频 lane 还续不起来”；所以这轮我不再催 bot3 继续写 refresh 页面，而是把 TODO 明确改成先修数据连续性。**
