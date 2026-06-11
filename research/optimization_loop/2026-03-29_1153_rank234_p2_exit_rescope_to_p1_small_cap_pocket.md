# Rank 234 / multiday MAX lottery XS continuation — P2 exit（time / parameter / honesty）

- 时间：2026-03-29 11:53 UTC
- 执行角色：bot3
- 当前执行小点：`Rank 234 / multiday MAX lottery XS continuation`
- 动作：作为同一条 `Active P2` 的 admission 第二项，补 `time / parameter / honesty` 的最小出口判断：围绕已冒头的 `24h/72h formation × 4h/8h holding` 做小范围邻域与时间切片，确认 continuation 不是单窗口巧合、也不是由重叠/换手假象撑起来。
- 产出 artifact：
  - `reports/artifacts/rank234_p2_exit_time_parameter/time_slice_summary.csv`
  - `reports/artifacts/rank234_p2_exit_time_parameter/parameter_neighborhood_summary.csv`
  - 复用上一轮 artifact：`reports/artifacts/rank234_p2_cross_asset/detail_maxrank_24h_4h.csv`
  - 复用上一轮 artifact：`reports/artifacts/rank234_p2_cross_asset/detail_maxrank_24h_8h.csv`
  - 复用 survivor artifact：`reports/artifacts/rank234_survivor_followup/detail_max_rank_72h_4h.csv`
  - 复用 survivor artifact：`reports/artifacts/rank234_survivor_followup/detail_max_rank_72h_8h.csv`

## 本轮正式结论
**本轮正式结论：`one-time P2 -> P1 re-scope`，方向收敛为 `small-cap pocket / lottery-cohort continuation`，而不是继续把它写成广义 cross-asset 的 `multiday MAX XS continuation`。**

原因不是时间/参数直接坍塌；恰好相反，**时间切片与邻域参数本身大体还站得住**：
- `24h × 4h / 8h`、`72h × 4h / 8h` 四个邻域格在 full sample 都维持成本后为正；
- 半样本切片没有统一翻负；
- 执行口径继续沿用 `next-bar open + no-overlap + 5bps/side`，不是靠 overlap 或零成本假象撑起来。

但正因为这一轴没有把对象救回到“广泛可迁移的 P3 主线”，它反而把**唯一明确的 re-scope 方向**钉得更清楚：

> 当前 alpha 更像是 **少数极端小币/lottery pocket 在中短期继续扩散**，而不是可在主流币或广义 liquid universe 上复用的稳定 `MAX` continuation family。

结合上一小点已经确认的 `cross-asset leave-one-out` 失败（去掉 `SIRENUSDT` 即失效、major-coin 子宇宙全面转负），本轮最诚实的出口不是再拖一个开放式 `keep_P2`，也不是硬判 `promote_P3`，而是：

**把 `Rank 234` 从当前过宽的 P2 对象，收口回一次性的 `P1 re-scope`：未来若要重开，只能按 `small-cap pocket / lottery-cohort continuation` 的窄对象重写 spec，再重新验证。**

## 怎么做的
### 1) 时间切片
对四个相邻候选格分别按 rebalance 序列做：
- `first_half / second_half`
- `first_third / mid_third / last_third`

检查成本后 `mean_net_bps` 是否在切片后全面翻负。

### 2) 参数邻域
只看当前 policy 允许的最小邻域：
- formation：`24h` 与 `72h`
- holding：`4h` 与 `8h`

不再扩大参数搜索，只回答“这是不是只靠一格侥幸窗口存活”。

### 3) honesty / execution realism
沿用已冻结的诚实执行口径：
- `next-bar open`
- `no-overlap`
- `5 bps/side`

因此本轮没有引入任何更宽松的执行假设，也没有靠重叠持仓把 headline 撑高。

## 关键结果
### A. 参数邻域并没有一换就塌
四个邻域格 full-sample 的成本后净边：
- `24h × 4h`: `+34.42 bps/trade`
- `24h × 8h`: `+75.37 bps/trade`
- `72h × 4h`: `+22.45 bps/trade`
- `72h × 8h`: `+42.73 bps/trade`

这说明它不是只靠一组精确参数卡出来的单点海市蜃楼；至少在 `24h/72h × 4h/8h` 这个很小的邻域里，continuation headline 是连着存在的。

### B. 时间切片也不是统一翻负
最关键的切片结果：

#### `24h × 4h`
- `first_half`: `+25.71 bps`
- `second_half`: `+43.06 bps`
- `mid_third`: `-0.74 bps`
- `last_third`: `+64.06 bps`

#### `24h × 8h`
- `first_half`: `+63.79 bps`
- `second_half`: `+86.77 bps`
- `mid_third`: `+25.07 bps`
- `last_third`: `+123.96 bps`

#### `72h × 4h`
- `first_half`: `+3.59 bps`
- `second_half`: `+41.15 bps`
- `first_third`: `-0.37 bps`
- `last_third`: `+48.12 bps`

#### `72h × 8h`
- `first_half`: `+18.78 bps`
- `second_half`: `+66.30 bps`
- `first_third`: `+14.24 bps`
- `last_third`: `+75.06 bps`

读法很明确：
- 它**不是**“每一切都稳如老狗”；中段确实出现接近零或略负的片段；
- 但它也**不是**一换时间切片就全面失效；多数切片仍为正，最近一段还更强。

所以单从 time/parameter/honesty 这一轴看，`Rank 234` 其实还保留了某种真实 pocket continuation，而不是纯噪音。

## 为什么结论仍然不是 promote_P3
因为 admission 不是只问“时间切片能不能站住”，还要看**对象定义是否诚实**。

上一小点已经给出的硬事实是：
- `24h × 4h / 8h` 的 headline 净边主要由 `SIRENUSDT` 单币 pocket 主导；
- leave-one-out 去掉 `SIRENUSDT` 后两格都转负；
- major-coin 子宇宙下 `24h × 4h / 8h / 72h × 4h / 8h` 全部转负。

这意味着：
- **time / parameter** 这一轴回答的是“这个 pocket 不是瞬时幻觉”；
- 但 **cross-asset** 这一轴已经回答了“这个 pocket 不是广义 cross-asset family”。

两者合起来，最诚实的系统认知就不再是：
- `promote_P3`（太宽，因 portability 明显不成立）
- 也不是 `drop_to_background`（太狠，因为 pocket 本身并非完全虚假）

而是：

> **one-time P2 -> P1 re-scope**：只承认它目前像一条 `small-cap pocket / lottery-cohort continuation` 的窄对象，先退出当前过宽的 `Active P2` 定义；若将来要重开，必须按这条更窄 spec 重新回到前排，而不是继续沿用现在这个“广义 MAX continuation”名字硬拖在 P2。

## 对 runtime 的一句话写回
`Rank 234 / multiday MAX lottery XS continuation` 的 `24h/72h × 4h/8h` 邻域与时间切片在 `next-bar open + no-overlap + 5bps/side` 下大体仍为正，说明 pocket continuation 不是单窗口巧合；但结合上一小点已确认的 `SIRENUSDT` 主导与 major-coin/leave-one-out 失效，这条对象当前唯一诚实出口是 `one-time P2 -> P1 re-scope`：把它收窄成 `small-cap pocket / lottery-cohort continuation`，而不是继续作为广义 cross-asset P2 主线。

## 一句话 result
`Rank 234` 的时间切片与 `24h/72h × 4h/8h` 邻域并未坍塌，说明它保留的是一个真实但狭窄的 small-cap lottery pocket continuation；因此本轮不再开放式 `keep_P2`，而是把当前过宽对象做一次性 `P2 -> P1 re-scope`。
