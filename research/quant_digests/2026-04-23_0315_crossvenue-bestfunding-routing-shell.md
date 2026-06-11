# 别把这份 2026 perp-carry 仓只读成“又一个 funding 收租脚本”：对 short-cycle crypto desk，更该先保留的是「cross-exchange best-funding routing × sign-constrained delta-neutral carry × hysteresis hold」这条完整 raw alpha 壳
- 时间：2026-04-23 03:15 UTC
- 类型：GitHub repo / notebook audit
- 主题类型：raw alpha
- 基础 alpha：同标的 delta-neutral funding carry（short rich perp / long spot；若 funding 为负则反向 long perp / short spot）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：carry / funding / cross-venue / delta-neutral / routing / hysteresis / open-interest / macro-gate / complete-shell
- 证据类型：repo 源码 + notebook 结果 + 参数/成本/路由定义

## 1. 这次看了什么
看的是 2026 GitHub 仓库 `PietroC21/Crypto-PerpetualFutures`。它不是只给一句“funding rate 高了就 short perp long spot”，而是把 **跨所 funding 路由、sign-constrained entry、zero-cross / min-hold exit、OI gate、VIX/SPY macro gate、weight scheme、fee model、P&L attribution** 都写成了可直接运行的策略壳。

和最近已经写过的 funding / basis 主题相比，这个 repo 真正的新意不在“carry 存在”本身，而在：**同一条 carry alpha，如果只做单所版本会被费率打穿；但把 perp 腿动态路由到当下 funding 最肥的 venue，结果会从负变正。**

## 2. 先回答 base alpha 是什么
这篇东西的 **base alpha 很清楚**：

> **base alpha = 同标的 spot↔perp 的 delta-neutral funding carry**，也就是在 perp 对 spot 明显偏贵、且 funding 足够 rich 时，做 `short perp + long spot` 去收 funding；若 funding 明显为负，则反向做 `long perp + short spot` 收负 funding。

所以它不是单纯 filter / regime / overlay，而是一条 **能独立站住的 raw alpha**。仓库里的 OI / 宏观门控只是 admission / veto，venue routing 是 alpha 壳的重要放大器，不是主题本体。

## 3. 核心结论
- 这份 repo 最有价值的地方不是“crypto perp 能收 funding”这句常识，而是它明确展示了：**venue routing 本身就是决定 carry 是否过成本线的核心步骤**。
- repo 的执行逻辑是：每个 rebalance 时点，先在多交易所 funding 里找 **best available funding rate**，再做 sign-consistent 的 delta-neutral carry，而不是死守单一 venue。
- Notebook 给出的 cross-exchange 结果里，**gross CAGR 约 +9.5% / net CAGR 约 +5.76% / ann vol 约 0.71% / max drawdown 约 1.22% / profit factor 约 4.06**；同一份研究里，**Binance-only 版本在 2023+ 口径是 net CAGR 约 -10.0%**，说明“跨所选最肥 funding 腿”不是 cosmetic，而是生死线。
- 另一个很值钱的细节是 **exit 设计**：不是 funding 一掉回阈值内就立刻平，而是用 **`z_exit=0` + `min_hold=3` 个 8h 周期** 的 hysteresis hold，目标是减少 turnover 和 fee drag。
- Exchange dominance 分析显示：实际贡献主要集中在 **Binance 与 Hyperliquid**；repo 里给出的结论是 position-period 大致 **Binance ~45% / Hyperliquid ~55%**。也就是说，完整的“跨六所”叙事可以先缩成更实用的 **Binance + Hyperliquid 双场地 routing**。

## 4. 为什么和当前项目有关
它和 desk 当前目标的关系非常直接：

