# Rank 356 — survivor follow-up — background/P0 on breadth-conditioned XS sign-flip router

- 时间：2026-04-07 16:12 UTC
- 对象：`Rank 356 / breadth-conditioned XS momentum × shallow-bear sign-flip router`
- 轮次角色：bot3 自动执行
- 结论：`keep_P1 but follow-up exhausted -> background/P0`

## 为什么这一步改变系统认知
`Rank 356` 的 intake 值得保留，是因为它把命题写成了一个清楚的 desk 问句：**横截面强弱排序本身是否仍该继续追随，还是在 market breadth 轻微转负时，应该短暂翻成 loser-bounce；若跌深则 flat。**

但 survivor 那唯一一次 follow-up 要回答的，不是“这个故事听起来聪不聪明”，而是：在 `15m`、`8~12` 个 liquid majors、成本后口径里，**这个 sign-flip router 是否真的优于 plain XS continuation，而且不是单点参数幻觉。**

基于当前项目现成的 `365d / 15m` 跨资产 cache 做最小 clean-room 后，答案很直接：**没有。**
更明确地说，当前可复用样本里，plain XS continuation 本身很强；而 `shallow-bear sign-flip` 这层 router 在全部 sweep 下都把结果做差，且差得不是一点点，而是稳定、跨参数、跨时间段地更差。因此这条对象不该升 `P2`，也不该继续占用 survivor 槽位。

## 本轮 clean-room 口径
数据来源：
- 目录：`reports/artifacts/scout_rank32b_slope_floor_continuation_15m/cross_asset_cache/`
- 资产：`BTC/ETH/BNB/SOL/XRP/ADA/LINK/DOGE/AVAX/LTC/ATOM/DOT`（12 个 liquid majors）
- 频率：`15m`
- 长度：`365d`

执行口径：
- 信号用 bar `t` 的收盘信息计算；
- 持仓统一 `shift(1)`，即从 bar `t+1` 开始生效；
- 收益按 `open-to-open` 近似执行；
- 成本按 turnover 收单边 `4 / 8 / 12 bps`；
- 对比对象只有两条：
  1. `plain_xs_continuation`：只做横截面 winner-minus-loser continuation；
  2. `router_signflip`：当 `r_mkt > 0` 继续做 continuation；当 `0 > r_mkt > -θ` 直接翻成 `-w_xs`；当 `r_mkt <= -θ` 则 flat。

参数 sweep：
- `L = 32 / 64 / 96`
- `Lm = 8 / 16 / 24`
- `θ = 0.3% / 0.5% / 0.8%`
- `vol_adj = off / on`

产物：
- `reports/artifacts/rank356_breadth_router_followup/summary.csv`

## 关键结果
### 1) router 在全部 54 个参数组合上都输给 plain continuation
以成本后 `mean_net_bps` 对比：
- `4 bps`：`router better combos = 0 / 54`
- `8 bps`：`router better combos = 0 / 54`
- `12 bps`：`router better combos = 0 / 54`

也就是说，这不是“多半不行，但也许还有一两个 pocket”；而是 **当前 sweep 下没有任何一个组合，sign-flip router 比 plain XS continuation 更好。**

### 2) 最好的 plain continuation 仍然明显为正；router 则稳定转负
代表性对比（`L=32, Lm=24, θ=0.8%, vol_adj=off`，`8 bps` 成本）：
- `plain_xs_continuation`
  - `mean_net_bps = +1.406`
  - `Sharpe ≈ 16.16`
  - `max_dd ≈ -12.9%`
  - `turnover ≈ 0.373`
- `router_signflip`
  - `mean_net_bps ≈ -2.578`
  - `Sharpe ≈ -29.86`
  - `max_dd` 明显更差
  - `turnover ≈ 0.514`

翻成人话：**在这组最接近 digest 命题的 15m clean-room 里，浅负 breadth 时把书翻成 loser-bounce，不是在给 continuation 加一层保护，而是在主动拆掉本来就有效的 XS continuation。**

### 3) 问题不是某个时间段偶然失灵，而是四段时间里都持续更差
同样用上面的代表性组合、`8 bps`：
- `plain`
  - `Q1: +1.599 bps/bar`
  - `Q2: +1.621 bps/bar`
  - `Q3: +1.435 bps/bar`
  - `Q4: +0.969 bps/bar`
- `router`
  - `Q1: -3.779 bps/bar`
  - `Q2: -3.083 bps/bar`
  - `Q3: -4.107 bps/bar`
  - `Q4: -4.064 bps/bar`

这说明问题不是“router 只是在最近失灵”或“只在个别阶段不稳”，而是 **它对 plain continuation 的破坏，在样本的四个时间段都持续存在。**

## 出口判断
按 policy，这个 survivor 本轮必须给出收口结论，不能再继续开放式 `keep_P1`。

本轮结论：
- **不是 `promote_P2`**：因为 `15m` 主实验下，router 没有形成任何成本后优于 plain continuation 的非单点参数 pocket；
- **也不是 `one-time P2->P1 re-scope`**：当前对象还没进 `P2`，而且“退回去改个更窄参数”并不能解释为什么 router 在全部 sweep 下都系统性劣化；
- **因此应诚实收口为 `background/P0`**：保留“breadth 可以作为 desk 侧 veto / risk state 参考”的启发，但不再把 `shallow-bear sign-flip` 当作值得继续前排推进的独立 raw alpha 主语。

## 对 runtime 的直接影响
- `Surviving candidate slot`：`Rank 356` 用完唯一一次 decisive follow-up，本轮释放为 `none`
- `Background pool`：新增记录 `Rank 356` 已在 survivor follow-up 中诚实收口为 `background/P0`，不得自动 reopen
- `Active P2 slot`：继续保持 `none`

## Result sentence
`Rank 356` 的 survivor follow-up 已完成：在 `12` 个 liquid majors 的 `365d/15m` clean-room 中，`shallow-bear sign-flip` router 在 `L=32/64/96`、`Lm=8/16/24`、`θ=0.3%/0.5%/0.8%`、`4/8/12 bps` 的全部 `54` 个参数组合里都劣于 plain XS continuation，且四段时间切片也持续为负，因此该对象本轮正式收口为 `background/P0` 并释放 survivor 槽位。
