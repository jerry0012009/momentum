# 2026-04-01 17:29 UTC — Rank 67 park reframe review

## Context
- Loop: `bot6 park-reframe`
- Scope this round: revisit exactly one parked rank without overturning the original `park` verdict
- Selected rank: `Rank 67 / regime-matrix shared-state gate`
- Selection reason:
  - 当前轮转默认优先看 `50+`，而 `Rank 67` 属于该号段
  - 距离上次 `bot6` 复盘（`2026-03-25 02:55 UTC`）已超过 7 天，符合“最近 7 天优先换别的”的约束
  - 这条线原始审计文件清楚、上次结论也明确，适合低频复核“最近新增证据有没有让它长出新的唯一修改轴”

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- prior park-reframe logs:
  - `research/park_reframe/2026-03-25_0255_rank67-park-reframe.md`
  - `research/park_reframe/2026-04-01_1313_rank21-park-reframe.md`
  - `research/park_reframe/2026-04-01_1529_rank26-park-reframe.md`
- needed evidence:
  - `research/optimization_loop/2026-03-18_2130_rank67-regime-matrix-park.md`
  - `research/quant_digests/2026-04-01_1426_lowfreq-liquidity-proxy-gate-overlay.md`

## What the original rank was trying to do
- 把 `30m` 的 `Trend / Expansion / Compression / Mean Reversion` 四态，写成 `ema_psar_long / fib_retest_long / breakout_short` 三条 setup 共用的 **shared allow/deny gate**。
- 也就是说，原 Rank 67 不是“单一 setup 的环境层”，而是想提供一套 **统一 shared state language**，直接决定哪些 15m entry 可以出手。

## Why Rank 67 was parked originally
原始审计文件：
- `research/optimization_loop/2026-03-18_2130_rank67-regime-matrix-park.md`

核心结论没有歧义：
- `no_MR` / `trend+exp` 对若干 setup 确实有“少亏或略增益”效果，尤其 `fib_retest_long` 有局部改善；
- 但改善主要靠 **大幅砍样本**，而不是稳定修好交易质量：
  - `ema_psar_long` retention 约 `16.2%~21.0%`
  - `fib_retest_long` retention 约 `15.2%`
  - `breakout_short` retention 约 `17.0%~26.1%`
- `breakout_short` 在 `trend+exp` 下虽然少亏，但 `false-break / false-hold 4bars rate` 反而从 `61.70%` 升到 `72.22%`；
- `compression_to_expansion_breakout` 在这套最小代理口径里几乎没有形成可比样本。

翻成人话：
- 这不是“regime 主题完全没信息”；
- 但把它包装成三条主线共用的统一硬 gate，主要是在靠砍单美化，不够诚实；
- 所以原始 `park` verdict 必须保留。

## Hard park or soft park?
**当前仍是 `soft park`，但已经明显偏硬。**

为什么还没到 hard park：
- regime / environment 主题本身没有被证伪；
- `fib_retest_long` 的局部改善也说明“环境许可层”不是纯噪声。

为什么比普通 soft park 更硬：
- 原 rank 最自然的一刀，本来就是把“shared 4-state gate”降级成更窄的单家族环境层；
- 这条残余修改轴其实早已被更具体的 queue 项消费：
  - `Rank 25b`：30m 4-state regime 只服务 breakout family；
  - `Rank 21b`：把 broader risk state 降级成低频 extremity risk overlay；
  - `Rank 9b`：把 regime-switch stack 改写成 asymmetric veto，而不是 shared language；
- 最近新增证据也没有把 `Rank 67` 拉回“值得单独再 draft 一个新编号”的位置。

## Is there any salvage signal?
**有，但仍然很弱，而且更像支持已有派生，不足以支持新的派生。**

仍能留住的“可救信号”主要只有两点：
1. `fib_retest_long` 在 `no_MR / trend+exp` 下的局部改善，说明 environment allow/deny 不是空话；
2. 最近的 `2026-04-01_1426_lowfreq-liquidity-proxy-gate-overlay.md` 又再次强调：
   - 短周期 desk 里，很多信息更诚实的角色是 **gate / sizing / cost overlay**；
   - 不该硬写成“共用方向语言”或“独立 alpha 本体”。

但这两点加在一起，得出的并不是 `Rank 67b`，而只是更进一步确认：
- Rank 67 的残余价值，只配收缩成 **更窄、更单家族、职责更清楚的环境层**；
- 这个位置已经被 `Rank 25b` 一类候选更干净地占住了。

## The single best cut
如果现在还保留唯一一刀，答案仍然是：

- **single modification axis:** `demote shared 4-state regime language into a single-family environment allow/deny layer only`

也就是：
- 不再给 `ema_psar_long / fib_retest_long / breakout_short` 三条线共享同一套 4-state regime 语言；
- 只允许它服务一个明确 family（最自然仍是 breakout family / `Rank 25b` 那一路）；
- 继续把 regime 信息留在“环境许可层”，而不是写成三 setup 共用的 entry 硬门。

但也正因为如此，本轮不再起新编号：
- 这条唯一诚实修改轴并不新；
- 它已经被 `Rank 25b` 更窄地实现；
- 再写 `Rank 67b` 只会和现有 queue 形成重复记账。

## Is a new derived hypothesis worth drafting?
**不值得。**

原因：
1. 原 `park` verdict 仍然完全成立；
2. Rank 67 的唯一诚实残余，仍只是“shared state language 太宽，应收缩成 single-family environment layer”；
3. 这条残余修改轴已经被既有 `Rank 25b / 21b / 9b` 等更窄提案分拆吸收；
4. 最近新证据（包括低频 liquidity/cost overlay 这一类）更多是在强化“角色降级”这件事，而不是给 Rank 67 提供第二条独立新轴。

## Direct answers required by bot6 brief
- **原 rank 为什么 park？**
  - 因为 clean replication 显示：它确实能让某些 setup 少亏，但主要靠大幅砍样本；把它写成三条主线共用的 shared 4-state gate 不够诚实。
- **它更像 hard park 还是 soft park？**
  - `soft park`，但已明显偏硬。
- **有没有“可救信号”？**
  - 有：environment allow/deny 仍有局部信息量；但这更适合单家族环境层，而不是 shared state language。
- **最值得改的唯一一刀是什么？**
  - 把 `shared 4-state regime language` 降级成 `single-family environment allow/deny layer only`。
- **是否值得形成新的 derived hypothesis？**
  - **不值得。** 因为这条唯一诚实残余已经被既有更窄提案吸收，最近没有新证据支持再起一个 `Rank 67b`。

## Final verdict
- **Final verdict:** `keep_park`
- Original `park` verdict remains intact
- Current reading: `soft park`，但原始 `shared-state gate` 读法已明显偏硬
- Existing narrower descendants elsewhere in queue remain enough; this round drafts nothing new

## Queue action
- Keep `Rank 67` parked
- Do **not** draft `Rank 67b`
- Do **not** change top-level `docs/TODO.md` scheduling

## File-change / commit note
- This round only updates the park-reframe log, index, and queue
- No selective commit was made because the task only required minimal documentation updates, and the shared workspace may contain unrelated dirty files
