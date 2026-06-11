# 别把 100ms L2 方向概率只当 HFT demo：对 short-cycle desk，更该先测「persistent high-confidence L2 drift aggregation」这条 microstructure raw alpha

- 时间：2026-04-06 13:50 UTC
- 类型：2026 GitHub 新 repo source audit（README + 核心推理/特征/交易管理代码）+ Binance WebSocket 公共文档
- 主题类型：raw alpha
- 基础 alpha：**在 100ms 级别的 BTCUSDT L2 深度流里，盘口失衡、深度距离、累积量、短窗波动与 OBI 变化，会对未来 10 秒 mid-price 漂移给出方向 edge；把“连续高置信同向 10 秒信号”聚合成 `1m/3m` 持仓，而不是逐 tick 硬追，可形成一条可交易的短周期 directional raw alpha。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/microstructure/order-book/l2/depth-pressure/order-book-imbalance/directional/10s/100ms/probability-calibration/aggregation/binance/btc/1m/3m/5m/repo/public-data/cost/risk
- 证据类型：repo README + `feature_builder.py` + `model_runner.py` + `trade_manager.py` + Binance Spot WebSocket docs

## 1. 这次看了什么
这轮我没有继续补一篇“又一个 pairs / funding / carry 变体”，而是挑了一份 **刚更新的、能直接落成完整交易壳** 的新 repo：

- **ma8044 (2026), _Horizon-10_**
  - 类型：GitHub repo
  - Venue：GitHub
  - DOI：N/A
  - Readable URL：<https://github.com/ma8044/horizon-10>
  - Repo URL：<https://github.com/ma8044/horizon-10>
  - README raw：<https://raw.githubusercontent.com/ma8044/horizon-10/main/README.md>
  - Feature builder：<https://raw.githubusercontent.com/ma8044/horizon-10/main/backend/app/engine/feature_builder.py>
  - Model runner：<https://raw.githubusercontent.com/ma8044/horizon-10/main/backend/app/engine/model_runner.py>
  - Trade manager：<https://raw.githubusercontent.com/ma8044/horizon-10/main/backend/app/state/trade_manager.py>

补充的公开数据/文档口径：

- **Binance Spot WebSocket Streams**
  - Readable URL：<https://developers.binance.com/docs/binance-spot-api-docs/web-socket-streams>
  - repo 内默认 live endpoint：`wss://stream.binance.com:9443/ws/btcusdt@depth20@100ms`

我最后选它，原因很直接：

1. **base alpha 很清楚，而且是 raw alpha。** 不是“模型能不能预测”这种空话，而是 **L2 微观结构状态 → 下一个短窗 mid-price 漂移**。
2. **它已经把 entry / exit / cost 壳写出来了。** 这比只给一堆 feature 重要得多。
3. **它正好补当前学习进展里的一个缺口：** 我们最近 intake 里已经有很多 microstructure 因子，但真正把“特征 → 校准概率 → 阈值入场 → spread-crossing 成本 → 固定 horizon 平仓”串成一条完整策略壳的材料还不算多。

换句话说，这一轮不是在补“新术语”，而是在补 **可直接落回测框架的完整微结构 raw alpha 壳**。

---

## 2. 先回答：这篇东西的 base alpha 是什么？
### 2.1 base alpha 是清楚的，而且不是 filter 伪装
一句人话：

> **如果买盘/卖盘深度、盘口距离、累积量和短窗 OBI 变化，在连续几个 100ms tick 上都朝同一个方向挤压，那未来 10 秒的 mid-price 更容易朝同向漂移。**

repo 里把这件事落成了一个非常直接的预测对象：

- 标的：`BTCUSDT`
- 数据：Binance `depth20@100ms` L2 流（live）
- 标签：未来 **10 秒** mid-price 方向
- 类别：`Decrease / Stable / Increase`
- 方向阈值：**0.5 bps**（README 直接写明）

这不是 overlay。
这也不是 regime gate。
它本体就是一条 **microstructure directional raw alpha**：

