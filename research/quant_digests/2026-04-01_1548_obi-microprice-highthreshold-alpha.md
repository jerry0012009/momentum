# 别把这份 2025 OBI ML repo 只读成“高 AUC HFT demo”：对 short-cycle desk，更该先诚实快检的是「多窗口 OBI × microprice 信号 × 高阈值 directional admission」这条 fast raw alpha

- 主题类型：raw alpha
- 基础 alpha：多窗口 order-book imbalance（OBI）+ microprice lead 所刻画的**极短周期方向延续 / 漂移**（microstructure / directional continuation）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 时间：2026-04-01 15:48 UTC
- 类型：2025 GitHub 新仓库 source audit（`README.md` + `train_ultimate_model.py` + `test_ultimate_backtest.py` + `src/processors/improved_features.py` + `collect_week_data.py` + GitHub API metadata）
- 主题标签：raw-alpha/microstructure/order-book/obi/microprice/high-threshold-admission/directional/continuation/lightgbm/binance/btc/eth/bnb/sol/1m/3m/5m/repo/public-data/cost/latency
- 证据类型：2025 GitHub 新仓库 source audit（核心特征/训练/回测文件 + 仓库元数据）

## 1. 这次看了什么
这次主材料不是论文，而是一份 **2025-10-18 创建** 的 GitHub 新仓库：**vinay2209 (2025), _hft-order-imbalance-trading_**。repo headline 很容易让人把它读成“又一个 HFT + ML demo”，但对我们 desk 真正更值得 intake 的，不是它的 AUC headline，而是它已经写得很清楚的那条 **盘口失衡 directional raw alpha**：

- 用 Binance L2 order book 公共流抓多币盘口快照；
- 从 **OBI / weighted OBI / volume imbalance / spread / volatility / microprice** 做多窗口特征；
- 预测未来一小段时间里，价格是否会走出**足够覆盖成本**的同向漂移；
- 再用高阈值 admission 去决定何时出手。

翻成人话：
**它不是在赌“ML 会神奇赚钱”，而是在赌“当盘口压力明显偏向一边时，后面会有一个足够大的极短周期同向漂移”。**

这是一条很标准的 `raw alpha`，只是当前 repo 也很诚实地告诉你：**alpha 存在，不等于 taker after-cost 能活。**

## 2. 先回答一句：这篇东西的 base alpha 是什么？
**base alpha 不是 LightGBM，也不是 AUC。**

它的 alpha 本体是：
- 当买盘深度明显压过卖盘深度、且 microprice 已经领先 mid-price 上移时，
- 后面极短一段时间里，mid-price 更容易继续往上漂；
- 反过来，卖压失衡时，更容易往下漂。

也就是：
**盘口失衡 + microprice lead → 极短周期方向延续。**

所以它是：
- `raw alpha`
- `microstructure`
- `directional continuation`
- 不是 filter，不是 regime，也不是只能依附别的 alpha 才能活的 overlay。

## 3. 为什么这轮值得写，而不是继续补一个只会服务别人的 gate
最近我们已经补过不少：pairs、carry、cross-sectional、breakout、liquidity overlay、maker OBI。当前还值得继续扩的，是**更快、更脏、但能直接扩张素材池的 fast alpha**。这份 repo 值得进池，原因有三条：

1. **base alpha 很清楚。** 就是盘口压力是否继续传导到短期价格漂移。
2. **公开数据拿得到。** Binance 公共 WebSocket/L2 就够做最小实验，不依赖封闭流。
3. **repo 给了诚实的 cost/latency 结论。** 它不是“回测乱飞”，而是直接告诉你：高 AUC 也可能 still fail fee wall。这对 desk 很值钱，因为它帮助我们更快把这类 alpha 放对位置：**是 maker-biased fast alpha，还是 naive taker 不该碰的东西。**

