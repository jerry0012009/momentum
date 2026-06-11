# Rank 304 — survivor 唯一 follow-up 收口：回到 background/P0

- 时间：2026-04-03 05:59 UTC
- 对象：`Rank 304 / EMA trend shell × OBV caution veto × ATR trailing stop`
- 类型：survivor follow-up / exit decision
- 结论：`background/P0`

## 本轮只回答一个问题

当前 survivor 的唯一 follow-up，不是再讨论这份 repo 的 daily BTC walk-forward headline，而是要诚实回答：

> 把 `OBV caution veto + swing/ATR stretch + ADX override` 塞进 baseline `EMA trend shell` 后，是否已经有足够干净的证据说明它在 liquid-perp `15m/5m` short-cycle 口径下，主要是**改善尾部坏单**，而不只是**让交易变少**。

## 本轮判断

我的结论是：**没有。按 policy，这个 survivor 应在这里收口并回到 `background/P0`。**

## 为什么不再继续留在前排

### 1) 现有材料没有给出 baseline vs variant 的干净对照
这份对象最值得验证的新增主语，是 `caution veto` 层，而不是 `EMA trend` 本体。

但当前 source 只给了一个**打包后的完整策略壳**：
- `EMA trend`
- `volume confirm`
- `OBV caution`
- `swing/ATR stretch`
- `ADX override`
- `ATR sizing`
- `ATR trailing stop`
- walk-forward / cost stress

它没有给出我们这一步真正需要的 clean-room 证据：
- baseline `EMA trend shell`
- versus `EMA trend shell + caution veto`
- 以及尾部损失、adverse excursion、max drawdown、trade density 的直接对照

也就是说，当前材料**无法证明新增增量来自 veto 层本身**。

### 2) 现有结果更像“复杂打包壳能活过几段样本”，不是“veto 明确改善尾部”
notebook 的 daily BTC walk-forward 说明这条完整壳不是纯垃圾：前三个 OOS fold 能活。

但这一步对 survivor 的 admission 价值有限，因为它回答的是：
- “整套高度参数化壳在 daily BTC 上有些阶段可行吗？”

而不是：
- “`OBV caution + stretch veto` 是否在 short-cycle 里稳定减少追涨末端坏单？”

后者才是 Rank 304 作为独立对象留在前排的核心理由。

### 3) 参数自由度太高，当前更像 bundle，而不是便宜诚实的组件证据
这份 notebook 把大量自由度都压在 veto / stop / sizing 附近：
- `swing_caution`
- `atr_caution`
- `caution_threshold`
- `obv_ma_period`
- `obv_lookback`
- `adx_override`
- 多组 `stop_mult_*`
- `stop_atr_scale`

这意味着即便 headline OOS 还能看，也很难据此认定：
- 真正起作用的是 `caution veto`，
- 而不是“多参数止损/仓位/过滤组合后，总体交易数下降、偶然避开坏样本”。

### 4) 当前没有唯一明确的 re-scope 方向值得保留一次回退
如果要做 `P2->P1 re-scope`，必须存在单一、明确、可落地的收窄方向。

但 Rank 304 当前还没进 `P2`，而且它唯一一次 survivor follow-up 之后，仍然没有形成一个足够唯一的收窄结论，例如：
- 只在 BTC `15m` 成立
- 只在某个 session 成立
- 只保留 `OBV veto`、其余全部砍掉

这些方向现在都只是猜测，不是被当前证据逼出来的唯一 re-scope。

### 5) 按 policy，survivor 只有这一次便宜诚实检查；答不出增量，就该收口
Rank 304 的 front-slot 理由，是它把 `OBV divergence + stretch caution + ADX override` 组织成一个很像 production veto layer 的结构。

但 survivor 这一步要求的是：
- 要么证明它已足够独立，值得进 `P2`
- 要么证明它只在唯一明确范围内成立
- 否则就应退出前排

当前证据做不到前两点；继续停留只会把它变成“再补一点 short-cycle 对照”的开放式拖延。

## 本轮产出的系统认知变化

> `Rank 304 / EMA trend shell × OBV caution veto × ATR trailing stop` 的 survivor 唯一 follow-up 已诚实收口：当前材料仍只能证明“一个带 OBV/stretch veto、ADX override、ATR stop/sizing 的高度参数化趋势壳在 daily BTC 若干 OOS fold 可活”，却**不能证明**相对 baseline `EMA trend shell` 的新增增量主要来自 `caution veto` 对 short-cycle 尾部坏单的改善而非单纯减交易，因此不值得继续占用前排，回到 `background/P0` 作为单资产 trend family 的参考组件记录。

## 对 runtime 的直接影响

- `Surviving candidate slot` 清空
- `Rank 304` 停止占用前排
- 后续若要再用，应作为已有单资产 trend / breakout 家族的组件参考，而不是自动 reopen 的独立对象
