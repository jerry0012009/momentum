# Rank candidate / seesaw negative lead-lag alt basket — fresh intake park

- 时间：2026-03-26 17:57 UTC
- 对象：`research/quant_digests/2026-03-26_1555_seesaw-negative-leadlag-alt-basket.md`
- 轮次角色：bot3 fresh intake 最小首判
- 结论：`park`

## 本轮只回答一个问题
`5m large-cap shock -> alt basket 反向 seesaw` 这条 cross-sectional raw alpha，是否已经值得进入 survivor。

## 证据收口
本轮直接采用 digest 已经落好的最小 transfer check，不额外泛化主题：

1. 最诚实 pocket 只剩一条：`BTC+ETH 5m leader shock top20% -> 反向做 SOL/XRP/DOGE/ADA/LINK basket，持有 3 根 5m`。
2. 这条 pocket 的 follower-only gross 只有 **+1.64 bps/trade**，hit rate **53.9%**；spread-hedged 版本更薄，只有 **+0.88 bps**。
3. 同主题一旦迁到 `15m signal bar` 就直接翻负：top20% 为 **-1.45 bps**，top10% 为 **-1.80 bps**。
4. 论文摘要支持“negative lead-lag / seesaw”这个研究方向成立，但当前 desk 可复现版本仍停留在一个 execution-fragile 的 5m follower-only 小 pocket，上不了更稳的跨窗口或更诚实的对冲口径。

## 为什么这轮不进 survivor
survivor 应保留给“值得再花那唯一一次 follow-up 预算”的对象；这条线当前还没到那个阈值。

- 它不是没有信号，而是 **信号厚度太薄、对执行太敏感**；
- 现在最强结果已经卡在很窄的 `5m top20 shock + hold 15m` 口袋里；
- 一旦换成更宽时间粒度或更中性的 spread 读法，优势就明显变薄甚至翻负；
- 因此本轮更诚实的记账方式是：把它留在 background/research pool 作为 `negative lead-lag` 方向证据，而不是给它前排 survivor 配额。

## 单一句子结果
`5m large-cap shock -> alt basket 反向 seesaw` 虽然在 `5m top20 shock + hold 3 bars` 上有正向 pocket，但 edge 仍过薄且高度依赖 follower-only 执行、无法迁移到更稳的 `15m` 或 spread 口径，因此本轮 fresh intake 结论为 `park`，不进入 survivor。

## 运行态需回写
- `Fresh intake slot`：更新为本对象已完成首判且结论 `park`
- `cycle_plan[3]`：写入上述单句结果并标记 `done`
- 其余前排槽位不变
