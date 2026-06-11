# 2026-03-23 13:19 UTC · Rank 150 本地 estimator calibration cut

- 严格遵循：`docs/TODO.md` 顶部 `TRADING DESK BOARD`、`docs/AUTO_OPTIMIZATION_LOOP.md`、`docs/BOT2_BOT3_OPERATING_CARD.md`
- 本轮路径：`Scout`
- 本轮范围：只做 **1 个主点 + 1 个紧邻子点**

## 0) 顶板判路
- `Paper / 待开启自动运行 = empty`
- 未出现 `stale / error / refresh drift / ledger/open-position anomaly / red-watch` 的 interrupt 信号
- 因此按 `Next 3 bot3 runs` 继续执行 **Run 1（Rank 150 / 151 二选一最小本地 frozen cut）**
- 上一轮已完成 `Rank 151` 的 frozen A/B/C；本轮补 `Rank 150` 的本地 calibration（顶板默认顺序）

## 1) 主点（Rank 150）
### 动作
完成 `Rank 150 / DFA Hurst persistence gate` 的 **estimator-specific 本地校准切刀**（BTC/ETH/SOL，15m）。

### 产物
- `reports/artifacts/scout_rank150_dfa_hurst_persistence_gate_15m/estimator_calibration_summary.csv`
- `reports/artifacts/scout_rank150_dfa_hurst_persistence_gate_15m/bucket_diagnostics_by_asset.csv`
- `reports/artifacts/scout_rank150_dfa_hurst_persistence_gate_15m/bucket_diagnostics_pooled.csv`
- `reports/artifacts/scout_rank150_dfa_hurst_persistence_gate_15m/estimator_calibration_meta.json`
- 复跑脚本：`scripts/build_rank150_dfa_hurst_calibration_cut.py`

### 关键结果（pooled）
- MC calibration（random walk，80 paths）：
  - `window=128`: `mu=1.4611`, `sigma=0.1602`, `low=1.3810`, `high=1.5412`
  - `window=192`: `mu=1.4871`, `sigma=0.1105`, `low=1.4319`, `high=1.5423`
- `window=192` 分桶 8-bar forward（bps）：
  - `high`: `n=1140`, `mean=+5.82bps`, `share=36.86%`
  - `mid`: `n=916`, `mean=-3.11bps`
  - `low`: `n=1037`, `mean=-1.90bps`

最小结论：`Rank 150` 从“仅 source-intake”推进到“本地可审计 calibration 已落地”，仍为 `keep_P1`，但下一步可以直接复用 `window=192` 做单 family A/B/C honest gate。

## 2) 紧邻子点（不扩任务）
只做邻接诊断，不新开重回测：
- `window=192` 下，`high-persistence` 桶已具备正向 drift 且保留约 `36.9%` 事件量；
- `mid/low` 桶不占优，支持“low-persistence veto / high-persistence allow”的 desk 直觉；
- 因而下一刀不应继续调阈值，而应进入 **1 条 desk-family-specific A/B/C** 验证。

## 3) 简短 scorecard
- `usefulness = 3/3`
- `time_stability = 2/3`
- `cross_asset_stability = 2/3`
- `cost_trade_stability = 1/3`
- `deployability = 2/3`
- `recommended_action = keep_P1`
- `why_now = 顶板 Run 1 明确要求 Rank 150 的 estimator calibration；上一轮已做完 Rank 151，本轮补齐 Rank 150 的最小本地可验证切刀。`
- `main_weakness = 仍是 proxy 级 forward drift 诊断，不是 desk-family 的 post-cost A/B/C 守门结论。`

## 4) 本轮可交付变化
- 完成了可复跑脚本 + 校准 artifact（从“观点”变“可审计数据”）
- 明确下一步最短路径：`window=192` 进入单 family A/B/C（而非继续调 estimator 参数）
