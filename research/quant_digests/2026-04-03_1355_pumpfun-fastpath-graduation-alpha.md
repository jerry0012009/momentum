# 别把这篇 2026 Pump.fun 论文只读成“毕业概率说明书”：对 short-cycle desk，更该先测的是「同一 `vSOL` 下的快路径 launch alpha」
- 时间：2026-04-03 13:55 UTC
- 类型：论文 / 公开链上数据
- 主题类型：raw alpha
- 基础 alpha：**同一条 Pump.fun bonding curve 上，若新币在早期以更少成交笔数、更低 bot 占比、更健康的参与者结构快速累积 `vSOL`，其后续“继续吸引资金并冲向 graduation”的概率显著更高；可把它做成一个 launch-phase long-only event alpha，而不是把 `vSOL` 本身误当成充分信号。**
- 是否可独立复现：**是**
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：**是**
- 主题标签：raw-alpha/event-driven/launchpad/pumpfun/solana/onchain/microstructure/flow-velocity/graduation-probability/bot-share/long-only/1m/3m/5m/public-data/paper/cost/risk
- 证据类型：2026 arXiv 论文 HTML source audit + Pump.fun 公开机制 + Solana 链上可观测交易日志口径

## 1. 这次看了什么
这轮补一个**和最近 perp pairs / funding / cross-venue 线不一样，但仍然是可独立复现的 raw alpha**：Marino、Naviglio、Tarantelli、Lillo 在 2026 年的新论文 **_Predicting the success of new crypto-tokens: the Pump.fun case_**。

一句话先说清这篇东西的 **base alpha**：**不是“某个 memecoin 会不会成功”这种叙事判断，而是“同样走到某个 bonding-curve 状态时，哪类 token 更容易继续吸到资金并冲向 graduation”**。对 short-cycle desk 来说，真正该抄的不是“毕业概率曲线”本身，而是其背后的 **path-dependent flow alpha**：**同样的 `vSOL`，快路径比慢路径更值钱；低 bot 污染路径比高 bot 污染路径更值钱。**

这条线之所以值得进池子：
- 它是 **raw alpha**，不是纯解释型综述；
- 数据**公开可拿**，链上逐笔可回放；
- 频率天然足够高，虽然不一定是传统 `5m/15m perp`，但非常适合 `1m/3m` 的**高强度事件驱动实验**；
- 能拆成完整策略：`entry / exit / sizing / cost / dump veto` 都能落地。

## 2. 核心结论
- 这篇东西的 base alpha 很清楚：**launch-phase continuation / graduation continuation**，不是 filter 伪装成 alpha。
- 样本非常大：作者抓了 **2025-09-01 到 2025-10-01** 的 Pump.fun 全量新币，合计 **655,770** 个 token；其中只有 **4,338** 个毕业，毕业率约 **0.63%**。这说明“随便冲”几乎一定死，必须做强筛选。
- 论文给出一个非常有用的**经济学 sanity check**：如果你在某个 `vSOL` 水位买入并持有到 graduation，最粗糙的 break-even 条件是
  `p(grad | features, vSOL) > (vSOL / 115)^2`。
  - 这意味着：`vSOL=30` 时至少要 **6.8%** 的毕业概率才勉强打平；
  - `vSOL=50` 时要 **18.9%**；
  - `vSOL=80` 时要 **48.4%**；
  - `vSOL=100` 时要 **75.6%**。
- 只看 `vSOL` 自身还不够。论文明确说：**仅靠 baseline `vSOL` 曲线，做 naive buy-and-hold 是过不了 break-even 的。** 真正有用的是附加条件。
- 最强附加条件不是“明星钱包”，而是**流动性积累速度**：在相同 `vSOL` 下，**用更少成交笔数冲到该水位**的 token，毕业概率明显更高；作者直说它是全文里**最有信息量的 predictor**。
- bot 结构也有用。作者表格给出的 out-of-sample 结果里：
  - 当 token 至少到过 `vSOL ≥ 80`，baseline 毕业概率约 **35.4%**；
  - 若再要求**非 bot 交易占比 > 30%**，概率升到约 **43.6%**；
  - 当 token 至少到过 `vSOL ≥ 100`，baseline 约 **63.8%**；
  - 加上同样的非 bot 条件后升到约 **74.8%**。
  这说明“谁在参与这段上涨”确实重要，不是只有资金量重要。
