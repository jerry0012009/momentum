# 别把这篇 2025 JBF 论文只读成“不确定性预测做市收益”：对 short-cycle desk，更该先测的是「market-maker style cross-sectional short-term reversal」这条 5m/15m raw alpha（但有明显 cost cliff）
- 时间：2026-04-02 18:45 UTC
- 类型：paper + Binance 公共数据最小 transfer / cost check
- 主题类型：raw alpha
- 基础 alpha：做市者式的横截面短期反转——上一根相对市场跌得更多的币做多、涨得更多的币做空，押注下一根价格向均值回归
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha / cross-sectional / mean reversion / liquidity provision / market making / short-term reversal / 5m / 15m / cost / turnover
- 证据类型：开放获取论文 + 本地 public-data proxy

## 1. 这次看了什么
这次主材料是 **Hisham Farag, Di Luo, Larisa Yarovaya, Damian Zieba (2025), _Returns from liquidity provision in cryptocurrency markets_, Journal of Banking & Finance, 175, 107411**。这篇 paper 表面上在讲“哪些日频不确定性变量能预测 liquidity provision premium”，但对我们 desk 来说，**最值得先 intake 的不是那些日频预测器，而是它拿来定义 liquidity provision premium 的那条 5 分钟横截面反转 raw alpha 本体**。

换句话说：
- `base alpha` 很清楚：**cross-sectional short-term reversal**
- `paper 里的 SPOTVOL / LTV / RV / risk aversion / Tether liquidity` 更适合后续当 gate / overlay
- 真正该先做的，是先问：**这条 raw alpha 在 5m / 15m、在 crypto perp 的现实成本下还剩多少？**

## 2. 论文里真正该抄的 alpha 定义
论文沿用 Nagel (2012) 的 liquidity provision 视角，把 market maker 提供流动性的收益写成一条横截面反转策略：

\[
LR_t = -\left(\frac{1}{2}\sum_i |R_{i,t-1}-R_{m,t-1}|\right)^{-1} \sum_i (R_{i,t-1}-R_{m,t-1})R_{i,t}
\]

直白翻译：
1. 先看上一根里每个币相对“横截面平均收益”是强是弱；
2. 上一根超跌的，下一根做多；
3. 上一根超涨的，下一根做空；
4. 权重按相对偏离幅度归一化，构成一条 dollar-normalized long-short 反转组合。

这就是一个非常标准、非常可复刻的 **raw alpha**：
- `entry`：每根 bar 收盘后，根据上一根相对市场偏离生成多空权重
- `exit`：下一根 bar 结束就换仓/平旧仓
- `sizing`：按相对偏离幅度分配；总 long/short 归一化
- `risk`：天然 market-neutral，但会有极高 turnover
- `cost`：必须显式建模，否则 gross edge 会被误读成可交易 alpha

## 3. 论文给了什么硬证据
我觉得最有用的几个数字是：
- 论文样本里，这条 **liquidity provision premium 的 5 分钟均值是 `0.720%`，标准差 `4.526%`**；作者强调它高度右偏，说明收益集中在少数“市场需要流动性”的时刻。
- 他们用日频变量去预测这条 5 分钟 premium，**out-of-sample `R²_OS` 在 `h=6` 时大约在 `4.22% ~ 4.62%`**，说明“什么时候这条 alpha 更肥”是有可预测性的。
- 在主回归 Model 5 里，预测器全部标准化后：
  - `SPOTVOL` 每升高 `1σ`，premium **下降 `0.260%`**
  - `LTV` 每升高 `1σ`，premium **上升 `0.100%`**
  - `RV` **上升 `0.056%`**
  - `Risk Aversion` **上升 `0.085%`**
  - `Tether liquidity shock` **上升 `0.187%`**
- 作者的核心经济解释是：**当中介/做市者更吃紧、尾部风险更大、稳定币流动性变化更剧烈时，提供流动性的补偿更高。**

但对我们 desk 来说，这些数字只说明第二层：**raw alpha 的肥瘦会变。第一层 alpha 本体仍然是短期横截面反转。**

## 4. 我做的 Binance 公共数据最小 transfer check
为了不只停在 paper 叙事，我直接用 **Binance USDⓈ-M 公共 K 线** 做了一个最小 proxy：
- 宇宙：`BTC / ETH / BNB / SOL / XRP / ADA / DOGE / LINK / AVAX / LTC`
- 频率：`5m`（14 天）和 `15m`（45 天）
- 信号：按论文 Eq.(1) 的横截面相对偏离构造 long-short 反转组合
- 成本：按组合 turnover 扣一边 `2 / 4 / 6 bps`

### 4.1 结果先说结论
**gross edge 明显存在，但 naive 连续换仓版有非常凶的 cost cliff。**

### 4.2 连续权重版（最接近论文公式）
- `5m`：gross 累计约 **`+16.0%`**，但平均每根 turnover **`1.42x`**；
  - 若按单边 `2bps`，net 变成 **`-63.1%`**
  - break-even fee 只剩大约 **`0.26bps` / 单边**
- `15m`：gross 累计约 **`+53.4%`**，平均每根 turnover **`1.43x`**；
  - 若按单边 `2bps`，net 变成 **`-55.3%`**
  - break-even fee 大约 **`0.70bps` / 单边**

