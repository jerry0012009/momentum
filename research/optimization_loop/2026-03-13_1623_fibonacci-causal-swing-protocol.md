# 给 Fibonacci mini brief 固定 causal swing protocol v1

## 为什么这次选这个

这轮继续严格沿 Fibonacci 这条刚刚补出来的 mini brief 线程推进，没有扩新来源，也没有急着上实验。

原因很简单：这条线当前最大的真实风险，不是“还没多一个网页入口”，而是**如果不先把 swing high / low 的因果口径写死，后面做 15m clean-room 实验时很容易把 hindsight pivot 偷带进去**。那样即使实验结果好看，也不够可信。

所以这轮最合适的一小步，不是再加内容，而是把最关键的 no-lookahead / no-rewrite 规则写进 brief 本体，让后面谁来接手，都按同一套因果边界做。

这轮最值得复用/借鉴的点是：**当一个外部方法最容易出错的地方是结构锚点本身时，先固定 causal anchor protocol，往往比立刻跑第一轮回测更重要。**

## 核心结论（中文摘要）

核心结论：**Fibonacci mini brief 现在已经固定 `causal swing protocol v1`：pivot 必须经 `2-bar right confirmation` 才正式可见，回撤位只能由最近一对已确认 opposite swings 生成，且已形成的交易候选不允许被后来才确认的新 swing retroactively 重写。**

证据如何支持这个结论：**本轮已把这套规则直接写进 `Trendline Replication Briefs` 的 `Brief E · Fibonacci pullback confirmation`，并同步更新 `TODO.md` 镜像页；本地与发布目录里的页面都已 grep 到 `causal swing protocol v1 / 2-bar right confirmation / retroactively 重写` 这些关键约束。**

## 本轮做了什么改动

本轮只做一个主点：**固定 Fibonacci 线的 causal swing protocol。**

具体改动：

1. 更新 `scripts/build_trendline_replication_briefs_report.py`
   - 在 `Brief E · Fibonacci pullback confirmation (Gurrib et al., 2022)` 的“最小 clean-room 定义”里新增：
     - `causal swing protocol v1`
   - 明确三条规则：
     1. swing high / low 需要 `2-bar right confirmation` 才算正式可见；
     2. 回撤位只能由最近一对已确认的 opposite swings 生成；
     3. 已形成的交易候选，在失效 / 成交前不允许被后来才确认的新 swing retroactively 重写。

2. 同步修正同一张 brief 的风险段
   - 不再只说“swing 定义要 causal”；
   - 而是进一步明确：即使采用 `causal swing protocol v1`，pivot delay 也会让信号变慢，因此后续实验要把“更干净的因果边界”和“更少的时效性损失”分开评估。

3. 更新 `docs/TODO.md`
   - 在 `E3-A. shortlist 机制` 的 Fibonacci 进度说明后追加：
     - 该 mini brief 已固定 `causal swing protocol v1`；
     - 明确 pivot 可见性、回撤位生成边界，以及禁止 retroactive rewrite。

4. 重建并发布最小必要页面
   - 重建：
     - `reports/site/reading/trendline_replication_briefs/report.html`
     - `reports/site/plans/momentum_todo.html`
   - 只同步到：
     - `/var/www/momentum-report/reading/trendline_replication_briefs/report.html`
     - `/var/www/momentum-report/plans/momentum_todo.html`

## 验证 / 证据

本轮采用最小必要验证：

1. 本地页面 grep
   - `reports/site/reading/trendline_replication_briefs/report.html` 已出现：
     - `causal swing protocol v1`
     - `2-bar right confirmation`
     - `retroactively 重写`
   - `reports/site/plans/momentum_todo.html` 已出现对应的 TODO 进度说明。

2. 发布目录 grep
   - `/var/www/momentum-report/reading/trendline_replication_briefs/report.html` 已出现与本地一致的新约束；
   - 说明最小发布成功，线上静态目录已同步。

## 风险 / 边界

- 这轮没有新增实验结果，只是把 no-lookahead 边界从“提醒”升级成“明确协议”；
- `2-bar right confirmation` 只是当前 v1，后面仍可能比较 `1-bar / 2-bar / 3-bar` 对信号时效性的影响；
- 固定因果边界后，后续实验结果可能会比不严谨版本更弱，但这恰恰是好事：弱一点但可信，比强一点但偷看未来值钱得多。

## 下一步建议

1. 下一小步可以直接接这套协议做最小实验：
   - BTC / ETH / SOL
   - 15m
   - `baseline / confirm-1bar / confirm-2of3 / retest-hold`
2. 实验时优先额外记录：
   - `pivot_delay_bars`
   - `entry_lag_bars`
   - `false_break_ratio`
   - `post_cost_return`
3. 如果发现 `2-bar right confirmation` 把时效性伤得太重，再单独开一轮比较 `causal swing protocol v2`，而不是回退到模糊的 hindsight swing。

## Commit hash

- 本轮未提交。

## 如果未提交，说明原因

当前 worktree 里已有大量与本轮无关的脏文件、历史重建产物和其它线程修改。此时做 selective commit 仍然很容易混入无关内容，所以这轮仍只完成日志、邮件与最小页面发布，不做提交。