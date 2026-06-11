# 别把这份 2025 IV-RV repo 只读成“对称 long/short vol 教程”：对 short-cycle desk，更该先测的是「BTC rich-IV short straddle carry」这条 raw alpha
- 时间：2026-04-15 05:38 UTC
- 类型：2025 GitHub repo source audit（`README.md` + `build_weekly.py` + `backtest.py`）+ Deribit DVOL / ETHVOL 与 Binance public-data probe
- 主题类型：raw alpha
- 基础 alpha：当 BTC 短天期隐含波动率（IV proxy）显著高于 trailing realized volatility（RV）时，做 **short ATM straddle / short vol carry**，赚取“隐含波动率偏贵但未来已实现波动率没有同步跟上”的 risk-premium / carry 收敛。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / options / carry / relative-value / volatility-risk-premium / short-vol / straddle / deribit / btc / 5m / 15m / repo / public-data / cost / risk
- 证据类型：repo 源码 + 公开行情 probe

## 1. 这次看了什么
这次看的是 GitHub 仓库 **khalil-benzina / Crypto-IV-RV-Straddle-Carry**（2025）。

repo 表面写的是一条很对称的策略：
- 若 `RV > IV`，做多 ATM straddle；
- 若 `IV > RV`，做空 ATM straddle；
- 用下一周 realized vol 与当前 IV 的差值记 proxy PnL。

但对我们这个 desk 来说，**真正值得 intake 的不是这条“对称 long/short vol”原样照抄版**，而是 repo 里更适合交易台落地的旁支：

> **只在 BTC 的 IV 明显贵于 trailing RV 时做 short-vol carry；不要默认对称去接 long-vol。**

原因很简单：
1. **base alpha 清楚**：不是宏观故事，也不是 filter；本体就是 `IV rich to trailing RV -> forward RV 仍低于 IV` 的 carry / risk-premium 收敛。
2. **补的是当前池子里相对少的一块**：不是再做一条 pairs / funding / lead-lag，而是 **options vol carry**。
3. **repo 给的最小实验成本很低**：Deribit 公共 DVOL 指数 + 公共现货/期货价格就能先做第一轮 falsification。

## 2. 核心结论
### 2.1 先回答 base alpha
**这篇东西的 base alpha 是什么？**

不是“波动大就别做趋势”这种 overlay，也不是“市场恐慌时期权更贵”这种解释层。它的 base alpha 就一句：

> **当 ATM / short-dated implied vol 明显高于近期已实现波动率，而下一周 realized vol 并没有继续爆上去时，short straddle / short vol carry 有正的风险溢价。**

这是标准的 **raw alpha / carry / relative-value**，不是 filter。

### 2.2 repo 原始对称版，不是最适合我们 desk 的读法
我按 repo 的最小口径，用：
- **Binance 日线 close** 估 `trailing 7d RV` 与 `next 7d RV`
- **Deribit `public/get_volatility_index_data`** 取 `DVOL / ETHVOL` 作为 `IV proxy`
- 每周五取一个 snapshot

先跑了 repo 的对称 long/short proxy。结果：

#### BTC（2023-07-21 至 2026-04-03，`141` 个周样本）
- **对称 long/short**：
  - avg proxy PnL ≈ **`0.0371`**
  - Sharpe ≈ **`0.17`**
  - win rate ≈ **`60.3%`**
- **always short vol**：
  - avg proxy PnL ≈ **`0.0692`**
  - Sharpe ≈ **`0.33`**
  - win rate ≈ **`71.6%`**

这说明一个很关键的事：

> **repo 的“IV<RV 就去 long vol”这半边，在 BTC 上并没有帮你增厚 edge，反而拖累了更朴素的 short-vol carry。**

#### ETH（同样 `141` 个周样本）
- **对称 long/short**：Sharpe ≈ **`0.04`**
- **always short vol**：Sharpe ≈ **`0.09`**

ETH 这条线明显更弱，至少在这版 proxy 下，不值得作为第一优先落点。

### 2.3 真正更值得 desk 先测的是：BTC rich-IV only
我进一步把它改成更交易台化的版本：

- 只在 `IV - trailing RV` 处于历史高分位时出手；
- 只做 **short vol**；
- 其它时候宁可空仓，不默认接 long-vol。

结果反而更像一个可以继续追的 raw alpha：

#### BTC：只做 `IV-RV` 位于历史 **top 30%** 的 rich-IV 周
- 交易次数：**`42`**
- avg proxy PnL ≈ **`0.0895`**
- Sharpe ≈ **`0.57`**
- win rate ≈ **`78.6%`**

也就是说，这个 repo 对 desk 最值钱的读法不是“做一条对称 vol timing 策略”，而是：