## 4. 这次看的主来源
### 4.1 主来源（repo）
- **Author / Repo owner**：vinay2209
- **Year**：2025
- **Title / Repo**：*hft-order-imbalance-trading*
- **Venue**：GitHub repository
- **DOI**：N/A
- **Readable URL**：https://github.com/vinay2209/hft-order-imbalance-trading
- **Repo URL**：https://github.com/vinay2209/hft-order-imbalance-trading
- **GitHub metadata**：created `2025-10-18T17:52:35Z`，pushed `2025-10-18T17:59:43Z`

### 4.2 这轮实际看的关键文件
- `README.md`
- `train_ultimate_model.py`
- `test_ultimate_backtest.py`
- `src/processors/improved_features.py`
- `collect_week_data.py`

## 5. 这条 raw alpha 在代码里到底怎么定义
### 5.1 数据口径本身就是盘口级
`collect_week_data.py` 里，repo 直接从 Binance order book stream 抓：
- `BTCUSDT`
- `ETHUSDT`
- `BNBUSDT`
- `SOLUSDT`

并且设定：
- order book `depth=10`
- 目标一周连续抓取
- 代码里写的是 **7 天约 600 万 snapshots** 的量级目标

这说明它的原始 alpha 不是 K 线级别，而是**盘口更新级 / event-time** 级别。

### 5.2 特征核心不是“黑箱”，而是经典盘口压力 + 领先价
`improved_features.py` 里最关键的几类特征有：
- `obi` 与 `weighted_obi`
- 多窗口 rolling OBI（`5/10/20/50/100`）
- OBI momentum（`diff(5/10/20/50)`）
- `volume_imbalance`
- `spread_bps`
- `microprice_signal`
- 多窗口短期波动率

这里最该拿走的不是“用了很多 feature”，而是它其实已经把 alpha 拆得很白：

1. **深度失衡**：哪边挂单更厚；
2. **领先价格**：microprice 是否已经比 mid-price 更偏向某边；
3. **成本门槛**：spread / slippage / fee 够不够让这次信号值得做。

### 5.3 target 也不是简单 next-tick，而是“成本后还值不值得做”
repo 的 target 不是随便预测下一跳方向，而是先把成本写进去：
- taker fee：`4 bps`
- estimated slippage：`2 bps`
- 合计成本：`6 bps`
- 额外最小利润要求：`5 bps`

所以 `target_profitable_50` 的意思不是“50 步后涨没涨”，而是：
**50 步后，是否涨到足够覆盖 6 bps 成本，再额外留出 5 bps 盈利空间。**

这点非常重要，因为它把 raw alpha 从一开始就放进了成本语境里，而不是先做一个没法交易的 classification demo。

### 5.4 训练层其实是在回答一个很具体的问题
`train_ultimate_model.py` 的问题本质上是：

> 给定当前盘口失衡、microprice、spread、波动率、量能状态，未来极短一段时间里，是否会出现**足够大的同向价格漂移**？

这比“未来涨跌方向预测”更接近真实交易问题。

## 6. 最值得拿走的硬数据点
### 6.1 repo 自己给出的 headline 数字
`README.md` 直接写了四个最重要的数据点：
- **3.75M samples**
- **AUC = 0.8658**
- **Win rate ≈ 47%**
- **Net return = -2.76%**

这个组合很关键，因为它直接说明：
**分类质量不错，不代表策略 after-cost 能活。**

### 6.2 机会密度本身就很稀缺
repo 还给了一个很值钱的事实：
- 满足“足够覆盖成本并有意义盈利”的价格移动，
- **只占 1.076%**。

翻成人话：
**这不是一条可以频繁随便打的 alpha，而是必须高阈值筛选、机会本来就稀少的 fast alpha。**

### 6.3 latency wall 也被写死了
`README.md` 的直白结论：
- repo 端到端 latency：`50–100ms`
- professional HFT：`<1ms`

也就是说，即使你方向判断是对的，**机会窗口也可能在你下单前就没了**。

### 6.4 数据规模与交易对设置至少不是玩具
`collect_week_data.py` 和训练脚本给出的口径：
- 4 个主流币：BTC / ETH / BNB / SOL
- 全量训练 `3.75M` 样本
- 时间顺序切分：`70/15/15`
- target 正样本非常稀薄（脚本日志模板显示要打印正样本占比）

