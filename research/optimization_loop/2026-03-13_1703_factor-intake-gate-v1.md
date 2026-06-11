# 固定 factor intake gate v1：什么时候外部候选能从 reading 升到 factors

## 为什么这次选这个

这轮没有再扩新的文献来源，也没有立刻跳去跑新的小实验，而是补一个长期缺口：`E3-C. factor intake gate`。

最近几轮已经把 Fibonacci 这条线逐步推进到：
- 来源卡；
- 最小 reproducibility audit；
- secondary mini brief；
- causal swing protocol。

但如果没有一个统一的入库门槛，后面每个外部候选都会反复遇到同一个问题：**到底什么时候它还只是 reading 里的外部材料，什么时候才有资格升成我们本地的 candidate factor？**

所以这轮最合适的小步，是先把这个 gate 固定成 v1。这样后面不论是 Fibonacci、Svogun、还是未来的新候选，都可以按同一套纪律判断，而不是临场拍脑袋。

这轮最值得复用/借鉴的点是：**当候选池开始从“阅读”走向“本地验证”时，优先固定 admission gate，比继续堆更多来源更能减少后续判断漂移。**

## 核心结论（中文摘要）

核心结论：**`jerry/momentum` 现在已经固定了 `factor intake gate v1`：外部 replication candidate 只有在 clean-room 定义清楚、已有最小本地验证、样本与统计口径已报告、且至少做过一个现实约束切片之后，才有资格从 `reading/` 升到 `factors/`。**

证据如何支持这个结论：**本轮已把 `E3-C. factor intake gate` 在 `docs/TODO.md` 中正式勾掉，并把同一套规则写进 `Trendline Replication Briefs` 页面；本地页与发布目录都已出现 `Factor intake gate v1`、`已有最小本地验证`、`至少有一个现实约束切片`、以及“若第 1 / 2 项任一缺失则继续留在 reading/”这些明确门槛。**

## 本轮做了什么改动

本轮只做一个主点：**定义 factor intake gate v1。**

具体改动：

1. 更新 `docs/TODO.md`
   - 将 `E3-C. factor intake gate` 从 `[ ]` 改为 `[x]`；
   - 固定 `factor intake gate v1` 的 5 项最小要求：
     1. 核心事件 / 因子定义已 clean-room 明确；
     2. 已有最小本地验证结果（event study 或 MVP backtest）；
     3. 已报告样本量与最小统计口径；
     4. 已报告至少一个现实约束切片（交易成本/滑点、OOS、rolling、跨资产 中至少一项）；
     5. 已明确它更像 `alpha candidate / feature candidate / filter candidate` 中哪一类。
   - 同时写清默认决策纪律：
     - 若第 1 / 2 项任一缺失：继续留在 `reading/`，不能升到 `factors/`；
     - 若 1~4 都齐且角色判断清楚：可以升为“本地候选因子 / candidate factor”；
     - 若它主要价值只是过滤或确认层，不硬包装成 alpha。

2. 更新 `scripts/build_trendline_replication_briefs_report.py`
   - 新增独立卡片：`Factor intake gate v1（什么时候能从 reading 升到 factors）`
   - 把上面 5 条门槛与 3 条默认决策纪律网页化，方便所有 replication briefs 共用同一口径。

3. 重建并发布最小必要页面
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
     - `Factor intake gate v1`
     - `已有最小本地验证`
     - `至少有一个现实约束切片`
     - `继续留在 reading/`
   - `reports/site/plans/momentum_todo.html` 已出现同样的 gate 条目与门槛说明。

2. 发布目录 grep
   - `/var/www/momentum-report/reading/trendline_replication_briefs/report.html` 已出现与本地一致的 `Factor intake gate v1` 文案；
   - 说明最小发布成功，线上静态目录已同步。

## 风险 / 边界

- 这轮没有新增任何实验结果，只是把“什么时候允许入库”先固定成统一纪律；
- `gate v1` 是最小版本，后面如果本地验证变多，可能还会再细分为更强的 `alpha gate / feature gate / filter gate`；
- 现在先做 v1 的价值，不在于它完美，而在于它让后续每个候选都少走一遍“到底算不算本地因子”的口水仗。

## 下一步建议

1. 下一个最自然的小步，是把 `Fibonacci` 或 `Svogun` 用这套 gate 跑一遍，给出第一张明确的 `factor intake decision` 示例；
2. 更具体地说：
   - `Fibonacci` 当前大概率还停在 `reading/ -> secondary mini brief`，因为还缺最小本地验证；
   - `Svogun` 则更接近能做第一张 `filter candidate intake decision` 的对象。
3. 这样后面再出现新候选，就能直接复用同一模板，而不是重写判断标准。

## Commit hash

- 本轮未提交。

## 如果未提交，说明原因

当前 worktree 里仍有大量与本轮无关的脏文件、历史重建产物和其它线程修改。此时做 selective commit 容易把无关内容混入，所以这轮仍只完成日志、邮件与最小页面发布，不做提交。