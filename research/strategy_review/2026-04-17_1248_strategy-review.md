# 2026-04-17 12:48 UTC bot2 strategy review

## Inputs checked
- Policy: `docs/BOT2_BOT3_POLICY.md`
- State: `docs/BOT2_BOT3_STATE.md`
- Repo status: `git status --short`（工作树仍主要是历史遗留未跟踪临时文件；本轮不把这些噪音当成调度依据）
- Recent optimization loop: `2026-04-17_1245_cycle_plan_no_pending_guard.md`（确认当前旧 `cycle_plan` 已无合法 `pending`，只剩 stale blocked residue）
- Recent strategy review: `2026-04-17_0355_strategy-review.md`
- Recent fresh source candidates: `research/quant_digests/2026-04-17_0439_regimeaware-xsmomentum-btcvol-overlay.md`、`research/quant_digests/2026-04-17_0920_depthimbalance-maker-skew-mm-shell.md`

## 四个问题（本轮结论）
1. `Paper launch queue` 是否非空？
   - 结论：**否**。
   - `current_target = none`；`connected_runner_live` 虽非空，但这些对象都已完成 runner + scheduler + first verified run，不属于待接线 queue。

2. 本轮 `fresh intake` 是什么？
   - 结论：`research/quant_digests/2026-04-17_0920_depthimbalance-maker-skew-mm-shell.md`
   - 理由：上一条 runtime fresh intake（`APR-ranked funding carry with spread-cap allocation shell`）已在 `2026-04-16_1954_item1_fundingdesign_residual_freshintake_background_p0.md` 收口 `background/P0`；此后最近新增 repo/paper alpha 报告里，最新且最具体的 intake 对象是 2026-04-17 09:20 的 `OBI → fair-value 偏移 → maker quote skew shell`。

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
   - 结论：**不值得**。
   - 这里的“上一条 fresh intake”仍指 runtime 已闭环的 `APR-ranked funding carry with spread-cap allocation shell`：它本身已在统一 after-cost 与 delayed-confirmation 口径下直接首判 `background/P0`，不存在 survivor 资格，更不值得补唯一一次 follow-up。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
   - 结论：**不存在**。
   - `Active P2 = none`；最近一次 P2 出口是 `Rank 417`，但它已在 `2026-04-16_0309_rank417_p2_exit_rescope_to_p1_noeth_pairs.md` 执行完 one-time `P2->P1 re-scope` 并退出 active 槽位，不构成本轮待判对象。

## Rank 合规检查
- 当前前排对象（`Paper launch queue / Surviving candidate / Active P2`）均无“已到 `keep_P1 / P2 / P3` 但无正式 rank”的违规。
- 本轮无需补发新 Rank。

## 排班判断
- 当前没有待接线 `P3`、没有 `Active P2`、也没有 survivor 锁定权对象。
- 旧 `cycle_plan` 已全部变成 stale blocked residue；继续保留会让 bot3 只能反复触发 no-pending guard，因此必须重写。
- 按 policy 默认顺序，本轮应直接切回 fresh intake，并优先填入最近新增、具体且未执行过 first-verdict 的对象：
  1. `2026-04-17_0920_depthimbalance-maker-skew-mm-shell.md`
  2. `2026-04-17_0439_regimeaware-xsmomentum-btcvol-overlay.md`
  3. 若前两项未形成新的 survivor / P2，再回到 `derived_hypothesis_drafted`：`Rank 60`
  4. 再补 `Rank 27`
- 本轮不把 `Rank 57` 继续排在前四里：它本身不如 `Rank 60 / Rank 27` 更前，而且当前已有两条更新鲜、未判过的 repo alpha intake，应先吃新料。

## State rewrite（本轮执行）
- `Fresh intake slot` 改写为：
  - `status = open_pending_first_verdict`
  - `current_target = research/quant_digests/2026-04-17_0920_depthimbalance-maker-skew-mm-shell.md`
  - `source_record` 同步切到上述 09:20 digest
- `cycle_plan` 按合法优先级重写为 4 项，且全部恢复为真实 `pending`：
  1. `depthimbalance-maker-skew-mm-shell`（fresh intake first-verdict）
  2. `regimeaware-xsmomentum-btcvol-overlay`（fresh intake first-verdict）
  3. `Rank 60 derived_hypothesis_drafted`（conditional fresh intake）
  4. `Rank 27 derived_hypothesis_drafted`（conditional fresh intake）

## P2->P3 兜底裁判检查
- 本轮无 `Active P2`，也无 desk review 已清楚表明“足够值得 paper trade / paper launch 但 bot3 尚未升级”的对象。
- 因此本轮无需把任何对象强制写入 `P3 / Paper launch queue` 或 handoff 路径。
