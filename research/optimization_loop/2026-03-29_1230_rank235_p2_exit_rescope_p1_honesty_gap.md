# Rank 235 / richest-venue routing × hysteresis funding carry — time / parameter / honesty 审计与 P2 出口判定

- 时间：2026-03-29 12:30 UTC
- 对象：`Rank 235 / richest-venue routing × hysteresis funding carry`
- 当前槽位：`Active P2`
- 本轮小点：`time / parameter / honesty`
- 结论：**不走 fast-track `promote_P3`；执行 `one-time P2 -> P1 re-scope`**
- 新认知：**这条线的 repo 已把时间窗与参数边界写得相当清楚，但“quoted funding → realized carry”的兑现口径并不诚实：代码实际把当期 ex-post richest venue 的 funding 直接记成持仓收益，且没有把持仓中 venue 切换与跨 venue basis drift 作为持续成本扣掉；因此当前对象不能按 paper-launch 候选继续前推，只能收窄为“只按入场时可预先锁定的下一 funding 窗口报价选 venue，并显式计入换腿/换 venue/basis drift”的窄版 P1 对象。**

---

## 1. 本轮检查材料
1. `strategy_cross.py`
2. `strategy.py`
3. `notebook_cross.ipynb`
4. `FINAL_Notebook_V2.ipynb`
5. 既有 digest：`research/quant_digests/2026-03-29_0939_richest-venue-routing-hysteresis-carry-alpha.md`

---

## 2. time stability：有边界，但不是可直接 fast-track 的那种稳定
### 2.1 repo 的时间边界是清楚的
- `notebook_cross.ipynb` 明写：
  - 全样本：`2020-01 -> 2026-02`
  - 真正三 venue 稳定共存的可比窗口：`2023-09-01 -> 2026-02`
- regime table 输出：
  - `Binance only (2020-01 -> 2022-12)`: `CAGR 3.8%`
  - `+ GateIO (2023-01 -> 2023-05)`: `CAGR 21.9%`
  - `+ Hyperliquid (2023-05 -> 2023-08)`: `CAGR 3.0%`
  - `All 3 stable (2023-09 -> 2026-02)`: `CAGR 27.6%`

### 2.2 但这说明它更像“venue availability 驱动”的窗口结果
- strongest window 确实在 `2023-09+`。
- 早期样本与过渡样本并不支持“任意时间窗都一样稳”。
- 所以时间口径能支持“这条线值得继续保留”，**但不足以支持 fast-track 进 paper launch**。

---

## 3. parameter stability：入场阈值与 hold 设定相对清楚
### 3.1 代码里参数边界明确
`strategy_cross.py` 默认：
- `z_lookback = 270`
- `z_entry = 2.0`
- `z_exit = 0.0`
- `min_hold = 3`（即 `3 × 8h = 24h`）
- `oi_min_ratio = 0.5`
- `vix_gate = 30`
- `spy_dd_gate = 5%`
- 双腿 fee：`perp 4.5bps + spot 10bps = 14.5bps`

### 3.2 notebook 邻域也不算脆
`z_entry` 敏感性表：
- `1.00 -> CAGR 14.20%, MaxDD 8.94%`
- `1.25 -> CAGR 14.93%, MaxDD 6.83%`
- `1.50 -> CAGR 14.48%, MaxDD 5.70%`
- `1.75 -> CAGR 13.84%, MaxDD 4.70%`
- `2.00 -> CAGR 13.87%, MaxDD 3.62%`
- `2.50 -> CAGR 12.53%, MaxDD 2.06%`

结论：
- 参数不是“只在一个点上活”。
- `hysteresis + min_hold` 方向本身是合理的，主要作用确实是**压 churn / 压 fee drag**。
- 但参数稳定 ≠ execution realism 过关。

---

## 4. honesty / execution realism：这里是当前不能升 P3 的核心 blocker
### 4.1 最大问题：repo 把“当期 richest venue”按 ex-post 最优直接记成收益
`strategy_cross.py` 的关键实现：
- `compute_best_fr()` 对每个 `(period, asset)` 直接取当期各 venue 的 `max(FR)`。
- `compute_pnl_cross()` 里：
  - `funding_pnl = (-pos_lagged * best_fr).sum(axis=1)`

这意味着：
- 持仓收益记账用的是 **`best_fr(t)`**；
- 但持仓对象并没有显式记录“我在 period t 实际 short 的是哪个 venue”；
- fee 也只对 **position 进出** 收费，没有对 **持仓中 venue 改换** 收费。

这会产生一个关键偏乐观：
> **只要某资产在持有期间 richest venue 换了，代码就会自动把收益切到新的 richest venue 上，但不会同步支付换 venue 的交易成本，也没有证明交易时点能事先锁定那个新 venue 的下一窗 funding。**

这不是小 wording 问题，而是会直接抬高 `routing` 这一核心 alpha 组件的兑现率。

