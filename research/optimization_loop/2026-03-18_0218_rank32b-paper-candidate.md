# 2026-03-18 02:18 UTC — Rank 32b 参数稳定性过关，升到 P2 paper candidate

## 为什么这次选这个
- 先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 与 `Next 3 bot3 runs` 执行。
- `Run 1 / EMA` 当前仍是 `running paper / waiting_not_due`：最新 `ema_paper_trading_due_guardrail_snapshot.csv` 显示 A 股下一次 close 在 `2026-03-18 07:00 UTC`、美股在 `2026-03-18 20:00 UTC`、Crypto 在 `2026-03-19 00:00 UTC`，所以这轮不能假装有新的 paper refresh 可做。
- 因此主资源按规则切到 `Run 2 / Scout Seat`。
- 当前 active Scout 只有 `Rank 32b`，而且上一轮已经把它推进到 `P1 weak candidate`；按 `P1` 规则，这轮只允许再做 **1 次便宜诚实检查**，做完就要更偏向 `升格 / park`，不能继续拖成近义说明页。

## 做了什么改动
1. 新增脚本：
   - `scripts/build_rank32b_parameter_stability.py`
2. 基于现有 `BTC/ETH/SOL 120d 15m` cache，固定信号骨架不变（`EMA cross + aligned slope floor`），只改一个参数轴：
   - `slope_floor = 0.0002 / 0.0003 / 0.0004 / 0.0005 / 0.0006`
3. 新增 artifact：
   - `reports/artifacts/scout_rank32b_slope_floor_continuation_15m/parameter_stability_summary.csv`
   - `reports/artifacts/scout_rank32b_slope_floor_continuation_15m/parameter_stability_asset_summary.csv`
4. 新增 reader-facing 页面：
   - `reports/site/factors/scout_rank32b_slope_floor_continuation_15m/parameter_stability_check.html`
5. 更新主报告链接与 desk 板写回：
   - `reports/site/factors/scout_rank32b_slope_floor_continuation_15m/report.html`
   - `docs/TODO.md`

## 验证 / 证据
### 1) EMA paper seat 仍是 waiting_not_due
`reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 当前仍显示：
- 创业板ETF / 贵州茅台 / 沪深300ETF：`next_expected_close_utc=2026-03-18 07:00 UTC`
- 美股 1d+1wk：`2026-03-18 20:00 UTC`
- Crypto 1d+1wk：`2026-03-19 00:00 UTC`

所以这轮不该再重复 paper refresh，而应如实转去 Scout。

### 2) 参数稳定性主结论
`Rank 32b` 主变体在不同 `slope_floor` 邻域下，6bps 成本后都没有塌：
- `0.0002`：`mean_total_return≈48.92%`、`positive_asset_ratio=3/3`、`mean_trades≈125.0`
- `0.0003`：`mean_total_return≈51.53%`、`positive_asset_ratio=3/3`、`mean_trades≈96.0`
- `0.0004`（当前主档）：`mean_total_return≈50.76%`、`positive_asset_ratio=3/3`、`mean_trades≈75.7`
- `0.0005`：`mean_total_return≈51.07%`、`positive_asset_ratio=3/3`、`mean_trades≈59.3`
- `0.0006`：`mean_total_return≈54.04%`、`positive_asset_ratio=3/3`、`mean_trades≈47.7`

### 3) 成本 / 交易数维度没有把它判死
当前主档 `slope_floor=0.0004`：
- `6bps/side≈50.76%`
- `10bps/side≈41.59%`
- `15bps/side≈30.94%`
- `20bps/side≈21.11%`
- 各档 `positive_asset_ratio=3/3`

换句话说，这条线当前更诚实的读法已经不是“只在一个参数点上好看”。

### 4) 为什么这轮把它从 P1 升到 P2
上一轮把它留在 `P1`，主要担心是：
- 会不会参数一碰就碎；
- trade density 会不会稀到不适合 admission。

这轮直接回答了第一条，而且顺带缓解了第二条：
- 参数邻域没有塌；
- 绝对 trade count 已经在 `47.7~125.0` 笔/资产量级，不再是“几乎没有样本”的那种稀疏；
- 因此更诚实的口径是：**它已经满足进入 `paper candidate pool` 的最小条件**。

## 核心结论
- **一句话结论**：`Rank 32b` 这轮通过了最关键的便宜诚实检查，不该继续留在 `P1`，当前更诚实的位置是 **`P2 paper candidate`**。
- **证据怎么支持它**：`slope_floor=0.0002~0.0006` 的参数邻域都保留正 pocket，而当前主档 `0.0004` 在 `20bps/side` 下仍为正、且 `3/3` 资产为正，说明它不是单一热像素，也不只是靠过度稀疏样本撑出来的幻觉。

## 风险 / 边界
- 这轮只补了 `参数稳定性`，没有新追 bar，也没有做新的 `asset-leg scope honesty`。
- `no_trade_ratio` 仍高，说明它依旧是事件型 / 低频触发候选，不适合被误读成高频执行模板。
- 当前最自然的下一步不是直接改成 live，也不是继续磨 wording，而是：**只再给 1 个 truly verdict-changing 的最小检查，回答它该不该升到 `P3 narrow paper pilot`。**

## 下一步建议
- 若下一轮 `EMA` 仍是 `waiting_not_due`，则对 `Rank 32b` 默认只做 1 个最小会改 verdict 的检查：
  - 优先 `asset-leg scope honesty / narrow-paper promotion check`
  - 做完后更偏向 `升到 P3 / 压回 park`
- 若没有新的 hard fail，默认不应再把它拉回 `P1` 或继续留在 purely research 态。

## Commit hash
- 未提交。
- 原因：repo 里有大量与本轮无关的脏文件；当前只安全保留 selective artifact / TODO 局部写回 / site 页面更新，不适合混提。