- 论文还提醒了一个很关键的现实：**creator/早期钱包的 dump 在这个生态里非常常见。** 在满足最少 30 笔成交的样本里，作者用稳健 Shewhart 规则检测到 **92.22%** 的 token 至少出现过一次 dump 事件。也就是说，这条 alpha 能做，但**不能把 exit 写得太天真**。

## 3. 为什么和当前项目有关
如果继续只补 perp trend / breakout / pairs，会慢慢形成素材池偏科；这篇东西补的是一个**此前素材池里相对缺的“一级发行 / launchpad / bonding-curve 微观结构 alpha”方向**。

它和当前 desk 的直接关系在于：
- 给 raw alpha 素材池补一条**事件驱动型**支线，而不是再补一个泛 filter；
- 可与我们已有的 `OFI / bot-flow / microstructure / liquidity gate` 框架共用很多实现件；
- 即使最后不做 Pump.fun，也能迁移到其他**launchpad / AMM 初期价格发现**场景；
- 对 `1m / 3m` 尤其友好：不是等 K 线走完，而是等**路径特征**成形。

## 3.5 策略拆解（必填）
- 方向属性：**event-driven / launch continuation / microstructure raw alpha**
- 基础 alpha：**同一 `vSOL` 水位下，资金积累更快、bot 污染更低、参与者结构更健康的 token，更可能继续完成 graduation；可做 launch phase continuation。**
- regime：**只在 Pump.fun / 类似 bonding-curve launchpad 的活跃时段有效；SOL 主链拥堵、手续费异常、链上拥堵严重时应降权。**
- filter / veto：**必须过滤极端 bot 污染、成交笔数过慢、creator dump 信号、极端单钱包控盘、超快不可成交 token。**
- risk / sizing / execution overlay：**长仓 only；极小单名义；分散到一篮子事件；触发 creator-dump / 急速回撤 / 时间超限就强平；不要用“持有到毕业”当唯一 exit。**

## 4. 可复刻的最小实验
### 4.1 研究假设
如果我们用公开 Solana 链上数据重建 Pump.fun token 的 launch 早期路径，那么**在相同 `vSOL` 阶段，`低 trades-to-vSOL + 低 bot share + 非单钱包挤出来的流入` 的组合，应当显著提高后续 1~15 分钟继续上冲 / 逼近 graduation 的概率与风险调整收益。**

### 4.2 先别做太花，最小版这样切
**Universe**
- 标的：Pump.fun 新发 token
- 样本：最近 `30` 天或 `60` 天
- 事件起点：token creation 后前 `15` 分钟

**状态变量**
1. `vSOL_now`
2. `n_trades_to_now`
3. `bot_share_to_now`
4. `unique_wallets_to_now`
5. `top_holder_share`（若拿得到）
6. `creator_related_wallet_sell_flag`（若拿得到）

**最小入场规则（v1）**
- 只看 token 第一次达到 `vSOL ∈ [30, 50]` 的时刻；
- 要求 `n_trades_to_now <= 50` 或落在当日同批 token 的前 `20%` 快路径分位；
- 要求 `bot_share_to_now <= 70%`（更保守可直接要求 non-bot > 30%）；
- 要求最近 `60s` 无单钱包大额 dump；
- 满足则在下一笔可成交价格或下一根 `15s/1m` bar 进场。

**最小出场规则（v1）**
- `TP1`：到达 `vSOL=80` / `100` 分段止盈；
- `TP2`：接近 graduation 前分批减仓，不强求吃满最后一段；
- `SL1`：出现 creator/关联钱包 dump 特征立即走；
- `SL2`：入场后 `3m / 5m` 内 `vSOL` 不再创新高则时间止损；
- `SL3`：价格自入场高点回撤超过阈值（例如 `12%~15%`）则止损。

