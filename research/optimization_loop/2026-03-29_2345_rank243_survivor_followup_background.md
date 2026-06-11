# Rank 243 / coin-margined same-expiry box-spread implied-rate alpha — survivor follow-up closed to background

- 时间：2026-03-29 23:45 UTC
- 执行角色：bot3
- 当前执行小点：`Rank 243 / coin-margined same-expiry box-spread implied-rate alpha`
- 对应 survivor 来源：`research/optimization_loop/2026-03-29_2332_rank243_coinmargined_boxspread_rate_keep_p1.md`

## 结论
**survivor follow-up verdict = `done -> background/P0`，不升 `P2`。**

这次唯一 follow-up 已经把 `Rank 243` 的唯一 decisive blocker 直接回答完：
在限定的 **Deribit BTC 近 2~3 个近月 expiry、近 ATM、宽度 `500~5000 USD` 的 strike pair** 上，把 coin-margined premium 与 payoff 统一到同一 USD 结算口径后，**`USD-normalized executable box APR` 没有留下值得升 `P2` 的真实 pocket**；repo 里看起来很大的利润，主要是单位混用造成的幻觉，而不是可执行融资 edge。

## 本轮怎么做的
### 1) 复核 repo 口径
直接读取了：
- `https://raw.githubusercontent.com/signorloops/crypto-options-research-platform/master/strategies/arbitrage/option_box.py`

复核点不是“代码风格”，而是最关键的会计口径：
- repo 把 `K_high - K_low` 这种 **USD payoff 宽度** 和 coin-margined premium 直接放在同一条 profit 算式里；
- 这会把 BTC 计价 premium 错当成已经是 USD payoff 的同单位量，导致 paper 上出现夸大的 box profit。

### 2) 做最小 live executable check
抓取：
- Deribit 公共 API：`public/get_book_summary_by_currency?currency=BTC&kind=option`

筛选范围：
- 只保留 BTC options
- 只看最近 3 个 expiry（实际覆盖 `2026-03-30 / 2026-03-31 / 2026-04-01`）
- 只看近 ATM、宽度 `500~5000 USD` 的 strike pair
- 只保留四腿都有 quote 的样本

对每个 strike pair 同时重算：
1. `repo_raw_profit`：沿用 repo 的单位混用写法，故意保留为对照组
2. `USD-normalized mid APR`：先把四腿净 premium 从 BTC 近似映射到 USD，再与 box payoff 宽度比较
3. `USD-normalized executable APR`：四腿按可执行方向落到 bid/ask，再做同样的 USD 口径比较

## 关键结果
样本量：`328` 组可比较 box。

### A. repo raw profit 继续给出巨大“利润”幻觉
代表性样本：
- `2026-04-01 64500-67000`：`repo_raw_profit ≈ 2499.96`
- `2026-03-31 60000-65000`：`repo_raw_profit ≈ 4999.92`
- `2026-04-01 66000-71000`：`repo_raw_profit ≈ 4999.92`

这些数字本身就说明：如果不先统一单位，repo 会把 box 宽度几乎原样读成利润，根本不能拿来做 admission。

### B. 一旦统一成 USD-normalized mid，边几乎全部塌到 0
代表性样本：
- `2026-04-01 64500-67000`：`USD-normalized mid profit ≈ 0.00`
- `2026-03-31 60000-65000`：`USD-normalized mid profit ≈ -0.00`
- `2026-04-01 64500-66500`：`USD-normalized mid profit ≈ 0.00`

也就是说，这批近月近 ATM box 在中间价上已经基本只是 **贴现关系本身**，没有形成可拿去升 `P2` 的 mid pocket。

### C. executable 口径下系统性转负
`top10` 里 executable APR 最好的样本也仍然为负：
- `2026-04-01 64500-67000`：`USD-normalized executable profit ≈ -205.77`，`APR ≈ -13.83`
- `2026-03-31 60000-65000`：`USD-normalized executable profit ≈ -207.31`，`APR ≈ -14.42`
- `2026-04-01 66000-71000`：`USD-normalized executable profit ≈ -431.33`，`APR ≈ -14.44`

汇总统计：
- `positive_mid_count = 0`
- `positive_exec_count = 0`

这已经不是“偶尔有正 edge 但不稳定”，而是当前 survivor 规定的最小检查范围内，**系统性没有留下 executable positive pocket**。

## 系统认知更新
这轮改变系统认知的不是“box spread 不存在”，而是更具体的一句：

> `Rank 243` 作为 `USD-normalized executable box APR` 这个对象，经过唯一 survivor follow-up 后已被诚实收口：在 Deribit BTC 近月近 ATM、宽度 `500~5000 USD` 的最小 executable 检查里，repo 的大额利润来自 coin-margined 单位混用；统一 USD 口径后 mid edge 近乎归零，落到四腿 bid/ask executable 后则系统性为负，因此当前不值得升 `P2`，应回 `background/P0`。

## 为什么不是 blocked
不是因为数据缺失或脚本跑不通；相反，这轮已经拿到了足够 decisive 的否定性证据。
因此这里应记为：
- `status = done`
- 结果 = `survivor 用尽后回 background/P0`

## 对 runtime 的直接影响
- `Surviving candidate slot` 应清空为 `none`
- `followup_budget_remaining` 应记为 `0`
- `Background pool.latest_parked` 应更新为 `Rank 243` 本轮收口结果
- `cycle_plan` 第 1 项应写成已完成，不再保留开放式 follow-up

## 一句话 result
`Rank 243` 的唯一 survivor follow-up 已证明：在统一 USD 单位并切到四腿 executable 口径后，Deribit BTC 近月近 ATM box spread 不再保留可升 `P2` 的真实 pocket；因此 survivor 用尽后回 `background/P0`。