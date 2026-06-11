# 别把 pairs 只做成“跨币种对冲”：这篇 2024 论文更值得先偷的是 **same-coin 多报价篮子** 的 stat-arb raw alpha
- 时间：2026-03-24 01:26 UTC
- 类型：近 5 年论文 + 开源仓库 + Kraken 公共数据最小快检
- 主题类型：raw alpha
- 基础 alpha：relative value / stat-arb / pairs mean reversion（同一币种在多报价路径上的短周期偏离回归）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/mean-reversion/relative-value/stat-arb/pairs/multiquote/basket/crypto/5m/15m/1m/3m/paper/repo
- 证据类型：论文规则 + 开源代码 + 公开数据快检

## 1) 先回答：这篇东西的 base alpha 是什么？
**base alpha = 同一资产（例如 ETH）在不同 quote 路径下的短期“相对错价”会均值回归。**

不是 breakout，不是 confirmation。它本体就是可独立交易的 **relative-value / stat-arb raw alpha**：
- 先构造多条 ETH 报价路径（例如 `ETHUSD`、`ETHEUR×EURUSD`、`ETHGBP×GBPUSD`）
- 当两条路径出现极端偏离（z-score 超阈值）时，做多便宜腿、做空昂贵腿
- 等偏离回归（或超时）后平仓

---

## 2) 为什么这轮值得进研究池
最近我们已经补了不少 trend / breakout / funding 旁支。这个主题的价值在于：
1. **直接扩 raw alpha 素材池**（stat-arb / relative value 家族）
2. 论文 + repo 给了完整骨架：`entry / exit / sizing / risk / cost`
3. 能快速映射到 `5m/15m`，也可下钻 `1m/3m`
4. 和当前 desk 组件兼容：可做独立策略，也可做组合里的 market-neutral sleeve

---

## 3) 论文与仓库里最该偷的“可执行骨架”
基于 Yang & Malik (2024) + 开源实现：
- **Entry**：spread z-score 超 `open_threshold`
- **Exit**：z-score 回落到 `close_threshold` 或超时
- **Sizing**：不是简单 1:1；用优化分配多对冲腿权重（风险厌恶参数 `λ`）
- **Risk**：market-neutral 约束、每币种资金占用约束、交易成本项
- **Cost**：显式交易费用（论文/代码都强调“成本会显著吞噬边际”）

论文关键数字（作者样本，非我们实盘结论）：
- 全周期（含成本 0.1%）5min：`OTT λ=1 年化 15.49%`，DM 约 `0.60%`
- 牛市（2021，5min，0.1%）：`OTT λ=1 年化 36.75%`
- 熊市（2022，5min，0.1%）：`OTT λ=1 年化 4.99%`

> 读法：它不是“保证赚钱模板”，而是说明 **多报价偏离回归** 在不同市场状态下都可能提供可交易信号。

---

## 3.5) 策略拆解（必填）
- 方向属性：market-neutral relative value / stat-arb
- 基础 alpha：同一币种多报价路径偏离后的回归
- regime：偏离事件足够多、且流动性/执行可承接时更有效
- filter / veto：重大事件窗口、点差/冲击异常扩张、连续超时不回归
- risk / sizing / execution overlay：
  - z-score 分级仓位
  - 多腿净敞口约束（近似 delta-neutral）
  - `time stop + adverse expansion stop`
  - 成本梯度（maker/taker + spread + impact）

---

## 4) 最小可复现实验（公开数据，已落地）
### 4.1 数据源、公开性、更新频率
- 数据源：Kraken Public OHLC API（公开可得，无需私钥）
- 品种：`ETHUSD, ETHEUR, ETHGBP, EURUSD, GBPUSD`
- 更新频率：可直接请求 `1m/5m/15m/...`
- 本轮口径：`5m` 与 `15m`；窗口各 721 根（近几天）

### 4.2 最小实验定义
- 构造三条 USD 路径：
  - `usd_direct = ETHUSD`
  - `usd_from_eur = ETHEUR × EURUSD`
  - `usd_from_gbp = ETHGBP × GBPUSD`
