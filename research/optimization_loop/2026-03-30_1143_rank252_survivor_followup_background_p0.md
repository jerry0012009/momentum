# Rank 252 survivor follow-up — public proxy 下无诚实可保留的 maker/taker executable pocket，回 background/P0

- 时间：2026-03-30 11:43 UTC
- 对象：Rank 252 / order-flow imbalance × fill-aware maker/taker routing
- 本轮动作：作为当前唯一合法 survivor 的唯一一次 follow-up，只回答公开 `bookTicker + aggTrades` 代理下压成 `L1 OFI + spread hurdle + sign-flip exit` 后，`1m/3m` 上按 `maker/taker` 分层是否还剩成本后稳定为正的 executable pocket
- 本轮 verdict：**唯一 follow-up 用完，回 `background/P0`**

## 结论先说
这轮真正改变系统认知的点不是“OFI 完全没信息”，而是更窄的一句：

> **一旦把对象诚实压到公开 `bookTicker + aggTrades` 代理，`maker/taker split` 里最值钱的 maker 那条腿就失去可验证 fill truth，只剩 taker/quote-mid 幻觉二选一；因此这条线不再保有独立于既有 `single-asset OFI taker` 家族的 executable pocket，不够升 `P2`。**

也就是说，失败点不在 `OFI` 三个字，而在这条卡最核心的新边界——**fill-aware maker/taker routing**——没法在当前公开代理里被诚实保留下来。

## 这轮为什么可以直接收口，而不是再拖
上一轮 intake 已经把 blocker 锁得很窄：
- 不是再问 `OFI` 有没有方向性；
- 也不是再问 repo OOS 数字漂不漂亮；
- 而是只问：**公开代理下，maker/taker 分层后是否还能留下 after-cost executable pocket。**

这一步现在已经可以直接回答：**不能诚实回答“能”。** 理由有三层。

## 1) public `bookTicker + aggTrades` 只能给到 L1 quote 和已成交 tape，给不了 maker fill truth
这条对象和旧 `OFI + VWAP pressure taker` 家族的真正区别，原本就在于：
- 先算 `alpha_bps`
- 再比较 `maker_edge`
- 再用 `QI`/queue proxy 判断自己是否值得挂 maker
- 最后让 `maker or taker` 成为同一 admission state machine 的一部分

但公开代理下能拿到的只有：
- `bookTicker`：best bid/ask 与 top-of-book size
- `aggTrades`：已成交流方向与成交量

拿不到的恰恰是 maker 这条腿最关键的 truth：
- 我方真实挂单队列位置
- 我方订单相对 queue 的先后
- 是否被同价位更早挂单挡住
- cancel/replace 后 queue 重置的损失
- partial fill path
- adverse selection 下“看似会成交，实际只在最差时点成交”的条件分布

因此 public proxy 最多只能给一个 **fill fantasy proxy**，而不是 executable truth。

## 2) 一旦把 fill fantasy 拿掉，maker/taker split 就退化成旧家族；保留下来的不是 Rank 252 这张卡
如果继续硬做，会出现两种不诚实路径：

### 路径 A：把 maker 假定成“看到触价/有成交就算我能成交”
这会把关键 alpha 夸大，因为：
- 触价 ≠ 我能排到；
- 有别人成交 ≠ 我以同价优先成交；
- 最容易成交的时刻往往也是 adverse selection 最强的时刻。

这不是小误差，而是直接决定 `maker_edge > 0` 是否成立的核心口径错误。

### 路径 B：为避免 fill 幻觉，干脆只保留 taker
这样虽然更诚实，但对象主语也跟着塌了：
- 剩下的是 `L1 OFI + spread/cost hurdle + sign-flip exit` 的 taker directional alpha；
- 这已经非常接近我们现有的 `single-asset OFI + VWAP pressure taker` / 其他 public microstructure follow-through 家族；
- 新对象最该回答的 `fill-aware maker/taker split` 边界反而不见了。

换句话说，**如果为了诚实而删掉 maker，那 surviving 的不再是 Rank 252 这张卡；如果保留 maker，又只能靠不可验证 fill 想象。** 这就足以把 survivor 收口为不进入 `P2`。

## 3) 当前公开代理还会把 1m/3m 持有与 30s drift 主语进一步错配
repo 的 base alpha 是 `lagged OFI z-score -> future 30s drift`。当前 follow-up 虽然允许压到 `1m/3m`，但这本来就是一种 desk-friendly 降采样近似。若再叠加：
- L2 -> L1 的信息降级
- queue truth -> fill proxy 的信息降级
- maker/taker 联合决策 -> 事后粗分层 的信息降级

那么最后剩下的“正 pocket”即便看起来存在，也很难说还是这张卡本来的对象边界，而不是一个更弱的、已被其他近邻覆盖的 public taker continuation 变体。

因此，本轮最诚实的答案不是“公共版一定全无 alpha”，而是：

> **公共版不足以保住 Rank 252 最值钱的独立对象边界；而若只保留可诚实执行的部分，又退化成旧 family，不能作为新的 P2 admission 对象继续占前排。**

## 为什么不是 `promote_P2`
升 `P2` 的前提，不是“主题听起来对”，而是要保住一个**独立、诚实、可继续 admission 的对象主语**。

Rank 252 这张卡真正的 admission 主语是：
- `lagged OFI z-score`
- `cost-aware gating`
- `fill-aware maker/taker split`

这轮 follow-up 已经证明：
- 在公开 proxy 下，第三条没法被诚实保留；
- 把第三条删掉后，对象边界会坍塌回旧 taker/microstructure 家族；
- 所以当前没有必要把它升成 `P2` 再继续做 effectiveness / stability / honesty admission。

## 为什么也不是 `keep_P1`
policy 已经明确：survivor 只有这一次 follow-up 预算。

这一步又恰好打在上一轮唯一 blocker 上，并且已经给出 decisive 结果：
- blocker 不是“还没来得及测”；
- 而是“当前允许的公开代理口径无法诚实回答对象最核心的新边界”。

所以再继续留在前排，只会变成：
- 要么重复同一个 honesty blocker；
- 要么偷偷把题目改成纯 taker OFI；
- 要么默认等更贵的 L2/Tardis 数据来救。

这三种都不符合当前 policy 的最小诚实收口原则。

## 本轮写回 runtime 的一句话
`Rank 252 / order-flow imbalance × fill-aware maker/taker routing` 的唯一 survivor follow-up 已完成：一旦把对象诚实压到公开 `bookTicker + aggTrades` 代理，`maker/taker split` 中最关键的 maker 腿就失去可验证 fill truth，若保留则落入 fill 幻觉、若删掉则退化成既有 OFI taker 家族，因此当前公开版不保有独立、成本后可审计的 executable pocket，本轮不升 `P2`，直接回 `background/P0`。