1. **这是 raw alpha，不是解释性材料。**
2. **它已经是完整策略壳**：entry / exit / sizing / risk / fee / routing 都有。
3. **它天然适合映射到 short-cycle desk**：alpha state 是 `8h/1h funding`，但执行层完全可以拆成 `15m/5m` child execution。
4. 它补的不是最近刚写过的 pairs / semivariance 近邻，而是 **另一类可以长期留在素材池里的 carry shell**：
   - state 层：funding / venue / carry richness
   - execution 层：`15m/5m` 分批进出、spread / liquidity veto
   - risk 层：OI / macro / hold-time / fee budget

换句话说，这篇最适合 desk 保留的，不是“又一个 funding 观点”，而是：

> **单 venue carry 常常只是研究幻觉；可交易版本要把 routing、hold、fees、gate 一起写进去。**

## 5. 策略拆解（必填）
- 方向属性：carry / relative-value / delta-neutral
- 基础 alpha：同标的 perp-vs-spot funding carry
- regime：funding 异常足够大、流动性没塌、风险-off 宏观状态不过热
- filter / veto：OI gate、VIX gate、SPY 5d drawdown gate、sign-consistency
- risk / sizing / execution overlay：fixed-weight 或 equal-invested、zero-cross exit、min-hold、two-leg fee accounting、best-venue routing

## 6. repo 里最值得 desk 抄的 6 个组件
### 6.1 Best-funding routing
核心不是“这根 funding 高不高”，而是：
- 对每个资产、每个 rebalance 时点，
- 在 Binance / Gate / OKX / Bybit / Deribit / Hyperliquid 里，
- 选 **当下最值得做 carry 的那条 perp 腿**。

这一步直接决定 gross carry 厚度。repo 给出的分析里，加入 Hyperliquid 之后，策略从单 venue 不可交易变成可交易。

### 6.2 Sign-constrained entry
不是只看 `|z|` 大就开仓，而是要求方向一致：
- `best_fr > 0` 时才做 `short perp + long spot`
- `best_fr < 0` 时才做 `long perp + short spot`

这很重要，因为它把“funding 异常”与“你实际收的是哪边 funding”绑定了起来，避免做反方向的伪 carry。

### 6.3 Hysteresis + minimum hold
repo 的默认参数不是来回抖动式的 threshold in/out，而是：
- `z_entry = 2.0`
- `z_exit = 0.0`
- `min_hold = 3`（3 个 8h 周期）

对 short-cycle desk，这个设计的启发很大：
**alpha state 可以慢，但 execution 不必每根 K 都翻仓。**
很多 funding/basis 策略真正亏在“有 edge，但你太爱交易”。

### 6.4 OI liquidity gate
repo 用 `open_interest >= 0.5 * rolling_mean(OI)` 做 admission。这个点比“看 volume”更靠谱，因为在 crypto 里 volume 更容易被噪声或 wash trading 污染。

### 6.5 Macro gate
repo 还用了：
- `VIX > 30` flatten
- `SPY 5-day drawdown > 5%` flatten

这些不是给 intraday 主信号下 direction，而是明确定位成 **shared risk overlay**。对我们 desk，可直接翻译成“risk-off 时减半 / 不开新仓”，而不是伪装成逐根主信号。

### 6.6 Full fee model
它明确把两腿成本都算进去：
- perp taker fee
- spot taker fee
- turnover 只在仓位变化时扣

这点很关键，因为很多 funding shell 只展示 funding 收入，却不把 **spot hedge 成本** 当真成本，最后在真实执行里直接翻车。

## 7. 可复刻的最小实验
这条 alpha 不适合被伪装成“每 5m 都产生一个独立方向信号”。更合理的 desk 落地方式是：

### 7.1 最小实验定位
- **主题类型**：raw alpha
- **state 频率**：`1h / 8h funding state`
- **execution 频率**：`15m` 主执行，`5m` 做微调
- **目标**：验证“best-venue routing + hysteresis hold”是否能留下足够 net carry

### 7.2 最小研究口径
1. 资产：先做 `BTC/ETH/SOL`，再扩到 `BNB/XRP/DOGE/AVAX`
2. 交易所：先只做 `Binance + Hyperliquid`
3. state：
   - 聚合未来可收 funding 的 venue-level funding
   - 计算 `best_fr` 与 rolling z-score
