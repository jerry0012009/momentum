# Rank 247 / VPIN-driven jump-sign continuation — survivor follow-up exhausted -> background

- 时间：2026-03-30 06:04 UTC
- 轮次角色：bot3 auto executor
- 对应 cycle_plan 小点：`Rank 247 / VPIN-driven jump-sign continuation`
- 前置记录：`research/optimization_loop/2026-03-30_0505_rank247_vpin_jump_sign_continuation_intake_keep_p1.md`
- 结论：`survivor follow-up exhausted -> background/P0`

## 这一步回答的问题
在固定公开可复现的 `BTC` 逐笔/聚合成交口径下，`high-VPIN × same-sign realized jump` 的 `1/3/5 bars` continuation 是否真的留下了一个成本后还能站住的独立 pocket，而不是又一条会被普通 jump-followthrough / flow 近邻吸收的微结构叙事。

## 本轮采用的最小诚实 replication
这轮严格只做 survivor 允许的那一次最小 decisive follow-up，不再叠第二层 regime / filter / exit：

- 数据：Binance USDⓈ-M Futures 公共 `aggTrades`
- 标的：`BTCUSDT`
- 样本：`2024-01-15` 到 `2024-01-21` 共 `7` 个完整自然日
- bar：逐笔聚合成 `1m`
- toxicity 代理：`rolling 50min abs(signed_notional) / rolling 50min total_notional`
- high-VPIN 定义：上述 toxicity 代理在滚动 `1d` 历史中的 `top 10%`
- jump 定义：`abs(ret_1m) >= 2 * rolling 60m sigma`
- 方向确认：`flow_sign == jump_sign`
- 入场：事件后 **next-bar open**
- 持有：固定 `1 / 3 / 5 bars`
- 去重：`no-overlap`，按最长 `5 bars` 持有去重
- 成本：round-trip `3 / 5 / 8 bps`
- 产物目录：`reports/artifacts/rank247_survivor_followup_20260330/`

## 关键结果
### 1) 最小 replication 下没有出现成本前都为正的 continuation pocket
`high-VPIN × same-sign jump` 去重后只留下 `68` 个事件；三档持有的 gross 都没有转正：

- `1 bar`: `gross_mean = -0.71 bps/event`，`win_rate = 42.65%`
- `3 bars`: `gross_mean = -0.19 bps/event`，`win_rate = 48.53%`
- `5 bars`: `gross_mean = -0.39 bps/event`，`win_rate = 41.18%`

对应成本后均值：
- `1 bar`: `net@3/5/8bps = -3.71 / -5.71 / -8.71`
- `3 bars`: `net@3/5/8bps = -3.19 / -5.19 / -8.19`
- `5 bars`: `net@3/5/8bps = -3.39 / -5.39 / -8.39`

也就是说，这条 survivor follow-up 连 **gross continuation** 都没站住，更不用说 realistic cost 之后。

### 2) 它没有形成独立于普通 jump-followthrough 的更强 pocket
为了避免把“高 VPIN 没用”误判成“jump 本身也许有用只是这里太严”，我额外只做了同一事件框架下的最小控制组对照（不改数据、不改执行）：

- `jump_only`
  - `1/3/5 bars gross = -0.64 / -0.73 / -1.35 bps`
- `jump_plus_sameflow`
  - `1/3/5 bars gross = -0.59 / -0.71 / -1.21 bps`
- `highvpin_jump_sameflow`
  - `1/3/5 bars gross = -0.71 / -0.19 / -0.39 bps`

这里唯一稍微没那么差的是 `3 bars` 的 `-0.19 bps`，但它仍然是负的，而且事件数只有 `68`。这说明：

> 高 VPIN 并没有把普通 same-sign jump followthrough 提纯成一个可交易 continuation pocket；它只是把样本进一步砍薄了，但没有把方向质量推过 0。

### 3) 因而这轮不该再把它留在前排继续开放式续命
`Rank 247` 的唯一 survivor follow-up 原本就只该回答一个问题：

> 固定公开口径后，`high-VPIN × same-sign jump` 是否真的留下了干净、可复现、成本后还能站住的短窗 continuation？

当前答案是：**没有。**

而且这个“没有”已经是最便宜、最贴题的 event-level replication；继续拖只会变成：
- 继续换 jump 阈值
- 继续换 VPIN proxy
- 继续换小时段 / weekday filter
- 继续在负 gross 的母体上做切样本找 pocket

这已经超出 survivor 唯一 follow-up 的预算，也不符合 policy 对前排资源的诚实要求。

## hard verdict
- **`Rank 247 / VPIN-driven jump-sign continuation`：不升 `P2`，回 `background/P0`**
- 原因不是“VPIN 论文没价值”，而是：**在最小公开 BTC event-study 口径下，`high-VPIN × same-sign jump` 没有留下独立、可交易、成本后站得住的 continuation pocket。**

## runtime 结论
- `Surviving candidate slot` 应清空为 `none`
- `followup_budget_remaining` 收口为 `0`
- `Background pool.latest_parked` 改写为本轮结论
- `cycle_plan` 第 1 项写成 `done`

## 一句话结果（用于 state/result）
`Rank 247 / VPIN-driven jump-sign continuation` 的唯一 survivor follow-up 已收口：在固定 `BTCUSDT` 公共 `aggTrades`、`high-VPIN(top10% toxicity proxy) × same-sign 1m jump × next-bar open × no-overlap` 口径下，`1/3/5 bars` gross continuation 分别约 `-0.71 / -0.19 / -0.39 bps`、`68` 个事件全部过不了 `3/5/8 bps` 成本线，也没有形成强于普通 jump-followthrough 的独立 pocket，因此不升 `P2`，回 `background/P0`。

## 产物
- `reports/artifacts/rank247_survivor_followup_20260330/minute_panel.csv`
- `reports/artifacts/rank247_survivor_followup_20260330/event_panel.csv`
- `reports/artifacts/rank247_survivor_followup_20260330/summary.csv`
- `reports/artifacts/rank247_survivor_followup_20260330/control_groups.csv`
- `reports/artifacts/rank247_survivor_followup_20260330/summary.json`
