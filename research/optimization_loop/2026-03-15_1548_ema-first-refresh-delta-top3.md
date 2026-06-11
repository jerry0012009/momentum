# 2026-03-15 15:48 UTC — EMA top-3 first-refresh delta 落表（从 queue 进入真实状态）

## 本轮目标
- 主点：`EMA / PSAR raw alpha focus`
- 紧邻子点：`docs/TODO.md`（把 deployment-facing 未完成项收口为已完成）

## 为什么本轮选这个
- 先看了 `git status --short`、最近 optimization loop 记录与 `docs/TODO.md`。
- 当前最贴近 paper/shadow 继续推进、且仍未完成的 EMA 小任务是：
  - `EMA：沿 first-refresh queue 落下首个真实 refresh / week-1 delta 记录`
- 这条比继续做近义 wording / verdict sync 更接近 deployment：它能把 `day-0 snapshot + first-refresh queue` 变成第一笔真实状态变化，直接帮助判断是否继续往 paper trading/伪实盘推进。

## 本轮改动

### 1) `scripts/build_ema_psar_raw_alpha_report.py`
新增一组 first-refresh delta 产物逻辑（只覆盖 queue top-3 lanes）：

- 新增配置与缓存目录：
  - `EMA_REFRESH_BOOTSTRAP_CACHE_DIR`
  - `EMA_FIRST_REFRESH_TOP_SCOPE_CONFIG`
- 新增函数：
  - `load_stooq_daily_bars(...)`：拉取/回退缓存美股日线（SPY/QQQ/AAPL）
  - `load_first_refresh_member_bars(...)`
  - `summarize_long_only_live_state(...)`（EMA / PSAR 当前信号 + 持仓状态）
  - `describe_scope_live_state(...)`
  - `build_ema_paper_trading_first_refresh_delta(...)`
- 在主流程中新增输出 artifact：
  - `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_first_refresh_delta.csv`
- 在 EMA 页面新增 `Q35`（top-3 first-refresh delta）并把边界段顺延为 `Q36`。
- `相关产物` 列表已追加 `ema_paper_trading_first_refresh_delta.csv`。

这次 top-3 lane 的真实 delta 结果为：
1. `创业板ETF 1d / A股-1d`：
   - `flat_waiting_first_signal -> EMA BUY 1/1`
   - `position -> long_open_since_2026-03-12`
   - `review_action -> keep_primary_start_weekly_review`
2. `美股 1d+1wk（SPY/QQQ/AAPL） / 美股-1d`（front queue）：
   - `flat_waiting_first_signal -> EMA SELL 3/3`
   - `position -> flat_3/3`
   - `review_action -> keep_secondary_then_stricter_front_recheck`
3. `沪深300ETF 1d / A股-1d`（shadow lane）：
   - `flat_waiting_first_signal -> EMA SELL 1/1`
   - `position -> flat`
   - `review_action -> keep_shadow_until_promotion_gate`

### 2) `docs/TODO.md`
将未完成项改为已完成：
- `[x] EMA：沿 first-refresh queue 落下首个真实 refresh / week-1 delta 记录`
- 并补充已完成证据（Q35 + artifact）与当前口径（top-3 lanes 的真实状态变化）。

## 最小验证
已执行：
1. `python3 -m py_compile scripts/build_ema_psar_raw_alpha_report.py scripts/build_plans_site.py`
2. `python3 scripts/build_ema_psar_raw_alpha_report.py`
3. `python3 scripts/build_plans_site.py`

验证要点：
- 新 artifact 已落地：
  - `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_first_refresh_delta.csv`
- EMA 页面已出现：
  - `Q35`（top-3 first-refresh delta）
  - `Q36`（边界）
- `docs/TODO.md` 对应任务已 `[x]`。

备注：构图阶段仍有 matplotlib CJK 字形 warning（历史现象），不影响 CSV/HTML。

## 本轮结论（给 Jerry）
- EMA 线本轮不是继续补“应该怎么 refresh”，而是把 queue 前 3 条 lane 的首笔真实状态写进同一张账本。
- 这让判断更直接：
  - primary（创业板ETF 1d）已经进入真实可续写状态；
  - front-queue secondary（日频美股）当前没有新 long，继续优先 stricter recheck；
  - 沪深300ETF 1d 仍应停在 shadow，不应因 recent 改善偷渡升格。

## 执行层 hygiene 记录
- 本轮先用 `git status --short` 做环境观测；工作区存在大量与本轮无关的历史脏改/未跟踪文件。
- 中途一次 `grep` 因 shell 反引号展开失败（`first-refresh: command not found`），已按要求改用更保守 pattern 重试并完成检查。
- 本轮仅聚焦 EMA first-refresh delta 主线，不把其他脏改混提为本轮成果。

## Git / 提交说明
- 本轮未提交 commit。
- 原因：当前 worktree 脏范围很大，直接提交易混入无关改动；后续若提交，应仅做 selective commit（本轮相关文件）。

## 关键文件
- `scripts/build_ema_psar_raw_alpha_report.py`
- `docs/TODO.md`
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_first_refresh_delta.csv`
- `reports/site/factors/ema_psar_raw_alpha/report.html`
- `reports/site/plans/momentum_todo.html`
