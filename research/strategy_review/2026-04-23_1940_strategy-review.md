# 2026-04-23 19:40 UTC strategy review（bot2，40m desk review）

Cron: `[cron:a3e89b2e-958f-4ad3-b625-c280a257b68a bot2-strategy-review-40m]`

## Inputs checked
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`
- `git status --short`
- recent `research/optimization_loop/`
- recent `research/strategy_review/`
- recent `research/quant_digests/`

## repo / recent evidence summary
- 工作树仍然很脏，但本轮继续遵守硬约束：**只更新 `docs/BOT2_BOT3_STATE.md`**，并新增本条 `strategy_review` 日志。
- 最近 optimization front 的最新真实收口顺序已经很清楚：
  - `2026-04-23_1816_dffnn_5lag_btc_forecast_freshintake_background_p0.md`
  - `2026-04-23_1832_crossvenue_fundingspread_duration_freshintake_background_p0.md`
  - `2026-04-23_1926_prepump_anomaly_composite_freshintake_background_p0.md`
  - `2026-04-23_1938_rs_semivariance_cycleplan_sync_done.md`
- 这说明上一版 `cycle_plan` 里的三条 fresh intake 已经全部被消费：`1806`、`1710` 已 first verdict 收口 `background/P0`，`2310` 也已做 runtime sync done；当前仍然没有任何 `P3/P2/P1` 前排收口动作。
- 最新未见 optimization 消费的正式 digest 里，当前最应该顶到 fresh intake 前排的是：
  1. `research/quant_digests/2026-04-23_1910_triangular-arb-fee-capacity-reality-check.md`
  2. `research/quant_digests/2026-04-23_0942_polymarket-funding-confirmed-skewfade-alpha.md`
  3. `research/quant_digests/2026-04-23_0901_btc-intraday-session-momentum-alpha.md`
  4. `research/quant_digests/2026-04-23_1053_xvenue-median-outlier-reversion-alpha.md`
- `Paper launch queue` 仍然非空，但只有 `connected_runner_live` 列表非空；`current_target = none`，没有待 bot3 继续做 launch wiring 的 pending `P3`。

## 只回答 4 个问题
1. **`Paper launch queue` 是否非空？**
   - **是，非空。**
   - 但非空部分只体现在 `connected_runner_live` 列表；`current_target = none`，没有需要继续补 `runner + scheduler + first verified run` 的 pending `P3` 对象。

2. **本轮 `fresh intake` 是什么？**
   - **`research/quant_digests/2026-04-23_1910_triangular-arb-fee-capacity-reality-check.md`。**
   - 原因：最近三条已排到前面的 intake（`1806 / 1710 / 2310`）都已被消费并收口/同步完成；在 `P3/P2/P1` 全空的情况下，按 policy 对“最近新的 repo/paper/alpha report”优先，当前 fresh intake 前排应切到最新未消费的 `1910 / triangular arb fee-capacity reality check`。

3. **上一条 fresh intake 是否值得那唯一一次 follow-up？**
   - **不值得。**
   - 上一条真正完成 first verdict 的 fresh intake 是 `research/quant_digests/2026-04-23_1710_prepump-anomaly-composite-alpha.md`。
   - 它已在 `research/optimization_loop/2026-04-23_1926_prepump_anomaly_composite_freshintake_background_p0.md` 诚实收口 `background/P0`：after-cost 余量高度集中在少数币与少数挤仓日，`BTC/ETH` 两个最大出现主语未保住同向正边际，因此不配 survivor 的唯一 follow-up。

4. **当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？**
   - **当前不存在明确 `Active P2`。**
   - 最近明确的 `Active P2` 仍是 `Rank 434 / newlisting early-short bubble fade`，但它已由 bot2 兜底推进 `P3`，且 launch wiring 已完成并写入 `connected_runner_live`；当前没有需要继续做 `P3 / P1 / P0` 出口裁决的 `P2` 对象。

## Rank / legality check
- `Paper launch queue.current_target = none`
- `Surviving candidate slot.current_target = none`
- `Active P2 slot.current_target = none`
- 当前前排不存在无 rank 的 `keep_P1 / P2 / P3` 对象，因此本轮**无需补新的整数 Rank**。
- 也未发现 background pool 被自动拉回前排的违规情况。

## cycle_plan 重写结论
按 policy 默认排班顺序扫描后：
- `P3 launch wiring`：无 pending 对象；
- `P2 admission / exit`：无 `Active P2`；
- `P1 唯一 follow-up`：无 survivor，且上一条 fresh intake 已正式收口 `background/P0`；
- 因此前排预算诚实切回 `fresh intake`。

本轮把 `cycle_plan` 重写为 4 条具体 fresh intake：
1. `research/quant_digests/2026-04-23_1910_triangular-arb-fee-capacity-reality-check.md`
2. `research/quant_digests/2026-04-23_0942_polymarket-funding-confirmed-skewfade-alpha.md`
3. `research/quant_digests/2026-04-23_0901_btc-intraday-session-momentum-alpha.md`
4. `research/quant_digests/2026-04-23_1053_xvenue-median-outlier-reversion-alpha.md`

## 为什么这样排
- `#1 1910 / triangular arb fee-capacity reality check`：最新、未消费、distinctness 高，适合放在当前 fresh intake 第一位。
- `#2 0942 / polymarket funding-confirmed skew fade`：仍是今天的新 digest，且属于 prediction-market × funding 确认的独立题材，不应被更老的同类对象替代。
- `#3 0901 / BTC intraday session momentum`：虽然同属 intraday momentum 家族，但截至本轮仍未见 optimization first verdict，且论文口径与前几条 funding/cross-venue 线 distinct enough。
- `#4 1053 / xvenue median outlier reversion`：同样是今天的新 digest，且与 `1910` 的三角套利不同，它更偏 cross-venue outlier close / reversion，值得作为剩余预算补位。
- 不再把 `1806 / 1710 / 2310` 留在 pending：它们已经分别被 `1832 / 1926 / 1938` 消费或同步完成，再继续挂前排只会造成 stale runtime。

## 已写回 `BOT2_BOT3_STATE.md` 的要点
- `Fresh intake slot.current_target` 改为 `research/quant_digests/2026-04-23_1910_triangular-arb-fee-capacity-reality-check.md`
- `Fresh intake slot.source_record` 同步改为 `1910`
- `Fresh intake slot.latest_result` / `latest_result_record` 保持最近完成的 `1710 -> background/P0`
- `cycle_plan` 重写为 `1910 / 0942 / 0901 / 1053` 四条具体 pending 动作
- `Paper launch queue` / `Surviving candidate` / `Active P2` 无层级改动

## 尾部执行约束
- homepage 刷新与中文邮件摘要必须作为两个独立命令执行。
- 若 homepage 刷新失败，只记为非阻断尾部失败，不回滚本轮 review / state rewrite / log。
- 若邮件发送失败，只记为通知失败，不回滚本轮 review / state rewrite / log。
