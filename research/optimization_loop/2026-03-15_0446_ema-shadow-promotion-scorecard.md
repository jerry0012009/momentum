# EMA A股 daily shadow 升格评分卡

- 时间：2026-03-15 04:46 UTC
- 本轮主点：`EMA / PSAR raw alpha focus`
- 紧邻子点：`paper-trading candidate / operating spec` 之后，继续把 `沪深300ETF 1d` 的 shadow 状态压成更硬一点的 promotion verdict

## 为什么这次选这个

1. 先看了 `git status`、最近 optimization loop 记录，以及 `docs/TODO.md` 当前接力棒，确认最近三轮已经完成：
   - `EMA final survivor map -> paper-trading candidate spec`
   - `breakout -> one_more_gate admission verdict`
   - `EMA candidate spec -> operating spec / guardrails`
2. 当前 steering 明确要求默认优先推进**离 paper 最近**的对象；而 `EMA baseline family` 仍是目前三条线里最接近 paper trading 的对象。
3. 既然 `candidate spec` 与 `operating spec` 都已经有了，下一刀最像样、也最 deployment-facing 的小任务就不该再是泛泛 wording，而是：
   - `沪深300ETF 1d` 现在到底够不够从 `shadow watch` 升格；
   - 还是应该继续留在 shadow，不要因为 recent 改善就偷渡进正式 paper batch。

## 做了什么改动

### 1) 把 A股 daily strict-holdout 压成一张 `shadow-promotion scorecard`

更新：
- `scripts/build_ema_psar_raw_alpha_report.py`

新增 artifact：
- `reports/artifacts/ema_psar_raw_alpha/ema_ashare_daily_shadow_promotion_scorecard.csv`

网页新增：
- `reports/site/factors/ema_psar_raw_alpha/report.html`
- 新增 `Q25. 如果只在 A股 daily 里给 EMA 一个 primary 和一个 shadow，沪深300ETF 1d 现在够不够升格？`

这张评分卡没有新增回测，而是**复用现有 strict-holdout 窗口**，用 5 个最小 gate 压缩成 deployment-facing 判断：
1. overall 正 holdout 占比 ≥ 62.5%
2. overall 跑赢 PSAR 占比 ≥ 62.5%
3. recent 3 个 holdout 至少 2/3 为正
4. 最新 holdout 为正
5. 最新 holdout 仍跑赢 PSAR

### 2) 把 `primary` 与 `shadow` 的分工压得更硬

本轮结论现在已经能直接落到网页上：
- `创业板ETF 1d`：约 **5/5 gate 命中**
  - overall 正 holdout 约 `75.00%`
  - overall 跑赢 PSAR 约 `75.00%`
  - latest holdout net20 约 `39.63%`
  - 当前最诚实位置仍是 **`keep_primary`**
- `沪深300ETF 1d`：约 **3/5 gate 命中**
  - recent 3 个 holdout 里约 `66.67%` 为正
  - latest holdout net20 约 `13.96%`
  - latest 相对 PSAR 约 `+7.59pp`
  - 但 overall 正 holdout 仍只有 `50.00%`
  - overall 跑赢 PSAR 也只有 `50.00%`
  - 当前最诚实位置是 **`stay_shadow_not_promote`**

一句话说就是：
**沪深300ETF 1d 最近确实在变好，但还没厚到可以从 shadow 升格进正式 paper batch。**

### 3) TODO / 计划入口同步

更新：
- `docs/TODO.md`
- `reports/site/plans/momentum_todo.html`

已新增并打勾：
- `[x] EMA：把 沪深300ETF 1d 的 mixed/watch 状态压成 shadow-promotion scorecard`

这样当前 TODO 入口已经能直接回答：
- `创业板ETF 1d` = 继续当 `primary pilot`
- `沪深300ETF 1d` = 仍是 `shadow watch`，但可作为下一刀最该追的 `shadow promotion candidate`

## 验证 / 证据

已执行：

```bash
python3 -m py_compile scripts/build_ema_psar_raw_alpha_report.py scripts/build_plans_site.py
python3 scripts/build_ema_psar_raw_alpha_report.py
python3 scripts/build_plans_site.py
```

命中检查：
- `reports/artifacts/ema_psar_raw_alpha/ema_ashare_daily_shadow_promotion_scorecard.csv` 已生成
- `reports/site/factors/ema_psar_raw_alpha/report.html` 已出现新的 `Q25`
- 页面内已出现 `keep_primary` 与 `stay_shadow_not_promote` 两个 verdict
- `docs/TODO.md` 与 `reports/site/plans/momentum_todo.html` 已同步新增并打勾该任务

备注：
- 运行期间仍出现 matplotlib 中文字形 warning（既有字体问题），但 HTML / CSV 产物正常生成，不影响本轮结论页落地。
- 本轮没有重跑重型下载；主要复用现有 strict-holdout 结果，把它们压成更 deployment-facing 的 verdict 表达。

## 风险 / 边界

1. 这轮**没有新增更长 forward holdout**，只是把现有 A股 daily strict-holdout 压成更硬的 promotion scorecard。
2. `沪深300ETF 1d` 当前的 recent 改善还不足以说明它已经稳定转强；真正没补齐的仍是 overall 厚度，而不是 latest 单窗表现。
3. 因此这轮结论不是“沪深300ETF 1d 不值得再看”，而是：**它现在值得继续当 shadow promotion candidate，但还不配并入正式 paper batch。**

## 下一步建议

1. 如果 EMA 线继续，默认优先做 `沪深300ETF 1d` 的更严格前瞻 honesty / holdout 扩展，回答它能否把当前 `overall 50% / overall 50% beats-PSAR` 再补厚。
2. 不建议回头再做泛泛的 `EMA family closure-copy`；现在更有价值的是继续追这个 shadow pocket 能否真升格，或者诚实确认它就该长期停在 shadow。
3. breakout 线维持已有更硬 verdict：`shadow-admission queue / one_more_gate`；若下一轮切 breakout，优先继续盯 `ETH+SOL pair-conditioned halfsize` 的 forward transferability。

## Commit hash

本轮**未提交**。

原因：
1. repo 在本轮开始前就存在大量与本轮无关的既有脏改动与未跟踪文件；
2. 本轮涉及文件（`docs/TODO.md`、`scripts/build_ema_psar_raw_alpha_report.py`、`reports/site/factors/ema_psar_raw_alpha/report.html`、`reports/site/plans/momentum_todo.html`）也处在持续累计修改链上；
3. 当前无法安全保证 selective commit 只打包本轮增量，因此这轮只落文件、日志与邮件，不做不干净提交。

## 一句话结论

**EMA 线现在已经不只是知道“沪深300ETF 1d 要 shadow”，而是知道“它为什么还只能 shadow、差的是哪两道 gate”；这让下一轮是否继续追它，变成一个更清楚的 admission 问题。**
