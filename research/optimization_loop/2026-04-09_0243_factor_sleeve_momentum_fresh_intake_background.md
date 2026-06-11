# `winning factor sleeve × next-window continuation` / fresh intake → background / P0

- 时间：2026-04-09 02:43 UTC
- 执行角色：bot3
- 轮次来源：13 分钟自动执行轮次
- 依据文件：`docs/BOT2_BOT3_POLICY.md`、`docs/BOT2_BOT3_STATE.md`
- 对应 cycle_plan 小点：`research/quant_digests/2026-04-09_0116_factor-sleeve-momentum-xs-router-alpha.md`

## 本轮只执行的一个动作
作为当前首条 fresh intake，判断 `winning factor sleeve × next-window continuation` 是否真是新的独立 factor-rotation raw alpha，还是只是把已有 factor-sleeve / factor-momentum / XS router 线换个论文叙事再讲一次。

## 本轮新增的最关键事实
仓库里已经存在同主题、且更完整的前序对象：
- digest：`research/quant_digests/2026-03-31_0828_crypto-factor-momentum-sizevol-rotation-alpha.md`
- 首判：`research/optimization_loop/2026-03-31_0919_rank267_crypto_factor_momentum_sizevol_rotation_intake_keep_p1.md`
- 后续 admission / re-scope：`research/optimization_loop/2026-03-31_1240_rank267_p2_exit_rescope_to_p1_exmajors_scope.md`

也就是说，`factor sleeves -> sleeve-level winner rotation / factor momentum` 这条主语并不是今天才第一次被压出来；它早已被正式赋予 durable identity：`Rank 267`。

## 为什么这次不能再当 fresh intake 留在前排
这篇 2026-04-09 digest 虽然补了一个新的 `15m` liquid-major portability probe，但它没有跨过“旧主题重复叙事”这条线，原因有三：

1. **主语没有新到能脱离 Rank 267**
   这次写的核心句仍是：
   - 先构造 `momentum / size / volatility / liquidity / short-reversal` factor sleeves；
   - 再做 `recent winning factor spread -> next-window continuation` 的 sleeve rotation。

   这与 `Rank 267` 当初的正式主语——`cross-sectional factor sleeves (size / low-vol / short-horizon momentum) + sleeve-level winner rotation / factor momentum`——在对象级上是同一条线，不是新的 queue-facing pocket。

2. **新增 probe 还不足以推翻旧 blocker，反而更像重复确认**
   这次最显著的新信息是：
   - `mom24h` timed next-bar 约 `+0.55 bps / 15m`；
   - `short_reversal` 约 `+0.34 bps`；
   - 但论文里更强的 `size / volatility` 在 liquid-major `15m` transfer 上约 `-0.39 / -0.10 bps`。

   这并没有形成一个能把对象改写成全新前排 pocket 的新结论；相反，它只是再次说明：
   - broad `factor zoo` 不宜直接平移到 short-cycle liquid majors；
   - 真实可做的，仍更像“少数 sleeves 的窄 router / rotation”，而这正是 `Rank 267` 之前已经进入过、且后来又因 scope 诚实性被收窄过的路线。

3. **当前 evidence 仍停在“论文成立 + 15m 上有薄弱提示”**
   digest 自己也明确写了：
   - `先不要做大而全 34-factor zoo`；
   - 先做 `single sleeve` vs `sleeve router` A/B；
   - 先拆 `taker-taker` 与 `maker-ish` 成本；
   - 只有成本后仍优于单 sleeve，再考虑下钻到 `5m`。

   换句话说，这次新增信息仍主要是“值得继续测的一种 router 读法”，而不是“桌面上已经拿到独立、诚实、可分账的新 alpha pocket”。

## 正式 verdict
> `research/quant_digests/2026-04-09_0116_factor-sleeve-momentum-xs-router-alpha.md` 没有形成新的 fresh intake；它本质上是在复述并局部更新已有 `Rank 267` 的 factor-sleeve / factor-momentum 主语，而新增的 liquid-major 15m probe 也没有提供足以把对象从旧 blocker 中解放出来的新独立 pocket，因此本轮首判直接收口为 `background / P0`。

## 对 runtime 的直接影响
- `cycle_plan[1]` 应写成 `done`
- `cycle_plan[1].result` 应明确记为：
  - `2026-04-09 0116 factor-sleeve momentum` 不是新的 queue-facing pocket，而是旧 `Rank 267` 因子轮动线的重复叙事；新增 liquid-major 15m probe 仍未证明可独立前排，因此直接收口为 `background / P0`
- `Fresh intake slot` 应把当前 pending 目标顺延到下一条仍未执行的 fresh intake（即 `2026-04-09_0041_hyperliquid-xs-funding-carry-persistence-alpha.md`），同时把本轮 verdict 写入 `latest_result`
- `Background pool` 更新最新 parked 记录为本轮对象

## 一句话 result（供 state 回写）
`2026-04-09 0116 factor-sleeve momentum` 不是新的独立 fresh intake，而是在重复已有 `Rank 267` 的 factor-sleeve / sleeve-rotation 主语；新增 liquid-major 15m probe 仍只说明“少数 sleeves 值得继续 A/B”，没有形成可独立前排的新 pocket，因此本轮首判直接收口为 `background / P0`。
