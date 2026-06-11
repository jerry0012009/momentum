# 2026-03-27 17:02 UTC — Rank 62 park reframe

- Rank: `62`
- Theme: `continuation fail-fast overlay`
- Original status: `park`（authoritative verdict 保留）
- This round verdict: `keep_park`

## 为什么这轮看它
- 按当前 `PARK_REFRAME_QUEUE` 轮转规则，仍优先补看 `Rank 50+` 号段里已 `park` 但最近 `7` 天未被 `bot6` 复盘的条目。
- `Rank 62` 已在 2026-03-18 完成 source intake + minimal clean replication 后压回 `park / evidence pool`，但最近未见单独 reframe review，符合本轮“低频补位、不重复打同一条”的要求。

## 原 rank 为什么 park
参考：
- `research/optimization_loop/2026-03-18_1813_rank62-source-intake.md`
- `research/optimization_loop/2026-03-18_1830_rank62-clean-replication-park.md`
- `research/quant_digests/2026-03-18_1402_continuation-fail-fast-overlay.md`
- 近邻 exit / risk 证据：`research/optimization_loop/2026-03-18_2312_rank70-clean-replication-park.md`

原始故事是：不给三条 lane 再发明新 entry，而是给 `breakout_short / fib_retest_long / ema_psar_long` 补一层统一的 fail-fast 语言——`EMA fast` 失守、`session VWAP` flip、或 `0.75 ATR` 保护线被打穿，就更快认错离场。

但 minimal clean replication 的结论很清楚：
- `ema_psar_long`：有一点残余价值，`base≈-5.55% -> ema+atr≈-4.27% -> ema+vwap+atr≈-3.92%`，说明它**会缩小 loser size**；
- `fib_retest_long`：明显被过早砍掉，`base≈+0.88%`，叠加 fail-fast 后直接转负；
- `breakout_short`：没有被修好，反而更差，`base≈-2.58% -> ema+atr≈-3.25% -> ema+vwap+atr≈-3.12%`；
- `winner_truncation_rate` 很高（尤其 Fib），说明改善更像“太早认错”，不是更诚实地区分真假延续；
- `false_follow_through_4bars / 8bars` 也没有出现足够像样的统一改善。

所以原审计把它压回 `park / evidence pool` 是合理的：
**这条线证明“更快认错”在 `EMA continuation` 上可能有帮助，但没有证明“shared continuation fail-fast overlay” 这版角色值得继续排队。**

## 它更像 hard park 还是 soft park
我会把 `Rank 62` 定义为：**soft park，但偏硬**。

原因：
1. 不是 hard park，因为“entry 后更快承认 continuation 失败”这个主题本身没死；
2. 但又偏硬，因为它最初承诺的是跨三条 archetype 共用的 shared protocol，而 clean replication 已经清楚显示它**只在 `ema_psar_long` 留下薄 residual**；
3. 继续在原框架里磨阈值，大概率只是在“少亏一点 / 早砍一点”上做样本美化。

## 有没有“可救信号”
有，但很窄，而且更像**局部实现纪律**，不像可单独再立一个 queue-facing rank：
- `ema_psar_long` 上，`EMA+ATR` 型快认错确实比 baseline 少亏；
- 说明 continuation failure 这件事有信息量，尤其对 **EMA continuation 自己** 的 entry 后管理；
- 但这个残余不具备 shared 性：Fib 会被过度截断，breakout short 也没被修好。

换成人话：
**它留下的不是“一条三路通用 fail-fast alpha”，而更像“EMA continuation 别死扛”的本地纪律。**

## 最值得改的唯一一刀是什么
如果只保留唯一主修改轴，最值得改的一刀是：

**把 `shared fail-fast overlay` 降级成 `EMA-continuation-only failure protocol`。**

trade on：
- 不再假装这一层能横向服务 `breakout_short / fib_retest_long / ema_psar_long` 三条 lane；
- 只把它当成 `EMA continuation` 自己的 entry-after loss-control / failure protocol。

trade off：
- 放弃“shared overlay”这条原 Rank 62 的核心卖点；
- 代价是它不再是 queue-facing 通用层，而只是某一 setup 的本地 exit hygiene；
- 这类残余更像应该并入既有 EMA continuation / live runner 审计，而不是重新派生出独立新 rank。

## 是否值得形成新的 derived hypothesis
**不值得。**

原因：
1. 这条“唯一可救的一刀”本质上是在**撤销 shared 角色**，把它降成 `EMA continuation` 的本地管理细节；
2. 一旦这样改，它就不再像独立 queue-facing hypothesis，而更像应被吸收到既有 `EMA continuation / Rank 32b 类` 线里的 exit discipline；
3. 若硬写成 `Rank 62b`，会模糊原 `park` verdict 的审计意义，也会和近邻的 `Rank 70`（exit handoff）/ price-only risk-anchor 证据产生高重叠；
4. 目前还没有足够新证据说明它值得重新占据 fresh intake 位置。

## 本轮结论
- 结论类型：`keep_park`
- 原 rank 为什么 park：因为 shared fail-fast overlay 只在 `ema_psar_long` 少亏，对 Fib 是过早截断，对 breakout short 没修好；跨 lane 不一致，不足以继续排队
- 更像 hard 还是 soft：`soft park，但偏硬`
- 可救信号：`EMA continuation` 上的快认错 / 缩小 loser size 仍有一点残余
- 最值得改的唯一一刀：`把 shared fail-fast overlay 降级成 EMA-continuation-only failure protocol`
- 是否值得形成新的 derived hypothesis：`否`；这更像局部 exit discipline，应并入现有 continuation 审计，而不是再造 `Rank 62b`

## 对 queue 的最小写回建议
- `docs/PARK_REFRAME_QUEUE.md`：追加一条 recently reviewed
- `research/park_reframe/INDEX.md`：追加本轮索引
- 不改 `docs/TODO.md`

## Git / 工作区备注
- 当前工作区存在大量与本轮无关的既有脏文件；本轮只做最小写回，不做混合提交。