- 看到同向微结构压力；
- 用校准后的方向概率决定要不要进；
- 持有一个固定短 horizon；
- 吃 mid-price 漂移减去 spread-crossing 成本。

### 2.2 为什么它比继续补一篇“普通 OFI / OBI 论文”更值得
因为我们最近已经看过不少：

- OFI / VWAP pressure
- L1 / L2 imbalance
- adverse selection / VPIN / toxicity
- microprice / jump continuation

这些材料多数都告诉你：

> **“这个 feature 可能有 edge。”**

但 `Horizon-10` 多走了一步，它直接告诉你：

> **“这条 edge 怎么以 10 秒持有期、阈值触发、显式 spread-crossing 的方式被交易出来。”**

这对当前 desk 更值钱。因为 bot7 当前优先级本来就不是继续堆“解释型 feature”，而是扩充 **可独立复现、可直接落地的策略素材池**。

---

## 3. repo 到底给了什么对 desk 有用的证据
### 3.1 它不是一句“我有个模型”，而是完整给出特征布局
`feature_builder.py` 把实时特征工程写得非常清楚，而且强调 **zero allocations per tick**。核心是 **131 个特征**：

- `[0-39]`：20 档 ask/bid 原始量
- `[40]`：spread
- `[41]`：tick 间时间差（microseconds）
- `[42-121]`：每档 price distance + cumulative volume
- `[122-124]`：`OBI top 5 / 10 / 20`
- `[125-130]`：短窗时间特征
  - `volatility_mid_5s`
  - `volatility_obi_5s`
  - `obi_10_delta_1s`
  - `ask_vol_accel_1s`
  - `bid_vol_accel_1s`
  - `obi_10_delta_5s`

翻成人话，它不是只看一个“OBI 大于 0 就做多”的简陋规则，而是在做：

> **盘口厚度、深度距离、失衡、5 秒噪声强度、1~5 秒压力变化的联合读数。**

这点很重要，因为它意味着 desk 后续最小实验不一定非得全抄 131 维；也可以先抽出：

- `OBI_top10`
- `spread`
- `distance_to_mid`
- `5s mid vol`
- `OBI delta 1s / 5s`

做一版轻量 existence check。

### 3.2 它给的训练口径够具体，能让我们知道不是随手拼 demo
README 写了几组很关键的数据点：

- **数据源**：Tardis 的 Binance `book_snapshot_25`
- **样本区间**：`2025-01` 到 `2026-04`
- **总样本行数**：**11,782,301**
- **标签 horizon**：**10 秒**
- **方向阈值**：**0.5 bps**
- **切分方式**：严格时间顺序，`70% train / 10% val / 20% test`

这些数字不代表它已经被验证成 production alpha；但至少说明：

- 它不是拿几小时样本做玩具实验；
- 它至少认真处理了时间顺序和泄漏问题；
- 它有明确、稳定的 label 口径，而不是事后挑窗口。

### 3.3 它把“概率校准”单独拿出来了，这对实盘很关键
`model_runner.py` 不是裸 LightGBM，而是：

- `LightGBM booster`
- 再包一层 **per-class Isotonic Regression calibration**
- 最后输出归一化概率：`[P(Decrease), P(Stable), P(Increase)]`

这点对 desk 的价值，比“模型多复杂”更大。

因为短周期方向壳最怕的是：

- logit / tree score 看起来很大；
- 但不同时间段分数不可比；
- 一上线就发现 threshold 根本没法稳定设。

repo 至少在框架上解决了这个问题：

> **把模型输出变成可设阈值的 calibrated probability。**

这让它自然适合做：

- 二段式入场（先看方向，再看置信度）
- 不同成本场景下的 threshold sweep
- 概率分桶后的单调性检查

### 3.4 它把交易管理也写成了明确规则，而不是“预测完就算完”
`trade_manager.py` 里最值钱的部分，是把交易落成了一个很诚实的 paper-trade 壳：

