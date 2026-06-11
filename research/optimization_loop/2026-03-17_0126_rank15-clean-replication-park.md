# 2026-03-17 01:26 UTC｜Scout Seat：Rank 15 clean replication + Light Stability Pack（park）

## 为什么这次选这个
先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 执行：

- `Run 1 / Paper Seat`：`EMA` 已在上一轮完成 crypto due-now refresh，当前是 `waiting_not_due`，不能在 waiting-window 空转；
- `Run 2 / Scout Seat`：当前默认主资源位；
- `Run 3 / tiny-live plumbing`：仅在 `Run 2` 无合格动作时回退。

本轮先比较 active Scout 候选边际价值：

1. `Rank 2` 已是 `narrow paper pilot approved`，当前无新的真实 append/review need；
2. `Rank 7~14` 均已完成 clean replication + Light Stability Pack 且为 `park`；
3. `Rank 15` 仍停在 `source intake / clean-room spec`，是当前唯一可直接推进成 hard verdict 的 fast-lane 候选。

因此本轮主点定为：**把 Rank 15 从 intake 推进到 clean replication + Light Stability Pack，并给出 `promote / park` 的硬结论。**

## 本轮主点（1 个）
- 新增脚本：`scripts/build_sr_regime_switch_clean_replication.py`
- 在不引入新数据源的前提下，复用 `Binance 120d 15m` cache，一次跑完：
  - `touch_or_cross_baseline`
  - `confirm1_outside`
  - `confirm2of3_outside`
  - `retest_hold_reclaim`
- 统一执行口径：`next-bar open | 1 ATR stop | 2 ATR target | 8-bar time stop | 6/10/15/20 bps`。

## 紧邻子点（1 个）
- 将 Rank 15 的状态最小回写到指挥板与 shortlist：
  - `docs/TODO.md` 顶部 `TRADING DESK BOARD`
  - `reports/artifacts/literature/scout_seat_fast_cycle_crypto_shortlist_v1.csv`
- 把 `Rank 15` 从 `clean replication next` 更新为 `park / evidence pool`，避免下一轮继续误占主资源。

## 最小验证 / 执行证据
已执行：

1. `python3 scripts/build_sr_regime_switch_clean_replication.py`
   - 产物成功输出：
     - `reports/artifacts/scout_sr_regime_switch_15m/overall_summary.csv`
     - `.../time_stability_drycheck.csv`
     - `.../parameter_stability_drycheck.csv`
     - `.../cross_asset_stability_drycheck.csv`
     - `.../cost_trade_stability_drycheck.csv`
     - `reports/site/factors/scout_sr_regime_switch_15m/report.html`
2. 回写并复核：
   - `docs/TODO.md`
   - `reports/artifacts/literature/scout_seat_fast_cycle_crypto_shortlist_v1.csv`

## 关键结果（hard verdict）
- **Rank 15 当前 hard verdict = `park / evidence pool`（不进入 paper candidate pool）。**
- `6bps/side` 下相对最不差变体为 `retest_hold_reclaim`，但仍：
  - `mean_total_return≈-1.94%`
  - `positive_asset_ratio=1/3`
  - `mean_no_trade_ratio≈81.73%`
- Light Stability Pack 四项都出现硬 fail：
  - 时间稳定性：`1/3` positive buckets（fail）
  - 参数稳定性：`0/5` 邻域为正（fail）
  - 跨标的稳定性：`1/3` 资产为正（fail）
  - 成本/交易数稳定性：`0/4` 成本档位为正（fail，20bps≈-5.45%）

一句结论：**“多等确认”并没有把这条 support/resistance regime-switch 候选救成可晋升策略，当前应诚实压回 park。**

## reader-facing 落点
- `reports/site/factors/scout_sr_regime_switch_15m/report.html`（已更新）
- `docs/TODO.md` 顶部 `TRADING DESK BOARD`（已同步）

## 风险 / 边界
1. 本轮使用的是既有 `Binance 120d 15m` cache，结论属于 fast-lane 快筛结论，不是长期样本终局；
2. 但当前 board 的目标是快速 `promote/park`，在四项稳定性都硬 fail 的前提下继续延展同线边际价值很低；
3. 下一轮应转向新的 paper/repo-based 15m 候选 intake 或真实 paper append/review need。

## Git / 提交
- 未提交。
- 原因：当前工作区存在大量与本轮无关的脏文件与未跟踪文件，不适合安全 selective commit。
