# 别把这份 2025 repo 只读成 funding carry 观察表：对 short-cycle desk，更该先测的是「annualized basis − implied funding gap × convergence band shell」

- 时间：2026-04-07 05:51 UTC
- 类型：GitHub / 项目报告 / notebook
- 主题类型：raw alpha
- 基础 alpha：**交割合约年化 basis 与永续 funding 年化之间的脱锚会回归；当季度合约相对“funding 隐含 carry”过贵时，做多现货/近似现货、做空交割合约；反之反手。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha / relative-value / carry / funding / basis / mean-reversion / btc / binance / 5m / 15m / repo / public-data / cost
- 证据类型：工程经验

## 1. 这次看了什么
这次看的是 **Grant Belford (2025)** 的 GitHub 仓库 **Basis-Funding-MR-Strat**，核心材料包括：
- repo 内 PDF：**BTC Basis-Funding Spread Trading Analysis**（日期 `2025-04-01`）
- repo 内 notebook：`Binance-Basis-FundingRate-MR-Apr25.ipynb`

它真正值得我们 intake 的，不是“funding 能不能收租”，而是更像一个 **carry/relative-value raw alpha**：
**季度合约的年化 basis 和永续 funding 年化，本质上都在给 BTC 的持有成本/拥挤度定价；两者短期脱锚过大，往往会往回收。**

## 2. 核心结论
- **一句话核心结论：** 这份 repo 最值钱的不是 funding 方向判断，而是 **`basis_ann - funding_ann` 这条 carry 差值本身可以交易回归**。
- **一句话证明方式：** 作者直接用 Binance 公共 BTC spot / quarterly futures / perp funding 数据，先算年化 basis、再和 funding 年化做差，用阈值进出场和成本回测验证它的收敛性。
- PDF 里的主回测样本是 **`2024-06-28 ~ 2024-12-01`**；简单阈值壳并不夸张：**总收益 `1.60%`、年化 `3.78%`、Sharpe `1.95`、最大回撤 `-1.42%`、仅 `7` 笔 round-trip**。这说明它更像 **低频 RV/carry alpha**，不是高频暴利脚本。
- repo 的 notebook 把信号写得很直白：`spread = basis_annual_pct - funding_annual_pct`；默认 **入场阈值 `5%`，出场阈值 `1%`**，单笔名义本金 `10,000 USD`，每边手续费 `5 bps`。
- 更关键的是 PDF 里给了 **mean-reversion diagnostics**，这比主回测收益更值钱：
  - **11 次极端 spread episode 里有 9 次在 5 天内回归**；
  - 常态下 **半衰期约 `5~7` 天**，冲击后可缩到 **`2~3` 天**；
  - 当 **Hurst < `0.35` 且半衰期 < `5` 天** 时，历史上 **`86%`** 的 episode 最后盈利。  
  对我们 desk 来说，这意味着：**raw alpha 是 gap close，本轮真正可复用的是“half-life / Hurst / gap-zscore 做 admission”这层。**

## 3. 为什么和当前项目有关
这条线和当前 `momentum` 很相关，因为它补的是我们一直在找的 **raw alpha 素材池里的 carry / relative-value / stat-arb 分支**，而不是再做一层抽象解释。

更重要的是，它给了一个对 short-cycle 更友好的改写方向：
- repo 原版是 **spot vs quarterly futures**；
- 但对我们 desk，更实用的实现通常是 **perp 充当近似现货腿 / hedge 腿**，把 alpha 核心保留成：
  **“交割合约 basis 相对 funding 隐含 carry 过贵/过便宜，之后做 convergence。”**

也就是说，这轮最值得抄的不是“原样照搬 spot 腿”，而是：
1. **保留 `basis-funding gap` 这个 raw alpha 本体**；
2. **把 half-life / Hurst / z-score 变成 admission layer**；
3. **把执行腿改成更贴 desk 的 perp-vs-delivery / perp-vs-synthetic-spot 壳。**

