# breakout v0 的 split / regime honesty 协议写回原型页

## 为什么这次选这个

这轮继续沿 `support_breakout_v0 / breakout-short follow-up` 这条收口线推进，但不再补新数字，而是把上一轮 first-pass 成本结果后面最关键的下一步写成明确协议：**如果真要继续验证 breakout v0，split / regime honesty 到底该怎么做才算诚实。**

之所以选这个点：
1. 上一轮已经证明这条线不是被轻微成本直接抹平；
2. 当前真正的不确定性已经缩到 `test split` 与 `up regime`；
3. 在 13 分钟节奏下，先把验证协议写死，比仓促补一个半成品 rolling/OOS 页更诚实，也更方便 Jerry 直接从网页看到“下一步该怎么验”。

## 做了什么改动

1. 更新 `scripts/build_support_breakout_v0_reports.py`
   - 在 `support_breakout_v0_h24` 页新增专门一段：**如果下一步真做 split / regime honesty，应该怎么做才诚实？**
   - 明确写死五条纪律：
     - 固定当前 `support_breakout_raw @ h24` 与 `24bar hold`，不因局部表现差临时改规则；
     - 至少同时看 `gross + 20bps`；
     - split 侧优先问 `test` 是否持续接近或低于零；
     - regime 侧优先问这条线是否主要只在 `flat` 环境成立、在 `up` 环境明显失效；
     - 若主要靠 `train + flat` 两块把 overall 抬起来，就继续把它当 `conditional alpha / v0 原型`，而不是升格成通用 short。
2. 更新 `docs/TODO.md`
   - 在 breakout follow-up 那条已收窄任务下补入 `split / regime honesty protocol v1` 最新进度说明；
   - 这次不是新开大任务，所以没有新增未勾选项，也没有虚假勾掉任何尚未完成的大项。
3. 重建可见产物：
   - `reports/site/factors/support_breakout_v0_h24/report.html`
   - `reports/site/plans/momentum_todo.html`

## 验证 / 证据

### 1) 原型页已出现新的 honesty 协议段

验证命中：
- `reports/site/factors/support_breakout_v0_h24/report.html` 已出现 `如果下一步真做 split / regime honesty，应该怎么做才诚实？`

这说明本轮产出已经正式落到网页，而不是只停留在日志里。

### 2) TODO 与 plans 镜像已同步

验证命中：
- `docs/TODO.md` 已出现 `split / regime honesty protocol v1` 进度注；
- `reports/site/plans/momentum_todo.html` 也已同步出现同样说明。

### 3) 当前固定口径更清楚了

结合上一轮 first-pass 成本结果：
- `20bps` 下 overall 平均单笔仍约 `1.24%`、累计约 `75.03%`；
- 但 `test split` 累计约 `-3.08%`；
- `up regime` 累计约 `-2.98%`。

因此当前更诚实的下一步已经被写死：
- 不是继续找新 breakout 变体；
- 而是先回答这两个弱点究竟是“可接受的条件性 alpha 特征”，还是已经足够说明它不该继续升格。

## 风险 / 边界

1. 这轮是 **验证协议 / 决策页补强**，不是新回测；
2. 因此没有新增 OOS 窗口统计或净值曲线；
3. 但在当前高频自动循环里，这比仓促补一个不诚实的 split/regime 页更合适。

## 下一步建议

最值得接的下一小步是：
1. 真做一版 `support_breakout_raw @ h24` 的 `split / regime honesty` 小页，优先报告 `gross vs 20bps` 下的 `test` / `up regime` 生存情况；
2. 若仍想保持极小步，则先只做 `avoid_fluctuating` 与 `trade_all` 在同一 `20bps` 口径下的最小对照。

## Commit

本轮**未提交**。

原因：当前 repo worktree 仍然非常脏，而且 `docs/TODO.md`、`scripts/build_support_breakout_v0_reports.py`、`reports/site/factors/support_breakout_v0_h24/report.html`、`reports/site/plans/momentum_todo.html` 在本轮前就已处于 dirty 状态；此时做 selective commit 仍无法保证只打包本轮改动。
