# 别把 stablecoin depeg 只当新闻噪音：这篇 2025 JIMF 更该先落地的是「USDT depeg → jump-risk / cojump-risk size-down + veto」共享 overlay

- 时间：2026-03-29 14:58 UTC
- 类型：overlay
- 主题标签：overlay/shared-gate/regime/stablecoin/usdt/depeg/jump-risk/cojump/position-sizing/execution-veto/event-driven/crypto/btc/eth/alts/1m/3m/5m/15m/paper/public-data/cost
- 证据类型：2025 *Journal of International Money and Finance* 开放获取全文 PDF（作者仓库镜像可读）+ Crossref 元数据 + 本地全文抽取
- 主题类型：overlay
- 基础 alpha：无独立方向 alpha；它服务于多类 raw alpha 的 shared jump-risk / cojump-risk gate（尤其是 mean reversion、carry、pairs、breakout 追单）
- 是否可独立复现：是（公开 stablecoin 价格 + BTC/ETH/全市场 `1m/5m` 行情即可复现）
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否（更适合作为 shared regime / risk overlay，而不是 standalone 方向策略）

## 1. 这次看了什么

这次主看的是：

> **Baptiste Perez Riaza, Jean-Yves Gnabo (2025)**  
> **From depegs to jumps: The role of stablecoin instabilities in crypto market dynamics**  
> *Journal of International Money and Finance*  
> DOI: `10.1016/j.jimonfin.2025.103339`  
> Readable URL: <https://doi.org/10.1016/j.jimonfin.2025.103339>  
> OA PDF（作者仓库镜像）：<https://pure.unamur.be/ws/files/112887849/Perez_Riaza_and_Gnabo_2025_.pdf>  
> Repo URL：未见官方复现仓库

我这轮选它，不是想把 stablecoin 事件硬包装成“又一条逐根短周期方向 alpha”，而是因为它给了一个我们现有素材池里还没单独钉牢的、**非常实盘化的共享风险层**：

> **当 USDT 明确脱锚时，BTC 单币 jump risk 和全市场 cojump risk 会同时急剧上升。**

这不是一句宏观废话，而是可以直接写进 desk 风控/仓位管理/执行 admission 的东西。

## 2. 先回答用户要求的那句：这篇东西的 base alpha 是什么？

这篇东西如果硬要说“base alpha 是做多还是做空”，其实答不清。

原因很简单：论文证明得很强的是：

- **jump 更容易来**
- **cojump 更容易来**
- **jump 幅度更大**

但没有给出一个足够干净的、可直接单独交易的方向结论，比如：

- “USDT depeg 后固定做空 BTC”
- 或“USDT depeg 后固定做多波动且方向可知”

所以它不该被伪装成 raw alpha。

更诚实的 desk 分类应该是：

- **主题类型：overlay**
- **作用对象：多个 raw alpha 家族**
- **核心功能：jump-risk gate / cojump-risk gate / size-down / execution veto**

换句话说：

> **这篇东西的 base alpha 不是“方向”，而是“识别一个极不正常、极容易把普通 bar-based alpha 打坏的市场状态”。**

## 3. 论文里最值得 desk 拿走的不是解释，而是三组硬结果

论文用的是：

- **5 分钟频率**数据
- **2022-01-01 到 2023-06-30**
- 样本为 **70 个非 stablecoin crypto-assets + 1 个 stablecoin（USDT）**
- 价格、成交额、市值来自 **CoinPaprika**
- depeg 检测默认阈值：**偏离 `$1` 达到 `0.5%`**

最值得记的不是“stablecoin 很重要”，而是下面这几组可直接 desk 化的数字。

### 3.1 USDT 脱锚后，BTC jump probability 不是小幅抬升，而是陡升

按论文 Table 6(b)：

- **post-event 5m**：
  - `P(jump | USDT depeg) = 26.16%`
  - `P(jump | control) = 0.73%`
  - **概率比 = 35.94x**
- **post-event 15m**：
  - `34.18% vs 2.18%`
  - **15.65x**
- **post-event 1h**：
  - `50.63% vs 8.73%`
  - **5.80x**

这说明什么？

> **USDT depeg 不是“消息吓一跳然后算了”，而是会把 BTC 拉进一个接下来 5m~60m 都明显更容易出现跳变的 regime。**

### 3.2 这不是只影响 BTC 单腿，还是 market-wide cojump risk

按 Table 7(b)：

- **post-event 5m**：
  - `P(cojump | event) = 18.57%`
  - `P(cojump | control) = 0.48%`
  - **39.07x**
- **post-event 15m**：
  - `23.63% vs 1.43%`
  - **16.57x**
- **post-event 1h**：
  - `33.76% vs 5.70%`
  - **5.92x**

