# Rank 113 / alpha-beta abstain / profit-window source intake

## 为什么这次选这个
- 先按交易台指挥板执行 `Run 1 / EMA due-check first`：实际运行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due` 后，继续如实返回 **全 desk `waiting_not_due`**；最近 due 仍是 `美股 1d+1wk -> 2026-03-20 20:00 UTC`、`Crypto 1d+1wk -> 2026-03-21 00:00 UTC`。
- `manual_narrow_paper_last_run_summary.json @ 2026-03-20T07:24:44Z` 仍是 `new_closed_trades_appended=0`，说明当前也没有新的 `P3 status-changing event` 能插队。
- 按 `docs/TODO.md` 顶部最新 `Next 3`，`Rank 112` 已完成那 1 次最小 clean replication 并降到 `P1 weak candidate / evidence_pool / budget used`，所以本轮合法主动作只剩 **`alpha-beta abstain / profit-window` 的 ex-ante honesty gate source intake**。
- 同时遵守 `7.10.1`：任何进入 queue-facing / reader-facing 的新 Scout 方向，都必须先拿顺序 Rank，因此本轮先把它正式编号为 **`Rank 113`**。

## 做了什么改动
1. 新增 `scripts/build_rank113_alpha_beta_abstain_source_intake.py`
   - 把论文 + repo 的可迁移核心收缩成 queue-facing source intake card；
   - 明确它只允许作为 **现有 base setup 的 ex-ante admission / veto overlay**，而不是独立 alpha；
   - 把 `alpha / beta` 翻译为只能使用 `signal 当根及之前数据` 的 move-size proxy band：
     - 过小 = 噪音，不做；
     - 过大 = 冲击尾端，不追；
     - 中间窗口 = base setup 才允许继续；
   - 把 `profit-window` 约束成：只能在训练段按 post-cost expectancy 冻结 1 个 hold horizon，再去测试段验证。
2. 运行脚本，落地 reader-facing artifacts：
   - `reports/artifacts/literature/scout_rank113_alpha_beta_abstain_profit_window_source_intake_card.csv`
   - `reports/site/reading/repo_scout/rank113_alpha_beta_abstain_profit_window_source_intake.html`
3. 最小更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`
   - 追加 `2026-03-20 07:47 UTC` 顶板补充；
   - 把当前主 Scout 顺序改写为 `Rank 113 > Rank 112 > Rank 111 > ...`；
   - 把 `Next 3` 前推为：
     - `Run 1 = EMA due-check first`
     - `Run 2 = Rank 113 1 次最小 clean replication`
     - `Run 3 = 若 Rank 113 hard-fail / exhausted，则回 fresh intake；再不行才 tiny-live plumbing`

## 验证 / 证据
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 输出继续确认：当前无 `due-now / overdue lane`；最近 due 约为 `美股 1d+1wk 12.2h`、`Crypto 1d+1wk 16.2h`。
  - 该命令以 code `2` 退出，但这是 `require-due` 下的**预期 waiting 路径**，不是异常失败。
- `python3 scripts/build_rank113_alpha_beta_abstain_source_intake.py`
  - 成功写出 CSV card 与 HTML 页面。
- 当前 hard verdict：**`Rank 113 / alpha-beta abstain / profit-window = guard-passed / admit_to_clean_replication_queue`**。

## 当前最诚实的结论
- 这条线**可以被诚实地翻译成 ex-ante overlay**，但前提是：
  1. 它只回答“现有 setup 该不该做”；
  2. 不能直接搬论文里的 `forward return labels` 当实时信号；
  3. `alpha / beta` 阈值与 `profit-window` 只能由训练段或滚动过去窗口估计并冻结；
  4. clean replication 必须统一到 `signal 当根及之前数据 + next-bar open + no-overlap`。
- 翻成人话：**这条线值得花 1 次最小 replication 预算，去验证“别做太小的噪音单，也别追已经冲太远的单”是否真能改善现有 setup；但它现在还不配被说成一条独立策略。**

## 风险 / 边界
- 最大风险不是“效果不好”，而是**把 forward-label 论文偷渡成 lookahead gate**。这轮已经在 intake 卡里把这个风险写死；下一轮若 replication 仍不遵守 train/test 冻结，就应直接判不诚实。
- 若 dual-band 结果只是通过大幅砍掉 trade count 换来表面改善，或只在单一 symbol / 单一窗口偶然有效，应直接 `park`，不要拖成长期 P1。
- 当前 `Live Seat` 继续保持空位；`Rank 113` 还没有任何 `Light Stability Pack` 完成项，不配争抢 live challenger。

## 下一步建议
- 下一轮若 `EMA` 仍 `waiting_not_due`：
  1. 只选 **1 条** base archetype（优先 breakout-short 或 fib retest）；
  2. 训练段先冻结 `lower no-trade band`、`upper shock band`、`1 个 profit-window`；
  3. 测试段只比较 `baseline / lower-band-only / dual-band` 三臂；
  4. 主看 `post-cost expectancy / trade_retention / false-break or fail-rate / symbol dispersion`；
  5. 若没有 honest uplift，就直接 park，切回 fresh intake。

## Commit hash
- 本轮未提交。
- 原因：当前 git 工作区存在大量与本轮无关的已修改/未跟踪文件，无法安全 selective commit；为避免混提，先只保留 artifact、顶板更新与日志。
