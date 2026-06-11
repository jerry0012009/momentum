# Rank 356 / breadth-conditioned XS momentum × shallow-bear sign-flip router intake keep P1

- Time: 2026-04-07 14:49 UTC
- Target: `research/quant_digests/2026-04-07_1412_breadth-conditioned-xs-momentum-router-alpha.md`
- Action: fresh intake first verdict
- Verdict: `keep_P1`
- Rank: `356`

## What changed
这条对象保留下来的不是“再讲一次 generic XS momentum”，而是一个与 `Rank 213 / large-cap XS momentum × short-leg jump veto` 不同的 desk 命题：**alpha 本体仍是横截面强弱排序，但决定收益形态的关键增量不再是 short-leg risk 控制，而是一个极便宜的 market-breadth router——市场轻微转负时，把书从 `winner continuation` 短暂翻成 `loser bounce`；若跌深则直接 flat。**

## Why it is not background / P0
1. 这次新对象的独立主语不是“momentum 家族”这四个字，而是 **`XS ranking + shallow-bear sign-flip + deep-bear flat`** 这条完整路由。它回答的是 *什么时候 continuation 应该直接翻成 reversal*，而不是 `Rank 213` 已占用的 *如何控制 short leg jump concentration*。
2. digest 给出的可迁移实验口径是具体的：`xs_raw_i = ret_i(L) * (vol_i / EWMA(vol_i, L))`，再用 `r_mkt` 的三段阈值决定 `+w / -w / 0`。这已经是一个可以独立复刻、独立失败、也可独立通过的 raw alpha shell。
3. repo 证据虽来自日频，但至少说明这不是空喊 regime：holdout blend Sharpe `1.81 / 1.98` 高于 benchmark `1.35`，且 XS 腿与 route 逻辑都写得足够清楚，值得保留一次最小 decisive follow-up。

## Why it is not P2 yet
1. 当前证据主体仍是 **日频 notebook**；用户环境要落地的是 `5m/15m` short-cycle desk，router 会不会在高频口径里沦为噪音开关，暂时没有过关证据。
2. digest 已经自己点出最关键风险：浅跌翻书若只靠更高 turnover 才成立，`post-cost / post-slippage / funding` 很可能把 pocket 吃光。
3. 目前还没有证明它在 liquid-major perp/spot universe 上跨过 `effectiveness / time stability / parameter stability / honesty` 的 admission 门槛，所以不能直接升 `P2`。

## Minimal honest next follow-up
若进入 survivor，唯一一次便宜 follow-up 应直接回答：
- 在 `8~12` 个 liquid majors 的 `15m` 主实验、`5m` 复核里，`shallow-bear sign-flip` 是否在成本后仍优于 plain XS continuation；
- `θ`（浅跌阈值）与 `L/Lm` 做最小 sweep 后，是否存在非单点参数 pocket；
- 若 router 的收益主要来自少数高换手噪音段，或 deep-bear flat 才是唯一有用部分，则应诚实收口回 background，而不是继续把它包装成新主线。

## Runtime implication
- 正式分配 `Rank 356`。
- 本轮 first verdict 为 `keep_P1`。
- 由于当前 `Surviving candidate slot` 为空，`Rank 356` 应进入该槽位，并获得唯一一次 follow-up 预算。

## Result sentence
`Rank 356 / breadth-conditioned XS momentum × shallow-bear sign-flip router` fresh intake 已完成 first verdict：它的独立主语不是 generic XS momentum，而是 `winner continuation / shallow-bear loser-bounce / deep-bear flat` 这条可独立复刻的 regime router，因此本轮保留为 `keep_P1` 并进入 survivor；但现有证据仍主要来自日频 repo，尚不足以证明它在 short-cycle、成本后口径下已达到 `P2` admission。