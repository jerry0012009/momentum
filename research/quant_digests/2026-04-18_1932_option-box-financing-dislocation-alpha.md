# 别把这套 crypto options 平台只读成“期权研究基建”：对 short-cycle desk，更该先保留的是「box implied financing dislocation」这条 relative-value raw alpha
- 时间：2026-04-18 19:32 UTC
- 类型：GitHub / public-data probe
- 主题类型：raw alpha
- 基础 alpha：同到期、不同行权价构成的 box spread，其隐含融资价格若显著偏离理论贴现值，就做 long box / short box 收敛
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha / relative-value / stat-arb / options / box-spread / implied-rate / financing / deribit / 1m / 5m / maker-first
- 证据类型：工程经验 + 公开实时数据快检

## 1. 这次看了什么
看的是 GitHub 仓 `signorloops/crypto-options-research-platform` 里的 `strategies/arbitrage/option_box.py`，它把 crypto options 研究平台里最值得 desk 先抽出来的旁支，落成了 **box spread 套利**：四腿期权拼出一个到期现金流固定的盒子，再比较“今天买这个盒子的成本”与“到期一定拿回的 strike 宽度”。

## 2. 核心结论
- 这条线的 **base alpha 很清楚**：不是猜 BTC 涨跌，而是赌 **隐含融资价格会回到更合理的无套利区间**。
- repo 给出的策略骨架很完整：扫描同 expiry 的 strike 组合、比较 `net_premium` 与 `K_high-K_low`、在 `long_box / short_box` 之间选更赚钱的一边，并显式扣四腿成本。
- 但它现在还**不能直接照抄上线**：仓库主打 coin-margined options，`option_box.py` 里的 box 关系仍更接近线性期权语义；真上 Deribit/OKX 前，必须先把合约单位、inverse payoff、成交费和可成交 size 全部按 venue 规则重写。
- 我用 Deribit BTC 公共期权链做了 live quick check：当前有 `365` 个双边可配对的 call-put strike，若只看 `<=45d` 且 `0.9~1.1` moneyness，仍有 `109` 个可配对 strike、可组成 `982` 个 near-ATM box。说明**公开数据和实验素材非常够**。
- 但 taker 直做当前并不厚：这些 near-ATM `<=45d` boxes 的 **绝对偏离中位数约 `19.39bps`**，最好的一组（`2026-05-29`, `74k/76k`）粗扣四腿价差宽度和 `8bps` 后，仍约 **`-29.36bps`**；`982` 组里 **0 组** 在这个粗成本口径下转正。当前 first verdict：更像 **maker-first / fee-edge / 高频监控 alpha**，不是随手 taker 就能吃的午餐。

## 3. 为什么和当前项目有关
这条线和当前 desk 有直接关系，因为它补的是我们还没系统积累够的 **relative-value / stat-arb raw alpha**，而且不是“慢频宏大叙事”，而是可以按 `1m/5m` 频率持续扫描的微结构型价格错位。对短周期研发更值钱的不是 repo 里的整个平台，而是这条可单独拆出来的 **融资贴现偏离 → 盒子回归** 壳。

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / stat-arb
- 基础 alpha：box implied financing mispricing
- regime：优先近到中期 expiry、ATM 附近、双边报价连续、size 足够的时段
- filter / veto：四腿都有双边价；四腿最小 size 过线；偏离幅度必须大于四腿 spread + fees + inventory buffer
- risk / sizing / execution overlay：maker-first、腿间成交顺序控制、残腿超时撤单、单 expiry / 单 strike-width 风险上限

## 4. 可复刻的最小实验
- 研究假设：Deribit/OKX 的短天期 near-ATM box，有时会给出高于或低于理论贴现值的瞬时融资价格，但多数可见偏离会先被四腿 spread 吃掉。
- 可计算定义：对同 expiry 的 `K_low < K_high`，算 `premium = C(K_low)-P(K_low)-C(K_high)+P(K_high)`；把期权 mid 按标的价格换成 USD 近似，比较 `premium_usd` 与 `K_high-K_low`；只有 `|deviation| > four_leg_width + fee_buffer + inventory_buffer` 才算候选。
- 最小回测切口：Deribit BTC options，先做 `1m` snapshot 采样，限定 `<=45d`、`0.95~1.05` moneyness、四腿都有 bid/ask，再比较 `mid 口径`、`maker 口径`、`taker 口径` 三层净边。
- 最该先看：`正净边机会占比`、`偏离持续时间`；其次才是年化 implied rate 和单腿残留风险。

## 5. 风险与保留意见
- 最大保留意见不是“没有机会”，而是 **repo 当前 box 数学更像线性模板**；coin-margined / inverse venue 要先校正 contract spec，否则容易把假边当真边。
- 四腿策略天然怕残腿和排队，看到偏离不等于能同时成交。
- 这类机会很可能只在低费率、maker rebate、或极短暂 order-book 失衡里存在；若默认 taker，今天这次快检已经给出偏负 verdict。

## 6. 来源
- signorloops. (2026). *crypto-options-research-platform*. GitHub.
  - Repo URL: `https://github.com/signorloops/crypto-options-research-platform`
  - Read files: `strategies/arbitrage/option_box.py`, `strategies/arbitrage/conversion.py`, `tests/test_arbitrage.py`
- Deribit API Docs.
  - Readable URL: `https://docs.deribit.com/`
- 本地快检 artifact：
  - `reports/artifacts/quant_digests/2026-04-18_option_box_arbitrage_summary.json`
  - `reports/artifacts/quant_digests/2026-04-18_option_box_arbitrage_candidates.csv`
