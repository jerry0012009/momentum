# EMA 首周 review 记分卡

## 为什么这次选这个
- 本轮先按要求检查了 repo 状态、`docs/TODO.md` 与最近几轮自动优化记录。
- breakout 线这半天已经连续把 `pure-test / pre-down / down-risk` 相关 retrospective blocker 压得很细，而且 `scope verdict` 已明确写成：当前样本里的 micro-slicing 基本榨干，下一次有效推进更该来自新的 forward / shadow `pure-test/down-tail` 命中，而不是继续在同一段历史样本里补近义切片。
- EMA 线这边刚连续补完 `candidate spec -> operating spec -> monitoring board -> runbook -> day-0 checklist / ledger -> day-0 seed rows`，离真正 `paper / shadow` 还差的一刀更像是：**首个 weekly review 到底怎么诚实地判 green / yellow / red，以及判完后具体 keep / demote / stop 什么**。
- 所以本轮选了一个更接近 deployment、又能在一轮里完整做完的小任务：把 EMA 的 day-0 启动链再压成 `first weekly review scorecard / red-yellow-green protocol`。

## 做了什么改动
1. 更新 `scripts/build_ema_psar_raw_alpha_report.py`
   - 新增 `build_ema_paper_first_week_review_scorecard()`；
   - 复用现有 `runbook + monitoring board`，生成 `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_first_week_review_scorecard.csv`；
   - 在 `EMA / PSAR Raw Alpha Focus Report` 新增 `Q31`，专门回答“day-0 后第一轮 weekly review 怎么判、怎么动作”；
   - 原来的“这页边界”顺延为 `Q32`。
2. 更新 `docs/TODO.md`
   - 把 `EMA：把 day-0 launch seed rows 再压成 first weekly review scorecard / red-yellow-green protocol` 标记为已完成；
   - 补上当前更 deployment-facing 的口径：
     - `创业板ETF 1d` 若首周转 red，直接 `demote_to_shadow`；
     - secondary 任一 pocket 若转 red，只降该 pocket，不再用整批结果遮盖；
     - `沪深300ETF 1d` 首周即便顺利也默认 `stay shadow`；
     - stoplist 若误混回账本，立即 `rollback`。
3. 重建可见交付
   - 重跑 `reports/site/factors/ema_psar_raw_alpha/report.html`；
   - 重跑 `reports/site/plans/momentum_todo.html` 镜像。

## 验证 / 证据
- 运行：`python3 scripts/build_ema_psar_raw_alpha_report.py && python3 scripts/build_plans_site.py`
  - 结果：成功，退出码 `0`。
- 页面检查：
  - `reports/site/factors/ema_psar_raw_alpha/report.html` 已出现 `Q31` 与 `EMA paper/shadow first weekly review scorecard`；
  - 原边界段已顺延为 `Q32`。
- 产物检查：
  - `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_first_week_review_scorecard.csv` 已生成；
  - 核心动作口径已落表：
    - `创业板ETF 1d`：`green = keep_primary；yellow = keep + extra review；red = demote_to_shadow`；
    - secondary 三组：`red = demote_that_pocket_to_shadow`；
    - `沪深300ETF 1d`：`green / yellow` 也仍是 `keep_shadow`；
    - stoplist 三格：`red = rollback_to_stoplist_now`。
- TODO 镜像检查：
  - `reports/site/plans/momentum_todo.html` 已同步出现这条新完成项。

## 风险 / 边界
- 这轮没有新增 forward 回测或新的 holdout 证据，做的是**运行规则压缩**，不是又宣称 EMA 已经进入真实 paper trading。
- 这张 scorecard 解决的是“首周怎么判、怎么动作”，不解决“secondary batch 是否还需要更严格 holdout honesty 再收窄”。后者若继续推进，仍应优先补真实 forward / holdout，而不是再造近义 board。
- 当前 worktree 本来就有大量与本轮无关的脏文件和未跟踪产物；本轮只在记录里说明，不混提无关改动为“本轮成果”。

## 下一步建议
- EMA 线如果继续，下一刀更值得补 **secondary batch 的更严格 forward / holdout honesty**，尤其是现在 `paper_now_secondary` 的 `美股 / Crypto / 贵州茅台 1d+1wk` 是否需要进一步分层，而不是继续补近义运营页面。
- breakout 线则继续遵守当前 freeze 口径：除非拿到新的 `pure-test / down-tail` forward 命中，否则不要再在同一段历史样本里做更细 retrospective micro-slicing。

## Commit hash
- 未提交。
- 原因：当前 git 工作区存在大量与本轮无关的已修改/未跟踪文件；本轮虽只改了 `scripts/build_ema_psar_raw_alpha_report.py`、`docs/TODO.md` 及对应站点/产物，但此时直接提交容易把无关改动混进来，因此先保留为未提交状态更安全。
