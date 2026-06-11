# 2026-03-15 16:38 UTC — EMA active 1d refresh 连续性修复（Crypto / 茅台断流清零）

## 本轮目标
- 主点：`EMA / PSAR raw alpha focus`
- 紧邻子点：`docs/TODO.md` 中最接近 deployment / admission 的未完项
- 选定任务：**先修复 active `1d` lanes 的 refresh 数据连续性（优先 `Crypto-1d` 与 `贵州茅台-1d`）**

## 为什么选这刀
- 先检查了 `git status --short`、最近几轮 optimization loop 记录、`docs/TODO.md` 与 `docs/AUTO_OPTIMIZATION_LOOP.md`。
- 近几轮 EMA 已连续补齐 `candidate spec / operating spec / monitoring board / runbook / first refresh / daily snapshot`，按 steering 不应再继续堆近义 board 页面。
- `Q35b` 已把真正的运行 blocker 暴露出来：`5` 条 active `1d` lanes 里此前约 `live = 1`、`cache fallback = 2`、`data unavailable = 2`。
- 这已经不是 wording 问题，而是 paper/shadow 能否连续记账的运行问题；因此本轮优先把 `Crypto-1d` 与 `贵州茅台-1d` 的 refresh 断流先压掉。

## 本轮改动

### 1) `scripts/build_ema_psar_raw_alpha_report.py`
对 EMA daily refresh loader 做最小必要补强：
- 新增 `normalize_refresh_bars(...)`
  - 把不同来源的 OHLCV 统一整理成 refresh 所需结构。
- 扩展 `load_stooq_daily_bars(...)`
  - 支持直接读取非 `.us` symbol；本轮用于 `600519.cn`。
- 新增 `load_binance_daily_bars(...)`
  - 通过 Binance spot `klines` API 直接拉取 crypto 日线，避免依赖当前环境里缺失的 `yfinance` 模块。
  - 为了保持 `latest_completed_bar_utc` 的诚实口径，若当天 UTC 日线仍在形成中，会主动丢弃未收盘的 open bar。
- 扩展 `load_first_refresh_member_bars(...)`
  - 新增 `stooq_direct` 与 `binance_spot` 两类 refresh source。
- 调整 `EMA_DAILY_REFRESH_SCOPE_CONFIG`
  - `Crypto 1d+1wk（BTC/ETH/SOL）` 改为使用 `BTCUSDT / ETHUSDT / SOLUSDT` 的 `binance_spot` 日线。
  - `贵州茅台 1d+1wk` 改为使用 `stooq 600519.cn` 日线。

### 2) `docs/TODO.md`
将以下 deployment-facing 任务标记为完成：
- `[x] EMA：先修复 active `1d` lanes 的 refresh 数据连续性（优先 Crypto-1d 与 贵州茅台-1d）...`

并补充新的结果口径：
- `refresh_data_unavailable` 红灯已清零
- 当前约为：`live = 3`、`cache fallback = 2`、`data unavailable = 0`

## 产物 / 结果
已刷新：
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_daily_refresh_snapshot.csv`
- `reports/site/factors/ema_psar_raw_alpha/report.html`
- `reports/site/plans/*`

当前 daily refresh snapshot（all active `1d` lanes）核心读数：
- 数据健康：`live = 3`、`cache fallback = 2`、`data unavailable = 0`
- 账位状态：`long_open / mixed_open = 2`，`flat = 3`
- 关键 lane：
  - `Crypto 1d+1wk（BTC/ETH/SOL）`：现已可正常 refresh，`latest_completed_bar_utc = 2026-03-14 00:00 UTC`，`EMA BUY 3/3`，`long_open_3/3`
  - `贵州茅台 1d+1wk`：现已可正常 refresh，`latest_completed_bar_utc = 2026-03-13 00:00 UTC`，`EMA SELL 1/1`，`flat`
  - `创业板ETF 1d` / `沪深300ETF 1d`：仍依赖 frontier cache fallback，但不再是 `data unavailable`

## 验证
已做最小必要验证：
1. `python3 -m py_compile scripts/build_ema_psar_raw_alpha_report.py scripts/build_plans_site.py`
2. `python3 scripts/build_ema_psar_raw_alpha_report.py`
3. `python3 scripts/build_plans_site.py`

结果：
- 构建成功
- EMA 页面中 `Q35b` 已更新为 `live = 3 / fallback = 2 / unavailable = 0`
- 仍有 matplotlib CJK 字形 warning，为历史现象，不影响 CSV / HTML 结论产物

## 结论
- EMA 当前最显性的 deployment blocker 已从“有 2 条 active 日频 lane 完全断流”降到“仍有 2 条 lane 依赖 cache fallback”。
- 这一步的意义不是新增 alpha，而是把 `closest to paper` 的口径从“看上去能跑”推进到“至少 active 日频账本都能连续续写”。
- 若 EMA 下一刀继续推进，默认更该盯：
  1. `创业板ETF 1d` 与 `沪深300ETF 1d` 的 live-source / fallback 依赖是否还能再压缩；
  2. 同一张 snapshot 的连续 market-close refresh 续写，而不是再补近义 runbook/board 文案。

## 执行层 hygiene
- 本轮把 `git status --short` 仅作为环境观测，不把脏 worktree 视为失败条件。
- 当前 repo 存在大量与本轮无关的既有脏改 / 未跟踪文件；本轮只认领 EMA refresh continuity 相关改动与产物，不混提其他线的改动。
- shell 探测阶段发现当前环境缺 `yfinance`，未把整轮判死，而是改用更保守、可直接工作的公开数据源完成同一目标。

## Git / 提交说明
- 本轮未提交 commit。
- 原因：当前工作区存在大量与本轮无关的历史脏改，且相关脚本文件本身已处在演化中的脏状态；此时做 selective commit 风险偏高，容易混入非本轮改动。后续若要提交，应在更干净上下文中严格挑选本轮文件。
