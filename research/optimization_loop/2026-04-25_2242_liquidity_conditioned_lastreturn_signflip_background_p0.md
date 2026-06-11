# liquidity-conditioned last-return sign flip — first verdict background/P0
- 时间：2026-04-25 22:42 UTC
- 对象：`research/quant_digests/2026-04-25_1846_liquidity-conditioned-lastreturn-signflip.md`
- 执行动作：fresh intake first verdict
- 结论：`background/P0`

## 本轮只回答一个最小 decisive blocker
这条 intake 要想合法进入 survivor，必须先收束成一句新的、可继续 cheap follow-up 的具体主语，而不能只是重复“liquidity 可能决定 momentum/reversal 符号”的框架叙事。

我用的最小 blocker 不是再扩做新回测，而是检查它是否已经提供了**新的 queue-facing alpha 主语**。

## 为什么本轮直接收口到 background/P0
### 1) 它没有提供新的前排对象，而是在重复已存在框架
仓库里已经有：
- `research/quant_digests/2026-04-04_2355_liquidity-split-lastday-return-xs-alpha.md`
- `research/optimization_loop/2026-04-04_2359_rank336_liquidity_split_lastday_return_xs_first_verdict_keep_p1.md`

也就是 `Rank 336 / liquidity-split last-day return cross-sectional` 这条线早就把同一个核心框架写清楚了：
- 同一个 `24h last return` feature，方向可能随 liquidity bucket 改变；
- 前排上真正值得 desk 化的是 liquid-major 版本，而不是泛泛的全市场 sign-router 故事。

因此，本条 2026-04-25 digest 若想成为新 intake，必须比 `Rank 336` 更进一步，给出一个**新的、可独立命名的可执行主语**。它没有做到。

### 2) 当前 public probe 也没有验证出稳定的 liquidity sign-flip 边界
本条 digest 自己给出的最小公开快检结论是：
- 在 `liquid majors` 10 币桶里，最近样本上 `24h` loser-bounce **reversal** 为正；
- 在次一级 `mids` 10 币桶里，无论 momentum 还是 reversal 都接近 0；
- 也就是说，最新公开 probe 并没有给出一个可迁移的“高流动性 continuation / 低流动性 reversal”边界，反而更像：
  - majors 有一条 loser-bounce；
  - mids 不厚；
  - 所谓 liquidity-conditioned sign flip 仍停留在方法论层，而不是可直接排进 survivor 的具体对象。

### 3) 所以它不满足 keep_P1 的门槛
本轮 `keep_P1` 需要的是一句具体主语，例如：
- “rolling liquidity top bucket 上的 24h winner continuation 值得做一次 child execution follow-up”，或
- “majors 24h loser-bounce 在最便宜成本后仍值得做一次 long-leg attribution follow-up”。

但当前 digest 没有把对象收束到这种程度；它更像对既有 `Rank 336` 主题的重复表述，而且最新 probe 还削弱了原本的 sign-flip 主张。

## 会改变系统认知的话
`liquidity-conditioned last-return sign flip` 并未形成新的 survivor：它只重复了已存在的 `Rank 336 / liquidity-split last-day return` 框架，而最近 Binance 20 币快检又没有验证出可迁移的 liquidity sign-flip 边界，因此本条 intake 诚实收口到 `background/P0`。

## 对 runtime 的影响
- 不分配新 Rank（因为 verdict 为 `background/P0`）
- 不改 `Fresh intake slot` / `Surviving candidate slot` / `Active P2 slot`
- 仅将当前 `cycle_plan` 第 4 项写为 `done`

## 尾部执行状态（非阻断）
- `publish_homepage_index.sh` 异步进程最终返回 `SIGKILL`（session: `lucky-sh`）。
- 按 policy 归类为尾部 publish 失败，不影响本轮已完成的 verdict / state / 日志。
- 邮件通知步骤已先成功发送（`[momentum-bot3-auto] 流动性分层 sign-flip 收口 P0`）。
