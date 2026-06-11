# 别把 15m 动量 pocket 直接当真 alpha：先让它过 `TSM vs drift` 诚实门
- 时间：2026-03-17 16:35 UTC
- 类型：论文
- 主题标签：trend / momentum / honesty-gate / drift / crypto / 15m
- 证据类型：论文证据 + desk source intake

## 1. 这次看了什么
这次回收的是：
- **Huang, Li, Wang, Zhou (2020)**
- **Time series momentum: Is it there?**
- Venue: **Journal of Financial Economics**
- DOI: **10.1016/j.jfineco.2019.08.004**

这篇对当前 desk 最有用的，不是再给一个“新动量 alpha”，而是给出一个更便宜也更诚实的 intake 提醒：**别把回测里赚钱的动量策略，直接误读成“最近几根收益方向本身就有稳定预测力”。**

翻成当前 15m crypto scout 语言：如果一条候选主要只是顺着长期漂移/均值方向在吃 beta，或者只是被仓位/波动缩放救起来，那它不该被过早写成 `paper candidate`。在进入更重的 stability 包之前，先做一刀 `TSM vs drift` 的轻量诚实门，边际价值很高。

## 2. 核心结论
- **结论 1：经典 TSM 策略赚钱，不等于“最近收益符号”这个简单信号本身证据很硬。** 论文重做了经典 TSMOM 证据链，发现逐资产 time-series 回归很弱；很多看起来强的 pooled 结果，在 bootstrap 校正后并不够稳。
- **结论 2：策略收益里，可能混进了“历史平均漂移/长期均值方向”的贡献。** 作者构造了一个不要求 serial predictability 的对照思路（`TSH / history` 类基线），结果发现它和经典 TSM 的收益表现非常接近。
- **结论 3：因此更诚实的问题不是“这条动量线有没有赚钱”，而是“它到底是在吃 recent-return signal，还是只是在吃更慢的 drift / beta / weighting effect”。**
- **结论 4：对当前 desk 来说，这意味着 `sign(momentum)` 家族应先过一刀 cheap honesty gate，再决定要不要继续给 clean replication / stability budget。**

## 3. 为什么和当前项目有关
一句话核心结论：**这条 source intake 不是要扩一个新大框架，而是给当前 `5m / 15m crypto` scout 池补一个更便宜的 admission honesty gate。**

它直接服务当前 board 的三个需求：
1. **更快给 hard verdict**：先回答“这条 edge 是 recent momentum 还是慢 drift”，比继续磨近义说明页更能改变 verdict。
2. **更贴近当前主线**：这不是新的外部数据线，也不是另起炉灶；它直接落在现有 `multi-tf momentum / sign(momentum)` 邻近家族上。
3. **预算友好**：只需要复用现有 `BTC/ETH/SOL 120d 15m` cache，就能先做一轮最小 clean replication / honesty 对照。

## 4. 对 desk 的最小 clean-room 映射（source intake only）
### 候选名
`recent-return sign vs history-drift honesty gate`

### trade on / trade off
- **trade on（baseline leg）**：当前资产最近一段固定窗口收益为正/负，则沿该方向交易（最小版 `sign(momentum_N)`）
- **trade on（drift leg）**：当前资产更慢的 rolling / expanding 平均收益方向为正/负，则沿该方向交易（`history-drift sign`）
- **trade on（agree-only gate）**：只有当 `recent-return sign` 与 `history-drift sign` 同向时，才允许保留 recent-momentum 交易
- **trade off**：方向缺失，或 recent sign 与 drift sign 冲突

### 先不做什么
- 不扩成全市场横截面动量宇宙
- 不引入额外外部数据
- 不一上来做重型参数搜索
- 不把它误写成 `paper candidate`；这一轮只是 `source intake`，下轮若继续，默认只做最小 clean replication

## 5. 下轮最小 clean replication 应该怎么做
### 固定样本
- 资产：`BTC / ETH / SOL`
- 周期：`15m`
- 样本：现有 `120d` 本地 cache
- 执行：`next-bar open -> 持有 8 根 15m bar`

### 只比较三档最小规则
1. `recent_sign_only`
2. `history_drift_only`
3. `recent_and_drift_agree`

### 先看哪 4 个指标
- `post_cost_return`
- `positive_asset_ratio`
- `trade_count`
- `time-pocket honesty`

### 当前更想回答的问题
不是“哪条收益最高”，而是：
- 如果 `recent_sign_only` 和 `history_drift_only` 表现几乎一样，那说明这条线更像 drift，不像可独立宣称的 recent-momentum alpha；
- 如果 `agree-only gate` 能明显减少烂交易、且成本后更稳，它才值得继续拿下一轮最小 stability budget；
- 如果三档都弱，那就应更快 `park`，避免又把 budget 扔进泛动量近义线。

## 6. 当前 hard verdict（仅限 source intake）
- **`Rank 36 / recent-return sign vs history-drift honesty gate`：允许进入下一轮最小 clean replication queue**

注意：
- 这还不是 `paper candidate`
- 也不是 `narrow paper pilot`
- 更不是说它已经证明了动量有效

它当前只是满足了 fresh intake 的最低条件：
1. 来源清楚；
2. `trade on / trade off` 能写清；
3. 不依赖外部新数据；
4. 能复用当前 crypto 15m cache 做便宜诚实检查。

## 7. 风险与保留意见
- 原论文是跨资产月频证据，不是 15m crypto；迁移的是**诚实门逻辑**，不是参数。
- 这条 intake 很可能最后给出的 hard verdict 仍是 `park / evidence pool`；但那也比继续空转或再磨 P3 continuity 更值钱。
- 如果下轮 clean replication 发现 `recent_sign_only` 只是 drift 的近义包装，就应尽快 park，不要再给它过多预算。

## 8. 来源
1. Huang, D., Li, J., Wang, L., & Zhou, G. (2020). *Time series momentum: Is it there?* Journal of Financial Economics, 135(3), 774-794.
   - DOI: https://doi.org/10.1016/j.jfineco.2019.08.004
   - Readable URL: https://www.sciencedirect.com/science/article/pii/S0304405X19301953
   - Working-paper mirror: https://ideas.repec.org/p/cuf/wpaper/717.html
