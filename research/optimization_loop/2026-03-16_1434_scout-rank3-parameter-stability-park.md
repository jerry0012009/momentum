# 2026-03-16 14:34 UTC｜Scout Seat：Rank 3 补齐参数稳定性并给出 `park` 硬结论

## 为什么这次选这个
按 `docs/TODO.md` 顶部 `TRADING DESK BOARD`：

- `Run 1 / Paper Seat`：`EMA` 处于 `waiting_not_due`，无 due-now / overdue 动作；
- 默认切到 `Run 2 / Scout Fast Lane`；
- 只认领 1 个主点 + 1 个紧邻子点：
  - **主点**：给 `Rank 3 third_touch_plus_ema_macd` 补齐 `Light Stability Pack` 里剩余的 **参数稳定性**；
  - **紧邻子点**：把 verdict 同步到 reader-facing 页面与 `TODO` 顶部指挥板。

## 开始前检查
- `git status --short`：工作区有大量与本轮无关脏文件/未跟踪文件；本轮只做 selective 改动，不混提。
- 最近 runs：
  - `2026-03-16_1423_scout-rank3-tradecount-time-stability.md`
  - `2026-03-16_1355_scout-rank2-paper-candidate-admission-memo.md`
- 当前席位：`Paper=EMA waiting_not_due`，`Live=暂空`，`Scout=默认主资源`。

## 本轮动作
1. 修改 `scripts/build_third_touch_ema_macd_first_verdict.py`：
   - 新增产物：
     - `reports/artifacts/scout_third_touch_ema_macd_15m/parameter_stability_drycheck.csv`
   - 扩展 Rank 3 构建链：
     - 参数邻域快检（touch tolerance / third-touch window / EMA slope bars）
     - `parameter_stability_verdict` + bullets 写入 `trial_meta.csv`
     - factor report 新增 `parameter stability dry-check` 卡片
   - 增加稳定性总判定：当 `trade-count/time/parameter` fail 触发强失败时，将 Rank 3 hard verdict 收敛为 `park`。

2. 修改 `scripts/build_trendline_alpha_scout_report.py`：
   - Rank 3 卡片增加 `parameter stability` 行，避免只展示 friction/trade-count/time。

3. 更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`：
   - `Rank 3` 阶段从 `Light Stability Pack` 改为 **`park`**；
   - `Next 3 bot3 runs` 默认顺序改为：`Rank 2 -> Rank 4 -> tiny-live`，`Rank 3` 退到 evidence pool。

## fallback 记录（满足 8.1）
- 对 `TODO.md` 的一次脚本替换出现 `exact block not found`；
- 立即执行 fallback：`read` 重新定位目标片段 -> 再次脚本替换；
- 第二次替换成功完成，未将整轮判失败。

## 最小验证
执行：
1. `python3 -m py_compile scripts/build_third_touch_ema_macd_first_verdict.py scripts/build_trendline_alpha_scout_report.py`
2. `python3 scripts/build_third_touch_ema_macd_first_verdict.py`
3. `python3 scripts/build_trendline_alpha_scout_report.py`
4. `bash scripts/publish_homepage_index.sh`

说明：首次串行命令在长耗时构建后被 SIGTERM 中断（超时链路），随后补跑剩余步骤并成功完成。

## 关键结果 / hard verdict
- `trial_meta` 新结论：
  - **hard verdict**：Rank 3 已补齐最小 Light Stability Pack 后，样本与参数邻域仍过薄，当前应 `park`，不进入 `paper candidate pool`，不争夺 `Live Seat`。
- 参数稳定性快检（新增）：
  - `positive_neighbor_floor`：pass（7/7 positive）
  - `cross_asset_neighbor_floor`：**fail**（0/7 配置达到 >=2/3 正资产）
  - `trade_count_neighbor_floor`：**fail**（0/7 配置达到 >=1 mean trades/asset）
  - `false_break_neighbor_guard`：pass（0.00%）
- 组合读法：虽然单点收益仍为正且假突破低，但跨标的覆盖与交易厚度不达标，故按 desk 纪律 `park`。

## 可部署产物（deployable artifacts）
- `reports/artifacts/scout_third_touch_ema_macd_15m/parameter_stability_drycheck.csv`
- `reports/artifacts/scout_third_touch_ema_macd_15m/trial_meta.csv`（verdict 更新）
- `reports/site/factors/scout_third_touch_ema_macd_15m/report.html`
- `reports/site/reading/trendline_alpha_scout/report.html`
- `docs/TODO.md` 顶部指挥板（Rank 3 park + Next 3 重排）

## reader-facing 落点
- `reports/site/factors/scout_third_touch_ema_macd_15m/report.html`
- `reports/site/reading/trendline_alpha_scout/report.html`
- `reports/site/plans/momentum_todo.html`（通过 publish 刷新）
- `https://jp.jerrypsy.top/momentum/`

## 提交说明
- 本轮未提交 git：当前工作区有大量与本轮无关脏文件，避免混提。
