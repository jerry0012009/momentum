# 2026-03-16 16:58 UTC — Rank2 receipt log template

## 本轮定位
- 席位判断：`EMA` 仍处于 `waiting_not_due`，因此本轮继续遵守 desk 顺序，不在 Paper Seat 等待窗口里空转。
- 认领主点：`Run 3 / tiny-live plumbing`。
- 紧邻子点：沿上一轮的 `Rank 2 whitelist-bound receipt chain operator packet`，把真实 replay 发生后的 **审计回写模板** 先冻结下来。
- 本轮仍只服务 `Rank 2 combo_all` 这一条窄范围 `paper candidate`，没有新开候选。

## 为什么选这个
上一轮已经把当前唯一允许动作压成了：
- `BTC/ETH/SOL whitelist`
- `test/no-fill`
- `intent -> ack -> cancel/close receipt chain`

但如果真实 replay 发生时，没有预先定死回写字段，后续很容易又退回到“口头说补过了 receipt chain”，而不是留下可审计的证据行。

因此这轮最小但有用的推进，不是再解释 Rank 2 是不是 `paper candidate`，而是把 **receipt chain 落地时必须怎么写回** 提前压成模板。

## 本轮改动
### 1) 新增 artifact
新增：
- `reports/artifacts/alpha_closure_board/small_live_rank2_receipt_chain_log_template_v1.csv`

内容特点：
- 为 `BTC / ETH / SOL` 三条 whitelist leg 各生成一条模板行；
- 预留并强制要求：
  - `intent_ref`
  - `ack_ref`
  - `cancel_or_close_ref`
- 默认 `chain_status=pending_real_replay`；
- 明确 `scope_check=must_match_packet_scope`、`capital_check=must_remain_0`；
- 直接复用上一轮 operator packet 的：
  - `writeback_on_success`
  - `writeback_on_fail`
  - `required_refs_bundle`
  - `current_blockers`
- 让后续真实 replay 发生后，可以把“有没有完整 receipt chain”落成 concrete row，而不是靠说明文字代替。

### 2) 网页可见落点
已更新：
- `reports/site/reading/trendline_alpha_scout/report.html`

新增 reader-facing 卡片：
- `Run 3 receipt log template（Rank 2 test/no-fill audit row）`

这张卡的定位很克制：
- 不是放行；
- 不是宣称 receipt chain 已发生；
- 只是把“真实 replay 发生后必须留下哪三段 ref、缺哪段就继续 blocked”写成固定审计模板。

### 3) 代码改动
只做了与本轮直接相关的最小修改：
- `scripts/build_trendline_alpha_scout_report.py`

新增逻辑：
- 从现有 `small_live_rank2_receipt_chain_operator_packet_v1.csv` 与 `small_live_rank2_status_snapshot_v1.csv` 生成 `small_live_rank2_receipt_chain_log_template_v1.csv`；
- 在 `trendline_alpha_scout` 页面增加对应卡片。

## 最小验证
已完成：
- `python3 -m py_compile scripts/build_trendline_alpha_scout_report.py`
- `python3 scripts/build_trendline_alpha_scout_report.py`
- 校验新 artifact：
  - 共 `3` 行（`BTC/ETH/SOL`）
  - 字段已包含 `intent_ref / ack_ref / cancel_or_close_ref / chain_status`
- grep 校验网页：
  - `Run 3 receipt log template（Rank 2 test/no-fill audit row）` 已出现在 `reports/site/reading/trendline_alpha_scout/report.html`

## 硬结论
- `Rank 2 combo_all` 的席位判断 **没有变化**：
  - 仍是窄范围 `paper candidate`；
  - 仍停在 `paper_candidate_only / blocked`；
  - 仍不得偷进 `shadow_parity / tiny-live`。
- 本轮新增的是一个 **paper/live plumbing artifact**：
  - 它把 receipt chain 的 writeback 方式定死；
  - 但它本身不是 receipt chain，也不是放行票。
- 从现在起，后续若真做 whitelist-bound `test/no-fill replay`，应优先直接填写这张模板，而不是再临时设计字段。

## 风险 / 边界
1. 这仍然只是模板，不是来自真实 venue 的回执；因此不能把它当作“已补齐 receipt chain”的证据。
2. 模板当前绑定的是现有 `Rank 2` scope 与 `BTC/ETH/SOL whitelist`；若候选 scope 变动，必须先重生 operator packet，再改模板。
3. 当前 blocker 仍然存在：`idle_gap_watch`、`time_pocket_review`、`route_receipt_chain_missing`、`promotion_boundary=paper_candidate_only`。

## 下一步建议
1. 若后续外部条件允许，优先在 `BTC/ETH/SOL` 中选一条 whitelist leg 做一次真实 `test/no-fill intent -> ack -> cancel/close` replay，并直接回写到这张模板；
2. 若仍没有真实 replay 条件，则继续诚实保持 `paper_candidate_only / blocked`，不要把模板误写成放行；
3. 若 `EMA` 仍在 `waiting_not_due` 且 `Rank 2` 也没有真实执行窗口，再按 desk 规则看是否有新的 scout 快筛动作可认领。

## Commit hash
- 未提交。
- 原因：当前 git 工作区存在大量与本轮无关的历史脏文件，本轮只做局部可审计改动，避免混提。