这比“单币波动放大”更重要，因为它意味着：

- pairs / stat-arb 的 spread 关系可能一起断
- 横截面 market-neutral 的相关性和 beta 映射会突然漂
- carry / basis 的 rebalance 可能在最差时点成交
- mean reversion 会在“本来该回”的地方继续被强制拉穿

### 3.3 下行 depeg 更危险，不只是更频繁，而是更暴力

论文把 depeg 方向拆开后，发现 **downward depeg** 更值得 desk 紧张。

按 Table 11：

- **USDT downward depeg 后 5m BTC jump 概率**：
  - `40.00% vs 0.73%`
  - **54.87x**
- **1h BTC jump 概率**：
  - `65.00% vs 8.75%`
  - **7.43x**
- **1h market cojump 概率**：
  - `42.50% vs 5.71%`
  - **7.44x**

也就是说：

> **若是“往下脱锚”的 USDT shock，别再把它当普通噪音；它更像是全市场 jump regime 的强触发器。**

### 3.4 跳不是只更多，而且更大

按 Table 8：

- **正向 BTC jump 均值（post-event 1h）**：`0.890%`
- **控制组正向 jump 均值**：`0.578%`
- **负向 BTC jump 均值（post-event 1h）**：`-0.936%`
- **控制组负向 jump 均值**：`-0.534%`

论文还指出：

- depeg 后的 jump 分布与控制组显著不同（Wilcoxon 1% 显著）
- **negative depeg** 后的 jump 平均更大

这对 desk 的含义非常直接：

> **不是“波动略高一点”，而是尾部/滑点/止损穿透/相关性失真都更容易一起出来。**

## 4. 为什么这一轮值得写一个非 raw alpha 主题

先把这个问题正面回答掉。

当前 desk 的 raw alpha 素材池已经不算薄：

- trend / momentum
- mean reversion
- cross-sectional / relative value
- pairs / stat-arb
- carry / funding / basis
- event-driven
- order-flow / microstructure

反而更稀缺的是：

> **一个能同时服务这几类 alpha 的、公开可得、分钟级可复现、而且确实有论文证据支撑的 shared stress gate。**

USDT depeg 这一层正好满足：

1. **公开可得**：stablecoin 价格公开
2. **分钟级可做**：`1m / 5m` 就能落地
3. **跨策略共享**：不是只服务一种 setup
4. **不伪装成 alpha 本体**：定位诚实

所以这轮虽然不是 raw alpha，但它不是“泛泛解释型主题”，而是：

> **一个直接服务现有 raw alpha 池的 shared jump-risk overlay。**

## 5. 真正 desk 化之后，它该怎么用

最核心的一句：

> **depeg shock 出现后，不是默认去猜你该做多还是做空，而是先承认市场进入了“跳跃风险显著升高”的异常区间。**

所以它最适合的落法，不是 standalone directional book，而是下面这几类共享动作。

### 5.1 对 mean reversion / pairs / stat-arb：先 veto

这类策略最怕两件事：

- spread 暂时不再均值回归，而是结构性扩张
- 多腿一起被 jump 和 cojump 冲穿，导致 hedge ratio 短时失效

所以第一版 overlay 应该非常直接：

- **depeg 触发后前 15m~30m：禁止开新 MR / pairs / spread fade**
- 已持仓只允许减仓，不做逆势加码
- 所有基于 rolling z-score 的加仓阈值上调

### 5.2 对 carry / basis / funding：先 size-down，再限制 rebalance

carry 书最容易在 depeg shock 下犯的错，不是方向错，而是：

- 在高冲击时段做不必要 rebalance
- 在高滑点时点被动补 hedge
- 误把 temporary dislocation 当“又便宜了”

所以更合理的是：

- **新开 carry notional 砍到平时的 `25%~50%`**
- shock 后 `30m~60m` 禁止 taker 追单式 rebalance
- 只有当 basis / premium 回到正常带宽时才恢复常规 sizing

### 5.3 对 breakout / continuation / event alpha：不是 veto，而是 mode switch

这类策略和前两类不同。

depeg regime 下：

- continuation 可能更强
- 但 jump risk / slip risk 也更高

所以更合理的不是一刀切禁止，而是：

- 仅允许**同向 already-moving** 的事件单继续参与
- 初始仓位降到 `0.33x ~ 0.5x`
- 放弃 maker 幻觉，直接用更保守的冲击成本假设
- 持有期更短，避免从事件 alpha 退化成噪音扛单

也就是说，对 breakout/momentum 家族，它更像：

- **admission tightening + size-down**
- 而不是完全 veto

## 6. 最小可复现实验怎么做

### 6.1 数据源与公开性

论文原始口径：

- **CoinPaprika 5m 价格 / 市值 / 24h volume**
- 公开可取

