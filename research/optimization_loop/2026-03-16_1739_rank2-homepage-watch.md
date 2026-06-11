# 2026-03-16 17:39 UTC｜Run 3：Rank 2 blocked closeout 同步到首页 Deployment Watch

## 为什么这次选这个
按 `docs/TODO.md` 顶部 `TRADING DESK BOARD`：

- `Run 1 / Paper Seat`：`EMA` 仍处于真实 `waiting_not_due`。本轮先用 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due` 复核，结果仍无 `due-now / overdue` lane，因此不能在 paper waiting-window 空转。
- `Run 2 / Scout Seat`：`Rank 2 combo_all` 当前已完成 `clean replication + Light Stability Pack + paper candidate admission`，且 board 已把下一步收紧到：**要么补真实 `test/no-fill receipt-chain replay`，要么继续诚实 blocked**。这轮没有真实 venue receipt 条件，因此不再继续扩研究。
- `Run 3 / tiny-live plumbing`：上一轮已经把 `small_live_rank2_closeout_snapshot_v1.csv` 同步到 `alpha_closure_board`；但首页 `Deployment Watch` 还没有直接显示 `Rank 2` 当前仍是 `dry_run_only / paper_candidate_only / blocked`。本轮最小但有用的一步，是把这条 blocked closeout 状态直接同步到首页，让 Jerry 不用先点进二级页才能看到。

## 开始前检查
- 已检查 `git status --short`：工作区仍有大量与本轮无关的历史脏文件 / 未跟踪文件，本轮继续只做 selective 修改，不混提。
- 已执行：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 结果：当前仍没有 `due-now / overdue` lane；最靠前的是 `美股 1d+1wk`，约 `2.4` 小时后到点。
  - 结论：`Paper Seat` 本轮仍然是严格 `waiting_not_due`，因此按 desk 顺序切到 `Run 3`。
- 当前 authoritative seat 状态保持不变：
  - `Paper Seat = EMA running paper / waiting_not_due`
  - `Live Seat = 暂空`
  - `Scout Seat = Rank 2 narrow paper candidate`

## 本轮主点
### 1）把 Rank 2 closeout 状态挂进首页 Deployment Watch
修改：
- `scripts/build_site_index.py`

新增首页读取：
- `reports/artifacts/alpha_closure_board/small_live_rank2_closeout_snapshot_v1.csv`

首页现在会直接显示一条新的 watcher：
- `Scout Rank 2 / tiny-live plumbing`
- 当前 `closeout_state = dry_run_only`
- 当前唯一允许动作仍是：`BTC/ETH/SOL whitelist` 上的一次真实 `test/no-fill receipt-chain replay`
- 只要出现 `scope drift / capital > 0 / missing ack or cancel / new symbol routing`，就继续停在 `paper_candidate_only / blocked`
- 当前 blocker 仍保留：`idle_gap_watch`、`time_pocket_review`、`route_receipt_chain_missing`、`promotion_boundary=paper_candidate_only`

这一步没有伪造新的执行回执，也没有把 Rank 2 往 tiny-live 偷推半格；它只是把已有的 blocked closeout 事实从 `alpha_closure_board` 再压到首页主读面。

### 2）回写 authoritative board
已更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 的 `Rank 2` 条目，新增 `2026-03-16 17:34 UTC` 补充：
- 首页 `Deployment Watch` 现也直接读取 `small_live_rank2_closeout_snapshot_v1.csv`
- Jerry 只看首页也能看到：`Rank 2` 仍处于 `dry_run_only / paper_candidate_only / blocked`
- 在真实 receipt chain 落地前，默认不应把它误读成 `tiny-live ready`

## 最小验证
已执行并通过：
1. `python3 -m py_compile scripts/build_site_index.py`
2. `python3 scripts/build_site_index.py`
3. `grep -n "Scout Rank 2 / tiny-live plumbing\|small_live_rank2_closeout_snapshot_v1.csv\|paper_candidate_only / blocked" reports/site/index.html`
4. `grep -n "2026-03-16 17:34 UTC\|small_live_rank2_closeout_snapshot_v1.csv" docs/TODO.md`
5. `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`
6. `stat -c '%y %n' /var/www/momentum-report/index.html /root/clawd/jerry/momentum/reports/site/index.html`
   - 结果：站点首页与发布目录时间戳已同步刷新

## 硬结论
本轮没有改变 desk 席位判断，但把一个容易被读漏的事实直接推到了首页：

**`Rank 2 combo_all` 现在仍然只是窄范围 `paper candidate`，并且 closeout 状态仍是 `dry_run_only / paper_candidate_only / blocked`。它当前唯一允许动作仍是 `BTC/ETH/SOL whitelist` 上的一次真实 `test/no-fill receipt-chain replay`；在真实 `intent_ref + ack_ref + cancel_or_close_ref` 同链落地、且 `scope` 不漂移、`capital=0` 之前，它既不能进入 `shadow_parity`，更不能被写成 `tiny-live ready`。**

## 网页可见落点
- 首页：`reports/site/index.html`
- 发布路径：`/var/www/momentum-report/index.html`
- 补充页面仍保留：`reports/site/factors/alpha_closure_board/report.html`

## 风险 / 边界
1. 本轮没有新增真实 venue receipt，也没有缩短 `Rank 2` 到 tiny-live 的真实距离。
2. 首页新增的是 blocked-state watcher，不是放行票，更不是 receipt-chain pass。
3. 当前若继续围绕 `Rank 2` 推进，默认只应等待真实 whitelist-bound replay 条件，而不应再回到同类近义说明页。

## Commit hash
- 基线：`2080941`

## 未提交原因
当前 git 工作区仍含大量与本轮无关的历史脏文件 / 未跟踪文件；本轮只完成 selective 脚本、首页、board、日志与邮件交付，不提交。
