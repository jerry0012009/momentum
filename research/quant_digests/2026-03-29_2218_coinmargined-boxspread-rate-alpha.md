# 别把 coin-margined options repo 直接当现成套利机：这份 2026 新仓库更该先测的是「same-expiry box spread implied-rate 偏离」raw alpha，但必须先修单位口径
- 时间：2026-03-29 22:18 UTC
- 类型：GitHub / source audit / Deribit 公共链 live snapshot
- 主题类型：raw alpha
- 基础 alpha：同到期、同标的、不同执行价的 **box spread 融资错价**（long cheap box / short rich box）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否（当前 repo 的 box 模块还需先修 coin-margined 单位归一）
- 主题标签：raw-alpha/options/relative-value/stat-arb/box-spread/implied-rate/coin-margined/deribit/okx/1m/3m/5m/15m/repo/public-data/cost
- 证据类型：工程经验 + 公共市场数据

## 1. 这次看了什么
这次看的是 **signorloops（2026）** 的 GitHub 仓库 **Crypto Options Research Platform**，重点拆了 `strategies/arbitrage/option_box.py`，再用 **Deribit 公共 BTC options chain** 做了一次轻量 live sanity check。它真正值得 desk intake 的，不是“又一个 options 平台”，而是：**same-expiry box spread 可以直接当一条 options relative-value raw alpha 来扫，分钟级就能做最小实验。**

## 2. 核心结论
- **一句话结论**：base alpha 很清楚——扫 **box implied rate** 偏离，便宜就做多 box、太贵就做空 box；它本质上是期权版的短周期融资/相对价值套利。
- repo 的好处是把骨架写得很完整：默认 `min_annualized_return=2%`、`transaction_cost_per_leg=0.001`、四腿总费用按 `0.004` 处理，还带 strike 扫描、流动性分数和 annualized return 排序，足够直接改成 desk 最小实验。
- **但当前实现不能直接上**：repo 在 coin-margined 语境里把 `payoff = K_high - K_low` 和 BTC 计价 premium 直接相减，存在**单位混用**。对 Deribit/OKX 这类币本位期权，premium 要先映射到统一的 USD / 结算单位口径，再谈 box profit。
- live 数据说明这个修正很重要：按 repo 原公式，`10APR26 76000-85000` 这组 box 会被误读成接近 **+$9,000** 的“利润”；但把 premium 先乘当前标的价近似转成 USD 后，同一类机会只剩小得多的价差口袋。
- 更进一步，**mid 上有 pocket，不代表能成交**：我用 Deribit 公共链粗扫后，`31MAR26 62000-64500` 这组 box 在 mid 近似下、扣 `0.004 BTC` 粗费后，仍像有 **约 +$702**；但换成四腿可执行 bid/ask 后，近 ATM 样本里最好的 box 也大约只有 **-$334**，说明真正该先测的是 **executable box rate**，不是 mark/mid 幻觉。

## 3. 为什么和当前项目有关
这条不是解释型材料，而是**可直接扩充 raw alpha 素材池**的新分支：
- 它补的是当前池子里相对少的 **options relative-value / stat-arb**，不是第 N 次重复 perp pairs；
- 它天然有完整策略骨架：entry、exit、carry-to-expiry、四腿成本、流动性过滤、保证金占用都能清楚写出来；
- 它和 desk 当前短周期节奏兼容：不是等日频结算，而是每 `1m/3m/5m/15m` 扫一次期权链，抓 **implied financing pocket**；
- 它还能反过来训练我们对 **单位口径 / 可执行价 / bid-ask honesty** 的纪律，这一点对 funding、basis、pairs 都通用。

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / stat-arb
- 基础 alpha：same-expiry box spread 相对理论贴现值或隐含融资利率的偏离
- regime：只做近月、近 ATM、链上四腿都有可成交深度的时段
- filter / veto：四腿任一腿无 bid/ask、OI/size 过低、box APR 未覆盖四腿费用与保证金占用时 veto
- risk / sizing / execution overlay：按 box 宽度与保证金占用限仓；优先 maker / 被动腿；若 box rate 回归阈值内可提前平，否则持有到 expiry 兑现

## 4. 可复刻的最小实验
- **研究假设**：在 coin-margined BTC options 上，统一到同一结算单位后，仍会周期性出现可执行的 rich/cheap box pocket；mid 看似有边的机会，经过四腿 bid/ask 和费用后会大幅收缩。
- **数据源**：Deribit `public/get_book_summary_by_currency`（公开可得，分钟级可抓）；第二步再补 OKX public options。
- **实验口径**：每分钟重建同 expiry strike pair 的 long/short box；premium 统一转 USD（或直接用精确 inverse payoff 口径）；分别算 `mid APR` 与 `executable APR`。
- **entry/exit**：`executable_APR > funding/cash hurdle + fees + margin haircut` 才进；回落到关闭阈值则平，否则持有到到期。
- **sizing/risk/cost**：单 box 占用不超过组合风险预算；四腿都按真实 bid/ask；再做 maker/taker 两套 friction ladder。
- **先看什么**：不是先看 Sharpe，而是先看 3 个最小指标——可执行正 edge 次数、edge 在费后保留比例、到期兑现 vs 提前回归的贡献拆分。

## 5. 风险与边界
- 这条 alpha **不是 bar-based directional signal**，而是 options chain 的 minute scanner；它能映射到 `1m/3m/5m/15m`，但本体是事件/报价驱动。
- 当前 live check 只做了 Deribit BTC 的粗扫，且用“premium × 当前标的价”近似 USD；正式版应改成**精确 inverse 合约 payoff/结算口径**。
- 四腿执行风险很高；如果没有组合下单或至少两腿先后成交保护，纸面 edge 很容易被腿风险吃掉。

## 6. 来源
1. **signorloops (2026), _Crypto Options Research Platform_**  
   - Repo URL: https://github.com/signorloops/crypto-options-research-platform  
   - Readable URL: https://github.com/signorloops/crypto-options-research-platform  
   - 关键源码：  
     - https://raw.githubusercontent.com/signorloops/crypto-options-research-platform/master/strategies/arbitrage/option_box.py  
     - https://raw.githubusercontent.com/signorloops/crypto-options-research-platform/master/README.md  
     - https://raw.githubusercontent.com/signorloops/crypto-options-research-platform/master/docs/theory.md
2. **Deribit API Docs**  
   - Readable URL: https://docs.deribit.com/  
   - 本轮使用：`public/get_book_summary_by_currency?currency=BTC&kind=option`

## 7. 下一步怎么测
第一步别急着回测全年，先做一个 **单日 minute-level box scanner**：
1. 只抓 Deribit BTC 近 2~3 个近月 expiry；
2. 只扫近 ATM、宽度 `500~5000 USD` 的 strike pair；
3. 同时输出 `repo_raw_profit`、`USD-normalized mid profit`、`USD-normalized executable profit` 三列；
4. 先证明“单位修正前后差多少、mid 到 executable 又掉多少”；
5. 只有当 executable 口径下仍稳定出现 pocket，再进入 maker/taker、保证金和持有到期 vs 提前回归的正式回测。
