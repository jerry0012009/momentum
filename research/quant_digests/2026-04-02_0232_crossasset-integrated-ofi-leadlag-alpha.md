# 别把 OFI 只读成单币盘口压力：对 crypto short-cycle desk，更该先测的是「leader coin lagged integrated OFI × follower 1m/3m continuation」这条 cross-asset raw alpha

- 主题类型：raw alpha
- 基础 alpha：**跨资产、滞后一期的 integrated OFI / cross-asset OFI** 可以预测下一小段时间内跟随币种的短周期收益；翻成人话，就是“领涨/领跌币的订单流先动，后排币的价格再跟”
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 时间：2026-04-02 02:32 UTC
- 类型：2023 *Quantitative Finance* 论文摘要 / OpenAlex metadata + 2023 *Mathematical Finance* 论文摘要 / OpenAlex metadata + 2025 GitHub repo（`ofi.py`）source audit + 2026 Binance 公共数据 repo scaffold（`README.md` + `data_integration.py` + `feature_engineering.py` + `model_training.py` + `backtester.py`）
- 主题标签：raw-alpha/microstructure/cross-asset/lead-lag/ofi/integrated-ofi/order-book/relative-value/directional/binance/btc-eth-sol-bnb/1m/3m/5m/repo/paper/public-data/cost
- 证据类型：paper-first（alpha 命题）+ repo scaffold（特征工程 / 公共数据 / 最小回测骨架）

## 1. 这次看了什么
这轮更值得 intake 的，不是再补一张“单币 OBI / microprice 会不会预测下一跳”的老卡，而是把 **OFI 从单资产扩成跨资产 lead-lag raw alpha**。

这条线的核心证据链很干净：

1. **Cont, Cucuringu, Zhang (2023, *Quantitative Finance*)** 说明：
   - 把盘口多档位信息整合成 **integrated OFI**，比只看 best-level OFI 更能解释冲击；
   - 更重要的是，**lagged cross-asset OFIs 确实能提升对 future returns 的预测**；
   - 但这种 cross-impact **主要发生在短期，而且衰减很快**。
2. **Kolm, Turiel, Westray (2023, *Mathematical Finance*)** 说明：
   - 真正有信息量的不是原始 order book state，而是 **stationary order-flow inputs**；
   - 他们在 **115 只 Nasdaq 股票** 上发现：order-flow 类输入显著优于直接喂 raw book；
   - 有效预测窗口大约只有 **两次平均价格变动**，再次强调这是一条短命、要快测快杀的 alpha。
3. **parshG/OFI-Feature-Construction (2025)** 已经把这条线最关键的 engineering 拆出来：
   - `best_level_ofi`
   - `multi_level_ofi`
   - `integrated_ofi`（PCA 聚合多档位）
   - `cross_asset_ofi`（LassoCV 做 cross-impact beta）
4. **tsuithomas/crypto_research_order_book_imbalance (2026)** 虽然 headline 还是单币 OBI，但它给了我们一个现成的 **Binance 公共数据 ingestion + 1m 特征工程 + walk-forward + 成本回测骨架**，正好能把上面的跨资产 OFI 命题移植到 crypto 最小实验。

所以这次真正该记进研究池的，不是“OBI 又能预测方向”，而是：

> **如果 BTC / ETH 这些 leader coin 的 integrated OFI 先走强/走弱，后排币的 1m / 3m 收益是否会出现可交易的短暂跟随？**

这是一条标准的 `raw alpha`，不是 filter，也不是只能依附别的策略的 overlay。

## 2. 先回答一句：这篇东西的 base alpha 是什么？
**base alpha 很清楚：跨资产订单流 lead-lag。**

不是：
- 单币 OBI 过高，所以少做；
- 或者“盘口有点偏，所以拿来当 veto”。

而是：
- 先把 leader coin 的盘口多层订单流压缩成 `integrated OFI`；
- 再看它对 follower coin 下一小段收益有没有 **滞后预测力**；
- 如果有，就可以做：
  - `directional continuation`（直接做 follower）
  - 或 `relative-value long/short`（long 强流入腿、short 弱流入腿）

翻成人话：
**先动的不是价格，而是订单流；先动的不是所有币一起，而是 leader 先动、follower 后跟。**

## 3. 为什么这轮值得写，而不是继续在单币 OBI 或 pairs 里内循环
最近 digest 里，single-asset microstructure、pairs、carry、cross-sectional 已经不少；但 **multi-asset flow lead-lag** 这块还相对空。

这轮值得写，原因有三条：

