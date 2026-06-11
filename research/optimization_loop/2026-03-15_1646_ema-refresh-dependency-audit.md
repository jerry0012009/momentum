# 2026-03-15 16:46 UTC — EMA 运行依赖审计（live / fallback priority）

## 为什么这次选这个
- 先检查了 `git status --short`、最近几轮 optimization loop 记录、`docs/AUTO_OPTIMIZATION_LOOP.md` 与 `docs/TODO.md`。
- breakout 线当前同一样本里的 retrospective slicing 已基本 freeze；按今天 steering，若没有新的 `pure down / pre-down bridge / thicker pure-test blocks` overturn 证据，就不该继续在同一段历史样本里堆 micro-slices。
- EMA 线这边，近几轮已经连续补完 `candidate spec / operating spec / monitoring board / runbook / day-0 / refresh snapshot / continuity fix`；当前更 deployment-facing 的真实缺口，已经从“断流”收敛成“**哪些 lane 仍靠 fallback，下一刀该先修哪里**”。
- 所以本轮选一个小而完整的运营型切片：把 all active `1d` lanes 的 `live / fallback` 依赖压成一张 audit 表，避免继续补近义 runbook 页面。

## 做了什么改动

### 1) `scripts/build_ema_psar_raw_alpha_report.py`
新增 `build_ema_paper_trading_refresh_dependency_audit(...)`：
- 直接复用现成 `ema_paper_trading_daily_refresh_snapshot`，不新增重型下载；
- 按 `paper_status + data_source + monitor_status` 把 all active `1d` lanes 压成运行优先级表；
- 统一给出：
  - `dependency_status`（`live / cache_fallback / broken`）
  - `ops_priority`
  - `deployment_read`
  - `next_action`
  - `why_it_matters`
- 并输出新 artifact：
  - `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_refresh_dependency_audit.csv`

### 2) EMA 页面
- 在 `reports/site/factors/ema_psar_raw_alpha/report.html` 新增 `Q35c`：
  - 把当前 all active `1d` lanes 的 source-risk / runbook-priority 压成一张 deployment-facing 审计表；
  - 明确区分：
    - `创业板ETF 1d` = `p1_primary_live_source_upgrade`
    - `沪深300ETF 1d` = `p2_shadow_fallback_watch`
    - 美股日频 = `p3_front_queue_honesty_recheck`
    - 茅台日频 = `p4_mid_queue_keep_live`
    - crypto 日频 = `p5_backstop_keep_live`

### 3) `docs/TODO.md`
新增并勾选：
- `[x] EMA：把 active 1d lanes 的 live / fallback 依赖压成 refresh dependency audit（明确下一刀先修哪里）`

并把当前更诚实的 deployment-facing 口径写死为：
- active `1d` lanes 已经 `data unavailable = 0`；
- 但仍有约 `2/5` 条依赖 cache fallback；
- 而且其中就包含唯一 primary pilot `创业板ETF 1d`；
- 所以 EMA 当前更像：`can-run / can-ledger, but still primary source-risk`，还不是“source-risk 也已清零”的更稳 paper-ready。

## 验证 / 证据
已做最小必要验证：
1. `python3 -m py_compile scripts/build_ema_psar_raw_alpha_report.py scripts/build_plans_site.py`
2. `python3 scripts/build_ema_psar_raw_alpha_report.py`
3. `python3 scripts/build_plans_site.py`

结果：
- 新 artifact 已落地：
  - `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_refresh_dependency_audit.csv`
- EMA 页面已出现 `Q35c`
- `plans/momentum_todo.html` 已同步刷新
- 当前 dependency audit 结论为：
  - `创业板ETF 1d`：`frontier_cache_fallback`，`p1_primary_live_source_upgrade`
  - `沪深300ETF 1d`：`frontier_cache_fallback`，`p2_shadow_fallback_watch`
  - `美股 1d+1wk`：`stooq_live`，`p3_front_queue_honesty_recheck`
  - `贵州茅台 1d+1wk`：`stooq_live`，`p4_mid_queue_keep_live`
  - `Crypto 1d+1wk`：`binance_live`，`p5_backstop_keep_live`

## 核心结论
- 这轮之后，EMA 线当前最像 deployment blocker 的已经不是“有没有继续跑”，也不是“还缺不缺一页 runbook”，而是：**唯一 primary pilot 仍依赖 fallback。**
- 证据支持这句结论，因为当前 `5` 条 active `1d` lanes 里虽然 `data unavailable = 0`，但 fallback 仍有 `2/5`，且最该优先保护的 `创业板ETF 1d` 正是其中之一。

## 风险 / 边界
- 这轮推进的是 **运营诚实度 / 运行依赖清单**，不是新增 alpha 证据，也没有改变 EMA 本身的 holdout / rolling verdict。
- `frontier_cache_fallback` 不等于“账本不能跑”，但它意味着 primary lane 还没有进入更稳的 live-source 状态；如果后面继续长时间停在 fallback，就会弱化 `closest to paper` 的运行诚实度。
- 构建过程仍有 matplotlib CJK glyph warning；这是历史现象，不影响 CSV / HTML 结论产物。

## 下一步建议
1. 若下一轮继续 EMA，默认优先把 `创业板ETF 1d` 的 A股日频 fallback 依赖进一步压成可重复 live source，至少先把 primary lane 从 cache-dependent 往 live-dependent 推一步。
2. `沪深300ETF 1d` 的 fallback 风险继续记录，但资源顺序仍排在 primary 之后；它不应抢过 primary source fix。
3. live secondary 这边默认不要再回到 source 修补分支，优先回到 `front-queue honesty / week-1 review / 连续 refresh 续写`。

## 执行层 hygiene
- 本轮把 `git status --short` 仅作为环境观测；当前 worktree 存在大量与本轮无关的历史脏改 / 未跟踪文件。
- 本轮只认领 EMA refresh dependency audit 相关改动，不混提 breakout / Fibonacci / 其他站点历史脏改。
- 这轮复用了现成 refresh snapshot 与 runbook 状态，没有重跑重型研究下载。

## Git / 提交说明
- 本轮未提交 commit。
- 原因：当前 repo 仍有大量与本轮无关的既有脏改，且多个报告/站点文件本身已处于演化中的脏状态；此时做 selective commit 很容易把非本轮改动混进去。后续若要提交，应在更干净上下文里严格挑选本轮文件。