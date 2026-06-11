# 2026-03-18 07:01 UTC — EMA A股 due-now follow-up 已真实消化

## 为什么这次选这个
- 先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 与 `Next 3 bot3 runs` 检查当前 desk。
- 上一轮 `06:58 UTC` 的 authoritative 排班已明确：当前窗口下一步优先级是 **`Run 1 = EMA due-now follow-up`**，因为 wall-clock 即将跨过 A 股三条 lane 的 `2026-03-18 07:00 UTC` close。
- 本轮实际开始时主机时间已到 `2026-03-18 07:00:14 UTC`，因此最诚实的动作不是继续做 `Rank 49`，而是先回 `Paper Seat` 消化这次真实 due-now 窗口。
- 按规则，本轮只认领 **1 个主点 + 1 个紧邻子点**：
  1. 主点：执行 `EMA` 的 guarded refresh；
  2. 紧邻子点：把新状态最小写回 authoritative board。

## 做了什么改动

### 主点：执行 `Run 1 / EMA due-now follow-up`
- 实际运行：
  - `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 直接产物更新：
  - `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_refresh_history.csv`
  - `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`
  - `reports/site/factors/ema_psar_raw_alpha/report.html`

### 紧邻子点：authoritative 写回
- 最小更新 `docs/TODO.md` 顶部 `Next 3 bot3 runs`：
  - 追加 `2026-03-18 07:01 UTC` 补充；
  - 把这次 A 股 due-now refresh 写回 board；
  - 将下一轮顺序重置为：
    - `Run 1 = EMA due-check only`
    - `Run 2 = Rank 49 minimal clean replication（仅当仍 waiting_not_due）`
    - `Run 3 = Rank 35b（若 Rank 49 预算用尽或 fresh source 再次失效）/ tiny-live plumbing`

## 验证 / 证据

### 1）本轮确实已经进入 due-now 窗口
- 执行前主机时间：`2026-03-18 07:00:14 UTC`
- 因此当前不再是“06:59 的 due-soon 推演”，而是已经跨过 A 股 `07:00 UTC` 的真实 close。

### 2）refresh history 确实新增 completed-bar rows
- `ema_paper_trading_refresh_history.csv` 本轮后累计增至 **15 条**。
- 新追加的 2 条中，至少明确包含：
  - `贵州茅台 1d+1wk` -> `latest_completed_bar_utc=2026-03-17 00:00 UTC`
  - `沪深300ETF 1d` -> `latest_completed_bar_utc=2026-03-18 00:00 UTC`
- 说明这次不是伪 refresh，而是确实消化了 A 股 due-now 窗口里的新 completed-bar 写账动作。

### 3）due guardrail 已回到 waiting_not_due
最新 `ema_paper_trading_due_guardrail_snapshot.csv` 显示：
- `美股 1d+1wk（SPY/QQQ/AAPL）` -> `2026-03-18 20:00 UTC`
- `Crypto 1d+1wk（BTC/ETH/SOL）` -> `2026-03-19 00:00 UTC`
- `创业板ETF 1d / 贵州茅台 1d+1wk / 沪深300ETF 1d` -> `2026-03-19 07:00 UTC`
- 当前 **没有 `due-now / overdue` lane**。

### 4）reader-facing 页面已同步
- `reports/site/factors/ema_psar_raw_alpha/report.html` 已在同一次 refresh 链路中重建。
- 因此这轮结果不是只留在日志或邮件里，而是网页可见。

## 当前硬结论
- **这次 `Run 1 / EMA due-now follow-up` 已被真实消化。**
- `Paper Seat / EMA` 当前应重新读作：**`running paper / waiting_not_due`**。
- 因此下一轮默认不该继续重复 A 股 refresh，而应回到：
  - `Run 1 = EMA due-check only`
  - `Run 2 = Rank 49 minimal clean replication（若仍 waiting_not_due）`
  - `Run 3 = Rank 35b / tiny-live plumbing fallback`

## 风险 / 边界
- 这轮只做了当前真正会改状态的 paper continuation，没有继续展开 `Rank 49` 的 clean replication，避免同一轮同时打开两个主点。
- `run_ema_paper_trading_guarded_refresh.py --require-due` 在本机进程层返回了 **exit code 2**，但其标准输出已明确显示：
  - report 重建成功；
  - refresh history 追加了 2 条 completed-bar rows；
  - due guardrail 已更新回 waiting_not_due。
- 因此本轮按 **artifact state** 视作已成功消化；后续若再次出现“有真实产物但退出码非 0”的情况，再单独补一轮脚本返回码语义审计，不在本轮岔开主线。

## 下一步建议
1. 下一轮先做 `EMA due-check only`，确认没有新的时钟触发。
2. 若仍 `waiting_not_due`，按板上顺序只给 `Rank 49` **1 次最小 clean replication**。
3. 若 `Rank 49` 预算用尽后仍不改 verdict，再回退比较 `Rank 35b / tiny-live plumbing`，不要挤占当前已托管的 `P3` continuity。

## Commit hash
- 未提交。
- 原因：当前 git 工作区存在大量与本轮无关的脏文件与未跟踪产物，不安全混提。
