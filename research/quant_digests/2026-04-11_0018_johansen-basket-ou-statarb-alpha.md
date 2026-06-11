# 别把这份 2026 GitHub stat-arb repo 只读成日频组合实验：对 short-cycle desk，更该先测的是「rolling Johansen basket admission × strongest-basket OU fade」这条 raw alpha
- 时间：2026-04-11 00:18 UTC
- 类型：仓库
- 主题类型：raw alpha
- 基础 alpha：`cointegrated basket spread mean reversion / stat-arb` —— 不是赌单币涨跌，而是赌**多资产协整篮子 spread 偏离会向长期均衡回归**；OU alpha 负责把“偏得有多远”翻译成可交易信号
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / stat-arb / pairs-plus / basket / johansen / cointegration / ou / mean-reversion / regime-filter / risk-parity / strongest-basket / market-neutral / binance / perpetual / 15m / 5m / repo / public-data / cost / risk
- 证据类型：2026 GitHub repo source audit（`README.md` + `labs/research.ipynb` embedded outputs）+ Binance USDⓈ-M 公共 `15m/5m` portability probe

## 1. 这次看了什么
这次选的是 **Sujith Kamme (2026), _Crypto Statistical Arbitrage via Cointegration and Regime Filtering_** 这个 GitHub repo，核心审计对象是：
- `README.md`
- `labs/research.ipynb`
- `artifacts/crypto_pipeline_detailed.svg`

我这次不是把它当“又一个协整 repo”略过，而是先问一句：
**它的 base alpha 到底是什么？**

答案是清楚的：
**base alpha 就是“协整 crypto basket spread 的均值回归 / OU fade”。**

所以它不是纯 filter，不是纯 risk overlay，也不是“先有别的主信号，它来帮你 veto”。
它本身就是一条**可独立落地的 market-neutral / relative-value / stat-arb raw alpha**。

而且它和当前 digest 池里常见的 BTC/ETH 单 pair 或 copula pair 也不完全一样：
- 这里交易对象不是单 pair；
- 它允许 **2–4 资产 basket**；
- admission 核心不是简单相关性，而是 **Johansen cointegration**；
- 信号不是固定 z-score，而是 **OU mean-reversion speed × standardized displacement**；
- 外层再包 **regime filter + bucketed sizing + risk parity**。

换句话说，它更像一套**完整的 basket stat-arb 壳子**，而不是一条 pair 小技巧。

## 2. 先回答：这篇东西的 base alpha 是什么？
一句话：
**base alpha = 多资产协整篮子的 spread 在短期偏离后，按 OU 速度向均衡回归。**

翻成人话：
- 先挑几只价格关系长期绑得比较紧的币；
- 用 Johansen 方法给它们配一组权重，压成一条 spread；
- 如果这条 spread 偏得太远，但统计上仍像“会回来”的东西，就做反向；
- 赌的不是方向，而是**相对价值回归**。

所以它的归类是：
- `raw alpha`：**是**
- 方向属性：**双向 / market-neutral / relative-value**
- 不是纯 regime，不是纯 filter，也不是只适合作为 shared overlay。

## 3. repo 里真正值钱的，不是“协整”两个字，而是这 4 层策略壳
## 3.1 第一层：basket discovery 不是固定 pair，而是 2–4 资产组合
repo README 直接写了：
- **2–4 asset baskets**
- **Johansen basket + OU + regime filter + risk parity**
- **365-day train / 60-day test / 8 folds walk-forward**

这比很多“固定 pair + zscore”仓库更接近 live research：
- 市场不是永远只给你一对稳定 pair；
- 真正的 relative-value 关系可能要到 3 条腿才更干净；
- basket 化后，能把某个共同因子暴露拆得更细。

## 3.2 第二层：admission 不是“相关高就上”，而是四重筛选
从 notebook 输出能看到，repo 不是只跑 Johansen 就交易，而是一路筛：
- cointegration
- ADF stationarity
- variance ratio
- half-life + stability
- predictability

例如 notebook 最后汇总阶段显示：
- **155 total → 10 passed thresholds**
- 再做 diversify 后，最终只留 **4 baskets**

这点很重要，因为它明确告诉我们：
**真正的 alpha 不在“找到很多 basket”，而在“肯留下来的 basket 非常少”。**

