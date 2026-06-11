# 2026-03-15 21:21 UTC｜首页新增 Deployment Watch，把 EMA 真等待与 breakout 硬 blocker 直接压成首页守门快照

## 为什么这次选这个
- 先检查了 `git status --short`、`docs/TODO.md`、`AUTO_OPTIMIZATION_LOOP.md`、以及最近几轮 optimization logs。
- 当前 steering 下，最接近 `paper trading / 伪实盘` 的仍是 `EMA baseline family`；但这一轮还没到下一根真实 `completed bar`，不能伪造新的 `market-close refresh / week-1 review`。
- breakout 这边，`pure down coverage = 0/100`、`pre-down bridge coverage = 0`、`one_more_gate` 的 scope 已收紧完成；继续回切旧样本只会重复 micro-slicing，不会 overturn 当前 verdict。
- 因此本轮不再继续补近义 EMA board / queue 页面，也不回到 breakout 旧样本，而是选一个**更接近网页最终表达 / deployment 判断**的小而完整任务：
  - 把 EMA 当前是否已到点、append-only ledger 连续性、以及 breakout 当前最硬 blocker，直接压成首页可见的 `Deployment Watch / 当前守门快照`。

## 本轮主点
- 主点：**首页 index 直接读取 live artifacts，给出 deployment-facing 守门快照**。
- 紧邻子点：把这条进展回写 `docs/TODO.md` / `plans` 镜像，避免首页与 roadmap 脱节。

## 做了什么

### 1) 扩展 `scripts/build_site_index.py`，让首页读当前守门 artifacts
新增了三类 artifact 读取：
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_refresh_history.csv`
- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_scope_verdict_20bps.csv`

并在首页 hero 下方新增一个 `Deployment Watch / 当前守门快照` 区块，直接输出：
- `EMA ledger`：当前是否已经进入 `due_now / overdue`，若没有，则显示最靠前 lane、下一次 close 与剩余时间；
- `EMA continuity`：`refresh_history` 当前累计了多少条 completed-bar rows、覆盖多少条 lane、最近一次写入时间、history 里最新 completed bar 截止到哪里；
- `Breakout gate`：当前最诚实 scope、当前最不该误读成什么、以及下一次什么才算有效推进。

这一步的价值是：Jerry 不需要再先翻 EMA 主报告 / due guardrail / breakout scope verdict，单看首页就能判断“现在该继续等 EMA 真 close，还是 breakout 终于有了足以 overturn `one_more_gate` 的新证据”。

### 2) 同步更新 `docs/TODO.md`
在已完成的首页入口任务下补了一条最新进展：
- 首页现在不再只有静态 priority 文案；
- 已能直接读取 `EMA due guardrail + refresh history + breakout scope verdict`；
- 首页级别就能展示 deployment-facing 守门状态。

### 3) 重建 plans / homepage 静态页
执行：
- `python3 scripts/build_plans_site.py`
- `python3 scripts/build_site_index.py`

结果：
- `reports/site/plans/momentum_todo.html` 已同步出现这条更新；
- `reports/site/index.html` 已出现 `Deployment Watch / 当前守门快照`。

## 当前首页守门快照（本轮生成时）
- `EMA ledger`：当前还没有 `due_now / overdue` lane；最靠前的是 `Crypto 1d+1wk（BTC/ETH/SOL）`，下一次 close 约在 `2026-03-16 00:00 UTC`，约 `3.2` 小时后到点。
- `EMA continuity`：`ema_paper_trading_refresh_history.csv` 当前累计 `5` 条 completed-bar rows，覆盖 `5` 条 lane；最近一次写入 `2026-03-15 21:05 UTC`，history 里最新 completed bar 截止到 `2026-03-14 00:00 UTC`。
- `Breakout gate`：当前 scope 仍是 `up-flat biased conditional alpha / shadow-admission candidate`；当前最不该误读成 `near-down protective policy`，因为 `default pair` 仍是 `pure down = 0/100`、`48h down-risk zone = 0/109`、`future pure-down 48h = 0/44`；下一次有效推进仍必须来自新的 `forward shadow / holdout` 真正命中 `pure-test/down-tail`。

## 验证 / 证据
执行：
- `python3 -m py_compile scripts/build_site_index.py`
- `python3 scripts/build_site_index.py`
- `python3 scripts/build_plans_site.py`
- `grep -n "Deployment Watch\|当前守门快照\|21:19 UTC" reports/site/index.html reports/site/plans/momentum_todo.html`

验证结果：
- `build_site_index.py` 语法检查通过。
- 首页已生成成功，并出现 `Deployment Watch / 当前守门快照` 区块。
- `reports/site/plans/momentum_todo.html` 已同步出现 `2026-03-15 21:19 UTC` 的首页守门快照更新。
- 本轮没有重刷 EMA 主报告，也没有新增近义 EMA board / breakout digest；只补首页最终表达层与 roadmap 同步。

## 风险 / 边界
- 这不是新的 EMA forward 证据，也不是新的 breakout overturn 证据；它只是把**当前真实状态**更直接地挂到首页。
- `EMA` 线仍未完成 line-305 那个真正的未完成主任务：沿同一张 live ledger 落下下一轮真实 `market-close refresh / week-1 review`。
- breakout 侧也没有改写 `one_more_gate` verdict；只是把“现在最不该误读成什么”压成首页级可见口径，避免继续被当作 near-down protective policy。

## 执行层 hygiene
- `git status --short` 显示当前 worktree 里仍有大量与本轮无关的既有脏改 / 未跟踪文件；本轮没有把这些无关内容混进来。
- 本轮直接相关文件只有：
  - `scripts/build_site_index.py`
  - `docs/TODO.md`
  - `reports/site/index.html`
  - `reports/site/plans/momentum_todo.html`
- 本轮没有去碰 `pytrendline_event_validation_v3`，也没有把 breakout 拉回更窄 context 分支。

## 发布 / 发送
- 已执行：`bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`
  - 结果：`[ok] homepage index published -> /var/www/momentum-report/index.html`
  - 线上地址：`https://jp.jerrypsy.top/momentum/`
- 已执行：`python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-auto] 首页守门快照上线" --body-file /root/clawd/jerry/momentum/research/optimization_loop/2026-03-15_2121_homepage-deployment-watch.md`
  - 结果：邮件已发送到默认收件箱 `18810813576@163.com`

## Commit hash
- HEAD：`9884685`
- 本轮未提交。

## 未提交原因
- 当前 repo 里存在大量与本轮无关的历史脏改 / 未跟踪产物；虽然本轮变更面很小，但在这种 worktree 状态下做 selective commit 仍有误混无关文件的风险，因此本轮保持未提交更稳妥。
