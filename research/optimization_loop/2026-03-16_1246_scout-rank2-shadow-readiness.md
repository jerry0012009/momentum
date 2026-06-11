# 2026-03-16 12:46 UTC｜Scout Seat：Rank 2 combo_all 历史样本 shadow-readiness dry-check

## 为什么这次选这个
先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 与 `Next 3 bot3 runs` 守门：

- **Run 1 / Paper Seat**：`EMA` 仍处于 `running paper / waiting_not_due`，当前没有新的 `due-now / overdue` lane；A 股下一次 close 仍要等后续 market close。
- **Run 2 / Scout Seat**：最新 authoritative override 已明确——在候选进入 `shadow-admission / continuity-week / live-readiness` 之前，Scout 默认优先用**历史样本**推进 `first verdict / friction / trade-count / shadow-readiness`，而不是默认追 shared Binance `15m` cache 的最新 completed bar。
- **Run 3 / tiny-live plumbing**：虽然仍可作为 fallback，但既然 Scout 还有合规的历史样本刀口，就不应跳过去空转。

因此本轮只认领 **1 个主点**：把 `Rank 2 combo_all` 补成一张基于现有历史样本的 `shadow-readiness dry-check`；并认领 **1 个紧邻子点**：把这个 verdict 同步到 reader-facing scout 总览与 TODO 顶部排班说明。

## 开始前检查
### repo / 脏文件
`git status --short` 显示 worktree 里已有大量与本轮无关的既有脏文件与未跟踪产物（集中在 EMA、breakout、trendline、workspace 根目录等）。本轮只做 **selective** Scout Rank 2 页面与 TODO/站点镜像刷新，不混碰其他主题。

### 当前席位状态
- `Paper Seat = EMA`：`waiting_not_due`
- `Live Seat = breakout`：`bench / recheck-only`
- `Scout Seat`：按 authoritative override，优先补基于历史样本的 `trade-count / shadow-readiness` 收紧，而不是继续追 `Rank 3` continuity

## 本轮做了什么
### 主点：为 Rank 2 补一张 shadow-readiness dry-check
更新脚本：`scripts/build_volume_supportflip_higherlow_first_verdict.py`

新增 artifact：
- `reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_shadow_readiness_drycheck.csv`

新增逻辑：
- 基于现有 `variant_aggregate.csv` + `combo_all_friction_ladder.csv`，把 `combo_all` 压成一张只回答“值不值得继续保留为 shadow-candidate”的快筛卡；
- 明确区分：
  - `pass`：基础 post-cost 回报、15bps friction、2/3 跨资产为正、最小 trade-count、false-break 控制；
  - `fail`：`shadow_admission_scope` 仍未满足；
  - `watch`：20bps 仍为正只是加分项，不是准入许可证。

### 紧邻子点：把 verdict 外显到 reader-facing 页面
同步更新：
- `scripts/build_trendline_alpha_scout_report.py`
- `docs/TODO.md`

重新生成：
- `reports/site/factors/scout_volume_supportflip_higherlow_15m/report.html`
- `reports/site/reading/trendline_alpha_scout/report.html`
- `reports/site/plans/momentum_todo.html`
- 首页 index（含发布）：`bash scripts/publish_homepage_index.sh`

## 最小验证
执行：
1. `python3 -m py_compile scripts/build_volume_supportflip_higherlow_first_verdict.py scripts/build_trendline_alpha_scout_report.py scripts/build_plans_site.py`
2. `python3 scripts/build_volume_supportflip_higherlow_first_verdict.py`
3. `python3 scripts/build_trendline_alpha_scout_report.py`
4. `python3 scripts/build_plans_site.py`
5. `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`
6. `grep` 校验落点：
   - `reports/site/factors/scout_volume_supportflip_higherlow_15m/report.html`
   - `reports/site/reading/trendline_alpha_scout/report.html`
   - `reports/site/plans/momentum_todo.html`

全部通过。

## 关键结果 / hard verdict
`reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_shadow_readiness_drycheck.csv` 结果：

- `base_post_cost_return`：**pass**（`2.33%` @ `6bps/side`）
- `friction_15bps_hold`：**pass**（`1.10%`）
- `cross_asset_floor`：**pass**（`66.67%` = `2/3` assets positive）
- `trade_count_floor`：**pass**（mean trades `6.7` / asset）
- `false_break_guard`：**pass**（`6.67%`）
- `shadow_admission_scope`：**fail**（仍只有 `120d / 15m / 3 assets`，且 `positive_assets=2/3`）
- `friction_20bps_watch`：**watch**（`0.42%`，仅作加分项）

一句话 hard verdict：

**`Rank 2 combo_all` 已通过最小 `trade-count / friction / false-break` 快筛，仍值得保留为 `keep-narrower shadow-candidate`；但样本仍偏窄，当前还不是 `shadow-admission-ready / replace-ready / tiny-live ready`。**

## 风险 / 边界
- 这仍然只是 **历史样本 dry-check**，不是新的 forward continuity，更不是 shadow/live 放行；
- 当前 evidence 只覆盖 `120d / 15m / BTC+ETH+SOL`；
- `2/3` positive assets 足够支撑“继续观察”，不足以支撑“准入”。

## 对 desk 排班的含义
- 当 `EMA` 处于 `waiting_not_due` 时，Scout 默认仍应先于 tiny-live 拿主资源；
- 但后续优先级应继续停留在 **历史样本收紧**（`trade-count / shadow-readiness / honesty`），而不是默认回到追最新 completed `15m` bar；
- 只有 board 或 bot2 最新 review 明确授权 continuity/shadow 检查时，才应再把“基于新 completed bar 的 continuity”当成本轮主点。

## 网页可见落点
- `reports/site/factors/scout_volume_supportflip_higherlow_15m/report.html`
- `reports/site/reading/trendline_alpha_scout/report.html`
- `https://jp.jerrypsy.top/momentum/`

## Commit hash（基线）
- `5e1d263`

## 如果未提交，原因
当前 worktree 里有大量与本轮无关的既有脏文件与未跟踪文件；为避免混提，本轮只做 selective 构建、站点刷新与 run log 记录，不做提交。