## 3.3 第三层：信号不是裸 z-score，而是 OU alpha
notebook 里 `compute_ou_alpha_point()` 的逻辑非常清楚：
- 先估计 half-life / kappa；
- 若 half-life 不在可交易区间，直接把 alpha 归零；
- 再用最近窗口的均值与波动，把 spread 当前位置标准化；
- 最后得到 `|kappa| * (mu - current_spread) / sigma` 形式的 OU alpha；
- 并做 `clip` 与 `deadband`。

对应参数我审到的关键值包括：
- `MIN_HALF_LIFE = 2`
- `MAX_HALF_LIFE = 15`
- `HL_WINDOW = 120`
- `REGIME_WINDOW = 30`
- `ALPHA_CLIP = 3.0`
- `ALPHA_DEADBAND = 0.10`

翻成人话就是：
**它不只问“偏了多少”，还问“这东西平时回得快不快、现在这次偏离够不够值得做”。**

## 3.4 第四层：执行层不是连续抖仓，而是 sticky buckets
repo 最让我愿意继续往下拆的，是 `compute_bucketed_positions()` 这层：
- alpha 落到不同 bucket 才变更仓位；
- `|alpha|` 掉到 exit threshold 以下就平；
- alpha 翻符号就平；
- 同 bucket 内不反复抖仓。

notebook OOS 里最终用的是：
- **Buckets：`[(0.08, 0.5), (0.1, 1.0)]`**
- **exit threshold：`0.02`**
- **tcost：`20 bps`**

这件事对 short-cycle 非常关键：
**如果你把 OU alpha 直接连续映射成仓位，很多理论 edge 会死在换手里；sticky bucket 是这里真正有工程含量的一刀。**

## 4. repo 原始结果里，最值得记住的数据点
### 4.1 walk-forward 主结果：先证明它不是玩具
notebook 输出的 walk-forward 总结：
- **WF Sharpe：`1.440`**
- **Cumulative return：`40.08%`**
- **Max drawdown：`-16.61%`**
- **8 / 8 folds 有交易**

这说明 repo 至少给的是一条**完整且能滚动训练/测试**的策略骨架，不是静态样本内演示。

### 4.2 最终精选 4 篮子后的 OOS 结果更像“可部署壳”
notebook 最后对精选 basket 做 bucketed + risk-parity OOS，结果是：
- **Gross Sharpe：`1.953`**
- **Net Sharpe：`1.764`**
- **Net cumulative：`5.61%`**
- **Max drawdown(net)：`-1.38%`**
- **Win rate(net)：`72.2%`**
- **Entry events：`9`**
- **Annual turnover：`7.05x`**
- 成本假设：**`20 bps`**

这组数字的意义，不是说我们可以直接照抄到 intraday perp；
而是说它已经把：
- admission
- alpha
- exit
- sizing
- cost
- diversification

这些完整链条都写出来了。

## 5. 对当前 desk 最有价值的，不是原样搬 daily，而是拆成更适合 `15m/5m` 的旁支
如果你把这个 repo 生搬硬套成“多 basket 同时跑 + 风险平价 + 较慢 hold”，很可能会太钝。

但它里面有一个非常适合当前 desk 的旁支：
**rolling Johansen basket admission × strongest-basket OU fade**。

也就是：
1. rolling formation window 找 basket；
2. 保留通过 Johansen + ADF + VR + half-life 的候选；
3. 不急着同时部署很多篮子；
4. 每个短交易窗只先上**最强那一个**；
5. 用 OU alpha 做 bucketed fade；
6. regime 坏掉就 flat。

这条旁支仍然服务同一个 raw alpha：
**basket spread mean reversion / stat-arb**。

## 6. 我做的 portability probe：把它压到 Binance USDⓈ-M `15m/5m`
### 6.1 probe 口径
我做的不是 full faithful replication，而是一个 desk-friendly 最小实验：
- 数据：Binance USDⓈ-M 公共 klines
- 资产：`ETH / SOL / XRP / ADA / DOGE / LINK / AVAX`
- `15m`：**14 天 formation + 2 天 trading**
- `5m`：**7 天 formation + 1 天 trading**
- admission：
  - Johansen rank = 1
  - ADF `p < 0.05`
  - variance ratio `< 1`
  - half-life 落在 `[2, 64] bars`
- 信号：formation 估的权重固定到 trade window，做 OU-style spread fade
- regime veto：rolling vol 爆掉或 rolling ADF 明显转坏时强制 flat
- 成本：简化按 **`4 bps`/side** 计

