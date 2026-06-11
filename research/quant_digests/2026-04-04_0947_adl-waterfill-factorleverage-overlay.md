# 别把 ADL 只当交易所黑盒：这篇 2026 Columbia 论文更适合先落地的是「water-filling leverage equalization × factor-adjusted deleveraging」共享 overlay

- 时间：2026-04-04 09:47 UTC
- 类型：2026 arXiv 全文 HTML + Hyperliquid ADL 文档对照
- 主题类型：overlay
- 基础 alpha：**答不清它自身的独立 base alpha，所以不把它当 raw alpha**；更准确地说，它服务于 **perp carry、breakout / momentum、mean reversion、maker / spread capture** 这类短周期 raw alpha，作用是在强平瀑布或极端冲击时，决定**先砍谁、砍多少、按 gross leverage 还是 factor-adjusted leverage 去砍**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否（更适合作为共享 risk overlay / deleveraging policy）
- 主题标签：overlay/risk/leverage/adl/auto-deleveraging/perpetual-futures/cross-margin/factor-adjusted-leverage/water-filling/liquidation-cascade/sizing/veto/portfolio-risk/btc/eth/1m/3m/5m/15m/paper/public-docs
- 证据类型：论文证据 + 交易所公开规则文档

## 1. 这次看了什么
主材料是 **Steven Campbell, Natascha Hey, Ciamac C. Moallemi, Marcel Nutz (2026), _Risk-Based Auto-Deleveraging_**。先按这轮要求回答一句：

> **这篇东西的 base alpha 是什么？**
>
> **答：它不是独立 raw alpha。**
>
> 它真正值得 desk 拿走的，是一套**极端行情下的统一去杠杆 / 缩仓分配原则**：如果必须砍仓，不要再用“谁盈利多、谁看起来排队靠前”这种经验规则，而是优先把**最高风险 leverage** 压平；在 cross-margin 下，压的还不是 naive gross leverage，而是**factor-adjusted leverage**。

所以这篇 paper 的正确定位不是 alpha 本体，而是 **shared risk overlay**。

## 2. 核心结论
一句话版：

> **当系统被迫 ADL / 缩风险暴露时，最稳的做法不是按 PnL × leverage 之类启发式排队，而是按“谁的 post-ADL leverage 最高”去做 water-filling 式 leverage equalization；如果是 cross-margin 组合，还应改成 factor-adjusted leverage。**

最该记住的硬点：

1. **现实相关性不低**：论文指出，**约 95% 的 perpetual volume** 发生在采用 queue-based ADL 的交易所上；这不是边角机制，而是主流市场结构的一部分。
2. **极端行情不是假设题**：文中点到 **2026-01-30 单日约 $2.56B leveraged positions 被清算**，而 2025-10-10~11 多个 major venue 也触发了 ADL。
3. **单资产 isolated margin 下**：在 expected-loss 目标下，**唯一最优解**就是最小化系统内**最大 leverage**，最后会落成一个非常直观的 **water-filling / leverage-draining** 规则。
4. **CVaR 下**：water-filling 仍然最优，只是**不再唯一**；高于某个 leverage cutoff 的账户，先怎么砍都行，但最终必须把 leverage 压回 cutoff 以下。
5. **cross-margin 下**：**gross leverage 可能是错指标**。如果组合里有真实 hedge，按 gross leverage 生砍会误伤；论文给出的解析 benchmark 是 **single-factor 下对 factor-adjusted leverage 做 clipped water-filling**。

## 3. 为什么它和当前 desk 直接相关
这轮我没有再补第 N 条 entry alpha，而是补一个我们迟早要有、但目前研究池里还很缺的部件：

> **统一的极端行情去杠杆规则。**

原因很简单：最近两天我们已经连续 intake 了大量 raw alpha——pairs、carry、cross-sectional、microstructure、single-asset mean reversion 都在补——但这些线一旦实盘并行，真正会把组合打穿的，往往不是“信号方向错了一点”，而是：

- 瀑布时到底先关哪个 sleeve；
- hedge 组合要不要跟 gross notional 一起被一刀切；
- maker / carry / basis 这种低 edge 线在 stress 下是不是该优先让路；
- `1m / 3m` 的急剧波动里该不该立刻做 portfolio-level throttle。

所以它虽然不是 raw alpha，本质上却是在补**live component 拆解**。

## 3.5 策略拆解（必填）
- 方向属性：shared risk overlay / deleveraging policy
- 基础 alpha：**现有 perp raw alpha**（carry、breakout、mean reversion、maker / spread capture、pairs / relative value）
- regime：**强平瀑布、保险基金吃紧、liq cluster 连锁、组合 leverage 超阈值、cross-margin hedge 失效**
- filter / veto：当 risk budget 不足时，不是按主观优先级砍仓，而是按 **water-filling leverage equalization** 或 **factor-adjusted leverage** 自动缩减
- sizing / risk：把每个 sleeve/account 的 `notional / equity` 或 `factor-adjusted leverage` 作为主要状态量，触发时做 clipped deleveraging
- cost / execution：核心目标不是提升每笔收益，而是**降低尾部 shortfall、避免坏 debt、减少把好 hedge 错砍掉**

