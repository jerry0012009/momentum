# Rank 177 / funding-boundary-post-settlement-spread-alpha — fresh intake 首判（keep_P1）

- 时间：2026-03-26 03:26 UTC
- 对象：`research/quant_digests/2026-03-26_0202_funding-boundary-post-settlement-spread-alpha.md`
- 轮次角色：bot3 auto optimization
- 动作类型：fresh intake first verdict
- 结论：**keep_P1**
- 正式 Rank：**177**

## 本轮只回答一个问题
这条对象是否值得作为一个新的前排候选继续保留？

答案：**值得，但保留的必须是一个非常具体的骨架**——
**`post-settlement long richest funding / short cheapest funding spread` 这条 funding-boundary event-driven relative-value pocket**，而不是把原 repo 当成单腿 latency 工具，也不是泛泛“funding 有信息量”。

## 为什么这次给 keep_P1
1. **对象足够具体，可独立成策略骨架**
   - 事件时钟清楚：`00/08/16 UTC` 主 funding 结算边界；
   - 排序变量清楚：刚落地 funding snapshot 的 richest vs cheapest；
   - 交易表达清楚：`long highest-funding / short lowest-funding` 的等美元 spread；
   - 持有窗口也已有初始 pocket：`15m~60m`，其中 `60m` 最像可存活版本。

2. **它不是“赚 funding 本身”，而是结算后 crowding 延续**
   这点很关键。若只是 repo 原意里的 boundary latency / 临门一脚方向赌法，容易落成不稳的微结构窗口；但 digest 已经把它 desk-transfer 成一个更诚实、可复现的 post-settlement spread alpha，这个改写是有价值的。

3. **最小快检给出的量级，值得买一次 survivor follow-up**
   digest 内 21 天、125 个主结算事件的最小快检显示：
   - `15m gross spread ≈ +26.7 bps`
   - `60m gross spread ≈ +98.2 bps`
   - `gap 前 25%` 事件里 edge 更集中

   这还不是 admission 级证据，但已经足够说明：它不像纯噪声题材，值得拿一次 survivor 预算去做更诚实的流动性/方向拆分验证。

## 为什么这轮还不能直接升 P2
当前证据仍主要来自 digest 里的最小公共数据快检，离 admission 还差几个关键收口：
- 高流动性 universe 过滤后是否仍成立；
- `long richest only`、`short cheapest only`、`spread` 三种表达究竟哪边贡献 alpha；
- `top1/top3/top5` 与 `+0m/+1m/+3m entry` 是否稳定；
- 粗成本下 `15m` 与 `60m` 的净后生存线是否仍然诚实。

所以这轮最诚实的位置是：**先给 P1，不抢跑到 P2。**

## 本轮改变的系统认知
**Rank 177：fresh intake 首判完成，保持 P1；值得保留的是 `post-settlement long richest funding / short cheapest funding spread` 这条 funding-boundary event-driven relative-value 骨架，而不是把 repo 误读成单腿 latency 工具。**
