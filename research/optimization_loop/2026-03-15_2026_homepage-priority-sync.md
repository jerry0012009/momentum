# 2026-03-15 20:26 UTC｜首页 index 口径同步到当前真实优先级

## 为什么这次选这个
- 先检查了 `git status --short`、`docs/TODO.md`、最近几轮 optimization logs，以及当前站点首页 hero 文案。
- 当前 steering 已经很明确：
  1. `EMA baseline family` = closest to paper / 伪实盘；
  2. `support_breakout_v0` = 仍卡在 `one_more_gate`；
  3. `Fibonacci` = archived / optional filter。
- 但首页 `reports/site/index.html` 仍在把三条线近乎平铺地写成 `V3 / breakout / Fibonacci / EMA` 的 closure-first 入口，和现在最关键的 deployment-facing 判断已经有点脱节。
- 这轮如果继续补 EMA 守门近义说明，容易重复最近两轮的执行层动作；相反，把**首页总入口**同步到当前真实优先级与下一步诚实读法，能直接减少 Jerry 的判断摩擦，属于“网页最终表达”上的小而完整推进。

## 本轮主点
- 主点：**首页 index hero 改写成当前真实优先级 / deployment 读法**。
- 紧邻子点：把 `EMA` 的下一步动作与 `breakout` 的 blocker 直接压成首页最短判断，避免还要跨页拼结论。

## 做了什么
### 1) 改写首页生成脚本的 hero 口径
修改：`scripts/build_site_index.py`

把首页顶部几段说明从旧的“平均推进三条线”改成现在更诚实的写法：
- 明确默认优先顺序：
  - `EMA baseline family（closest to paper / 伪实盘）`
  - `support_breakout_v0（one_more_gate）`
  - `Fibonacci（archived / optional filter）`
- 明确首页最短判断：
  - `EMA`：继续沿同一张 live ledger 等下一次真实 completed bar，再跑
    `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - `breakout`：当前仍只能按
    `up-flat biased conditional alpha / one_more_gate` 读；
    除非后续前瞻证据终于补出非零 `pure down` / `pre-down bridge` 覆盖
  - `Fibonacci`：先停在 archived / optional filter
- 明确 `PyTrendline v3` 现在只作为历史证据包，默认不再当 active 主任务。

### 2) 重建首页静态页
执行：`python3 scripts/build_site_index.py`

结果：`reports/site/index.html` 已同步生成，hero 文案已更新，不再继续把旧的资源顺序挂在项目总入口上。

## 为什么这步有价值
这轮没有新增 alpha，也没有伪造 EMA 的下一轮 refresh；价值在于把**“现在到底该继续推什么”**直接写到首页：
- 如果 Jerry 只看首页，现在就能立刻知道：
  - 最该盯的是 `EMA`，而且下一步不是继续补 board，而是等真实 close；
  - `breakout` 还没过 `one_more_gate`，blocker 不是 wording，而是 `pure down / pre-down bridge` 仍没补出来；
  - `Fibonacci` 默认已经退到 optional filter。
- 这比继续在子页里补一层近义说明更接近“最终网页表达”。

## 验证 / 证据
执行：
- `python3 scripts/build_site_index.py`
- `sed -n '35,52p' reports/site/index.html`

验证结果：
- 首页重建成功；
- hero 里已经出现新的优先级与最短判断：
  - `EMA baseline family -> support_breakout_v0 -> Fibonacci`
  - `EMA` 的守门命令 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - `breakout` 的 `up-flat biased conditional alpha / one_more_gate` 读法
  - `PyTrendline v3` 只作历史证据包

## 风险 / 边界
- 这轮是**入口表达同步**，不是新的策略证据，也不改变任何 report 子页里的原始结论。
- 没有去重开 `pytrendline_event_validation_v3`。
- 没有伪造 `EMA` 的新 refresh / week-1 review；当前真实状态仍是等待下一根 completed bar。
- 也没有尝试继续切 breakout 的 same-sample 微切片；首页只把当前 blocker 说得更直接。

## 相关文件
- `scripts/build_site_index.py`
- `reports/site/index.html`

## 执行层 hygiene
- `git status --short` 显示当前 worktree 里仍有大量与本轮无关的历史脏改 / 未跟踪产物；本轮没有把这些无关改动混进判断。
- 本轮直接相关改动只涉及：
  - `scripts/build_site_index.py`
  - `reports/site/index.html`
- 后续仍按要求刷新并发布首页 index、并把本记录邮件发出。

## 发布 / 发送
- 已执行：`bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`
  - 结果：`[ok] homepage index published -> /var/www/momentum-report/index.html`
  - 线上地址：`https://jp.jerrypsy.top/momentum/`
- 已执行：`python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-auto] 首页优先级口径同步" --body-file /root/clawd/jerry/momentum/research/optimization_loop/2026-03-15_2026_homepage-priority-sync.md`
  - 结果：邮件已发送到默认收件箱 `18810813576@163.com`

## Commit hash
- HEAD：`582e2cc`
- 本轮未提交。
- 原因：当前工作区噪音非常大，且存在大量与本轮无关的既有脏改 / 未跟踪文件；虽然本轮变更面很小，但在当前状态下不做 selective commit 更稳妥，避免误混无关文件。