这说明：**alpha 本体不是没有，而是“连续、满功率、每根重配”的实现方式太贵。**

### 4.3 稀疏版 quick patch（top-2 loser vs top-2 winner，延长持有）
我又做了一个更 desk-friendly 的稀疏 proxy：
- 每根只做 `top-2 loser` vs `top-2 winner`
- 不每根都完全翻仓，而是把持有期拉长

结果：
- `15m`、持有 `8` 根时：gross 仍有 **`+11.5%`**，平均 turnover 降到 **`0.198x` / rebalance`**
- 但在单边 `2bps` 下，net 仍约 **`-6.0%`**
- 对应 break-even fee 约 **`1.29bps` / 单边**

我的读法是：**它已经从“完全不现实”走到了“只差 execution / maker 化 / 稀疏化再砍一刀”的区间**，所以值得留在素材池，但当前不能把 naive 版本当成可直接实盘的完整策略。

## 5. 为什么这条东西仍值得收进研究池
因为它补的是我们当前比较需要的 **mean reversion / cross-sectional / liquidity-provision raw alpha**，而且是：
- base alpha 非常清楚
- 公共数据可做
- 可直接映射到 `5m / 15m`，甚至 `1m / 3m`
- 后续还能自然挂上 filter / regime / execution veto

更重要的是，这篇 paper 给了一个很好的研究分层：
1. **第一层：raw alpha 本体** —— market-maker style short-term reversal
2. **第二层：什么时候更值得开** —— volatility / tail risk / stablecoin liquidity gate
3. **第三层：怎么别被成本杀死** —— sparse execution / maker priority / slower refresh / bucket trade

## 6. 策略拆解（按 desk 语言重写）
- 方向属性：cross-sectional / market-neutral / short-term mean reversion
- 基础 alpha：上一根相对市场超涨/超跌的币，在下一根发生反转
- regime：流动性吃紧、尾部风险高、市场需要“有人接单”时，这条 alpha 往往更肥
- filter / veto：不一定要把 paper 的日频变量直接照搬成主信号，更适合拿来做开关或 risk budget
- risk / sizing / execution overlay：
  - 限 universe 到最液态 perp
  - 只做 top/bottom 极端分位，不做全横截面满配
  - 延长持有或分批换仓，砍 turnover
  - 优先 maker / queue-friendly 执行
  - 必须把真实成交成本、funding、滑点、missed fill 全算进去

## 7. 下一步怎么测
我建议按下面顺序，而不是直接把论文原式拿去跑：

### Step 1：先测“稀疏化能不能救成本”
a. `15m` 主频，`5m` 备选
b. 宇宙只保留 `10~20` 个最液态 perp
c. 只做 `top 10% loser` / `top 10% winner`
d. 持有 `2 / 4 / 8` 根，对比 turnover 下降和 edge 衰减

### Step 2：再测“gate 能不能把肥段挑出来”
a. 用 paper 里的思想，但换成 desk 能快速拿到的 proxy：
- 市场 realized vol
- 横截面 dispersion
- stablecoin flow proxy（若拿得到）
- 大盘下跌 / liquidation cluster proxy
b. 问题不是“预测收益方向”，而是：**什么时候值得开 liquidity-provision alpha**

### Step 3：最后才测 execution
- maker-only / maker-first
- quote life
- fill ratio
- queue decay
- 部分成交后 residual inventory 风险

如果 Step 1 做完后，在 `15m` 稀疏版下，break-even fee 仍显著低于我们真实可拿到的 fee + slippage，那就别继续浪费时间抠花活了；如果能把 break-even 拉到 `1.5~2.0bps+` 单边，再值得往 execution 走。

## 8. 我当前的判断
这篇 paper **值得进研究池，但更像“raw alpha 候选 + 明确成本红线”**，而不是今天就能无脑上线的策略。

一句话判断：
**alpha 是真的，问题不是有没有 edge，而是它现在更像“做市补偿”而不是“白送方向收益”；如果 execution 不够强，edge 会被 turnover 吃光。**

## 9. 来源与复现入口
- Farag, Hisham; Luo, Di; Yarovaya, Larisa; Zieba, Damian (2025). *Returns from liquidity provision in cryptocurrency markets*. **Journal of Banking & Finance**, 175, 107411.
  - DOI: `10.1016/j.jbankfin.2025.107411`
  - Readable URL: `https://www.sciencedirect.com/science/article/pii/S0378426625000317`
  - Open PDF URL: `https://pure-oai.bham.ac.uk/ws/portalfiles/portal/264447617/Farag2022Returns.pdf`
  - Alt metadata URL: `https://ideas.repec.org/a/eee/jbfina/v175y2025ics0378426625000317.html`
- 本地 artifacts：
  - `reports/artifacts/quant_digests/liquidity_provision_proxy_summary_20260402.csv`
  - `reports/artifacts/quant_digests/liquidity_provision_proxy_5m_20260402.csv`
  - `reports/artifacts/quant_digests/liquidity_provision_proxy_15m_20260402.csv`
  - `reports/artifacts/quant_digests/liquidity_provision_sparse_proxy_20260402.csv`
