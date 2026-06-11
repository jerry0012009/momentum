# 2026-03-15 06:48 UTC — EMA shadow recent-forward honesty audit

## 本轮主点
- 主点：`EMA / PSAR raw alpha focus`
- 紧邻子点：把 `沪深300ETF 1d` 的 shadow 状态从 scorecard 再压成一刀 **recent-forward honesty audit**，避免继续只补 EMA 的 entry-layer board。

## 为什么选这个
- 按最新 steering，EMA 线若没有新的 **真实前瞻 / honesty 证据**，就不要继续补 `admission-board / operating-board / monitoring-board` 近义层。
- 最近 breakout 线已经连续补了 `pure-test tail / down-tail coverage / mixed-tail protective gate`，本轮不再重复同一块。
- 当前最 deployment-facing、且仍未被真正压硬的问题，是：`沪深300ETF 1d` 这个 `shadow_watch` 到底有没有出现足够硬的 recent-forward promotion honesty。

## 先检查了什么
1. 回看 `docs/TODO.md` 当前接力棒与最近几轮记录，确认：
   - EMA 线已连续完成 `candidate spec / operating spec / shadow scorecard / monitoring board`
   - 当前默认不应继续新增 EMA 近义 board
   - 若继续 EMA，更该补 `沪深300ETF 1d` 的真实 forward / holdout honesty
2. 复用现成 artifact：
   - `reports/artifacts/ema_psar_raw_alpha/ema_non60m_ashare_daily_holdout_window_metrics.csv`
   - `reports/artifacts/ema_psar_raw_alpha/ema_ashare_daily_shadow_promotion_scorecard.csv`
3. 未重跑额外下载；只复用脚本已有 `A股 daily strict holdout` 结果。

## 本轮实际推进
### 1) 新增 recent-forward honesty audit 产物
更新：
- `scripts/build_ema_psar_raw_alpha_report.py`

新增函数：
- `build_ema_ashare_daily_recent_forward_audit(...)`

新增 artifact：
- `reports/artifacts/ema_psar_raw_alpha/ema_ashare_daily_recent_forward_audit.csv`

口径：
- 只看 A 股 daily 各口袋最近 `2` 段已发生的 strict forward holdout
- 直接汇总：
  - forward 起止区间
  - EMA / PSAR 的 tail cumulative net20
  - EMA tail positive share
  - EMA tail beats-PSAR share
  - tail worst holdout
  - forward honesty verdict

### 2) 把新证据落到 EMA 主报告页
更新：
- `reports/site/factors/ema_psar_raw_alpha/report.html`

新增：
- `Q27. 如果真的只追 沪深300ETF 1d 的 shadow-promotion honesty，最近两段真实 forward holdout 在说什么？`

这段现在不再只是重复 `3/5 gate`，而是直接回答：
- `沪深300ETF 1d` 最近两段真实 forward holdout 虽然都为正
- 但同段累计仍落后 PSAR
- 且只在 `1/2` 段跑赢 PSAR
- 所以它现在可以写成 `recent-forward positive`，但**还不能写成 promotion honesty passed**

### 3) TODO / plans 同步
更新：
- `docs/TODO.md`
- `reports/site/plans/momentum_todo.html`
- `reports/site/plans/index.html`
- `reports/site/plans/report.html`

新增并打勾：
- `[x] EMA：把 沪深300ETF 1d 的 shadow 状态再压成 recent-forward honesty audit`

## 核心结果
### 沪深300ETF 1d（shadow watch）
最近 `2` 段真实 forward holdout（`2024-03-12 -> 2026-03-12`）：
- EMA tail cumulative net20：约 `+14.26%`
- PSAR tail cumulative net20：约 `+18.71%`
- EMA vs PSAR cumulative delta：约 `-4.45pp`
- EMA positive holdout share：`2/2 = 100%`
- EMA beats-PSAR share：`1/2 = 50%`
- tail worst holdout：约 `+0.26%`
- verdict：`positive_but_not_promotable`

更诚实的解释：
- 它已经不是“recent-forward 仍然偏负”的口袋；这点算真实进展。
- 但它也还不是“promotion honesty 已经过线”的口袋：
  - 因为同一段真实 forward 里，累计仍没跑赢 PSAR；
  - 最弱那段只勉强为正；
  - 还缺一段更厚、更不贴边的正 holdout 来支撑升格。

### 创业板ETF 1d（primary pilot）
同样最近 `2` 段 forward holdout：
- EMA tail cumulative net20：约 `+62.27%`
- PSAR tail cumulative net20：约 `+58.85%`
- verdict：`keep_primary_recent_forward_ok`

这说明：
- 当前 primary / shadow 的分工并没有被 recent-forward 证据推翻；
- `创业板ETF 1d` 仍能继续承担 primary；
- `沪深300ETF 1d` 仍更诚实地停在 shadow。

## 为什么这轮算真实推进
这轮没有再补 EMA 的近义 board，也没有回到 closure-copy。

它交付的是一刀新的 **真实 forward / honesty 证据**：
- 现在不是只会说 `沪深300ETF 1d = 3/5 gate, stay shadow`
- 而是能更硬地说：
  - **最近两段真实 forward holdout 已转正**
  - 但**promotion honesty 仍未过线**
  - 因为它还没有在同一段真实 forward 里持续跑赢 PSAR

这直接帮助判断：
- EMA 线还该不该继续往 paper / 伪实盘推进；
- `沪深300ETF 1d` 到底是“下一轮最该追的 shadow candidate”，还是已经能升格。

## 修改文件
- `scripts/build_ema_psar_raw_alpha_report.py`
- `docs/TODO.md`
- `reports/artifacts/ema_psar_raw_alpha/ema_ashare_daily_recent_forward_audit.csv`
- `reports/site/factors/ema_psar_raw_alpha/report.html`
- `reports/site/plans/index.html`
- `reports/site/plans/momentum_todo.html`
- `reports/site/plans/report.html`

## 最小验证
已执行：
```bash
python3 -m py_compile /root/clawd/jerry/momentum/scripts/build_ema_psar_raw_alpha_report.py /root/clawd/jerry/momentum/scripts/build_plans_site.py
python3 /root/clawd/jerry/momentum/scripts/build_ema_psar_raw_alpha_report.py
python3 /root/clawd/jerry/momentum/scripts/build_plans_site.py
```

抽查：
- `ema_ashare_daily_recent_forward_audit.csv` 已生成
- `ema_psar_raw_alpha/report.html` 已出现 `A股 daily recent-forward honesty audit（latest 2 holdouts）`
- `TODO.md` 与 `plans/momentum_todo.html` 已同步出现 `recent-forward honesty audit`

备注：
- 运行期间仍有 matplotlib 中文字形 warning（既有字体问题），但 HTML / CSV 正常生成，不影响本轮结论。

## git / 提交说明
本轮未提交。

原因：当前 `git status --short` 仍显示大量与本轮无关的既有脏改动与未跟踪文件；本轮不应把这些无关改动混进同一次提交。若后续需要提交，应只做安全的 selective commit。

## 邮件
- 主题：`[momentum-auto] EMA shadow 前瞻诚实度`
- 通过默认 SMTP 脚本发送本记录
