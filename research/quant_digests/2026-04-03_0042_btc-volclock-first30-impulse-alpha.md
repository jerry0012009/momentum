# 别把这篇 BTC intraday TSMOM 只读成“24h 市场也有 open/close”：对 short-cycle desk，更该先测的是「volume-clock 首 30m 极端冲击 × 同向续行 30~60m」这条单币 raw alpha

- 主题类型：raw alpha
- 基础 alpha：BTC 在“伪开盘”首 30 分钟出现**极端成交量 + 极端方向冲击**时，随后 30~60 分钟仍有同向续行；若不做极端筛选，边际很快被成本吃掉
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1) 为什么这轮值得 intake
先回答一句：这篇东西的 **base alpha** 是什么？

> **base alpha = 单币 BTC 的会话起始冲击续行。**
> 不是“时间段解释”、不是“市场微观结构综述”，而是一个可直接写成策略的 directional raw alpha：观察某个伪开盘窗口的首 30 分钟，如果这 30 分钟本身就是高成交/高波动且方向明确，则后续 30~60 分钟更容易沿原方向继续走。

这比把论文 headline 机械翻成“first half-hour predicts last half-hour”更适合我们 desk，因为我们真正关心的是：
1. **能不能在 `5m/15m` 上直接下单；**
2. **是不是必须加 regime/filter 才能活过成本；**
3. **最小实验是不是今天就能做。**

答案是：**可以，而且关键不是“所有首 30m 都追”，而是只追“极端量 + 极端冲击”的首 30m。**

---

## 2) 来源与可信度

### 论文
- **Authors**: Dehua Shen, Andrew Urquhart, Pengfei Wang
- **Year**: 2021 online / 2022 print
- **Title**: *Bitcoin intraday time series momentum*
- **Venue**: *Financial Review*, Vol. 57, Issue 2, pp. 319–344
- **DOI**: `10.1111/fire.12290`
- **Readable URL**: <https://doi.org/10.1111/fire.12290>
- **Repo URL**: N/A

### 本轮实际可读取到的证据层级
- **Crossref metadata**：作者、期刊、卷期页码、online/print 时间可确认
- **OpenAlex abstract**：可确认论文核心结论
- **本地 public-data portability probe**：用 Binance USDⓈ-M `BTCUSDT` `15m` 数据做 desk 口径最小实验

### 需要先说清的限制
这轮**没有拿到全文正文**，所以论文细节（例如 volume-clock 的精确定义、资产配置实现细节）我不把它当已完全复原；本笔记更像：
- **论文 abstract 给出方向**
- **本地 public-data probe 验证 desk 可迁移部分**

换句话说，**这是高相关 intake，不是 production 认证。**

---

## 3) 论文到底说了什么（abstract-level）
OpenAlex 抽到的摘要核心句子有 4 个：

1. Bitcoin 24 小时交易，没有传统股票那种清晰 open / close；
2. 作者用 **trading volume 作为 market trading time 的 proxy**；
3. 论文发现 **first half-hour positively predicts the last half-hour return**；
4. **最高成交量或最高波动的 first trading sessions**，可预测性最强；且这种 intraday momentum 更像是 **liquidity provision** 驱动，而不是 late-informed trading。

把这段翻成人话：
- BTC 虽然没有交易所开收盘，但市场还是会自己形成“像开盘一样重要”的时段；
- 真正值得看的是**最活跃、最有冲击的早段**；
- 如果一开始就走得很猛，而且量也大，这种 move 有更高概率不是纯噪音，而是会继续传导。

---

## 4) 对 short-cycle desk 的重构：别照抄 headline，先拆成可交易部件
### 4.1 论文 headline 版本
- “first half-hour predicts last half-hour”

这个 headline 如果直接照搬，问题有两个：
1. **持有到 session 最后半小时太慢**，未必是我们最优的短周期持有口径；
2. 不加筛选就全追，极容易被成本吃掉。

### 4.2 desk 更该先测的版本
对我们更有用的重构是：

> **raw alpha：会话首 30m 的极端 directional impulse，会在接下来 30~60m 延续。**

对应拆解：
- **alpha 本体**：首 30m 同向续行
- **regime/filter**：必须要求首 30m 同时满足高成交量 / 高波动 / 大实体冲击中的至少 2 个
- **execution**：只在首 30m 结束后入场，不猜方向，不抢第一腿
- **risk**：30m / 60m timeout 为主，避免把 intraday 冲击策略硬拖成日内摆动仓

