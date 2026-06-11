# EMA rolling / OOS 先写死最小 falsification slice

## 为什么这次选这个

这轮继续沿 `EMA / PSAR raw alpha focus` 这条收口线推进，但不急着直接开 rolling 回测，而是把一个更小、也更容易避免跑偏的问题先写死：**如果下一步只先做一个最小 rolling / OOS 切片，应该先做哪一块。**

之所以选这个点：
1. 当前 `EMA` 这条线剩下的主任务就是 rolling / OOS honesty，但如果不先收窄，很容易一上来又铺成“大而全”；
2. `docs/TODO.md` 里这条任务还没完成，但协议已经有了，缺的是“第一刀先切哪里”的明确口径；
3. 在 13 分钟节奏下，把最小 falsification slice 写进网页和 plans，比仓促补一个半成品 rolling 页更诚实。

## 做了什么改动

1. 更新 `scripts/build_ema_psar_raw_alpha_report.py`
   - 在 `Q11. 如果下一步真把 EMA 当主 baseline，rolling / OOS 应该怎么做才诚实？` 里新增一条：
     - **如果只先做一个最小切片，默认优先先做 `EMA 60m gross vs 20bps` 的 rolling / walk-forward。**
   - 同时把理由直接写回页面：
     - `EMA 60m` 是当前最脆的一块；
     - first-pass 成本里，它的 positive-only median breakeven cost 约 `27.5bps`；
     - 扣 `20bps` 后只剩约 `4/9` 组合存活；
     - 所以它最适合先当 baseline 的 falsification slice，而不是先去挑最好看的日/周频窗口。
2. 更新 `docs/TODO.md`
   - 在 `优先补 EMA 的成本 / rolling / OOS / 跨市场稳定性` 这条最新进度下，补上这个 first-slice 默认口径；
   - 说明这条任务仍未完成，但后续真正做 rolling 页时，第一刀该切哪里已经写死。
3. 重建可见产物：
   - `reports/site/factors/ema_psar_raw_alpha/report.html`
   - `reports/site/plans/momentum_todo.html`

## 验证 / 证据

### 1) 主报告已出现新的 first-slice 口径

验证命中：
- `reports/site/factors/ema_psar_raw_alpha/report.html` 已出现：
  - `如果只先做一个最小切片：优先先做 EMA 60m 的 gross vs 20bps rolling / walk-forward`

这说明本轮不是只在日志里提建议，而是已经把下一步默认动作写进了网页。

### 2) 当前为什么先看 EMA 60m 更合理

这轮固定下来的读法是：
- 日/周频虽然更厚，但不适合作为最小 falsification slice；
- `EMA 60m` 的成本空间最薄：positive-only median breakeven cost 约 `27.5bps`；
- 扣 `20bps` 后只剩约 `4/9` 组合存活；
- 所以如果它在 rolling / walk-forward 下也快速塌掉，就能更早回答“EMA baseline 幻觉是不是主要靠更厚样本撑起来”。

### 3) TODO / plans 镜像已同步

验证命中：
- `docs/TODO.md` 已同步这条 `first falsification slice` 进度说明；
- `reports/site/plans/momentum_todo.html` 也已同步出现同样口径。

## 风险 / 边界

1. 这轮是 **验证顺序 / 切片优先级收口**，不是新 rolling 回测；
2. 因此没有新增窗口统计或净值曲线；
3. 但它确实把“下一轮该从哪里先下刀”写成了站点可见的明确指令，能降低后续把 rolling / OOS 做散的风险。

## 下一步建议

下一步最值得接的就是：
1. 真做一版 `EMA 60m gross vs 20bps` 的 rolling / walk-forward 小切片；
2. 优先报告窗口正收益占比、坏窗口是否扎堆、以及 `gross -> 20bps` 后存活窗口比例。

## Commit

本轮**未提交**。

原因：当前 repo worktree 仍然非常脏，而且 `docs/TODO.md`、`scripts/build_ema_psar_raw_alpha_report.py`、`reports/site/factors/ema_psar_raw_alpha/report.html`、`reports/site/plans/momentum_todo.html` 在本轮前就已处于 dirty 状态；此时做 selective commit 仍无法保证只打包本轮改动。
