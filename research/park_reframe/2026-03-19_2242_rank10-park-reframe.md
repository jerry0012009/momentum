# 2026-03-19 22:42 UTC — Rank 10 park reframe review

## Reviewed rank
- `Rank 10 / volatility-managed EMA / ATR sizing overlay`
- Original status stays: **`park / evidence pool`**
- This round verdict: **`derived_hypothesis_drafted`**

## 1) 原 rank 为什么 park？
`Rank 10` 原始 fast-lane clean replication 测的是：保留 `EMA20 > EMA50` 方向层，再用 `ATR_ref / ATR14` 的 clipping 仓位缩放（`0.75~1.25`、`0.50~1.50`、`0.25~1.75`）去回答“波动管理能不能把这条 EMA 线救活”。

原结论很硬：**没有救活，反而更差。**
- `baseline_100 @ 6bps/side`：跨资产 `mean_total_return≈-15.66%`、`positive_asset_ratio=0/3`
- 主变体 `atr_clip_050_150 @ 6bps/side`：`mean_total_return≈-26.21%`、`mean_max_drawdown≈-35.03%`、`positive_asset_ratio=0/3`
- 时间 / 参数 / 跨标的 / 成本-交易数 四项 `Light Stability Pack` 全部出现硬 fail

所以原 `park` 不是“参数还没调好”，而是：**把 ATR-vol scaling 当作这条 EMA 线的 standalone rescue axis，在当前 15m crypto clean-room 口径下已经被审计成失败。**

## 2) 它更像 hard park 还是 soft park？
我把它判成 **`soft park`**。

不是因为原 verdict 不够硬，而是因为它失败得很集中：
- 失败的是“`ATR_ref / ATR14` 这套 clipping 仓位缩放 + EMA baseline”作为**独立策略/独立 rescue line**的写法；
- 不是“ATR / stop-distance / volatility normalization 这一整类 risk-layer 信息彻底没用”。

换句话说，**原 Rank 10 的角色更像写错了**：它不太像该被当成独立 alpha 或独立 admission 线，而更像 shared risk overlay。

## 3) 有没有可救信号？
有，但只是一条很窄的可救信号：

### 可救信号 A：最近旁支证据已经把“ATR 信息”收敛到 shared sizing / veto 角色
`2026-03-19 13:44 UTC` 的 digest《别把 ATR 只当止损距离：`stopDistancePct` 更像 breakout-short / Fib / EMA-PSAR 的 shared size-veto 层》给了一个很贴 Rank 10 主题、但职责更窄的旁支：
- 不再问“ATR 缩放能不能直接救活一条 EMA alpha”；
- 改问“`stopDistancePct=(ATR*K)/close` 能不能作为 shared risk overlay，在高波动/高 stop-distance 事件里做 `size-down / veto`”。

这条旁支的本地代理快检至少给出一个值得保留的方向性信号：
- 固定名义：`net8_mean≈-0.49 bps/笔`
- `size-down` 后：`sized_net8_mean≈+1.22 bps/笔`
- 最差的明确就是 high-ATR 桶：`net8_mean≈-6.14 bps`

这说明 **ATR 主题本身不一定死掉了，死掉的是“把它写成 standalone EMA rescue clip”这层职责**。

### 可救信号 B：它天然适合 shared overlay，而不是第四条 entry alpha
原 Rank 10 的好处一直不是“它会给新 trigger”，而是它天生就是 risk-layer 语义；这跟现在 desk 很缺的 shared overlay 角色是对得上的。也就是说，**题目没必要推翻，只要降级职责。**

## 4) 最值得改的唯一一刀是什么？
**唯一修改轴：把 `ATR_ref / ATR14` 的 standalone volatility-managed EMA sizing，改写为 `ATR stopDistancePct` shared size-veto overlay。**

只改这一刀，不再同时改：
- 不换 universe
- 不换 trigger family
- 不偷带第二层 regime
- 不偷带 long/short allocation matrix
- 不把 exit / trailing / time filter 一起塞进来

更直白地说：
- 原 Rank 10：`ATR scaling` 是这条线自己的主角
- 新提案：`ATR stopDistancePct` 只做现有 setup 的 shared risk gate / sizing layer

## 5) 是否值得形成新的 derived hypothesis？
**值得。**

