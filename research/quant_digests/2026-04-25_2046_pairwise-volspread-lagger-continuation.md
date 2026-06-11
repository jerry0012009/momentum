# 别把这个 2026 Hyperliquid 仓只读成“作者秀收益”：对 short-cycle crypto desk，更该先拆的是「leader 波动冲击 × lagger 方向跟随」这条 1m raw alpha

- 时间：2026-04-25 20:46 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `bot.py`）
- 主题类型：raw alpha
- 基础 alpha：**当预先排好的 leader/lagger 对中，leader 在 1m 上先出现足够大的波动/收益冲击时，lagger 在下一小段时间更容易沿同方向跟随**；可先写成 `sign(ret_leader_1m) * 1[abs(ret_leader_1m) > k * rv_leader]`，交易 lagger。
- 是否可独立复现：否
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha/lead-lag/cross-asset/relative-value/vol-spread/continuation/1m/3m/5m/15m/repo/cost/risk
- 证据类型：工程经验

**先回答 base alpha 是什么：** 不是“lead-lag 这个大词”，而是很具体的一条 `raw alpha`：**同一批活跃 perp 里，先动的 leader 若在 1m 上打出足够大的波动冲击，后动的 lagger 会有一小段方向跟随窗口。**

## 1. 为什么这条线值得单独拎出来

今天已经写过不少 `funding / basis / xs reversal / pairs z-score fade`。这个 2026 仓 `mateofrqt/Crypto-LeadLag-Strategy` 真正有补充价值的，不是作者的 daily L/S 或 15m directional，而是 README 里那条 **Pairwise Vol-Spread — 1-Minute**：

- 预先离线排好 `leader/lagger` 对；
- 每根 `1m` bar 先看 leader 是否出现足够大的波动/收益事件；
- 若满足条件，就在 **lagger** 上顺着 leader 的方向开仓；
- 用固定风险规则退出，而不是无限追。

翻成人话：
- 不是赌“价差回归”；
- 也不是做“横截面赢家轮动”；
- 而是赌 **信息扩散有时不是同时完成的**，先被打穿的那条腿会把冲击传给后面的那条腿。

这对我们 desk 有价值，因为它能补一条与 `pairs mean reversion` 完全不同的分支：**relative-value 也可以做 continuation，而不只做 fade。**

## 2. 我实际读到了什么

### Repo
- **Author / Year / Title**: `mateofrqt` / 2026 / *Crypto-LeadLag-Strategy*
- **Venue**: GitHub repository
- **DOI**: N/A
- **Readable URL**: <https://github.com/mateofrqt/Crypto-LeadLag-Strategy>
- **Repo URL**: <https://github.com/mateofrqt/Crypto-LeadLag-Strategy>

### 本轮审计文件
- `README.md`
- `bot.py`

### 和本主题最相关的硬信息
1. README 明确把第二套策略写成：
   - **Pairwise Vol-Spread (Intraday)**
   - **Timeframe: 1m**
   - **Universe: scheduled leader/lagger pairs**
   - **Style: pairwise statistical arbitrage / trend continuation**
2. README 给出 walk-forward 结果（**费用按 round-trip 0.09% 建模**）：
   - In-sample：`28` 笔，`+2.48%`
   - Short OOS：`24` 笔，**`+14.54%`**，最大回撤 **`-0.81%`**
   - Long OOS：`398` 笔，`-27.7%`，最大回撤 `-35.4%`
3. README 自己就承认：
   - 长 OOS 退化很明显；
   - **pair schedule 需要定期重拟合**，否则 edge 会掉。
4. `bot.py` 里能看到 live 壳的一些风险约束：
   - `min_leader_move = 0.0005`（至少 `0.05%` leader move 才动）
   - `rebalance_threshold = 0.30`
   - 有 budget filter、vol scalar、drawdown circuit breaker、position close / flip 流程

最重要的一点是：**repo 没公开核心 signal construction 与 pair-schedule 参数**。所以它不是“拿来就能一键复现”的公开 alpha；但它把 base alpha 壳说清楚了。

## 3. desk 化拆解