> **把 `IV 很贵` 当成 admission，只在 rich-IV 状态下做 BTC short straddle carry。**

这比继续补一个 shared filter 更值得写，因为它本体就是一条 **carry / options relative-value raw alpha**。

## 3. 为什么和当前项目有关
这轮值得做它，而不是继续补一条 pair / spread / breakout，原因有三点：

1. **补 raw alpha 素材池的空白**  
   我们最近 relative-value / pairs / funding / lead-lag 很多，但 **options-vol-carry** 这一块还不够厚。

2. **它和短周期 desk 不是冲突关系，而是“信号慢、执行快”关系**  
   这条 alpha 的状态定义可以是周频 / 日频，但 entry、hedge、风控、平仓都完全可以放到 `5m / 15m`：
   - `5m` 监控 IV-RV spread 是否回补
   - `5m` 做 BTC perp delta hedge
   - `5m/15m` 做 gamma / loss / basis 失控 veto

3. **公开数据可拿，最小实验门槛低**  
   - Deribit DVOL / ETHVOL：公共 API，可小时级更新
   - Binance / Deribit 标的价格：公共 API，可 `1m/5m/15m`
   - 再往前一步就能切到真实 option chain mid-IV / ATM straddle mid，而不是停留在故事层

## 3.5 策略拆解（必填）
- 方向属性：options / carry / relative-value / volatility risk premium
- 基础 alpha：`IV rich to trailing RV -> forward RV does not catch up -> short straddle earns carry`
- theme 定位：**raw alpha**，不是 filter / regime / overlay
- 交易对象：Deribit BTC short-dated ATM straddle（优先 next Friday / 5d~9d 到期）
- entry：
  - `IV_proxy - RV_trailing >= q70` 或 rolling z-score 超阈值
  - 优先只做 BTC；ETH 先不作为主落点
- exit：
  - `IV-RV` spread 回落到 `q40` 以下；或
  - 剩余到期 `< 24h`；或
  - 亏损 / realized vol shock / basis blowout 触发硬止损
- sizing：按 vega target / gamma cap / max notional 控制，不按名义本金裸卖
- hedge：用 BTC perp 每 `5m` 做 delta refresh；高波动时可切到 `1m`
- 主要风险：short gamma、jump risk、skew/term-structure 漂移、option spread、hedge 频率不足、funding / basis
- 成本：option bid-ask + option taker/maker fee + perp hedge fee + funding + 滑点

## 4. public-data first probe（这轮最关键的实证）
### 4.1 数据源、公开性、更新频率
- **Deribit volatility index API**：`public/get_volatility_index_data`
  - 公开性：公开可得
  - 更新频率：可小时级取样
  - 用途：先做代理 IV 指数
- **Binance daily close / public kline**
  - 公开性：公开可得
  - 更新频率：可 `1m/5m/15m/1d`
  - 用途：先算 trailing / forward RV

### 4.2 这轮最小可复现实验口径
1. 每周五取一次 snapshot；
2. `RV_trailing = trailing 7d annualized realized vol`；
3. `IV_proxy = Deribit DVOL/ETHVOL`；
4. `RV_forward = next 7d annualized realized vol`；
5. proxy PnL：
   - always short vol：`IV_proxy - RV_forward`
   - 对称版：若 `IV>RV_trailing` 则 short，否则 long
   - desk 版：仅当 `IV-RV_trailing` 大于历史 `q70` 时 short，其他时间 flat

### 4.3 first verdict
**BTC 有戏，但不是 repo 原样那种“对称 long/short”。**

更准确的 first verdict 是：
- **BTC rich-IV short-only 值得继续测；**
- **ETH 暂不优先；**
- **long-vol 那半边别先默认相信。**

### 4.4 当前最新状态（最近完整周：`2026-04-10`）
- BTC：
  - `RV7 ≈ 35.2%`
  - `DVOL ≈ 43.1%`
  - `IV - RV ≈ +7.9 vol pts`
- ETH：
  - `RV7 ≈ 50.7%`
  - `ETHVOL ≈ 64.3%`
  - `IV - RV ≈ +13.7 vol pts`

注意：
- 这说明 **当前确实还是 rich-IV 状态**；
- 但 BTC 的 `+7.9 vol pts` 还**不到我这轮 probe 里 q70 的强 admission 区**（大约 `+17.3 vol pts`），所以更像“偏贵但不极端”，不是一定要立刻裸上 size 的状态。

## 5. 对 short-cycle desk 的正确落地方式
别把它理解成“这是一条周频策略，所以和 `5m/15m` 无关”。更合理的 desk 化方式是：

