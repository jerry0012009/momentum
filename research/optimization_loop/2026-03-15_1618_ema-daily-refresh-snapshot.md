# 2026-03-15 16:18 UTC — EMA 全 active 1d lanes 的 daily refresh snapshot 落表

## 本轮目标
- 主点：`EMA / PSAR raw alpha focus`
- 紧邻子点：`docs/TODO.md`（把本轮 deployment-facing 小任务显式勾选）

## 为什么这次选这个
- 先看了 `git status --short`、最近几轮自动优化记录与 `docs/TODO.md`。
- 当前 steering 明确要求：EMA 线不要再堆 admission/operating/monitoring 近义层，而要继续补 **更接近 paper/shadow 实际运行** 的动作。
- 上一轮已完成 top-3 first-refresh delta（Q35），但 Jerry 还不能一眼看出“**所有 active 日频 lanes 今天到底在不在跑**”。
- 所以本轮选一个小而完整的 deployment 切片：把 top-3 扩到全部 active `1d` lanes，落成一张 daily refresh snapshot，并把数据健康（live/fallback/断流）写进账本。

## 做了什么改动

### 1) `scripts/build_ema_psar_raw_alpha_report.py`
本轮新增并接入：
- `EMA_DAILY_REFRESH_SCOPE_CONFIG`
  - 覆盖 active `1d` lanes：`创业板ETF 1d`、`美股 1d+1wk（美股-1d）`、`Crypto 1d+1wk（Crypto-1d）`、`贵州茅台 1d+1wk（A股-1d）`、`沪深300ETF 1d`。
- `load_yfinance_refresh_bars(...)` / `load_stooq_daily_bars(...)`
  - 统一支持 live 拉取 + 本地 cache fallback，并把来源模式写回账本（`stooq_live` / `*_fallback` / `load_failed_no_cache`）。
- `classify_refresh_data_health(...)`
  - 把 refresh 数据健康分为：`ok_live_refresh` / `ok_refresh_with_cache_fallback` / `refresh_data_unavailable`。
- `build_ema_paper_trading_daily_refresh_snapshot(...)`
  - 基于 day-0 snapshot 生成全 active `1d` lanes 的 daily refresh 快照。
  - 若某 lane 出现 `load_failed_no_cache`，自动落红：
    - `monitor_status = refresh_red_data_unavailable`
    - `review_action = pause_refresh_fix_data_source`

并新增 artifact：
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_daily_refresh_snapshot.csv`

### 2) EMA 页面（deployment-facing 可见性）
- 在 `reports/site/factors/ema_psar_raw_alpha/report.html` 新增 `Q35b`：
  - 主题：**把 top-3 首刷扩到全部 active 1d lanes 的 daily refresh snapshot**。
  - 页面直接给出 live/fallback/断流计数，以及 long/flat 计数。
  - 将新 artifact 加入“相关产物”列表。

### 3) `docs/TODO.md`
新增并勾选：
- `[x] EMA：把 top-3 首刷扩到全部 active 1d lanes 的 daily refresh snapshot（看真实数据源与账位状态）`
- 说明该任务产物与当前口径（不再补近义 board，直接看 runbook 是否真实续跑）。

## 验证 / 证据
已执行最小必要验证：
1. `python3 -m py_compile scripts/build_ema_psar_raw_alpha_report.py scripts/build_plans_site.py`
2. `python3 scripts/build_ema_psar_raw_alpha_report.py`
3. `python3 scripts/build_plans_site.py`

结果：
- 新 artifact 已落地：
  - `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_daily_refresh_snapshot.csv`
- EMA 页面已出现 `Q35b`，并展示 all active `1d` lanes snapshot。
- `TODO` 页已同步新 `[x]` 条目（plans 站点已重建）。

当前 snapshot（5 条 active `1d` lanes）读数：
- 数据健康：`live = 1`，`cache fallback = 2`，`data unavailable = 2`
- 仓位：`long_open/mixed_open = 1`，`flat = 4`
- 关键状态：
  - `创业板ETF 1d`：`EMA BUY` + `long_open_since_2026-03-12`（fallback 但可续写）
  - `美股 1d+1wk（日频）`：`SELL 3/3` + `flat_3/3`（live）
  - `Crypto 1d+1wk（日频）`、`贵州茅台 1d+1wk（日频）`：`load_failed_no_cache`，已自动落 `pause_refresh_fix_data_source`
  - `沪深300ETF 1d`：`SELL` + `flat`（fallback）

## 风险 / 边界
- 本轮是 **运营层 refresh 可见性** 推进，不是新增 alpha 证据本身。
- 目前有 2 条日频 lane 数据断流（crypto / 茅台），这不是“策略失败”结论，但会阻断其 paper/shadow 连续记账；必须先补数据源稳定性。
- 图表阶段仍有 matplotlib CJK 字形 warning（历史现象），不影响 CSV/HTML 结论产物。

## 下一步建议
1. EMA 主线下一刀优先：修复 `Crypto-1d` 与 `茅台-1d` refresh 数据源，先把 `pause_refresh_fix_data_source` 清零，再谈 promote/demote。
2. 若数据源修复后，继续按同一张 snapshot 连续写 `market-close` refresh（避免回到近义文案补丁）。
3. breakout 线按既定 steering 保持：除非出现非零 pure-down / pre-down bridge 新证据，否则不再回到 micro-slices。

## 执行层 hygiene 记录
- 本轮把 `git status --short` 仅作为环境观测；当前 worktree 存在大量与本轮无关脏改/未跟踪文件。
- 本轮只声明 EMA daily refresh snapshot 相关改动，不混提其他线的历史脏改。

## Git / 提交说明
- 本轮未提交 commit。
- 原因：当前仓库存在大范围无关脏改，无法安全保证“只包含本轮改动”的纯净提交；后续若提交应使用严格 selective commit。
