# 2026-03-15 12:35 UTC — breakout scope verdict 压缩页

## 本轮目标
- 主点：`support_breakout_v0 / breakout-short follow-up`
- 选择理由：本轮 steering 明确要求优先处理最接近 deployment / admission 的 breakout 主线；而上一轮已把 `current-sample freeze verdict` 压清，若当前样本仍没有 overturn-scope 的新证据，就不该继续做 micro-slices，而应把 breakout 的 `scope verdict / up-flat biased conditional alpha` 压成 deployment-facing 表达。

## 本轮完成
1. 新增 breakout scope artifact：
   - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_scope_verdict_20bps.csv`
   - 把当前更硬的项目级写法压成 4 行：
     - 当前最诚实的 scope = `up-flat biased conditional alpha / shadow-admission candidate`
     - 当前最不该误读成什么 = `not near-down protective policy`
     - 当前边界 = `BNB/BTC/ETH/SOL × 60m × support_breakout_raw @ h24 × avoid_fluctuating × ETH+SOL pair halfsize`
     - 下一次什么才算有效推进 = `fresh forward/shadow pure-test/down-tail honesty`
2. 在 `reports/site/factors/support_breakout_v0_h24/report.html` 新增 breakout scope 压缩节：
   - 明确写死 breakout 当前不是通用 breakout-short，也不是 near-down protective policy；
   - 明确写死当前更诚实的 deployment verdict 是 `up-flat biased conditional alpha / one_more_gate candidate`；
   - 明确写死 same-sample retrospective slicing 已基本榨干，下一次有效推进必须来自新的 forward / shadow `pure-test/down-tail` 证据。
3. 同步更新 `scripts/build_alpha_closure_board_report.py` 并重生成：
   - `reports/site/factors/alpha_closure_board/report.html`
   - breakout 卡片现在直接写明：scope 已收窄成 `up-flat biased conditional alpha / shadow-admission follow-up`；
   - 下一步明确改成：默认不再补近义 board / wording，而是等待新的 shadow / holdout 真正命中 `pure-test/down-tail`。
4. 更新 `docs/TODO.md`：
   - 已把本轮 scope verdict 压缩页标为完成 `[x]`，并写明当前固定口径。

## 关键结论
- breakout 当前仍可继续保留，但只能被诚实地理解成一条 **窄 scope 的 conditional alpha**；
- 当前证据不支持把它写成 near-down protective policy，也不支持把它重新泛化成更广 breakout-short 模板；
- 当前 blocker 仍然是硬 blocker，而不是 wording 问题：
  - `pure down = 0/100`
  - `48h down-risk zone = 0/109`
  - `future pure-down 48h = 0/44`
- 因此同一段历史样本里的 retrospective micro-slicing 已经不会再改写 verdict；下一次 breakout admission 的有效推进，必须来自新的 forward / shadow `pure-test/down-tail` honesty。

## 最小验证
- `python3 scripts/build_alpha_closure_board_report.py`
- `grep -n "up-flat biased conditional alpha\|avoid_fluctuating_scope_verdict_20bps.csv" reports/site/factors/support_breakout_v0_h24/report.html`
- `grep -n "up-flat biased conditional alpha\|retrospective slicing 已基本榨干\|48h down-risk zone" reports/site/factors/alpha_closure_board/report.html`
- 结果：scope verdict 已出现在 breakout 主报告与 closure board；artifact 也已成功写出并可读。

## Git / 工作区说明
- 本轮开始前 `git status --short` 已显示工作区存在大量脏改动。
- 更重要的是：我本轮触达的 `reports/site/factors/support_breakout_v0_h24/report.html` 与 `reports/site/factors/alpha_closure_board/report.html` / `scripts/build_alpha_closure_board_report.py` 本身就已包含本轮之前累积的未提交 diff，无法安全拆出“只包含本轮改动”的纯净 selective commit。
- 因此本轮**未提交 git commit**，以避免把前序未提交改动混进本轮提交。

## 对下一轮的直接帮助
- breakout 线接下来若还继续，不应再回到更窄 context 分支或新增近义 board；
- 只剩两种诚实动作：
  1. 等新的 forward / shadow 样本真正命中 `pure-test/down-tail`；
  2. 若短期内仍无此类证据，则把主资源切回 EMA 的真实 paper/shadow 运行，而不是继续在 breakout 当前样本里重切。
