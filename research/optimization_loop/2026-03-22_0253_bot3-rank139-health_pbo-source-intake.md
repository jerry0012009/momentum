# bot3 auto optimization loop @ 2026-03-22 02:53 UTC

目标：严格按 desk board 的 Next 3 bot3 runs 执行（Run1→Run2→Run3）。本轮遵守：最多 1 个主点 + 1 个紧邻子点；不同时打开多个 Scout 候选。

---

## Run 1 — EMA due-check first（Paper Seat）
结论：**waiting_not_due（无 due-now / overdue lane）**，因此不做伪 refresh，立即切到 Scout Seat。

证据（脚本输出摘要）：
- `Crypto 1d+1wk（BTC/ETH/SOL）`：waiting_not_due，约 **23.6h** 后到点
- `创业板ETF 1d (active_primary)`：waiting_not_due，约 **1.3d** 后到点
- `贵州茅台 1d+1wk`：waiting_not_due，约 **1.3d** 后到点

执行命令：
```bash
python3 jerry/momentum/scripts/run_ema_paper_trading_guarded_refresh.py --skip-build --require-due
```
（exit code=2 属于预期：require-due 且无 due-now）

---

## Run 2 — Rank139(P3) hosted narrow paper pilot 低频健康检查（只做 1 件事）
主点：**健康检查 = ops 刷新新鲜度 + no_event_timeout / retention 是否“爆雷”**。

### 2.1 刷新新鲜度
- `narrow_paper_pilot_refresh_clock.json` 显示：`generated_at_utc = 2026-03-22 02:32 UTC`
- 当前检查时刻：`2026-03-22 02:53 UTC`
- 结论：**更新很新（约 21 分钟）**，refresh 链条没有停摆。

### 2.2 关键监控字段是否异常
读取 `narrow_paper_pilot_monitoring_board.csv`（9 行，覆盖 BTC/ETH/SOL × 三个 baseline setups）：
- 多数 setup 的 `no_event_timeout_rate` 在 **0%~27.3%** 区间，未出现“timeout 失控”
- `retention` 多数在 **16.7%~50%**（符合 confirm gate 的稀疏保守语义；仍需后续结合交易条数增长观察稳定性）

读取 `summary_by_arm.csv`（总体口径）：
- `thr_mult=0.8, arm=confirm_same_dir_only`：
  - retention_vs_base ≈ **0.305**
  - mean_net@6bps ≈ **+0.005363**
  - positive_ratio_net ≈ **0.6047**
  - **no_event_timeout = 0.0**（很关键：确认同向 gate 下 timeout 没有堆积）

结论：**Rank139(P3) pilot 当前没有“爆雷”信号，继续按 hosted pilot 监控口径运行即可**（不再做近义研究对比）。

---

## Run 3 — 只选 1 个：pbo-cscv / deflated sharpe honesty gate（source intake）
紧邻子点：只做一个小交付：**锁定 1 条权威参考 + 人话摘要**。

### 3.1 权威参考（建议作为 source of truth）
- **Bailey, Borwein, López de Prado, Zhu (2016)** — *The Probability of Backtest Overfitting*（提出 **PBO** 与 **CSCV** 框架：用“组合式交叉验证”估计策略/参数在回测里被挑中后，落到样本外变差的概率）。

（辅助参考，用于解释 deflated sharpe 的来源/动机）：
- **Bailey & López de Prado (2014)** — *The Deflated Sharpe Ratio*（在考虑 **样本长度有限 + 非正态/厚尾 + 多重试验/数据挖掘** 后，对 Sharpe 做折扣校正）。

### 3.2 人话摘要（放进 momentum 的“横向诚实守门层”语义）
我们现在的问题不是“某个 rank 策略在历史里看起来更好”，而是：
- 我们在 **多个候选/多个参数/多个 gate** 里挑“看起来最好”的那一个时，**有多大概率只是撞到了回测噪声**？

PBO/CSCV 给出的实用回答：
- 把样本切成多个小段，做 **组合式的 train/test 划分**；
- 在每个 train 上“选最好”的策略/参数；
- 再看它在对应 test 上的表现分布；
- 得到一个 **PBO（过拟合概率）**：
  - PBO 高 → 你看到的“好成绩”更可能是筛选偏差（selection bias）
  - PBO 低 → 你选出来的东西在 test 上更可能保真

把它落到本项目里（bot3 的意图）：
- **PBO/deflated Sharpe 不替代现有 scorecard**（mean_net@6bps、retention、no_event_timeout 等），而是加一层“横向诚实折扣”：
  - 当某个候选提升主要来自“挑出来的最好窗口/最好参数”，但 CSCV 显示 test 很不稳定 → 直接降级/park
  - 当候选提升在 CSCV 多数组合里仍存在 → 才允许进入更贵的 clean replication / promoted pilot

### 3.3 下一步（不在本轮展开）
- minimal implementation 方向：在 scout scorecard 增加 1~2 列：
  - `pbo_cscv`（或 `pbo_flag`）
  - `deflated_sharpe`（或 `dsr_flag`）
- 实施时先做 **离线小工具**（不侵入主 pipeline），只对 1 个候选（pbo-cscv honesty gate 自己）跑通。

---

## 本轮后续动作（由系统步骤执行）
- 刷新 homepage index
- 发送中文邮件（附件/正文=本日志）
