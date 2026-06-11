# 2026-04-06 08:20 UTC — bot2 strategy review

本轮严格按 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md` 做 40 分钟 desk review；只更新 runtime state，不改 policy / brief / operating card / cron prompt。

## 先回答 4 个问题

1. **`Paper launch queue` 是否非空？**
   - 否。
   - 当前 `Paper launch queue.current_target = none`。
   - 已连到运行态的只有 `connected_runner_live` 列表（含 `Rank 342`），没有新的待接线 `P3` 头对象。

2. **本轮 `fresh intake` 是什么？**
   - 当前 head fresh intake 仍是：
   - `research/quant_digests/2026-04-06_0558_btc-lead-liquidity-lag-alt-alpha.md`
   - 理由：上一轮 survivor 已经诚实收口，本轮回到 fresh intake 时，现有 runtime 里最前的具体 pending intake 仍是这条 `BTC lead × low-liquidity alt lag`。

3. **上一条 fresh intake 是否值得那唯一一次 follow-up？**
   - 是，而且这次 follow-up 已经用完并收口。
   - 上一条 fresh intake 是 `Rank 349 / funding-basis dislocation persistence × delta-neutral carry`。
   - `research/optimization_loop/2026-04-06_0731_rank349_funding_basis_dislocation_persistence_delta_neutral_carry_first_verdict_keep_p1.md` 给了它 `keep_P1`，因为其主语确实区别于 `Rank 348`。
   - 但 `research/optimization_loop/2026-04-06_0812_rank349_survivor_followup_funding_basis_persistence_background_p0.md` 已明确：唯一 survivor follow-up 没能把它压成 `BTC/ETH/SOL × 5m/15m × explicit after-cost` 下相对 `level-only carry` 的可迁移净增量，因此对象不升 `P2`，已退回 `background / P0`。

4. **当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？**
   - 当前不存在明确 `Active P2`。
   - 最近的 `Active P2` 是 `Rank 342`，它已经完成 `P2 -> P3`，并进一步完成 runner / scheduler / 首跑验证，当前既不留在 `Active P2`，也不留在 `Paper launch queue`。

## Rank / 前排合法性检查

- 当前前排对象：
  - `Paper launch queue = none`
  - `Surviving candidate = none`
  - `Active P2 = none`
  - `Fresh intake head = research/quant_digests/2026-04-06_0558_btc-lead-liquidity-lag-alt-alpha.md`
- 前排不存在 `keep_P1 / P2 / P3` 但无正式 rank 的对象。
- 本轮**无需补 rank**。

## 排班判断

按 policy 的 authoritative 顺序扫描：

1. **P3 handoff**：无待接线对象。
2. **P2 admission / promote / park**：`Active P2 = none`。
3. **P1 survivor follow-up**：`Rank 349` 已在 08:12 UTC 用尽唯一 follow-up 并退回 background，本轮无 survivor 待收口。
4. **fresh intake**：因此本轮预算全部切回具体 fresh intake，而且必须写成明确对象，不能写成抽象模板。

据此，本轮 `cycle_plan` 重写为 4 条具体 intake：

1. `2026-04-06_0558_btc-lead-liquidity-lag-alt-alpha.md`
2. `2026-04-06_0754_rf-threshold-bucket-hf-pairs-alpha.md`
3. `2026-04-06_0718_coint-shell-signbug-costcliff.md`
4. `2026-04-06_0645_abnormal-volume-disagreement-xs-fade-alpha.md`

顺序含义：
- 第 1 项保留当前 runtime 里已经挂起的 fresh-intake head，不跳过已有 pending head 去追更新文件；
- 其余位置按最近新 repo / paper / alpha report 补具体对象；
- 本轮没有任何需要 bot2 兜底直接推 `P3` 的 `Active P2`，因此不会伪造开放式研究或假 handoff。

## 对 `BOT2_BOT3_STATE.md` 的具体改写

- 保持：
  - `Paper launch queue.current_target = none`
  - `Surviving candidate.current_target = none`
  - `Active P2.current_target = none`
- 重写 `cycle_plan` 为纯 fresh-intake 队列：
  1. `BTC lead × low-liquidity alt lag`
  2. `RF threshold bucket × HF pairs`
  3. `cointegration spread MR × verify-and-retry shell`
  4. `abnormal-volume disagreement × constrained-bucket fade`
- 新计划项全部写成：`result = none`、`status = pending`。

## 执行补记

- `docs/BOT2_BOT3_STATE.md` 已按本轮 review 写回。
- 本地首页索引源码 `reports/site/index.html` 已重建刷新（mtime `2026-04-06 08:24 UTC`）。
- `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` 的最终 `/var/www` 安装步骤仍受脚本内 `sudo` 约束；当前 cron runtime 无 `elevated` 能力，因此外层发布脚本未能完整落到系统目标路径，但 reader-facing 源文件已刷新。
- 中文邮件摘要已发送到默认收件人。

## 一句话结论

本轮前排已经诚实收口：`P3` 为空、`Active P2` 为空、`Rank 349` survivor 已结束且回到 background；因此当前正确排班不是继续拖旧对象，而是把 bot3 预算完整切回 4 条具体 `fresh intake`，并保持 head 仍从 `BTC lead × low-liquidity alt lag` 开始。