这就不再是“论文里的时间结构趣闻”，而是一个完整的 `entry/exit/filter/cost` 骨架。

---

## 5) 本地最小 portability probe（Binance USDⓈ-M `BTCUSDT` `15m`）

### 5.1 数据与口径
- **数据源**：本地已缓存 Binance USDⓈ-M `BTCUSDT` `15m` perp K 线
- **样本**：`2021-03-20 03:30 UTC` → `2026-03-19 03:15 UTC`
- **文件**：
  - 原始 K 线：`reports/artifacts/scout_rank32b_slope_floor_continuation_15m/perp_cache/BTCUSDT__1825d__15m__perp.csv`
  - 本轮事件明细：`reports/artifacts/quant_digests/btc_intraday_tsmom_20260403/session_events.csv`
  - 本轮汇总：`reports/artifacts/quant_digests/btc_intraday_tsmom_20260403/key_configs.csv`

### 5.2 会话定义（desk translation）
论文原文是 volume-clock 的“market trading time”，但全文没拿到，所以这轮先做一个**诚实而保守的 desk translation**：
- 把一天切成 `00/08/16 UTC` 三个 **8h funding-style sessions**；
- 每个 session 的**前两根 `15m` bar = 首 30m**；
- 在首 30m 结束后决定是否入场；
- 测：
  - 首 30m 后继续拿 **30m / 1h / 2h**；
  - 以及更接近论文 headline 的 **session 最后 30m**。

### 5.3 首先看：不加筛选时，edge 很薄
如果把所有 session 的首 30m 都拿来追：
- **gross** 确实有一点点正边际；
- 但进到 realistic friction 后，**很快被吃穿**。

也就是说，论文里“有 intraday momentum”这句话，**对交易不等于“直接无脑追”。**

### 5.4 真正有用的是极端 gate
我做了 rolling 120-session 的分位筛选，发现最像 desk 可交易版本的是：

#### A. `first30m volume >= rolling 95%` 且 `|first30m return| >= rolling 95%`
- **同向追 30m**
  - trades: `120`
  - gross avg: `+11.84 bps/trade`
  - gross hit-rate: `55.8%`
  - gross Sharpe: `4.25`
  - **若按 `4 bps/side` 计**：
    - net avg: `+3.83 bps/trade`
    - net hit-rate: `50.8%`
    - net Sharpe: `1.38`
    - compounded return: `+4.17%`

- **同向追 1h**
  - trades: `120`
  - gross avg: `+12.29 bps/trade`
  - gross hit-rate: `51.7%`
  - gross Sharpe: `3.05`
  - **若按 `4 bps/side` 计**：
    - net avg: `+4.28 bps/trade`
    - net hit-rate: `47.5%`
    - net Sharpe: `1.06`
    - compounded return: `+4.17%`

#### B. `first30m range >= rolling 95%` 且 `first30m volume >= rolling 95%`
- **同向追 30m**
  - trades: `176`
  - gross avg: `+10.08 bps/trade`
  - gross hit-rate: `53.4%`
  - gross Sharpe: `3.15`
  - **若按 `4 bps/side` 计**：
    - net avg: `+2.07 bps/trade`
    - net Sharpe: `0.65`

#### C. 只用 `volume >= rolling 95%`
- **同向追 1h**
  - trades: `279`
  - gross avg: `+9.44 bps/trade`
  - **但按 `4 bps/side` 计只剩 `+1.43 bps/trade`，Sharpe 也明显掉到 `0.37`**

### 5.5 这组数怎么读
关键不是“paper 对不对”，而是：

1. **方向上，paper 的 high-volume / high-volatility 版本确实能 transfer 到 BTC perp `15m`；**
2. **但只有在非常极端的首 30m 冲击下才够厚；**
3. **全样本追首 30m continuation 没法活过成本；**
4. 真正像 production 候选的是：
   - **极端 first30 impulse 才开仓**；
   - **30m~1h 短持有**；
   - 尽量压低执行成本，最好争取 maker / queue-aware 版本。

---

## 6) 这条 alpha 的最小策略骨架

## 6.1 Entry
在每个 `8h` session：
1. 观察前两根 `15m` bar；
2. 计算：
   - `ret_30m = close_t2 / open_t1 - 1`
   - `vol_30m = sum(volume)`
   - `range_30m = max(high)/min(low)-1`
3. 若满足：
   - `sign(ret_30m) != 0`
   - `vol_30m >= rolling_q95(vol_30m, 120 sessions)`
   - `abs(ret_30m) >= rolling_q95(abs(ret_30m), 120 sessions)`
