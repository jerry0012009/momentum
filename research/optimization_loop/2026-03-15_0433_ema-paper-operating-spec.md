# EMA 伪实盘运行纪律落页（operating spec）

- 时间：2026-03-15 04:33 UTC
- 本轮主点：`EMA / PSAR raw alpha focus`
- 紧邻子点：`closure / board` 与 `TODO` 的 deployment-facing 入口同步

## 为什么这次选这个

1. 先看了 `git status`、最近 optimization loop 记录与 `docs/TODO.md`，确认最近两轮已经把：
   - `EMA final survivor map -> paper-trading candidate spec`
   - `breakout -> one_more_gate admission verdict`
   都压到了网页与 TODO。
2. 当前 steering 明确要求优先推进**离 paper trading 最近**的对象；在现有三条线里，`EMA baseline family` 仍是 `closest to paper`。
3. 既然 `candidate spec` 已经有了，下一步最接近 deployment 的缺口就不该再是泛泛 closure wording，而是：**如果今天真要开一版 EMA baseline 的伪实盘，primary / secondary / shadow / exclude 到底该怎么分账、怎么继续、怎么降级。**

## 做了什么改动

### 1) 把 EMA 的 candidate spec 再压成 `paper-trading operating spec`

更新：
- `scripts/build_ema_psar_raw_alpha_report.py`

新增 artifact：
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_operating_spec.csv`

网页新增：
- `reports/site/factors/ema_psar_raw_alpha/report.html`
- 新增 `Q24. 如果今天真要开一版 EMA baseline paper，运行纪律应该怎么写？`

这版 operating spec 把运行纪律写死为：
- `创业板ETF 1d` = `primary paper pilot`
  - 必须单独记账，不和 secondary / mixed / exclude 口袋混成一条 family 曲线
- `美股 1d+1wk`、`Crypto 1d+1wk`、`贵州茅台 1d+1wk` = `secondary backstop batch`
  - 只能按 `market × freq` 分开记账，不能拿来稀释 primary pilot 的真实表现
- `沪深300ETF 1d` = `shadow watch only`
  - 继续观察，但默认不并入正式 paper batch
- `Crypto 60m`、`沪深300ETF 1wk`、`创业板ETF 1wk` = `hard exclude`
  - 默认停用；除非未来出现新的 overturn evidence，否则不能靠 family 汇总、局部反弹或 overlay 重新混回 baseline paper 叙事

### 2) 把 closure board 的 EMA 口径同步成 `candidate spec + operating spec`

更新：
- `scripts/build_alpha_closure_board_report.py`
- `reports/site/factors/alpha_closure_board/report.html`

同步后，这页不再只说“EMA 已有 candidate spec”，而是明确写成：
- `EMA / PSAR` = `closest to paper`
- 当前已有 `final survivor map + paper candidate/operating spec`

### 3) TODO / 计划入口同步

更新：
- `docs/TODO.md`
- `reports/site/plans/momentum_todo.html`

已新增并打勾：
- `[x] EMA：把 candidate spec 再压成 paper-trading operating spec / guardrails`

## 验证 / 证据

已执行：

```bash
python3 -m py_compile scripts/build_ema_psar_raw_alpha_report.py scripts/build_alpha_closure_board_report.py scripts/build_plans_site.py
python3 scripts/build_ema_psar_raw_alpha_report.py
python3 scripts/build_alpha_closure_board_report.py
python3 scripts/build_plans_site.py
```

命中检查：
- `reports/site/factors/ema_psar_raw_alpha/report.html` 已出现 `Q24. 如果今天真要开一版 EMA baseline paper，运行纪律应该怎么写？`
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_operating_spec.csv` 已生成
- `reports/site/factors/alpha_closure_board/report.html` 已出现 `paper candidate/operating spec`
- `docs/TODO.md` 已出现并打勾 `paper-trading operating spec / guardrails`

备注：
- 运行时仍有 matplotlib 中文字形 warning（既有字体问题），但 HTML / CSV 产物正常生成，不影响这轮结论页落地。

## 为什么这轮算真实推进

这轮不是继续补“EMA 看起来最接近 paper”的泛泛结论，而是把最关键的 deployment-facing 问题压成了**可执行纪律**：

- 哪些口袋可以 live paper / secondary batch / shadow only / hard exclude；
- primary 与 secondary 是否允许合并叙事；
- mixed / fail pocket 是否还能借 family 汇总重新混回 baseline paper。

这直接帮助回答 Jerry 现在更实际的问题：

> 如果今天真要开始一版 EMA 伪实盘，该怎么跑，哪些地方不能自欺？

## 风险 / 边界

1. 这版 operating spec 依然建立在当前 survivor map / candidate spec 上，不等于这些口袋都已经完成 production 级 admission。
2. `美股 / Crypto / 贵州茅台` 的 secondary batch 目前主要还是依赖长样本 gross/cost 厚度与已有边界，不等于它们都已经经历了和 A股 frontier 完全同等级的 strict holdout。
3. 这轮解决的是**运行纪律与 admission 边界**，不是新增 net backtest / 新 holdout slice。

## 下一步建议

1. 如果 EMA 线继续，默认优先挑战 `沪深300ETF 1d` 这种 `mixed / watch` pocket，回答它能不能从 shadow 升级，而不是回头再给 `60m crypto` 或 `A股 weekly frontier` 找 hopeful 解释。
2. breakout 线仍保持当前更诚实的口径：`shadow-admission queue / one_more_gate`；若继续，应优先追问 `ETH+SOL pair-conditioned halfsize` 在更长 forward windows 里是否还能守住迁移性。

## Commit hash

本轮**未提交**。

原因：
1. repo 工作区在本轮开始前就存在大量与本轮无关的既有脏改动与未跟踪文件；
2. 本轮涉及的关键文件（`docs/TODO.md`、相关脚本、站点页）也处在持续累计修改链上；
3. 当前无法安全保证 selective commit 只打包本轮增量，因此这轮只落文件与邮件，不做不干净提交。

## 一句话结论

**EMA 线现在不只知道“谁能进 paper”，还知道“进了之后必须怎么分账、什么时候该降级”；这让它比 breakout 更接近真正可执行的伪实盘对象。**
