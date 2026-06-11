# 2026-03-16 11:12 UTC｜small-live review registry template：把 closeout 状态固定成同一条可审计 registry row

## 为什么这次选这个
按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 执行：

- **Run 1 / Paper Seat**：`EMA` 仍是 `running paper / waiting_not_due`，当前没有新的 `due-now / overdue` lane。
- **Run 2 / Scout Seat**：本轮先诚实核对共享 Binance `15m` cache，`BTCUSDT / ETHUSDT / SOLUSDT` 最新 completed bar 仍都停在 `2026-03-16 10:45 UTC`，因此当前没有 genuinely new local bar，不能再重跑 `Rank 3 third_touch_plus_ema_macd` continuity。
- 所以这轮按板上规则回退到 **Run 3 / tiny-live plumbing**。

本轮只认领：
- **主点**：新增 `small_live review registry template v1`（deployable artifact）
- **紧邻子点**：把它同步到 `alpha_closure_board` 页面与 `TODO / plans` reader-facing 落点

## 本轮产物
### 1）新增 artifact
- `reports/artifacts/alpha_closure_board/small_live_review_registry_template_v1.csv`

这张卡不是重复 `review ticket template` 或 `writeback matrix`，而是把 closeout 真正落到 **同一条 review registry row** 时最少要带什么压成模板。覆盖 5 类 registry row：

1. `dry_run review row`
2. `shadow parity green row`
3. `parity_red freeze row`
4. `reopen gate row`
5. `resume green row`

每类都写死：
- 最小主键 / 引用（如 `ticket_id`、`candidate_id`、`paper_ref_id`、`prior_red_ref_id`）
- 必须同时落下的状态字段（如 `ticket_status`、`closeout_state`、`next_queue`、`mismatch_status`）
- 必须挂接的证据 / 附件引用
- 何时才配进入下一条队列
- 哪些缺失下必须继续阻断

### 2）同步代码与页面
修改：`scripts/build_alpha_closure_board_report.py`
- 新增路径常量：`SMALL_LIVE_REVIEW_REGISTRY_TEMPLATE_PATH`
- 新增生成函数：`get_small_live_review_registry_template_rows()`
- 新增导出函数：`write_small_live_review_registry_template_csv()`
- 在 `render()` 与 `main()` 中纳入该 artifact 与 reader-facing 卡片

同步页面：
- `reports/site/factors/alpha_closure_board/report.html`
- `docs/TODO.md`
- `reports/site/plans/momentum_todo.html`
- 首页：`https://jp.jerrypsy.top/momentum/`

## 为什么这一步有用
上一轮已经把 `review ticket -> closeout -> writeback -> next queue` 压成矩阵；但 future run 真落表时，仍可能出现：

- 知道应该关成 green / red，却没有同一条 registry row 的固定模板
- `prior_red_ref_id`、`next_queue`、`closeout_state` 分散写在日志、邮件和不同 CSV 里
- 关单结论有了，但状态切换仍没真正闭合

这张卡解决的是最后这一格：

**不只知道“该怎么关单”，还知道“关单后同一条 registry row 至少该长什么样”。**

## 最小验证
1. 读取共享 Binance `15m` cache，确认 `BTCUSDT / ETHUSDT / SOLUSDT` 最新 completed bar 仍都为 `2026-03-16 10:45 UTC` ✅
2. `python3 -m py_compile scripts/build_alpha_closure_board_report.py scripts/build_plans_site.py` ✅
3. `python3 scripts/build_alpha_closure_board_report.py` ✅
4. `python3 scripts/build_plans_site.py` ✅
5. `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` ✅
6. `head -n 6 reports/artifacts/alpha_closure_board/small_live_review_registry_template_v1.csv` ✅
7. `grep -n "11:12 UTC\|small_live_review_registry_template_v1.csv" docs/TODO.md reports/site/plans/momentum_todo.html reports/site/factors/alpha_closure_board/report.html` ✅

## 本轮 hard verdict
一句话：

**这轮没有伪造 Scout continuity；在确认共享 `15m` cache 仍停在 `10:45 UTC` 后，如实回退到 `Run 3`，把 tiny-live 的 `closeout / registry / writeback` 再补成一张可直接复用的 registry row 模板。**

## 风险 / 边界
- 本轮不是 tiny-live 放行，也不是任何真实下单。
- 未重开 `EMA` 发散、未重跑 breakout heavy analysis。
- 只做了与当前 Run 3 fallback 紧邻的一格，不扩成新主线。

## 下一步建议
- 若下一轮前共享 cache 仍停在 `10:45 UTC`，继续优先沿 `closeout / registry / writeback` 紧邻缺口补 tiny-live。
- 若出现 genuinely new completed `15m` bar，再优先回到 `Run 2` 做 `Rank 3` honest continuity。

## Commit
- HEAD：a9a00d9
- 本轮未提交（worktree 有大量无关脏文件，避免混提）。
