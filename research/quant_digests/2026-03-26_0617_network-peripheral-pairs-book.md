# 别把 pairs 继续只卷 cointegration p-value：这篇 2025 Nature 新论文更该先测的是「peripheral same-community pair book」
- 时间：2026-03-26 06:17 UTC
- 类型：2025 Nature 开放获取论文 + Binance Futures 公共 `1h/15m` 网络代理最小快检
- 主题类型：raw alpha
- 基础 alpha：cointegrated / stable spread 的 market-neutral mean reversion（long cheap leg / short rich leg）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/network/peripheral/community/portfolio-construction/cointegration/hurst/1h/15m/5m/binance/perpetual/paper
- 证据类型：论文证据 + 本地公共数据网络代理快检

## 1. 这次看了什么
先回答 base alpha：**这篇东西的 base alpha 不是“网络结构本身”，而是很标准的 pairs spread mean reversion。**

真正新东西在于：作者不是再卷“哪一对 cointegration p-value 最低”，而是问 **这些 pair 放进同一本 book 之后，会不会其实在偷偷共振、传染、一起炸？**

主论文是 **Mar Grande, Javier Borondo (2025), _Embedding pairs trading in market networks: a network science approach to portfolio construction_, Humanities and Social Sciences Communications**。它用 Binance 大样本小时线，把“pair 选得像不像同一社区、是不是处在网络外围、会不会跨社区当 weak-tie 桥”直接拉进 pairs 组合构建。对我们 desk 来说，最值钱的不是把 pairs 再包装成 network science 故事，而是把一个老问题说透：**pairs alpha 不是只看单对均值回归，还要看 pair 和 pair 之间的隐藏共振风险。**

## 2. 核心结论
- **一句话核心结论：** 这篇论文给的不是新 alpha 家族，而是 pairs raw alpha 的更诚实 book-construction 规则：**优先做 peripheral、且尽量留在 same-community 的 pair；少碰跨社区 weak-tie。**
- **一句话它怎么证明：** 作者用 `472` 个 Binance 代币、`2021-01` 到 `2025-01` 的 `1h` 数据，先滚动 `28d` 做 cointegration 网络，再按外围/中心/跨社区来组 `20` 对 pair 的组合，连续周频再平衡 `209` 周，并做 `20` 次 Monte Carlo 重复。
- 论文里最硬的三组数字：
  1. **经典 top-cointegration benchmark**：Return `0.83`，SNR `0.2682`，Sortino `0.4289`，VaR5 `-0.0445`，CVaR5 `-0.0957`。
  2. **Peripheral_PMFG**：Return 仍是 `0.83`，但 **Sortino 提到 `1.0447`**，VaR5 改善到 `-0.0341`，CVaR5 改善到 `-0.0532`。翻成人话：**收益没变好多少，但尾部风险和 downside quality 明显更好。**
  3. **Peripheral_TMFG**：Return `0.76`，低于 benchmark，但 SNR `0.3069`、CVaR5 `-0.0518`，说明就算不追求更高收益，network-aware 选对也能明显压尾部。
- 论文另一个很 desk 化的结论是：**跨社区 weak-tie pair 更差。**
  - 作者对 weak-tie vs strong-tie 的收益分布做 Anderson-Darling 检验，像 `PMFG-Louvain p=0.001`、`TMFG-Louvain p=0.03`、`SBM p=0.001` 这类结果都过了显著性；
  - 人话就是：**桥接不同社区的 pair，长期关系没那么稳，更容易把不一样的市场驱动硬绑在一起。**
- 我补的 Binance Futures 公共 `1h` 网络代理快检（`BTC/ETH/BNB/SOL/XRP/ADA/DOGE/LINK/LTC/TRX/AVAX/ETC`，形成期约 `95d`、OOS `30d`）给出一个更保守但更贴 desk 的结论：
  - **classic_top_proxy**（按相关性 × Hurst × half-life 排前 `5` 对）最好：平均 **`+118.1 bps/trade`**、**`+1.01 bp/h`**、胜率 **`56.98%`**；
  - **peripheral_same_community** 也为正：平均 **`+71.2 bps/trade`**、**`+0.73 bp/h`**、胜率 **`58.33%`**；
  - **central_same_community** 较弱：平均 **`+111.7 bps/trade`**，但只有 **`+0.57 bp/h`**、胜率 **`55.71%`**；
  - 这组小样本代理 **没有复现出“peripheral > classic”**，但至少给出两点：
    - **peripheral sleeve 的持仓效率（bp/h）高于 central sleeve**；
    - 这批 liquid majors 里，**几乎没有值得保留的 weak-tie cross-community 候选**，说明“别硬跨社区拼 pair”这条很可能是真约束。
- 翻成人话：**network 这层更像是在 pairs raw alpha 上做“少踩隐藏相关风险”的诚实配书，而不是魔法增益器。**

## 3. 为什么和当前项目直接相关
- 它服务的还是 **pairs / stat-arb raw alpha**，不是纯解释型网络研究。base alpha 很清楚：spread mean reversion。  
- 当前项目已经积累了不少 “怎么做单对 / 多对 pair entry” 的材料；这篇补的是更缺的一块：**当 pair 扩成 book 时，怎么避免大家其实都在押同一件事。**
- 对我们这种 `5m/15m` 执行 desk，最现实的落法不是把社区标签当逐根信号，而是：
  - `1h` 做 formation / pair selection；
  - `15m` 或 `5m` 做 spread 执行；
  - 用 community / peripheral 信息控制 pair book 的配置和扩容顺序。

