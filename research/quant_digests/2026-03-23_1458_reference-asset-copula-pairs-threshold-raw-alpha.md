# 别把 copula 当主角：这篇 2025 论文更值得先落地的是「cointegration spread 均值回归 + 阈值分层」raw alpha
- 时间：2026-03-23 14:58 UTC
- 类型：近 5 年论文 + 开源仓库 + Binance 公共数据最小快检
- 主题类型：raw alpha
- 基础 alpha：pairs / stat-arb / relative-value mean reversion（价差偏离→回归）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：pairs/stat-arb/relative-value/mean-reversion/cointegration/copula/threshold-selection/cost/crypto/5m/15m
- 证据类型：论文证据 + 工程证据 + 本地快检（可复现）

## 1. 这次看了什么
这次主看 **Tadi & Witzany (2025)** 的 *Copula-based trading of cointegrated cryptocurrency Pairs*。对我们 desk 来说，最有价值的不是“copula 名字本身”，而是它把 **完整可执行的 pairs skeleton**（pair selection、entry/exit threshold、频率选择、成本口径）讲清楚了：
> **base alpha = cointegration spread 的均值回归**，copula 更像强化触发/过滤层。

并补看了一个可跑通流程的开源实现（`Manan-Rawat/Crypto_pairs`）用于工程拆解（OLS spread、top-pair ranking、threshold 回测、copula AIC 选择）。

## 2. 核心结论
- **一句话核心结论：** 这条线最可落地的 raw alpha 不是“高维 copula 拟合本身”，而是 **cointegration spread mean reversion + 阈值/频率分层**。
- **一句话证明方式：** 论文直接比较 hourly vs 5-min 与不同开仓阈值，显示策略表现对采样频率和阈值高度敏感，且 copula 变体之间有明显优劣分化。

论文里对我们最关键的 3 个数据点（可直接指导最小实验）：
1. 在其样本设置下，**5-min + EG** 的最佳总净收益可到 **205.9%**（`α1=0.20`）。
2. **5-min + EG** 的年化净收益随阈值提升从 **56.7% (`α1=0.10`)** 升到 **75.2% (`α1=0.20`)**。
3. 对比口径下，return-based copula 方法虽有高毛收益，但交易成本吞噬显著；说明 **“触发更激进 ≠ 成本后更好”**。

## 3. 为什么和当前 desk 直接相关
- 这是 **独立 raw alpha 家族补充**（pairs/stat-arb），不是继续在 breakout/retest 里内循环。
- 它天然具备完整策略要素：
  - entry（z-score/CMI 阈值）
  - exit（均值回归/阈值回落/超时）
  - sizing（beta- 或 dollar-neutral）
  - risk（max-hold、drawdown、pair 失稳停机）
  - cost（手续费/滑点直接进回测）
- 和我们当前 1m/3m/5m/15m 研发节奏兼容：先用简化 spread 版本做 first verdict，再决定是否引入 copula gate。

## 3.5 策略拆解（必填）
- 方向属性：market-neutral relative-value / stat-arb
- 基础 alpha：
  - 定义价差 `spread_t = log(P_y) - beta_t * log(P_x)`
  - 当 `|z(spread_t)|` 偏离过大时，押注向均值回归
- regime/filter：
  - 只在 pair 稳定（相关+半衰期+平稳性）时开机
  - 在事件波动/流动性差/结构断裂时 veto
- risk/sizing/execution：
  - beta-neutral 权重
  - `max_hold` 超时平仓
  - 必须显式计入双边成本

## 4. 本地最小快检（Binance 公共数据）
### 4.1 数据与口径
- 数据源：Binance Spot klines（公开 API）
- 公开性：公开可得，无需私有授权
- 更新频率：5m / 15m K 线
- 本次快检样本：
  - 5m：最近 `5000` bars（约 17 天）
  - 15m：最近 `5000` bars（约 52 天）
- 候选池：`BTC/ETH/BNB/SOL/XRP/DOGE/LINK/ADA`
- 训练/测试：前 60% 用于 pair 诊断；全样本滚动回测
- 成本假设：每次进场/出场各 `8 bps`（round-trip `16 bps`）

### 4.2 快检结果（关键）
- **5m**：在当前筛选条件（`corr>0.6`, `half-life 4~120`）下，候选 pair 数为 **0**。
- **15m**：可得到 6 个候选 pair；在 `entry z=1.5` 下：
  - 组合层平均 `mean net` 为 **-4.27 bps/trade**（343 笔）
  - 但存在可交易子簇：`SOL-LINK` 为 **+10.32 bps/trade**（63 笔，胜率 76.2%）
- 阈值抬高（`z=2.0/2.5`）后，组合层结果进一步变差（分别约 **-15.72 / -49.81 bps/trade**）。

**读法：**
- 这条 raw alpha 在 15m 上有“局部可交易对”，但不是“全池都能做”；
- 阈值并非越高越好，且成本后表现对 pair selection 极敏感；
- 5m 若要成立，先要放宽或重做 pair formation（否则 trade opportunity 不足）。

## 5. 下一步怎么测（可直接执行）
1. **Pair-first**：先固定候选对（例如 `SOL-LINK`、`DOGE-ADA`），不要全池平均。  
2. **三维参数网格**：`entry z ∈ {1.2,1.5,1.8,2.0}` × `exit z ∈ {0.0,0.25,0.5}` × `max_hold ∈ {24,48,72}`。  
3. **稳定性门槛**：增加 rolling cointegration / half-life 漂移约束，pair 失稳即下线。  
4. **成本敏感性曲线**：画 `4/8/12/16 bps` 四档，确认生存边界。  
5. **1m/3m 映射**：只对通过 15m first verdict 的 pair 下钻，不对全池盲测。

## 6. 风险与保留意见
- 论文中的高收益结果依赖其完整实现细节，不能直接线性移植到我们口径。
- 开源仓库提供了流程骨架，但其超高成功率表述需谨慎，必须以成本后 OOS 复测为准。
- 当前快检说明“局部 pair 可行、全池平均不行”，因此生产化必须做严格 pair governance。

## 7. 来源
1. **Masood Tadi, Jiří Witzany (2025). _Copula-based trading of cointegrated cryptocurrency Pairs_. Financial Innovation.**  
   - DOI: `10.1186/s40854-024-00702-7`  
   - Readable URL: https://link.springer.com/article/10.1186/s40854-024-00702-7
2. **Manan-Rawat (2025). _Crypto_pairs_. GitHub repository.**  
   - Repo URL: https://github.com/Manan-Rawat/Crypto_pairs  
   - Readable URL: https://github.com/Manan-Rawat/Crypto_pairs
3. **Fil, M., & Kristoufek, L. (2020). _Pairs Trading in Cryptocurrency Markets_. IEEE Access.**  
   - DOI: `10.1109/ACCESS.2020.3024619`  
   - Readable URL: https://ieeexplore.ieee.org/document/9205395

## 8. 本地复现产物
- `reports/artifacts/quant_digests/copula_pairs_threshold_probe_20260323/meta.json`
- `reports/artifacts/quant_digests/copula_pairs_threshold_probe_20260323/selected_candidates.csv`
- `reports/artifacts/quant_digests/copula_pairs_threshold_probe_20260323/pair_results.csv`
- `reports/artifacts/quant_digests/copula_pairs_threshold_probe_20260323/summary_by_interval_entry.csv`
