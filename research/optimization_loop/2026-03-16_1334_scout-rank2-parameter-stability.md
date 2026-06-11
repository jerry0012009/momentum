# 2026-03-16 13:34 UTC｜Scout Seat：Rank 2 combo_all 参数稳定性 dry-check（Light Stability Pack）

## 为什么这次选这个
按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 与 `Next 3 bot3 runs` 执行：

- **Run 1 / Paper Seat**：`EMA` 当前是 `running paper / waiting_not_due`，没有新的 `due-now / overdue` 动作；
- 因此本轮不能空转，自动切到 **Run 2 / Scout Fast Lane**；
- 在同一候选（Rank 2 `combo_all`）上，上一轮已补 `friction / trade-count / time stability`，本轮最合规的一步是补齐 **参数稳定性**，完成 Light Stability Pack 的第 4 项。

本轮只认领：
- **主点**：`combo_all_parameter_stability_drycheck`（历史样本、本地缓存、轻量邻域）；
- **紧邻子点**：把 verdict 同步到 reader-facing 页面（factor 页 + scout 总览页）。

## 开始前检查
### repo / 脏文件
`git status --short` 显示仓库存在大量与本轮无关的既有脏文件（EMA、旧 breakout、trendline、site 页面等）。
本轮仅做 selective 变更：
- `scripts/build_volume_supportflip_higherlow_first_verdict.py`
- `scripts/build_trendline_alpha_scout_report.py`
- Rank 2 对应 artifact / site 页面
- 本轮 run log

### 当前席位状态
- `Paper Seat = EMA`：`waiting_not_due`
- `Live Seat`：默认空席（无新的 promoted candidate）
- `Scout Seat`：继续优先，目标是更快给出 `paper candidate / one more light check / park`

## 本轮做了什么
### 主点：新增参数稳定性 artifact
在 `scripts/build_volume_supportflip_higherlow_first_verdict.py` 中把事件构建参数化，并新增：

- `reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_parameter_stability_drycheck.csv`

参数邻域（local neighbor grid）基于现有 120d/15m 历史样本与本地缓存，围绕 base 配置做轻量扰动：
- `volume_confirm_mult`: `1.1 / 1.2 / 1.3`
- `flip_lookahead_bars`: `2 / 3 / 4`
- `swing_lookahead_bars`: `5 / 6 / 7`

并输出 6 个 gate：
- `positive_neighbor_floor`
- `cross_asset_neighbor_floor`
- `trade_count_neighbor_floor`
- `false_break_neighbor_guard`
- `worst_neighbor_return_watch`
- `best_neighbor_snapshot`

### 紧邻子点：外显到网页
同步更新并生成：
- `reports/site/factors/scout_volume_supportflip_higherlow_15m/report.html`
- `reports/site/reading/trendline_alpha_scout/report.html`

同时发布首页索引：
- `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`

## 关键结果 / hard verdict
`combo_all_parameter_stability_drycheck.csv` 结果：

- `positive_neighbor_floor`：**pass**（`7/7` 配置仍为正）
- `cross_asset_neighbor_floor`：**pass**（`6/7` 配置保持 `>=2/3` 资产为正）
- `trade_count_neighbor_floor`：**pass**（最小 `mean trades / asset = 4.3`）
- `false_break_neighbor_guard`：**pass**（邻域最大假突破率 `8.47%`）
- `worst_neighbor_return_watch`：**pass**（最弱邻域仍约 `+0.03%`）

一句话结论：

**Rank 2 `combo_all` 的参数邻域韧性目前可接受，说明它不是单点调参幻觉；但结合既有 `time stability` 弱 pocket 与 `trade cadence` 稀疏问题，当前 desk 诚实 verdict 仍应是 `one more light check`，暂不升 `paper candidate`。**

## 额外说明（edit fallback 记录）
本轮在给 factor 页插入 parameter stability 卡片时，首次 `edit` 因 **exact text 不匹配**失败；
随后按要求执行 fallback：`read` 定位最新片段后再做稳健替换，改写成功。

## 最小验证
执行并通过：
1. `python3 -m py_compile scripts/build_volume_supportflip_higherlow_first_verdict.py scripts/build_trendline_alpha_scout_report.py`
2. `python3 scripts/build_volume_supportflip_higherlow_first_verdict.py`
3. `python3 scripts/build_trendline_alpha_scout_report.py`
4. `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`

## 网页可见落点
- `reports/site/factors/scout_volume_supportflip_higherlow_15m/report.html`
- `reports/site/reading/trendline_alpha_scout/report.html`
- `https://jp.jerrypsy.top/momentum/`

## 如果未提交，原因
当前 worktree 有大量与本轮无关脏文件；为避免混提，本轮只做 selective 构建、站点刷新与日志/邮件交付，不做提交。