### 4.3 成本口径
这条线一定要老实：
- Pump.fun 虚拟曲线阶段每次 swap 有 **1.25% fee**；
- 论文的 break-even 推导还**忽略 gas 与额外摩擦**，所以真实门槛只会更高；
- 若没有链上实际成交明细与滑点模型，任何纸面收益都很容易偏乐观。

### 4.4 先看 4 个指标
1. `conditional_grad_prob`：按 `vSOL bucket × speed bucket × bot-share bucket` 统计后续毕业率
2. `entry_to_exit_return_net_fee`
3. `max_drawdown_before_exit`
4. `creator-dump hit-rate after entry`

### 4.5 下一步怎么测
1. **先复现论文最核心的两层条件**：`vSOL` + `trades_to_vSOL`，确认“快路径优于慢路径”在你自己的链上重建口径里也存在；
2. 再加 `bot_share`，检验它对 `vSOL≥80` 和 `vSOL≥100` 区间是否真有 uplift；
3. 把“毕业”目标改成更贴 desk 的短持有目标，例如：`未来 1m/3m/5m 最大上冲幅度`、`是否在 5m 内继续冲到下一档 vSOL`；
4. 最后单独做 **dump veto**：入场后若出现 creator wallet/cluster 的异常集中卖出，策略收益是否明显改善。

## 5. 为什么这篇值得、但也不能过度神化
### 值得的地方
- 论文直接告诉你：**别把 `vSOL` 当充分条件，路径本身才是 alpha。**
- 数据是**公开链上原始数据**，不是黑箱 vendor；
- 可直接复现成**事件驱动完整策略**，而不是停在“解释一个现象”。

### 保留意见
- 这条线更像 **launchpad 特化 alpha**，不是通用 perp alpha；
- raw alpha 成立不代表容易实盘，因为**手续费高、滑点高、失败率极高**；
- 论文里的经济学 break-even 仍然过于乐观，因为它默认“失败就归零、成功就卖到毕业”，但没把所有现实摩擦和可成交性细节吃进去；
- “成功 trader” 这类变量有一定实现复杂度，且论文自己也承认不如 liquidity velocity 稳健；
- 生态中 dump 极多，所以**exit 设计的重要性不低于 entry**。

## 6. 我对 desk 的实际建议
如果真要把它推进到研发队列，建议不要一开始就做全量复杂模型，而是按下面顺序：
1. **先做快路径二分类**：`same vSOL, fewer trades wins?`
2. 再做 **bot-share 条件增强**；
3. 然后把目标函数从“毕业”替换成**更近端、更可交易的 1m/3m/5m follow-through**；
4. 最后才补 creator cluster、钱包画像、图聚类这些重特征。

换句话说，**先证明“路径速度”本身能赚钱，再去加更花的链上身份特征。**

## 7. 来源
1. **Giulio Marino, Manuel Naviglio, Francesco Tarantelli, Fabrizio Lillo. (2026). _Predicting the success of new crypto-tokens: the Pump.fun case_. arXiv, q-fin.ST.**
   - Venue: arXiv
   - DOI: <https://doi.org/10.48550/arXiv.2602.14860>
   - Readable URL: <https://arxiv.org/abs/2602.14860>
   - Readable URL: <https://arxiv.org/html/2602.14860v1>
   - Repo URL: N/A（未见公开代码仓库）

2. **Pump.fun Documentation / Platform mechanism (2026 access).**
   - Venue: Official Docs / Platform
   - DOI: N/A
   - Readable URL: <https://pump.fun>
   - Repo URL: N/A

3. **Solana RPC / transaction log data (2026 access).**
   - Venue: Solana Docs
   - DOI: N/A
   - Readable URL: <https://solana.com/docs/rpc>
   - Repo URL: N/A
