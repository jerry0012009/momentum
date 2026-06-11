# EMA rolling / OOS honesty 协议写回决策页

## 为什么这次选这个

这轮继续沿 `EMA / PSAR raw alpha focus` 这条收口线推进，但不做新回测，而是把下一个最关键、也最容易被误做歪的任务先写成明确协议：**如果后面真把 EMA 当主 baseline，rolling / OOS 应该怎么做才算诚实。**

之所以选这个点：
1. `docs/TODO.md` 里这条任务还没完成，但已经足够接近“该动手做真正验证”阶段；
2. 在 13 分钟节奏下，先把协议写死，比仓促补一个半成品 rolling 页更诚实；
3. 这能直接减少后续跑偏风险，也能让 Jerry 在网页上立刻看到“下一步该怎么验 EMA”。

## 做了什么改动

1. 更新 `scripts/build_ema_psar_raw_alpha_report.py`
   - 在 `EMA / PSAR Raw Alpha Focus Report` 中新增一段 **Q11：如果下一步真把 EMA 当主 baseline，rolling / OOS 应该怎么做才诚实？**
   - 明确写死四条纪律：
     - 固定 `EMA9/EMA20`，不再二次调参；
     - 按 `asset × freq` 做 rolling / walk-forward，而不是只看整段累计；
     - 至少同时报告 `gross + 20bps` 近似；
     - 不只问 EMA 是否赚钱，也问它是否仍比 `PSAR` 更像稳定主干。
2. 更新 `docs/TODO.md`
   - 在 `优先补 EMA 的成本 / rolling / OOS / 跨市场稳定性` 这条下补上 `rolling / OOS honesty protocol v1` 的最新进度说明；
   - 这条任务仍保持未完成，因为本轮完成的是**协议收口**，不是正式 rolling / OOS 结果页。
3. 重建可见产物：
   - `reports/site/factors/ema_psar_raw_alpha/report.html`
   - `reports/site/plans/momentum_todo.html`

## 验证 / 证据

### 1) 网页已出现新的 rolling / OOS 协议段

验证命中：
- `reports/site/factors/ema_psar_raw_alpha/report.html` 已出现 `Q11. 如果下一步真把 EMA 当主 baseline，rolling / OOS 应该怎么做才诚实？`
- 原边界段已顺延为 `Q12`

这说明本轮产出已经正式落到网站可见页面，而不是只留在日志里。

### 2) TODO 与 plans 镜像已同步

验证命中：
- `docs/TODO.md` 已出现 `rolling / OOS honesty protocol v1` 进度注；
- `reports/site/plans/momentum_todo.html` 也已同步出现同样说明。

### 3) 当前项目级读法更收紧了

这轮之后，关于 EMA 的下一步默认验证方式更明确：
- 不是再去优化参数；
- 不是只看全样本累计收益；
- 而是要看 rolling 后大多数窗口是否仍为正、坏窗口会不会集中扎堆、以及 `60m` 在 `20bps` 近似下是否还存活。

因此，这轮虽然没新增收益数字，但确实把“下一个关键验证该怎么做”写成了可执行协议。

## 风险 / 边界

1. 这轮是 **验证协议 / 决策页补强**，不是新 OOS 回测；
2. 因此没有新增 rolling 结果、窗口统计或净值曲线；
3. 但在当前高频自动化节奏下，这比仓促做一个不诚实的 rolling 页更合适。

## 下一步建议

最值得接的下一小步就是：
1. 真正做一版 `EMA rolling / walk-forward honesty` 页，优先报告窗口正收益占比与坏窗口聚集度；
2. 若仍想保持极小步，则先只做 `EMA 60m` 在 `gross vs 20bps` 下的 rolling 生存率小切片。

## Commit

本轮**未提交**。

原因：当前 repo worktree 仍然非常脏，而且 `docs/TODO.md`、`scripts/build_ema_psar_raw_alpha_report.py`、`reports/site/factors/ema_psar_raw_alpha/report.html`、`reports/site/plans/momentum_todo.html` 等路径本轮前就已在 dirty 状态；此时做 selective commit 仍无法保证只打包本轮改动。
