# Momentum Auto Optimization Loop — 2026-03-15 07:06 UTC

## 本轮主点（deployment-facing）
- 主点：`support_breakout_v0` 的 `down regime tail` admission 方向，补一刀 **反向 sanity check**：
  - 验证 `hard gap = pure down coverage` 是否可以直接靠 `pure down 一律 0.5x` 解决。
- 紧邻子点：把结论同步到主入口 verdict（`support_breakout_v0` 页 + `alpha_closure_board` + `docs/TODO.md`），避免下轮继续在同类 wording 上打转。

## 为什么选这个点
- EMA 线本轮默认不再补近义 board；除非有新的 forward honesty。
- breakout 线当前 blocker 已明确在 `pure-test / down-tail honesty`。
- 上轮已证明 `down+flat mixed-tail` 是可行候选；本轮需要回答更硬的问题：
  - **能不能直接把 pure down 全砍半，当成 admission 的现成补丁？**

## 本轮执行
1. 在 `scripts/build_support_breakout_v0_reports.py` 中新增并接入 `pure down -> 0.5x` 对照路径（基于默认 `ETH+SOL pair-conditioned halfsize`）：
   - 新增落盘：
     - `avoid_fluctuating_eth_sol_pair_halfsize_down_overlay_hourly_path_20bps.csv`
     - `avoid_fluctuating_eth_sol_pair_halfsize_down_overlay_hourly_summary_20bps.csv`
     - `avoid_fluctuating_eth_sol_pair_halfsize_down_overlay_affected_hours_20bps.csv`
2. 在 `reports/site/factors/support_breakout_v0_h24/report.html` 的 mixed-tail gate 段新增 admission-facing 说明：
   - 明确写出 `pure down` blunt overlay 会带来“回撤更浅但收益回落”的 trade-off；
   - 明确这刀并未触达当前 strict pure-test tail（pure down 仍是 0 小时），因此不是更优 next gate。
3. 同步 `scripts/build_alpha_closure_board_report.py` / `reports/site/factors/alpha_closure_board/report.html`：
   - breakout 证据与 not-yet 段落补入该 sanity check 结论。
4. 更新 `docs/TODO.md`：
   - 在 breakout 主线补充 `2026-03-15 06:59 UTC` 条目（结果+verdict）。
5. 重建页面：
   - `python3 scripts/build_support_breakout_v0_reports.py`
   - `python3 scripts/build_alpha_closure_board_report.py`
   - `python3 scripts/build_plans_site.py`

## 核心结果（本轮新增证据）
默认候选基线（`avoid_fluctuating_eth_sol_pair_halfsize`）：
- cumulative net20：约 `19.90%`
- max drawdown：约 `-9.04%`

若机械叠加 `pure down -> 0.5x`（blunt down overlay）：
- cumulative net20：约 `19.48%`（**回落**，约 `-0.42pp`）
- max drawdown：约 `-7.96%`（改善，约 `+1.08pp`）
- affected pure-down hours：`63`

关键诚实解读：
- 这说明 `down-tail hard gap` 虽然真实存在，但**不能被误读为“pure down 一律半仓”的现成补丁**；
- 当前更像可继续推进的仍是 `down+flat mixed-tail / shadow honesty` 方向，而不是 blunt pure-down overlay。

## 本轮结论（admission）
- breakout 线正式 verdict 继续维持：`one_more_gate`。
- 新证据的作用是**收窄错误方向**：
  - 否掉“pure down 机械半仓就能过关”的捷径；
  - 保留 `mixed-tail protective gate + 更前瞻 shadow honesty` 作为下一步。

## 最小验证
已执行：
```bash
python3 -m py_compile scripts/build_support_breakout_v0_reports.py scripts/build_alpha_closure_board_report.py scripts/build_plans_site.py
python3 scripts/build_support_breakout_v0_reports.py
python3 scripts/build_alpha_closure_board_report.py
python3 scripts/build_plans_site.py
grep -n "pure down 一律砍半\|19.48%\|down+flat mixed-tail / shadow honesty" reports/site/factors/support_breakout_v0_h24/report.html reports/site/factors/alpha_closure_board/report.html docs/TODO.md
```

## 本轮变更文件（相关）
- `scripts/build_support_breakout_v0_reports.py`
- `scripts/build_alpha_closure_board_report.py`
- `docs/TODO.md`
- `reports/site/factors/support_breakout_v0_h24/report.html`
- `reports/site/factors/alpha_closure_board/report.html`
- `reports/site/plans/index.html`
- `reports/site/plans/momentum_todo.html`
- `reports/site/plans/report.html`
- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_down_overlay_*.csv`

## Git / hygiene 记录
- `git status --short` 显示仓库存在大量历史脏改与未跟踪文件（含本轮无关内容）。
- 本轮未提交（no commit）：避免把无关改动混入本轮结果；后续若要提交，应只做安全 selective commit。

## 邮件
- 主题：`[momentum-auto] breakout下行尾部反向校验`
- 通过默认 SMTP 脚本发送本记录。
