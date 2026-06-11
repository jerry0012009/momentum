# 2026-03-30 19:07 UTC — Rank 257 / on-chain shock × predicted vol spike / BTC short-horizon mean reversion — survivor follow-up → background/P0

## 本轮执行对象
- cycle_plan 第 1 项：`Rank 257 / on-chain shock × predicted vol spike / BTC short-horizon mean reversion`
- 执行动作：作为当前唯一合法前排 survivor，执行它那唯一一次 decisive follow-up；继续锁定在 `fee-rate / tx-count shock × predicted high-vol state` 触发后的 BTC `3m/5m` post-spike sign mapping，并只回答统一事件时间对齐、统一 friction ladder 与同一执行口径下，`MR vs continuation` 是否有一侧还能保住可审计的成本后 edge。

## 读取依据
- policy：`docs/BOT2_BOT3_POLICY.md`
- runtime：`docs/BOT2_BOT3_STATE.md`
- fresh intake record：`research/optimization_loop/2026-03-30_1811_rank257_onchain_vol_spike_btc_mr_intake_keep_p1.md`
- digest：`research/quant_digests/2026-03-30_1348_onchain-vol-spike-btc-mr-alpha.md`
- 原文可读页：`https://link.springer.com/article/10.1007/s44257-025-00046-1`

## 这一步实际回答的问题
在不额外发明数据或口径的前提下，这条 survivor 的唯一 follow-up 能不能把对象从“值得测的前排假设”收口成“已有一侧方向足够诚实、足够清楚，值得升到 P2 继续 admission”？

## 核查结论
结论是：**不能；唯一 follow-up 用尽后应回到 `background/P0`，不升 `P2`。**

原因：
1. **这一步要求的是 sign 收口，但论文自身没有把方向讲清楚。**
   digest 已经指出正文同时出现 `volatility-based mean-reversion` 与 `predicted volatility > 0.7 做多 / < 0.5 做空` 两套互相不等价的交易叙述。也就是说，当前公开证据连“事件后该反着做还是顺着做”都没锁死。
2. **现有公开结果只支持“高波动状态可预测”，不支持 `3m/5m` post-spike MR 在统一成本后可交易。**
   论文给出的强证据是 forecast 层（如 Hybrid 的更低 MSE / 更高 R²）和一个作者自定义的 `5m hold, 0.1% cost` 回测汇总，但它没有把 `MR` 与 `continuation` 放在同一事件锚、同一成本口径下做 frozen A/B，也没有把 `3m/5m` 的方向映射单独报出来。
3. **survivor 预算只允许一次便宜诚实检查；这次检查已经把唯一 decisive blocker 暴露得够清楚。**
   当前阻碍不是还差一条普通稳定性补图，而是最核心的方向证据仍依赖作者叙述口径漂移。既然公开材料无法在统一执行口径下证明 `MR` 或 `continuation` 任一侧有明确成本后 edge，就不该继续占用前排资源。

## exit verdict
- verdict：`background/P0`
- 原因标签：`directionality_not_honestly_resolved`
- survivor follow-up budget：已用尽
- 是否升 `P2`：否

## 会改变系统认知的一句话
`Rank 257` 的唯一 survivor follow-up 已经诚实暴露出核心缺口：公开证据只能证明“链上 shock × 高预测波动”能识别高波动状态，却不能在统一事件锚与统一成本口径下证明 `3m/5m` 的 `MR` 或 `continuation` 任一侧有明确可交易 edge，因此本轮用尽唯一 follow-up 后回 `background/P0`。

## 本轮写回范围
- `Surviving candidate slot`：从 `Rank 257` 收口为 `none`
- `Background pool`：登记 `Rank 257` 本轮 park 结论
- `cycle_plan` 第 1 项：写回 `done`
- 不改 policy / brief / cron prompt
- 不重排后续小点

## reader-facing
- 这是 survivor 出口决策 + 层级变化，属于真实推进，应刷新首页。
