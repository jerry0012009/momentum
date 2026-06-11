# 2026-04-09 21:11 UTC — factor-sleeve momentum router fresh intake first verdict

## 执行对象
- `research/quant_digests/2026-04-09_0116_factor-sleeve-momentum-xs-router-alpha.md`
- 角色：`Fresh intake slot` 的当前唯一 pending 小点

## 本轮要回答的问题
`winning factor sleeve × next-window continuation` 在当前 `15m` liquid-major universe 里，是否已经窄到足以成为一个**独立、desk 可执行**的 raw alpha pocket，而不是高换手、低容量、易样本幻觉的元路由想法。

## 最小证据回看
直接采用 digest 里已经写明、且足以决定 first verdict 的 portability probe：
- universe：近约 `70d`、`10` 个 liquid majors、`15m`
- sleeves：`24h momentum / size / volatility / liquidity / short-reversal`
- factor-momentum timing 结果：
  - `mom24h` timed next-bar 约 `+0.55 bps / 15m`，胜率约 `51.4%`
  - `short_reversal` timed next-bar 约 `+0.34 bps`
  - 论文摘要里更强的 `size / volatility` 在这份 liquid-major `15m` transfer 上约 `-0.39 / -0.10 bps`

## first-verdict 口径
这条线当前**不够格保留为 P1**，原因不是“论文不成立”，而是对 desk 当前可执行口径来说，它还没有收敛成独立 pocket：

1. **edge 太薄，离成本缓冲太近**
   - 当前能迁移的只剩 `mom24h` 与一点点 `short_reversal`；按 `15m` router 的典型换手，这个量级很容易被 taker fee、滑点、选 sleeve 噪音吃掉。

2. **最有说服力的论文主结论没有迁移到当前 desk 口径**
   - digest 明确写了论文摘要里最强的是 `size / volatility` 相关 anomaly；但在 liquid-major `15m` transfer 上并未复制。
   - 这意味着当前可交易 universe 里的可迁移部分，不是论文主信号本体，而只是一个更弱、更窄的子集。

3. **它更像 overlay/router，不像独立 alpha pocket**
   - 现有结果更像“在若干已有 sleeves 之间做轻微择时”，而不是单独拿出来就能稳定兑现的 raw alpha。
   - 如果单 sleeve 本身还没在当前 desk 成本口径下稳定存活，那么在 sleeves 之上再套一层 momentum router，默认更容易变成高换手元策略幻觉。

4. **当前唯一诚实延伸方向不是继续 keep_P1，而是将来在已存活 sleeve 之上 reopen**
   - 如果未来已有 `funding / basis / short-reversal / XS momentum` 某几条 sleeve 先被证明单独可交易，那么“router 是否提升 post-cost expectancy”可以作为二层组合问题重开。
   - 但这不是当前 fresh intake first verdict 应该保留在前排的理由。

## 结论
- first verdict：`background / P0`
- 不分配 Rank
- 不进入 `Surviving candidate slot`

## 会改变系统认知的一句话
`winning factor sleeve × next-window continuation` 在当前 liquid-major `15m` transfer 上只表现为极薄、依赖少数 sleeve 的高换手上层路由想法；论文里更强的 `size/volatility` 主信号未迁移成功，因此它还不是可独立兑现的 raw alpha pocket，fresh intake first verdict 收口为 `background / P0`。