4. 则在第 3 根 bar 开盘按 `sign(ret_30m)` **同向入场**。

## 6.2 Exit
两个最小版本都值得先测：
- **版本 A：固定持有 30m**（更纯的冲击续行）
- **版本 B：固定持有 1h**（给 move 一点扩散时间）

## 6.3 Sizing
建议第一轮别做复杂 Kelly：
- 每笔固定风险预算 `r`
- 仓位按最近 24h 的 realized vol 做简单 inverse-vol scaling
- 若同日已出现 1 笔同方向失败，后续同类信号减半

## 6.4 Risk
- 单笔 hard stop：`0.8 ~ 1.0 x first30m range`
- 若入场后下一根 bar 立即完全吞没首 30m 实体，直接平
- 同一 session 最多 1 笔，避免把事件冲击策略做成连续加仓

## 6.5 Cost
这条策略对成本很敏感：
- **8 bps round-trip 以上基本只剩极窄 edge**；
- 若能做到更低成交成本（maker、rebate、低冲击进场），edge 才更像样。

---

## 7) 它服务于哪个 raw alpha 家族
这是个很清楚的家族归属：

- **主家族**：`trend / momentum / directional continuation`
- **共享 gate**：`volume shock / volatility shock / impulse size`
- **可扩展方向**：
  - 加 `OI` / `funding` 做 crowding veto
  - 加跨市场 lead（Coinbase/ETF/Asia venue）做更强确认
  - 加 `1m/5m` execution shell，减少吃单成本

所以这不是“单篇论文的时间结构趣闻”，而是可以直接并进我们现有 directional alpha 池的一条 **event-style momentum shell**。

---

## 8) 与当前 desk 的关系
这条东西和我们现在的短周期研发是直接相连的：
- 和一般 EMA / breakout 不同，它不是持续持仓趋势，而是**会话开头冲击事件**；
- 和纯 microstructure OFI 不同，它只用 OHLCV 就能做最小实验；
- 和慢频日内 seasonality 不同，它强调的是**极端首 30m 冲击**，不是固定时间段平均效应。

更直白地说：

> 如果我们需要一个“今天就能在 `15m/5m` 上最小复现”的 BTC directional intake，这条比继续泛泛写 open/close seasonality 更值。

---

## 9) 下一步怎么测
这部分必须明确，不然 digest 只剩观点。

### Step 1：把 `15m` signal 改成 `5m` execution
- signal 仍用首 30m 冲击判定；
- 但入场改用第 `7~9` 根 `5m` 内的 pullback / micro pullback；
- 目标：把 round-trip cost 从 taker 版压到更低。

### Step 2：把 gate 从 2 个扩成 4 个做 honest ablation
最该加的两个：
- `first30m signed volume imbalance proxy`
- `first30m open-interest delta`

看是否能把：
- trades 维持在 `>80`，同时
- net avg 提升到 `>5 bps/trade @ 4 bps/side`。

### Step 3：做 session 定义敏感性
目前是 `8h funding-style session`，下一轮应同时测试：
- `UTC day`
- `Asia / Europe / US` 三段会话
- `volume-ranked pseudo-open`

也就是更接近论文原始 volume-clock 的定义，而不是只用 funding-session 近似。

### Step 4：加 market-state split
论文说 downturn 阶段更强；所以应补：
- BTC 在 `4h/1d` 下行 regime 时，这条边际是否更厚；
- 若是，则把它升格成 **bear-market directional playbook** 组件，而不是全时段常开策略。

---

## 10) 结论
这篇 paper 真正对我们有价值的，不是“BTC 也有 intraday TSMOM”这句 headline，而是下面这句更交易化的翻译：

> **BTC 没有官方开盘，但市场会自己制造“伪开盘”；而只有当这个伪开盘的首 30 分钟同时出现极端量和极端方向冲击时，后续 30~60 分钟的同向续行才厚到值得测。**

因此，这轮我会把它归类为：
- **主题类型**：raw alpha
- **基础 alpha**：`first30m extreme impulse continuation`
- **当前 verdict**：**可进研究池，但必须带极端 gate；不带 gate 不值得上生产候选。**

---

## 参考链接
- DOI / 文章页：<https://doi.org/10.1111/fire.12290>
- Crossref metadata：<https://api.crossref.org/works/10.1111/fire.12290>
- OpenAlex metadata / abstract：<https://api.openalex.org/works/https://doi.org/10.1111/fire.12290>