## 3.5 策略拆解（必填）
- 方向属性：相对价值 + continuation
- 基础 alpha：leader 的 1m 冲击先发生，lagger 的 1m~3m 跟随后发生
- regime：适合高联动、信息传导快、同主题币同步性强的时段
- filter / veto：只做预先筛好的高耦合 pair；leader move 不够大不做；极端高波动或流动性塌陷时不做
- risk / sizing / execution overlay：固定风险退出、pair schedule 定期重拟合、budget cap、drawdown circuit breaker、成本前置建模

对我们更重要的读法不是照抄作者结果，而是把它翻成一个**最小可测壳**：

> `leader event` 触发后，`lagger` 在未来 `1~3` 根 bar 的 sign / markout，是否比随机同方向追单更好？

## 4. 可复刻的最小实验

### 最小实验 A：先不碰作者 proprietary schedule，只做公开版
- **资产**：`BTC/ETH/SOL/BNB/XRP/DOGE/ADA/AVAX/LINK/OP/ARB`
- **周期**：主测 `1m`，辅测 `3m`
- **pair 生成**：滚动 `5d~10d` 计算 `leader→lagger` 的 lagged corr / lead-lag hit-rate，只保留前 `N` 个 pair
- **事件定义**：
  - `ret_leader_1m`
  - `rv_leader = std(ret_1m, 60)`
  - 当 `abs(ret_leader_1m) > k * rv_leader` 时触发，`k` 先扫 `1.5 / 2.0 / 2.5`
- **交易**：
  - 若 leader 上涨，则做多 lagger；leader 下跌则做空 lagger
  - 在 lagger 上持有 `1 / 2 / 3` 根 `1m` bar，或 `1` 根 `3m` bar
- **先看指标**：
  1. event-conditioned forward return / hit-rate
  2. 扣 `4~6 bps` one-way 后是否仍为正

### 最小实验 B：只测“冲击强度是否单调”
- 按 leader event 的 z-score 分层：`1.5~2 / 2~2.5 / >2.5`
- 看 lagger 的未来 `1m/3m` markout 是否单调上升
- 若不单调，这条线大概率只是噪声或 news chase

### 最小实验 C：把 15m 当 regime gate，不把它伪装成 1m 主信号
- 只有当 pair 在 `15m` 上同向 trend / 同主题 beta 扩散期，才允许 1m 事件触发
- 这能直接回答：**短周期 alpha 本体在 1m，15m 只是 gate，还是它根本离不开高一级 regime。**

## 5. 风险与保留意见

1. **不是 fully reproducible public alpha**
   - README 明说信号构造和参数未公开；
   - 所以当前更适合当 `raw alpha intake`，不是直接升格成 replication-ready 策略。

2. **长 OOS 退化是很重的警告**
   - `24` 笔短 OOS 的漂亮结果，不足以盖过 `398` 笔长 OOS 的明显失效；
   - 更合理的解释是：**pair schedule / 事件阈值是强时变对象**。

3. **它最怕两种环境**
   - 全市场同步乱跳，谁也不是 leader，只是一起噪声放大；
   - 低流动性币被单笔打穿，表面像 leader，实则只是局部冲击。

4. **成本门槛可能比看上去更高**
   - README 已经把 round-trip fee 设到 `0.09%`；
   - 若我们在公开市场上拿不到更好的 maker/queue edge，很多 1m 跟随 edge 会被直接吃掉。

## 6. 一句话结论

**这份仓最值得 desk 留样的，不是作者展示的收益曲线，而是那条很清楚的 1m raw alpha 壳：`leader 波动冲击先发生 -> lagger 有短暂方向跟随窗口`。**

**一句话证明方式：** 公开 README 给了 walk-forward OOS 结果和明确的交易壳，虽然没公开核心参数，但已经足够支撑我们做一个自己的最小事件研究版。

## 7. 下一步怎么测

先不要复刻作者整套 live infra；直接做一个 **event study + friction ladder**：
- `1m` 上先测 leader event 触发后的 lagger `1/2/3` bar markout；
- 再加 `15m` regime gate；
- 最后才决定要不要上 pair scheduler、仓位分配和多 pair 组合。

如果 event study 本身不过线，就别被 repo 的架子和 live 标签带偏。

## 8. 来源
- `mateofrqt`. (2026). *Crypto-LeadLag-Strategy*. GitHub repository.
- Readable URL / Repo URL: <https://github.com/mateofrqt/Crypto-LeadLag-Strategy>
- 审计文件：`README.md`, `bot.py`
