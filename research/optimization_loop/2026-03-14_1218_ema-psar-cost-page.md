# EMA / PSAR 成本页正式挂回主报告

## 为什么这次选这个

这轮继续沿 `EMA / PSAR raw alpha focus` 这条收口线推进，但不再只停留在独立 artifact 审计，而是把上轮已经得到的 `cost budget` 结果正式挂回主报告。

原因很直接：
1. 这条线当前最缺的是“扣完成本后还值不值得继续往策略层走”的直观表达；
2. 上一轮已经有 `ema_psar_cost_budget_v1` 产物，本轮可以复用，不需要重跑重型下载；
3. 这也是一个足够小、但对 Jerry 判断“EMA 还是不是主 baseline、PSAR 还值不值得单独追”非常有帮助的收口动作。

## 做了什么改动

1. 更新 `scripts/build_ema_psar_raw_alpha_report.py`
   - 新接入 `reports/artifacts/ema_psar_cost_budget_v1/ema_psar_cost_budget_strategy_summary.csv`
   - 新接入 `reports/artifacts/ema_psar_cost_budget_v1/ema_psar_cost_budget_summary.csv`
   - 在主报告中新增专门的 **Q9 成本敏感性段**，把整体与分频率成本空间正式写回页面；
   - 顺手补了一个小稳健性改动：若 `06_btc_ema_psar_equity.png` 已存在，就不再为了重建报告去加载 replication 模块 / 拉 BTC 数据，避免无意义的外部依赖。
2. 重建 `reports/site/factors/ema_psar_raw_alpha/report.html`
   - 页面现在会明确回答：
     - 日/周频成本空间够不够厚；
     - 60m 是否会被手续费明显压扁；
     - 为什么这会进一步支持 `EMA > PSAR` 的当前排序。
3. 更新 `docs/TODO.md`
   - 将 `EMA cost sensitivity page` 标记为完成；
   - 将 `PSAR cost + trade-frequency sensitivity page` 标记为完成；
   - 并把当前正式读法补成结果说明，而不是只留“first-pass audit”进度注。

## 验证 / 证据

### 1) 页面已正式接入成本段

验证命中：
- `reports/site/factors/ema_psar_raw_alpha/report.html` 中已出现 `Q9. 成本一扣之后，这两条线还站得住吗？`
- 边界说明也已顺延成 `Q10`

### 2) 当前正式结论更清楚了

基于已存在的 `ema_psar_cost_budget_v1`：

- **EMA overall**：positive-only median breakeven cost 约 `383.2bps`
- **PSAR overall**：positive-only median breakeven cost 约 `300.9bps`
- **EMA 60m**：positive-only median breakeven cost 约 `27.5bps`；扣 `20bps` 后仍约 `4/9` 组合存活
- **PSAR 60m**：positive-only median breakeven cost 约 `15.4bps`；扣 `20bps` 后只剩约 `2/9`，到 `50bps` 时 `0/9`

这让当前项目级读法更稳：
- `EMA` 仍更适合作为 `raw alpha baseline candidate`
- `PSAR` 更像 `fast reaction / loss-protection candidate`
- 尤其在 `60m` 上，不宜再把 PSAR 当成与 EMA 同级的主 alpha 期待

### 3) 最小技术验证已通过

执行：
- `python3 /root/clawd/jerry/momentum/scripts/build_ema_psar_raw_alpha_report.py`

结果：
- 成功生成报告；
- 期间只有 matplotlib 的中文字体 warning；
- 无阻塞性报错。

## 风险 / 边界

1. 这轮挂回页面的仍是 **基于 gross 汇总结果的线性成本近似**，不是逐笔净值级正式 net 回测。
2. 所以本轮完成的是“成本页 / 读法页”收口，不是“EMA/PSAR 成本问题已经彻底研究完”。
3. 这轮没有继续扩新候选，也没有重跑 OOS / rolling，仍符合当前 `closure-first` 节奏。

## 下一步建议

下一步最值得接的仍是两件事：
1. `EMA` 的 rolling / OOS honesty 页；
2. `EMA + PSAR` 最小组合研究，重点回答“PSAR 当快退出层后，是否比单跑 EMA 更诚实”。

## Commit

本轮**未提交**。

原因：当前 repo worktree 已存在与本轮同文件路径上的在途未提交改动（尤其 `docs/TODO.md`、`scripts/build_ema_psar_raw_alpha_report.py`、`reports/site/factors/ema_psar_raw_alpha/report.html` 早于本轮就已是 dirty），此时做 selective commit 容易把前序改动一并打包，无法保证是干净、可归因的单轮提交。
