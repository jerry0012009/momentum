# 2026-03-17 14:06 UTC · Rank 2 next status-change gate

## 本轮主点
- 在 `EMA = waiting_not_due` 且当前 active Scout 候选都没有更高边际的 genuinely verdict-changing 动作时，本轮按 `Run 3` 执行，但**不再继续补 Rank 2 的近义 launch/closeout copy**。
- 主交付改为：把 `Rank 2` 这条线的“文档链止损闸门”写成公开 artifact，明确 **接下来什么动作才会真的改状态，什么动作不再算进展**。

## 认领依据（先比较 active Scout / P3）
- `Paper Seat / EMA`：最新 due guardrail 仍是 `waiting_not_due`；当前没有 `due-now / overdue` lane。
- `Scout Seat`：
  - `Rank 17`：已到 `narrow paper pilot approved`，当前默认只允许真实 append/review 或 genuinely verdict-changing 最小检查；本轮没有新的 append/review need。
  - `Rank 29`：已到 `P3 monitoring / weekly-review red-watch`；本轮没有新的 append/review need。
  - `Rank 2`：最近连续多轮主要新增的是 `launch packet / starter row / closeout copy`，已触发“不要继续磨同一条线的 admission write-back / operator packet / closeout docs”的 desk 规则。
- 结论：本轮继续服务 desk 主线，但不是再补一个相邻模板，而是把 **Rank 2 doc-chain 到此为止** 公开写死，逼后续默认只在 `真实 replay` 与 `切回 fresh Scout intake` 之间选择。

## 本轮产物
### 1) 新 artifact
- `reports/artifacts/alpha_closure_board/small_live_rank2_next_status_change_gate_v1.csv`

两条 hard gate：
1. **当前唯一会改变状态的动作**
   - 只有同一条 whitelist-bound `test/no-fill` replay 的真实 `intent / ack / cancel(close)` refs，才算 status change；
   - 没有真实 refs，`Rank 2` 仍停在 `paper_candidate_only / blocked -> dry_run_only`。
2. **为什么默认不再继续补 doc-chain**
   - `launch packet` 与 `starter rows` 已经把 replay 成功后的第一条 `shadow_parity green row` 最小字段压成可照抄模板；
   - 再写更多 `launch packet / starter row / wording / closeout copy`，不会再减少真实 blocker。

### 2) reader-facing 页面同步
- `reports/site/factors/alpha_closure_board/report.html`
  - 新增 `Rank 2 next status-changing gate（v1）` 区块；
  - 公开写死：**继续补 Rank 2 相邻 packet / starter / wording，默认已不再减少 blocker；真正会改状态的只剩一次真实 whitelist-bound replay。**

### 3) desk board 同步
- `docs/TODO.md`
  - 在 `Next 3 bot3 runs` 顶部 authoritative override 中新增 14:06 UTC 补充：
    - `small_live_rank2_next_status_change_gate_v1` 已落地；
    - 后续若没有真实 replay receipt refs，默认不要再把 `Run 3` 主资源继续花在 Rank 2 近义 closeout copy；
    - 更诚实的下一步要么是真 replay，要么切回新的 `paper / repo based 5m / 15m crypto` Scout intake。

## 验证
1. `python3 -m py_compile /root/clawd/jerry/momentum/scripts/build_alpha_closure_board_report.py`
2. `python3 /root/clawd/jerry/momentum/scripts/build_alpha_closure_board_report.py`
3. `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`

## 错误 / 回退
- 首次生成时出现 `NameError: rank2_next_status_change_gate_rows is not defined`。
- 原因：已在 `main()` 写入新 artifact，但漏加 `rank2_next_status_change_gate_rows = get_rank2_next_status_change_gate_rows()`。
- 修复：补上变量初始化后重跑；二次生成成功，首页已发布。

## 当前 hard verdict
- `Rank 2` 当前最诚实的状态没有变化：仍是 **`narrow paper candidate, paper_candidate_only / blocked`**。
- 本轮真正新增的不是 another packet，而是一个公开 stop-loss gate：
  - **没有真实 whitelist-bound replay refs，就不再把相邻文档当成“继续推进”。**
- 因此后续默认顺序应更收敛：
  1. 有 operator 真 replay / 真 refs 回填时，再继续 `Rank 2`；
  2. 否则 `EMA waiting_not_due` 阶段，应优先切回新的 `paper / repo based 5m / 15m crypto` Scout intake，而不是继续磨 Rank 2 文档链。

## 相关文件
- `scripts/build_alpha_closure_board_report.py`
- `docs/TODO.md`
- `reports/artifacts/alpha_closure_board/small_live_rank2_next_status_change_gate_v1.csv`
- `reports/site/factors/alpha_closure_board/report.html`
- `reports/site/index.html`