1. **它还是 raw alpha，不是旁支 filter。**
   - 入场信号本体就是“leader OFI 先动，follower 未来收益响应”。
2. **它能直接扩素材池。**
   - 既可以服务 `1m / 3m` 的高强度 directional alpha；
   - 也可以服务 market-neutral 的 long/short spread 版本。
3. **它比单币 OBI 更 desk-friendly。**
   - 单币 OBI 很容易死在延迟和 fee wall；
   - cross-asset lagged OFI 至少在逻辑上多了一层“滞后可抓取窗口”，更像 `1m / 3m / 5m` desk 能诚实检验的东西。

所以如果问“它为什么比继续补一个普通 OBI 卡更值得？”
答案是：
**因为它把单币微结构 edge 升级成了跨资产传导 edge，理论上更接近 desk 真正能抓的短周期 alpha。**

## 3.5 策略拆解（必填）
- 方向属性：cross-asset directional / relative-value
- 基础 alpha：leader coin 的 lagged integrated OFI 预测 follower coin 下一小段收益
- regime：只在高流动、低 spread、leader/follower 关系稳定时启用
- filter / veto：spread 异常放宽、成交稀薄、事件冲击、相关关系失稳时停做
- risk / sizing / execution overlay：按 leader-follower beta 缩放；做 cost ladder；maker-biased 优先，必要时 taker only 做 existence check

## 4. 这次看的主来源
### 4.1 alpha 主来源（paper）
1. **Cont, Rama; Cucuringu, Mihai; Zhang, Chao (2023)**  
   **Title:** *Cross-impact of order flow imbalance in equity markets*  
   **Venue:** *Quantitative Finance*  
   **DOI:** `10.1080/14697688.2023.2236159`  
   **Readable URL:** https://doi.org/10.1080/14697688.2023.2236159  
   **Open PDF URL:** https://www.tandfonline.com/doi/pdf/10.1080/14697688.2023.2236159?download=true  
   **Repo URL:** N/A

2. **Kolm, Petter N.; Turiel, Jeremy; Westray, Nicholas (2023)**  
   **Title:** *Deep order flow imbalance: Extracting alpha at multiple horizons from the limit order book*  
   **Venue:** *Mathematical Finance*  
   **DOI:** `10.1111/mafi.12413`  
   **Readable URL:** https://doi.org/10.1111/mafi.12413  
   **Open PDF URL:** https://onlinelibrary.wiley.com/doi/pdfdirect/10.1111/mafi.12413  
   **Repo URL:** N/A

### 4.2 engineering 辅助来源（repo）
3. **parshG (2025), *OFI-Feature-Construction***  
   **Venue:** GitHub repository  
   **DOI:** N/A  
   **Readable URL / Repo URL:** https://github.com/parshG/OFI-Feature-Construction  
   **GitHub metadata:** created `2025-06-16T03:33:41Z`, pushed `2025-06-16T03:34:43Z`  
   **实际看的文件：** `ofi.py`

4. **tsuithomas (2026), *crypto_research_order_book_imbalance***  
   **Venue:** GitHub repository  
   **DOI:** N/A  
   **Readable URL / Repo URL:** https://github.com/tsuithomas/crypto_research_order_book_imbalance  
   **GitHub metadata:** created `2026-03-03T08:54:44Z`, pushed `2026-03-03T08:58:05Z`  
   **实际看的文件：** `README.md`, `src/data_integration.py`, `src/feature_engineering.py`, `src/model_training.py`, `src/backtester.py`

## 5. 这条 alpha 到底有什么硬信息，不是空想
### 5.1 2023 cross-impact paper 给出的最关键结论
OpenAlex 摘要重建后，最值钱的三句是：

- **integrated OFI 比 best-level OFI 更能解释 price impact**；
- contemporaneous impact 上，多资产 cross-impact 没有比 sparse model 多太多解释力；
- 但 **lagged cross-asset OFIs 确实提升 future return forecasting**，而且这种效应 **主要发生在短期并快速衰减**。

这对 desk 的翻译很直接：
- 同步共振没什么好做的，通常已经反映进价格；
- 真正能做的是 **小滞后窗口里的跨币传导**。

### 5.2 2023 deep OFI paper 给出的窗口感
这篇 paper 摘要里至少有三个硬点：

- 样本是 **115 只 Nasdaq 股票**；
- **order-flow derived inputs** 明显优于直接喂 raw order book states；
- 有效预测 horizon 大约只有 **两次平均价格变动**。

