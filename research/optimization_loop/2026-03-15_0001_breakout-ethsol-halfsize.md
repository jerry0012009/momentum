# breakout：ETH+SOL residual pair 的最小条件化 sizing 切片

## 本轮认领

- 主点：`support_breakout_v0 / breakout-short follow-up`
- 具体任务：在 `avoid_fluctuating` 已经落地、且 residual weakness 已收窄到 `ETH+SOL` 两仓口袋的前提下，交一版**最小条件化 sizing** 结果切片，验证它是否比继续诊断更值钱。

## 为什么选这个

这一刀正好对应 `docs/TODO.md` 里 breakout Top 3 的旧第 3 条，而且属于“已经知道弱点在哪里之后，必须交一版动作验证”的自然下一步：
1. `confirm_1` 是否抢位已经基本看清；
2. `avoid_fluctuating` 已证明有帮助，但 `test` / residual pocket 仍没完全修好；
3. 最新 pair/context 诊断已把问题进一步收窄到 `ETH+SOL` 两仓小时。

所以这轮不再继续补 wording，而是直接回答：**如果只对这一个 residual pair 做很克制的 halfsize，会不会有净改善？**

## 做了什么改动

1. 更新 `scripts/build_support_breakout_v0_reports.py`
   - 新增 `apply_hourly_pair_sizing_policy(...)`
   - 新增 `summarize_hourly_pair_sizing_compare(...)`
   - 在现有 `avoid_fluctuating` hourly path 基础上，新增一条最小 sizing 变体：
     - 仅对 `ETH-USD + SOL-USD` 的两仓小时做 `0.5x` 半仓
     - 不动其它 pair / 不动其它并发桶
2. 新增 durable artifacts
   - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_hourly_path_20bps.csv`
   - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_hourly_summary_20bps.csv`
   - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_affected_hours_20bps.csv`
   - `reports/artifacts/support_breakout_v0_h24/raw_gate_eth_sol_pair_halfsize_compare_20bps.csv`
3. 更新网页 / 总入口
   - `reports/site/factors/support_breakout_v0_h24/report.html`
     - 新增一节：**如果只做一刀最小条件化 sizing：把 gate 后的 ETH+SOL 两仓残余口袋降到半仓，会发生什么？**
   - `reports/site/factors/alpha_closure_board/report.html`
     - breakout 卡片 evidence / next 已同步到这次最小 sizing 结果
   - `reports/site/plans/momentum_todo.html`
4. 更新 `docs/TODO.md`
   - 将 breakout Top 3 旧第 3 条标记为完成 `[x]`
   - 并把下一棒收窄成：
     - `ETH+SOL pair-conditioned halfsize` 的更严格 holdout / walk-forward 复核
     - 以及是否需要再收窄成更克制的 `context-conditioned sizing`

## 核心结果

### 1) 这刀 halfsize 是真的有净改善，不只是“看起来更稳”

同样在 `20bps hourly mark-to-market` 框架下：

- `raw_v0` hourly path：约 `14.04%`
- `avoid_fluctuating` hourly path：约 `15.46%`
- `avoid_fluctuating + ETH+SOL pair halfsize`：约 `19.90%`

所以，相比 gate-only，这刀最小条件化 sizing 带来的路径改善约为：
- **`+4.44pp` cumulative net return**

### 2) 回撤也有同步改善，而不是单纯拿风险换收益

- gate-only max drawdown：约 `-9.97%`
- pair-conditioned halfsize 后：约 `-9.04%`

也就是说，这刀不是“收益更高但更抖”，而是：
- **回撤约再收窄 `0.93pp`**

### 3) 它改动范围其实很小，说明 residual pocket 不是到处都是

这次被动到的只有：
- `44/398` 个活跃小时
- 约占总活跃小时的 `11.06%`

而且被压的那块 residual pair pocket 自己的条件累计也从：
- 约 `-7.17%`
- 收窄到约 `-3.61%`

这说明 breakout 线的后续动作已经不该再停留在“继续找 weak pair 在哪”，而是可以开始做更有针对性的 sizing honesty。

## 当前更诚实的项目级读法

这轮之后，breakout 线的口径进一步收紧为：
- `raw` 仍是 breakout-short 主原型；
- `confirm_1` 不值得继续抢位；
- `avoid_fluctuating` 是有帮助的最小环境 gate；
- 而在 gate 已落地后，**最像样的 next step 已经不是继续换变体，而是对 residual pair 做更正式的 sizing / holdout honesty**。

换句话说：
- 当前已不只是“知道 ETH+SOL 是问题口袋”；
- 而是已经证明：**对这块口袋下手，确实能带来可见净改善。**

## 验证

执行：
- `python3 /root/clawd/jerry/momentum/scripts/build_support_breakout_v0_reports.py`
- `python3 /root/clawd/jerry/momentum/scripts/build_alpha_closure_board_report.py`
- `python3 /root/clawd/jerry/momentum/scripts/build_plans_site.py`

验证命中：
- `reports/site/factors/support_breakout_v0_h24/report.html` 已出现：
  - `如果只做一刀最小条件化 sizing...`
  - `44/398`
  - `11.06%`
  - `15.46% -> 19.90%`
  - `-9.97% -> -9.04%`
- `reports/site/factors/alpha_closure_board/report.html` 已同步新的 breakout evidence / next
- `reports/site/plans/momentum_todo.html` 已同步新的 Top 3
- `reports/artifacts/support_breakout_v0_h24/` 下已生成新的 `eth_sol_pair_halfsize` artifacts 与对照表

## Commit

本轮**未提交**。

原因：当前 repo worktree 仍然很脏，而且 `docs/TODO.md`、`scripts/build_support_breakout_v0_reports.py`、`scripts/build_alpha_closure_board_report.py`、对应站点输出与 artifact 路径在本轮前就已处于 dirty / untracked 混合状态；此时做 selective commit 仍无法保证只打包本轮改动。