原因：
1. 原 `park` 审计意义非常清楚，保留即可；
2. 新旁支不是“再调 clip 参数”，而是**把同一主题降级到更诚实的职责层**；
3. 改动轴足够单一，bot2 后续也能直接判断要不要入板。

因此本轮结论是：**`derived_hypothesis_drafted`**。

## 6) 新假设的 trade on / trade off
### Proposed derived hypothesis
- `proposed_rank = Rank 10b`
- `source_rank = Rank 10`
- `single modification axis = demote standalone volatility-managed EMA / ATR sizing into an ATR stopDistancePct shared size-veto overlay`

### trade on
不再让 `Rank 10` 自己决定方向或单独开仓；保留现有 `breakout-short / Fib retest_hold / EMA-PSAR continuation` 的原始 entry，只在每个 setup 触发时额外计算：
- `stopDistancePct = (ATR14 * K) / close`（第一轮先固定 `K=2`）
- 然后只比较三臂：
  1. `base`
  2. `size_mult = clip(median(stopDistancePct)/stopDistancePct, 0.5, 1.5)`
  3. `high_stopDistancePct veto`（高分位直接不做）

第一轮目标只回答：
- 高 ATR / 高 stop-distance 事件是否值得 `size-down / veto`
- 而不是让 ATR 自己变成 entry alpha

### trade off
放弃“volatility-managed EMA sizing 本身就是独立 alpha / 独立 rescue line”的原 Rank 10 读法，换取更诚实的 shared risk overlay 角色。

代价也要写清：
- 它不再是独立策略；
- 如果阈值过严，可能只是靠砍交易数美化结果；
- 所以第一轮必须只测 `base vs size-down vs veto`，不偷带新 trigger / exit / regime / allocation overlay。

## 7) 为什么是现在（why now）
因为原 Rank 10 的失败已经被审计得足够清楚：继续在 `ATR_ref / ATR14 clip` 那条线上补参数，只会重复消费旧结论。

而最近的新旁支证据又刚好把同主题收敛到一条更窄、也更贴 desk 当前缺口的读法：
- 不是“ATR 能不能救一条 EMA 线”；
- 而是“高 stop-distance 事件要不要统一降仓/禁做”。

这是一条**保留原 park、只改角色、不改主题**的诚实 reframe。

## 8) 建议写回 queue 的短提案格式
- `Rank 10b | proposed_rank=Rank 10b | source_rank=Rank 10 | status=derived_hypothesis_drafted | single modification axis=demote standalone volatility-managed EMA / ATR sizing into an ATR stopDistancePct shared size-veto overlay | trade on=不再让 Rank 10 自己决定方向或单独开仓；只在现有 breakout-short / Fib retest_hold / EMA-PSAR continuation setup 触发时额外计算 stopDistancePct=(ATR14*K)/close（第一轮先固定 K=2），并比较 base vs size_mult=clip(median(stopDistancePct)/stopDistancePct,0.5,1.5) vs high_stopDistancePct_veto 三臂；ATR 信息只负责 size-down / veto，不单独开仓 | trade off=放弃“ATR_ref / ATR14 clipping 本身就是独立 alpha / 独立 rescue line”的原 Rank 10 读法，换取更诚实的 shared risk overlay 角色；代价是它不再是独立策略，而且若阈值过严，可能只是靠砍交易数美化结果，因此第一轮必须只测 base vs size-down vs veto，不偷带新 trigger / exit / regime / allocation overlay | why now=原 Rank 10 clean replication 已把 standalone volatility-managed EMA 这条路审计得很清楚：收益、回撤、时间、参数、跨标的、成本四项一起失败；但 2026-03-19 新增的 ATR stopDistancePct digest 又正好给出一条只改角色、不推翻原 park 的窄 reframe，因此现在值得保留一个 queue-only 的 Rank 10b 提案 | suggested initial state=source intake / clean replication next`

## 9) 本轮最终结论
- Final verdict: **`derived_hypothesis_drafted`**
- Original `Rank 10` verdict remains: **`park / evidence pool`**

## 10) Commit note
- 本轮只做最小必要文档改动。
- 默认不改 `docs/TODO.md` 顶部排班。
- 若工作区存在无关脏文件，则不混提；本轮以 selective doc update 为主。