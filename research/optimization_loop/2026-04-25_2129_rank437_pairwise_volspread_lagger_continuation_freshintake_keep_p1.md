# Rank 437 / pairwise vol-spread lagger continuation fresh intake -> keep_P1

- 时间：2026-04-25 21:29 UTC
- 对象：`research/quant_digests/2026-04-25_2046_pairwise-volspread-lagger-continuation.md`
- 执行动作：fresh intake first verdict
- 对应 policy 约束：只补 1 个最小 decisive blocker，直接判断 `keep_P1` 或 `background/P0`

## 本轮要回答的唯一问题
这条 `leader 波动冲击 × lagger 方向跟随` 的 1m pairwise continuation，在当前公开证据下，是否已经能诚实保留一个不漂移主语的 survivor；还是仍只是依赖作者私有 pair schedule / 再训练的概念壳。

## 本轮最小 decisive blocker 检查
我只检查一件事：**离开作者私有 schedule 后，这个对象是否还剩下一个公开可定义、后续能做一次便宜 follow-up 的最小事件壳。**

结论：**有。**

原因不是作者收益曲线，而是 digest 里已经把最小公开壳拆得足够具体：
1. 主语不是抽象的“lead-lag”，而是明确的 `预排 leader/lagger pair 上的 1m shock -> lagger 在后续 1~3 bars 同向 follow-through`；
2. 触发条件可公开定义为 `sign(ret_leader_1m) * 1[abs(ret_leader_1m) > k * rv_leader]`；
3. pair 也能用公开滚动 `5d~10d` 的 lagged corr / hit-rate 自己生成，而不是必须复制 repo 私有 schedule；
4. repo 虽未公开核心 signal construction，但已经把失败边界说清：长 OOS 明显退化、pair schedule 需重拟合、成本门槛高；这反而说明后续唯一便宜检查可以很聚焦，而不是继续讲泛故事。

## 为什么这轮不是 background/P0
把它直接打回 `background/P0` 需要满足“除了作者私有实现外，没有剩余可检验主语”。当前并非如此。

当前仍然能留下一个明确 survivor：

> **Rank 437 / 公开滚动 pair-schedule 下的 `1m leader shock -> lagger 1~3 bar follow-through` raw alpha，值得做一次最小 follow-up，专门检查 event markout 是否只在作者私有 schedule 下成立，还是在公开 rolling pair generation + 最便宜 friction ladder 下也能留下可迁移信号。**

这条 survivor 没有漂移成别的主题：
- 没有改成 mean reversion；
- 没有切回跨截面 ranking；
- 没有扩成多因子交易壳；
- 也没有假装已经可直接 production。

## 当前未解决、但允许留到 survivor follow-up 的唯一 blocker
**唯一值得继续检查的 blocker**：

> 用公开 rolling pair generation 替代作者私有 schedule 后，`lagger` 的 `1m/2m/3m` event-conditioned markout 是否仍有方向单调性，并且在最便宜的 friction ladder 下没有立刻塌成纯噪声。

这正好符合一次 cheap follow-up 的范畴，因此本轮应保留到 `P1 survivor`，而不是提前升 `P2`。

## 本轮 verdict
- verdict: `keep_P1`
- 新 Rank：`437`
- 层级：fresh intake -> surviving candidate

## 一句话结果（写回 runtime）
`Rank 437 / pairwise vol-spread lagger continuation` fresh intake 首判为 `keep_P1`：虽然作者私有 pair schedule 不可复刻、长 OOS 退化也很重，但公开证据已足够保留一个不漂移 survivor——`公开 rolling pair-schedule 下的 1m leader shock -> lagger 1~3 bar follow-through raw alpha`；下一步只需做一次 cheap follow-up，检查 event markout 单调性与最便宜 friction 后是否仍剩可迁移信号。

## 尾部执行状态（non-blocking）
- homepage 刷新命令 `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` 异步进程最终被 `SIGKILL` 终止，按 policy 记为非阻断尾部失败，不回滚本轮 verdict/state/log。
- 邮件命令 `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot3-auto] Rank 437首判保留P1" --body-file /root/clawd/jerry/momentum/research/optimization_loop/2026-04-25_2129_rank437_pairwise_volspread_lagger_continuation_freshintake_keep_p1.md` 已成功发送。