## 3.5 策略拆解（必填）
- 方向属性：market-neutral、双边、多对 pair 组合
- `formation`：
  - universe 先从流动性最好的 `20~80` 个 perp 开始；
  - 每周或每天用最近 `28d` 的 `1h` 数据更新 pair 关系；
  - 先选出具备均值回归属性的 pair（例如 `H < 0.5`、half-life 合理、spread 稳定）
- `entry`：
  - 计算 spread：`s_t = log(P_A) - beta * log(P_B)`；
  - 若 `z_t` 落在 `(1, 2)`，做空 spread；若落在 `(-2, -1)`，做多 spread；
  - 论文原文还叠加 `H < 0.5` 作为开仓必要条件
- `exit`：
  - spread 回到均值附近平仓；
  - 若 `|z| > 2`，止损；
  - 最长持有 `168h`
- `sizing`：
  - 单 pair 按 spread 波动做 risk parity；
  - 单社区 gross cap；
  - 单节点（同一币）在全 book 内做 exposure cap，避免一币多 pair 偷偷堆仓
- `risk / veto`：
  - 默认不优先做 cross-community weak-ties；
  - 默认优先 same-community、但社区之间分散配置；
  - 当 pair 之间共享同一腿或同一社区过度集中时，主动降配
- `cost`：
  - 先跑 `4 / 8 / 12 bps round-trip`；
  - perp 还要把 funding 和 borrow-like carry 影响记进 pair 持有成本

## 4. 可复刻的最小实验
- 数据源：Binance USDⓈ-M Futures `fapi/v1/klines`（公开可得）
- 频率映射：
  - `1h`：pair formation / network clustering / half-life & Hurst 计算
  - `15m`：下单与退出执行频率
  - `5m`：只建议做 execution slicing，不建议把 formation 也压到这么快
- 最小实验口径：
  1. 取 `20~30` 个最活跃 perp；
  2. 用最近 `28d` 的 `1h` 收盘构建 pair 候选池；
  3. 先用简单网络代理（相关性层级聚类 + 节点 strength/periphery）替代完整 PMFG/TMFG；
  4. 比较三本 book：
     - classic top-pairs
     - peripheral same-community
     - central same-community / weak-ties
  5. 输出：pair overlap、社区集中度、trade count、gross/net bps、VaR/CVaR、回撤共振。
- 这次本地 admission 级快检已经说明：
  - **classic 选法在小 liquid universe 上暂时仍最强；**
  - **peripheral sleeve 不是更暴利，但单位时间产出优于 central sleeve；**
  - **cross-community 候选很少，说明 weak-tie 该默认谨慎。**

## 5. 下一步怎么测（必须）
1. **把 universe 扩到 `50~100` 个 perp**：现在 `12` 个大币太少，网络结构被流动性龙头压扁，容易看不出论文里的外围优势。  
2. **做真正的 rolling book test**：每周重构 pair 与社区，不要只做一次 formation + 一次 OOS。  
3. **把 network 只放在“配书层”而不是 alpha 打分层**：先比较 `classic alpha score`，再叠加 `community cap / peripheral preference`，看是不是 risk-adjusted 更好。  
4. **把执行切到 `15m`**：信号仍在 `1h` 更新，但在下一个 `15m` 窗口执行，测 slippage、maker 填单率和组合净值。  
5. **专门做 contagion test**：统计单日大波动时，不同 pair book 是否出现“同时失真”的共振回撤；这比只看均值收益更重要。  

## 6. 风险与保留意见
- 这篇论文提供的是 **pairs raw alpha 的 portfolio-construction 升级**，不是全新 alpha 家族。若当前任务是纯扩 raw alpha 池，这条线的价值在“pairs book 更诚实”，不在“发现了全新品类信号”。  
- 本地快检是 **相关性/strength 网络代理**，不是原文 PMFG/TMFG + 真 cointegration 网络的精确复现。  
- 小 liquid universe 下，paper 的外围优势并没有完整复现；这意味着 **network-aware selection 更可能先体现为 risk/overlap 管理，而不是直接提高 raw return。**  
- 论文原样是 `1h` formation；对 `1m/3m` 直接硬下钻大概率会把结构层噪声放大，当前更适合作为 `15m` 执行上层。

## 7. 来源
1. **Grande, M., & Borondo, J. (2025). _Embedding pairs trading in market networks: a network science approach to portfolio construction_. Humanities and Social Sciences Communications.**  
   - Venue: `Humanities and Social Sciences Communications`  
   - DOI: `10.1038/s41599-025-05661-7`  
   - Readable URL: `https://www.nature.com/articles/s41599-025-05661-7`  
   - Table 2 URL: `https://www.nature.com/articles/s41599-025-05661-7/tables/2`  
   - Table 4 URL: `https://www.nature.com/articles/s41599-025-05661-7/tables/4`

2. **Binance Developers. _USDⓈ-M Futures API – Kline/Candlestick Data_.**  
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`

## 8. 本地产物
- `reports/artifacts/quant_digests/network_pairs_proxy_20260326_0615/summary.json`
- `reports/artifacts/quant_digests/network_pairs_proxy_20260326_0615/group_summary.csv`
- `reports/artifacts/quant_digests/network_pairs_proxy_20260326_0615/pair_quality_proxy.csv`
- `reports/artifacts/quant_digests/network_pairs_proxy_20260326_0615/classic_top_proxy_pairs_backtest.csv`
- `reports/artifacts/quant_digests/network_pairs_proxy_20260326_0615/peripheral_same_community_pairs_backtest.csv`
- `reports/artifacts/quant_digests/network_pairs_proxy_20260326_0615/central_same_community_pairs_backtest.csv`
