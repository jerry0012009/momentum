# 别继续只盯 near-expiry settlement pocket：对 short-cycle desk，更该先补的是「Deribit-OKX 长天期 wing quote-gap × delta/DTE capped close-out」这条 raw alpha
- 时间：2026-04-12 05:18 UTC
- 类型：GitHub / repo source audit + public live probe
- 主题类型：raw alpha
- 基础 alpha：同一张 BTC 期权（same expiry / same strike / same C/P）在 Deribit 与 OKX 之间若出现可成交的 premium gap，做 `short rich venue / long cheap venue`，赌 quote gap 收敛；`delta cap` 与 `DTE cap` 只是 admission layer，不是 alpha 本体。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：options / relative-value / stat-arb / cross-venue / quote-gap / long-dated-wing / delta-cap / dte-cap / deribit / okx / btc / 1m / 3m / 5m / 15m
- 证据类型：工程证据（repo source audit）+ Deribit / OKX 公共 API live scan

## 1. 这次看了什么
这轮主看的是 GitHub 仓库 **Hudie / crypto_algo_trading**，重点读了：
- `strategy/catch_gap.py`
- `strategy/catch_large_gap.py`
- GitHub repo metadata

这份仓库很老，接口也还是 `OKEx` 年代，不适合直接拿来跑实盘；但它有一个对当前 desk 仍然很值钱的地方：**它把“同合约跨 venue premium gap 收敛”写成了完整策略壳，而不是只做监控面板。**

先把 **base alpha** 说清楚：
> **同 expiry / same strike / same option type 的 BTC option，本质上是同一份状态暴露；若 Deribit bid 明显高于 OKX ask，或反过来，就不是方向交易，而是 cross-venue relative-value convergence。**

和我们 3 月 26 日那篇 **近到期 OKX-Deribit call premium 收敛** 不同，这次更值得 intake 的不是 `settlement-window` 那个老 pocket，而是：
- repo 本身其实已经把 **delta / DTE / gap threshold** 写成 admission shell；
- 我这次 live scan 看到的残余 crossed-BBO，**几乎都不在近到期，而在长天期 call wing**；
- 所以当前更值得 desk 化的问题变成：
  **近到期 pocket 可能已经很干净，剩下的 edge 是否主要迁移到了 long-dated wing inventory dislocation？**

这不是 filter，不是 overlay，而是一条仍然能独立下单的 raw alpha；只是它的“最可能出现在哪里”变了。

## 2. repo 真正有价值的，不是旧 API，而是完整策略骨架

### 2.1 `catch_gap.py` 直接把 entry shell 写死了
源码核心触发条件在这几行：
- `v['deribit'][0] - float(v['okex'][2]) >= gap`
- `float(v['okex'][0]) - v['deribit'][2] >= gap`
- `timedelta <= t`
- `abs(delta) <= d`

也就是只在以下同时满足时触发：
1. **rich venue bid > cheap venue ask**，形成 crossed gap；
2. 剩余到期时间在允许区间内；
3. 绝对 delta 不超过上限；
4. gap 足够大，超过该 bucket 的最小门槛。

`catch_gap.py` 给的主触发梯度是：
- `gap >= 0.0025`, `|delta| <= 0.36`, `DTE <= 3d`
- `gap >= 0.0040`, `|delta| <= 0.33`, `DTE <= 6d`
- `gap >= 0.0055`, `|delta| <= 0.32`, `DTE <= 10d`
- `gap >= 0.0070`, `|delta| <= 0.31`, `DTE <= 15d`
- `gap >= 0.0090`, `|delta| <= 0.30`, `DTE <= 31d`

因为 BTC option premium 本身常以 BTC 计价，这套阈值可以直接读成：
**repo 只想做“至少 25~90 bps of underlier”的真实大 gap，而且只想做低 delta、较短期限的 contract。**

### 2.2 `catch_large_gap.py` 又额外给了一层长一点的壳
`catch_large_gap.py` 进一步放宽成：
- `gap >= 0.01`, `DTE <= 31d`
- `gap >= 0.03`, `DTE <= 93d`

这说明作者并不是只相信 near-expiry；他真正的思路更像：
> **同合约跨 venue gap 是 alpha 本体；近到期 / 低 delta / 大 gap 只是为了提升 fill quality 与降低残余风险。**

### 2.3 它连 sizing / risk / execution 顺序都给了
源码不是只报信号，还把完整执行顺序写出来了：
- `RISK_RATIO_CALL = 2`
- `RISK_RATIO_PUT = 4`
- `MAX_SIZE_PER_TRADE = 2`
- 仓位上限取以下几者最小值：
  - OKX 顶层可卖/可买量
  - Deribit 顶层可买/可卖量
  - 两侧账户保证金可承受量
  - 单笔最大 size cap
- 执行顺序默认是：**先买便宜腿，再逐档挂出贵腿**；若贵腿未完全成交，再取消余单。

