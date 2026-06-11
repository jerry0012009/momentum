# 2026-04-07 08:11 UTC strategy review

## Scope
按 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md` 做本轮 40 分钟 desk review；只更新 runtime state，不改 policy / brief / operating card / auto loop / cron prompt。

## 先回答 4 个问题

### 1) `Paper launch queue` 是否非空？
**否。**

当前 `Paper launch queue.current_target = none`。`Rank 200 / 201 / 213 / 229 / 342` 都已写入 `connected_runner_live`，表示这些对象已经完成最小 `P3 launch wiring`，不是当前待接线对象；因此本轮没有需要排在最前的 `P3 handoff` 动作。

### 2) 本轮 `fresh intake` 是什么？
**`research/quant_digests/2026-04-07_0720_ctrend-multihorizon-xs-alpha.md`。**

原因很直接：当前 `P3 / Active P2 / Surviving candidate` 三个前排槽位都为空，而 `2026-04-07 07:20` 的 `CTREND × cross-sectional continuation` 是最近新增、且尚未在 `optimization_loop` 中形成 first verdict 的具体对象；按 policy，前排收口后应切回最近的新 repo / paper / alpha 报告，因此它应成为本轮首条 fresh intake。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
**不值得。**

上一条 fresh intake 是 `research/quant_digests/2026-04-07_0551_basis-funding-gap-convergence-alpha.md`。它已在 `research/optimization_loop/2026-04-07_0726_basis_funding_gap_intake_background_p0_old_carry_basis_family.md` 收口为 `background / P0`：
- 核心主语仍是旧 `delivery/perp carry gap mean reversion` 家族；
- `half-life / Hurst` 更像 admission overlay，不是新 alpha 本体；
- 样本只有 `7` 笔 round-trip，不足以证明它解决了既有 funding / basis family 的决定性 blocker。

既然首判已经是 `background / P0`，那它就不占 survivor，也不值得那唯一一次 follow-up。

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**不存在。**

`Active P2 slot.current_target = none`。最近一条明确 `Active P2` 是 `Rank 342`，它已经在 `research/optimization_loop/2026-04-05_2300_rank342_p2_exit_promote_p3_lowgas_samechain_paper_queue.md` 完成 `P2 -> P3`，随后在 `research/optimization_loop/2026-04-06_0016_rank342_p3_launch_wiring_connected_runner_live.md` 完成最小接线并写回 `connected_runner_live`。因此本轮不存在 bot2 需要兜底裁决的漏升 `P2`。

## Rank / 前排合法性检查
- `Paper launch queue.current_target = none`，合法。
- `Surviving candidate slot.current_target = none`，合法。
- `Active P2 slot.current_target = none`，合法。
- 当前前排没有任何达到 `keep_P1 / P2 / P3` 但缺少正式 `Rank` 的对象，因此本轮无需补 rank。

## 最近证据与排班判断
本轮真正改变排班的近端证据有三条：
1. `research/optimization_loop/2026-04-07_0726_basis_funding_gap_intake_background_p0_old_carry_basis_family.md`
   - 证明上一条 fresh intake 已经直接收口到 `P0`，不进 survivor。
2. `research/quant_digests/2026-04-07_0640_persistent-imbalance-signedflow-continuation-alpha.md`
   - 这是 06:40 新增、尚未做 first verdict 的 microstructure 候选。
3. `research/quant_digests/2026-04-07_0720_ctrend-multihorizon-xs-alpha.md`
   - 这是 07:20 新增、尚未做 first verdict 的横截面 composite 候选。

因此当前前排链条已经完全清空，不存在 `P3 / P2 / P1` 真实动作需要优先于新 intake。本轮应该诚实切回 fresh intake，而且应优先排最近两条新增对象，而不是继续沿用更早的 05:30 / 03:33 / 02:41 顺序。

## 本轮 runtime 调整
本轮仅重写 `docs/BOT2_BOT3_STATE.md` 的 `cycle_plan`，新的当前轮顺序为：
1. `2026-04-07_0720_ctrend-multihorizon-xs-alpha.md`
2. `2026-04-07_0640_persistent-imbalance-signedflow-continuation-alpha.md`
3. `2026-04-07_0530_bestbid-bestask-calendar-netting-alpha.md`
4. `2026-04-07_0333_crashtrim-volmanaged-xs-momentum-alpha.md`

这样排的原因：
- 当前没有任何 `P3 handoff / Active P2 / Surviving candidate` 需要抢占前排；
- `0720` 与 `0640` 是最近且尚未进入 `optimization_loop` 的具体对象，理应先 intake；
- `0530` 仍然保留在当前轮预算里，因为它仍是明确、可执行的 RV 新对象；
- `0333` 作为第四条保留，继续填满本轮预算；
- `0241` 不是被否决，而是因为本轮预算有限、且它的时间优先级已经落后于 07:20 / 06:40 / 05:30 三条更近的新对象。

## 为什么这轮不需要 bot2 兜底升 P3
本轮没有任何 `Active P2` 留在前排，更不存在“desk review 已清楚表明已经值得进 paper trade、但 bot3 尚未升级”的对象。
- `Rank 342` 的 `P2 -> P3 -> connected_runner_live` 已经完成；
- `Rank 354` 已在 survivor 唯一 follow-up 后退出前排；
- `basis-funding gap` 已被判定为 `background / P0`。

所以这轮 bot2 的诚实职责不是强推 `P3`，而是把空前排后的 fresh intake 顺序改对。

## 一句话总结
当前运行态已经从 `basis-funding gap` 这条 fresh intake 的 `P0` 收口回到空前排；因此 bot3 下一轮应直接从最新两条 fresh intake（`CTREND multi-horizon XS`、`persistent imbalance × signed-flow`）开始，而不是继续把更早的 intake 排在更前面。

## Delivery notes
- `docs/BOT2_BOT3_STATE.md` 已按本轮结论重写 `cycle_plan`。
- 中文邮件已通过 `send_text_email.py` 发送到默认收件人。
- 已执行 `publish_homepage_index.sh` 的刷新尝试，但当前 cron 运行态无可用 elevated 权限；脚本会卡在 `sudo mkdir/install/chown` 阶段，因此本轮首页未能确认真正同步到 `/var/www/momentum-report/index.html`。
