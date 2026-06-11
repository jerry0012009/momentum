# Rank 363 / survivor follow-up exhausted -> background

- 时间：2026-04-08 05:16 UTC
- 执行轮次：bot3 13m auto
- 对象：`Rank 363 / HTF EMA gate × 15m RSI pullback continuation`
- 结论：`keep_P1 exhausted -> background`

## 本轮只回答的问题
作为当前唯一合法 survivor，这条 `HTF EMA200 regime gate -> LTF shallow pullback continuation` 在统一 majors perp 样本、统一 post-cost 口径与最小逐层剥皮要求下，是否已经足够诚实地升级到 `P2`。

## 本轮收口判断
结论是否定的，而且这不是“再补一点就好”的类型，因此本轮不再继续占用 survivor 前排，而是直接收口到 `background`。

## 为什么这轮不能升 P2
1. **缺少 clean-room replication 事实层。** 目前对象的核心证据仍是 repo/source audit 与策略壳拆解，没有一份在统一 majors perp 样本下跑出来的 post-cost replication 结果，连最基本的 `expectancy / trade`、trade count、成本后盈亏分布都还不存在。
2. **最关键的 decisive question 仍未被回答。** 这条对象能否成立，核心不是“规则看起来顺不顺”，而是：
   - `HTF gate only`
   - `+ EMA9/21`
   - `+ RSI zone`
   - `+ MACD`
   - `+ BB mid`
   逐层加上去后，到底是哪一层在贡献净边。现在没有任何统一样本上的 layer attribution，因此无法证明它不是单纯在吃泛趋势 beta，或只是靠过滤把样本压到少量顺风单。
3. **当前缺口不是唯一明确的 re-scope。** 这不是“只差把宿主改成 ETH/SOL-only”或“只差把 15m 改成 5m entry”的问题，而是 admission 所需的第一性证据根本没落地；因此它也不满足一次性 `P2->P1 re-scope` 的前提。

## 为什么本轮直接 background，而不是继续 keep_P1
`Rank 363` 已经用掉 survivor 的唯一 follow-up 预算，但本轮仍未得到能改变层级的 replication 证据，也没有出现唯一明确的 re-scope 方向。按当前 policy，这类对象应诚实写成 `keep_P1 exhausted -> background`，而不是继续把“需要 clean-room replication”挂在前排反复拖延。

## 本轮 verdict
`Rank 363` 目前仍只是一个定义清楚、值得保留备忘的 trend-pullback hypothesis：它把 `HTF trend gate + LTF shallow pullback continuation` 这条 raw alpha 主语压清了，但没有在统一 majors perp 样本、统一 post-cost 口径下证明净边存在，也没有证明增益来自 pullback continuation 本体而非泛趋势 beta / 过滤压样本，因此本轮诚实结论为 `keep_P1 exhausted -> background`。
