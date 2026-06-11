# 2026-03-20 14:10 UTC · Rank 22 park reframe review

## 本轮为什么选 Rank 22
- 本轮仍只处理 **1 条** 已 `park` 的 `Rank 1~37`。
- 最近 `7` 天内，`Rank 22` 还没有被 `bot6 park-reframe` 单独复盘过。
- 它属于已经完成 `clean replication + Light Stability Pack`、但尚未做过低频 reframe 判断的旧 parked 条目，适合做一次“是否还值得派生新窄假设”的审计。

## 先看原 park 为什么成立
依据：`research/optimization_loop/2026-03-17_0437_rank22-clean-replication-park.md`

原始定义是：
- 保留 `baseline multi-tf momentum` 方向层；
- 只有当最近 4 根收盘连续站在 `MA20` 同侧，并满足 `upwave / downwave` 形态时才允许入场。

原 park 的硬证据很直白：
- 主变体 `updownwave_ma20` 在 `6bps/side` 下仍约 **`-7.94%`**，`positive_asset_ratio = 1/3`；
- 邻域最不差的 `MA15` 也只有约 **`-3.26%`**，只是少亏；
- 时间上 `bucket_2 ≈ -12.70%`，没有稳定覆盖；
- 跨资产只剩 `SOL` 单腿为正，`BTC / ETH` 都明显为负；
- 成本升到 `10/15/20bps` 后继续恶化到约 **`-27.51% / -46.17% / -59.98%`**。

所以原结论并不是“这条线完全没信息”，而是：**它更像减亏过滤器，不像能独立成立的 queue-facing alpha / paper candidate。**

## hard park 还是 soft park？
**本轮判断：更像 `soft park`。**

原因：
- `persistence / reclaim / recovery` 这个主题本身没有死；
- 但 `Rank 22` 采用的具体写法——`multi-tf momentum + 固定 MA20 同侧 4 连收 + wave 形态`——已经被审计成“方向太粗、角色也放错了”；
- 它的问题更像 **把一个可能只适合做 long-side admission / recovery 质量过滤的东西，写成了可直接开仓的 standalone gate**。

也就是说，原 `park` 应保留，但它不是那种“主题本身已被彻底证伪、再看都是浪费时间”的 hard park。

## 有没有可救信号？
**有，但很弱，而且已经被邻近证据大幅消费。**

本轮看到的可救信号主要有两类：
1. `Rank 22` 自身 clean replication 已经说明：它确实比 baseline 少亏，说明 `persistence / recovery` 不是完全无信息；
2. 近两天的新 digest 反复给出同一方向的更诚实读法：
   - `2026-03-20_0426_ema-close-reclaim-not-raw-alpha.md`：`EMA close reclaim` 只够做 **Fib / EMA long-side 的减亏 admission layer**，不够救活 raw alpha；
   - `2026-03-20_1353_rsi-state-machine-admission-not-shared-short-gate.md`：`RSI enter→exit→re-enter` 更像 **long-side 稀疏 admission**，不适合 shared short gate；
   - `Rank 17 pullback recovery confirmation` 已经在更诚实的 scope 下被推进到 **`narrow paper pilot approved（ETH+SOL only）`**。

这些证据共同说明：
- “回踩后恢复 / 重新站回防守线 / 持续性恢复”这条主题 **可能还有信息**；
- 但最自然、最诚实、最接近 queue-facing 的那条窄救法，已经被 **`Rank 17` + 最近 long-side admission digests** 基本消费掉了。

## 最值得改的唯一一刀是什么？
如果硬要切，唯一还算诚实的一刀只能是：

**把 `standalone up/down wave + MA20 persistence gate` 降级成 long-side sparse recovery admission layer。**

也就是：
- 不再让它自己决定完整 entry；
- 只在已有 `Fib retest_hold / EMA continuation long` 出现时，额外要求一个“先失守再收回、且恢复保持短暂持续性”的最小 recovery 状态；
- 同时默认不镜像给 breakout-short。

## 这唯一一刀值不值得形成新的 derived hypothesis？
**本轮结论：不值得，维持 `keep_park`。**

原因不是这刀完全荒唐，而是它已经没有足够独立的新意：
- 这条“降级成 long-side recovery admission layer”的救法，和 `Rank 17` 已经存活的 `pullback recovery confirmation` 主旨高度重叠；
- 同时又与 `EMA close reclaim`、`RSI state-machine admission` 这两条近期 digest 给出的 long-side 稀疏 admission 读法高度同向；
- 如果现在再派生一个 `Rank 22b`，很大概率只是把同一主题换壳重写，审计价值低，且容易稀释原 `park` 结论的边界。

换句话说：
- **原 Rank 22 的失败结论要保留；**
- **它更像 soft park，而不是 hard park；**
- **可救信号存在，但最自然的单轴救法已被近邻存活线和近期 digest 基本消费，因此当前不再单独起一个新派生号。**

## 本轮最终结论
- `verdict = keep_park`
- `original park verdict kept = yes`
- `park type = soft park`
- `derived hypothesis drafted = no`

## 给 bot2 / bot3 的边界说明
- 这轮**没有**推翻原 `park`；
- **没有**改 `docs/TODO.md` 顶部排班；
- **没有**新增 `Rank 22b`；
- 只是在低频审计上补了一句更清楚的话：
  - `Rank 22` 失败的不是“恢复/持续性主题完全没信息”；
  - 而是“把它写成 standalone queue-facing gate 的这版职责已经被否掉”；
  - 其最自然的 long-side admission 救法已被 `Rank 17` 与近期 digest 基本消费，当前不必重复派生。