- **状态定义**：日频 / 小时级看 `IV-RV`
- **执行时钟**：`5m`
- **hedge 时钟**：`1m~5m`
- **风控时钟**：`5m/15m`

也就是说：

> **alpha 本体是 options vol carry；short-cycle 的职责不是把它伪装成逐 bar 方向预测，而是把 entry、delta hedge、risk veto、early exit 做快。**

这和 funding / basis / lower-bound options event 是同类思路：**信号未必每根 bar 变化，但执行与风控必须短周期。**

## 6. 风险与保留意见
1. **这轮 PnL 还是 proxy，不是真实 option book PnL**  
   目前只是用 `IV_proxy - RV_forward` 做第一轮筛选，还没进入真实 straddle mid、vega、gamma、theta、hedge cost 的完整回放。

2. **short vol 天生怕跳变**  
   再漂亮的平均 carry，也可能被单次 vol explosion 吃穿。

3. **DVOL 不是你真实成交的那只 straddle**  
   真正落地必须切到：
   - 固定到期（如 next Friday）
   - 固定 moneyness（如 ATM ± 0.25 delta）
   - 固定 entry / exit mid-to-fill 规则

4. **ETH 这版证据不够强**  
   当前更像 BTC-only 候选，而不是 BTC+ETH 一起铺。

## 7. 下一步怎么测
### 7.1 先把 proxy 升级成真实可交易壳
1. 直接拉 **Deribit option chain**；
2. 固定 `5d~9d` 到期的 **ATM straddle mid-IV**；
3. 每 `5m` 记录一次 `IV - trailing RV`；
4. 真正回放 `short straddle + BTC perp delta hedge` 的 PnL，而不是只看 `IV-RV` proxy。

### 7.2 只测 3 个版本，不要一开始就乱加花活
- **A**：always short BTC ATM short-dated straddle
- **B**：repo 对称版（`IV>RV` short / `IV<RV` long）
- **C**：desk 版 rich-IV only short（`IV-RV > q70`）

先看哪个版本在**净费用后**还活着。

### 7.3 这 5 个维度必须一起出表
- net expectancy
- max drawdown
- hedge turnover
- funding drag
- entry spread / fillability

### 7.4 最先加的 veto
- FOMC / CPI / major macro window
- BTC basis 异常扩张
- skew 突变（只贵 ATM 还是整条 surface 都贵）
- order book depth 不足
- 单日 realized vol 已经冲破历史高分位

## 8. 一句话结论
> 这份 2025 repo 真正值得 desk intake 的，不是“对称 long/short IV-RV”这层壳，而是更窄、更像交易台策略的那半边：**只在 BTC 的 IV 明显贵于 trailing RV 时做 short-vol carry**；这轮 public-data probe 下，BTC `q70 rich-IV` 版本的 proxy Sharpe 约 **`0.57`**、win rate 约 **`78.6%`**，明显优于 repo 原始对称版的 **`0.17`**，所以它值得进入 raw alpha 素材池继续深挖。

## 9. 来源
1. **khalil-benzina** (2025). *Crypto-IV-RV-Straddle-Carry*. GitHub Repo.  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: `https://github.com/khalil-benzina/Crypto-IV-RV-Straddle-Carry`  
   - Repo URL: `https://github.com/khalil-benzina/Crypto-IV-RV-Straddle-Carry`  
   - 关键文件：`README.md`, `build_weekly.py`, `backtest.py`

2. **Fabian Woebbeking** (2021). *Cryptocurrency volatility markets*. *Digital Finance*.  
   - DOI: `10.1007/s42521-021-00037-3`  
   - Readable URL: `https://link.springer.com/content/pdf/10.1007/s42521-021-00037-3.pdf`  
   - 用途：说明 crypto options 的 intraday implied-vol 指数可以从公开期权数据稳定抽取，不是伪指标。

3. **Julian Winkel, Wolfgang Karl Härdle** (2023). *Pricing Kernels and Risk Premia implied in Bitcoin Options*. *Risks*.  
   - DOI: `10.3390/risks11050085`  
   - Readable URL: `https://www.mdpi.com/2227-9091/11/5/85/pdf?version=1683355953`  
   - 用途：给 BTC options 的 time-varying risk premium / short-dated protection demand 提供学术 grounding。

4. **Deribit API**（本轮 probe 实际使用）  
   - `https://www.deribit.com/api/v2/public/get_volatility_index_data`

5. **本地 probe artifact**  
   - 脚本：`reports/artifacts/quant_digests/2026-04-15_ivrv_shortvol_probe.py`  
   - 汇总：`reports/artifacts/quant_digests/2026-04-15_ivrv_shortvol_probe_summary.json`