4. entry：
   - `|z| > z_entry`
   - `best_fr` 方向与持仓方向一致
5. exit：
   - `|z| < z_exit` 或 funding sign flip
   - 再加 `max_hold` 与 `min_hold` 双边约束
6. cost：
   - 先粗扣两腿 round-trip taker 成本
   - 再比较 maker-first child execution 的成本改善

### 7.3 映射到 `15m/5m` 的方式
- **不是**把 funding alpha 直接降采样成 5m 裸信号；
- **而是**让 `15m/5m` 负责：
  - 分批建仓 / 平仓
  - venue spread 不利时先 veto
  - 波动爆炸时暂缓 child orders
  - funding window 前后控制冲击成本

也就是：
**alpha state 在 funding，edge 留在 routing，短周期负责 execution。**

## 8. 我认为最值得优先验证的 desk 假设
### 假设 A：
`Binance-only` carry 在我们口径里大概率依然偏薄，但 **`Binance + Hyperliquid` best-leg routing** 可能把 net expectancy 拉回正值。

### 假设 B：
相比继续卷 entry 阈值，更值得先测的是：
- `min_hold`
- `z_exit`
- maker/taker 组合
- funding window 前后的 child execution 规则

### 假设 C：
对这类 alpha，真正的“快周期提升”不是把 state 做得更快，而是把 **execution friction** 压下去。

## 9. 风险与保留意见
- 这份 repo 的主回测口径偏 `8h/1h`，所以它对 desk 的直接意义更像 **完整壳 / state engine**，不是现成 `5m` 裸 alpha。
- 宏观 gate（VIX / SPY）对 crypto short-cycle desk 未必是最终最优实现，可能需要换成 crypto-native 风险代理（如 BTC 急跌、OI 急缩、basis collapse）。
- Spot hedge 腿在真实世界里还要考虑资金占用、可借券/库存、划转与 venue 风险；这些 repo 都只是部分近似。
- Hyperliquid 的 1h funding 频率给了 routing 优势，但真实执行里也可能带来更高的切换频率；因此 **routing alpha 与 turnover drag 必须一起看**。

## 10. 来源
- PietroC21. (2026). *Crypto-PerpetualFutures*. GitHub.
- Repo URL: `https://github.com/PietroC21/Crypto-PerpetualFutures`
- Readable URL: `https://github.com/PietroC21/Crypto-PerpetualFutures/blob/main/README.md`
- Notebook / code sources used:
  - `https://github.com/PietroC21/Crypto-PerpetualFutures/blob/main/FINAL_Notebook.ipynb`
  - `https://github.com/PietroC21/Crypto-PerpetualFutures/blob/main/FINAL_Notebook_V2.ipynb`
  - `https://github.com/PietroC21/Crypto-PerpetualFutures/blob/main/strategy_cross.py`
  - `https://github.com/PietroC21/Crypto-PerpetualFutures/blob/main/strategy.py`
- Local audit path: `/tmp/Crypto-PerpetualFutures`

## 11. 下一步怎么测
不要先去优化一堆 z-score 小参数，先做一个 **desk 版双场地 carry shell smoke test**：
1. 只保留 `Binance + Hyperliquid` 两地；
2. `BTC/ETH/SOL` 先跑 `best_fr z-score + sign-constrained carry`；
3. execution 只做两版：
   - `15m` 一次性 taker
   - `5m` 三段 maker-first / taker-backstop
4. 比较 4 个核心指标：
   - net carry / day
   - bps per turnover
   - hold-time distribution
   - routing switch frequency
5. 若 `routing-switch frequency` 过高，就别继续加币，先把 **sticky routing / cooldown / min-hold** 调顺。

一句话版下一步：
**这条策略先别继续证明“funding 有用”，而是先证明“best-venue routing 后，净 carry 还剩多少”。**
