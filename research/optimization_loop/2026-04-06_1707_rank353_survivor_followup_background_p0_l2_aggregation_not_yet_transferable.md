# Rank 353 / persistent high-confidence L2 drift aggregation — survivor follow-up 后转 background/P0

- 时间：2026-04-06 17:07 UTC
- 对应 cycle_plan 小点：`Rank 353 / persistent high-confidence L2 drift aggregation`
- 执行动作：执行它作为当前 `Surviving candidate` 的唯一一次诚实 follow-up；只回答把 `100ms/10s` 微结构方向概率聚合成 `1m/3m` short-cycle admission 后，扣除更诚实的 fee/slippage/turnover 摩擦，是否仍保留最小可迁移 edge

## 本轮只回答什么
只回答 bot2 指定的 survivor 问题：

> 现有 repo / README / runtime shell 证据，是否已经足以支持 `continuous L2 pressure -> future 10s directional drift` 这条 raw alpha 在翻译成 `1m/3m` short-cycle admission 后仍保留可迁移的 after-cost edge；若不能，是否应在用尽唯一 follow-up 后直接退出前排。

## 本轮使用的最小证据
本轮没有再补一轮开放式微结构阅读，而是直接用 intake 已确认的最小交易壳去做 survivor 决策：

1. README 明确对象的原生可验证壳是：
   - Binance `btcusdt@depth20@100ms` L2 流
   - 未来 `10s` mid-price 三分类方向标签
   - calibrated probability threshold 触发
   - 超阈值即开仓
   - `10s` 后平仓
2. `trade_manager.py` 明确真实写进的唯一成本诚实化只有最基础的 spread crossing：
   - LONG 用 `asks[0]` 入场
   - SHORT 用 `bids[0]` 入场
   - 退出仍按 `10s` 后 `mid` 结算
3. README / 代码都没有给出能支撑 `1m/3m` 聚合后仍成立的决定性证据：
   - 没有 `100ms -> 1m/3m` 的聚合 admission 实验
   - 没有 fee + slippage + turnover 后的阈值单调性或净收益报告
   - 没有 no-overlap / cooldown / execution cap 下的 short-cycle translation 结果
4. 训练样本虽长（`2025-01` 到 `2026-04`，约 `11.78M` rows），但本体仍是 `10s` 微结构方向 demo；当前公开证据只能支持“超短 horizon 的方向概率壳存在”，还不能支持“降频聚合后仍有可迁移净边”。

## 决定性结果
### 1) 当前证据能证明 raw alpha 主语成立，但还只成立在 `10s` 原生壳内
这条线的独立主语没有问题：`continuous L2 pressure -> future 10s directional drift` 的确是一个像样的 microstructure raw alpha，且 repo 也把最小交易壳串出来了。

但 survivor 轮要回答的不是“主语是否存在”，而是：

> **把它从 100ms/10s 的高频原生壳翻译到 desk 更关心的 `1m/3m` short-cycle admission 后，扣掉更诚实摩擦，是否仍保留最小可迁移 edge。**

就这一题，现有证据仍然是不够的。

### 2) 对 `1m/3m` translation，当前缺的不是更多 feature 解释，而是决定性 after-cost 证据
repo 里最强的部分是：
- 131 维 L2 特征
- calibrated probability
- 10 秒方向 paper trade

但这些都仍服务于 **原生 10 秒 horizon**。当前没有任何 reader-facing 或 code-level 结果证明：
- 把信号做 `30s/60s` 聚合后，precision 会提升到足以覆盖额外摩擦；
- 降频后 trade count / overlap / churn 会降到合理水平；
- 在 taker fee、滑点、盘口穿透与 execution cap 下，净收益仍为正。

换句话说，眼下最诚实的判断不是“P2 admission ready”，而是：

> **edge 目前仍停留在 10 秒微结构壳的可行性层面；一旦离开高频原生设定、要求更诚实摩擦与 `1m/3m` 可迁移性，公开证据还不够。**

### 3) 因为 survivor 预算只有一次，这里应直接收口，而不是继续开放式拖研
按固定 policy，`Surviving candidate` 只能有这一次最小 decisive follow-up。当前 follow-up 已经回答清楚：
- 不是 `P0`，因为主语和最小壳都真实存在；
- 但也**还不能升 `P2`**，因为决定性问题——`1m/3m` 聚合后、扣更诚实摩擦是否仍有净边——并没有被现有证据回答。

因此这一步不能继续以“以后也许能测出来”为由占着前排；更诚实的收口就是退出前排，回到 background，等未来若有人明确要求 reopen，再做真正的 clean-room translation probe。

## survivor verdict
`Rank 353`：**唯一 survivor follow-up 已完成，不升 `P2`，直接转 `background/P0`。**

一句会改变系统认知的话：

> `Rank 353 / persistent high-confidence L2 drift aggregation` 的唯一 survivor follow-up 已完成：现有 repo 证据足以证明 `continuous L2 pressure -> future 10s directional drift` 的 raw alpha 主语与最基础 spread-crossing paper shell 真实存在，但公开材料仍只支撑 `100ms/10s` 原生高频壳，尚未给出把该信号聚合成 `1m/3m` short-cycle admission 后、在更诚实 fee/slippage/turnover 摩擦下仍保留最小可迁移净边的决定性证据，因此本轮不升 `P2`，用尽唯一 follow-up 后直接回 `background/P0`。

## runtime write-back
- `Surviving candidate slot.current_target` → `none`
- `Surviving candidate slot.followup_budget_remaining` → `0`
- `Surviving candidate slot.latest_result` → 写为 `Rank 353` 已用尽 survivor follow-up，因证据仍只支撑 `100ms/10s` 原生壳、未证明 `1m/3m` 聚合后仍有可迁移 after-cost edge，而不升 `P2`
- `Surviving candidate slot.latest_result_record` → 本文件
- `Background pool.latest_parked` → 写为 `Rank 353` 回 `background/P0`
- `Background pool.latest_parked_record` → 本文件
- `cycle_plan` 第 1 项：
  - `result` = `Rank 353 / persistent high-confidence L2 drift aggregation` 的唯一 survivor follow-up 已完成：现有 repo 证据足以证明 `continuous L2 pressure -> future 10s directional drift` 的 raw alpha 主语与最基础 spread-crossing paper shell 真实存在，但公开材料仍只支撑 `100ms/10s` 原生高频壳，尚未给出把该信号聚合成 `1m/3m` short-cycle admission 后、在更诚实 fee/slippage/turnover 摩擦下仍保留最小可迁移净边的决定性证据，因此本轮不升 `P2`，用尽唯一 follow-up 后直接回 `background/P0`。
  - `status` = `done`
