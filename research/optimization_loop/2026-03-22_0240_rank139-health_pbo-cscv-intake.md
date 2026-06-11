# bot3 auto optimization loop (13m)

- time: 2026-03-22 02:40 UTC
- board: `docs/TODO.md` > TRADING DESK BOARD > Next 3 bot3 runs

## Run 1 — EMA due-check first（require-due）

执行：
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`

结果（脚本退出码=2，符合 waiting_not_due 语义）：
- 当前 **没有 due-now / overdue lane**，不允许伪造 refresh。
- 最靠前 next due：
  - Crypto 1d+1wk（BTC/ETH/SOL）≈ **21.3h** 后到点
  - 创业板ETF 1d ≈ **28.3h** 后到点
  - 贵州茅台 1d+1wk ≈ **28.3h** 后到点

结论：Paper Seat 真实 `waiting_not_due` → **立刻切 Scout Seat（不空转）**。

---

## Run 2 — Rank 139(P3) hosted narrow paper pilot 低频健康检查（只做 1 件事）

检查对象：
- `reports/artifacts/scout_rank139_cusum_event_bar_confirm_veto_15m/narrow_paper_pilot_monitoring_board.csv`

观测：
- 文件 mtime：`2026-03-22 02:32:36 UTC`（说明 ops/产物仍在更新）
- rows=9（BTC/ETH/SOL × 3 setups）
- `no_event_timeout_rate`：max≈**0.278**（当前不算爆雷）
- `retention`：min≈**0.118**（BTC-USD / ema_psar_long @0.8 留存很低，属于需要盯的早期风险信号）

本轮结论：
- **继续 keep 该 hosted lane**（没有出现明显“timeout 极端飙升 / retention 崩塌到不可用 / 全臂负贡献”这类爆雷信号）。
- 下一次低频检查优先看：
  1) BTC-USD/ema_psar_long retention 是否持续 <0.15；
  2) breakout_short 的 timeout 是否继续上行并拖累 mean_net。

---

## Run 3 — 只选 1 个（pbo-cscv honesty gate）

### 本轮交付选择
按 board 允许动作：只做 **source intake（锁定 1 个权威参考 + 人话摘要）**。

### 权威参考（当前可用性说明）
我尝试抓取 SSRN（Cloudflare 403），因此本轮先把“可执行的框架+引用信息”写入，下一轮再补可直链的开放版本（arXiv/作者主页/镜像）。

建议作为本项目的 anchor reference（需后续补可访问链接）：
- **CSCV / PBO**：Bailey, Borwein, López de Prado, Zhu — *The Probability of Backtest Overfitting*（核心：用 **Combinatorially Symmetric Cross-Validation** 估计“被挑中的 best strategy 在真实 OOS 上翻车”的概率）
- **Deflated Sharpe**：Bailey & López de Prado — *The Deflated Sharpe Ratio*（核心：在“多次试错/非正态/样本小”的情况下，对 Sharpe 做折扣，避免把噪声当 alpha）

### 人话摘要（落到 momentum scout scorecard 的可执行口径）
这条 honesty gate 想解决的不是“再榨一点收益”，而是：
- 当我们同时试了很多 arms / 参数 / 变体时，**best-in-sample 的 Sharpe 很可能只是运气**；
- 需要一个轻量的“诚实守门层”，在 Scout 阶段就把“可能过拟合”显式打出来。

最小接线建议（不改主回测口径，只做 scorecard 增补列）：
1) 在每个 scout 对比表里，记录 `n_trials`（本轮实际比较了多少 arms/参数/候选）。
2) 增加两列：
   - `deflated_sharpe`：对 `sharpe_oos` / `sharpe_is`（取你现在最稳定的定义）做折扣，输出“多重比较后的保守 Sharpe”。
   - `pbo_risk_flag`：用 CSCV（或简化版：rolling split 的 best-rank 翻车频率）输出一个 0/1 或 low/med/high。

**先跑起来的策略**：
- 即使我们暂时不实现完整公式，先把 `n_trials` 与 “OOS rank reversals / 翻车频率”以启发式方式写入 scorecard，也能让 Scout 的叙事更诚实。

下一步（Next run 候选动作，二选一即可）：
- A) 补齐可公开访问的 1 个 PDF 链接（arXiv/作者主页/镜像）并写成 `research/strategy_review/pbo_cscv_honesty_gate.md`；
- B) 做 minimal implementation：给 `reports/artifacts/*/scorecard.csv` 增补 `n_trials + pbo_risk_flag`（先启发式），避免拖慢当前 pipeline。
