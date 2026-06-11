# 把 Fibonacci 线补成 secondary mini brief，直接对接 15m 最小验证

## 为什么这次选这个

这轮继续沿上一轮刚推进的 `Gurrib et al. (2022)` 线程往前走，但仍然控制在一个很小的闭环里。

上一轮已经做完：
- 来源卡；
- 最小 reproducibility audit；
- scout board 更新。

如果这轮再去新开来源，就会把刚建立起来的判断链条打断。当前更合适的一小步，是把这条 Fibonacci 线从“只是一个 scout / digest 对象”，继续推进成一个 **可直接开做的 mini brief**：后面谁来接这条线，都可以直接按固定实验设计去做 15m 最小验证，而不用再重新定义问题。

这轮最值得复用/借鉴的点是：**对于证据质量一般、但机制启发很强的外部材料，最好的推进方式往往不是急着升成 shortlist 主候选，而是先补成 `secondary mini brief`，把最小 clean-room 实验路径写死。**

## 核心结论（中文摘要）

核心结论：**`Gurrib et al. (2022)` 现在已经从 scout 卡进一步补成了 `secondary mini brief`，后续可以直接按 `裸 pullback vs confirm-1bar vs confirm-2of3 vs retest-hold` 在 15m crypto 上做最小 clean-room 对照。**

证据如何支持这个结论：**本轮已把这条 Fibonacci 线写进 `Trendline Replication Briefs` 页面，明确了数据口径、因果边界、最小事件定义、四组对照实验和成功标准；同时 `TODO.md` 镜像页也已同步写明：它当前仍不是 shortlist 主候选，而是服务后续 pullback / confirmation 小实验的 secondary mini brief。**

## 本轮做了什么改动

本轮只做一个主点：**给 Fibonacci 线补 mini brief。**

具体改动：

1. 更新 `scripts/build_trendline_replication_briefs_report.py`
   - 在“当前已落地页面”里加入：
     - `Fibonacci Pullback Confirmation · Quant Digest`
   - 新增一个独立卡片：
     - `Brief E · Fibonacci pullback confirmation (Gurrib et al., 2022)`
   - 在 brief 里明确：
     - 它当前定位为 `secondary mini brief`
     - 不复刻原论文日频收益数字；
     - 只复刻对当前主线最有价值的部分：`recent-window swing high/low -> Fibonacci 回撤位 -> 作为 pullback / breakout confirmation layer`
     - 15m 最小实验设计：
       1. `baseline`：裸 pullback entry
       2. `confirm-1bar`
       3. `confirm-2of3`
       4. `retest-hold`
     - 关键指标：
       - `false_break_ratio`
       - `max_drawdown`
       - `post_cost_return`
     - 成功标准：
       - 不是要求 Fibonacci-only 收益最好看；
       - 而是要求确认层设计能否在不过度伤害收益的情况下，压低假突破 / 假回踩与回撤。

2. 更新 `docs/TODO.md`
   - 在 `E3-A. shortlist 机制` 下补进度说明：
     - 已把 `Gurrib et al. (2022)` 追加成 `secondary mini brief`；
     - 当前用途是给 15m `裸 pullback vs confirm-1bar vs confirm-2of3 vs retest-hold` 做最小 clean-room 对照；
     - 仍不升为 shortlist 主候选。

3. 重建最小必要页面
   - 重建：
     - `reports/site/reading/trendline_replication_briefs/report.html`
     - `reports/site/plans/momentum_todo.html`

4. 发布最小必要页面
   - 没有再跑整套 `publish_report_site.sh`；
   - 只把这两个已重建页面同步到：
     - `/var/www/momentum-report/reading/trendline_replication_briefs/report.html`
     - `/var/www/momentum-report/plans/momentum_todo.html`

## 验证 / 证据

本轮采用最小必要验证：

1. 本地页面 grep
   - `reports/site/reading/trendline_replication_briefs/report.html` 已出现：
     - `Brief E · Fibonacci pullback confirmation (Gurrib et al., 2022)`
     - `secondary mini brief`
     - `confirm-1bar`
   - `reports/site/plans/momentum_todo.html` 已出现：
     - `Gurrib et al. (2022)`
     - `secondary mini brief`
     - `裸 pullback vs confirm-1bar vs confirm-2of3 vs retest-hold`

2. 发布目录 grep
   - `/var/www/momentum-report/reading/trendline_replication_briefs/report.html` 已出现与本地一致的新 brief 文案；
   - 说明最小发布成功，线上静态目录已同步。

## 风险 / 边界

- 这轮没有做新的本地回测，只是把实验设计写成可执行 brief；
- 这条线当前仍不适合升为 active replication 主候选；
- 若后续做 15m clean-room 实验，最需要警惕的是：
  - swing high / low 定义是否 causal；
  - 是否把 hindsight 的回撤结构偷偷带进入场判断；
- 当前 repo/worktree 里仍有大量与本轮无关的脏文件和重建产物，因此这轮不适合贸然提交。

## 下一步建议

1. 下一小步可以直接接这张 brief，不必再重新定义实验：
   - BTC / ETH / SOL
   - 15m
   - `baseline / confirm-1bar / confirm-2of3 / retest-hold`
2. 若实验结果只改善回撤、不改善收益，也仍然有价值——它可能更适合作为 filter / confirmation candidate，而不是 alpha 主体。
3. 若短窗口确认完全没有帮助，则这条 Fibonacci 线可以很快收口，不必继续占主线资源。

## Commit hash

- 本轮未提交。

## 如果未提交，说明原因

当前 worktree 里已有大量与本轮无关的脏文件、历史重建产物和其它线程的修改。虽然本轮改动本身很小，但此时做 selective commit 仍然容易把无关内容混进去，所以这轮只完成日志、邮件与页面发布，不做提交。