## 4. 论文真正给了什么可落地部件

### 4.1 单资产 isolated margin：先压平最高 leverage，而不是先找“最赚钱的人”
论文最有用的一点，不是“ADL 很重要”这种废话，而是把它写成了明确优化问题。

在单资产、isolated margin 设定下，若交易所要在总共 `Q` 的目标回补量里，决定每个账户该被买回多少 `x_i`，那么在 **expected loss** 目标下，最优规则等价于：

> **最小化系统里最大的 post-ADL leverage。**

最后得到的是一个非常实用的 threshold rule：

- 初始 leverage 高于阈值的账户，先被砍；
- 被砍到同一个 leverage threshold 为止；
- leverage 本来就在阈值以下的账户，不动。

换成人话：

> **不是排队砍完 A 再砍 B，而是把系统里最危险的几根杠杆杆子一起削平。**

这比常见 queue-based 逻辑更适合 desk 自己做 portfolio risk overlay，因为它天然更像一个**连续的 risk budget 分配器**，而不是僵硬的单列队。

### 4.2 为什么 paper 认为现行 queue-based ADL 规则不够好
论文直接点名了主流 perpetual venue 常用的 queue-based 方法：

- 典型优先级会把 **P&L × leverage** 一类指标拿来排序；
- Hyperliquid 文档给出的示例排序指标就是：`(mark_price / entry_price) * (notional_position / account_value)`。

但 paper 认为这种规则有几个结构性问题：

1. **Sybil resistance 不好**：拆成多个小账户，可能改变排队位置；
2. **path dependence**：分两次 ADL 和一次性 ADL，结果可能不同；
3. **wash-trade resistance 不好**：如果排序显式依赖 P&L，就可能被交易路径影响。

相反，paper 里的 minimax leverage / water-filling 规则在理论上具备：

- distribution-free
- wash-trade resistant
- Sybil resistant
- path-independent

对 desk 来说，最实际的含义不是“追求完美机制设计”，而是：

> **别让 risk overlay 被账户拆分、PnL 幻觉或分批触发顺序轻易绕开。**

### 4.3 cross-margin：别再迷信 gross leverage
这是这篇 paper 最值得我们 desk 拿走的第二部分。

一旦进入 multi-asset / cross-margin，真正风险就不再只是“谁 notional 大”。

举个 desk 语境里的直白例子：

- 一个 sleeve 是 `BTC breakout long`；
- 另一个 sleeve 是 `ETH/BTC relative-value short beta`；
- 看 gross notional，它们都很大；
- 但看对共同风险因子的净暴露，它们未必同样危险。

论文的关键判断是：

> **naive gross leverage 会误伤有真实 hedge 的组合。**

所以在 cross-margin 下，正确 benchmark 不是继续看 gross leverage，而是引入 asset-level shadow prices，再在 single dominant factor 情况下，回到一种 **factor-adjusted leverage 的 clipped water-filling**。

翻成人话：

> **真正该先砍的，不是名义仓位最大的腿，而是对共同风险因子最裸奔、最缺缓冲的腿。**

这对我们这种会把多条 `1m / 3m / 5m / 15m` 线一起挂在 perp book 上的 desk，意义比“再补一条 entry”更直接。

## 5. 和 `1m / 3m / 5m / 15m` 的关系怎么理解
这条东西**不是逐根方向信号**，所以不能伪装成 “1m 看多 / 5m 看空” 的 alpha。

更准确的映射是：

### `1m / 3m`
这是**紧急降档层**。

适合干的事：
- 连续大波动时，按每分钟更新的 leverage / factor-leverage 做快速 throttle；
- 先砍最危险的几条腿，而不是全盘等比例减仓；
- 对 maker / carry 这类低 edge 策略，优先降杠杆或直接停做。

### `5m / 15m`
这是**正常风控重平衡层**。

适合干的事：
- 每根 bar 或每 3 根 bar 重算 risk budget；
- 当组合 leverage 逼近阈值时，先对 factor-adjusted leverage 最高的 sleeves 做 clipped reduction；
- 保留对冲有效的 relative-value / pairs 线，不要被 gross notional 一刀切误伤。

所以它和 short-cycle desk 的关系不是“预测下一根涨跌”，而是：

> **决定极端行情里哪几条短周期 alpha 还能继续活着。**

## 6. 最小实验该怎么做
这轮我没有去做“公开价格快检”，因为这篇 paper 的 edge 不在公开行情本身，而在**账户层 / sleeve 层状态机**。只看公开 K 线，复现不出它真正要解决的问题。

