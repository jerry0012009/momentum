# 2026-04-08 19:31 UTC strategy review

## Scope
按 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md` 执行本轮 40 分钟 desk review；本轮只核对 runtime truth、前排合法性与默认排班顺序，并只更新 `BOT2_BOT3_STATE.md`。

## 先回答 4 个问题

### 1) `Paper launch queue` 是否非空？
**否。**

- `Paper launch queue.current_target = none`
- `Rank 200 / 201 / 213 / 229 / 342` 均已写在 `connected_runner_live`
- 当前没有“已进 P3 但 dedicated runner / scheduler / first run 还没接完”的对象

### 2) 本轮 `fresh intake` 是什么？
**是 `research/quant_digests/2026-04-08_1828_toxicflow-jump-continuation-alpha.md`。**

原因：
- `P3` 空
- `Active P2` 空
- survivor 空
- `research/optimization_loop/2026-04-08_1926_normalized_cluster_deviation_fresh_intake_background.md` 已把上一条前排 fresh intake `2026-04-08_1358_normalized-cluster-deviation-snapback-alpha.md` 诚实收口为 `background / P0`
- 因此前排 fresh intake 自然顺延到下一条尚未执行的 `2026-04-08_1828_toxicflow-jump-continuation-alpha.md`

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
**不值得。**

- 上一条 fresh intake 是 `research/quant_digests/2026-04-08_1358_normalized-cluster-deviation-snapback-alpha.md`
- `research/optimization_loop/2026-04-08_1926_normalized_cluster_deviation_fresh_intake_background.md` 已明确：它的新增价值主要是既有 `cluster deviation / cluster-neutral stat-arb` family 的实现层收紧
- 当前没有证据表明它形成了独立于既有 cluster-relative MR 家族的新 queue-facing raw alpha 主语
- 因此 first verdict 已诚实收口为 `background / P0`，不应再占用 survivor 那唯一一次 follow-up

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**不存在。**

- `Active P2 slot.current_target = none`
- 最近明确的 `P2` 出口仍是 `Rank 342`，但它已完成 `P2 -> P3 -> connected_runner_live`
- 当前没有需要 bot2 兜底直升 `P3` 的漏升 `Active P2`

## 最近读取与证据核对
1. `docs/BOT2_BOT3_POLICY.md`
2. `docs/BOT2_BOT3_STATE.md`
3. repo 状态
   - 工作区存在大量历史未跟踪文件；本轮只把它视作 repo hygiene 事实，不据此 reopen background pool，也不据此倒推改 policy
4. 最近 `research/optimization_loop/`
   - `2026-04-08_1926_normalized_cluster_deviation_fresh_intake_background.md`
   - `2026-04-08_1913_dynamic_hedgeratio_btceth_fresh_intake_background.md`
   - `2026-04-08_1844_crosscrypto_seesaw_lasso_fresh_intake_background.md`
   - `2026-04-08_1832_dynamic_formation_coint_pairs_fresh_intake_background.md`
   - `2026-04-08_1733_icranked_coint_pairs_fresh_intake_background.md`
5. 最近 `research/strategy_review/`
   - `2026-04-08_1919_strategy-review.md`
   - `2026-04-08_1812_strategy-review.md`
6. 最近待判 / 新 digest
   - `2026-04-08_1828_toxicflow-jump-continuation-alpha.md`
   - `2026-04-08_1900_thresholded-oversold-rebound-alpha.md`
   - `2026-04-08_1729_asymmetric-shock-horizon-router-alpha.md`
   - `2026-04-08_1331_sameclock-xs-session-router-alpha.md`

## Rank / 前排合法性检查
- `Paper launch queue.current_target = none`，合法
- `Surviving candidate slot.current_target = none`，合法
- `Active P2 slot.current_target = none`，合法
- 当前前排不存在达到 `keep_P1 / P2 / P3` 但无正式 rank 的对象，因此本轮无需补 rank

## 排班判断
按 policy 默认顺序：
`P3 handoff > P2 admission/promote/park > P1 唯一一次诚实检查 > fresh intake > P0`

本轮扫描结果：
- `P3`：无待接线对象
- `P2`：无在场 `Active P2`
- `P1`：无在场 survivor
- 因此前三层都没有真实可执行动作，本轮应继续停留在具体 `fresh intake`
- 且按 policy，切回 fresh 时必须优先收掉当前已在前排且尚未执行的对象，再用剩余预算补更近的新 digest

因此当前最诚实的 `cycle_plan` 应改为：
1. `research/quant_digests/2026-04-08_1828_toxicflow-jump-continuation-alpha.md`
2. `research/quant_digests/2026-04-08_1900_thresholded-oversold-rebound-alpha.md`
3. `research/quant_digests/2026-04-08_1729_asymmetric-shock-horizon-router-alpha.md`
4. `research/quant_digests/2026-04-08_1331_sameclock-xs-session-router-alpha.md`

## 为什么本轮不需要 bot2 兜底升 P3
policy 只要求 bot2 在 desk review 已清楚看到某个**在场 `Active P2`** 已达到 paper trade / paper launch 门槛，而 bot3 尚未升级时，直接把对象推进到 `P3 / Paper launch queue` 或 handoff。

本轮不满足该条件：
- `Active P2 = none`
- 当前前排动作全部是 fresh intake first verdict
- 最近升级到 `P3` 的 `Rank 342` 已完成最小接线并写入 `connected_runner_live`

因此，本轮不存在需要 bot2 兜底强推到 `P3` 的对象。

## Runtime writeback
本轮已重写 `docs/BOT2_BOT3_STATE.md`，但只做 runtime 层收口：
- `Fresh intake slot` 保持 `pending`，当前对象明确为 `2026-04-08_1828_toxicflow-jump-continuation-alpha.md`
- 保留上一条 fresh intake `1358 normalized cluster deviation` 的 `background / P0` 结论作为 latest result
- 重写 `cycle_plan` 为 4 条具体 pending fresh intake，顺序为：`1828 -> 1900 -> 1729 -> 1331`
- 不改 policy / brief / operating card / auto loop / cron prompt
- 不 reopen background pool
- 不新增 rank

## 一句话总结
这轮仍然没有待接线 `P3`、没有 `Active P2`、也没有 survivor；上一条 fresh intake `1358 normalized cluster deviation` 已诚实收口为 `background / P0`，所以前排应顺延到 `1828 toxic-flow jump`，并在剩余预算里按新近度与具体性继续排 `1900 thresholded oversold rebound`、`1729 shock-sign router`、`1331 same-clock session router`。