# Rank 441 / 7d vol-scaled TSMOM × shared cost budget — fresh intake keep_P1
- 时间：2026-04-26 01:00 UTC
- 执行器：bot3
- 对应 cycle_plan 小点：#3
- 结论：`keep_P1`
- 正式 Rank：`441`

## 本轮执行内容
对 `research/quant_digests/2026-04-25_2158_sharedcost-tsmom-lowerturnover-router.md` 做 fresh intake first verdict，只回答一个最小 decisive blocker：这条对象到底能不能从“shared-cost 下趋势比反转更厚”进一步收束成一句值得保留 survivor 的 queue-facing raw alpha 主语。

## 读后收口
可以，且应当收口成比 digest 标题更窄的一句：

> 慢速 `1h` parent trend（7d/14d vol-scaled continuation）可以作为 `15m` child direction router / admission layer；它不是诚实的裸 `15m` taker 趋势主系统，真正该保留的是“先给快触发层方向许可”的壳。

这句主语之所以成立：
1. digest 已明确 repo 的胜出分支不是短周期均值反转，而是更慢的 TSMOM；
2. portability probe 里，直接把它粗暴映射成 `15m` 裸 taker 主策略并不厚，说明不能把它包装成“15m 趋势 alpha 已验证”；
3. 但当只把慢速 trend 当成 parent direction gate 时，事件口径仍保留正向 signed return（尤其 `BNB/BTC` 子样本不差），足以支持它进入一次 survivor follow-up；
4. 因此它的 reader-facing 价值不是“趋势比反转好”，而是“慢信号更适合做 child execution 的方向 admission”。

## 为什么不是 background/P0
如果全文只能提供“趋势在 shared-cost 下比反转更便宜”这种方法论提醒，那应直接去 background pool；但当前 digest 已经给出足够具体的可检验主语：
- parent：`1h` 慢趋势 / `7d` 左右 vol-scaled continuation
- child：`15m` 方向 router / admission
- 下一步唯一便宜检查：在 majors 上看这条 parent->child 许可关系是否可迁移，以及是否只是低换手趋势换写法

这已经超过泛泛研究姿势，足以保留 1 次 survivor 跟进。

## 为什么还不能升 P2
当前证据仍停留在 first verdict：
- 还没有完成 majors portability 的最小 follow-up；
- 还没有把 child trigger 的 honesty / execution realism 说清（pullback、breakout、microburst 哪类 admission 才是真正可跑的，不是事后挑样本）；
- 当前更像 parent-direction hypothesis，而不是完整 pre-paper admission。

因此本轮只应 `keep_P1`，不应直接 `promote_P2`。

## runtime 回写
- 分配新 Rank：`441`
- Fresh intake slot 更新为：`Rank 441 / 7d vol-scaled TSMOM × shared cost budget`
- Surviving candidate slot 更新为：`Rank 441 / 7d vol-scaled TSMOM × shared cost budget`
- survivor budget：`1`

## 会改变系统认知的一句话
`Rank 441 / 7d vol-scaled TSMOM × shared cost budget` 不是“趋势比反转便宜一点”的方法论摘要，而是可保留为 `P1` 的具体主语：慢速 `1h` parent trend 可作为 `15m` child direction router / admission layer，值得做 1 次最小 majors portability / child-trigger honesty follow-up。

## 尾部步骤状态（异步回执）
- homepage publish：`bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` 异步回执为 `SIGKILL` 终止，按 policy 记为非阻断尾部失败，不影响本轮 verdict / state / rank 回写。
- 邮件通知：已发送（`[momentum-bot3-auto] Rank 441 保留为P1`）。