翻成人话：
**如果这条 alpha 有边，它不会活很久，所以不适合装成慢速 15m 主信号。**

### 5.3 2025 repo 已经把核心特征写成代码
`ofi.py` 里最关键的几段：

- `compute_best_level_ofi()`：顶档 OFI
- `compute_multi_level_ofi(levels=10)`：多档位 OFI 累加
- `compute_integrated_ofi(levels=10, n_components=1)`：
  - 对不同档位 OFI 构造矩阵；
  - 再用 `PCA(n_components=1)` 压成单一 `integrated_ofi`
- `compute_cross_asset_ofi()`：
  - 把 `ofi_value` 和 `return` 按 `ts_event × symbol` pivot 成矩阵；
  - 用 `LassoCV` 回归每个 target asset 的 return 对全市场 OFI 的敏感度

也就是说，**从 best-level → multi-level → integrated → cross-asset** 这条研究路径，repo 已经给出了一版最小工程实现。

### 5.4 2026 crypto repo 给出了 crypto 最小实验壳
这份 repo 的 evidence 强度一般，不能直接当论文结论，但工程上很值钱：

- `data_integration.py` 直接从 **Binance public aggTrades archive** 抓数据；
- 默认例子抓的是 **BTCUSDT, 2025-10-01 到 2025-12-31**；
- `feature_engineering.py` 先把 tick 聚成 `1min`，然后做：
  - `buy_vol`
  - `sell_vol`
  - `obi`
  - `volatility_20`
  - 以及 **5-period forward log return**（如果 `freq=1min`，就是 5 分钟前瞻）
- `model_training.py` 用 `XGBoost` 做 `80/20` walk-forward split；
- README 里给了几个可用的工程数字：
  - **OBI ~45% feature importance**
  - maker 假设下、`15 bps` conviction threshold 后，策略样例 **+3.21%**，同期市场 **-12.76%**

这些数字我不会当成强证据，但它告诉我们：
**Binance 公共数据 + 1m 聚合 + cost-aware threshold 的实验壳，已经足够搭一版跨资产 OFI 最小实验。**

## 6. 对当前 desk，更值得测的不是“单币 OBI”，而是“leader OFI -> follower return”
如果沿着这条证据链走，最自然的 desk 化改写不是：
- 继续在 BTC 单币上做 OBI 方向分类；

而是：
- 选一组 leader/follower：
  - `BTC -> ETH`
  - `BTC -> SOL`
  - `ETH -> SOL`
  - `ETH -> BNB`
- 每 `1m` 或事件聚合窗口计算 leader 的：
  - `best_level_ofi`
  - `multi_level_ofi`
  - `integrated_ofi`
  - `microprice gap`
- 然后预测 follower 未来 `1m / 3m / 5m` 收益

也就是：
**把 alpha 从“单币下一步往哪动”改成“谁先在订单流上表态，谁后在价格上跟”。**

## 7. 这条 raw alpha 可以怎样直接落地成完整策略
### 7.1 Entry
第一版先别复杂化，直接做：

- 设 leader-follower 对：`BTC/ETH`, `BTC/SOL`, `ETH/SOL`, `ETH/BNB`
- 每 `1m` 计算：
  - leader `integrated_ofi_z`
  - leader `microprice_gap_z`
  - follower `ret_1m_lag0`
  - spread / vol / volume 状态
- 当：
  - leader `integrated_ofi_z > z_up`
  - `microprice_gap_z` 同向
  - follower 当下还没完全跟上（例如 `follower_ret_1m < leader_ret_1m * beta_cut`）
  → 做多 follower
- 做空同理

### 7.2 Exit
先用最朴素的三档：
- 固定持有 `1 / 3 / 5` 根 `1m` bar
- 若 leader OFI 反向，立即平
- 若 follower 已补涨/补跌到阈值，平仓

### 7.3 Sizing
第一版先：
- 单对固定 notional
- 按 rolling vol 反比缩放
- 若做 long/short 版本，则按 leader-follower beta 近似配平

### 7.4 Risk / Cost
至少要有：
1. **spread gate**：follower spread 超过滚动 80% 分位数就不做
2. **liquidity gate**：近 `N` 根 trade count 太低不做
3. **event veto**：大新闻 / 极端瞬时波动 bar 不做普通 lead-lag 解释
4. **cost ladder**：round-trip 先跑 `2 / 4 / 6 / 8 / 10 bps`
5. **leader decoupling veto**：leader-follower 近几天相关性或 beta 崩掉则停用