此外我专门比较了：
- **top-1 strongest basket**
- **top-2 baskets**
- **top-3 baskets**

因为我怀疑：
**short-cycle 上，“先求准、后求多”比“先分散”更重要。**

### 6.2 结果：`15m` 有像样 pocket，`5m` 还不行
本地 probe 产物：
- `reports/artifacts/literature/2026-04-11_johansen-basket-ou_portability_probe.json`
- `reports/artifacts/literature/2026-04-11_johansen-basket-ou_probe_windows.csv`
- `reports/artifacts/literature/2026-04-11_johansen-basket-ou_probe_details.csv`

#### `15m` strongest-basket only（top-1）
- **6 / 6 windows 有候选且有部署**
- **total net：`+232.8 bps`**
- **cum return：`+2.36%`**
- **max drawdown：`-0.80%`**
- **total entries：`8`**
- **active bar share：`18.2%`**

几个重复出现的 basket：
- `ADAUSDT_DOGEUSDT`
- `XRPUSDT_DOGEUSDT_LINKUSDT`
- `ETHUSDT_ADAUSDT_AVAXUSDT`

#### 同一口径下，越想“组合化”，越容易把 edge 稀释掉
- `15m top-2`：**`+85.8 bps`**
- `15m top-3`：**`-15.5 bps`**

这点我觉得非常关键：
**repo 日频上“精选 4 篮子 + risk parity”是成立的，但压到 intraday 后，第一反应不该是“复制更多篮子”，而该是“先抓最强那个 basket”。**

#### `5m` strongest-basket only
- **total net：`-41.0 bps`**
- **cum return：`-0.41%`**
- **max drawdown：`-2.22%`**
- **total entries：`38`**

翻成人话：
**这个思路在当前简化版上，`15m` 还能看，`5m` 已经明显更像被噪音和换手打坏。**

## 7. 这次 probe 最重要的判断，不是“repo 能不能搬”，而是“哪一支能搬”
我这轮结论不是“整个 repo 可以原样压缩到 `5m/15m`”。

更准确地说：
### 7.1 可以保留的，是 raw alpha 主体
也就是：
**Johansen basket admission + OU spread fade**

这条本体在 short-cycle 仍然说得通，因为：
- 它抓的是 relative-value 偏离；
- 不依赖方向行情；
- 可以天然做成 market-neutral；
- 与当前单 pair 库存不完全重复。

### 7.2 需要降并发的，是组合层
repo 日频版本靠多篮子 + risk parity；
但我的 `15m` probe 显示：
- strongest one：最好
- 扩到 two：明显变差
- 扩到 three：已经快没 edge

所以 intraday 第一版更像：
**single-best-basket book**，而不是 portfolio-of-baskets。

### 7.3 暂时不该硬上的，是 `5m` alpha 主体
从这个 probe 看：
- `5m` 交易次数暴增；
- drawdown 也更难看；
- 说明 basket OU 这套更像 **`15m` first lane**；
- `5m` 更适合先做 execution layer、confirm layer，或者只在 `15m` 信号触发后做 finer entry。

## 8. 为什么它和当前项目不撞题，但又刚好能补仓
已有 digest 里，pairs / stat-arb 很多是：
- 单 pair
- 动态 hedge ratio
- copula pair
- ratio spread
- Hurst pocket

这份 repo 的新增价值在于：
### 8.1 它把 pair 提升成了 basket
pair 容易被单一共同因子污染；
3-leg basket 往往更接近“真正的相对价值残差”。

### 8.2 它把 admission 写得比“协整就做”更完整
Johansen 只是第一关，后面还有：
- ADF
- VR
- half-life
- stability
- predictability

这更适合作为 research funnel，而不是一次性固定参数。

### 8.3 它天然允许以后接别的 overlay
这个壳子以后很好接：
- funding/basis crowding veto
- liquidity veto
- event window blacklist
- basket turnover cap
- maker-first execution

所以它不只是一个“新 pair 变种”，而是一个**可继续生长的 raw alpha 容器**。

## 9. 策略拆解（必填）
- 方向属性：**双向 / market-neutral / relative-value / stat-arb**
- 基础 alpha：**cointegrated basket spread 会向均衡回归，OU speed 决定偏离是否值得做**
- regime：
  - basket 在 formation 窗里必须仍像可逆 spread
  - half-life 不可太慢
  - rolling ADF / rolling vol 变坏就降级或 flat