- 当 `P(Increase) >= threshold`：**LONG**，以 `asks[0]` 入场
- 当 `P(Decrease) >= threshold`：**SHORT**，以 `bids[0]` 入场
- 若多空都超过阈值：取概率更大的方向
- 持有 **10 秒**
- 用当时的 **mid-price** 平仓
- PnL 直接按 **spread-crossing** 后的 bps 计算

这比很多“方向预测论文”更诚实，因为它至少把最基本的成本楔子打进去了：

- LONG 不是用 mid 买入，而是用 ask；
- SHORT 不是用 mid 卖出，而是用 bid。

也就是说，repo 虽然没把 taker fee / 滑点 / queue position 全部算进来，但至少已经避免了最常见的 paper alpha 自欺：

> **拿 mid-to-mid 漂移冒充可交易收益。**

---

## 4. 对 short-cycle desk，最该拿走的不是“131 features”，而是这个更小、更可测的 alpha 壳
### 4.1 最重要的，不是逐 tick 乱开仓，而是做“persistent high-confidence aggregation”
如果机械照搬 repo 的 100ms 触发，很容易遇到：

- 信号太密；
- 连续同向开很多单；
- spread / fee 把 edge 吃掉；
- 结果只剩“看上去很忙”。

所以对我们 desk，更好的读法不是：

> **每个 100ms 有方向就冲。**

而是：

> **把连续 10 秒方向概率，聚合成 `1m / 3m` 的可执行 admission score。**

例如：

- 过去 `30s` 或 `60s` 内，统计 `P(up) - P(down)` 的时间平均；
- 或统计高置信同向 tick 的占比；
- 只有当这个聚合分数过阈值，才在下一根 `1m` bar 执行一次。

这一步非常关键。因为它把 repo 的 HFT 壳，翻译成了我们 desk 更能承受的短周期版本。

### 4.2 这条 alpha 最适合 `1m / 3m`，`5m / 15m` 更像聚合或 veto 层
我会很诚实地定位：

- **主 alpha 节奏**：`10s` 原生，最适合映射到 `1m / 3m`
- **`5m`**：可作为持有延展或 regime 聚合层
- **`15m`**：更适合做 execution veto / 交易时段限制，而不是把它硬抬成 15m 主信号

所以它是符合用户这轮偏好的：

- 允许 `1m / 3m` 的更快高强度 alpha；
- 不需要硬伪装成慢因子。

### 4.3 为什么它对当前素材池有直接关系
因为当前素材池里，已经有很多：

- trend / breakout / squeeze release
- pairs / stat-arb / carry / funding
- 单特征 microstructure alpha

但如果你真想把 short-cycle 盘做起来，还差一类材料：

> **从“连续 microstructure pressure”直接映射到“什么时候下单、持有多久、阈值设多高”的完整壳。**

`Horizon-10` 补的就是这一块。

---

## 5. 如果直接落地成完整策略，我会怎么写
### 5.1 entry
先不要全抄 repo 的逐 tick 模式；我会先写成 desk 版最小壳：

1. 从 Binance `depth20@100ms` 取 L2 快照；
2. 计算一版轻量 10s microstructure score：
   - `OBI_top10`
   - `spread`
   - `top-level volume imbalance`
   - `5s volatility_mid`
   - `obi_delta_1s`
   - `obi_delta_5s`
3. 每 `100ms` 产出 `P(up), P(down)`；
4. 在最近 `30s~60s` 聚合：
   - `agg_score = mean(P(up)-P(down))`
   - `same_sign_share = share(|P(up)-P(down)| > q and sign same)`
5. 只有当：
   - `agg_score > threshold`
   - `same_sign_share > threshold`
   - `spread < spread_cap`
   才在下一根 `1m` 或 `3m` 开仓。

### 5.2 exit
第一版别复杂化，直接做 3 层：

- **时间止盈/止损**：持有 `1 bar / 3 bars`
- **反向概率退出**：若 `P(down)-P(up)` 明显翻负（或翻正），提前平
- **微观结构失真退出**：若 spread 急扩、book top volume 骤降，直接平

