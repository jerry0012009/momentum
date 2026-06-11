# 2026-03-15 23:35 UTC｜首页补上 breakout fresh rerun 守门读法

## 为什么这次选这个
- 先检查了 `docs/TODO.md`、`docs/AUTO_OPTIMIZATION_LOOP.md`、最近两轮 optimization log，以及当前 worktree 状态。
- 当前 steering 仍是：`EMA baseline family` 最接近 paper，但真正未完成的主线还是等下一根真实 completed bar；现在还没到 `Crypto 1d` 的下一次 close，硬做只会继续伪造不存在的新 refresh。
- breakout 线刚在上一轮完成了 fresh rerun recheck，并确认**没有** fresh overturn evidence；但首页 `Deployment Watch` 之前仍主要展示抽象 `scope verdict`，没有把这轮 fresh rerun 的关键 blocker 直接露出来。
- 因此本轮选择一个更 deployment-facing、也更贴网页最终表达的小任务：把 breakout 最新 rerun 结果直接挂到首页守门快照里，让 Jerry 只看首页也能更快判断“这条线现在不该继续切旧样本”。

## 本轮主点
- 主点：`support_breakout_v0 / breakout-short follow-up`
- 紧邻子点：把最新 `fresh refresh recheck` 的 admission blocker 直接接到首页 `Deployment Watch`，并同步回写 `docs/TODO.md` / plans 镜像。

## 做了什么改动
### 1) 修改 `scripts/build_site_index.py`
- 新增 `read_latest_glob_csv_rows()`，让首页可自动读取最新一份 breakout `fresh refresh recheck` artifact，而不是写死单个文件路径。
- 在 `render_ops_watch()` 中追加一条新的首页守门摘要：
  - 当前 purged sample 尾部仍停在什么 `action_timestamp`
  - 上游 cache 只刷新到哪根 bar
  - `pure down` 与 `12h pre-down bridge` 这两个最硬 blocker 仍是多少
  - 当前 verdict 仍是 `same_sample_freeze_still_holds`
- 这样首页不再只说“breakout 还是 one_more_gate”，而是直接告诉读者：**fresh rerun 之后，为什么它还是不能继续往 admission 前进。**

### 2) 回写 `docs/TODO.md`
- 在首页入口那条已完成任务下面补一条最新说明：
  - `Deployment Watch` 已吸收 breakout 最新 rerun artifact；
  - Jerry 现在只看首页，也能直接知道这条线当前没有新的 overturn evidence，而不是还要回头翻 artifact 或 log。

## 产出文件
- `scripts/build_site_index.py`
- `docs/TODO.md`
- `reports/site/index.html`
- `reports/site/plans/momentum_todo.html`
- `research/optimization_loop/2026-03-15_2335_homepage-breakout-recheck-watch.md`

## 验证 / 证据
执行：
- `python3 -m py_compile scripts/build_site_index.py`
- `python3 scripts/build_plans_site.py`
- `python3 scripts/build_site_index.py`
- `grep -n "Breakout fresh recheck\|23:35 UTC\|action_timestamp\|Deployment Watch" reports/site/index.html reports/site/plans/momentum_todo.html`

验证结果：
- `build_site_index.py` 语法检查通过；
- `plans` 镜像与首页都已成功重建；
- 首页 `Deployment Watch` 现已新增 `Breakout fresh recheck` 条目，直接写出：
  - `action_timestamp` 仍停在 `2026-03-10 11:00:00+00:00`
  - 上游 cache 仍只到 `2026-03-13 13:00:00+00:00`
  - `pure down = 0/100`
  - `12h pre-down bridge = 0/11`
  - verdict 仍是 `same_sample_freeze_still_holds`
- `plans/momentum_todo.html` 也已同步出现 `2026-03-15 23:35 UTC` 的最新补充。

## 这一步的实际价值
- 这一步没有伪造 EMA 的新 refresh，也没有再回去对 breakout 切新的 retrospective micro-slices。
- 它做的是更诚实的网页收口：
  - breakout 已经 rerun 过；
  - rerun 之后 blocker 还是没动；
  - 因此首页现在能直接告诉 Jerry：这条线当前不该继续消耗主资源，除非真的出现新的 post-tail / down-tail 证据。
- 对当前项目判断最有帮助的一点是：
  - **EMA** 继续等真实 close；
  - **breakout** 当前没有 fresh overturn evidence；
  - 所以“下一轮该等什么 / 不该再做什么”在首页已经更清楚了。

## 风险 / 边界
- 这一步改善的是首页可见性，不会替代真正的 forward / shadow 新证据。
- 若后续 breakout 再生成新的 refresh recheck artifact，首页会按最新文件继续读；但它仍只是读 artifact，不会自己制造新结论。
- 本轮没有重跑 breakout，也没有推进 EMA 真实 refresh；新增的是“把最新 rerun 读法挂到首页”的 deployment-facing 表达。

## 执行层 hygiene
- `git status --short` 仍显示 repo 内外有大量与本轮无关的既有脏改 / 未跟踪文件；本轮没有把这些无关内容混进记录。
- 本轮只修改了首页构建脚本、TODO 注释和对应站点产物，没有回头扩新的 EMA board / protocol 页面，也没有 reopen `pytrendline_event_validation_v3`。

## Commit hash
- HEAD：`f09a838`
- 本轮未提交。

## 未提交原因
- 当前工作区仍很脏，存在大量与本轮无关的既有修改与未跟踪产物；在这种状态下做 selective commit 风险偏高。
- 本轮更适合保持为：可审计首页改动 + TODO/site 更新 + optimization log。