更合理的最小实验口径应该是：

### 实验 A：先把 desk 的策略簿状态化
对当前并行运行或历史回测的每条 sleeve，按 `1m` 采样出：

- `notional`
- `equity / allocated capital`
- `gross leverage`
- `beta to BTC / ETH / market factor`
- `expected edge`（可粗用 rolling bps/trade 或 recent Sharpe proxy）

然后为每条 sleeve 构造两种风险刻画：
1. `gross_leverage = notional / equity`
2. `factor_adjusted_leverage = |beta_factor| * notional / equity`（第一版先用单因子近似即可）

### 实验 B：比较 3 套去杠杆规则
在同一批 stress 时刻上，对比：

1. **pro-rata 减仓**
2. **exchange-style queue**（按 PnL × leverage 或盈利优先的近似队列）
3. **water-filling / factor-adjusted water-filling**

### 实验 C：stress 事件口径
优先拿这几类窗口：
- 大额清算日
- `1m / 3m` realized vol 急升窗口
- funding / OI / liq cluster 共振窗口
- 我们自己历史上 MAE 最大的交易日

### 实验 D：看 4 个结果指标
至少先看：
- `tail shortfall`（尾部资金缺口）
- `forced-close turnover`
- `组合恢复到正常 risk budget 的耗时`
- `被误砍的 hedge 占比`

### 第一版通过条件
如果 overlay 能做到：
- **tail shortfall 降 20%+**，
- 同时 **forced-close turnover 不比 pro-rata 高太多**，
- 且 **hedged sleeves 被误砍比例显著下降**，

那它就值得进 live risk stack。

## 7. 我对这条材料的结论
### 7.1 值得 intake 吗？
**值得。**

虽然它不是 raw alpha，但它补的是一个现在越来越该认真拆的 live component：

> **极端行情下，组合该怎么有原则地缩仓。**

### 7.2 现在就能直接上 production 吗？
**不能直接照搬。**

原因也很明确：
1. 论文主要是**规范性 / 优化型结果**，不是一份历史 pnl 论文；
2. 它默认 ADL 价格和账户状态可被清楚观测，而我们 desk 的真实执行会更脏；
3. factor-adjusted leverage 要先选好因子、beta 估计窗和更新频率。

### 7.3 最准确的 desk 化定位
我会把它定位成：

> **高优先级 shared risk overlay 候选：先做 desk-level replay，验证它能不能在不明显伤害 gross edge 的前提下，降低强平 / 尾部 shortfall。**

## 8. 风险与保留意见
- 这是 **risk overlay**，不是 raw alpha；不要伪装成方向因子。
- 论文里的“公平执行价 / 已知账户状态”假设，在真实瀑布行情里会比纸面更脏。
- 若 beta 估计不稳，factor-adjusted leverage 也会变得不稳；第一版应保持单因子近似和简单更新频率，别一开始就过拟合。

## 9. 下一步怎么测
最值得立刻开的，不是更多文献阅读，而是一个很实在的 replay：

1. **挑 3 条 raw alpha**：
   - breakout / momentum
   - mean reversion / fade
   - carry / basis 或 maker
2. **给每条线补状态变量**：`notional / equity / beta / recent edge`。
3. **回放最近 20~30 个 stress 窗口**，比较：
   - 不减仓
   - pro-rata
   - gross leverage water-fill
   - factor-adjusted water-fill
4. **如果 factor-adjusted 版本只在 tails 改善、但对常态收益损害很小**，就可以继续往 live risk governor 走。

## 10. 来源
1. **Campbell, S., Hey, N., Moallemi, C. C., & Nutz, M. (2026). _Risk-Based Auto-Deleveraging_. arXiv / q-fin.RM.**
   - Authors / Year / Title / Venue：Steven Campbell, Natascha Hey, Ciamac C. Moallemi, Marcel Nutz / 2026 / *Risk-Based Auto-Deleveraging* / arXiv
   - DOI：`10.48550/arXiv.2603.15963`
   - Readable URL：`https://arxiv.org/abs/2603.15963`
   - HTML URL：`https://arxiv.org/html/2603.15963v1`
   - Repo URL：N/A
2. **Hyperliquid Docs — Auto-deleveraging.**
   - 类型：交易所公开规则文档
   - Readable URL：`https://hyperliquid.gitbook.io/hyperliquid-docs/trading/auto-deleveraging`
   - 关键信息：公开给出按 unrealized PnL 与 leverage 使用情况排序的 ADL 逻辑

## 11. 文件与页面
- Markdown：`research/quant_digests/2026-04-04_0947_adl-waterfill-factorleverage-overlay.md`
- 预计页面：`https://jp.jerrypsy.top/momentum/reading/quant_digests/2026-04-04_0947_adl-waterfill-factorleverage-overlay.html`
