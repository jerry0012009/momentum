# multi-spread conflict routing × no-idle-capital 首判：不进入前排，回 background/P0

- 时间：2026-03-30 13:51 UTC
- 对象：`multi-spread conflict routing × no-idle-capital`
- 来源：`research/quant_digests/2026-03-30_1133_multiquote-conflict-routing-raw-alpha.md`
- 类型：fresh intake 首判

## 本轮只回答一个问题
`same-underlier multiquote mispricing convergence + conflict routing + quote-budget allocator` 是否已经形成一个**独立于既有 same-asset multi-quote spread 家族**的新前排对象，而不是把已有 pair spread mean reversion 再包一层 allocator 叙事。

## 结论
本轮结论是否定的：**不进入前排，回 background/P0。**

## 为什么这轮不保留成新的 fresh intake 对象
1. **alpha 本体没有变，还是同币多报价 spread 回归。**
   这篇 digest 自己也明确写了 base alpha 是 `same-underlier 多报价之间的相对错价回归`。真正新增的是“多条 spread 同时亮灯时怎么路由资金”，但这属于执行/分配层，不是新的 raw alpha 主体。

2. **公开快检证明了“有冲突要分配”，但还没证明 allocator 本身形成独立可单轮证伪的 alpha。**
   digest 给出的核心最小证据是：
   - `ETHUSDT/ETHUSDC/ETHFDUSD` 上 pair-level gross convergence 仍存在；
   - `5m` 最近 `1000` 根里有 `37` 根 bar 同时出现 `>=2` 条 pair 信号；
   - 因而 `conflict routing + no-idle-capital` 在工程上值得做。
   这说明**多信号冲突是真问题**，但还没有给出一个能把对象从 `Rank 196` 那类 same-asset multi-quote spread 家族里分离出来的 first-pass verdict：比如 allocator-only 相比 pair-by-pair baseline 的净增益、冲突净掉后减少的重复占用是否足以改变成本后 verdict、或者 quote-budget 约束是否能单独改变层级。

3. **与既有前案的边界仍然塌回 `Rank 196` 家族。**
   `Rank 196` 已经把同币多报价 spread mean reversion 的对象边界锁定为：
   - 同一底层币种；
   - 多个稳定币报价交易对；
   - rolling spread z-score 极端偏离后做均值回归；
   - 可再看 `|z|` 分层 sizing。
   这轮所谓新增的 `multivariate allocator / routing`，更像是这条家族未来若进入 replication 时要补的**组合执行层**，而不是值得单独占一个 fresh intake 槽位的新对象。

## 本轮对系统认知的改变
`multi-spread conflict routing × no-idle-capital` 说明 same-underlier 多报价家族未来需要补 conflict audit / allocator realism，但它**不是独立 raw alpha**；当前最诚实的归位方式是作为 `Rank 196` 家族的后续实现层参考，**不单列新 rank、不进入前排、直接回 background/P0**。

## 写回 runtime 的一句话
`multi-spread conflict routing × no-idle-capital` 这条 fresh intake 虽然把 `ETHUSDT/ETHUSDC/ETHFDUSD` 的多信号冲突与 quote-budget 占用问题说清楚了，但 alpha 本体仍是既有 same-asset multi-quote spread 回归，新增部分主要是 allocator/routing 执行层，尚不足以形成独立前排对象，因此本轮 `不进入前排，回 background/P0`。

## 本轮 verdict
- fresh intake：`不进入前排，回 background/P0`
- rank：`不分配新 Rank`
- 原因：`独立对象边界不足，增量主要是 allocator/routing 包装层，不是新的 raw alpha 主体`