- 对任意两条路径做 spread z-score
- 入场：`|z| >= z_in`
- 出场：`|z| <= z_out` 或 `max_hold` 到期
- 成本假设：round-trip `8 bps`（轻量代理口径）

### 4.3 本轮关键数据点
1. **错价事件确实存在**（不是 0）：
   - 5m 下 `usd_direct vs usd_from_gbp` 的 `p95 |mispricing| ≈ 15.81 bps`
   - 15m 下同对 `p95 |mispricing| ≈ 12.70 bps`
2. **极端偏离出现频率可交易**：
   - 5m 三组 pair 的 `|z|>2` 计数约 `29~48`
   - 15m 三组 pair 的 `|z|>2` 计数约 `28~39`
3. **但当前 naive 参数在 8bps 成本下仍为负**：
   - 最好的一组（5m, `usd_from_eur__usd_from_gbp`, `roll=192,z_in=2.5,z_out=0.25,max_hold=12`）
   - `gross_sum ≈ +55.73 bps`，`net_sum ≈ -48.27 bps`

结论要诚实：
- 这条 raw alpha **有信号密度和偏离幅度**，方向上成立；
- 但“naive 双阈值 + 固定持有”还没过成本线，下一步重点应放在 **执行与筛选治理**，而不是先堆更复杂模型。

---

## 5) 下一步怎么测（直接可执行）
1. **成本分层回测**：同一规则跑 `4/6/8/10 bps` 梯度，明确 break-even cost。  
2. **事件分层**：把入场分成 `|z|∈[2,2.5), [2.5,3), >=3`，验证是否“极端才有边”。  
3. **加入 regime gate**：仅在 `spread 波动分位` 与 `流动性分位` 同时满足时开机。  
4. **执行口径升级**：从固定成本换成 `maker占比 + spread/impact`，测 executable edge。  
5. **频率下钻**：同框架下钻 `3m/1m`，但先加 `participation cap`，防止高频幻觉。  

---

## 6) 风险与保留意见
- 本轮快检窗口较短（近几天），只能作为 intake 级证据，不是最终结论。  
- Kraken 多报价路径可交易性、手续费档位与我们目标 venue 可能不同，需迁移复核。  
- 该 alpha 可能高度依赖执行质量；若无 maker 优势，边际容易被成本抹平。  

---

## 7) 来源（论文 / 仓库 / 数据）
1. **Yang, H., & Malik, A. (2024). _Optimal Market-Neutral Multivariate Pair Trading on the Cryptocurrency Platform_. International Journal of Financial Studies, 12(3), 77.**  
   - Venue: International Journal of Financial Studies (MDPI)  
   - DOI: `10.3390/ijfs12030077`  
   - Readable URL: https://www.mdpi.com/2227-7072/12/3/77  
   - Preprint URL: https://arxiv.org/abs/2405.15461
2. **Hongshen-Yang. (2024). _optimal-trading-technique_. GitHub repository.**  
   - Repo URL: https://github.com/Hongshen-Yang/optimal-trading-technique  
   - Readable URL: https://github.com/Hongshen-Yang/optimal-trading-technique
3. **Kraken Support. _Downloadable historical OHLCVT data_ / Public OHLC API.**  
   - Readable URL: https://support.kraken.com/hc/en-us/articles/360047124832-Downloadable-historical-OHLCVT-Open-High-Low-Close-Volume-Trades-data  
   - API URL: https://api.kraken.com/0/public/OHLC

---

## 8) 本地复现实验产物
- `reports/artifacts/quant_digests/multiquote_ott_proxy_20260324/spread_diagnostics.csv`
- `reports/artifacts/quant_digests/multiquote_ott_proxy_20260324/grid_summary.csv`
- `reports/artifacts/quant_digests/multiquote_ott_proxy_20260324/best_by_pair_interval.csv`
- `reports/artifacts/quant_digests/multiquote_ott_proxy_20260324/best_trades.csv`
- `reports/artifacts/quant_digests/multiquote_ott_proxy_20260324/meta.json`
