# 别把 limited attention 只读成机制论文：对 short-cycle crypto desk，更该先测的是「同窗累计收益 × path smoothness continuation」这条 raw alpha

- 时间：2026-04-25 23:16 UTC
- 主题类型：**raw alpha**
- 基础 alpha：**同样是过去一段时间的累计涨跌，若这段 move 不是由单根 jump 打出来，而是由多根小 bar 连续扩散出来，则后续更容易 continuation；反之，单次大冲击更容易 exhaustion / fade。**
- 是否可独立复现：**是**
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：**否**
- 主题标签：raw-alpha/trend/momentum/attention/path-shape/smoothness/jump-vs-diffusion/continuation/exhaustion/btc/eth/sol/binance-perpetual/15m/5m/1m/paper/ssrn/public-data

## 1. 这次看了什么
这轮主线看的是：

1. **Aleksi Pitkäjärvi (2022)**  
   **A Limited Attention Theory of Time Series Momentum**  
   - Venue: SSRN working paper  
   - DOI: <https://doi.org/10.2139/ssrn.4168092>  
   - Readable URL: <https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4168092>

2. **Zhi Da, Umit G. Gurun, Mitch Warachka (2014)**  
   **Frog in the Pan: Continuous Information and Momentum**  
   - Venue: *Review of Financial Studies*  
   - DOI: <https://doi.org/10.1093/rfs/hhu003>  
   - Readable URL: <https://doi.org/10.1093/rfs/hhu003>

这次不再把它读成“注意力有限，所以动量可能存在”这种解释型结论，而是直接翻成一条 desk 更能立刻测的 raw alpha：

> **同样过去 `1h/4h` 已经涨了（或跌了），后面该不该继续跟，不只看累计收益大小，还要看这段路是“很多小步慢慢走出来”，还是“单根大跳一下打出来”。**

## 2. 一句话核心结论
**对短周期 crypto，更值得先测的不是“过去涨了多少”，而是“这段上涨/下跌的路径形状”：smooth / diffused path 更像 continuation，jump-dominated path 更像 exhaustion 或至少更不稳定。**

## 3. 一句话说明它怎么证明
- **Pitkäjärvi (2022)** 从**有限注意力 / 信息扩散不完全**的机制出发，解释为什么价格不会一次性把信息吃完；
- **Da et al. (2014)** 则把这件事更具体地落成：**连续、小步、分散的信息流**比**一次性、显眼的大消息**更容易留下后续动量。

对我们来说，值钱的不是“注意力”三个字，而是一个**纯价格可计算 proxy**：`path smoothness`。

## 4. 为什么这轮值得写
前面 desk 已经积累了很多：
- `return sign / momentum rank`
- `jump / no-jump`
- `funding / OI / crowding`
- `leader-laggard`
- `post-shock continuation / fade`

但中间一直少一个很轻、很便宜、又能同时服务 trend 与 fade 的桥：

> **同样的累计收益，先分辨它是“扩散型趋势”还是“冲击型趋势”。**

这层东西的好处是：
1. **完全不依赖外部 attention 数据**；
2. 只用 `1m/5m/15m` OHLC 就能做；
3. 既能服务单币 TSMOM，也能服务 BTC→alts 跟随、XS momentum、event-follow-through；
4. 也能反过来给 mean reversion 当 veto：**如果前面的 move 很 smooth，别急着逆；如果前面的 move 很 jumpy，顺势要更保守。**

## 5. desk 化后的 base alpha
### 5.1 翻成人话
不是所有“过去 4 根 `15m` 一共涨了 2%”都一样。

两种完全不同：
- **Smooth path**：四根里大多同向，小涨小涨小涨推出来；
- **Jump path**：前三根没啥，最后一根突然猛拉 2%。

这两种在交易上不是一回事：
- 前者更像**信息慢慢扩散、市场还没完全消化**；
- 后者更像**短时拥挤 / 追单 / 事件冲击已经集中释放**。

所以更适合 desk 先测的不是裸 `past return`，而是：

> **`past return × path smoothness` 联合信号。**

### 5.2 最小可计算定义
以 `15m` 为主、`5m` 做更快版本：

设过去 `L` 根 bar 的累计收益为：
- `ret_L = close_t / close_{t-L} - 1`

定义几种简单的 `path smoothness` 代理：

1. **Sign agreement ratio**  
   - `same_sign_share = 同向子 bar 数 / L`
   - 越接近 `1`，说明这段路越连续

2. **Largest-bar dominance**  
   - `max_abs_bar / abs(sum_bar_returns))`
   - 越大说明越像“单根 jump 主导”

3. **Path efficiency / monotonicity**  
   - `abs(sum_bar_returns) / sum(abs(bar_returns))`
   - 越高说明噪声越少、路径越直

4. **Jump concentration**  
   - `top1_abs_bar / sum(topk_abs_bar)` 或 `top1_abs_bar / sum(abs(bar_returns))`
   - 用来区分“扩散推进”与“一根打完”

### 5.3 最小 raw alpha 版本
#### 版本 A：continuation long/short
- 若 `ret_L > q80` 且 `smoothness > q70` → 做多持有 `H` 根
- 若 `ret_L < q20` 且 `smoothness > q70` → 做空持有 `H` 根

#### 版本 B：exhaustion fade
- 若 `ret_L > q80` 且 `jump_dominance > q80` → 轻量做空 / 不追多
- 若 `ret_L < q20` 且 `jump_dominance > q80` → 轻量做多 / 不追空

