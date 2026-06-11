# EMA / PSAR 成本空间 first-pass 审计

## 为什么这次选这个

这轮继续沿 `EMA / PSAR raw alpha focus` 这条收口线推进，优先补最缺的一块：**成本敏感性**。

原因很直接：当前 repo worktree 已经有不少在途改动，若这轮再去碰主报告脚本或大页结构，容易和已有未提交工作缠在一起；但基于现成 `regime_switch_indicator_stack_replication/cross_market_results.csv` 做一刀轻量、可复核的成本空间审计，既能形成新结论，也能给 Jerry 一个更像“该不该继续往策略层走”的判断依据。

## 做了什么改动

1. 新增产物目录：`reports/artifacts/ema_psar_cost_budget_v1/`
2. 基于现有 `cross_market_results.csv`，只抽 `EMA / PSAR` 两条线，补出：
   - `ema_psar_cost_budget_by_combo.csv`
   - `ema_psar_cost_budget_summary.csv`
   - `ema_psar_cost_budget_strategy_summary.csv`
   - `README.txt`
3. 计算口径：
   - `breakeven_roundtrip_cost_bps = profit_pct / nt * 100`
   - 并额外给出线性近似下的 `10 / 20 / 50 bps` 成本后净收益：`profit_pct - nt * (bps / 100)`
4. 在 `docs/TODO.md` 的 `C0-A / C0-B` 下补了最新进度说明，但**没有**把成本任务直接勾掉，因为这轮只是 first-pass audit，还不是正式的成本页 / net backtest 页。

## 验证 / 证据

### 1) EMA 与 PSAR 的日/周频成本空间都还够厚，但 60m 会明显收紧

来自 `ema_psar_cost_budget_summary.csv`：

- `EMA 1d`：median breakeven round-trip cost ≈ `518.1bps`
- `EMA 1wk`：median breakeven round-trip cost ≈ `2916.7bps`
- `PSAR 1d`：median breakeven round-trip cost ≈ `300.9bps`
- `PSAR 1wk`：median breakeven round-trip cost ≈ `877.9bps`

这说明若只看日/周频 first-pass gross 结果，两条线都不是“轻微成本一扣就塌”的状态。

### 2) 真正需要警惕的是 60m，而且 PSAR 比 EMA 更脆

- `EMA 60m`：正 gross 组合的 median breakeven round-trip cost ≈ `27.5bps`
- `PSAR 60m`：正 gross 组合的 median breakeven round-trip cost ≈ `15.4bps`

按同一份 summary 的线性近似：

- 扣 `20bps` 后，`EMA 60m` 仍约有 `4/9` 组合存活（`survive_20bps_share = 0.4444`）
- 扣 `20bps` 后，`PSAR 60m` 只剩约 `2/9` 组合存活（`survive_20bps_share = 0.2222`）
- 到 `50bps` 时，`PSAR 60m` 已是 `0/9` 存活，而 `EMA 60m` 仍约 `1/9`

### 3) 当前最该保留的项目级解释没有变，但现在多了成本侧证据

这轮结果和之前的角色判断是同方向的：

- `EMA` 更适合继续保留为 `raw alpha baseline candidate`
- `PSAR` 更像 `fast reaction / loss-protection candidate`

不是因为 PSAR 完全没收益，而是因为**它的换手更高，60m 成本空间更薄**，所以更难把“表面 gross 收益”稳定保留下来。

## 风险 / 边界

1. 这轮不是逐笔真实净值回放，只是**基于现有 gross 汇总的线性成本近似**；它适合先看“成本空间厚不厚”，不适合替代正式 net backtest。
2. `profit_pct / nt` 是一个很有用的 first-pass 指标，但没有处理滑点异质性、不同市场手续费结构、资金曲线 compounding 细节。
3. 因此这轮结论应读成：**先证明 PSAR 在高频端更容易被成本吞掉，值得优先补正式 net / rolling / OOS 页**，而不是“成本问题已经彻底研究完了”。

## 下一步建议

最值得接的下一小步有两个，优先级如下：

1. **EMA 正式成本页**：把 `gross / 10bps / 20bps / 50bps` 压成一页更像策略决策页的 summary，优先回答“EMA 是否还能稳坐 baseline”。
2. **EMA + PSAR 最小组合研究**：只做最窄问题——若 `EMA` 定主方向、`PSAR` 定更快退出，组合后是否比单跑 EMA 更诚实，而不是更花哨。

## Commit

已做 selective commit：`analysis: add EMA/PSAR cost budget audit`

## 备注

这轮刻意避免去改已在途的主报告脚本，只新增独立 artifact + TODO 进度说明，目的是在脏 worktree 环境下仍留下一个安全、可复核、不会和别的未提交改动打架的真实推进。