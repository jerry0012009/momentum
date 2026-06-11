# 2026-03-24 16:34 UTC — Rank 13 park reframe revisit

- source rank: `Rank 13 / partial-moment asymmetry TSMOM gate`
- current authoritative verdict in `docs/TODO.md`: `park / evidence pool`
- this round verdict: `keep_park`
- original park verdict kept: `yes`
- prior derived candidate already on queue: `Rank 13b`

## 1) 为什么这轮选 Rank 13
- 本轮仍受 `Rank 1~37` 范围约束；
- `Rank 13` 上次 park-reframe 复盘是 `2026-03-20 00:42 UTC`，不是本日刚复盘项；
- 它已经有一个窄派生 `Rank 13b`，因此这轮重点不是“再救一次”，而是判断：最近新增证据有没有强到足以再派生 `13c`，或者该把它压回纯 `keep_park`。

## 2) 原 Rank 为什么会 park
原 Rank 13 被 park 的原因很硬，而且很集中：

- `2026-03-17 00:38 UTC` clean replication 里，primary variant `pm_guard_100 @ 6bps/side` 约为：
  - `mean_total_return ≈ -71.90%`
  - `positive_asset_ratio = 0/3`
  - `mean_max_drawdown ≈ -75.70%`
- 它只比 `baseline_sign_mom`（约 `-78.35%`）少亏一点，不是形成正 alpha；
- `Light Stability Pack` 四项一起 fail：
  - 时间稳定性 `0/3 positive buckets`
  - 参数稳定性 `0/5 positive configs`
  - 跨标的稳定性 `0/3 positive assets`
  - 成本稳定性 `0/4 positive cost levels`

所以原始被否掉的，不是“方向性波动不对称这个主题永远无用”，而是：
**把 partial-moment asymmetry 直接写成 standalone sign-momentum rescue line，在 15m crypto 上不成立。**

## 3) 它更像 hard park 还是 soft park
我这轮仍判它是 **soft park**，但偏硬。

为什么不是 hard park：
- 原主题里“上行/下行波动不对称”本身仍可能有信息；
- 这类信息更像 shared directional risk layer，而不是独立入场骨架。

为什么说偏硬：
- 原 clean replication 的负值太深，不是小修小补能救；
- 最近新增的 momentum / state / forecast 证据，更多是在指向**新的 raw-alpha 家族**，不是给 Rank 13 再开第二条 overlay 分叉。

## 4) 有没有“可救信号”
有，但没有新增到足以再派生一条新 rank。

### 现存可救信号
唯一还成立的可救信号，仍然是上一轮已经写进 queue 的 `Rank 13b`：
- 把原本的 standalone partial-moment / asymmetry gate，降级成 `RS+/RS- realized-semivariance directional veto / sizing overlay`；
- 也就是：只在已有 setup 触发时，拿 asymmetry 去做 `veto / half-size`，而不再自己决定开仓。

### 为什么这轮不新增 `13c`
因为最近新增证据并没有给出一个比 `13b` 更贴原主题、且更窄的新修改轴：

1. `2026-03-24 10:30` 的 **market-percentile state TSMOM** 证据，本质是完整 `raw alpha`：
   - 它在讲“市场组合分位状态本身可直接做多空骨架”；
   - 这更像一条新的 state-driven momentum family，
   - 不是 Rank 13 这种 asymmetry risk gate 的诚实续写。

2. `2026-03-24 08:40` 的 **rolling-FPCA intraday sign forecast** 证据，也是在讲方向预测本身：
   - 它提供的是 forecast-driven sign alpha；
   - 这条线同样更像新 family，而不是对 Rank 13 的 overlay 再细分一刀。

3. 换句话说，最近新东西回答的是：
   - “有没有别的 momentum raw alpha 可以直接做？”
   - 而不是：
   - “Rank 13 原主题还剩哪一条更诚实、且比 13b 更好的单轴改写？”

所以可救信号**有**，但仍停留在既有 `Rank 13b`；本轮没有出现足够好的新证据去诚实地产生 `Rank 13c`。

## 5) 最值得改的唯一一刀是什么
这轮结论是：**唯一还值得保留的一刀，仍然是既有 `Rank 13b` 那一刀，不新增第二刀。**

也就是：
**把 standalone partial-moment asymmetry TSMOM gate，降级成 `RS+/RS- realized-semivariance directional veto / sizing overlay`。**

本轮不改成：
- state alpha
- forecast alpha
- multi-score overlay
- 新 entry skeleton

因为那样已经不是“reframe 原 Rank 13”，而是在借题另起新家族。

## 6) 是否值得形成新的 derived hypothesis
**这轮结论：不值得。**

原因：
- 原 `park` 审计结论完全不需要推翻；
- 唯一诚实的窄 reframe 已被 `Rank 13b` 消费；
- 最近新增证据虽然说明 momentum 主题还活着，但更像新的 `raw-alpha family`，并不支持再从 Rank 13 继续切出 `13c`。

因此本轮最终结论是：`keep_park`。

## 7) 本轮回答（按要求汇总）
- 原 rank 为什么 park：因为 standalone sign-momentum + partial-moment asymmetry guard 在 15m crypto 上 post-cost 深度为负，且稳定性四项全 fail；
- 它更像 hard 还是 soft：`soft park`，但偏硬；
- 有没有可救信号：有，且只剩既有 `Rank 13b` 这一条 shared directional veto / sizing overlay；
- 最值得改的唯一一刀：仍是 `Rank 13b` 的那一刀，不新增第二轴；
- 是否值得形成新的 derived hypothesis：`不值得`；
- 本轮最终结论：`keep_park`。

## 8) 对 queue 的实际含义
- 保留 `Rank 13b` 在 `docs/PARK_REFRAME_QUEUE.md` 里的 queue-only 候选身份；
- 但本轮不把它升级，也不新增 `Rank 13c`；
- 默认不改 `docs/TODO.md` 顶部排班。

## 9) 文件与提交说明
- 本轮只更新本日志、`research/park_reframe/INDEX.md`、`docs/PARK_REFRAME_QUEUE.md`；
- 未做 git commit：`git status --short` 显示工作区存在大量与本轮无关的脏文件，当前不适合安全地 selective commit。