这至少说明它不是拿几千条样本硬讲故事。

## 7. desk 角度最该偷的，不是 AUC，而是“高阈值 + 稀有机会 + 成本墙”这三个约束一起看
如果照 headline 去抄，你很容易把注意力放在：
- LightGBM 参数怎么调；
- AUC 能不能再从 0.8658 提到 0.88；
- feature importance 里谁排第一。

但对当前 desk，更值钱的读法是：

1. **raw alpha 本体**：盘口失衡 → 极短周期方向漂移；
2. **真正的限制**：机会稀缺、cost wall 高、latency 要求极苛；
3. **更适合 desk 的旁支读法**：不要把它直接当 taker HFT，而要把它看成 `1m/3m` maker-biased directional admission，或者 `5m` 策略的微结构确认层。

换句话说：
**这轮真正值得 intake 的，不是“复制 repo 的 HFT 系统”，而是“盘口失衡 fast alpha 存在，但只在高 admission bar + 低成本执行下才可能留边”。**

## 8. 这份 repo 为什么目前不能算“可直接落地完整策略”
这条必须写清楚，不然会把 raw alpha 和完整策略混在一起。

### 8.1 回测壳子还不够严谨
`test_ultimate_backtest.py` 至少有三个问题：
- 先 `sample(frac=0.1)` 再按时间排序，等于把原本连续盘口序列打散后重拼；
- 只测 `ETH` 单一合约；
- `holding_time = i - self.get_last_buy_index()` 这里拿“trade list 索引”近似“数据行索引”，持有时长口径并不干净。

所以：
**这份 repo 足够支撑“alpha existence / desk framing”，但还不够支撑“直接照抄回测收益”。**

### 8.2 执行假设对 desk 很关键
回测里用的是：
- maker fee `1 bp`
- slippage `1 bp`
- 合计 `2 bps`

但 README 总结里同时强调：
- 一般 round-trip 成本约 `2 bps`
- 想稳定赚钱需要更低费率、更低延迟、更大资金

所以它已经很明确地把自己限定在：
**只有 execution 足够强时，这条 raw alpha 才可能从“存在”变成“可交易”。**

## 9. 对 `1m / 3m / 5m / 15m` 的 desk 化映射
### 9.1 这条 alpha 的原生时间尺度更快
repo 的 native target 是 `10/20/50/100` 个盘口更新步，而不是 `5m/15m` bar。也就是说：
- 它更接近 `seconds / tens-of-seconds` 的 event-time alpha；
- 不是天然为 `15m` trend desk 设计的东西。

但这不代表它对我们没用，反而意味着：
**更合理的迁移方式，是把它当成 fast layer，服务 `1m/3m` 主交易或 `5m` admission。**

### 9.2 `1m` first-pass：先测 alpha existence
第一刀建议先做：
- Binance perp / spot 公共盘口流
- 主流币 `BTC/ETH/SOL/BNB`
- 每 `1m` 聚合出：
  - 平均 OBI
  - 末值 OBI
  - OBI slope
  - microprice-midprice gap
  - spread 均值与极值
- 预测未来 `1m` 或 `3m` 收益是否超过 `4/6/8 bps`

这是最接近 repo 原始思想，又能在 desk 上最小复现的一步。

### 9.3 `3m` second-pass：更像实际可交易口径
如果 `1m` 上方向性存在，但噪音太大，就把同一组特征降采样到 `3m`：
- 对 fast alpha 来说，`3m` 通常比 `5m/15m` 更像“还能保留 microstructure 信息”的上限；
- 也更容易让普通执行条件比秒级 HFT 稍微友好一点。

### 9.4 `5m/15m` 不该直接照搬成主 signal
到了 `5m/15m`，盘口失衡的边际信息会被大幅冲淡。更合理的做法通常不是：
- 直接拿 OBI 模型做 `5m/15m` 主 alpha，

