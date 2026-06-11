# 2026-03-15 06:18 UTC — breakout down-tail coverage gap (deployment hard gate)

## 本轮主点
- 主点：`support_breakout_v0 / breakout-short follow-up`
- 子点：把 `down regime tail` 从“泛泛担忧”压成可量化的 admission hard gap。

## 选题原因
- EMA 线当前没有新增 forward / holdout honesty 输入，本轮不继续补 EMA 近义 board。
- breakout 线上一轮已补 strict pure-test tail（`+0.77pp`），但 `down-tail` 仍是明确 blocker。
- 本轮目标：交付一刀 deployment-facing 的硬证据，而不是继续改 wording。

## 本轮推进
### 1) 新增 down-tail coverage 审计函数与产物
在 `scripts/build_support_breakout_v0_reports.py` 新增：
- `summarize_pair_regime_coverage_audit(gate_regime_summary, affected_regime_summary)`

新增 artifact：
- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_regime_coverage_audit_20bps.csv`

核心结果（default `ETH+SOL pair halfsize`，基于 gate-only `20bps hourly path`）：
- `down`：gate active hours `100`，gate cumulative `-1.52%`，policy affected `0`，coverage `0/100 = 0.00%`
- `flat`：coverage `14/256 = 5.47%`
- `up`：coverage `28/105 = 26.67%`

结论：当前 blocker 已可写成硬缺口：**down-tail coverage = 0/100**。

### 2) 把 hard gap 落到 breakout admission 主页面
更新：
- `reports/site/factors/support_breakout_v0_h24/report.html`

新增 section：
- `把它翻成 deployment hard-gate：当前 down-tail coverage 到底过线了吗？`

页面固定口径：
- 不是“还想再看一点 down-tail”
- 而是“当前默认 sizing 在 pure down 没有覆盖（0/100），所以 one_more_gate 不能解除”

### 3) 同步 closure board 与 TODO / plans
更新：
- `scripts/build_alpha_closure_board_report.py`
- `reports/site/factors/alpha_closure_board/report.html`
- `docs/TODO.md`
- `reports/site/plans/momentum_todo.html`

同步后的项目级读法：
- breakout 默认 candidate 的 transferability 焦虑已下降（5d/10d/pure-test tail 均未翻负）
- 但 `down-tail coverage` 仍是 deployment hard gap（`0/100`）
- 正式 verdict 继续维持：`one_more_gate`

## 最小验证
已执行：
```bash
python3 -m py_compile /root/clawd/jerry/momentum/scripts/build_support_breakout_v0_reports.py /root/clawd/jerry/momentum/scripts/build_alpha_closure_board_report.py /root/clawd/jerry/momentum/scripts/build_plans_site.py
python3 /root/clawd/jerry/momentum/scripts/build_support_breakout_v0_reports.py
python3 /root/clawd/jerry/momentum/scripts/build_alpha_closure_board_report.py
python3 /root/clawd/jerry/momentum/scripts/build_plans_site.py
```

抽查：
- 新 CSV 存在，包含 `down=0/100` 审计行
- breakout 主页已出现 `down-tail coverage` hard-gate 段落与 `0/100`
- TODO + plans 已同步 `2026-03-15 06:18 UTC` 补充

## git / 提交说明
本轮未提交。

原因：`git status --short` 显示大量与本轮无关的既有脏改动与未跟踪文件；为避免混提，未做 commit。若后续需要提交，应仅做 selective commit。

## 邮件
- 主题：`[momentum-auto] breakout down-tail 覆盖硬缺口`
- 通过默认 SMTP 脚本发送本记录