## 3.5 策略拆解（必填）
- 方向属性：**相对价值 / carry / stat-arb**
- 基础 alpha：**`gap_t = annualized_basis_t - annualized_funding_t` 的均值回复 / 收敛**
- regime：**只在 gap 极端、且 half-life 较短、Hurst 偏低时交易；临近交割最后几天默认降级或停机**
- filter / veto：**流动性不足、合约快到期、funding 刚发生剧烈 sign-flip、gap 尚未覆盖成本时不做**
- risk / sizing / execution overlay：**固定双腿名义仓位、明确 fee hurdle、最大持有时长、gap 继续恶化时的 hard stop / time stop；执行上优先考虑 perp-vs-quarterly 而非硬做 spot short**

## 4. 可复刻的最小实验
**研究假设：** 在 BTC 上，季度合约年化 basis 与永续 funding 年化的偏离会收敛，这个收敛可以迁移到 `5m / 15m` 级别做最小实验。

**一个可计算定义：**
```python
basis_ann_t = ((F_quarter_t / S_proxy_t - 1) / days_to_expiry_t) * 365 * 100
funding_ann_t = funding_rate_last_t * 3 * 365 * 100   # 8h funding 年化
gap_t = basis_ann_t - funding_ann_t
```
其中 `S_proxy_t` 第一轮可先用 **BTCUSDT perp mark** 或 spot 价格。

**最小回测切口：**
- 标的：Binance BTC 最近季度交割合约 + BTCUSDT perp
- 周期：先做 `15m`，再下探 `5m`
- 样本：至少覆盖 `4` 次季度滚动（避免只看一季）
- 交易规则（第一轮先朴素）：
  - `gap_t > +5pp` 或 `gap_z > 2`：**做多近似现货腿 / 做空交割合约**
  - `gap_t < -5pp` 或 `gap_z < -2`：**做空近似现货腿 / 做多交割合约**
  - `|gap_t| < 1pp`、`gap_z` 回到 `0` 附近、或达到最大持有时长就平仓
- 先看两项：
  1. **成本后 expectancy / Sharpe**
  2. **gap 在 `1/2/3` 天内关闭的比例**

如果第一轮想更 desk-fit，我会优先加一个 admission：
**只有当 rolling half-life < 5 天、且 Hurst < 0.35 时才允许开仓。**

## 5. 风险与保留意见
- **repo 当前样本偏短、交易数很少。** 只有 `7` 笔 round-trip，说明这更像“结构性低频机会”，不是可以直接拿来吹成高频 cash machine 的东西。
- **原版执行腿有 desk friction。** 现货腿在真实环境里会遇到借币、融资、划转、库存占用等问题；所以第一轮更适合改成 perp proxy，而不是盲抄现货 short。
- **funding 天生低频。** 它每 `8h` 更新一次，所以不要把它伪装成逐根新信息；更合理的读法是：**basis 在高频动，funding 是慢变量锚。**
- **临近交割时 curve 形状会变。** 若不单独处理 `days_to_expiry`、roll 和最后几天流动性，回测很容易失真。

> **最值得复用/复现的点：不是原 repo 的“固定 `±5% / 1%` 阈值”，而是 `basis-funding gap` 这个 raw alpha 本体，加上 `half-life / Hurst` 这层 admission。**

## 6. 来源
1. **Grant Belford. (2025). _Basis-Funding-MR-Strat_. GitHub repository.**  
   - Repo URL: `https://github.com/grantbelford/Basis-Funding-MR-Strat`
2. **Grant Belford. (2025-04-01). _BTC Basis-Funding Spread Trading Analysis_. Project report (PDF in repo).**  
   - Readable URL: `https://github.com/grantbelford/Basis-Funding-MR-Strat/blob/main/BTC_Spread_Trading_Report_Final.pdf`
3. **Grant Belford. (2025). _Binance-Basis-FundingRate-MR-Apr25.ipynb_. Notebook in repo.**  
   - Readable URL: `https://github.com/grantbelford/Basis-Funding-MR-Strat/blob/main/Binance-Basis-FundingRate-MR-Apr25.ipynb`
4. **Binance Futures API docs — Funding Rate History / Premium Index / Klines.**  
   - Funding history URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Get-Funding-Rate-History`
   - Public data portal: `https://data.binance.vision/`