如果要更贴 repo 原文，可以先保留一个更短的 direct replication 版：

- 10 秒 horizon
- ask/bid entry
- mid exit

这版适合作为 existence check。

### 5.3 sizing
sizing 不应该只按方向概率大小一把梭。第一版建议：

- `size ∝ clipped(|agg_score|)`
- 再乘：
  - `1 / spread`
  - `1 / realized_vol_1m`
  - `liquidity_cap`

也就是：

> **同样强的方向信号，贵的 spread、小的盘口、炸的短窗波动，都应该自然缩仓。**

### 5.4 risk
这条 alpha 最怕的不是“方向错一点”，而是：

- spread 扩张；
- 盘口突然抽空；
- 你看到的深度是假的，冲进去就没了；
- 信号只在极短 horizon 有效，却被你拉成过长持仓。

所以风控至少要盯：

- `spread cap`
- `book top depth floor`
- `signal age limit`
- `no-overlap / cooldown`
- 事件时段 veto（宏观数据、资金费率结算前后等）

### 5.5 cost
repo 已经做了最基础的一步：

- LONG 用 ask 入场
- SHORT 用 bid 入场

但 desk 真回测时，至少还要再补：

- taker fee
- partial fill / queue slippage
- 盘口穿透成本
- 高拥挤时的额外 impact

尤其是 10 秒 alpha，**不把 fee / slippage 写进回测，几乎等于没测。**

---

## 6. 外部数据与公开性：这条线能否快速复现？
### 6.1 原 repo 的训练数据不完全免费，但最小实验可以用公开流重做
repo 训练部分写的是：

- Tardis `book_snapshot_25`
- `2025-01` 到 `2026-04`
- 共 11.78M 行

这说明作者训练底层使用的是商业归档数据。

但对我们来说，这不构成阻碍。因为它的 **live inference 口径本身就是 Binance 公共 WebSocket**：

- `btcusdt@depth20@100ms`

所以 desk 最小实验完全可以改成：

- 直接抓 Binance 公共 L2 流；
- 本地缓存滚动窗口；
- 先测 existence，再决定要不要买更完整的归档数据补训练。

### 6.2 更新频率：天然适合超短周期
这条线的数据更新频率就是 `100ms`，所以它天然服务的是：

- `10s`
- `30s`
- `1m`
- `3m`

如果硬往 `15m` 上套，它更像：

- intrabar entry timing layer
- microstructure veto
- direction vote aggregator

### 6.3 最小可复现实验口径
**实验对象：** BTCUSDT

**数据源：** Binance public depth20 websocket

**更新频率：** `100ms`

**最小特征子集：**

- top-5 / top-10 OBI
- spread
- bid/ask top depth
- cumulative depth 10
- OBI delta 1s / 5s
- mid vol 5s

**最小标签：**

- 未来 `10s` mid return sign
- threshold 先抄 repo：`0.5 bps`

**最小回测壳：**

- 每 100ms 产生一个方向分数
- 聚合到 `1m`
- next-bar open 执行
- hold `1~3` bars
- taker fee + spread + impact cap

这已经足够回答：

> **“这条 10 秒级微结构方向 edge，能不能翻译成 desk 可用的 `1m/3m` raw alpha？”**

---

## 7. 这轮最值得立刻做的 3 个最小实验
### 7.1 实验 1：direct replication — 先测 repo 原生 10 秒壳还有没有 edge
目的：先回答“原生壳本身行不行”。

- 数据：Binance `depth20@100ms`
- 标的：BTCUSDT
- 规则：
  - `P(up) >= t` 做多，ask entry
  - `P(down) >= t` 做空，bid entry
  - `10s` 后 mid exit
- sweep：`t = 0.45 / 0.50 / 0.55 / 0.60`

关键看：

- 概率分桶单调性
- cost 前后 hit-rate
- threshold 上升时 precision 是否改善到足以覆盖 cost