而是：
- 用它做 `5m` breakout / momentum / mean-reversion 的 **entry veto / confirmation**；
- 或用它做 maker-vs-taker execution switch。

所以对我们当前 desk，这条 raw alpha 与 `5m/15m` 的关系是：
**更适合作为 fast sleeve 或微结构 admission，而不是直接替代主频 alpha。**

## 10. 可以怎样落成最小策略骨架
### 10.1 Entry
- 每 `1m` 计算：
  - top-of-book OBI
  - 5/10/20 bar OBI 均值与变化率
  - microprice gap
  - spread / realized vol
- 只有当：
  - `OBI_z` 足够高；
  - `microprice_gap` 同向；
  - `spread` 未显著放宽；
  - `realized vol` 没进入极端噪音区；
  才允许做多；做空同理。

### 10.2 Exit
第一版先别复杂化：
- 固定持有 `1/3/5` 根 `1m` bar；
- 或信号反向立即平；
- 或 `microprice_gap` 回到 0 附近平。

### 10.3 Sizing
这类 alpha 不适合“越有信号越梭哈”。第一版先：
- 单币固定 risk unit；
- spread/vol 扩大时自动降杠杆；
- 盘口深度不足时不放大仓位。

### 10.4 Risk / Cost
至少要有：
1. **spread veto**：spread 高于滚动分位阈值时不做；
2. **latency veto**：撮合延迟超阈值时停机；
3. **queue-quality gate**：如果做 maker，要看是否真的有排队优势；
4. **event veto**：重大数据/大单扫盘 bar 不把普通 OBI 当正常信号；
5. **cost ladder**：必须跑 `2/4/6/8/10 bps` after-cost，而不是只看 gross。

## 11. 最小可复现实验（直接对当前 desk）
### 实验 A：先做最朴素的 `1m` OBI directional existence check
- **Universe**：BTC / ETH / SOL / BNB
- **Data**：Binance 公共盘口流
- **Features**：OBI、weighted OBI、microprice gap、spread、vol
- **Target**：未来 `1m` / `3m` 收益是否超过 `4/6/8 bps`
- **回答问题**：在不做复杂 ML 的前提下，盘口失衡是否已经有方向性 edge？

### 实验 B：ablation ladder
固定同一口径，只比较：
1. 仅 OBI
2. OBI + microprice gap
3. OBI + microprice + spread gate
4. 再加 vol gate

这个实验很关键，因为它能直接回答：
**真正有贡献的是失衡本身、领先价、还是成本门控。**

### 实验 C：execution realism check
同一信号，同一持有期，只改：
- `2 bps`
- `4 bps`
- `6 bps`
- `8 bps`
- `10 bps`

并对比：
- taker-only
- maker-biased
- hybrid

要回答的问题是：
**这条 alpha 是“信号强但执行要求太高”，还是“信号本身就不够”。**

## 12. 下一步怎么测
建议按这个顺序走：

1. **先做 `1m -> 3m` 的 OBI / microprice 最小实验**，不要一上来就迷信模型复杂度。
2. **先用线性/阈值规则做 existence check**；如果连简单版本都没有信息，再上 LightGBM 没意义。
3. **第二步只做一件事：把 cost ladder 跑清楚。** 这条 alpha 的核心不是“准不准”，而是“过不过 fee wall”。
4. **如果 `1m/3m` 只有 maker-biased 才活，就把它明确定位成 fast sleeve / execution admission。**
5. **只有当 `1m/3m` 的 after-cost 版本已经活下来时**，才值得讨论往 `5m` 主策略里并进去做确认层。

## 13. 一句话结论
这份 2025 repo 真正值得 short-cycle desk intake 的，不是“0.8658 AUC 的 HFT 模型”这个 headline，而是更朴素也更诚实的结论：

**多窗口 OBI × microprice 的 fast directional raw alpha 确实存在，但它天然是“高阈值、低频机会、强执行依赖”的东西；先把它当 `1m/3m` maker-biased alpha existence card 来测，不要直接伪装成 `5m/15m` 主信号。**
