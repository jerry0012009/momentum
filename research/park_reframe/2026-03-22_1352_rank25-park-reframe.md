# 2026-03-22 13:52 UTC · Rank 25 park reframe review

## Scope
- Source rank: `Rank 25 / EMA + Donchian breakout confirmation`
- Original verdict stays: `park / evidence pool`
- This round only asks: **after the new closed-bar HTF / expiry-window evidence, does Rank 25 deserve a *new* narrower reframe beyond existing `Rank 25b`?**

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- needed evidence:
  - `research/optimization_loop/2026-03-17_0610_rank25-ema-donchian-p2.md`
  - `research/optimization_loop/2026-03-17_0623_rank25-time-redwatch-park.md`
  - `research/park_reframe/2026-03-18_1725_rank25-park-reframe.md`
  - `research/quant_digests/2026-03-18_1707_regime-matrix-shared-state-gate.md`
  - `research/quant_digests/2026-03-21_0145_state-expiry-latency-budget-gate.md`
  - `research/quant_digests/2026-03-21_0246_closedbar-htf-context-honesty-gate.md`
  - `research/quant_digests/2026-03-20_1530_range-location-veto-gate.md`

## Why this rank this round
- `Rank 25` 已在 `2026-03-18` 被 bot6 派生出 `Rank 25b`，正常不该在 7 天内重复看。
- 但这几天出现了 **直接相关的新证据**：
  1. `4-state regime matrix` 之后，又新增了 `confirmWindow + entryWindow expiry`；
  2. 又新增了 `closed-bar HTF merge_asof(backward)` 的 context honesty gate；
  3. 还新增了 `range location` 这类更 cheap 的 final-veto 读法。
- 所以这轮不是重讲旧结论，而是确认：**这些新证据会不会把 Rank 25 再推进成一个新的 `25c`，还是只会把现有 `25b` 写得更诚实。**

## 1) 原 rank 为什么 park？
原 `Rank 25` 被 park 的原因没有变：
- 它一度有很像样的 pocket：
  - `ema_donchian_l30_c3 @ 6bps/side` 约 `+16.83%`
  - `positive_asset_ratio = 3/3`
  - `mean_trades ≈ 33.67`
  - `10/15/20bps` 仍保留正 pocket
- 但 genuinely verdict-changing 的最小 honest recheck 把它压回了 `park`：
  - 主变体 `l30_c3` 是 `bucket_1负 / bucket_2正 / bucket_3负`
  - 邻近正 pocket `l40_c3` 也重复同样时间结构
  - 就算诚实缩到 `ETH+SOL-only`，仍然只有中段 bucket 为正

翻成人话：
- 原问题不是“entry 完全没 edge”；
- 而是 **这条 edge 更像阶段性环境 pocket，而不是可平权部署的 15m continuation 语法**；
- 所以原 `park` 结论必须保留，不能被事后抹平。

## 2) 它更像 hard park 还是 soft park？
**仍然更像 `soft park`。**

原因也没变：
- 它不是四项一起硬爆炸；
- 它留下的残余信息量主要集中在“环境许可层”这一类 blocker；
- 这也是为什么 `Rank 25b` 当时是一个诚实的窄派生。

但本轮的关键补充是：
- 新证据更像在告诉我们 **怎么把 `25b` 做得更诚实**；
- 不是告诉我们原 Rank 25 还能再切出第二条新的主修改轴。

## 3) 现有证据里有没有“可救信号”？
**有，但这些可救信号仍然收敛到同一条主轴：`25b`，而不是新的 `25c`。**

### 可救信号 A：regime allowance 仍是最对位的 blocker
`2026-03-18_1707_regime-matrix-shared-state-gate.md` 仍然最贴原始失败形状：
- Rank 25 不是参数/成本/跨资产先死；
- 它先死在 time bucket 上；
- 所以“上层状态允许/禁止”仍是最自然的一刀。

### 可救信号 B：expiry 说明 25b 不该无限等待
`2026-03-21_0145_state-expiry-latency-budget-gate.md` 给了一个重要补充：
- 即便 `Trend / Expansion` 环境允许出手，**确认也不应无限等待**；
- 否则 Rank 25 这类 breakout continuation 很容易把 stale follow-up 也混进同一类样本。

### 可救信号 C：HTF context 必须 closed-bar only
`2026-03-21_0246_closedbar-htf-context-honesty-gate.md` 进一步说明：
- 若 `25b` 真要借上层 `30m/1h` regime context，必须是 **closed-bar only**；
- 否则会把未收盘 HTF 状态偷渡进 15m，假装修好了 time instability。

### 可救信号 D：range location 更像 cheap veto，不是新主轴
`2026-03-20_1530_range-location-veto-gate.md` 也有价值；
但它更像：
- 对已有 continuation 做 quick veto；
- 不像比 `regime allowance` 更核心的新 reframe 母轴。

所以本轮的真实判断是：
- `Rank 25` 确实仍有“可救信号”；
- 但这些新信号没有打开第二条独立 reframe 路线；
- 它们都只是让 **现有 `Rank 25b` 的 implementation boundary 更清楚**。

## 4) 最值得改的唯一一刀是什么？
**唯一最值得改的一刀仍然是：保留原 `EMA bias + Donchian breakout confirmation`，只加上层 regime allow/deny gate。**

也就是：
- 不是改出 `25c`；
- 而是把 `25b` 的边界写得更死：
  1. regime gate 必须走 `closed-bar` 上层 context；
  2. confirm / entry 需要 `expiry window`；
  3. `range location` 之类 cheap veto 只配做 25b 的附属诚实检查，不该升级成第二主轴。

为什么本轮不把 expiry 或 range-location 单独升成新主轴：
- 它们都不能替代 `regime allowance` 这个原始 blocker；
- 单独抽出来，会把一条本来聚焦的 reframe 拆成多条近义候选；
- 这违反 bot6 的“每轮最多 1 条唯一主修改轴”。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论：`keep_park`。**

更准确地说：
- `Rank 25b` 仍然保留，且依旧是 Rank 25 唯一诚实的窄派生；
- 但在 `25b` 已存在的前提下，本轮新证据不足以再派生 `25c`；
- 所以这轮的动作应是 **保留原 park + 保留既有 25b + 不再新增新旁支**。

## 6) trade on / trade off 结论
本轮**不形成**新的 `Rank 25c`。

更诚实的保留口径：
- `trade on`：`Rank 25` 的残余信息量依旧更像“环境许可层”而不是“再找一个新的局部滤镜”；因此已有 `Rank 25b` 继续成立。
- `trade off`：新增的 `expiry / closed-bar HTF / range-location` 证据，只适合当 `25b` 的实现约束与 honesty guard，不适合再拆成新的 queue-facing hypothesis。

## Final verdict for this round
- `verdict`: `keep_park`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park`

## Minimal audit note
This round does **not** overturn the earlier `Rank 25b` draft.
Instead it records a narrower point: the new evidence since 2026-03-18 strengthens **implementation discipline** for `Rank 25b` (closed-bar HTF context, expiry windows, cheap veto checks), but does **not** justify drafting a second derived hypothesis such as `Rank 25c`.

## Git / write scope
- 本轮只做最小必要写入：本日志、`research/park_reframe/INDEX.md`、`docs/PARK_REFRAME_QUEUE.md`
- 默认不改 `docs/TODO.md`
- 未做 git commit：仓库当前存在大量与本轮无关的共享脏文件，避免混提