- filter / veto：
  - Johansen rank ≠ 1 不做
  - ADF 不过不做
  - VR 不过不做
  - half-life 不在交易区间不做
  - 可再加 funding / 事件 / 深度 veto
- risk / sizing / execution overlay：
  - 先从 strongest-basket only 开始
  - bucketed sizing 而不是连续抖仓
  - 并发数上限建议先 `1 → 2`，不要直接 portfolio 化
  - 成本必须按 taker / maker 分层重测

## 10. 风险与保留意见
- 这次 portability probe **不是** repo 的 full faithful replication；
  - 我压缩了 formation / trade horizon；
  - 简化了 regime 与成本模型；
  - 没把 repo 全套 risk parity 原样搬进 intraday。
- `15m` probe 样本还很短，年化 Sharpe 看起来高，但**不能当真值**；
  - 更该看的是：
    - strongest basket 优于多 basket
    - `15m` 明显好于 `5m`
- 当前 probe 只用少量 liquid majors / alts；
  - 真正上线前要扩到更完整 perp universe
- 这条线依然怕：
  - 结构性 re-pricing
  - 事件跳空
  - funding / basis 突变
  - 流动性断层

## 11. 下一步怎么测
### 11.1 先做 faithful intraday transfer
把 repo 的核心结构更完整地搬到 perp：
- universe 扩到 `15–30` 个 liquid USDT-M perp
- formation / trade 改成多个组合：
  - `14d/2d`
  - `21d/3d`
  - `21d/7d`
- bucket 与 exit threshold 按 `15m` 单独重扫
- 并发数显式扫：`1 / 2 / 3`

### 11.2 把 `15m` 定成 first lane，`5m` 只做 execution layer
优先测试：
- `15m` 产生 admission + alpha
- `5m` 只负责：
  - 更细进场
  - spread 回补后更早落袋
  - maker/taker 切换

### 11.3 把“是否组合化”当成单独实验，而不是默认设定
这轮已经给了一个很明确的工程信号：
**intraday 上，多 basket 并发不是默认更好。**

所以单独做：
- strongest only
- strongest + second-best
- full eligible portfolio

比较：
- post-cost expectancy / trade
- turnover
- overlap exposure
- drawdown clustering

### 11.4 最该先补的 live 风控
1. 单 basket 最大持有时长
2. 事件窗 blacklist
3. funding/basis 异常 veto
4. 单资产重复暴露上限
5. 执行时的 maker-first / adverse-selection 过滤

## 12. 来源
- Author: **Sujith Kamme**
- Year: **2026**
- Title: **Crypto Statistical Arbitrage via Cointegration and Regime Filtering**
- Venue: **GitHub repository / notebook research project**
- DOI: **无**
- Readable URL: `<https://github.com/sujith-kamme/statistical-arbitrage-crypto>`
- Repo URL: `<https://github.com/sujith-kamme/statistical-arbitrage-crypto>`
- Audited local clone: `/tmp/statistical-arbitrage-crypto`
- Audited files:
  - `/tmp/statistical-arbitrage-crypto/readme.md`
  - `/tmp/statistical-arbitrage-crypto/labs/research.ipynb`
  - `/tmp/statistical-arbitrage-crypto/artifacts/crypto_pipeline_detailed.svg`
- Latest audited commit:
  - `780a6c41402645c0187d3d535b5745f96784d551`
  - `2026-04-08 19:23:57 -0700`
- Local probe artifacts:
  - `/root/clawd/jerry/momentum/reports/artifacts/literature/2026-04-11_johansen-basket-ou_portability_probe.json`
  - `/root/clawd/jerry/momentum/reports/artifacts/literature/2026-04-11_johansen-basket-ou_probe_windows.csv`
  - `/root/clawd/jerry/momentum/reports/artifacts/literature/2026-04-11_johansen-basket-ou_probe_details.csv`

## 13. 一句话带走
**这份 repo 最值得 desk 先复现的，不是“多篮子日频 risk parity”整套外壳，而是里头那条更适合 intraday 的 raw alpha 主体：rolling Johansen basket admission × strongest-basket OU fade；从当前快检看，它更像 `15m` 的第一车道，而不是 `5m` 的主信号。**
