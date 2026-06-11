# 给 Gurrib 2022（Fibonacci 回撤）补来源卡与最小 reproducibility audit

## 为什么这次选这个

这轮继续沿最近的 E 模块线程推进，但刻意不再停留在“只新增一篇 digest”。

刚刚已经有一篇新的 quant digest：`2026-03-13_1337_fibonacci-retracement-pullback-confirmation.md`。如果只停在 digest，它对后续 alpha 研发的帮助还不够直接；更有价值的小步，是把这篇材料正式推进成：

1. 一张可审计的来源卡；
2. 一条最小 reproducibility / honesty audit；
3. 一个明确的 clean-room 入口；
4. 网页侧可见的 scout board 更新。

这轮最值得复用/借鉴的点是：**Fibonacci 回撤位这类材料，最好的用法通常不是直接当独立 alpha，而是把它降到 `pullback / breakout confirmation layer` 来看，并优先测试短确认窗口。**

## 核心结论（中文摘要）

核心结论：**`Gurrib et al. (2022)` 当前更适合作为 `pullback / breakout confirmation layer` 参考，而不是第一批 active replication 主候选。**

证据如何支持这个结论：**这篇论文全文可得、规则定义可读，也给了回测结果；但它没有公开官方代码，交易成本 / OOS 讨论偏弱，样本也不厚，而且论文里真正最可迁移的正面信息是“短窗口连续突破更常见、回撤位更适合当确认层”，而不是一个足够稳的独立 alpha 主体。**

## 本轮做了什么改动

本轮只做一个主点：**把 Gurrib 2022 从 digest 推进成来源卡 + 最小 audit + 网页可见条目。**

具体改动：

1. 更新 `docs/LITERATURE_TRENDLINE_SIGNAL_MAP.md`
   - 新增来源卡：
     - `Energy crypto currencies and leading U.S. energy stock prices: are Fibonacci retracements profitable?`
   - 明确写入：
     - `source_type = paper`
     - `fulltext_access = full_text`
     - `evidence_status = digest_done`
     - `fit_for_us = filter_candidate`
   - 在卡片中补齐：
     - 论文研究对象 / 市场 / 样本
     - Fibonacci-only 与 MA crossover 的结构定义
     - 回测证据的可读结论
     - 无官方代码、成本/OOS偏弱、样本偏薄等风险
     - 最小 clean-room 入口

2. 更新 `docs/TODO.md`
   - 在 `E2-A. 第一轮候选池` 下补进度说明：
     - 已新增 `Gurrib et al. (2022)` 来源卡；
     - 当前最可复用的点不是把 Fibonacci 回撤位当独立 alpha，而是把它当 `pullback / breakout confirmation layer`。
   - 在 `E2-B. 质量审计` 下补进度说明：
     - 已为 `Gurrib et al. (2022)` 补最小 audit；
     - 当前定位为 `confirmation / retest / filter reference`，优先做短窗口 pullback confirmation 对照。

3. 更新 `scripts/build_trendline_alpha_scout_report.py`
   - 在种子材料表里新增：
     - `Fibonacci retracement pullback confirmation`
   - 在侦察结论里补一句：
     - `Gurrib et al. (2022)` 当前先不升为主 replication candidate，最值得转写的是“确认窗口要短、回撤位更适合作为过滤层而不是独立 alpha 主体”。

4. 重建并发布页面
   - 重建：
     - `reports/site/plans/momentum_todo.html`
     - `reports/site/reading/trendline_alpha_scout/report.html`
   - 已发布到站点。

## 验证 / 证据

本轮采用最小必要验证：

1. 内容 grep 验证
   - `docs/LITERATURE_TRENDLINE_SIGNAL_MAP.md` 已出现 `Gurrib` 来源卡；
   - `docs/TODO.md` 已出现 `Gurrib et al. (2022)` 的 intake / audit 进度说明；
   - `reports/site/reading/trendline_alpha_scout/report.html` 已出现：
     - `Fibonacci retracement pullback confirmation`
     - 以及它作为 `pullback / breakout confirmation layer` 的结论说明。

2. 页面重建与发布
   - 执行：
     - `./.venv/bin/python scripts/build_plans_site.py`
     - `./.venv/bin/python scripts/build_trendline_alpha_scout_report.py`
     - `./scripts/publish_report_site.sh`
   - 结果：发布成功，站点已更新到 `https://jp.jerrypsy.top/momentum/`。

## 风险 / 边界

- 这轮没有新做本地回测或 replication brief，只是把 digest 正式推进成可审计来源卡与最小 audit；
- `Gurrib 2022` 的主样本是能源股 + 能源相关 crypto 的日频，不是我们主战场的 BTC/ETH 15m；
- 它最值得学的是“确认层结构”和“短窗口确认”，不是照搬参数；
- 这次为了发布页面，`publish_report_site.sh` 会顺带重建一批现有 reading / factors 页面，因此工作区出现了不少与本轮主点无关的已修改产物；这不影响本轮结论，但会影响是否适合立即提交。

## 下一步建议

1. 如果继续沿这条线走，最合适的下一小步是：
   - 单独补一个 `Fibonacci pullback confirmation` 的 clean-room mini brief；
2. 更具体地说，优先做：
   - `裸 pullback entry vs confirm-1bar vs confirm-2of3 vs retest-hold`
   - 在 15m BTC/ETH/SOL 上的最小对照；
3. 当前不建议直接把它升成主 replication candidate，也不建议直接把 Fibonacci 位当独立 alpha 主体。

## Commit hash

- 本轮未提交。

## 如果未提交，说明原因

当前 repo/worktree 里已有大量与本轮无关的脏文件和重建产物；同时 `publish_report_site.sh` 还会顺带刷新多个 reading / factors 页面。此时做 selective commit 容易把无关改动一并带入，所以这轮先不提交，只保留日志、邮件与站点更新。