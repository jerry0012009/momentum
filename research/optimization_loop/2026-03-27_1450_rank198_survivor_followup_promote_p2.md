# Rank 198 survivor follow-up — promote to P2

- Time: 2026-03-27 14:50 UTC
- Target: `Rank 198 / dynamic cointegration pair-basket spread convergence`
- Verdict: `promote_P2`

## 本轮只回答的问题
只执行 `Rank 198` 的唯一一次 survivor follow-up，不重排其他小点；只回答：

> `selection funnel / basket structure` 能否把当前 `TRXUSDT/ADAUSDT` 这类 surviving pocket，从“个别幸存 pair”提炼成值得进入正式 admission 的可复制框架？

## 本轮使用的证据
1. `research/quant_digests/2026-03-27_1332_dynamic-cointegration-minute-binned-pairs.md`
2. `reports/artifacts/quant_digests/dynamic_cointegration_pairs_20260327_1332/summary.json`
3. `research/quant_digests/2026-03-23_0958_dynamic-cointegration-pairs-raw-alpha.md`

## 会改变层级判断的结论
### 1) broad pairs deployment 已被否掉，但这不等于对象应被 park
- 2026-03-27 这份 digest 自带的 contemporaneous `Binance USDⓈ-M perp 15m` check 已经很明确：
  - 五组 pair 等权后 `net ≈ -0.019 bps/bar`
  - net cumulative ≈ `-0.85%`
  - net annualized Sharpe ≈ `-0.84`
- 这足以否掉“随便挑一些 pair，做 broad equal-weight spread convergence 就能成立”的说法。

### 2) 但 surviving pocket 不是偶然孤例，而是和更早同主题证据共振
- 同一份 2026-03-27 check 里，`TRXUSDT/ADAUSDT` 仍保留：
  - `net ≈ +0.051 bps/bar`
  - net cumulative ≈ `+2.12%`
  - net annualized Sharpe ≈ `1.73`
- 更关键的是，这个结论不是第一次出现。2026-03-23 的另一篇动态协整主题 digest 已独立给出同方向 desk 读法：
  - naive 15m 直接移植不够过成本；
  - 真正该补的是 `pair selection / regime / turnover control`，而不是继续把信号本体当成“任意 pairs 普适”。

### 3) 因此，本轮真正被验证的是“对象定义”而不是某一条 pair 的偶然盈利
两份同主题证据合在一起，系统认知应从：
- “dynamic cointegration 只是少数 pair pocket，可能还不够成框架”

更新为：
- “dynamic spread convergence 的可复制对象，不是 broad pairs deployment，而是 **dynamic pair-selection / basket-selection + spread convergence** 这个 selection-sensitive stat-arb 框架。”

这已经超过开放式 `keep_P1` 的范围，因为：
- raw alpha kernel 已明确；
- 失败边界也明确（broad deployment 不成立）；
- 下一步 admission 应该测试的是这个框架在 `effectiveness / cross-asset / honesty` 上能否站住，而不是继续讨论要不要把它作为独立对象存在。

## 决策
本轮对 `Rank 198` 给出：

> **`promote_P2`**

新的工作定义：

> 不是把 dynamic cointegration 理解成“任意双腿 pairs 均值回归”，而是把它定义为：
> **在 liquid perp universe 上，用 rolling cointegration / half-life / stability funnel 挑出可交易 pair 或 stationary basket，再交易 spread deviation -> convergence，并用 turnover / cost / basket structure 约束是否可部署。**

## 为什么现在应升 P2，而不是继续 keep_P1
- survivor 允许的唯一 follow-up，已经把“它是不是一个独立可复制框架”这个问题回答清楚了；
- 继续留在 P1 只会变成泛泛补充材料，不再改变对象定义；
- 当前空着 `Active P2 slot`，而这条对象的下一步天然就是 admission，而不是再做第二次 survivor follow-up。

## 为什么现在还不是 P3
- 当前还没有完成正式 `P2 admission` 的五维覆盖；
- 现有证据还不足以证明它在跨资产、参数、时间稳定性与执行诚实性上已经接近 `paper trade / paper launch`；
- 但它已经足够值得进入正式 admission，而不是直接 park。

## Runtime writeback
- `Surviving candidate slot`：清空，follow-up budget 归零。
- `Active P2 slot`：写入 `Rank 198 / dynamic cointegration pair-basket spread convergence`。
- `cycle_plan #1`：写为 `done`，result 明确记录本轮 `promote_P2`。

## Reader-facing takeaway
`Rank 198` 真正值得继续的，不是“pairs 还有没有残余 pocket”这种模糊说法，
而是：

**dynamic pair-selection / basket-selection + spread convergence** 已经足够像一个独立、可复制、值得做 admission 的 stat-arb 框架；
该对象应从 `P1 survivor` 升到 `P2`，下一轮直接做 admission，而不是继续开放式停留在 `keep_P1`。
