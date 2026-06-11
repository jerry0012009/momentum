# 2026-03-18 21:45 UTC · Rank 4 park reframe review

## Scope
- Source rank: `Rank 4 crypto pairs trading / stat-arb`
- Original verdict stays: `park / evidence pool`
- This round only asks: **should Rank 4 derive one narrower reframe hypothesis, without overturning the original park?**

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- recent reframe logs:
  - `research/park_reframe/2026-03-18_1925_rank11-park-reframe.md`
  - `research/park_reframe/2026-03-18_1725_rank25-park-reframe.md`
  - `research/park_reframe/2026-03-18_1513_rank30-park-reframe.md`
- needed evidence:
  - `research/optimization_loop/2026-03-16_1508_rank4-pairs-clean-replication-park.md`
  - `research/optimization_loop/2026-03-16_1838_rank4b-clean-replication.md`
  - `research/optimization_loop/2026-03-16_1853_rank4b-time-stability-park.md`
  - `research/quant_digests/2026-03-18_1714_btc-eth-spread-zscore-risk-overlay.md`

## Why this rank
- It is within `Rank 1~37` and currently parked.
- It has **not** been reviewed by `bot6` in the recent 7-day reframe queue.
- It is a good `bot6` candidate because the original rank already consumed the obvious direct-entry rescue path (`Rank 4b`), yet that rescue failed in a **very specific way**: pair-spread information was not clean enough to survive as standalone market-neutral alpha, but it also did not look like pure nonsense.
- A fresh digest now offers a narrower, more honest reinterpretation: **keep spread z-score, but demote it from direct pair-entry alpha to a shared risk overlay for existing continuation setups.**

## 1) 原 rank 为什么 park？
Rank 4 被 park，不是因为“pair spread / z-score 完全没信息”，而是因为它在当前 desk 的最小可执行表达里，**当作直接做多/做空价差的主策略并不成立**。

原 Rank 4 frozen-beta clean replication 关键证据：
- `BTC/ETH`：`trade_count=83`，`cumulative_net_return≈-12.42%`
- `BTC/SOL`：`trade_count=117`，`cumulative_net_return≈-22.91%`
- `ETH/SOL`：`trade_count=127`，`cumulative_net_return≈-27.77%`
- 三组主要 pairs 一起为负，因此原始 hard verdict 只能是 `park / evidence pool`

随后已经做过一次合法窄重开 `Rank 4b`：
- 唯一修改轴是把 frozen-beta 改成 `rolling-beta z-score spread`
- first pass 的确把 `ETH/SOL≈+2.28%`、`BTC/SOL≈+0.74%` 拉回轻微正 pocket
- 但补完唯一允许的一刀 `time stability` 后， surviving pairs 在最近 tercile 与最新月份又一起转负：
  - `BTC/SOL tercile_3≈-1.04%`，`2026-03≈-1.20%`
  - `ETH/SOL tercile_3≈-1.58%`，`2026-03≈-0.72%`

更直白地说：
- 这条线不是完全零信息；
- 但它**不够诚实地作为 standalone pairs alpha 存活**；
- 原 `park` verdict 必须保留，而且 `Rank 4b` 这条“继续当主策略修模型”的救法已经被审计消费掉了。

## 2) 它更像 hard park 还是 soft park？
**更像 `soft park`。**

原因不是原 rank 已经接近升格，而是：
- 它的失败并非“spread 变量毫无作用”，而更像“把它放在了错误的角色层级上”；
- `Rank 4b` 至少证明某些 pair pocket 曾短暂转正，说明 `spread disequilibrium` 不是纯噪音；
- 但这些 pocket 一到近期就塌，说明它不适合继续被包装成主 entry alpha。

所以更诚实的读法是：
- `hard park` 的部分在于：**作为 direct pairs trade 主策略，这条线已经该停了**；
- `soft park` 的部分在于：**spread 偏离本身也许还能以更降级的方式被利用**。

本轮最终给它的 park 类型读法仍记为 **`soft park`**，因为它保留了一个很窄、角色降级后的可救信号。

## 3) 有没有“可救信号”？
**有，但可救信号不在“继续修 pairs entry”，而在“把 spread 偏离降级成 shared overlay”。**