这很关键，因为它说明这条线不是“想象中的理论 no-arb”，而是一个已经被拆成：
- entry
- direction-neutral hedge
- size clipping
- partial-fill handling
- risk-ratio margin control
的完整原型。

### 2.4 但源码不能原样信任
仓库里直接写了历史 API key / secret，而且 OKEx 接口与当前交易所命名都过时。对 desk 来说，正确读法不是“git clone 直接跑”，而是：
- **保留 alpha 逻辑**
- **重写 data / execution adapter**
- **重做 today’s venue mapping 与 fee model**

## 3. live scan：现在真正还会 crossed 的，不是 near-expiry，而是 long-dated wing
我用公开 API 做了一次最小 live scan：
- Deribit：`public/get_book_summary_by_currency?currency=BTC&kind=option`
- Deribit：`public/get_order_book`
- OKX：`/api/v5/public/instruments?instType=OPTION&uly=BTC-USD`
- OKX：`/api/v5/market/tickers?instType=OPTION&uly=BTC-USD`

并把 Deribit / OKX 上 **same expiry / same strike / same C/P** 的 BTC options 对齐，得到 artifact：
- `reports/artifacts/literature/crossvenue_option_gap_scan_summary_2026-04-12.csv`
- `reports/artifacts/literature/crossvenue_option_gap_scan_detail_2026-04-12.csv`

### 3.1 这次快照的关键数字
快照时间：`2026-04-12 05:14:41 UTC`

1. **552 个** matched instruments 里，只有 **15 个** 出现正的 crossed-BBO 候选。
2. 其中：
   - `11` 个是 **sell Deribit / buy OKX**
   - `4` 个是 **sell OKX / buy Deribit**
3. **max gap = 0.002 BTC premium points**（约 **20 bps of underlier**）
4. **median gap = 0.0005**（约 **5 bps of underlier**）
5. **0 / 15** 满足 repo 的主触发梯度；也就是按 repo 的原始 executable 口径，**今天没有一笔真正过线**。

### 3.2 残余 gap 的期限分布非常偏
按 DTE 分桶：
- `<=31d`：**2** 个，且最大 gap 只有 **0.0001**
- `32~93d`：**0** 个
- `94~180d`：**4** 个，最大 gap **0.0005**
- `>180d`：**9** 个，最大 gap **0.0020**

这组数字的含义很直白：
> **今天还会肉眼看到的 cross-venue option gap，基本已经不在 near-expiry；它主要躲到了 long-dated wing。**

### 3.3 top candidates 也印证了这一点
最大的几档都集中在 **2026-12-25** 这组 long-dated calls：
- `80k C`: gap `0.0020`, Deribit delta `0.4869`
- `85k C`: gap `0.0020`, Deribit delta `0.4237`
- `90k C`: gap `0.0015`, Deribit delta `0.3644`
- `95k C`: gap `0.0015`, Deribit delta `0.3114`
- `100k C`: gap `0.0010`, Deribit delta `0.2651`

反而 `<=31d` 的两个小口袋只有：
- `2026-04-24 84000 C`: gap `0.0001`
- `2026-04-13 70500 P`: gap `0.0001`

也就是说，**近到期这条线目前不像“还能做但要精调阈值”，更像“已经被市场磨得只剩噪声”。**

## 4. 这条 raw alpha 现在该怎么 desk 化
### 4.1 正确定位
- **raw alpha 本体**：same-contract cross-venue option premium convergence
- **不是本体的东西**：delta cap / DTE cap / liquidity gate / cost buffer
- **当前最合理角色**：event-driven relative-value alpha
- **短周期时钟的职责**：`1m` 扫描、`1m/3m` 进场、`5m/15m` 管 time-stop 与 inventory risk

### 4.2 当前更诚实的 entry / exit 版本
#### Entry
只在以下同时满足时开仓：
1. same expiry / same strike / same option type 可对齐；
2. `rich_bid - cheap_ask > fees + spread buffer + stale buffer + venue risk buffer`；
3. cheap 腿与 rich 腿顶层 size 都足够过最小名义金额；
4. 先不做极低流动性的极深虚值；第一版建议 `0.20 <= |delta| <= 0.55`；
5. DTE 先分桶做，不混：`0~7d / 8~31d / 32~93d / 94~365d`。

#### Exit
任一满足就平：
1. gap 回落到 close threshold；
2. 到达固定 time-stop（如 `10m / 30m / 60m`）；
3. 一侧 quote 消失或明显 stale；
4. 距离 expiry / settlement 太近，但 gap 还没收敛；
5. 对 long-dated wing，若 vega / skew shift 让 mark-to-market 明显脱离 quote-close 逻辑，则强制减仓。

### 4.3 Sizing
第一版别做“理论无风险大容量”幻想，直接按：
- `size_cap = min(cheap_ask_size, rich_bid_size, venue_margin_cap, MAX_SIZE_PER_TRADE)`
- 每个 expiry bucket 单独设总风险上限
- long-dated wing 与 near-expiry 分开记账

