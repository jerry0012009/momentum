# breakout：shadow paper admission verdict 收口

- 时间：2026-03-15 04:22 UTC
- 本轮主点：`support_breakout_v0 / breakout-short follow-up`
- 紧邻子点：`closure / board` 的统一 `paper admission` 入口同步

## 先检查了什么

1. 查看 `git status` 与最近 optimization loop 记录，确认：
   - repo 里存在大量与本轮无关的既有脏改动；
   - 最近两轮已经分别完成：
     - `2026-03-15_0210_breakout-pair-walkforward-honesty.md`
     - `2026-03-15_0413_ema-paper-candidate-spec.md`
2. 回看 `docs/TODO.md` 当前 deployment-facing 接力棒，确认最直接未收口项就是：
   - `breakout：把 raw + avoid_fluctuating + pair-conditioned sizing 压成更硬的 admission verdict`
3. 复核现有 breakout 证据包，避免再做一轮泛泛 wording：
   - `avoid_fluctuating_capital_allocation_equal_weight_hourly_summary_20bps.csv`
   - `avoid_fluctuating_eth_sol_pair_halfsize_hourly_summary_20bps.csv`
   - `avoid_fluctuating_eth_sol_pair_halfsize_holdout_split_20bps.csv`
   - `avoid_fluctuating_eth_sol_pair_halfsize_walkforward_windows_20bps.csv`
   - 以及现有 `support_breakout_v0_h24/report.html` / `alpha_closure_board/report.html`

## 本轮实际推进

### 1) 把 breakout 线压成显式 admission verdict，而不再停留在“看起来接近 shadow paper”

更新：
- `scripts/build_support_breakout_v0_reports.py`
- `reports/site/factors/support_breakout_v0_h24/report.html`

新增页面段落：
- `admission verdict：这条 breakout 线今天够不够进 shadow paper？`

这次明确写死的 verdict 是：
- **当前已进入 `shadow-admission queue`**
- 但正式 verdict 仍是 **`one_more_gate`**
- **不是** `shadow paper now`

同时把 admission question 直接压成表格回答：
- scope 是否明确？→ 已明确到 `BTC/ETH/SOL/BNB, 60m, support_breakout_raw @ h24, avoid_fluctuating + ETH+SOL pair halfsize`
- 组合/资金曲线 honesty 还是不是主 blocker？→ **不是主 blocker**，因为 raw / gate-only / pair-conditioned 的统一 hourly path、1-slot、equal-weight 都已补齐 first-pass
- 默认 sizing candidate 是否已足够稳定？→ **还不够**，active rolling windows 里方向是对的，但改善集中在后半段，pure `test` 仍偏薄
- 最终 verdict → `one_more_gate`

### 2) 把“到底差哪一刀”收窄成可执行的 deployment-facing 判断

本轮没有再扩新候选，也没有继续纠缠更窄 context branch，而是把最关键缺口排位写死：

1. **主缺口 = `late-segment / pure-test transferability`**
   - `ETH+SOL pair-conditioned halfsize` 在 policy 真正触发的 rolling windows 里是 `3/3` 同时改善；
   - 但 pure `test` 真正被修到的目标 pocket 只有约 `5` 个小时；
   - 对应条件累计改善约 `+0.76pp`，方向对，但还不够厚。
2. **第二风险 = `down` regime tail`**
   - gate-only 口径下 `down` 累计仍约 `-1.52%`；
   - 说明这条线还没被洗成“任何环境都能放心 shadow 跑”的对象。
3. **不是主缺口 = portfolio honesty**
   - 因为这层已经不只是 per-asset 幻觉：
     - raw `20bps hourly path` 约 `14.04%`
     - `avoid_fluctuating` 约 `15.46%`
     - `ETH+SOL pair-conditioned halfsize` 约 `19.90%`
     - max drawdown 约从 `-12.03% -> -9.97% -> -9.04%`

这一步的意义是：
- breakout 线现在不再只是“继续研究看看”；
- 而是已经能明确回答 Jerry：
  - **这条线离 shadow paper 还差什么？**
  - **差的主要不是组合层，而是默认 sizing rule 的迁移性证明。**

### 3) closure / TODO 入口同步

更新：
- `scripts/build_alpha_closure_board_report.py`
- `reports/site/factors/alpha_closure_board/report.html`
- `docs/TODO.md`
- `reports/site/plans/momentum_todo.html`

已把以下事项打勾：
- `[x] breakout：把 raw + avoid_fluctuating + pair-conditioned sizing 压成更硬的 admission verdict`

同步后的统一口径：
- `EMA / PSAR` = `closest to paper`
- `breakout` = `needs one more gate`
- `Fibonacci` = `park / archive`

其中 breakout 的说明已进一步收窄为：
- 已进入 `shadow-admission queue`
- 但当前更硬 verdict 仍是 `one_more_gate`
- 主缺口是默认 sizing candidate 的迁移性，而不是“有没有统一资金曲线”

## 为什么这轮算真实推进

这轮不是再补泛泛 closure wording，而是把 breakout 线当前最接近 deployment 的问题——

> “今天到底能不能把它当 shadow paper policy 开始盯？”

压成了一个明确 verdict：
- **还不能放行**，但也**不该退回普通研究想法**；
- 它现在最诚实的位置是：**shadow-admission queue / one_more_gate**。

这直接帮助 Jerry 判断：
- 是继续往策略/伪实盘推进，还是先停；
- 若继续，下一刀该补哪里，而不是继续在 raw / confirm / context 分支里来回打转。

## 最小验证

已执行：

```bash
python3 -m py_compile scripts/build_support_breakout_v0_reports.py scripts/build_alpha_closure_board_report.py scripts/build_plans_site.py
python3 scripts/build_support_breakout_v0_reports.py
python3 scripts/build_alpha_closure_board_report.py
python3 scripts/build_plans_site.py
```

命中检查：
- `reports/site/factors/support_breakout_v0_h24/report.html` 已出现 `admission verdict：这条 breakout 线今天够不够进 shadow paper？`
- 页面内已出现 `one_more_gate`、`shadow-admission queue`、`迁移性` 等关键结论
- `reports/site/factors/alpha_closure_board/report.html` 已同步写入 breakout 的更硬 verdict
- `docs/TODO.md` / `reports/site/plans/momentum_todo.html` 已将该 breakout admission 项改为 `[x]`

## Git / 提交说明

本轮**未提交**。

原因：
1. 本轮开始前 repo 已存在大量与本轮无关的既有脏改动与未跟踪产物；
2. 本轮涉及文件（尤其 `docs/TODO.md`、两份脚本、多份站点页）本身也处在持续累计修改链上；
3. 当前无法安全保证 selective commit 只打包本轮增量。

因此这轮选择：落地文件、写记录、发邮件，但**不做不干净的混合提交**。

## 本轮一句话结论

breakout 线现在最诚实的位置已经可以明确写成：**`shadow-admission queue / one_more_gate`**；它离 shadow paper 还差的主要不是组合层资金曲线，而是 `ETH+SOL pair-conditioned halfsize` 这条默认 sizing 规则在更长后续窗口里的迁移性证明。
