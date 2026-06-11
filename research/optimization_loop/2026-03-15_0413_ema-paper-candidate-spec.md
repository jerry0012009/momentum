# EMA paper-trading candidate spec / admission board sync

- 时间：2026-03-15 04:13 UTC
- 本轮主点：`EMA / PSAR raw alpha focus`
- 紧邻子点：`closure / board` 里的统一 `paper trading admission verdict`

## 先检查了什么

1. 查看 `git status` 与最近 optimization loop 记录，确认 repo 里已有大量既有脏改动，且最近两轮刚完成：
   - `2026-03-15_0202_ema-final-survivor-map.md`
   - `2026-03-15_0210_breakout-pair-walkforward-honesty.md`
2. 回看 `docs/TODO.md` 当前接力棒，发现最靠近 deployment 的未收口项正是：
   - `EMA：把 final survivor map 继续压成 paper-trading candidate spec`
   - `项目级：在 closure / TODO 入口给出一版统一 paper trading admission verdict`
3. 结合本轮 steering：`EMA baseline family` 是当前 **closest to paper** 的对象，因此没有继续平均推进 breakout / Fibonacci，而是优先把 EMA 从 family boundary 再压成 deployment-facing spec。

## 本轮实际推进

### 1) 把 EMA final survivor map 压成可执行的 `paper-trading candidate spec`

更新：`scripts/build_ema_psar_raw_alpha_report.py`

新增 artifact：
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_candidate_spec.csv`

网页新增：
- `reports/site/factors/ema_psar_raw_alpha/report.html`
- 新增 `Q23. 如果把 final survivor map 再压成 paper-trading candidate spec，今天该怎么部署 EMA baseline？`

这版 spec 的明确口径是：
- `paper_now_primary`
  - `创业板ETF 1d`
- `paper_now_secondary`
  - `美股 1d+1wk（SPY/QQQ/AAPL）`
  - `Crypto 1d+1wk（BTC/ETH/SOL）`
  - `贵州茅台 1d+1wk`
- `shadow_only`
  - `沪深300ETF 1d`
- `exclude`
  - `沪深300ETF 1wk`
  - `创业板ETF 1wk`
  - `Crypto 60m（BTC/ETH/SOL rolling）`

也同步把 `PSAR` 的位置讲清：
- 仍是 `shadow comparator / protective hypothesis`
- 不是这版 EMA baseline paper admission 的主 pocket

### 2) 在 closure board 给出统一 `paper admission` 口径

更新：
- `scripts/build_alpha_closure_board_report.py`
- `reports/site/factors/alpha_closure_board/report.html`

现在 closure board 已显式分成：
- `EMA / PSAR` = `closest to paper`
- `breakout-short follow-up` = `needs one more gate`
- `Fibonacci` = `park / archive`

并且在卡片 pill 与对照表里直接显示 `paper admission`，避免下一轮继续围绕“三条线都重要”平均用力。

### 3) TODO / 入口同步

更新：
- `docs/TODO.md`
- `reports/site/plans/momentum_todo.html`

已把以下接力棒打勾：
- `[x] EMA：把 final survivor map 继续压成 paper-trading candidate spec`
- `[x] 项目级：在 closure / TODO 入口给出一版统一 paper trading admission verdict`

## 为什么这轮算真实推进

这轮没有再补泛泛 wording，也没有继续扩候选池；而是把 EMA 线从“family 边界已经清楚”进一步推进到“如果今天要做伪实盘，哪些 pocket 先纳入、哪些只 shadow、哪些直接排除”的部署范围说明。

这直接帮助回答 Jerry 当前最关心的问题之一：
- 这条 EMA 线现在到底离 paper trading 还有多远？
- 如果要先做一版最小 paper baseline，应该从哪里开始？

## 最小验证

已执行：

```bash
python3 -m py_compile scripts/build_ema_psar_raw_alpha_report.py scripts/build_alpha_closure_board_report.py scripts/build_plans_site.py
python3 scripts/build_ema_psar_raw_alpha_report.py
python3 scripts/build_alpha_closure_board_report.py
python3 scripts/build_plans_site.py
```

附加命中检查：
- `reports/site/factors/ema_psar_raw_alpha/report.html` 已出现新的 `Q23`
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_candidate_spec.csv` 已生成，且包含 `paper_now_primary`
- `reports/site/factors/alpha_closure_board/report.html` 已出现 `closest to paper`
- `docs/TODO.md` 对应接力棒已打勾

备注：
- 运行期间出现 matplotlib 中文字形 warning（glyph missing），属于既有绘图字体问题；本轮 HTML / CSV 产物正常生成，不影响本次结论页落地。

## 当前最诚实的 admission board

- `EMA baseline family`：**closest to paper**
  - 已有 candidate spec，但仍不是 production admission
  - 继续推进时，默认优先挑战 `沪深300ETF 1d` 这类 `mixed / watch` pocket，或抽查 secondary batch backstops 的 holdout honesty
- `support_breakout_v0`：**needs one more gate**
  - 已接近 shadow paper，但还差更硬的 admission honesty verdict
- `Fibonacci`：**park / archive**
  - 保留为 optional filter idea，不再抢主资源

## Git / 提交

本轮**未提交**。

原因：
1. 本轮开始前 repo 已存在大量与本轮无关的既有脏改动；
2. 本轮涉及的关键文件（尤其 `docs/TODO.md`、两份脚本、两份站点页）在开始前就已经处于 dirty 状态；
3. 在这种前提下做 selective commit，无法可靠保证只打包本轮增量。

因此这轮选择只落文件与邮件，不做不干净的提交。