### 4.2 1h venue 被聚成 8h best rate，本质更接近 same-window ex-post best print
对 Gate / Hyperliquid：
- 代码把 1h funding `resample("8h").sum()` 成 8h equivalent。
- 然后再在当期做 `best_fr = max(exchange FR)`。

问题是：
- 如果你在窗口起点做 routing，真正能锁定的是**当时已公布/可预估的下一 funding window 报价**；
- 这里用的是**整个 8h 窗内 realized 后再聚合出的 best funding**。

所以 repo 当前的“quoted funding”并不是严格意义上的可交易报价，更接近：
- `same-window ex-post best funding print`
而不是：
- `entry-time executable next-window carry quote`

### 4.3 spot/perp delta-neutral 被近似成 `spot_pnl ≈ 0`，跨 venue basis drift 没有进账本
`compute_pnl_cross()` 里明确写：
- `spot_pnl ≈ 0 — the long spot and short perp are delta-neutral, so mark-to-market changes cancel across legs.`

但当前对象不是“同 venue 同标的纯理论现金套”，而是：
- `long spot@Binance + short perp@best venue`

这里至少还有：
1. 跨 venue perp/spot basis 漂移
2. venue 间 mark/index 差异
3. 换腿时点的 spread/slippage
4. 若 richest venue 在持仓内切换，重新建腿的额外摩擦

这些没有进入持续 PnL，只在 entry/exit 上收一个双腿 taker fee，仍然偏乐观。

### 4.4 headline 数字与 venue universe 在不同 notebook 版本里并不一致
- `notebook_cross.ipynb` 的核心对照给出：
  - 全样本 cross net：`CAGR 13.9%`
  - `2023-09+`：`Binance-only net -10.0%` vs `Cross-exchange net +27.8%`
- `FINAL_Notebook_V2.ipynb` 的 Executive Summary 又写：
  - `Zero-cost CAGR +9.5%`
  - `Net CAGR +5.76%`
  - 且 venue 描述还扩到 `OKX / Bybit / Deribit / Hyperliquid`

这说明：
- repo 展示过的 headline 不是单一、稳定、同口径的一套结果；
- 当前更可信的是**结构性结论**，不是某个 CAGR 数字本身；
- 也进一步削弱了“已经足够诚实、可以 fast-track”的理由。

---

## 5. 这轮应该怎么写 quoted funding -> realized carry gap
建议今后对这条对象统一使用下面这句：

> **这里的 `quoted funding` 不能写成“可直接兑现的 carry”，因为 repo 当前记的是 `same-window ex-post best funding print`；真正可兑现的 `realized carry` 应该定义为：入场时可预先锁定的下一 funding 窗口报价 + 实际收到/支付的 funding cashflow − 持仓期间 venue switch / roll cost − 跨 venue basis drift − spot/perp legs spread & slippage − 其余执行摩擦。**

再压缩成一句 desk 口径：

> **当前 repo 更像证明“richest-venue routing 方向上可能有 alpha”，还没有诚实证明“按可交易报价路由后，这些 quoted funding 能稳定兑现成 realized carry”。**

---

## 6. 出口判定
### 6.1 为什么不是 `promote_P3`
虽然：
- 时间窗边界清楚；
- 参数边界也不算脆；
- `routing uplift` 的方向性证据确实存在；

但 honesty 这条没有过：
- ex-post richest venue 记账
- 无持仓中 venue switch cost
- 无跨 venue basis drift / spread drift 持续扣减
- headline 版本口径不一致

这意味着当前对象还**不是**可直接进 paper launch 的 execution-realistic 版本。

### 6.2 为什么不是直接 `drop_to_background`
因为这条线并非“alpha 幻觉被完全打穿”：
- `routing uplift` 的结构性方向仍然成立；
- `hysteresis/min_hold` 的作用也有明确解释；
- 只是当前 repo 的兑现口径过于乐观，不能把现成 headline 直接当 launch 依据。

### 6.3 所以唯一合法出口：`one-time P2 -> P1 re-scope`
新的窄版对象应改写为：
- **只按入场时可预先锁定的下一 funding window 报价做 venue 选择**；
- **显式记录持仓 venue**，不允许在账上无摩擦地自动切 richest venue；
- **把 venue switch / roll / spread / basis drift** 作为持续兑现折损写进实验口径；
- `hysteresis/min_hold` 仍可保留，但只能作为降低 churn 的执行层，不再与 routing uplift 的兑现混写。

---

## 7. 本轮 verdict（写回 state 用）
`Rank 235 / richest-venue routing × hysteresis funding carry` 的 `time / parameter / honesty` 审计已确认：repo 虽给出了相对清楚的时间窗与参数邻域，但当前实现把 `same-window ex-post best funding print` 直接记成持仓收益、且未为持仓中的 venue 切换与跨 venue basis drift 付费，因此 quoted funding 不能诚实外推成 realized carry；本轮不走 fast-track `promote_P3`，而是执行 `one-time P2 -> P1 re-scope`，把对象收窄为“只按入场时可预先锁定的下一 funding 窗口报价选 venue，并显式计入换腿/换 venue/basis drift”的窄版 spec。