### 7.2 实验 2：desk translation — 看“持续高置信聚合”能否优于逐 tick 开仓
目的：回答“如何从 HFT shell 翻译到 short-cycle shell”。

- 把 100ms 信号聚成 `1m`
- 只做每分钟一次决策
- 比较：
  - 逐 tick 开仓
  - `30s` 聚合开仓
  - `60s` 聚合开仓

如果聚合版的：

- trade count 明显下降
- 单笔 edge 更高
- fee drag 更小

那就说明这份 repo 最值钱的，不是 131 个 feature，而是 **microstructure persistence admission shell**。

### 7.3 实验 3：跨资产可移植性 — BTC 成立后，看看 ETH / SOL 会不会更强或更弱
目的：别把它锁死成“只对 BTC 有用”。

- 先冻结 BTC 的轻量特征子集与阈值
- 横移到 `ETHUSDT / SOLUSDT`
- 比较：
  - threshold 稳定性
  - spread 后 edge
  - signal decay 速度

如果 ALT 上 alpha 更脆弱，那这条线就更适合作为：

- BTC 主 alpha
- ALT execution veto / vote layer

---

## 8. 我对这条主题的判断
### 8.1 这是 raw alpha，不是“模型综述”
因为它的本体不是“LightGBM 好不好”，而是：

> **order-book pressure 是否能在未来 10 秒给出可交易方向漂移。**

模型只是实现方式。
alpha 本体是 **短窗盘口压力 → 短窗价格漂移**。

### 8.2 它为什么值得进当前素材池
因为它满足 bot7 当前优先级里最值钱的那一档：

- **可独立复现**：是
- **可直接写完整 entry/exit/cost**：是
- **和当前 short-cycle desk 直接相关**：是

更重要的是，它不是又一篇“解释为什么市场会动”的材料，而是已经告诉你：

- 特征怎么摆
- 概率怎么校准
- 阈值怎么触发
- 成本怎么先粗略打进去

### 8.3 它的局限也要说清楚
我不会把它吹成“已经验证的 production alpha”，因为 README 没给出足够完整的样本外 PnL / Sharpe / turnover / fee 后归因表。

所以更准确的定位是：

> **一份高信号、可快速复现、能直接变成最小实验的 repo-based raw alpha 候选。**

这正符合本轮任务要求。

---

## 9. 下一步怎么测
我建议下一步直接分成 **两层 verdict**：

1. **2~4 小时快速 verdict**
   - Binance public depth20@100ms
   - 轻量特征子集
   - 先测原生 `10s` 壳
   - 检查 probability bucket 单调性 + cost 后 hit-rate

2. **半天正式最小版**
   - 把 100ms 方向概率聚合成 `1m / 3m` admission score
   - 加 `spread cap / cooldown / no-overlap / fee`
   - 对 BTC / ETH / SOL 做横截面对照

如果第二层比第一层更稳，说明：

> **这份 repo 对 desk 最值钱的，不是“高频模型”四个字，而是“连续高置信 microstructure pressure 的短周期聚合交易壳”。**

## 10. 来源清单
- ma8044 (2026), _Horizon-10_ (GitHub Repo)  
  <https://github.com/ma8044/horizon-10>
- README raw  
  <https://raw.githubusercontent.com/ma8044/horizon-10/main/README.md>
- `backend/app/engine/feature_builder.py`  
  <https://raw.githubusercontent.com/ma8044/horizon-10/main/backend/app/engine/feature_builder.py>
- `backend/app/engine/model_runner.py`  
  <https://raw.githubusercontent.com/ma8044/horizon-10/main/backend/app/engine/model_runner.py>
- `backend/app/state/trade_manager.py`  
  <https://raw.githubusercontent.com/ma8044/horizon-10/main/backend/app/state/trade_manager.py>
- Binance Spot WebSocket Streams  
  <https://developers.binance.com/docs/binance-spot-api-docs/web-socket-streams>
