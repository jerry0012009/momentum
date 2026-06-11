# EMA baseline family survivors：先把 60m 剔掉后，还剩什么？

## 为什么这次选这个

这轮继续沿 `EMA / PSAR raw alpha focus` 这条收口线推进，但不再回去补 protocol / gate / closure-copy，而是按今天已经收紧过的口径，交一个真正结果导向的小切片：**既然 `EMA 60m crypto` 已经被 rolling falsification 打进 fail pocket，那如果先把 60m 暂时剔掉，`EMA / PSAR` 的 baseline family 还剩什么？**

之所以选这个点：
1. 这正对应 `docs/TODO.md` 顶部还没完成的 `EMA：改做 baseline family survivors`；
2. 现成 `ema_psar_cost_budget_by_combo.csv` 已经够回答这个问题，不需要新下载或重跑重型回测；
3. 这是一个结果切片，而不是又一轮 wording 补丁，符合当前“EMA 线默认先交结果”的要求。

## 做了什么改动

1. 更新 `scripts/build_ema_psar_raw_alpha_report.py`
   - 新接入 `reports/artifacts/ema_psar_cost_budget_v1/ema_psar_cost_budget_by_combo.csv`；
   - 新增 `build_baseline_family_survivor_slice(...)`，把 `EMA / PSAR` 分别按两桶压缩：
     - `non60m (1d+1wk)`
     - `60m only`
   - 输出新的 durable artifact：
     - `reports/artifacts/ema_psar_raw_alpha/ema_psar_baseline_family_survivors.csv`
2. 更新 `EMA / PSAR Raw Alpha Focus Report`
   - 新增 **Q16：如果明确把 60m 剔掉，EMA / PSAR 的 baseline family 还剩什么？**
   - 这段现在直接把 `non60m vs 60m` 放在同一张表里回答，不再让 Jerry 自己跨多张成本表去拼结论。
3. 更新 `docs/TODO.md`
   - 在顶部 `baseline family survivors` 那条下补入最新结果；
   - 在 EMA 详细收口段再补一条同页结果说明。
4. 重建可见产物
   - `reports/site/factors/ema_psar_raw_alpha/report.html`
   - `reports/site/plans/momentum_todo.html`

## 核心结果

### 1) `EMA non60m` 仍然是一批很厚的 baseline family survivors

来自 `ema_psar_baseline_family_survivors.csv`：

- `EMA non60m (1d+1wk)`：
  - 组合数：`18`
  - gross 正收益覆盖率：`18/18 = 100%`
  - median profit：约 `283.13%`
  - median trades：约 `28.5`
  - positive-only median breakeven cost：约 `2066.8bps`
  - `20bps` 存活：`18/18 = 100%`
  - `50bps` 存活：`17/18 ≈ 94.44%`

这说明如果先不碰 60m，`EMA` 这条线并没有塌掉；反而 `1d / 1wk` 这批组合明显还厚得多。

### 2) `EMA 60m` 与 non60m 已经不是同一层问题

同一张表里的对照：

- `EMA 60m only`：
  - gross 正收益覆盖率：`7/9 ≈ 77.78%`
  - median profit：约 `21.48%`
  - median trades：约 `111`
  - positive-only median breakeven cost：约 `27.5bps`
  - `20bps` 存活：`4/9 ≈ 44.44%`
  - `50bps` 存活：`1/9 ≈ 11.11%`

所以当前更诚实的读法已经变成：
- “EMA 还值不值得继续？” → **值，但看的是 non60m baseline family**
- “EMA 60m 还值不值得继续？” → **当前默认不值，至少不能再拿来当 hopeful baseline 证据**

### 3) `PSAR non60m` 也活着，但更像副线参照

- `PSAR non60m (1d+1wk)`：
  - gross 正收益覆盖率：`18/18 = 100%`
  - `20bps` 存活：`18/18 = 100%`
  - positive-only median breakeven cost：约 `585.0bps`

所以 `PSAR` 在 non60m 里也没死，但当前更自然的角色仍是：
- 作为 `EMA` 的次级对照；
- 或未来 protective layer / faster-reaction 候选；
- 而不是因为 60m overlay 失败，就重新抢回主 baseline 位。

## 这轮后的项目级读法

这轮之后，EMA 线更像被切成两层：
1. **`EMA 60m crypto`**：明确 fail pocket，别再继续围着它找 hopeful 证据；
2. **`EMA 1d / 1wk baseline family`**：仍是一批厚口袋，值得继续作为主 baseline family 去做后续更正式的 honesty / rolling / OOS。

因此，如果后面还继续 `EMA / PSAR` 线，默认资源更该投到：
- `EMA 1d / 1wk` 的 baseline family honesty；
- 而不是再默认去救 `EMA 60m`。

## 验证

执行：
- `python3 /root/clawd/jerry/momentum/scripts/build_ema_psar_raw_alpha_report.py`
- `python3 /root/clawd/jerry/momentum/scripts/build_plans_site.py`

验证命中：
- `reports/site/factors/ema_psar_raw_alpha/report.html` 已出现：
  - `Q16. 如果明确把 60m 剔掉，EMA / PSAR 的 baseline family 还剩什么？`
  - `2066.8bps`
  - `18/18`
- `reports/site/plans/momentum_todo.html` 已同步出现同样结果；
- `reports/artifacts/ema_psar_raw_alpha/ema_psar_baseline_family_survivors.csv` 已生成。

## Commit

本轮**未提交**。

原因：当前 repo worktree 仍然非常脏，而且 `docs/TODO.md`、`scripts/build_ema_psar_raw_alpha_report.py`、`reports/site/factors/ema_psar_raw_alpha/report.html`、`reports/site/plans/momentum_todo.html` 在本轮前就已处于 dirty 状态；此时做 selective commit 仍无法保证只打包本轮改动。
