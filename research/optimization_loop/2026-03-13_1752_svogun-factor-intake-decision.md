# 给 Svogun 2022 做第一张 factor intake decision：进候选库，但归类为 filter candidate

## 为什么这次选这个

这轮刻意按照 Jerry 刚刚提出的担心做纠偏：**不再继续补流程性页面，也不再只做“读完再整理”的动作，而是拿已经存在的本地复现/验证结果，直接做一个真实决策。**

当前最合适的对象不是 Fibonacci，而是 `Svogun 2022`：
- 它已经有 replication brief；
- 已经有本地 clean-room survival experiment；
- 已经有 cost / regime 两个现实约束切片；
- 也已经满足刚刚定义好的 `factor intake gate v1` 的大部分要求。

所以这轮最值钱的小步，不是再加来源卡，而是直接回答：**Svogun 2022 到底能不能进本地候选库？如果能，应该算 alpha / feature / filter 哪一类？**

这轮最值得复用/借鉴的点是：**文献有没有帮助，不只看有没有读懂，更看能不能把它压缩成一个会影响后续资源分配的明确判断。**

## 核心结论（中文摘要）

核心结论：**`Svogun 2022` 当前可以进入本地候选库，但角色应诚实标为 `filter candidate`，不是 `alpha candidate`。**

证据如何支持这个结论：**它已经有 clean-room 定义、最小本地验证、样本/统计口径，以及 cost + regime 两类现实约束切片；但从本地结果看，`rolling_breakout_20` 在 `60m_730d` 上虽然 gross 平均收益约 `+0.12%`，到 `net_high` 就转成约 `-0.18%`，说明这条线更像“告诉我们 breakout 研究必须过成本/制度过滤”的约束层，而不是一个可直接部署的赚钱 alpha。**

## 本轮做了什么改动

本轮只做一个主点：**给 Svogun 2022 做第一张 factor intake decision。**

具体改动：

1. 更新 `docs/TODO.md`
   - 在 `E3-C` 的第二条（shortlist 对象推进到 factor intake decision）下补进度说明：
     - 已先对 `Svogun 2022` 做第一张 `factor intake decision`；
     - 当前可进入本地候选库，但应标为 `filter candidate`，不是 `alpha candidate`。

2. 更新 `scripts/build_trendline_replication_briefs_report.py`
   - 在 `Factor intake gate v1` 后新增独立卡片：
     - `Factor intake decision #1 · Svogun 2022`
   - 明确写入：
     - 它为什么能通过 gate：
       - 已有 clean-room 定义；
       - 已有最小本地验证；
       - 已有样本与统计口径；
       - 已有 `gross / net_low / net_high` + `bubble_proxy` 现实约束切片；
     - 它为什么不是 alpha candidate：
       - `rolling_breakout_20` 在 `60m_730d` 上 gross 均值虽正（约 `+0.12%`），但 `net_high` 转负（约 `-0.18%`）；
       - 说明更有价值的是“为 breakout 研究提供 survival constraint”，不是直接提供策略主体。

3. 重建并发布最小必要页面
   - 重建：
     - `reports/site/reading/trendline_replication_briefs/report.html`
     - `reports/site/plans/momentum_todo.html`
   - 只同步到：
     - `/var/www/momentum-report/reading/trendline_replication_briefs/report.html`
     - `/var/www/momentum-report/plans/momentum_todo.html`

## 验证 / 证据

本轮采用最小必要验证：

1. 直接读取已有实验产物
   - `reports/artifacts/svogun2022_cost_regime_experiment/summary.json`
   - `overall_summary.csv`
   - `bubble_summary.csv`

2. 关键数字
   - `60m_730d / rolling_breakout_20 / gross`：
     - `trade_count=8205`
     - `mean_return ≈ +0.117%`
     - `positive_symbol_ratio = 75%`
   - `60m_730d / rolling_breakout_20 / net_high`：
     - `mean_return ≈ -0.183%`
     - `positive_symbol_ratio = 12.5%`
   - 说明：一旦计入更严成本，这条线从“纸面略正”快速退化成“明显不够资格当 alpha 主体”。

3. 页面 grep 验证
   - 本地与发布页都已出现：
     - `Factor intake decision #1 · Svogun 2022`
     - `filter candidate`
     - `not alpha candidate`
     - 以及 `gross 平均收益为正，但到 net_high 就转负` 这条核心证据。

## 风险 / 边界

- 这轮没有新增实验；是对已有本地复现结果做第一张正式 intake judgment；
- 它不意味着 `Svogun 2022` 现在就可以进正式策略层；
- 它的价值是：今后所有 breakout / trend 候选，都应该默认接受 cost / regime 生存性审查；
- 换句话说，它更像一个“研究约束因子”，不是一个“单独拿来赚钱的因子”。

## 下一步建议

1. 下一个最自然的小步，是对 `Fibonacci` 也做同样的 intake decision；
2. 但大概率结论会更保守：
   - 它现在还缺本地最小验证，所以暂时还不能升 candidate factor；
3. 如果要继续做更像“真找 alpha”的动作，下一步更值得做的是：
   - 用 `Fibonacci mini brief` 跑第一轮 15m clean-room 对照；
   - 或继续把 `pytrendline_event_validation_v3` 的 shortlist 往 OOS / stability 推一小步。

## Commit hash

- 本轮未提交。

## 如果未提交，说明原因

当前 worktree 里仍有大量与本轮无关的脏文件、历史重建产物和其它线程修改。此时做 selective commit 仍容易混入无关内容，所以这轮只完成日志、邮件与最小页面发布，不做提交。