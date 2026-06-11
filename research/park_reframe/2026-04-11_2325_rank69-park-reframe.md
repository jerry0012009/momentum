# 2026-04-11 23:25 UTC | Rank 69 park reframe review

- source rank: `Rank 69`
- original status: `park / evidence pool`
- this round verdict: `keep_park`
- original park verdict kept: `yes`

## Why this rank this round
- 按 `bot6` 默认轮转，优先继续看 `50+` 已 park 的条目。
- `Rank 69` 不在最近 7 天的 `park_reframe` 复盘列表里，满足低频复看要求。
- 它原本就带一个很明确的问题：到底是“低 IVU 开盘量结构”真有 shared continuation 信息，还是只是靠极端砍样本减亏；这类对象适合做一次低频复盘。

## Files read this round
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/optimization_loop/2026-03-18_2223_rank69-ivu-source-intake.md`
- `research/optimization_loop/2026-03-18_2242_rank69-clean-replication-park.md`
- `research/quant_digests/2026-03-19_0956_volume-clock-cs-spread-interaction-gate.md`
- `research/quant_digests/2026-04-03_0042_btc-volclock-first30-impulse-alpha.md`
- `reports/artifacts/scout_rank69_ivu_opening_volume_uncertainty_15m/setup_compare.csv`
- `reports/artifacts/scout_rank69_ivu_opening_volume_uncertainty_15m/parameter_stability.csv`
- `reports/artifacts/scout_rank69_ivu_opening_volume_uncertainty_15m/cost_trade_stability.csv`

## 1) 原 rank 为什么 park？
原 Rank 69 的主张是：把 `00:00 UTC` 固定 session anchor 后的开盘量不确定性（`IVU = vol_bar1 / sum(vol_bar1..bar7)`）当成一个 shared continuation gate，去过滤 `ema_psar_long / fib_retest_long / breakout_short` 三条线。

但最小 clean replication 给出的结论很直接：
- 主变体 `ivu_allow_q40` 的 aggregate 仍为负：`mean_total_return = -0.84%`；
- `mean_trade_count_retention = 8.02%`，已经接近“砍到几乎没交易”；
- `mean_failure_before_target_rate = 86.46%`，不像一个诚实的 continuation gate；
- setup 间也不统一：
  - `ema_psar_long`: `base=-3.68% -> q476=+4.22%`，有 pocket；
  - `fib_retest_long`: `base=+1.17% -> q476=+1.11% / q40=-0.62%`，没增量；
  - `breakout_short`: `base=-3.55% -> q476=-6.04% / q40=-2.14%`，仍负。

也就是说，原 rank 被 park，不是因为“方向完全荒唐”，而是因为：
**它没有把“开段量结构”证明成一个足够统一、足够便宜、足够不靠砍样本的 shared gate。**

## 2) 它更像 hard park 还是 soft park？
结论：**soft park，但明显向 hard park 靠。**

原因：
- 它并非三条 setup 全面同向崩坏；`ema_psar_long + q476` 确实留下一个 pocket。
- 但这个 pocket 没有跨 setup 扩散，也没有跨阈值稳定；`q40` 与 `size_haircut_q40` 都没把问题修好。
- 更关键的是，原对象的核心写法——`固定时钟 + bar1/bar1..7 的 IVU 比率 + shared allow gate`——已经被审计出强烈的 retention 依赖。

所以它还没到“主题完全死透”的 hard park；但对**原 Rank 69 本体**来说，已经非常接近 hard park。

## 3) 有没有“可救信号”？
有，但**可救信号不再属于原 Rank 69 这层写法本体**。

当前最可信的残余只剩一句：
- `开段冲击 / 流动性状态` 这类信息可能有用；
- 但有用的对象更像 **volume-clock / first-30m extreme impulse / spread×impulse** 这一类更完整的 event-style continuation family。

本轮交叉读到的后续证据非常一致：
1. `2026-03-19_0956_volume-clock-cs-spread-interaction-gate.md`
   - 明确指出：**crypto 不该先固定钟表开盘，而应先找成交量时钟**；
   - 且更值得保留的是 `volume-clock + spread×impulse`，不是固定 funding-style anchor。
2. `2026-04-03_0042_btc-volclock-first30-impulse-alpha.md`
   - 更进一步把同主题收敛成一条 **raw alpha**：`首 30m 极端成交量 + 极端方向冲击 -> 后续 30~60m 同向续行`；
   - 这已经不是“shared IVU gate”的语言，而是更完整的 event-driven continuation 对象。

所以，**可救信号有，但它救的是“开段冲击/流动性主题”，不是旧 Rank 69 的 fixed-clock IVU gate 壳。**

## 4) 最值得改的唯一一刀是什么？
如果只写“唯一一刀”，最诚实的一刀其实是：

**把 `固定 00:00 UTC 的 IVU shared gate` 改读为 `volume-clock anchored opening impulse / liquidity interaction`。**

但这正是本轮不 draft 新派生的原因：
- 这一下去，主语已经从 `IVU ratio gate` 换成了 `volume-clock event / impulse shell`；
- 它不只是阈值、角色、或 veto/allow 轻改；而是在换事件定义与宿主语义；
- 这更像新的 raw-alpha / family-level 对象，或者更上位地被后续 volume-clock / session-impulse 家族吸收。

因此，这一刀**有研究价值**，但**不再是属于 Rank 69 的诚实单轴 reframe**。

## 5) 是否值得形成新的 derived hypothesis？
结论：**不值得；本轮维持 `keep_park`。**

理由：
1. 原 rank 的唯一 pocket 主要停留在 `ema_psar_long + q476`，没有形成跨 setup 的 shared gate 证据。
2. 一旦把“固定开盘量不确定性”改成“volume-clock 冲击/流动性交互”，对象就已经换壳到别的 family。
3. 最近的新证据不是把 Rank 69 修窄，而是把它往：
   - `volume-clock shared gate`（更像 Rank 80 / 5b family 的近邻语义）
   - 甚至 `single-asset event-driven continuation raw alpha`
   这两个方向外推。
4. 继续写 `Rank 69b` 会模糊审计边界：看上去像在救 Rank 69，实际上是在借它改写成另一条新对象。

## 6) 如果硬要写 trade on / trade off，会怎样？
本轮不 draft，但为了审计边界，仍把它写清楚：

### 假如硬写成 reframe，唯一可能的方向
- single modification axis:
  - `replace fixed-clock IVU ratio gate with volume-clock anchored opening-impulse / liquidity-interaction definition`

### trade on
- 不再要求 `00:00 UTC` 固定 session；
- 不再把 `bar1 / bar1..7` 的 IVU 比率当主角；
- 改为先找当日真实 `volume-clock open`，再看 `first30 impulse` 与流动性状态是否支持 continuation。

### trade off
- 这已经不再是“原 shared IVU gate 的窄修补”；
- 它会把对象改写成更像新的 event-driven continuation shell；
- 因而会吃掉原 `park` verdict 的审计边界。

也正因为这组 `trade on / trade off` 已经明显越出原对象，所以本轮不应把它正式写成 `Rank 69b`。

## Final verdict
**`keep_park`**

- 原 `park` verdict 保留；
- `Rank 69` 更像 `soft park`，但明显继续向 `hard park` 靠；
- 可救信号存在，但属于更高位的 `volume-clock / opening-impulse` family，而不属于旧的 `fixed-clock IVU shared gate` 本体；
- 因此本轮不诚实 draft `Rank 69b`。

## Queue impact
- 仅更新 `docs/PARK_REFRAME_QUEUE.md` 的最近复盘记录；
- 不改 `docs/TODO.md` 顶部排班；
- 不新增 active reframe candidate。

## Commit note
- 本轮只做最小必要文档改动。
- `git status` 显示工作区存在大量与本轮无关的脏文件 / 未跟踪文件，因此**不做 selective commit**，避免混提。
