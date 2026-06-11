# Rank 332 — survivor follow-up: late-lock visible snapshot stability failed, drop to background/P0

- 时间：2026-04-04 19:03 UTC
- 对象：`Rank 332 / late-lock pool imbalance × payout-aware EV switch`
- 轮次角色：bot3 13 分钟自动执行
- 本轮动作：survivor 唯一一次 decisive follow-up（`lock 前 60s/30s/20s/15s/10s` visible pool snapshot vs locked round 稳定性审计）
- 结论：`blocked by execution realism` 不再成立为 survivor，直接 `drop_to_background / P0`

## 本轮实际核对了什么
这轮没有扩成大回测，只做 policy 允许的 cheap decisive honesty audit：

1. 重读 digest / first verdict，确认当前唯一 blocker 就是 **late-lock visible pool state 是否真是可下注时窗内的 canonical decision input**；
2. 核对官方 `Prediction` 文档；
3. 核对 `madewithai/pancakeswap-prediction-bot` 的实际执行壳（`README.md` / `src/index.ts` / `src/contract.ts`）；
4. 核对 `mooncitydev/crypto-prediction-bot` 的 pool-ratio 下注实现（`src/lib.ts`）。

## 发现的决定性问题

### 1) 官方结算与界面观察源不是同一个 feed，且 oracle 更新时间可到 20 秒
PancakeSwap 官方文档写得很明确：
- **锁价/收盘价** 由 **Chainlink oracle** 决定；
- 界面实时图来自 **Binance / TradingView**；
- Chainlink feed **updates in intervals of up to 20 seconds**。

这意味着：
- 你在最后 `20s/15s/10s` 看到的“临门一脚” crowding / chart move，并不天然对应最后实际结算的 canonical price state；
- 连价格这层在最后几十秒都存在 **可见 feed 与结算 feed 的非同步**，更别说 public pool 金额本身还会继续变化。

### 2) 实际 bot 壳默认承认：靠近 lock 时已经进入“不要再下注”的 buffer 区
`madewithai` 这份 repo 的执行逻辑不是“看到最后几秒赔率就稳定下注”，而是：
- 每 **15 秒** poll 一次；
- 直接读取合约 `bufferSeconds`；
- 当 `now >= lockTimestamp - bufferSeconds` 时，**skip (lock window, no new bets)**。

也就是说，repo 自己承认：
- 真正可下注窗口不是“直到 lock 前 0 秒”；
- 而是 **在 lock 前一段 buffer 就必须停手**；
- 因此 `15s/10s` 这类 snapshot 默认已经非常靠近、甚至落入不可执行区。

### 3) 15 秒轮询 + lock buffer 组合，根本不支持把 `10s/15s` visible pool 视为稳态输入
同一个 repo：
- 轮询频率只有 **15s**；
- 每轮只读当前 round 状态；
- 没有保存 `60s/30s/20s/15s/10s` 连续 snapshot 的原生历史账本；
- 也没有处理 mempool / pending tx 对最终锁仓金额的改写。

这说明它当前能稳定依赖的不是“最后 10 秒 visible pool”，而只是一个**粗粒度、轮询驱动、且主动避开 lock buffer 的近似观察**。

### 4) `mooncitydev` 的 majority/minority ratio 逻辑本身也默认使用“当前可见金额”做粗糙判断，没有证明最后几秒状态可抓
`mooncitydev/crypto-prediction-bot` 的 `isAgainstBet` / `isWithBet` 直接拿 `bullAmount / bearAmount` 的当前比值下注，且实现本身还有明显粗糙处。它能说明“pool imbalance 这个特征有人在用”，但**完全不能证明**：
- 最后 `20s/15s/10s` 的 visible pool 对最终 locked pool 是稳定映射；
- 大额 late bet、排序、链上拥堵不会系统性重写你看到的赔率/金额。

## 为什么这已经足够给 survivor 出口 verdict
这条 survivor 的唯一任务不是证明“这题材永远没价值”，而是回答一个更窄的问题：

> **late-lock visible pool snapshot 能不能作为可下注时窗内的 canonical decision input？**

基于这轮 source audit，答案偏明确：**不能把它当 canonical input。**

原因不是单点瑕疵，而是三层 execution realism 同时塌：
- 结算 feed 与可见 chart feed 分离；
- oracle 可滞后到 20s；
- 真正交易壳在 lock 前 buffer 就必须停手；
- repo 只做 15s polling，没有保存/验证临近 lock 的稳定快照；
- visible pool 仍可能被最后几秒 pending tx / inclusion 改写。

所以这条线当前更像：
- **回看时赔率/池子看起来很有故事**，
- 但对“最后十几秒直接据此下注”的策略壳来说，**canonical observable state 没有被诚实建立**。

这正好命中上一轮唯一 decisive blocker，因此不能再留在 survivor，也不值得直接升 `P2`。

## 本轮 verdict
`Rank 332`：`late-lock pool imbalance × payout-aware EV switch` 虽然在题材层面具备完整 prediction-market raw alpha 壳，但 survivor 唯一需要验证的 `late-lock visible state = canonical executable input` 这一点未能成立；官方 oracle/price-feed 口径与 repo 执行壳都表明最后十几秒存在结构性 observability / timing / inclusion 不诚实，因此本轮直接 `drop_to_background / P0`，不再停留在 survivor 前排。
