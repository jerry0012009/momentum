# breakout v0 补做 first-pass 成本敏感性

## 为什么这次选这个

这轮把主点切回 `support_breakout_v0 / breakout-short follow-up`，但不做重型新回测，而是补一个真正能帮助判断“这条线接下来该不该继续往策略层推进”的小验证：**先看最朴素的 breakout v0 在轻微成本下会不会被直接抹平。**

之所以选这个点：
1. 这条线当前已经明确进入 `cost / rolling OOS / non-overlap / environment gate` 的窄 follow-up 阶段；
2. 现有 `reports/artifacts/support_breakout_v0_h24/trades.csv` 已经足够支持一个 first-pass 成本切片，不需要重跑下载或扩样本；
3. 这是一个很小、但比继续补解释文案更接近真实策略判断的问题。

## 做了什么改动

1. 更新 `scripts/build_support_breakout_v0_reports.py`
   - 新增 `cost_sensitivity_table()` 与 `context_net_table()` 两个轻量汇总函数；
   - 基于已有 `v0_breakout trades.csv`，补算 `0 / 10 / 20 / 50bps` 的线性成本敏感性；
   - 额外补了 `20bps` 下按 `split` 与按 `regime` 的净收益摘要。
2. 新增 durable artifacts：
   - `reports/artifacts/support_breakout_v0_h24/cost_sensitivity.csv`
   - `reports/artifacts/support_breakout_v0_h24/cost_sensitivity_20bps_by_split.csv`
   - `reports/artifacts/support_breakout_v0_h24/cost_sensitivity_20bps_by_regime.csv`
3. 重建 `reports/site/factors/support_breakout_v0_h24/report.html`
   - 新增专门一段：`成本 first-pass：扣掉 10 / 20 / 50bps 后，这条线还剩多少？`
   - 页面现在会直接告诉 Jerry：这条线是不是被轻微成本直接吃掉，以及脆弱点更像在什么地方。
4. 更新 `docs/TODO.md`
   - 在 breakout v0 follow-up 那条已收窄的任务下补入最新进度说明；
   - 当前固定口径是：first-pass 成本没有直接抹平这条线，但后段稳定性与环境依赖仍明显需要补 honesty。
5. 重建 `reports/site/plans/momentum_todo.html`
   - 让该进度同步体现在站点 plans 镜像里。

## 验证 / 证据

### 1) first-pass 成本结果

基于 `support_breakout_v0_h24/trades.csv`：

- **gross**：平均单笔约 `1.44%`，累计约 `92.45%`
- **10bps**：累计约 `83.54%`
- **20bps**：平均单笔约 `1.24%`，累计约 `75.03%`
- **50bps**：平均单笔约 `0.94%`，累计约 `51.76%`

这说明：**breakout v0 并不是轻微成本一扣就没了。**

### 2) 真正的脆弱点更像 split / regime

在 `20bps` 下：

- **test split**：累计约 `-3.08%`
- **train**：累计约 `45.64%`
- **validate**：累计约 `24.01%`
- **flat regime**：累计约 `72.27%`
- **up regime**：累计约 `-2.98%`

因此当前更诚实的读法是：
- 问题不只是“成本会不会吃掉 overall gross”；
- 更关键的是这条线在后段与 `up regime` 下已经明显偏弱；
- 所以下一步应优先补 `split / regime honesty`，而不是继续扩 breakout 变体。

### 3) 页面已落地

验证命中：
- `reports/site/factors/support_breakout_v0_h24/report.html` 已出现 `成本 first-pass：扣掉 10 / 20 / 50bps 后，这条线还剩多少？`
- 页面里也已出现 `20bps 下按 split 看` 与 `20bps 下按 regime 看`
- `reports/site/plans/momentum_todo.html` 已同步该最新进度

## 风险 / 边界

1. 这轮仍是 **线性成本近似**，不是逐笔滑点 / 深度 / 资金容量模型；
2. 因此它只能回答“这条线是不是轻微成本一扣就塌”，还不能回答真实成交层面的全部问题；
3. 但它已经足够把下一步优先级收得更准：先补 `rolling / OOS / regime honesty`，再谈是否继续往策略层推进。

## 下一步建议

下一步最值得接的是：
1. 先做 `support_breakout_raw @ h24` 的 `split / regime honesty` 小页，别只看 overall；
2. 若还保持极小步，则可先做 `avoid_fluctuating` 与 `trade_all` 在同一成本口径下的对照。

## Commit

本轮**未提交**。

原因：当前 repo worktree 仍然非常脏，而且 `docs/TODO.md`、`scripts/build_support_breakout_v0_reports.py`、`reports/site/factors/support_breakout_v0_h24/report.html`、`reports/site/plans/momentum_todo.html` 等路径在本轮前就已处于 dirty 状态；此时做 selective commit 仍无法保证只打包本轮改动。