desk 最小实验可先用更容易落地的公开数据代理：

1. **主方案**：CoinPaprika / CoinGecko / 其他公开 stablecoin USD 价格序列
2. **交易所代理方案**：Binance spot 的 `USDCUSDT` / `USDTFDUSD` / `FDUSDUSDT` 等稳定币对
3. **市场响应**：Binance perp 或 spot 的 `BTCUSDT`, `ETHUSDT`, top-alt universe

更新频率：

- **1m 或 5m 即可**

### 6.2 depeg 事件定义

先别自由发挥，第一版直接抄论文骨架：

- 当 stablecoin 价格偏离 `$1` 超过 **`0.5%`**，记为候选事件
- 必须**连续至少 2 个 5m 观测**都在阈值外
- 若新事件距离前一个事件 **< 20m**，并入同一 shock
- 先把正负 depeg 合并；第二轮再拆方向

若你没有直接的 `USDT/USD`，可以用：

- `USDCUSDT` / `USDTFDUSD` 作为 peg proxy
- 再加一个“另一个稳定币本身没一起坏掉”的 sanity check

### 6.3 第一轮不要测 standalone alpha，先测 overlay value

最小实验建议直接做三个 A/B：

#### A. MR / pairs veto test

- 样本：现有 `5m / 15m` MR / pairs 信号
- 对照：正常执行
- 实验：若 depeg shock 触发，则 **未来 30m 禁止开新仓**
- 评估：
  - hit rate
  - avg trade PnL
  - max adverse excursion
  - slip proxy / tail loss

#### B. Carry / basis size-down test

- 样本：现有 funding / basis / carry 策略
- 实验：shock 后 `60m` 内新仓 notional 降到 `25%~50%`
- 评估：
  - gross alpha 保留率
  - max drawdown 改善
  - extreme slippage trades 减少幅度

#### C. Momentum admission test

- 样本：breakout / continuation / event-driven 单
- 实验：仅保留 **shock 后与首个 `1m/3m` impulse 同向** 的单
- 同时 `size=0.5x`，固定更严成本
- 评估：
  - 毛 alpha 是否还在
  - cost-adjusted expectancy
  - holding `5m/15m/30m` 哪个最稳

## 7. 对 `1m / 3m / 5m / 15m` 的关系

这篇东西和当前 desk 时间尺度是天然兼容的：

- **`5m` 是最自然的复现层**：论文原文就是 `5m` 数据
- **`15m` 适合做策略层 veto / size-down**：足够稳，不会被单根噪音主导
- **`1m / 3m` 更适合作为 execution / impulse confirmation 层**：
  - 看 depeg 触发后首个方向冲击
  - 决定是完全禁做，还是只保留同向 event 单

所以它不是那种“论文是日频，硬往分钟上拽”的东西；它本来就站在短周期。

## 8. 下一步怎么测

必须落到具体，不然这篇东西只会停在“很有道理”。

### 下一步 1：先做 shared gate，而不是造新方向策略

优先级最高的是：

- 给现有策略回放一层 `depeg_shock_flag`
- 看 **veto / size-down 能否显著改善 tail loss**

这是最短路径，也是最贴近实盘价值的路径。

### 下一步 2：只在第二阶段，才尝试从 overlay 往 raw alpha 分支挖

如果一定要从这篇东西里再往前挖一层 raw alpha，我只建议测一个非常克制的分支：

> **downward USDT depeg + BTC 首个 `1m/3m` impulse 同向 → 跟随 5m~15m**

也就是：

- 不直接“见 depeg 就空”
- 先让价格自己表态
- 再把 depeg 当成高 jump-risk / 高 continuation-risk 的 regime confirmation

这是从 overlay 往 raw alpha 走的最合理分支，但应该排在 shared gate 验证之后。

### 下一步 3：参数网格只保留最小集合

别上来就把自由度开爆。

第一轮只测：

- depeg threshold：`0.3% / 0.5% / 1.0%`
- overlay hold：`15m / 30m / 60m`
- direction split：`all / downward-only`
- universe：`BTC, ETH, top 10 perp`

只要这四维先给出清晰答案，就足够决定它值不值得进 production risk layer。

## 9. 一句话结论

这篇 2025 JIMF 不该被写成“stablecoin 脱锚会影响市场”这种空话。

它真正值得 desk 拿走的是：

> **USDT 明确脱锚后，未来 `5m~60m` 的 jump / cojump 风险显著升高；这更适合写成所有短周期 alpha 共用的 size-down + veto overlay，而不是伪装成一个独立方向策略。**

如果只做一个最小实验，我建议先做：

> **把 `downward USDT depeg` 写成 `30m/60m` shared risk flag，回放到现有 MR / pairs / carry / breakout 书上，看 tail loss 能不能明显下降。**
