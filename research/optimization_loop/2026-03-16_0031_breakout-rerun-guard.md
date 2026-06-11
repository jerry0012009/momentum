# 2026-03-16 00:31 UTC｜breakout rerun guard：把“何时值得重跑”压成可执行门槛

## 为什么这次选这个
- 先看了 `docs/TODO.md`、`docs/AUTO_OPTIMIZATION_LOOP.md`、当前 repo 状态与最近 loop 记录。
- 当前 steering 对 breakout 的要求是：只做可能 overturn scope verdict 的证据；若没有新证据，不要继续同类 micro-slice / wording。
- 在这条边界下，本轮选择一个 deployment-facing 小而完整动作：把 breakout 的“是否值得再跑 heavy refresh rerun”做成显式 guard，减少后续重复重跑与误判。

## 本轮主点
- 主点：`support_breakout_v0 / breakout-short follow-up`
- 紧邻子点：把 guard 结果同步到 `TODO + plans 镜像 + 首页 Deployment Watch`，让 Jerry 只看首页也能直接判断“现在该不该再跑 breakout heavy rerun”。

## 做了什么改动
1. 新增脚本：
   - `scripts/build_breakout_revisit_guard.py`
   - 作用：读取
     - `support_breakout_v0_h24/avoid_fluctuating_refresh_recheck_*_20bps.csv`（上次 heavy recheck 基准）
     - `pytrendline_event_validation_v3/cache/*.csv`（当前 cache 尾部）
     - `pytrendline_event_validation_v3/event_sample_purged.csv`（当前 breakout 样本尾部）
   - 输出：`reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_revisit_guard_20bps.csv`

2. 生成 guard artifact（本轮结果）：
   - `last_heavy_recheck_checked_bar_utc = 2026-03-13 13:00:00 UTC`
   - `current_cache_latest_bar_utc = 2026-03-16 00:00:00 UTC`
   - `cache_tail_delta_vs_last_recheck = +59.0h`
   - `revisit_guard_verdict = cache_advanced_rerun_worth_checking`
   - `operator_action = rerun heavy breakout refresh recheck`

3. 更新首页构建逻辑：
   - 修改 `scripts/build_site_index.py`
   - 新增读取 `avoid_fluctuating_revisit_guard_20bps.csv` 并在 `Deployment Watch` 输出一条 `Breakout rerun guard` 卡片。

4. 回写任务与网页镜像：
   - 更新 `docs/TODO.md`（breakout 线追加一条 `[x]` 最新补充，记录 guard 结果与动作边界）
   - 重建 `reports/site/plans/momentum_todo.html`
   - 重建 `reports/site/index.html`

## 验证 / 证据
- 执行：
  - `python3 scripts/build_breakout_revisit_guard.py`
  - `python3 scripts/build_plans_site.py`
  - `python3 scripts/build_site_index.py`
  - `python3 -m py_compile scripts/build_breakout_revisit_guard.py scripts/build_site_index.py`
- 核对：
  - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_revisit_guard_20bps.csv` 已生成并包含 `revisit_guard_verdict/operator_action`
  - `docs/TODO.md` 与 `reports/site/plans/momentum_todo.html` 已出现 `2026-03-16 00:31 UTC` 的新增条目
  - `reports/site/index.html` 已出现 `Breakout rerun guard` 段

## 风险 / 边界
- 本轮没有直接新增 breakout alpha 证据（没有新 non-zero pure-down / pre-down 命中）；本轮价值是把“何时值得重跑”从口头规则变成可执行 guard。
- `revisit_guard_verdict = cache_advanced_rerun_worth_checking` 只表示“重跑有意义”，不代表 `one_more_gate` 已被解除。
- `pytrendline_event_validation_v3` 仍只作为 breakout 上游历史证据包引用，未 reopen 为独立主线。

## 执行层 hygiene
- `git status --short` 显示工作区存在大量与本轮无关的历史脏改/未跟踪文件；本轮仅补 guard 脚本、guard artifact、TODO 与首页/plans 镜像，不混提无关改动。
- 本轮中途有一次重型 rerun 尝试耗时过长，已终止；最终改为轻量 guard 方案，避免继续把整轮时间消耗在重下载上。

## 下一步建议
- 下一轮若继续 breakout，默认先看 `avoid_fluctuating_revisit_guard_20bps.csv`：
  - 若仍是 `cache_advanced_rerun_worth_checking`，再跑一次 heavy rerun 去检查是否出现真正 overturn 证据；
  - 若回到 `same_sample_hold_no_rerun`，则不要再重复同类 rerun，时间切回 EMA close 后的 ledger 续写。

## Commit hash
- HEAD：`f09a838`
- 本轮未提交。

## 未提交原因
- 当前工作区存在大量与本轮无关的既有脏改，selective commit 风险高；因此本轮保持“可审计文件落地 + 首页可见 + 邮件同步”，不打包提交。
