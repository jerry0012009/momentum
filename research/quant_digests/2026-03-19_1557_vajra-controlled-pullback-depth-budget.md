# 别把 `controlled pullback <= 1.5%` 当 15m 通用过滤：在 EMA/PSAR continuation 上，它更像“前置状态预算”，不是触发后 gate
- 时间：2026-03-19 15:57 UTC
- 类型：GitHub + 本地代理快检
- 主题标签：ema/psar/raw-alpha/pullback/controlled-pullback/depth-budget/adx/volume/continuation/filter/repo/crypto/15m
- 证据类型：repo 规则（工程证据）+ 公开行情代理快检

## 1. 这次看了什么
这轮看的是一个很新的仓库：**Aatharva21 (2026) 的 `BTC-EMA-based-strategy-1H-`（Vajra）**。  
我没有照搬它的整套 1H BTC 策略，而是只抽了一个更适合我们 desk 的旁支问题：

> `controlled pullback <= 1.5%` 这条规则，放到我们 `15m EMA/PSAR continuation` 里，应该当触发过滤，还是当“前置状态预算”来用？

repo 里这条支路很清楚：
- `pullbackLookback = 5`
- `maxPullbackPct = 1.5`
- `nearEMA`
- `volume > 1.2 * SMA20`
- `ADX >= 25`

## 2. 核心结论
1. **一句话核心结论**：在当前 15m EMA/PSAR 代理触发口径里，`pullback<=1.5%` 几乎不筛选样本（108/109 已天然满足），所以它**不适合当触发后 gate**；更像该前置到“setup 预备状态预算”层。  
2. **一句话证明方式**：复用本地 `BTC/ETH/SOL 120d 15m` cache，统一 `next-bar open + hold 8 bars + no-overlap + 6/10/15bps`，比较 `baseline / depth15 / depth15+touch+green / repo_branch`。  
3. 关键数据（`6bps/side`）：
   - `baseline`：`mean_total_return = -3.66%`，`mean_trade_count = 34.67`
   - `depth15`：`-2.53%`，但 `retention = 99.05%`（几乎没筛选）
   - `repo_branch(深度+nearEMA+green+vol1.2+ADX25)`：`-2.47%`，但 `retention = 29.94%`、`positive_asset_ratio = 0/3`
4. 深度阈值扫一圈（同口径，6bps）后，`1.0%` 反而比 repo 默认 `1.5%` 更稳：
   - `depth<=1.0%`：`mean_total_return ≈ -1.34%`，`retention ≈ 92.66%`
   - `depth<=1.5%`：`mean_total_return ≈ -2.53%`，`retention ≈ 94.50%`

## 3. 为什么它直接服务当前三条收口线
- **EMA / PSAR raw alpha focus（最直接）**：这轮回答的是“回踩预算该放在哪一层”，属于 entry architecture，不是再加一个泛化指标。  
- **Fibonacci confirmation / retest_hold**：结论可迁移——“回踩深度预算”应优先作为 pre-condition，而非触发后再补刀。  
- **V3 breakout-short follow-up**：镜像后同理，`retest depth budget` 更像前置资格，不应和 post-break trigger 混成同层。  

如果问“为什么这题比继续做旧派生假设更值”：因为它是 **fresh repo-based**，且直接修正我们三线都在反复遇到的一个执行位错——**预算层 vs 触发层混用**。

## 4. 下一步怎么测（5m / 15m 最小实验）
### 4.1 数据与公开性
- 数据源：Binance Futures 公共 K 线（本轮复用本地 cache）
- 公开性：公开可得
- 更新频率：5m / 15m
- 本轮产物：
  - `reports/artifacts/quant_digests/vajra_controlled_pullback_proxy/candidate_events.csv`
  - `reports/artifacts/quant_digests/vajra_controlled_pullback_proxy/trade_log.csv`
  - `reports/artifacts/quant_digests/vajra_controlled_pullback_proxy/asset_summary.csv`
  - `reports/artifacts/quant_digests/vajra_controlled_pullback_proxy/overall_summary.csv`
  - `reports/artifacts/quant_digests/vajra_controlled_pullback_proxy/depth_threshold_sweep.csv`
  - `reports/artifacts/quant_digests/vajra_controlled_pullback_proxy/summary_snapshot.json`

### 4.2 最小可复现实验口径（建议先做这个）
下一轮不要再把 `depth<=x%` 接在 trigger 后面，改成 **pre-armed 状态机**：
1. 先定义 `armed_pullback`（过去 `N` 根内出现回踩，且 `depth<=x%`、nearEMA 成立）；
2. 只有在 armed 状态下，后续 `EMA/PSAR continuation trigger` 才可放行；
3. 对照三臂：
   - A：当前 baseline（触发即入场）
   - B：post-trigger depth gate（本轮已证伪近似无效）
   - C：pre-armed depth budget（主测试）
4. `x` 第一轮固定只测 `0.75% / 1.0% / 1.25%`，避免继续用过松 `1.5%`。

先看 4 个指标：
- `post_cost_expectancy`
- `trade_count_retention`
- `flip_to_fail_3bars_rate`
- `median_fwd3_ret`

## 5. 风险与保留意见
- 源 repo 明确写了 `BTC 1H`，不是 15m crypto 通用模板；
- 本轮是代理快检，不是完整 OOS 策略回测；
- `emaAngle` 在 Pine 里用原始价差换算角度，跨资产可移植性弱，本轮未把它当硬门；
- 当前结果不代表“pullback 预算无效”，只代表 **放在触发后这层几乎不产生信息增益**。

## 6. 来源
1. **Aatharva21. (2026). _BTC-EMA-based-strategy-1H- (Vajra)_.**
   - Venue: GitHub
   - DOI: N/A
   - Readable URL: <https://github.com/Aatharva21/BTC-EMA-based-strategy-1H->
   - Repo URL: <https://github.com/Aatharva21/BTC-EMA-based-strategy-1H->
2. **策略源码（Pine）**：`vajra_strategy.pine`
   - 关键规则：`pullbackLookback=5`、`maxPullbackPct=1.5`、`nearEMA`、`volume > 1.2*SMA20`、`ADX>=25`
   - Readable URL: <https://github.com/Aatharva21/BTC-EMA-based-strategy-1H-/blob/main/vajra_strategy.pine>
   - Raw URL: <https://raw.githubusercontent.com/Aatharva21/BTC-EMA-based-strategy-1H-/main/vajra_strategy.pine>
3. **仓库元数据（创建时间/更新）**
   - URL: <https://api.github.com/repos/Aatharva21/BTC-EMA-based-strategy-1H->
4. **公开行情数据源**
   - Binance Futures Klines API: <https://fapi.binance.com/fapi/v1/klines>
