# 2026-03-15 17:01 UTC — EMA A股日频 live source 修复（primary/shadow）

- 时间：2026-03-15 17:01 UTC
- 主点：`EMA / PSAR raw alpha focus`
- 紧邻子点：`创业板ETF 1d / 沪深300ETF 1d` 的 A股日频 refresh source

## 1) 为什么本轮选这个

先按要求检查了 repo 状态、`docs/AUTO_OPTIMIZATION_LOOP.md`、`docs/TODO.md`、以及今天最近几轮 optimization loop 记录。

当前 steering 下：
- breakout 线同一样本里的 retrospective slicing 已基本 freeze；若没有新的 `pure-down / pre-down bridge / thicker pure-test blocks`，继续在同一样本里切更细不再是默认优先；
- EMA 线是当前最接近 paper 的对象，但上一轮 `refresh dependency audit` 还明确写着：唯一 primary pilot `创业板ETF 1d` 仍靠 `frontier_cache_fallback`，同组 `沪深300ETF 1d` shadow 也一样。

因此本轮不再补近义 runbook / board，而是直接补 deployment-facing 的真实阻塞：
**把 A股 daily primary/shadow 两条 lane 的 refresh source 从 frontier cache fallback 升成可重复的 live source。**

## 2) 本轮改动

### A. `scripts/build_ema_psar_raw_alpha_report.py`

1. 新增 `Eastmoney` A股日线 loader：
   - 新增 `eastmoney_secid_from_ticker(...)`
   - 新增 `load_eastmoney_daily_bars(...)`
   - 通过 `push2his.eastmoney.com` 拉取 A股日线 K 线；
   - 成功时写入 `reports/artifacts/ema_psar_raw_alpha/refresh_bootstrap_cache/`，失败时再回退到本地 bootstrap cache。

2. 把 EMA paper/shadow 首刷配置里的两条 A股 daily lane 切到新 source：
   - `创业板ETF 1d`：`159915.SZ -> eastmoney_cn_daily`
   - `沪深300ETF 1d`：`510300.SS -> eastmoney_cn_daily`

3. 更新 runbook 里的数据源描述：
   - 不再写成“复用 frontier cache 为主”；
   - 改成“优先走 Eastmoney live；接口不可用时才退到 refresh bootstrap cache”。

4. 让 Q35c 的 deployment 结论按实际 dependency 状态动态切换：
   - 若还有 fallback，就继续写 `primary source-risk`；
   - 若 active `1d` lanes 已全部 live，就改写成“回到连续 refresh / week-1 review / front-queue honesty”。

### B. `docs/TODO.md`

新增并勾选：

- `[x] EMA：把 创业板ETF 1d / 沪深300ETF 1d 的 A股日频 refresh 源从 frontier cache fallback 升成可重复 Eastmoney live`

并写明当前结果口径：
- `ema_paper_trading_daily_refresh_snapshot.csv`
- `ema_paper_trading_refresh_dependency_audit.csv`

现在两条 A股 daily lane 已刷成 `eastmoney_live`；active `1d` lanes 当前约为：
- `live = 5`
- `cache fallback = 0`
- `data unavailable = 0`

### C. `scripts/build_alpha_closure_board_report.py`

做最小必要同步，避免首页继续停留在旧 blocker：
- EMA 状态补成：A股 daily primary/shadow refresh 已切到 live source；
- next step 改成：默认回到真实 `forward refresh / week-1 review`，而不是继续修同类 source 说明。

## 3) 结果 / 关键产物

### 核心产物
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_daily_refresh_snapshot.csv`
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_refresh_dependency_audit.csv`
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_runbook.csv`
- `reports/site/factors/ema_psar_raw_alpha/report.html`
- `reports/site/factors/alpha_closure_board/report.html`

### 本轮得到的 deployment-facing 结论
- `创业板ETF 1d`：`eastmoney_live`
- `沪深300ETF 1d`：`eastmoney_live`
- active `1d` lanes 现在已经是 `5/5 live`
- EMA 当前默认不再卡在“唯一 primary 仍靠 fallback”的 source-risk
- 因此下一刀更诚实的资源顺序应回到：
  1. 连续 `market-close refresh`
  2. `week-1 review`
  3. front-queue honesty / secondary recheck

而不是继续新增同类 source-risk 说明页。

## 4) 最小验证

已做：

1. `python3 -m py_compile scripts/build_ema_psar_raw_alpha_report.py scripts/build_alpha_closure_board_report.py scripts/build_plans_site.py`
2. `python3 scripts/build_ema_psar_raw_alpha_report.py`
3. `python3 scripts/build_alpha_closure_board_report.py`
4. `python3 scripts/build_plans_site.py`

关键验证结果：
- `ema_paper_trading_daily_refresh_snapshot.csv` 中：
  - `创业板ETF 1d = eastmoney_live`
  - `沪深300ETF 1d = eastmoney_live`
- `ema_paper_trading_refresh_dependency_audit.csv` 中：
  - `创业板ETF 1d` 已从 `p1_primary_live_source_upgrade` 变为 `p2_primary_keep_live`
  - `沪深300ETF 1d` 已变为 `p4_shadow_keep_live`
- EMA 页面 Q35c 已改写为：
  - active `1d` lanes 已全部 live；
  - 下一步重点回到连续 refresh / weekly review，而不是 source 依赖。

备注：构建过程中仍有历史性的 matplotlib CJK glyph warning，不影响 CSV / HTML 产物与结论。

## 5) Git hygiene / 提交说明

- 本轮开始前工作区已存在大量与本轮无关的脏改与未跟踪文件；`git status --short` 不能作为失败条件，但它明确说明当前仓库不是干净上下文。
- 本轮未提交 commit。
- 原因：当前 `scripts/build_ema_psar_raw_alpha_report.py`、`scripts/build_alpha_closure_board_report.py`、`reports/site/...` 等文件都处在持续演化链条里，且 repo 中存在大量与本轮无关的历史脏改；此时强做 selective commit 很容易把无关改动一起混入。
- 后续若要提交，应在更干净上下文里只挑本轮相关文件严格 selective commit。

## 6) 对下一轮的直接帮助

这轮不是新增 alpha 证据，而是把 EMA 当前最 deployment-facing 的运行阻塞之一真正拆掉：
**primary / shadow 的 A股 daily 账本现在都能默认走 live source，不再先天卡在 frontier cache fallback。**

所以 Jerry 下一轮若继续 EMA，默认更该问：
- `paper/shadow` 这张账本连续 refresh 之后表现是否还守得住？
- `week-1 review` 会不会把 primary 从 `active_primary` 打回 shadow？
- front-queue secondary 有没有在更严格 honesty 下需要降级？

而不是再继续问“source 还能不能跑”。
