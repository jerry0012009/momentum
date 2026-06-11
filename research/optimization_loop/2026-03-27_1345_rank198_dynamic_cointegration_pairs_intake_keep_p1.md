# Rank 198 intake — dynamic cointegration minute-binned pairs keep_P1

- Time: 2026-03-27 13:45 UTC
- Target: `research/quant_digests/2026-03-27_1332_dynamic-cointegration-minute-binned-pairs.md`
- Verdict: `keep_P1`
- Assigned Rank: `Rank 198`

## 本轮检查了什么
- 只按 `fresh intake` 的最小首判要求，重读该 digest，判断这条对象今天是否值得保留为前排候选；不把工作量扩成完整多腿工程，也不提前把它包装成 ready-for-paper 的结论。
- 重点只回答三件事：
  1. raw alpha 本体是否清楚；
  2. 是否能 clean-room 复刻；
  3. 当前公开市场最小 transfer check 是否还留下足够诚实的继续研究空间。

## 会改变判断的证据
- 这条对象的 alpha kernel 很清楚，不是泛泛“crypto pairs 可能均值回归”，而是：**先动态筛出协整更稳定、半衰期更短的 pair / basket，再交易 spread deviation -> convergence。** 这比很多只有 filter 没有母体 alpha 的主题更像可落地对象。
- 论文给出的 desk 组件完整：`dynamic pair-selection funnel`、`Johansen basket`、`zscore entry/exit`、`beta/vector sizing`、`volume/quote veto`、`maker/taker/funding` 成本口径都已明确，因此 clean-room 复刻成本低。
- 但 digest 自带的当代 `Binance USDⓈ-M perpetual 15m` 最小 transfer check 也明确说明：这条线**不是**“全 pair 等权就能活”的 broad edge。五组 pair 等权后 net 约 `-0.019 bps/bar`、年化 Sharpe 约 `-0.84`，组合平均已被成本与不稳定 pair 吃掉。
- 真正还留下净边的是少数 pair pocket，而不是全宇宙普适版本：本轮最清楚的是 `TRXUSDT/ADAUSDT`，net 约 `+0.051 bps/bar`、net cumulative 约 `+2.12%`、年化 Sharpe 约 `1.73`。这说明母体 alpha 还没死，但它今天更像 **selection-sensitive pocket**。

## 决策
本轮给这条对象 `keep_P1`，并分配正式编号：

> **Rank 198 / dynamic cointegration pair-basket spread convergence**

它的工作定义应收敛为：

> 在 liquid perp universe 上，先用 rolling cointegration / half-life / stability funnel 动态挑出可交易的 pair 或 stationary basket，再在 spread z-score 异常偏离时做 long-short convergence，检验其在成本后是否仍能留下稳定 pocket。

为什么是 `keep_P1`：
- raw alpha 对象足够干净，pair 版与 basket 版都能直接转成 clean-room 研究；
- 它补的是 desk 里真实缺口：`pair-selection / basket-selection + spread convergence` 这条 market-neutral baseline，而不只是又一个 filter；
- 当代 quick check 虽然否掉了“全篮子 broad deployment”叙事，但没有否掉 selection-sensitive pocket，本轮仍值得保留一次 survivor follow-up。

为什么不是 `promote_P2`：
- 当前 contemporaneous 证据只支持“少数 pocket 仍留净边”，不支持它已经成为稳定、广谱、接近 paper launch 的 admission 对象；
- 下一步最该回答的是 **selection funnel / basket 结构** 是否能把 pocket 从个别幸存扩成可复制框架，而不是直接进入更重的 P2 admission。

## Runtime writeback
- `Fresh intake slot`：将本对象写成已完成首判，结论 `keep_P1`，并正式赋予 `Rank 198`。
- `Surviving candidate slot`：占用为 `Rank 198 / dynamic cointegration pair-basket spread convergence`，保留唯一一次 follow-up 预算。
- `cycle_plan #1`：标记为 `done`，result 写明“当前 broad basket 已被成本打回负值，但 TRX/ADA pocket 仍留净边，因此该对象保留为 `keep_P1`，不直接升 `P2`”。

## Reader-facing takeaway
这条线今天最诚实的结论不是“crypto dynamic pairs 还能整篮子无脑做”，而是：

**Rank 198 = dynamic cointegration 选对/选篮子之后的 spread convergence pocket。**

也就是说，值得保留的不是“pairs 普遍有效”，而是“少数 surviving pair/basket pocket 仍可能有效，而真正要卷的是 selection funnel 和 basket 结构，不是继续微调单个 z-score 门槛”。
