# 2026-03-16 17:28 UTC｜Run 3：Rank 2 closeout snapshot sync to alpha closure board

## 为什么这次选这个
按 `docs/TODO.md` 顶部 `TRADING DESK BOARD`：

- `Run 1 / Paper Seat`：`EMA` 仍处于真实 `waiting_not_due`，这轮不能在 paper waiting-window 空转。
- `Run 2 / Scout Seat`：`Rank 2 combo_all` 已完成 `clean replication + Light Stability Pack + paper candidate admission`，当前更诚实的 desk 读法已不是继续扩研究。
- `Run 3 / tiny-live plumbing`：最近几轮已经把 `receipt-chain replay ticket / operator packet / log template / completion gate` 都落表，但这些 closeout 规则主要还挂在 `trendline_alpha_scout` 页与日志里；本轮最贴主线的一小步，是把 **Rank 2 仍 blocked、且唯一允许动作是什么** 同步进更核心的 `alpha_closure_board`，避免 reader-facing 主读板还停留在过宽泛的项目级 tiny-live 口径。

## 开始前检查
- 已检查 `git status --short`：工作区仍有大量与本轮无关的历史脏文件与未跟踪文件，本轮继续坚持 selective 改动，不混提。
- 当前 authoritative seat 状态仍是：
  - `Paper Seat = EMA running paper / waiting_not_due`
  - `Live Seat = 暂空`
  - `Scout Seat = Rank 2 narrow paper candidate`
- 相邻 runs：
  - `2026-03-16_1646_rank2-receipt-chain-operator-packet.md`
  - `2026-03-16_1658_rank2-receipt-log-template.md`
  - `2026-03-16_1707_rank2-receipt-completion-gate.md`

## 本轮主点
### 1）新增 deployable artifact：Rank 2 closeout snapshot
新增：
- `reports/artifacts/alpha_closure_board/small_live_rank2_closeout_snapshot_v1.csv`

这张快照不是再造一张近义说明页，而是把现有 3 份 closeout 证据压成一张更适合主读板消费的合成 artifact：
- `small_live_rank2_status_snapshot_v1.csv`
- `small_live_rank2_receipt_chain_operator_packet_v1.csv`
- `small_live_rank2_receipt_chain_completion_gate_v1.csv`

输出为 `BTC / ETH / SOL` 三条 whitelist leg 各一行，固定展示：
- 当前 `deployment_scope=paper_candidate_only`
- 当前唯一允许动作：`only one real test/no-fill receipt-chain replay on BTC/ETH/SOL whitelist`
- `operator` 限定：`cancel_after_ack; capital stays 0`
- 通过条件：三段真实 refs 同链落地，且 `scope` 不漂移、`capital=0`
- 硬阻断：`scope drift / capital > 0 / missing ack or cancel / new symbol routing`
- 当前 blocker：`idle_gap_watch / time_pocket_review / route_receipt_chain_missing / promotion_boundary=paper_candidate_only`

### 2）同步 reader-facing 主页面
更新：
- `scripts/build_alpha_closure_board_report.py`
- `reports/site/factors/alpha_closure_board/report.html`

新增 reader-facing 卡片：
- `Rank 2 paper-candidate closeout snapshot（v1）`

这张卡把当前最容易被误读的一点钉死：
- `Rank 2` 已经是窄范围 `paper candidate`
- 但 `closeout_state` 仍是 `dry_run_only`
- 在真实 receipt chain 落地前，仍只能写成 `paper_candidate_only / blocked`
- 只有同一条 whitelist-bound replay 上同时拿到真实 `intent_ref + ack_ref + cancel_or_close_ref`，且 `scope` 不漂移、`capital=0`，才允许收口到 `eligible_for_shadow_parity_review`

### 3）回写 authoritative board
已更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 的 `Rank 2` 条目，新增 `2026-03-16 17:28 UTC` 补充：
- `small_live_rank2_closeout_snapshot_v1.csv` 已落表；
- 上述 blocked closeout 规则已同步到更核心的 `alpha_closure_board` 页面；
- 当前 reader-facing 口径进一步锁死：`Rank 2` 仍只允许 whitelist-bound `test/no-fill receipt-chain replay`，不得偷写成 `tiny-live ready`。

## fallback 记录（按要求留痕）
- 尝试对 `scripts/build_alpha_closure_board_report.py` 做一次精确文本替换时，因目标片段未完全命中，首次脚本替换失败。
- 随后立即回退到 `read + 定位片段 + 更稳健脚本注入` 的方式完成局部改写，而不是让整轮失败。

## 最小验证
已执行并通过：
1. `python3 -m py_compile scripts/build_alpha_closure_board_report.py`
2. `python3 scripts/build_alpha_closure_board_report.py`
3. 校验新 artifact：`small_live_rank2_closeout_snapshot_v1.csv` 共 `3` 行（`BTC/ETH/SOL`）
4. `grep -n "Rank 2 paper-candidate closeout snapshot\|small_live_rank2_closeout_snapshot_v1.csv\|paper_candidate_only / blocked\|eligible_for_shadow_parity_review" reports/site/factors/alpha_closure_board/report.html`
5. `grep -n "2026-03-16 17:28 UTC\|small_live_rank2_closeout_snapshot_v1.csv\|alpha_closure_board" docs/TODO.md`
6. `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`

## 硬结论
本轮没有改变席位判断，但把它变得更难被误读：

**`Rank 2 combo_all` 现在已经是窄范围 `paper candidate`，但仍明确卡在 `paper_candidate_only / blocked`。它当前唯一允许动作仍然只是 `BTC/ETH/SOL whitelist` 上的一次真实 `test/no-fill receipt-chain replay`；在真实 `intent_ref + ack_ref + cancel_or_close_ref` 同链落地、且 `scope` 不漂移、`capital=0` 之前，它既不能进入 `shadow_parity`，更不能被写成 `tiny-live ready`。**

这轮的价值不是新增研究结论，而是把 closeout 规则从“散落在 scout 页与日志里的局部事实”同步成“alpha closure board 主读板上的明确事实”。

## 网页可见落点
- `reports/site/factors/alpha_closure_board/report.html`
- 首页索引已刷新：`https://jp.jerrypsy.top/momentum/`

## 风险 / 边界
1. 本轮没有新增真实 venue receipt，也没有缩短 `Rank 2` 到 tiny-live 的真实距离。
2. 新增的是 closeout snapshot，不是放行票，也不是新的 scout alpha 证据。
3. 由于 `build_alpha_closure_board_report.py` 会重写同页若干既有 artifact / 页面文件，本轮仍坚持不提交，避免在当前脏工作区里混提无关改动。

## Commit hash
- 基线：`2080941`

## 未提交原因
当前 git 工作区仍含大量与本轮无关的历史脏文件 / 未跟踪文件；本轮只完成 selective artifact、reader-facing 页面、board write-back、日志与邮件交付，不提交。
