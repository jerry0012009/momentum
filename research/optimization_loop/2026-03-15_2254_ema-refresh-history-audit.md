# 2026-03-15 22:54 UTC｜EMA refresh history audit：把 append-only ledger 连回主报告

## 为什么这次选这个
- 先检查了 `git status --short`、`docs/TODO.md`、`docs/AUTO_OPTIMIZATION_LOOP.md`，以及最近几轮 optimization logs。
- 当前 steering 仍是：`EMA baseline family = closest to paper`、`support_breakout_v0 = one_more_gate`、`Fibonacci = archived/optional`。
- `EMA` 的真正主任务仍是 line-305：沿同一张 live ledger 落下一轮新的 `market-close refresh / week-1 review`。但当前还没到下一根真实 completed bar，继续硬做只会重复 waiting-window 补丁。
- breakout 线当前也没有新的 overturn 入口；在同一段冻结样本上继续切更细 micro-slices，不符合当前 steering。
- 所以这轮选一个**紧邻 line-305、且更接近 deployment / bookkeeping honesty**的小切片：把已有的 `ema_paper_trading_refresh_history.csv` 正式挂回 EMA 主报告，并补一张可直接判断“是否真的在连续续写”的 `refresh_history_audit`。

## 本轮主点
- 主点：`EMA` 线的 append-only history bookkeeping。
- 紧邻子点：把这个 audit 回写 `docs/TODO.md` / plans 镜像，明确下一次真实 close 到来后该看什么，不再只盯覆盖式 latest snapshot。

## 做了什么

### 1) 在 `build_ema_psar_raw_alpha_report.py` 新增 refresh history audit builder
新增：
- `EMA_REFRESH_HISTORY_PATH`
- `EMA_REFRESH_HISTORY_AUDIT_PATH`
- `build_ema_paper_trading_refresh_history_audit()`

这张 audit 按 `deployment_scope × market_freq_book` 汇总现有 append-only ledger，并给每条 lane 写出：
- `rows_recorded`
- `distinct_completed_bars`
- `latest_completed_bar_utc`
- `latest_history_recorded_at_utc`
- `history_status`
- `continuity_read`
- `next_needed_to_advance`

当前最关键的 deployment-facing 读法是：
- 现在已经不只是“有一份最新 snapshot”；
- 还可以直接看出每条 lane 目前到底只是 `seed_only_history`，还是已经进入 `append_only_continuing`。

### 2) 把 history audit 正式挂回 `EMA / PSAR Raw Alpha Focus Report`
EMA 主报告新增 `Q35j`：
- 明确区分“覆盖式 latest snapshot” vs “append-only ledger 连续续写”；
- 给出当前项目级 verdict、seed 状态、最近一条 history 记录、以及下一次 close 到来后该怎么用这张 audit；
- 不新增 alpha 结论，只补**bookkeeping honesty / ledger continuity** 这一层 deployment 视角。

这一步对应当前 steering 里 EMA 下一刀更该补的那类内容：
- 记账口径
- refresh 连续性
- 运行审计
- 而不是继续新增近义 board / queue / closure-copy 页面

### 3) 回写 `docs/TODO.md`
在 line-305（`EMA：沿同一张 live ledger 连续落下下一轮 market-close refresh / week-1 review`）下面补了一条最新说明：
- `ema_paper_trading_refresh_history.csv` 现在已正式挂回主报告；
- 新增 `ema_paper_trading_refresh_history_audit.csv`；
- 当前各 lane 仍大多只有 `seed_only_history = 1` 条记录；
- 所以下一次真实 close 到来后，默认应优先检查 `rows_recorded` 是否从 `1` 增到 `2+`，而不是只盯新的覆盖式 snapshot。

注意：这**不是**把 line-305 标成完成；它只是把 line-305 下一次真实落地时该看的记账信号说得更清楚。

## 产出文件
- `scripts/build_ema_psar_raw_alpha_report.py`
- `docs/TODO.md`
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_refresh_history_audit.csv`
- `reports/site/factors/ema_psar_raw_alpha/report.html`
- `reports/site/plans/momentum_todo.html`

## 验证 / 证据
执行：
- `python3 -m py_compile scripts/build_ema_psar_raw_alpha_report.py`
- `python3 scripts/build_ema_psar_raw_alpha_report.py`
- `python3 scripts/build_plans_site.py`
- `grep -n "Q35j\|refresh history audit\|2026-03-15 22:46 UTC" reports/site/factors/ema_psar_raw_alpha/report.html reports/site/plans/momentum_todo.html`

验证结果：
- `build_ema_psar_raw_alpha_report.py` 语法检查通过；
- EMA 主报告已成功重建，并新增 `Q35j` / `EMA paper/shadow refresh history audit`；
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_refresh_history_audit.csv` 已落地；
- 当前 audit 显示 `5/5` 条 lane 都还是 `seed_only_history`，`rows_recorded = 1`；
- 这意味着 append-only ledger 已建立，但**真正的连续续写仍要等下一根真实 completed bar**。

## 这一步的实际价值
- 它不会伪造新的 forward refresh；
- 也不会改写 breakout 当前的 `one_more_gate`；
- 但它补上了一个真实 deployment-facing gap：
  - 之前可以看 queue / due-guardrail / latest snapshot；
  - 现在还能直接看**这张 ledger 到底是不是在连续追加**。

对 Jerry 的判断帮助更直接：
- 如果下一次真实 close 后 `rows_recorded` 仍停在 `1`，那就不是“页面还没更新”这么简单，而更像 refresh 没真正续写；
- 如果后续变成 `2+` 且无 duplicate key，才算这条 EMA paper ledger 真开始跑起来。

## 风险 / 边界
- 当前 history audit 依赖已有 `ema_paper_trading_refresh_history.csv`；它不会替代真正的 refresh 执行。
- 这一步只补记账与续写 honesty，不代表 EMA 已获得新的 forward alpha 证据。
- breakout / Fibonacci 本轮没有新增主结论。

## 执行层 hygiene
- `git status --short` 显示 worktree 存在大量与本轮无关的既有脏改 / 未跟踪文件；本轮没有把这些改动混进记录。
- 本轮没有尝试 selective commit，因为当前工作区过脏，且 `build_ema_psar_raw_alpha_report.py` / `build_plans_site.py` 会触发大量历史产物再生成，误混无关文件风险过高。

## Commit hash
- HEAD：`8cd0f42`
- 本轮未提交。

## 未提交原因
- 当前 worktree 内有大量与本轮无关的既有改动与未跟踪产物；在这种状态下做 selective commit 风险高于收益。
- 本轮更适合保持为**可审计未提交产出 + optimization log**，等后续有更干净的提交窗口再处理。