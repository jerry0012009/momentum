# bot3 momentum auto（13m）— 2026-03-22 13:41 UTC — pbo-cscv-canonical-links

> 约束：严格按 `docs/TODO.md` 顶部 TRADING DESK BOARD 的 **Next 3 bot3 runs**（Run1→Run2→Run3）。本轮最多：1 个主点 + 1 个紧邻子点；不同时打开多个 Scout 候选。

## Run 1 — EMA due-check first（Paper Seat）

- 执行：`python3 jerry/momentum/scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 结果：**waiting_not_due**（无 `due-now / overdue` lane；require-due 返回 code=2）
  - Crypto 1d+1wk（BTC/ETH/SOL）：约 **10.2h** 后到点
  - 创业板ETF 1d：约 **17.2h** 后到点
  - 贵州茅台 1d+1wk：约 **17.2h** 后到点

结论：不做伪 refresh；按规则立刻切到下一允许动作（优先 Scout Seat）。

## Run 2 — Hosted P3 continuity（低频、事件驱动）

- 观察：`reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json`
  - `run_at_utc=2026-03-22T13:21:20Z`
  - `new_closed_trades_appended=0`

结论：未出现 `refresh 失步 / ledger 爆雷 / open-position 异常 / red-watch` 等 status-changing event，**本轮跳过 Run2**（不做近义健康检查）。

## Run 3 — Scout Seat（主交付：pbo-cscv honesty gate）

### 主点
- `pbo-cscv / deflated sharpe honesty gate`

### 本轮交付（1 个小而硬）
把已有的最小 site 页面补齐“可点击的 canonical reference 链接 + 一句人话定位”，让后续任何人点开页面就能直接追到权威来源，而不是停在“标题列表”。

- 更新页面：`reports/site/factors/pbo_cscv_honesty_gate/report.html`
  - 增补：PBO/CSCV（Bailey et al.）与 DSR（Bailey & López de Prado）的外链入口
  - 增补：一句人话说明：PBO=筛选幻觉概率警报；DSR=给 Sharpe 做 selection-bias 折扣

### 影响与后续
- 这一步不扩候选、不改统计口径，只提高“可信 reference 的可达性”。
- 下一轮若仍要推进该线，优先做：`canonical CSCV/PBO/DSR 离线实现` 的参数/接口冻结（library-grade 前的最小可复现脚本），而不是继续做 proxy/demo。
