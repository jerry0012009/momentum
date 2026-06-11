# Rank 299 — survivor follow-up 收口：EMA(RSI) regime gate 没把裸 EMA trend 壳变成成本后可存活的 short-cycle sleeve，survivor budget exhausted -> background/P0

- 时间：2026-04-03 00:03 UTC
- 对象：`Rank 299 / EMA(RSI) regime hierarchy trend alpha`
- 执行动作：唯一合法的 survivor follow-up / exit decision
- 结论：`survivor budget exhausted -> background/P0`
- artifact：`reports/artifacts/rank299_survivor_followup/summary.csv`

## 这轮实际做了什么
直接按 intake 时承诺的最小 clean-room 检查，拿现成的高流动 BTC perp 公共 kline cache 做对照：

- 数据：
  - `BTCUSDT__120d__15m__perp.csv`
  - `BTCUSDT__120d__5m__perp.csv`
- baseline：裸 `EMA9 > EMA20` 趋势壳，首次转为 `trend_on` 时开多
- gate 版本：
  - `EMA7(RSI14) > 60`
  - `EMA9(RSI14) > 60`
  - 上述两档再各加一层 `PSAR bull` 过滤
- 持有：`1 / 2 / 4` bars
- 成本：`6bps/side` 与 `10bps/side`

这里故意不继续补更复杂资金管理或多腿执行，只回答 cycle_plan 要的那句：

> 这条 `EMA(RSI) regime gate × uptrend-only trend shell` 到底是给短周期趋势壳留下了成本后净增益，还是只是在砍交易次数？

## 核心结果
### 1) 15m：gate 主要是在砍交易，不是在造出可存活 edge
6bps/side 下：

- baseline，持有 4 bars：`272` 笔，`avg_gross_ret = +0.0017%`，`avg_net_ret = -0.1183%`，`total_net_return = -27.81%`
- `gate7_psar`，持有 4 bars：`170` 笔，`avg_gross_ret = +0.0012%`，`avg_net_ret = -0.1188%`，`total_net_return = -18.59%`
- `gate9`，持有 4 bars：`130` 笔，`avg_gross_ret = -0.0333%`，`avg_net_ret = -0.1533%`，`total_net_return = -18.33%`

读法很直接：
- trade count 确实被砍了 `37%~52%`
- 但成本后每笔期望仍然是负的
- 更好的总收益主要来自“少做、少亏”，不是 gate 把趋势壳提升成了正期望策略

### 2) 5m：最好的 pocket 也只是 gross 略正，成本后一律为负
6bps/side 下最好的几档：

- `gate9_psar`，持有 4 bars：`465` 笔，`avg_gross_ret = +0.0167%`，`avg_net_ret = -0.1033%`，`total_gross_return = +7.54%`，`total_net_return = -38.33%`
- `gate9`，持有 1 bar：`417` 笔，`avg_gross_ret = +0.0115%`，`avg_net_ret = -0.1085%`，`total_gross_return = +4.86%`，`total_net_return = -36.44%`

也就是说：
- `EMA9(RSI)` 相关 gate 在 5m 上的确留下了一个“gross 看起来不像完全错”的小 pocket
- 但这个 pocket 远远不够覆盖 `6bps/side`，到 `10bps/side` 只会更差
- 所以它还不能算是 desk 可用的 short-cycle trend sleeve

### 3) `EMA7(RSI)` 没有表现出比 `EMA9(RSI)` 更稳的 desk 版优势
论文 headline 暗示 `EMA7` 更优，但在这轮 BTC perp short-cycle clean-room 里：
- `EMA7` 系列没有给出优于 `EMA9` 的成本后优势
- 加 `PSAR` 也没有把负期望翻成正期望

## 为什么这轮不能 promote_P2
要升 `P2`，至少得看到一个很朴素的事实：

> regime gate 不是只把交易次数砍掉，而是真的把裸趋势壳改造成了成本后更诚实、可继续 admission 的 sleeve。

这轮没有看到这个事实。

更准确地说：
1. **15m** 上的改善主要来自少做，而不是正 edge 成形；
2. **5m** 上最好 pocket 仍只是 gross 微正、net 明显为负；
3. `EMA7/EMA9 + PSAR` 都没有给出足以继续前排占资源的 decisive evidence。

所以这条对象现在最诚实的状态不是 `promote_P2`，而是：

> **保留为“regime gate 可能降低 fee drag / drawdown，但尚未把 BTC perp short-cycle EMA trend 壳做成可存活 net alpha”的反例证据。**

## runtime 影响
- `Rank 299` 的 survivor follow-up 已执行完
- survivor budget 用尽
- 对象不升 `P2`
- 对象移回 `background/P0`

## 给 bot2 的最小可用句子
`Rank 299` 的唯一 survivor follow-up 已收口：BTC perp `15m/5m` clean-room 下，`EMA(RSI)>60` uptrend gate（含 `PSAR` 保护）确实能砍掉 `37%~52%` 的交易，但没有把裸 `EMA9/20` 趋势壳提升成成本后可存活的 short-cycle sleeve；最好 pocket 也只是 5m 上 gross 微正、net 明显为负，因此本轮结论是 `survivor budget exhausted -> background/P0`，不升 `P2`。
