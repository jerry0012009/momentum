# 别把《Short-Term Basis Reversal》只读成商品期限结构论文：对 short-cycle crypto desk，更该先拆的是「近远月相对回报差的短期反转」这条 raw alpha

- 时间：2026-04-23 13:28 UTC
- 类型：2025 SSRN 论文 metadata audit（Crossref）+ 持续更新复现实验仓 audit（rolling-panda-san/notebooks）+ Binance COIN-M public-data portability probe（`BTCUSD/ETHUSD`，`15m`）
- 主题类型：raw alpha
- 基础 alpha：**近端合约相对次近端合约若在刚过去的短窗里跑得过快（`Ret_front - Ret_back` 明显为正/负），下一短窗这段 spread return 往往会向反方向回摆；交易上做“front/back 相对回报差”的 fade，而不是做单腿方向预测。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/relative-value/stat-arb/carry/basis/term-structure/short-term-reversal/front-back/spread-return/15m/5m/paper/repo/public-data/cost/risk
- 证据类型：paper metadata + repo source + public API portability probe

## 1) 这次看了什么
主线材料：
- **Alberto G. Rossi, Yingguang Zhang, Yandi Zhu (2025)**
- **Title：** *Short-Term Basis Reversal*
- **Venue：** SSRN Electronic Journal
- **DOI：** `10.2139/ssrn.5250499`
- **Readable URL：** <https://doi.org/10.2139/ssrn.5250499>
- **Repo URL：** N/A（论文官方公开代码未检索到）

复现实验仓：
- **rolling-panda-san/notebooks**（持续更新至 2026-04-23）
- **Repo title：** *Analysis on systematic trading strategies*
- **Repo URL：** <https://github.com/rolling-panda-san/notebooks>
- **相关 notebook：** `commodity_basis_reversal.ipynb`
- **可读 raw URL：** <https://raw.githubusercontent.com/rolling-panda-san/notebooks/master/commodity_basis_reversal.ipynb>

先把 base alpha 说清楚：
> **这条线的 base alpha 不是“商品曲线形状本身”，而是“前一短窗 front-vs-back 的相对回报差会短期反转”。**

翻成人话：
- 如果近端合约刚才比次近端涨得快很多，这个“basis spread return shock”下一小段往往会回吐；
- 如果近端刚才明显跑输次近端，下一小段也常见反向修复；
- 所以它本质上是 **term-structure relative-value mean reversion**，不是趋势跟随，也不是低频 carry 收租。

这很适合当前 desk，因为它天然就是：
- `raw alpha`
- `relative value / stat-arb`
- 可拆成 `1m/3m/5m/15m` 的 child execution
- 可以独立于单腿方向判断存在

---

## 2) 从论文和复现实验仓里，真正该保留什么
repo `commodity_basis_reversal.ipynb` 给出的关键信息不是“商品有效，所以 crypto 也一定有效”，而是：

1. **信号定义足够简单**
   - 核心量是前端与次前端合约回报差：
   - `SRet_t^(F1-F2) = Ret_t^F1 - Ret_t^F2`
2. **它可以做成 cross-sectional，也可以做成 time-series**
   - 仓里既做了横截面 ranking，也做了单品种 sign-based reversal
3. **它本质上是 spread return 的短期反转，不依赖复杂特征工程**
4. **可直接转写成 crypto 的 perp-vs-quarterly / near-vs-far basis shell**

对 crypto desk，最值得先拿走的不是论文里商品横截面组合的长期表现，而是这个更短链路的命题：

> **在同一标的的近远月结构里，刚刚发生的期限结构冲击，下一短窗是否存在可交易的反向修复？**

如果这个命题在 crypto 成立，它就是一条非常干净的短周期 raw alpha；
如果只在高 carry / 高噪声阶段才成立，它也仍然可以转成一个很好的 `regime gate` 服务于 basis / funding / spread 系策略。

---

## 3) 本轮最小 public-data portability probe（Binance COIN-M，`15m`）
### 3.1 数据口径
为了不依赖私有数据，这轮只做最小可复现实验：

- 交易所：Binance COIN-M public API
- 合约对：
  - `BTCUSD` `PERPETUAL` vs `CURRENT_QUARTER`
  - `ETHUSD` `PERPETUAL` vs `CURRENT_QUARTER`
- 周期：`15m`
- 样本：最近 `1500` 根 `15m` bar（约 15.6 天）
- 定义：
  - `r_perp_t = close_perp_t / close_perp_{t-1} - 1`
  - `r_cq_t = close_cq_t / close_cq_{t-1} - 1`
  - `sret_t = r_perp_t - r_cq_t`
- 最小可交易解释：
  - 若上一根 `sret_{t-1}` 为正，表示 perp 刚刚相对 current quarter 跑太快；下一根做 `short perp / long current-quarter`
  - 若上一根 `sret_{t-1}` 为负，则反向