真正值钱的是：
- **不是 continuation 或 mean reversion 二选一；**
- 而是用 path 把两者分流。

## 6. 它和当前短周期主线的关系
### 6.1 服务 trend / momentum
它可以直接接到：
- `BTC-confirmed alt TSMOM`
- `single-asset intraday momentum`
- `cross-sectional winners-minus-losers`
- `leader impulse → follower continuation`

最自然的增强方式就是：
- **只保留 smooth winner**；
- 对 jump winner 降权或延后入场。

### 6.2 服务 mean reversion / fade
对于：
- `shock fade`
- `jump reversal`
- `liquidation unwind`
- `overreaction mean reversion`

它可以做一个非常直接的 admission layer：
- **不是所有大涨/大跌都值得反手；**
- **只有 jump-dominated move 才更像值得反。**

### 6.3 服务 event-driven
如果把 funding boundary、listing、macro shock、stablecoin event 当 source event，`path smoothness` 也能补一层：
- 是**事件后慢扩散**，还是**事件后瞬时砸/拉完就没了**。

## 7. 为什么这条线对 `1m/3m/5m/15m` 友好
因为它只需要公开 OHLC，就能很快做最小实验：
- `15m` 主实验：过去 `4` 根 / `8` 根 → 未来 `2` 根 / `4` 根
- `5m` 快速版：过去 `12` 根 / `24` 根 → 未来 `3` 根 / `6` 根
- `1m` 高强度版：过去 `30` 根 / `60` 根 → 未来 `5` 根 / `15` 根

而且它天然兼容当前成本框架：
- 低频一点，可以偏 `15m`
- 高频一点，可以偏 `5m`
- 若 `1m` 太容易被费率打穿，就保留作解释层或 entry timing 层

## 8. 当前最诚实的定位
这篇东西现在最适合定位成：

- **主题类型：raw alpha**
- 但更准确地说，是一条 **raw alpha skeleton / router**：
  - `smooth path` 偏 continuation
  - `jump path` 偏 exhaustion/fade

也就是说，它不是一句“买入所有 smooth path”；
而是一个**同一底层变量可以同时服务两类策略**的信号骨架。

## 9. 下一步怎么测
### 实验 1：单币 continuation vs jump-fade 分桶
- 标的：`BTCUSDT / ETHUSDT / SOLUSDT`
- 频率：`15m`
- source window：过去 `4` 根 / `8` 根
- hold：未来 `1/2/4` 根
- 分桶：
  1. `high ret + high smoothness`
  2. `high ret + high jump_dominance`
  3. `low ret + high smoothness`
  4. `low ret + high jump_dominance`
- 看每桶未来均值收益、t 值、成本后 bps

### 实验 2：给现有 momentum 信号加 path veto
拿当前已有任一动量基线：
- baseline：按过去 `1h` 或 `4h` return 排名/定方向
- 增强：
  - `smoothness top bucket` 保留
  - `jump_dominance top bucket` 降权或剔除
- 比较：trade count、hit rate、net bps、左尾

### 实验 3：给现有 fade 信号加 jump admission
拿当前已有任一 mean-reversion / shock-fade 线：
- baseline：极端 return 后反手
- 增强：只在 `jump_dominance` 高分位才允许反手
- 比较：是否减少“趋势日里逆势抄底/摸顶”

### 实验 4：BTC lead → alt follow 里加 smooth/jump 区分
- source：BTC 过去 `60m`
- target：ETH/SOL/ADA 等未来 `15m~60m`
- 问题：
  - BTC 的上涨若是 smooth diffusion，alts 是否更容易跟？
  - BTC 若是 single-bar jump，alts 是否更像迟到追高、随后回吐？

## 10. 风险与失败方式
1. **路径指标和波动率高度相关**  
   需要控制 realized vol，避免只是换一种写法描述“低噪声趋势”。

2. **大 jump 有时恰好是信息刚开始被定价**  
   不能先验断言“jump 就一定反转”；更可能是：
   - majors 更容易 exhaustion
   - high-beta alts 在某些 pocket 反而 jump 后继续追随

3. **强依赖持有期**  
   `1 bar`、`2 bar`、`4 bar` 可能完全不同；
   很多这种路径类信号，边际只活在很短的 post-event 窗口。

4. **成本敏感**  
   若最后只剩 `1m` 层有效，可能会被手续费和滑点吃掉；
   因此第一版最好先看 `15m/5m`。

## 11. 我对这条线的判断
这轮最值钱的不是“limited attention 终于能交易了”，而是：

> **我们终于把“机制故事”翻成了一个不依赖外部 attention 数据、只靠价格路径就能测的 raw alpha 壳。**

它的优点不是直接 production-ready，
而是**足够轻、足够通用、足够适合先做 first verdict**。

如果 first probe 有东西，它后面可以长成三种方向：
1. `single-asset continuation filter`
2. `shock-fade admission layer`
3. `BTC→alt lead-lag path router`

## 12. 来源
1. **Pitkäjärvi, A. (2022).** *A Limited Attention Theory of Time Series Momentum*. SSRN.  
   DOI: <https://doi.org/10.2139/ssrn.4168092>  
   Readable URL: <https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4168092>

2. **Da, Z., Gurun, U. G., & Warachka, M. (2014).** *Frog in the Pan: Continuous Information and Momentum*. *Review of Financial Studies*, 27(7), 2171–2218.  
   DOI: <https://doi.org/10.1093/rfs/hhu003>
