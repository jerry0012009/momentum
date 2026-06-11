# 别急着把 `DI dominance` 升级成三条线的 shared hard gate：它更像 setup 内部分层特征，而不是统一否决键
- 时间：2026-03-23 06:55 UTC
- 类型：GitHub 仓库 + 最小复现实验
- 主题类型：filter
- 基础 alpha：breakout_short / fib_retest_long / ema_psar_long（既有 setup）
- 是否可独立复现：否
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：breakout-short / fibonacci / retest_hold / ema / psar / dmi / adx / final-verdict / filter / crypto / 15m
- 证据类型：工程经验 + 本地快检（可复现）

## 1. 这次看了什么
看了仓库 **Herman-Rakale/backtest-ema-crossover-trailing-stop (2025)**。它的可借点不是“又一个 EMA crossover”，而是把 `DMI(+DI/-DI)` 放在触发当下做方向确认：
- 多头：`+DI > -DI`
- 空头：`-DI > +DI`
并叠 `ATR` 止盈止损、trailing stop、cross-switch 反手逻辑。

## 2. 核心结论
- **一句话核心结论：** 对我们当前三条 15m 收口线，`DI dominance` 不适合直接升成 shared hard gate；更像“setup 内部分层特征”。
- **一句话证明方式：** 复用本地 `BTC/ETH/SOL` 的三条 baseline 信号（breakout_short / fib_retest_long / ema_psar_long），按信号时点回填 `+DI/-DI/ADX`，比较 `8-bar signed return` 的 baseline vs `DI 对齐` vs `DI 对齐 + ADX>=20`。
- 在本次样本（`n=198`, 2025-11-17~2026-03-15）里：
  - baseline 全体均值约 **+2.88 bps**；
  - `DI 对齐`后为 **+2.17 bps**（几乎无增量）；
  - `DI 对齐 + ADX>=20` 变为 **-14.39 bps**（明显变差）。
- 分 setup 看：
  - `breakout_short`：`DI 对齐`与 baseline 完全一样（`n=61`），说明这批样本里 DI 方向几乎已被 trigger 隐含；
  - `ema_psar_long`：`DI 对齐`仅小幅改善（`+1.42 -> +1.74 bps`），但加 `ADX>=20`后显著转弱（`-25.92 bps`）；
  - `fib_retest_long`：`DI+ADX`有改善迹象（`+34.51 bps`），但样本仅 `n=11`，证据强度不足。

## 3. 为什么和当前项目有关
- 对 `V3 final-verdict / breakout-short follow-up`：这轮证据在提醒我们，别把 `DI`当成“统一追空放行器”；它对 breakout_short 可能并不新增信息。
- 对 `Fibonacci confirmation / retest_hold`：`DI+ADX`在 fib 子集有潜在价值，但更像 **retest 专用分层**，不该先当 shared gate。
- 对 `EMA / PSAR raw alpha focus`：`DI`可作为弱确认特征保留，但硬阈值化（尤其叠 `ADX>=20`）可能直接削弱短周期表现。

## 3.5 策略拆解（必填）
- 方向属性：顺势（按 setup 方向）
- 基础 alpha：现有三条 baseline（breakout_short / fib_retest_long / ema_psar_long）
- regime：可选 `ADX` 分层（暂不建议先 hard gate）
- filter / veto：`DI dominance`（当前证据更支持 soft score 而非 hard veto）
- risk / sizing / execution overlay：按 `DI margin = |+DI-−DI|` 做轻量仓位缩放，比二元放行更稳妥

## 4. 可复刻的最小实验
- **研究假设：** `DI`在三条线里不是“统一放行键”，而是“分 setup 的条件特征”。
- **一个可计算定义：**
  - `di_align = (+DI>-DI)` for long, `(-DI>+DI)` for short；
  - `di_margin = abs(+DI-−DI)`；
  - 指标窗：`DMI(14)`。
- **最小回测切口：**
  - 资产：BTC/ETH/SOL perpetual proxy；
  - 周期：15m；
  - 样本：最近 120~180 天；
  - 对照：`baseline` vs `+di_align(hard)` vs `+di_margin分层(top40%/mid/bottom)`。
- **先看 2 个指标：**
  1. `8-bar signed return`（均值/中位数）；
  2. `trade retention`（避免“靠砍样本变好”）。

## 5. 风险与保留意见
- 本轮是 proxy 快检，不是完整成交级回放；结论用于“先决定要不要升格”而非最终定案。
- `breakout_short`样本里 DI 方向可能被 trigger 结构预先包含，导致 DI 单独增量被遮蔽。
- `fib_retest_long` 的 `DI+ADX`改善样本过小（`n=11`），必须做滚动窗口和跨阶段复验。

## 6. 来源
1. Herman Rakale. (2025). *backtest-ema-crossover-trailing-stop*. GitHub repository.  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: https://github.com/Herman-Rakale/backtest-ema-crossover-trailing-stop  
   - Repo URL: https://github.com/Herman-Rakale/backtest-ema-crossover-trailing-stop  
   - Code URL: https://raw.githubusercontent.com/Herman-Rakale/backtest-ema-crossover-trailing-stop/main/strategy/adaptive_noise_breakout.py
2. Wilder, J. W. (1978). *New Concepts in Technical Trading Systems*. Trend Research.  
   - Venue: Book  
   - DOI: N/A  
   - Readable URL: https://en.wikipedia.org/wiki/Average_directional_movement_index

## 7. 本地复现产物
- `reports/artifacts/quant_digests/di_dominance_final_verdict_20260323/signal_di_join.csv`
- `reports/artifacts/quant_digests/di_dominance_final_verdict_20260323/overall_summary.csv`
- `reports/artifacts/quant_digests/di_dominance_final_verdict_20260323/setup_summary.csv`
- `reports/artifacts/quant_digests/di_dominance_final_verdict_20260323/asset_summary.csv`
- `reports/artifacts/quant_digests/di_dominance_final_verdict_20260323/meta.json`