也就是最简单的 1-bar fade：
- `pos_t = -sign(sret_{t-1})`
- `pnl_t ≈ pos_t * sret_t`

产物：
- `reports/artifacts/quant_digests/2026-04-23_1328_shortterm_basis_reversal_probe_raw.csv`
- `reports/artifacts/quant_digests/2026-04-23_1328_shortterm_basis_reversal_probe_summary.csv`

### 3.2 关键结果（先给 4 个最有用的数据点）
1. **lag-1 反转非常明显**
   - BTC：`lag1 autocorr = -0.492`
   - ETH：`lag1 autocorr = -0.524`
2. **不设阈值的 next-bar fade 也有正均值**
   - BTC：`uncond avg pnl = +1.52 bps/bar`，`win rate = 65.3%`
   - ETH：`uncond avg pnl = +1.89 bps/bar`，`win rate = 64.8%`
3. **大一点的 spread shock 更值钱**
   - 当 `|sret_{t-1}| >= 3 bps`：
     - BTC：`avg next-bar pnl = +2.81 bps`，`win rate = 74.5%`，`n = 631`
     - ETH：`avg next-bar pnl = +3.36 bps`，`win rate = 75.3%`，`n = 695`
4. **`4 bps` 级别的前一根 shock 开始接近“可与成本对话”的区间**
   - BTC：`|sig|>=4bps` 时，`avg next-bar pnl = +3.48 bps`，`win rate = 77.9%`
   - ETH：`|sig|>=4bps` 时，`avg next-bar pnl = +3.91 bps`，`win rate = 77.2%`

翻成人话：
- “刚刚哪一腿跑太快，下一根大概率往回拉” 这件事，在 Binance 近远月结构里是**能看到的**；
- 而且不是只有很极端的几笔样本才成立；
- 但 **edge 量级还没有大到可以无视成本**，所以它更像一条需要门槛、需要执行优化的 raw alpha，而不是裸市价冲进去的免费午餐。

---

## 4) 这条线对当前 desk 的真正价值
### 4.1 它是 raw alpha，不是纯 filter
因为交易对象和方向都能单独定义：
- long 哪腿 / short 哪腿
- 何时开 / 何时平
- cost 怎么计
- 风控怎么做

所以它不是“basis 大时别做别的策略”这种附属判断，而是可独立部署的一条 relative-value alpha。

### 4.2 它比“低频 carry 收租”更贴近当前短周期研发
很多 basis / funding 题材会滑到：
- 8h funding carry
- 日频期限结构
- 低周转持仓

而这条线的优势恰恰在于：
- **主信号是上一短窗的 spread-return shock**
- **理论上天然适合 `5m/15m`，甚至可以往 `1m/3m` 压缩**
- 更像短周期相对价值回归，而不是拿个慢因子硬塞进高频执行壳

### 4.3 它与最近 digest 不重复
近期已经做过：
- spot-perp basis fade
- perp-perp funding diff z-fade
- 多种 pairs / cointegration / cross-venue outlier

这轮不同之处在于：
- **不是跨 venue**，而是**同 venue 内的 near-vs-far term structure**；
- **不是静态 basis level**，而是 **basis spread return 的短期反转**；
- **不是 carry 水平排序**，而是 **shock → repair 的短窗回归**。

---

## 5) 可直接落地的完整策略壳
### 5.1 Entry（入场）
以 `15m` 为 parent signal：

1. 计算 `sret_t = r_front_t - r_back_t`
2. 定义上一根冲击强度 `shock_bps = |sret_{t-1}| * 1e4`
3. 仅在 `shock_bps >= theta_enter` 时入场
4. 入场方向：
   - 若 `sret_{t-1} > 0`：`short front / long back`
   - 若 `sret_{t-1} < 0`：`long front / short back`

建议初始阈值：
- BTC：`theta_enter = 3.0 ~ 4.0 bps`
- ETH：`theta_enter = 3.0 ~ 4.0 bps`

不要一开始就用 `1 bps`，因为那更像统计意义存在，但未必能穿过真实手续费。

### 5.2 Exit（出场）
优先从最朴素的三种出场开始 A/B test：

- **time stop**：固定持有 `1 bar`（先对齐本轮 probe）
- **spread repair exit**：若本根实时 `sret` 已回到 `0` 附近，提前平
- **stop**：若持仓后 `sret` 继续朝不利方向扩大到入场冲击的 `1.5x ~ 2.0x`，强制止损

### 5.3 Sizing（仓位）
- 基础做法：等名义 delta-neutral
- 再进一层：按 `shock_bps / recent_spread_vol` 分 3 档仓位
- 同时给单腿做 cap：
  - `per_symbol_cap`
  - `per_expiry_cap`
  - `per_term_bucket_cap`

### 5.4 Risk（风控）
- rollover 附近禁开新仓
- 合约成交深度不足时禁开
- 若一腿成交另一腿未成交，超过 `x` 秒未补齐则立刻减半/撤退
- funding 结算点附近单独建黑名单窗口
- 大行情新闻窗口（CPI / FOMC / ETF headlines）单独降权，因为那时期限结构冲击可能不是“误差修复”，而是“新信息定价”

