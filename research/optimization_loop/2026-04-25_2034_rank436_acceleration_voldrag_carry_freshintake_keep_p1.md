# Rank 436 / acceleration minus vol-drag carry fresh intake -> keep_P1

- Time: 2026-04-25 20:34 UTC
- Target: `research/quant_digests/2026-04-25_1950_acceleration-voldrag-carry-alpha.md`
- Slot: `Fresh intake -> Surviving candidate`
- Verdict: `keep_P1`
- Assigned rank: `436`

## Why this step was legal
按当前 `cycle_plan`，排在最前的 pending 小点就是该 fresh intake first verdict；本轮只执行这一项。

## Evidence actually used
从 digest 已给出的最小 portability probe 可直接读出三件关键事实：

1. `acceleration minus vol-drag carry` 作为横截面 raw alpha 并非空壳。
   - `15m` 直接 rebalance top-3 long-only：gross `+0.105 bps/bar`
   - `1h` refresh top-3 long-only：gross `+0.113 bps/bar`
   - `1h` refresh top-3 minus bottom-3：gross `+0.101 bps/bar`
   四组 probe 的 gross 全为正，说明“短窗加速度强、但 vol drag 更小”的相对排序在 short-cycle majors 上确有方向感。

2. 当前明确的 blocker 不是 alpha 本体失效，而是默认 taker 成本与换手。
   - `15m` top-3 long-only：turnover `14.14%/bar`，粗扣成本后 net `-0.461 bps/bar`
   - `1h` refresh top-3 long-only：turnover 降至 `7.76%/bar`，net 改善到 `-0.198 bps/bar`
   说明“降换手/更谨慎 execution”是会改变结论的唯一高杠杆方向，不是泛泛的再补点研究。

3. digest 已经把可继续验证的主语收束得足够具体。
   - 不是泛化的“多因子 repo 也许有东西”；
   - 也不是高换手的 top-bottom 对冲壳；
   - 而是：`12-coin majors 上每 1h refresh 的 top-N long-only carry router，并在 15m child execution 上压低摩擦`。

## Decision
将该对象保留为 `keep_P1`，并分配正式 `Rank 436`。

系统认知变化如下：

> `Rank 436 / acceleration minus vol-drag carry` 已具备一个不漂移主语的 survivor 结论：当前值得保留的不是“多因子框架”，而是 `12-coin majors 上每 1h refresh 的 top-N long-only carry router（15m child execution）`；唯一剩余 decisive blocker 是它能否在不改变主语的前提下，靠更低换手 / child execution / 最便宜 veto，把现有 gross edge 转成更接近可交易的 net 轮廓。

## Why not background/P0
若直接打回 `background/P0`，等于把“gross 持续为正、且 1h refresh 已明显改善 turnover/net”的对象与那些只有概念演示、没有具体下一步主语的 digest 混为一谈；这不符合当前 policy 对 `keep_P1` 的定义。

## Why not promote_P2
目前仍缺少一项最小 honesty/execution follow-up：验证 `1h parent -> 15m child` / 廉价 veto 是否真的能把成本继续压低，而不是仅凭“每小时更新好一些”就直接宣布 admission 充分。因此先停在 `P1 survivor` 合法，且只保留一次 follow-up 预算。

## Runtime writes completed
- `Fresh intake slot`：写回 `Rank 436 ... keep_P1`
- `Surviving candidate slot`：切换为 `Rank 436`，`followup_budget_remaining: 1`
- `cycle_plan[1]`：写回 result，并标记为 `done`

## Next-step guard
后续唯一合法 follow-up 应继续围绕同一个 decisive blocker：
- `1h parent -> 15m child` 是否能在不漂移主语的前提下改善净值/成本轮廓；
- 不得扩展成泛化多因子包装、也不得回到高换手 top-bottom 对冲。
## Tail execution status (non-blocking)
- Homepage publish: `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` 异步执行最终收到 `SIGKILL`，按 policy 记为非阻断尾部失败，不影响本轮已完成 verdict/state/log。
- Email notify: `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py ...` 已成功发送。
