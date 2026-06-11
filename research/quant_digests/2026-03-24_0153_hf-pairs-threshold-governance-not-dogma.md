# 别把 fixed/dynamic 阈值当教条：这篇 2025 高频 pairs 论文更值得先复现的是「阈值 × pair 数量」治理框架
- 时间：2026-03-24 01:53 UTC
- 类型：近 5 年论文 + 公开 API 最小快检（honest train/test）
- 主题类型：raw alpha
- 基础 alpha：pairs / stat-arb / relative-value mean reversion（价差偏离后回归）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/high-frequency/5m/15m/threshold-governance/cost
- 证据类型：论文证据 + 本地快检

## 1. 这次看了什么
先回答 base alpha：**这篇东西的 base alpha 不是“阈值技巧”，而是 cointegration / distance spread 的均值回归。**

这次主看：
- **Aghamohammadi & Dastkhan (2025)**，*Pair trading with high-frequency data in the cryptocurrency market*（China Finance Review International, DOI: `10.1108/CFRI-11-2024-0727`）

这篇对我们 desk 最值钱的点，不是“fixed 一定比 dynamic 好”这句 headline，而是它把可落地完整策略需要调的三类旋钮说清楚了：
1) entry/exit 阈值；2) pair 组合规模；3) 周期（含 `15m/5m`）。

## 2. 核心结论
- **一句话核心结论：** 高频 pairs 能不能活，不取决于“有没有回归信号”，更取决于“阈值治理 + pair 篮子治理 + 成本治理”是否诚实。  
- **一句话证明方式：** 论文在 top50 Binance 币池、跨牛稳熊三阶段、跨 `5m/15m` 做了 distance/cointegration/hybrid + 阈值敏感性比较；我用公开 Binance K 线做了同主题最小快检（train/test 分离、固定参数外推）看这件事在短样本是否也明显。

论文侧（来自摘要）最关键的 3 点：
1. 样本覆盖 `2020(牛)/2021(稳)/2022(熊)`，并明确包含 `15m` 与 `5m` 高频层。  
2. 比较了 distance、cointegration、hybrid 三种配对范式。  
3. 结论强调：阈值设置、退出阈值、pair 数量都会显著影响结果（而不只是“信号本身”）。

本地最小快检（公开数据，成本后）关键 3 点：
1. **全 pair 平均会被成本吃掉**：`15m fixed` 平均 `-11.79 bps/对`，`5m fixed` 平均 `-59.05 bps/对`。  
2. **同一规则下有 pocket**：`15m` 最佳对（`BTCUSDT__XRPUSDT`）仍可达 `+172.38 bps`，`5m` 最佳对（`ETHUSDT__DOGEUSDT`）`+185.33 bps`。  
3. **pair 数量很关键**：`15m fixed` 从“全 15 对平均 `-11.79 bps`”到“train 选前 4 对后 test 平均 `+37.18 bps`”；`5m fixed` 从全 15 对 `-59.05 bps` 到前 6 对 `+14.38 bps`。

> 读法：我们这轮不是在判“fixed vs dynamic 谁永远胜出”，而是在确认**阈值和篮子治理本身就是 alpha 生死线**。另外，本地 dynamic 使用的是 proxy 口径（不是论文原始 dynamic 定义），不做一比一优劣宣判。

## 3. 为什么和当前项目有关
这条线直接服务当前短周期 raw alpha 素材池（`pairs / stat-arb / relative value`）：
- 有完整策略链路：entry / exit / sizing / risk / cost 都可写成规则；
- 能直接映射到 `1m/3m/5m/15m`（先 `15m/5m`，再下钻）；
- 能补当前“信号很多，但组合治理不足”的缺口。

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / market-neutral / 均值回归  
- 基础 alpha：`spread` 偏离后向均值收敛  
- regime：关系稳定、流动性够、成本可承受时更有效  
- filter / veto：结构断裂、流动性骤降、事件冲击窗口禁入  
- risk / sizing / execution overlay：
  - pair 分层（先小篮子，不全池）
  - 按 z-score 档位分配仓位
  - max-hold + time-stop
  - maker/taker + 滑点 + 冲击成本显式入账

## 4. 可复刻的最小实验
### 4.1 数据源、公开性、更新频率
- 数据源：Binance Spot Public Klines API（公开可得，无需私钥）  
- 更新频率：`1m/3m/5m/15m/...`  
- 本轮口径：`5m` 与 `15m`，`limit=1500` bars

### 4.2 最小实验口径（honest）
- 币池：`BTC/ETH/BNB/SOL/XRP/DOGE`（15 个 pair）
- 训练/测试：前 60% 训练，后 40% 测试
- 模型：train 内估计 `alpha/beta`，test 固定外推（不重估）
- 交易规则：`entry |z|>2`，`exit |z|<0.5` 或 `max_hold=24 bars`
- 成本：单边 `8 bps`（round-trip 约 `16 bps`）

### 4.3 下一步怎么测（必须）
1. **先冻结 pair 选择流程**：只能用 train 排名选 `K`，再看 test；禁止用 test 反选 pair。  
2. **阈值网格**：`entry ∈ {1.44,1.65,2.0}` × `exit ∈ {0.0,0.25,0.5}`，分 `5m/15m` 各自测。  
3. **K 敏感性曲线**：`K=2,4,6,8,10...`，找“容量上限”而非追求全池覆盖。  
4. **执行诚实化**：把固定 bps 成本替换为 `maker占比 + spread + participation cap`。  
5. **下钻 3m/1m 只在通过 15m/5m 后进行**，并先测成交约束，否则容易出现“纸面 alpha”。

## 5. 风险与保留意见
- 论文正文网页受 Cloudflare 保护，本轮对论文主体依赖 Crossref 题录/摘要与可见元数据；未扩写不可见细节。  
- 本地 dynamic 仅为 proxy，不能拿来直接反驳/确认论文里的 dynamic 机制。  
- 样本窗口较短（近端数据），属于 intake 级证据，不是 final verdict。

## 6. 来源
1. **Aghamohammadi, A., & Dastkhan, H. (2025). _Pair trading with high-frequency data in the cryptocurrency market_. China Finance Review International.**  
   - DOI: `10.1108/CFRI-11-2024-0727`  
   - Readable URL: https://doi.org/10.1108/CFRI-11-2024-0727  
   - Metadata URL: https://api.crossref.org/works/10.1108/cfri-11-2024-0727
2. **Tsoku, J. T., & Makatjane, K. (2026). _Deep learning-based pairs trading: real-time forecasting of co-integrated cryptocurrency pairs_. Frontiers in Applied Mathematics and Statistics.**（实现参考）  
   - DOI: `10.3389/fams.2026.1749337`  
   - Readable URL: https://www.frontiersin.org/journals/applied-mathematics-and-statistics/articles/10.3389/fams.2026.1749337/full  
   - Repo URL: https://github.com/M-man2591/deep-learning-crypto-pairs-trading
3. **Binance Spot API Docs — Kline/Candlestick Data.**  
   - Readable URL: https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#klinecandlestick-data

## 7. 本地复现实验产物
- `reports/artifacts/quant_digests/hf_pairs_threshold_governance_20260324/interval_method_summary_honest.csv`
- `reports/artifacts/quant_digests/hf_pairs_threshold_governance_20260324/basket_k_sensitivity_honest.csv`
- `reports/artifacts/quant_digests/hf_pairs_threshold_governance_20260324/pair_train_test_metrics_honest.csv`
- `reports/artifacts/quant_digests/hf_pairs_threshold_governance_20260324/meta_honest.json`