### 4.4 Risk
这条线最主要的风险不是 BTC 方向，而是：
- **单腿先成交、另一腿滑走**
- **wing quote 很稀，盘口 stale**
- **长天期合约的 vega / skew inventory 风险**
- **不同 venue 的保证金、持仓与强平逻辑差异**
- **名义 crossed 但真实 size 太小**

### 4.5 Cost
必须显式进模型：
- 两腿 taker / maker fee
- 盘口宽度
- 部分成交与冲击成本
- 资金占用与 venue haircut
- 若非秒级 close-out，还要考虑持仓期间的 surface move 风险

## 5. 为什么这轮仍然值得进池
这轮不是在写一个泛泛的 options 微结构综述，而是在回答一个更具体的问题：

> **repo 给的 same-contract cross-venue option arb 壳，今天还剩什么？**

当前答案很明确：
1. **base alpha 还在**，而且仍然是可独立复现的 raw alpha；
2. 但 **near-expiry pocket 当前非常干净**，至少这次 live snapshot 看不到能过线的票；
3. 残余 crossed quote 更像 **long-dated wing inventory dislocation**，而不是之前那种 settlement-window pocket；
4. 所以这条线不该丢掉，但也不该继续按 3 月那种近到期故事重复写；
5. 对当前 desk，更值钱的是把它分裂成两个研究对象：
   - `near-expiry settlement pocket`：是否已经基本死掉？
   - `long-dated wing dislocation`：是否存在更稳定但更低频的 quote-close pocket？

## 6. 下一步怎么测
只做最小版，不扩 scope：

### 6.1 先跑 7 天 live sidecar
每 `1m` 记录：
- Deribit / OKX matched contracts 的 bid/ask
- underlier / mark / delta
- DTE / strike / option type
- crossed gap / gap net of simple fee buffer

### 6.2 只做 4 个核心分桶
1. DTE：`0~7d / 8~31d / 32~93d / 94~365d`
2. abs(delta)：`0.10~0.20 / 0.20~0.35 / 0.35~0.55`
3. side：`sell Deribit / buy OKX` vs `sell OKX / buy Deribit`
4. moneyness：ATM / slight OTM / wing

### 6.3 只回答 3 个问题
1. **真正过成本的票到底主要在哪个 bucket？**
2. **near-expiry 是否已经接近 0 票，需要降级？**
3. **long-dated wing 的 crossed gap 是瞬时噪声，还是可复现 pocket？**

### 6.4 kill rule
若连续 7 天里：
- `repo-style executable hits ≈ 0`
- `net-of-fee crossed rate` 仍极低
- long-dated wing 也没有稳定的 close-out 成交条件

那就把这条线从前排 raw-alpha pool 降到 **options watchlist**，不要继续烧时间。

## 7. 一句话结论
> **这条线依然是 raw alpha，但当前市场给出的残余形态已经变了：近到期 same-contract quote-gap 基本干净，真正还会 crossed 的更像 Deribit-OKX 长天期 wing inventory dislocation。对 short-cycle desk，下一步不是重复写 settlement-window，而是老老实实验证“long-dated wing quote-close”到底是不是还活着。**

## 8. 来源
1. **Hudie. (2020). _crypto_algo_trading_. GitHub repository.**
   - Venue: GitHub
   - Repo URL: `https://github.com/Hudie/crypto_algo_trading`
   - Readable URL: `https://github.com/Hudie/crypto_algo_trading`
   - GitHub metadata used: created `2020-08-14`, updated `2026-03-29`, stars `55`
   - 关键文件：
     - `https://raw.githubusercontent.com/Hudie/crypto_algo_trading/master/strategy/catch_gap.py`
     - `https://raw.githubusercontent.com/Hudie/crypto_algo_trading/master/strategy/catch_large_gap.py`

2. **Alexander, C., Chen, X., Deng, J., & Wang, T. (2024). _Arbitrage opportunities and efficiency tests in crypto derivatives_. Journal of Financial Markets.**
   - Venue: *Journal of Financial Markets*
   - DOI: `10.1016/j.finmar.2024.100930`
   - Readable URL: `https://doi.org/10.1016/j.finmar.2024.100930`
   - 用途：给“crypto derivatives 无效率口袋会收缩、但不会完全消失”这条判断提供近年的学术地基。

3. **本轮 public live probe 实际使用的公开接口**
   - Deribit instruments / book summary / order book:
     - `https://www.deribit.com/api/v2/public/get_instruments`
     - `https://www.deribit.com/api/v2/public/get_book_summary_by_currency`
     - `https://www.deribit.com/api/v2/public/get_order_book`
   - OKX public instruments / tickers:
     - `https://www.okx.com/api/v5/public/instruments`
     - `https://www.okx.com/api/v5/market/tickers`

4. **本轮 artifact**
   - `reports/artifacts/literature/crossvenue_option_gap_scan_summary_2026-04-12.csv`
   - `reports/artifacts/literature/crossvenue_option_gap_scan_detail_2026-04-12.csv`
