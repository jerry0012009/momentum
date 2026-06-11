# Rank intake first verdict — hour-of-week 条件化 XS market-neutral alpha

- 时间：2026-04-01 22:00 UTC
- 执行者：bot3
- 对象：`research/quant_digests/2026-04-01_2045_hour-of-week-xs-marketneutral-alpha.md`
- 动作：fresh intake first verdict
- 结论：`不进入前排，回 background / P0`

## 为什么这轮不保留到 P1
这条线不是完全没东西：它已经把对象收口成一个可描述的 raw alpha 轮廓——`hour-of-week` 条件化、横截面 `long-short`、weekday after-hours 做短窗 reversal、weekday regular-hours 做中窗 momentum、再用 rank-demean + sleeve blend 合成。但就当前项目的 runtime 标准看，它还不够诚实，也不够新，暂时不值得占用前排 survivor 预算。

本轮决定它回 `background / P0`，核心原因有三条：

1. **主题重叠度太高，当前更像旧 clock-family / same-slot 叙事换壳。**  
   digest 自己已经承认，这条线本质上是 `hour-of-week` / `same-hour` 条件化的时钟家族 alpha。当前项目里，clock-family 相关对象刚做过更严格的长期与跨市场审视；现阶段系统对“时钟口袋”不会再因为 notebook headline 或 session bucket 叙事就额外给前排预算。

2. **first verdict 所需的 honesty / execution 关键信息仍停留在 repo 口径，而非本项目 clean-room 口径。**  
   这条线虽然写出了可复刻实验框架，但还没有给出基于本项目现实 universe 的最小迁移证据：
   - 主流 perp universe 下到底哪些币、哪些 hour bucket 仍存活；
   - `H1/H3` 两条腿在统一 friction ladder 下是否仍有 after-cost 净边；
   - `1h` 生成、`15m/5m` 执行后 turnover 与 edge 是否一起塌掉；
   - 这种按 hour bucket 切换方向的做法，到底是稳定 XS alpha，还是少数时段 pocket 的样本内拼接。

3. **当前没有足够理由把它视为独立于既有 clock research 的新前排对象。**  
   如果后面真要 reopen，更合理的方式不是把它当“全新 raw alpha”继续推进，而是把它并回 `clock-conditioned cross-sectional scheduler` 这一研究族，要求它直接回答：在现实 perp universe、现实成本和年度拆分下，哪些 bucket 还能活，哪些只是历史 session 结构的短暂产物。

## 本轮系统认知变化
- 新增判断：`hour-of-week 条件化 XS long-short blend` 目前更像 **既有 clock-family / same-slot 研究的衍生变体**，而不是值得单独锁定 survivor 预算的新前排 raw alpha。
- 因此这条 intake 本轮**不分配 Rank**，直接留存为 `background / P0` 证据对象。

## 对后续 reopen 的唯一合理触发
只有在后续有人补出下面这种更硬的 clean-room 证据时，才值得重新拉回前排：
- Binance perp 主流 universe 的统一 replication；
- `weekday after-hours reversal` 与 `weekday regular-hours momentum` 至少一条腿在 after-cost 口径下仍稳定为正；
- 年度 / 币种 / bucket 拆分后不是由极少数 pocket 独撑；
- 子 bar 执行与 turnover 扣除后仍未被吃光。

在这之前，最诚实的 runtime 处理就是：**记录 insight，但不占前排。**
