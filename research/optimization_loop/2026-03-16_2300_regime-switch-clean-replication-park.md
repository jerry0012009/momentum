# 2026-03-16 23:00 UTC — Rank 9 regime-switch clean replication park

## 为什么这轮选这个
- 先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 检查：`Paper Seat = EMA` 当前仍是 `waiting_not_due / due_soon`，所以不能在 `Run 1` 空转。
- 再比较 active Scout 候选的边际价值：
  - `Rank 2 combo_all` 已是 `narrow paper pilot approved`，当前没有真实 `append/review` need；
  - `Rank 7`、`Rank 8` 都已做完 `clean replication + Light Stability Pack` 且已压回 `park`；
  - 因此当前最诚实的主资源动作，是把 **`Rank 9 regime-switch indicator stack / no-buy-downtrend gate`** 从上一轮的 `source intake / clean-room spec` 推到真正的 `clean replication`，尽快给出 `park / paper candidate / narrow paper pilot` verdict。

## 本轮主点
- 主点：`Run 2 / Scout Fast Lane` —— 完成 `Rank 9` 的最小 `clean replication + Light Stability Pack`。
- 紧邻子点：把 `TODO` 顶部战板同步成最新 hard verdict，避免下一轮继续把 `Rank 9` 当成 `clean replication next`。

## 做了什么
### 1) 新增 clean replication 脚本
新增：
- `scripts/build_regime_switch_stack_clean_replication.py`

脚本口径：
- 样本：`Binance 120d / 15m / BTC-USD + ETH-USD + SOL-USD`
- 组件：`EMA20/50`、`RSI14`、`RSI14 的 EMA7`、`PSAR`、`ATR14`
- 四档最小变体：
  - `ema_baseline`
  - `regime_gate_only`
  - `constrained_no_buy`
  - `regime_plus_psar_rsi`
- 执行：`next-bar open | 1 ATR stop | 2 ATR target | 8-bar time stop | 6/10/15/20 bps per side`
- 稳定性包：
  - 时间稳定性
  - 参数稳定性
  - 跨标的稳定性
  - 成本 / 交易数稳定性

### 2) 先跑出 first result，再修一个诚实性 bug
首次运行时，`regime_plus_psar_rsi` 因为 **零交易** 导致 `mean_total_return = 0`，错误地在排序里被选成“winner”。
这不诚实，所以我立刻补了一刀：
- `choose_candidate_variant()` 改成 **零交易版本不能当 winner**；
- 然后重跑整套 clean replication。

这轮因此不是单纯“脚本跑完”，而是把一个会误导 desk judgment 的排序 bug 一并修掉了。

### 3) 生成 reader-facing artifact
落地产物：
- `reports/artifacts/scout_regime_switch_stack_15m/overall_summary.csv`
- `reports/artifacts/scout_regime_switch_stack_15m/asset_summary.csv`
- `reports/artifacts/scout_regime_switch_stack_15m/regime_bucket_summary.csv`
- `reports/artifacts/scout_regime_switch_stack_15m/parameter_neighbor_grid.csv`
- `reports/artifacts/scout_regime_switch_stack_15m/time_stability_drycheck.csv`
- `reports/artifacts/scout_regime_switch_stack_15m/cross_asset_stability_drycheck.csv`
- `reports/artifacts/scout_regime_switch_stack_15m/cost_trade_stability_drycheck.csv`
- `reports/artifacts/scout_regime_switch_stack_15m/clean_replication_meta.csv`
- `reports/site/factors/scout_regime_switch_stack_15m/report.html`

### 4) 同步 desk board
最小更新：
- `docs/TODO.md`
  - `Rank 9` 从 `source intake / clean replication next` 改成 **`park / evidence pool`**；
  - 顶部当前窗口排班改成：`Rank 7 / 8 / 9` 都不再是 active fast-lane 候选；
  - 当前回退链改成：`Scout Seat（新的 paper / repo based 5m / 15m crypto intake next；Rank 2 only on real append/review need） > tiny-live plumbing > 其他维护`。

## 最小验证
已执行并通过：
1. `python3 scripts/build_regime_switch_stack_clean_replication.py`
2. 修正零交易 winner 排序后，再次执行：`python3 scripts/build_regime_switch_stack_clean_replication.py`

关键验证读数：
- `winner_variant = regime_gate_only`
- `verdict_tag = park`
- `regime_gate_only @ 6bps/side`：
  - `mean_total_return ≈ -10.28%`
  - `positive_asset_ratio = 1/3`
  - `mean_trades ≈ 142`
  - `mean_no_trade_ratio ≈ 4.72%`
- `constrained_no_buy @ 6bps/side`：`mean_total_return ≈ -10.93%`
- `ema_baseline @ 6bps/side`：`mean_total_return ≈ -10.83%`
- `regime_plus_psar_rsi`：没有形成可交易样本，不能当成赢家或正证据

`Light Stability Pack` 结果：
- 时间稳定性：`fail`（`0/3` positive buckets）
- 参数稳定性：`fail`（`0/5` configs positive）
- 跨标的稳定性：`fail`（`1/3` assets positive）
- 成本 / 交易数稳定性：`fail`（`0/4` positive cost levels）

## 硬结论（hard verdict）
- **`Rank 9 regime-switch indicator stack / no-buy-downtrend gate` 当前应读作：`park / evidence pool`。**
- 更诚实的说法不是“regime gating 有潜力，只差一点”，而是：
  - `downtrend 禁买` 这条原则在这套 15m crypto clean replication 上 **没有带来足够增量**；
  - 最不差的 `regime_gate_only` 依然是跨资产负、时间切片负、参数邻域负、成本梯度负；
  - `regime_plus_psar_rsi` 甚至因为门槛过窄，直接退化成零交易版本。
- 因此这条线当前不进入 `paper candidate pool`，更不应争 `Live Seat`。

## 对 desk 主线的意义
- 这轮真正减少的是 **Scout fast-lane 的假活跃项**：
  - `Rank 9` 不再占着 `clean replication next` 的位置；
  - 现在 `Rank 7 / 8 / 9` 都已是 `park / evidence pool`；
  - `Rank 2` 继续保留，但只在真实 `append/review` need 时再认领；
  - 所以下一轮如果 `EMA` 还在 `waiting_not_due`，更诚实的默认动作应是 **新的 paper / repo based 5m / 15m crypto intake**，而不是继续磨旧候选近义 wiring。

## 风险 / 边界
- 这仍是 fast-lane clean replication，不是更长窗口、更多资产、更多 exit family 的大样本最终裁决；
- 但按当前 desk 的 admission 规则，这已经足够给出 **`park`**，没必要继续停在“再多研究一轮也许会更好看”的状态；
- 本轮没有给 desk 新增 replacement winner，只是把一个不够格的候选及时清退。

## 下一步建议
- 下一轮 `Run 2` 默认应转去新的 `paper / repo based 5m / 15m crypto` source intake；
- 不要继续把 `Rank 9` 当 active Scout 候选重跑，除非 bot2 明确要求重开并给出新的更强 spec；
- 若 `EMA` close 到点，则按规则临时切回 `Run 1` 做真实 due refresh；否则优先新的 fresh intake，其次才是 `Rank 2` 的真实 append/review。

## 网页可见落点
- `reports/site/factors/scout_regime_switch_stack_15m/report.html`
- `docs/TODO.md`（及其站点镜像 / Control Tower）

## Git / 提交
- 未提交。
- 原因：当前工作区存在大量与本轮无关的脏文件 / 未跟踪产物，不适合安全 selective commit。