## 8. 这条 alpha 与 `1m / 3m / 5m / 15m` 的关系
### 8.1 `1m`
这是最该先打的主战场。
原因：
- cross-impact paper 明说效应短且快衰减；
- deep OFI paper 也说明有效 horizon 很短；
- 所以 `1m` 最适合先做 existence check。

### 8.2 `3m`
如果 `1m` 太噪，`3m` 是最自然的第二站：
- 还能保留短周期传导；
- 又比 1m 更容易跨过 fee wall。

### 8.3 `5m`
`5m` 不是首选发现层，更像：
- `1m/3m` alpha 已成立后，用来做 execution-friendly transfer；
- 或只保留高 conviction 子集。

### 8.4 `15m`
不建议把这条命题直接伪装成 `15m` 主信号。
更合理的是：
- 把它当 `15m` 策略的 intrabar admission / veto；
- 或当更慢策略的仓位倾斜层。

## 9. 最小可复现实验（直接对当前 desk）
### 实验 A：最朴素的 leader->follower directional check
- **Universe**：BTC, ETH, SOL, BNB
- **数据源**：
  - 公开可得：Binance public `aggTrades` / `bookTicker` / depth snapshot
  - 更新频率：tick / event-driven，聚合到 `1m`
- **特征**：leader 的 `best_level_ofi`, `multi_level_ofi proxy`, `integrated_ofi proxy`, `microprice gap`
- **Target**：follower 未来 `1m / 3m / 5m` log return
- **要回答的问题**：lagged leader flow 是否比 leader return 更早、更稳？

### 实验 B：best-level vs integrated OFI ablation
同一批 leader/follower，只比较：
1. best-level OFI
2. multi-level OFI
3. integrated OFI
4. integrated OFI + microprice gap

这一步要回答：
**多档位整合是否真的比顶档 OBI/OFI 更值钱？**

### 实验 C：directional vs relative-value
同一信号做两种交易壳：
1. 直接做 follower 单腿
2. long follower / short leader（或反之）

这一步要回答：
**edge 来自纯方向跟随，还是来自相对补涨补跌？**

### 实验 D：cost ladder
统一信号，统一持有期，只改：
- `2 bps`
- `4 bps`
- `6 bps`
- `8 bps`
- `10 bps`

不先卷复杂模型，先看：
**哪一层摩擦下还有净边。**

## 10. 这条线最容易犯的错
- **错法 1：** 把 contemporaneous 共振误判成可交易 alpha；真正该看的是 lagged 版本。
- **错法 2：** 只看 leader return，不看 leader order flow；结果把更早的信号扔了。
- **错法 3：** 只做顶档 OBI，不做多档位 / integrated 版本；可能把更稳的信息压没了。
- **错法 4：** 看到 `1m` 有显著性，就默认 `5m/15m` 更稳；实际上很多时候只是衰减完了。
- **错法 5：** 只看预测分数，不跑 cost ladder；微结构 alpha 最后常死在执行上。

## 11. 为什么它值得进研究池
这张卡值得进池，不是因为它已经给出了一份现成可实盘的 Sharpe，而是因为它把一条很适合 short-cycle desk 的命题讲得足够清楚：

> **真正有价值的，不一定是“单币盘口歪了一点”，而是“某个 leader 的订单流已经先转向，但 follower 价格还没完全反应”。**

这比继续在单币 OBI 上抠 1bps 更值得先测，因为它更像 desk 能在 `1m / 3m / 5m` 上抓到的可交易传导窗口。

## 12. 下一步怎么测
1. **先用 Binance 公共数据做 7~14 天最小实验**：只做 `BTC/ETH/SOL/BNB` 四币。
2. **先做最简单的线性 / 阈值版本**：不要一上来就上 XGBoost 或 LSTM。
3. **一定做四组 ablation**：
   - leader return only
   - leader best-level OFI
   - leader integrated OFI
   - integrated OFI + microprice
4. **第二步只盯 cost ladder**：这条线的关键不是预测显著，而是 after-cost 能不能活。
5. **如果 `1m` 活、`3m` 还能留边**，再决定是否把它升格成：
   - 单独的 fast raw alpha；
   - 或 pairs / spread / breakout 的 cross-asset admission layer。

## 13. 一句话结论
如果只带走一句话，我会带走这句：

**别再把 OFI 只当单币盘口指标；对 crypto short-cycle desk，更值得快检的是「leader coin 的 lagged integrated OFI 是否能在 1m/3m 上提前预告 follower 的补涨补跌」这条 cross-asset raw alpha。**
