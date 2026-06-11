# EMA 60m + PSAR exit overlay 真实结果切片

## 本轮认领

按最新收紧要求，这轮继续沿 `EMA / PSAR raw alpha focus` 推进，但不再补 protocol / gate / closure-copy，而是直接交第二个真实结果切片：
- 主点：`EMA / PSAR raw alpha focus`
- 具体任务：产出 `EMA 60m + PSAR exit overlay` 对比 `单跑 EMA 60m` 的最小组合结果，并落到网页可见页。

## 为什么选这个

原因很直接：
1. 上一轮已经把 `EMA 60m gross vs 20bps` rolling falsification slice 跑出来了，而且结果已经明显落入 `fail` 档；
2. 当前剩下最值钱的小问题就是：`PSAR` 作为更快退出 / protective overlay，到底能不能把这块最弱口袋救回来；
3. 这正好对应 TODO 里还没交真实结果的 `EMA + PSAR` 最小组合研究。

## 本轮实际推进

### 1) 在 `build_ema_psar_raw_alpha_report.py` 里补了真实组合计算路径（复用本地 cache）

新增内容：
- 本地实现 `psar(...)` 与 `psar_sell_cond(...)`（复用论文同口径参数 `0.02 ~ 0.2`）；
- 在现有 `BTC / ETH / SOL` 60m cache 上，把特征扩成：
  - `EMA9 / EMA20`
  - `PSAR`
  - `prev_high / prev_low`
- 新增 `run_ema_psar_exit_overlay_window(...)`
  - 规则收得很窄：
    - `EMA` 负责开仓与默认持有；
    - 退出条件改成：`EMA sell OR PSAR sell`；
    - `PSAR` 不负责开新仓，不抢主 alpha 位。
- 新增 `build_ema60m_psar_exit_overlay_slice()`
  - 同样使用 `45d window + 15d step`
  - 同样使用 `20bps` 近似
  - 同样复用 `pytrendline_event_validation_v3_crypto_180d/cache`

新增产物：
- `reports/artifacts/ema_psar_raw_alpha/ema60m_psar_exit_overlay_window_metrics.csv`
- `reports/artifacts/ema_psar_raw_alpha/ema60m_psar_exit_overlay_asset_summary.csv`
- `reports/artifacts/ema_psar_raw_alpha/ema60m_psar_exit_overlay_overall_summary.csv`

### 2) 把结果直接落到主报告页

更新：`reports/site/factors/ema_psar_raw_alpha/report.html`
- 新增 **Q14. 真把 `EMA 60m + PSAR exit overlay` 落成结果切片后，它有救到这块最弱口袋吗？**
- 页面现在会直接回答：
  - overlay 有多少窗口真的比单跑 EMA 更好；
  - 它有没有提高 net 正窗口占比；
  - 它是不是只是靠增加交易次数换来更差的成本后结果。

同时顺延章节：
- 原 `Q14 gate` → `Q15`
- 原边界段 → `Q16`

### 3) 同步 TODO / plans

- 更新 `docs/TODO.md`：在 `EMA + PSAR` 最小组合研究下补上真实结果，而不再只停留在协议层；
- 重建 `reports/site/plans/momentum_todo.html`。

## 本轮关键数据点（真实结果）

同一批 `BTC / ETH / SOL` 60m cache、同样 `45d window + 15d step`、同样 `20bps`：

- overlay 只在 `4/30` 个窗口里把 net20 做得比单跑 `EMA` 更好（约 `13.33%`）
- `EMA` 自己在 `20bps` 下至少还有 `2/30` 个正窗口（约 `6.67%`）
- overlay 后正窗口变成 `0/30`
- 整体 median window net20 delta 约 `-6.26pp`
- 整体 median trade delta 约 `+46` 笔
- `0/3` 个资产出现“median delta 为正”
- 各资产 median net20 delta：
  - BTC：`-7.27pp`
  - ETH：`-5.85pp`
  - SOL：`-5.31pp`

## 这组结果意味着什么

当前最诚实的项目级读法是：
1. `EMA 60m` 这块最脆口袋已经 fail；
2. `PSAR exit overlay` 在这批 crypto 60m cache 上也没有把它救回来；
3. 它更像是显著抬高了交易频率，却没有给出足够的成本后改善；
4. 因此当前不支持把 `PSAR` 包装成“EMA 60m 的现成修复层”。

换句话说：
- `PSAR` 仍可以保留为 `fast reaction / protective layer` 的研究角色；
- 但至少在这个最小真实切片里，它还没交出“对最弱口袋有净改善”的证据。

## 最小验证

执行：
- `python3 /root/clawd/jerry/momentum/scripts/build_ema_psar_raw_alpha_report.py`
- `python3 /root/clawd/jerry/momentum/scripts/build_plans_site.py`

结果：
- 报告与 plans 成功生成；
- 新 CSV artifacts 已生成；
- 只有 matplotlib 中文字体 warning，无阻塞报错。

## 下一步建议

这轮之后，EMA 线再往前最合理的动作已经更收紧了：
1. 不要再继续包装 `EMA 60m` 或 `PSAR overlay` 的 hopeful 文案；
2. 如果还继续 `EMA / PSAR` 线，更合理的是把 `60m` 明确视为失败口袋，改问：
   - 是否只保留日/周频作为 baseline 候选；
   - 或者诚实地把这条线从“主 baseline 候选”进一步降回更窄的 research branch；
3. 若还要继续组合验证，下一步应该更像“为什么 overlay 会显著增交易次数”这种诊断，而不是继续默认它会救回来。

## Commit

本轮**未提交**。

原因：当前 repo/worktree 仍包含大量跨轮 dirty / untracked 变更；而本轮涉及的 `docs/TODO.md`、`scripts/build_ema_psar_raw_alpha_report.py`、`reports/site/factors/ema_psar_raw_alpha/report.html`、`reports/site/plans/momentum_todo.html` 等路径在本轮前就已处于 dirty 状态，当前不具备安全 selective commit 条件。
