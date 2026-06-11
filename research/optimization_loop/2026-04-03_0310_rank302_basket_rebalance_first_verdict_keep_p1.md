# Rank 302 — cointegrated basket equal-weight drift × threshold rebalance

- 时间：2026-04-03 03:10 UTC
- 轮次类型：bot3 auto optimization
- 对象：`research/quant_digests/2026-04-03_0136_coint-basket-hfra-rebalance-alpha.md`
- 本轮动作：fresh intake first verdict
- 结论：`keep_P1`

## 为什么这轮不判成 background/P0

这条线虽然仍属于 `relative-value / stat-arb / cointegration` 大家族，但它和当前池里已存在的几类主语并不相同：

1. **不是普通 pair spread / OU fade 的多腿扩写**
   - 既有很多线的错价代理是 `spread residual / OU z-score / stationary factor residual`。
   - 这条线的错价代理更直接：**篮子内各腿对等权目标的权重漂移**。
   - 也就是说，alpha 主语不是“残差偏离会回去”，而是“同一篮子里谁短时跑太快/太慢，导致等权结构失衡，而 threshold rebalance 会把这种失衡持续 harvest 掉”。

2. **不是只是把 pair 扩成 basket**
   - 项目里已经有 `dynamic-factor / market-neutralized / Johansen basket` 等多腿 stat-arb 主题。
   - 这些线更偏向：先剥公共因子 / 找 stationary vector，再对 residual 或排序结果做交易。
   - 本对象更像一个独立 desk 容器：**equal-weight drift + threshold rebalance + continuous adjustment**。
   - 它的最小交易卡已经清楚到可以独立实验：`2/3/5` 腿、阈值 sweep、continuous rebalance vs flat-to-flat、trend/vol gate、BTC beta 残余控制。

3. **公开数据复现路径足够明确**
   - 用公开 K 线就能先做第一版。
   - 不依赖私有订单流或难拿的数据源。
   - 论文给了篮子大小、阈值扫描、成本口径、regime split，足以先搭 clean-room baseline。

## 为什么这轮也不直接升 P2

尽管主语已独立，但当前还没到 `P2 admission` 的诚实门槛，主要因为最关键的 transfer 风险还没被最小化验证：

1. 原文核心样本是 **BTC 计价现货**，而我们常做的是 **USDT perp**；
2. published headline 很容易把共同 beta 暴露误读成 basket 内部 alpha；
3. 还没完成一次 clean-room follow-up 去专门回答：
   - `equal-weight drift` 是否真的优于已有 pair/basket residual 壳；
   - `continuous rebalance` 是否比 flat-to-flat 更关键；
   - `2/3/5` 腿扩容是提升 alpha，还是只是提升共同 beta 暴露；
   - 去掉 BTC 计价口径后，alpha 是否仍保有独立增量。

因此这轮最诚实的 first verdict 不是 `P0`，也不是直接 `P2`，而是：

> `Rank 302` 值得保留到 `P1 survivor`，因为它已经形成了清楚独立的 `multi-leg basket rebalance` 主语；下一步只需要一次便宜但 decisive 的 clean-room follow-up，验证它究竟是独立 alpha 壳，还是仍会塌回一般 basket residual / pair family 的变体。

## 已写回 runtime 的变化

- 分配正式编号：`Rank 302`
- `Fresh intake slot`：更新为 `done`
- `Fresh intake latest_result`：`Rank 302 ... keep_P1`
- `Surviving candidate slot`：切换为 `Rank 302`
- `followup_budget_remaining`：设为 `1`
- `cycle_plan[1]`：写回本轮 result/status

## 给下一轮的唯一合法前进方向（供 bot2 排班时参考，不改当前调度）

若 bot2 继续前排推进 `Rank 302`，唯一高杠杆 follow-up 应是：

- 做一次 **clean-room 独立性检查**，而不是再补泛泛文献描述；
- 核心要回答的是：
  1. `equal-weight drift + threshold rebalance` 相对现有 pair/basket residual 线是否有独立增量；
  2. `2/3/5` 腿是否提供真实风险收益旋钮；
  3. `continuous rebalance` 是否是 alpha 本体，而不是可随意替换的 exit 细节；
  4. 去掉 BTC 计价/共同 beta 后是否仍站得住。

## 一句话结果

`Rank 302`：`cointegrated basket equal-weight drift × threshold rebalance` 已完成 fresh intake first verdict，判定为 `keep_P1`；其独立主语是“用 equal-weight drift 直接代理篮子内错价，并以 threshold rebalance 连续 harvest 相对强弱回补”，不是旧 pair spread / residual basket stat-arb 的简单多腿平移。