当前可救信号主要有三点：
1. `Rank 4b` 在不扩 universe 的前提下，曾把两组 pairs 拉回轻微正 pocket，说明问题不完全是“spread z-score 没信息”；
2. 真正把它压回 park 的，是 recency / time stability，而不是 lookahead、样本为零、或一加成本立刻全灭；
3. 最新 quant digest 刚好给出一个与 blocker 高度对位的窄改写：**BTC-ETH spread z-score 不拿来直接开 pair trade，而拿来给 breakout-short / Fib / EMA 这些 continuation setup 做 allow / reduce / veto 风险覆盖层。**

翻成人话：
- 原 Rank 4 更像把“跨币种失衡”硬当成主信号了；
- 但更自然的读法，也许是：当主币之间的相对偏离极端时，**先别急着做 continuation**。

## 4) 最值得改的唯一一刀是什么？
**唯一最值得改的一刀：保留 `spread z-score` 这个核心对象，但把它从 `direct pair-entry alpha` 改成 `shared risk overlay / position-sizing gate`。**

也就是：
- 不再让 `z_spread` 直接触发 `long spread / short spread`；
- 改成给现有 `breakout-short / Fib retest_hold / EMA-PSAR continuation` 做 shared risk layer：
  - `|z_spread|<=1`：allow / full size
  - `1<|z_spread|<=2`：reduce / half size
  - `|z_spread|>2`：veto new continuation entries
- 第一轮只允许比较 `base vs size-overlay vs hard-veto`，不能顺手偷带新 entry / new exit / new regime stack。

为什么这是一刀而不是多轴大改：
- 核心变量没变，仍是 `BTC-ETH spread z-score`；
- universe 没扩；
- 数据仍是公开价格序列；
- 只改了它的**角色定义**：从主信号降级成二阶风险覆盖层。

## 5) 是否值得形成新的 derived hypothesis？
**值得。结论：`derived_hypothesis_drafted`。**

理由：
- 原 `park` 结论完整保留，尤其“pairs alpha 本体不够诚实”这点不推翻；
- `Rank 4b` 已经把“继续修 direct-entry model”这条最自然救法消费过了，因此本轮不会重复命名旧故事；
- 最新 digest 提供的 reframe 很窄，而且正好回答原线最自然的剩余价值：**spread 偏离更像 crowding / dislocation risk，不像该直接下 pair trade。**

## 6) trade on / trade off 结论
### Proposed derived hypothesis
- `proposed_rank`: `Rank 4c`
- `source_rank`: `Rank 4`
- `single modification axis`: `demote BTC-ETH spread z-score from direct pairs-trade entry to a shared risk overlay / position-sizing gate for existing continuation setups`
- `trade on`: `保留现有 breakout-short / Fib retest_hold / EMA-PSAR 的原始 entry；只用 BTC-ETH rolling spread z-score 决定 allow / reduce / veto：|z|<=1 允许正常出手，1<|z|<=2 降仓，|z|>2 禁止新 continuation entry`
- `trade off`: `放弃“spread 偏离本身就是主 alpha”的原 Rank 4 读法，换取更诚实的 second-order crowding / dislocation 风险层；代价是它不再是独立策略，而且若阈值太激进，可能只是靠砍单美化结果，因此第一轮必须只测 overlay 本身，不偷带新 regime / exit`
- `why now`: `原 Rank 4 frozen-beta 为三组 pairs 一起转负，Rank 4b rolling-beta 虽把两组 pairs 拉回轻微正 pocket，却在最近 tercile / 最新月份重新转负，说明“继续当 standalone pairs alpha” 这条路已经被审计消费；而最新 BTC-ETH spread z-score digest 恰好给出一个更诚实、且只改角色不改核心变量的窄 reframe`
- `suggested_initial_state`: `source intake / clean replication next`

## Final verdict for this round
- `verdict`: `derived_hypothesis_drafted`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park`

## Minimal audit note
This round does **not** reopen Rank 4 itself.
It keeps the original `park` intact, and also keeps `Rank 4b` closed. The only new move is a narrower role downgrade: **`Rank 4c = keep spread z-score, but stop treating it as direct pair-entry alpha; test it only as a shared risk overlay for existing continuation setups.`**

## Git
- 本轮只做最小必要文档改动；未做 commit。
- 原因：工作区存在大量无关脏文件与未跟踪文件，当前不适合安全地 selective commit。
