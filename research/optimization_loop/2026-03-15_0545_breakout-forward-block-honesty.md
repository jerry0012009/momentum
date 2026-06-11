# 2026-03-15 05:45 UTC — breakout non-overlap forward-block honesty

## 本轮主点
- **主点：`support_breakout_v0` 的 late-segment / pure-test transferability honesty**
- 按最新 steering，当前不继续补 EMA 近义 board；优先回到更接近 deployment / admission 的 breakout 主缺口。
- 这轮选择把默认 `raw + avoid_fluctuating + ETH+SOL pair-conditioned halfsize` 再压成一刀更硬的 **non-overlap forward evidence**：
  - 不再只看 `10-day / 5-day` overlapping rolling windows；
  - 而是从首个 sizing 触发时点开始，压成更诚实的 non-overlap `5-day` forward blocks；
  - 目的是直接回答：这条默认 sizing candidate 是不是只在一张后段总表里好看，还是在真正往前走时大体还能守住。

## 为什么做这刀
- breakout 线当前正式 verdict 已经是 `shadow-admission queue / one_more_gate`；
- 主缺口已收窄成：
  1. `late-segment / pure-test transferability`
  2. `down tail honesty`
- 上一轮已补 `down tail` 的硬证据（`pure down = 0`），这轮就继续把另一个主缺口压成更 deployment-facing 的 forward honesty。

## 本轮产出

### 1) 新增 artifact：pair-conditioned sizing 的 non-overlap forward blocks
新增：
- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_forward_blocks_20bps.csv`

口径：
- baseline = `avoid_fluctuating` gate-only hourly path
- candidate = `avoid_fluctuating + ETH+SOL pair halfsize`
- 从首个受影响时点开始，按 non-overlap `5-day` blocks 顺推

结果：
- 共 `4` 个 active forward blocks
- 其中 `3/4` 个 block 相对 gate-only 改善
- `1/4` 个 block 小幅回吐，约 `-0.56pp`
- 最强 block：`2026-03-02 ~ 2026-03-07`
  - delta vs gate ≈ `+2.55pp`
  - drawdown improve ≈ `+2.67pp`
- 最弱 block：`2026-02-25 ~ 2026-03-02`
  - delta vs gate ≈ `-0.56pp`
  - drawdown improve ≈ `0.00pp`

### 2) 更新 breakout v0 原型页
更新：
- `reports/site/factors/support_breakout_v0_h24/report.html`

新增一段明确小节：
- “如果把 overlapping walk-forward 再压成更诚实的 non-overlap forward blocks，会发现它有多稳？”

页面口径现在从“后段 active windows 里 3/3 更好”收紧为：
- **大体对，但不是单调稳定**
- 默认 sizing candidate 已可写成 `usable but not monotonic`
- 因此 `late-segment` 证据已从 hopeful 提高到 usable，但**还不够跳过 `one_more_gate`**

### 3) 更新 alpha closure board
更新：
- `reports/site/factors/alpha_closure_board/report.html`
- `scripts/build_alpha_closure_board_report.py`

breakout 行同步收紧为：
- rolling active windows 仍说明触发时方向大体正确；
- 但更硬的 non-overlap `5-day` forward blocks 只做到 `3/4` 改善、`1/4` 回吐；
- 因此当前不能把它升级成 `shadow paper now`。

### 4) 更新源码 TODO 与 plans 入口
更新：
- `docs/TODO.md`
- `reports/site/plans/momentum_todo.html`

在 breakout admission 已完成条目下补一条最新说明：
- 这轮新增的更硬读法是：`3/4` blocks 改善、`1/4` 回吐约 `-0.56pp`
- breakout 默认 sizing candidate 现在应写成 `usable but not monotonic`

### 5) 代码层落地
更新：
- `scripts/build_support_breakout_v0_reports.py`

新增逻辑：
- `summarize_hourly_pair_forward_blocks(...)`
- 输出 CSV artifact
- 将 non-overlap forward blocks 嵌入 breakout v0 报告正文

## 最关键结论（给 admission / deployment 用）
- breakout 默认 sizing candidate 现在已经**不只是**“后半段某张总表更好”的 hopeful slice；
- 但它也还**不是**“只要触发就稳定更好”的可放行规则；
- 最诚实的新结论应写成：
  - **`ETH+SOL pair-conditioned halfsize` = usable but not monotonic**
  - breakout 主线仍停在 **`shadow-admission queue / one_more_gate`**
  - 下一刀仍应优先二选一：
    1. 继续补更长 / 更多 non-overlap forward evidence
    2. 补真正的 `down tail honesty`

## 最小验证
已做：
- `python3 -m py_compile`
  - `scripts/build_support_breakout_v0_reports.py`
  - `scripts/build_alpha_closure_board_report.py`
- 关键短语检查：
  - `non-overlap forward blocks`
  - `3/4` blocks improve / `1/4` block worse
  - `大体对，但不是单调稳定`
  - `usable but not monotonic`

## 本轮改动文件
- `docs/TODO.md`
- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_forward_blocks_20bps.csv`
- `reports/site/factors/alpha_closure_board/report.html`
- `reports/site/factors/support_breakout_v0_h24/report.html`
- `reports/site/plans/momentum_todo.html`
- `scripts/build_alpha_closure_board_report.py`
- `scripts/build_support_breakout_v0_reports.py`

## 邮件发送
- 已执行：
  - `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-auto] breakout 前瞻分块诚实度" --body-file /root/clawd/jerry/momentum/research/optimization_loop/2026-03-15_0545_breakout-forward-block-honesty.md`
- 结果：已发送到默认收件箱 `18810813576@163.com`

## Git / 提交说明
- 当前仓库存在大量与本轮无关的既有脏文件（docs / reports / scripts / 上层 workspace 都有）。
- 为避免误混，本轮**未提交**。
- 若后续需要提交，必须做严格 selective commit；至少应只挑本轮相关的 breakout/TODO/board 文件。
