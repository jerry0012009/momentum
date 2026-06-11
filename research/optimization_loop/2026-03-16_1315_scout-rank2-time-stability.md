# 2026-03-16 13:15 UTC｜Scout Seat：Rank 2 combo_all 时间稳定性 dry-check

## 为什么这次选这个
先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 守门：

- **Run 1 / Paper Seat**：`EMA` 仍是 `running paper / waiting_not_due`，当前没有新的 `due-now / overdue` lane。
- **Run 2 / Scout Seat**：上一轮已经给 `Rank 2 combo_all` 补了 `shadow-readiness` 与 `trade-count honesty`，继续沿同一候选补一刀 **Light Stability Pack** 比新开别的候选更合规。
- **Run 3 / tiny-live plumbing**：当前不是首选，因为 Scout 仍有明确的历史样本动作可做。

因此本轮只认领 **1 个主点**：为 `Rank 2 combo_all` 补一张纯历史样本的 **time stability dry-check**；并认领 **1 个紧邻子点**：把这个 verdict 同步到 Rank 2 factor 页与 scout 总览页，形成 reader-facing 落点。

## 开始前检查
### repo / 脏文件
`git status --short` 显示 worktree 里仍有大量与本轮无关的既有脏文件和未跟踪产物（EMA、旧 breakout、trendline、workspace 根目录等）。本轮只碰：

- `scripts/build_volume_supportflip_higherlow_first_verdict.py`
- `scripts/build_trendline_alpha_scout_report.py`
- 新生成的 Rank 2 artifact / site 页面
- 本轮 run log

不混碰其他主题，也不做整仓提交。

### 当前席位状态
- `Paper Seat = EMA`：`waiting_not_due`
- `Live Seat`：默认空席，不强撑 weak challenger
- `Scout Seat`：继续拿主资源，但当前主点必须是**历史样本上的快筛收紧**，不是追最新 bar continuity

## 本轮做了什么
### 主点：新增 `combo_all_time_stability_drycheck.csv`
更新脚本：`scripts/build_volume_supportflip_higherlow_first_verdict.py`

新增 artifact：
- `reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_time_stability_drycheck.csv`

新增检查逻辑（全部基于现有 `trades.csv`，不拉新数据）：
1. 把 `combo_all` 的历史交易按时间切成 `early / mid / late` 三段；
2. 逐段看跨资产平均回报、资产覆盖、false-break 稳定性、每段交易数；
3. 输出一张只回答“它是不是明显依赖单一 regime”的时间稳定性卡。

### 紧邻子点：把 time stability verdict 外显到网页
同步更新：
- `scripts/build_trendline_alpha_scout_report.py`

重新生成：
- `reports/site/factors/scout_volume_supportflip_higherlow_15m/report.html`
- `reports/site/reading/trendline_alpha_scout/report.html`

这样 Jerry 不只在日志/邮件里看到这轮结论，也能在 reader-facing 页面里直接看到 Rank 2 的时间稳定性判断。

## 最小验证
执行：
1. `python3 -m py_compile scripts/build_volume_supportflip_higherlow_first_verdict.py scripts/build_trendline_alpha_scout_report.py scripts/build_plans_site.py`
2. `python3 scripts/build_volume_supportflip_higherlow_first_verdict.py`
3. `python3 scripts/build_trendline_alpha_scout_report.py`
4. `grep -n "time stability" reports/site/factors/scout_volume_supportflip_higherlow_15m/report.html reports/site/reading/trendline_alpha_scout/report.html`

全部通过。

## 关键结果 / hard verdict
`reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_time_stability_drycheck.csv` 给出的当前读法：

- `positive_bucket_floor`：**pass**（`2/3` 时间窗口为正）
- `bucket_trade_floor`：**pass**（每个时间窗口至少 `6` 笔交易）
- `bucket_asset_coverage`：**fail**（最弱窗口只有 `2/3` 资产出现）
- `false_break_time_guard`：**fail**（某一窗口最大 `false-break ratio = 33.33%`）
- `worst_bucket_return_watch`：**watch**（`early` 窗口跨资产平均回报约 `-1.34%`，且 `0/3` 资产为正）

一句话 hard verdict：

**`Rank 2 combo_all` 的时间切片还不够稳：虽然 3 段里有 2 段守住正向，但最早窗口是三资产同步偏弱的负 pocket，且某段假突破占比抬到 33.33%；因此当前更诚实的 desk 读法仍是 `keep-narrower / one more light check`，还不该升格成 `paper candidate`。**

## 这轮结果对 desk 的含义
- 这轮没有推翻 Rank 2 之前的 `friction / shadow-readiness / trade-count honesty`；
- 但它补上了 **Light Stability Pack** 中更关键的一刀：时间稳定性；
- 这使得 Rank 2 的当前读法更完整了：
  - **不是 park**，因为成本、trade-count、跨资产还没把它判死；
  - **也不是 paper candidate**，因为时间切片里仍有明显弱 pocket；
  - **最合适的下一步** 仍是 `one more light check`，而不是 continuity-week / shadow-ready / tiny-live ready。

## 风险 / 边界
- 这仍然只是 **历史样本上的 dry-check**，不是新的 forward continuity；
- 时间切分采用 120d 样本上的 3-way split，是 desk honesty 工具，不是假装更正式的 walk-forward；
- 当前 `Rank 2` 还没有达到“只凭这套证据就进 paper candidate pool”的把握。

## 网页可见落点
- `reports/site/factors/scout_volume_supportflip_higherlow_15m/report.html`
- `reports/site/reading/trendline_alpha_scout/report.html`

## Commit hash（基线）
- `b3c2dc4`

## 如果未提交，原因
当前 worktree 里有大量与本轮无关的既有脏文件和未跟踪文件；为避免混提，本轮只做 selective 构建、网页刷新与 run log 记录，不做提交。
