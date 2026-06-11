# 2026-03-15 18:12 UTC｜EMA/PSAR closure board 同步 A股 daily overlay verdict

## 为什么这次选这个
- 先看了 repo 状态、最近 optimization loop 记录、`docs/TODO.md`、以及当前 EMA live-ledger 工件。
- 当前 steering 里，EMA 仍是最接近 `paper trading / 伪实盘` 的对象；但最近两轮已经把 `refresh_clock` 与 `A股 daily overlay runbook audit` 做出来了。
- 这时如果继续补近义 spec / board，边际价值很低；更值得做的是把**最新的 deployment-facing verdict 直接同步到项目级首页入口**，让 Jerry 在首页就能看清：
  1. EMA 仍是 closest-to-paper；
  2. `PSAR overlay` 虽对 `创业板ETF 1d` 有帮助，但**还不能焊进默认 runbook**。

## 本轮主点 / 子点
- 主点：`EMA / PSAR raw alpha focus`
- 紧邻子点：`alpha_closure_board` / baseline compare 的 deployment-facing 表达同步

## 做了什么改动
1. 修改 `scripts/build_alpha_closure_board_report.py`
   - 把 EMA 卡片的 `status / role / evidence / not_yet / next` 同步到最新 runbook overlay verdict。
   - 明确写死：
     - `PSAR overlay` 当前**只配 primary pocket 的 shadow-protective 观察位**；
     - 不能因为 `创业板ETF 1d` 一格改善，就偷渡成整个 A股 daily 的默认 protective layer。
2. 同步刷新 closure board 里的 baseline comparator 导出：
   - `reports/artifacts/alpha_closure_board/structure_vs_ema_baseline_v1.csv`
   - 把 `EMA baseline family` 一行补成：当前 baseline seat 继续由 EMA 持有，A股 daily overlay overall 仍是 `mixed`，所以不支持把 PSAR 额外焊成默认保护层。
3. 重新生成项目级 closure 页：
   - `reports/site/factors/alpha_closure_board/report.html`

## 本轮固定下来的更硬口径
- `EMA` 仍是项目默认 `raw alpha baseline / paper candidate`。
- `PSAR overlay` 的最新 A股 daily 读法应收敛成：
  - `创业板ETF 1d`：约 `75%` holdout 改善，median net20 delta 约 `+2.00pp`；
  - `沪深300ETF 1d`：约 `25%` 改善，median net20 delta 约 `-1.51pp`；
  - 两格合并后 overall 改善占比约 `50%`、median delta 约 `-0.38pp`。
- 因此项目级首页现在更诚实的写法是：
  - `PSAR` 目前**只配作为 primary pocket 的 shadow protective 观察位**；
  - **不是** `A股 daily` 默认 runbook overlay；
  - 更不能拿它替代 `沪深300ETF 1d` 的 promotion gate。

## 验证 / 证据
最小必要验证：
1. `python3 -m py_compile scripts/build_alpha_closure_board_report.py`
2. `python3 scripts/build_alpha_closure_board_report.py`

结果：
- 成功生成：
  - `reports/site/factors/alpha_closure_board/report.html`
  - `reports/artifacts/alpha_closure_board/paper_live_promotion_gate_v1.csv`
  - `reports/artifacts/alpha_closure_board/structure_vs_ema_baseline_v1.csv`
- 当前 closure board 首页入口已能直接回答：
  - EMA 为什么仍坐 baseline seat；
  - PSAR overlay 为什么还只能停在 `shadow-protective` 观察位。

## 为什么这轮算有效推进
- 这轮不是再造一页近义 board，而是把**最新 runbook-level verdict 提到项目级总入口**。
- 对 Jerry 来说，这直接减少了一层判断摩擦：现在在首页就能看到“EMA 该继续按 live ledger 往前跑；PSAR overlay 先别焊进默认规则”。
- 这也避免下一轮又把同一件事在 EMA 子页里讲了一遍、但 closure 首页还停留在旧读法。

## 执行层 hygiene
- `git status --short` 只作为环境观测，不作为失败条件。
- 当前 worktree 仍有大量与本轮无关的历史脏改 / 未跟踪文件；本轮没有混做 breakout / Fibonacci，也没有回去 reopen `pytrendline_event_validation_v3`。

## 提交情况
- 本轮未提交。
- 原因：仓库里存在大量与本轮无关的既有脏改；且本轮触达的 `build_alpha_closure_board_report.py / alpha_closure_board` 本身也处在持续演化区，当前不适合安全做 selective commit，避免把历史改动一起打包。