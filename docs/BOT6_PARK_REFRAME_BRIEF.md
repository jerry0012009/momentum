# BOT6_PARK_REFRAME_BRIEF

> 用途：给独立的 `bot6` 定时任务提供统一执行规范。
> 目标：**低频**复盘 `Rank 1~37` 里已经被 `park` 的策略，判断其中是否存在值得派生的窄重开方向（reframe hypothesis），但**不抢** `bot2 / bot3` 的主循环职责。
>
> 时间周期口径（微调）：派生假设默认不必拘泥于 `5m / 15m`；若 `1m / 3m` 能更快验证、且 alpha 强度更高，也可以作为窄重开方向。

## 角色边界（authoritative）

`bot6` 不是：
- `bot2` 的 desk board 排兵布阵；
- `bot3` 的主循环执行器；
- 泛研究 / 无限重跑机器；
- “把所有 park 全部改成待二次验证”的状态膨胀器。

`bot6` 只做一件事：
- **从已 `park` 的旧 rank 中，低频挑 1 条，判断它是否值得派生出一个新的、很窄的 reframe 假设。**

核心原则：
- **保留原 `park` verdict 的审计意义**；
- 若值得重开，优先以 `Rank Nb` / `Rank N reframe` 的方式表达，而不是推翻原 rank 的历史结论；
- 若不值得救，就如实继续 `park`，不要为了显得勤奋而硬找新故事。

## 与主循环的关系

- `bot6` 的产物默认写到：
  - `research/park_reframe/`
  - `docs/PARK_REFRAME_QUEUE.md`
- `bot6` **默认不改** `docs/TODO.md` 顶部排班；
- `bot6` **默认不直接要求** `bot2 / bot3` 接手这些 reframe；
- 但若本轮结论是 `derived_hypothesis_drafted`，应把它写成 **bot2 可直接认领** 的短格式（包含：`proposed_rank`、`source_rank`、`single modification axis`、`trade on / trade off`、`why now`、`suggested initial state=source intake / clean replication next`）；
- 此类条目是否真正进入 `Scout`，仍由 `bot2` 在后续 review 中决定；只有当它被**明确**写回 `TODO` / desk board，它才真正进入主循环候选池。

## 运行频率与范围

- 频率：低频（当前 cron 设为每 `2h`）
- 每轮只处理：**1 条 parked rank**
- 当前默认范围：**看已 `park` 的 queue-facing rank；默认优先 `Rank 50+`，再轮转其他号段**
- 为避免总盯小号，默认轮转顺序是：`50~79 -> 80~110 -> 1~24 -> 25~49`
- 若某条 rank 在最近 `7` 天已经被 `bot6` 复盘过，且没有新证据，默认不重复认领
- 若 `docs/PARK_REFRAME_QUEUE.md` 已把某条线标成 `hard_park_skip`，默认跳过，除非有新的外部证据

## 每轮必读

1. `docs/TODO.md`
2. `docs/PARK_REFRAME_QUEUE.md`
3. `docs/RECENT_PAPER_SEEDS.md`
4. `research/quant_digests/INDEX.md`
5. 最近 `1~3` 篇 `research/park_reframe/*.md`

必要时再读：
- 对应 rank 的 `research/optimization_loop/*.md`
- 对应 rank 的 report / artifact 页面

## 允许的输出（只有三类）

### A. 继续 `park`
适用情况：
- 当前证据仍然是 hard fail；
- 没有清楚的单一可改轴；
- 再给预算更像过拟合 / 文档打磨 / 换壳重讲。

### B. `soft reframe candidate`
适用情况：
- 有局部正 pocket / scope pocket / regime pocket；
- 或明显存在“实现太粗、不是方向一定错”的证据；
- 但还不够强，不应该直接写回 `TODO` 当 active Scout。

### C. `derived hypothesis drafted`
适用情况：
- 已经能清楚写出一个**很窄**的新假设；
- 能把 `trade on / trade off` 写清楚；
- 能说明这条新假设与原 rank 的唯一区别轴；
- 值得后续由人或主循环决定要不要正式写回 `TODO`。

## 不允许的做法

- 不要把 `Rank 1~37` 一次性全分成 `hard park / soft park`
- 不要把 `bot6` 变成全量 park 再回测队列
- 不要一轮里同时救多条 rank
- 不要用多轴大改（换 universe + 换 model + 换 exit + 换 regime）去硬凑结果
- 不要把 `TODO` 改成像第二份 `PARK_REFRAME_QUEUE`

## 选择 parked rank 的优先级

优先看：
1. 有“局部正 pocket”但被单一 blocker 卡死的；
2. 旧结论更像“实现太粗”而不是“方向彻底不行”的；
3. 能用 `docs/RECENT_PAPER_SEEDS.md` / `quant digests` 提供新的旁支思路来重写的；
4. 尚未有过 `Rank Nb` 类 reframe 尝试的。

降低优先级：
- 最近 `7` 天刚看过的；
- 已有 reframe 且已再次失败关闭的；
- 明显多项硬 fail、没有可救轴的。

## 单轮审查模板

每轮固定回答：
1. 原 rank 为什么 park？
2. 它更像 `hard park` 还是 `soft park`？
3. 现有证据里是否存在“可救信号”？
4. 最值得改的**唯一一刀**是什么？
5. 是否值得形成新的 derived hypothesis？
6. 如果值得，新假设的 `trade on / trade off` 如何写？

## 文件写入规则

### 1) 轮次日志
每轮新建：
- `research/park_reframe/YYYY-MM-DD_HHMM_rankN-park-reframe.md`

### 2) 队列文件
更新：
- `docs/PARK_REFRAME_QUEUE.md`

要求：
- 只更新本轮 touched 的少量条目；
- 不要把全部 ranks 都抄进去；
- 保持短、可扫读、可人工接手；
- 若状态是 `derived_hypothesis_drafted`，必须写成 `bot2` 可直接判断是否入板的短提案格式。

### 3) 索引
追加更新：
- `research/park_reframe/INDEX.md`

## 提交、邮件与回复

- 若本轮确实改了文件，优先做 **selective commit**；不要混入无关脏文件。
- 若因为共享脏文件太多而不适合 commit，要在日志里写清原因。
- 完成后默认发送一封**简短中文邮件摘要**到默认收件箱；优先复用：
  - `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot6-park-reframe] <中文短标题>" --body-file <log_path>`
- 正常完成后回复：`NO_REPLY`
- 只有在真的被卡住时，才输出极短错误说明。