### 5.5 Cost（成本）
这条线最怕的是“理论有 edge，执行后被吃光”。

建议 friction ladder 至少做：
- `2 bps round-trip`
- `4 bps round-trip`
- `6 bps round-trip`

当前 probe 给出的含义是：
- 裸跑全样本，`1.5~1.9 bps/bar` 不够安心；
- 加阈值后到 `3~4 bps` 冲击样本，才开始勉强进入能跟 `2~4 bps` 成本对话的区间；
- 所以 **这条线默认应该是 maker-first / passive-first，或至少 child execution 优化优先**。

---

## 6) 对 `1m / 3m / 5m / 15m` 的映射
### `15m`
最自然的第一版 parent signal 周期，和本轮 public-data probe 一致。

### `5m`
最值得做的下一步：
- 继续用 `15m` 判断大冲击是否成立；
- 但把执行拆到 `5m` 子 bar，观察 repair 是否主要发生在前 `1~2` 个 `5m`。

### `1m / 3m`
更像二阶段升级：
- 先确认 `15m`/`5m` parent signal 有净边；
- 再压到 `1m/3m` 找更精细的入场（例如 micro pullback 后挂单补腿），而不是直接跳去超短频裸做。

---

## 7) 这轮结论应该怎么用
### 结论 1：可以进 raw alpha 素材池
因为它满足：
- base alpha 清楚
- 可独立复现
- 可直接落地完整策略壳
- 与近期 intake 重复度低

### 结论 2：但当前更像“值得继续做的 alpha 壳”，不是已确认可实盘上线
原因不是信号不明显，而是：
- 当前只做了单 venue、连续合约、近 15 天、next-bar 粗测；
- 还没把真实 roll、盘口深度、双腿成交、fee tier、maker ratio 放进去。

### 结论 3：如果后续成本压不过去，也别丢
即使最终发现它单独做不够厚，也很可能还能保留下来作为：
- basis / funding 策略的 execution veto
- near-vs-far router
- term-structure shock regime gate

但那是降级后的用途；**当前默认仍把它视作 raw alpha 候选。**

---

## 8) 下一步怎么测（必做）
1. **把单 venue continuous contract probe 升级为真实合约级回测**
   - 不再只用 continuous series；
   - 明确 front / next 合约切换与 roll window；
   - 避免 continuous stitching 夸大可交易性。

2. **做 `15m parent -> 5m child execution` 的两层实验**
   - parent：`shock_bps >= {2,3,4,5}`
   - child：下一 `1~3` 个 `5m` 内分段挂单或 VWAP 补腿
   - 看净边是否优于“下一根 15m 直接开平”。

3. **扩到更多币种与更多 term buckets**
   - 至少补 `BTC / ETH / SOL`（若有可交易季度合约）
   - 比较 `PERP vs CURRENT_QUARTER` 和 `CURRENT vs NEXT_QUARTER`

4. **显式加入成本与成交约束**
   - maker/taker 两套
   - 不同 fee tier
   - 双腿最小可成交名义
   - 单腿未成交风险

5. **做“高 carry / 低 carry / funding flip”分层**
   - 检查这条短期反转，是不是只在 basis 已经很高或 funding 很偏的时候更强；
   - 若是，就把它进一步拆成 `raw alpha + regime gate` 结构。

---

## 9) 风险与保留意见
- 论文正文本轮未拿到全文，当前对论文的直接证据仍以 Crossref metadata 为主。
- rolling-panda-san 的 notebook 使用私有 `vivace` 库，**可读但不能直接原样跑**；好处是信号定义已经足够清楚，仍可独立重写。
- 本轮 crypto probe 是 **Binance COIN-M continuous contracts 的 portability test**，不是严格 paper replication。
- 连续合约会弱化 roll 细节；正式回测必须回到真实 expiry 级别。
- 当前结果是“有短期回摆现象”，不是“已经证明扣完成本后稳定赚钱”。

---

## 10) 来源
1. **Rossi, A. G., Zhang, Y., & Zhu, Y. (2025). _Short-Term Basis Reversal_. SSRN Electronic Journal.**
   - DOI: <https://doi.org/10.2139/ssrn.5250499>
   - Readable URL: <https://doi.org/10.2139/ssrn.5250499>
   - Repo URL: N/A
2. **rolling-panda-san/notebooks**
   - Repo URL: <https://github.com/rolling-panda-san/notebooks>
   - Relevant notebook: <https://github.com/rolling-panda-san/notebooks/blob/master/commodity_basis_reversal.ipynb>
3. **本轮最小实验产物**
   - `reports/artifacts/quant_digests/2026-04-23_1328_shortterm_basis_reversal_probe_raw.csv`
   - `reports/artifacts/quant_digests/2026-04-23_1328_shortterm_basis_reversal_probe_summary.csv`
