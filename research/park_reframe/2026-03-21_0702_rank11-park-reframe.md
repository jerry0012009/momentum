# 2026-03-21 07:02 UTC · Rank 11 park reframe review

## Scope
- Source rank: `Rank 11 / Lo-style causal extrema pattern gate`
- Original verdict stays: `park / evidence pool`
- This round only asks: **after the new 2026-03-21 CUSUM event-bar digest, does Rank 11 now deserve one narrower derived reframe hypothesis?**

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- needed evidence:
  - `research/optimization_loop/2026-03-16_2343_rank11-clean-replication-park.md`
  - `research/quant_digests/2026-03-21_0652_cusum-event-bar-confirm-veto-gate.md`

## Why this rank this round
- 严格说，`Rank 11` 最近 7 天内已经被 bot6 复盘过；正常应优先换别的。
- 但当前 `Rank 1~37` 已 park 条目在最近几天基本都被轮过一遍，而 `Rank 11` 刚好出现了一条**直接相关的新证据**：`CUSUM event bar` 把“确认是否真的走出来”这件事重新写成了更诚实的 confirm-veto 层。
- 所以这轮不是重讲旧结论，而是借新证据确认：**Rank 11 该不该从‘Lo-style causal extrema pattern gate’派生出一条新的窄 hypothesis。**

## 1) 原 rank 为什么 park？
原 `park` 结论来自 clean replication 的硬失败，而且失败不轻：
- `mean_total_return ≈ -4.33%`
- `positive_asset_ratio = 0/3`
- `mean_trades ≈ 58.3`
- Light Stability Pack 四项全 `fail`
  - 时间稳定性：`1/3` positive buckets
  - 参数稳定性：`0/5` positive 邻域
  - 跨标的稳定性：`0/3`
  - 成本/交易数稳定性：`0/4`

翻成人话：
- 问题不是“差一点点”；
- 也不是“只是成本太高”；
- 而是 **Lo-style causal extrema pattern 这条线，在 15m BTC/ETH/SOL 上既不稳、也不厚、也没有可复用平台**。

所以原始 `park` verdict 仍然有完整审计意义，不能被推翻成“其实方向对，只是少一个小补丁”。

## 2) 它更像 hard park 还是 soft park？
**这轮仍更像 `hard park`。**

原因：
- `Rank 11` 的失败不是“确认层太粗，所以只要换更细确认就能救”；
- 它更像是 **模式本体的样本与稳定性都不够**；
- 新 digest 提供的是一个更通用的 `market-activity confirm-veto` 思路，但这更像适用于 breakout-short / Fib / EMA-PSAR 这些已经有主体 pocket 的线，不像是专门替 Rank 11 这条 pattern gate 翻案。

## 3) 有没有“可救信号”？
**有一点，但不足以升级成真正可救信号。**

这次的新 digest 真正增加的信息是：
- 不该把确认层死绑在固定 15m 时间 bar；
- 可以用 `same_dir_first / opp_dir_first / no_event_timeout` 去判断信号后有没有真实事件流；
- 这对已有主体 setup 的 follow-up honesty 很有帮助。

但对 `Rank 11` 来说，问题在于：
- 原线的主体不是“已有不错 pocket，只缺 follow-up 过滤”；
- 而是 clean replication 本身就已经把 **模式识别 + causal extrema 触发** 这条路压成了全维度偏负；
- 这时再加一层 `CUSUM confirm-veto`，更像给一个已经失败的 trigger 再套二次守门，而不是找到新的唯一主修改轴。

所以它最多说明：
- `事件流确认` 这类思路值得保留；
- 但更适合挂在现有 desk 主线或更新 rank 上，而不是拿来给 `Rank 11` 派生 `Rank 11b`。

## 4) 最值得改的唯一一刀是什么？
如果硬要写，最像“一刀”的写法会是：
- **把 `Lo-style causal extrema pattern gate` 改写成 `pattern trigger + CUSUM same-dir-first confirm-veto`。**

但这刀现在**不够诚实**，因为它违反了 brief 想防止的两件事：
1. 它不是在修一个已经显露主体 edge 的 setup，而是在给一个四项稳定性全 fail 的旧 trigger 叠加二层确认；
2. 它和最新 digest 所服务的 `breakout-short / Fib / EMA-PSAR` confirm-veto 角色高度重叠，独特性不够。

所以这轮最诚实的答案反而是：
- **没有足够干净的唯一一刀。**
- 新证据更适合服务别的线，不适合把 `Rank 11` 重新打开。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论：`keep_park`。**

为什么：
- 原 `park` 的主 blocker 没被新证据推翻；
- 新 digest 打开的，是一个更通用的 confirm-veto 层，不是 `Rank 11` 专属的新 rescue path；
- 若现在硬写 `Rank 11b`，大概率只是把“pattern 失败”包装成“再加一道确认也许能行”，这不够诚实。

## 6) trade on / trade off 结论
本轮**不形成**新的 `Rank 11b`。

更诚实的保留口径：
- `trade on`：`CUSUM event-confirm` 作为 shared follow-up honesty layer 是有价值的，应优先服务 breakout-short / Fib / EMA-PSAR 这类已有主体 pocket 的线；
- `trade off`：放弃把它硬绑回 `Lo-style causal extrema pattern gate`，因为那会把一个通用确认层误写成原 Rank 11 的专属救法；
- 因此 `Rank 11` 继续保留 `park` 的审计结论，而新证据应被理解为**旁支 confirm-veto 资源**，不是 `Rank 11` 的 reopen 理由。

## Final verdict for this round
- `verdict`: `keep_park`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `hard park`

## Minimal audit note
This round revisits `Rank 11` only because there is **new evidence** after the prior bot6 review.
That new evidence does **not** overturn the old conclusion; it mainly shows that `CUSUM event-confirm` is a better shared follow-up layer for stronger existing setups, not a reason to derive `Rank 11b` from an already hard-parked pattern gate.

## Git / write scope
- 本轮只做最小必要写入：本日志、`research/park_reframe/INDEX.md`、`docs/PARK_REFRAME_QUEUE.md`
- 默认不改 `docs/TODO.md`
- 未做 git commit：仓库当前存在大量与本轮无关的共享脏文件，避免混提
