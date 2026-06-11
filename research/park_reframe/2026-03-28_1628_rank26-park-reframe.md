# 2026-03-28 16:28 UTC · Rank 26 park reframe review

## Scope
- Source rank: `Rank 26 regime_triplet state gate`
- Original verdict stays: `park / evidence pool`
- 本轮问题：在不推翻原 `park` 审计结论的前提下，`Rank 26` 现在是否还值得再派生出一个新的窄 reframe hypothesis？

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- needed evidence:
  - `research/optimization_loop/2026-03-17_0656_rank26-regime-triplet-paper-candidate.md`
  - `research/optimization_loop/2026-03-17_0724_rank26-ethsol-recheck-park.md`
  - prior reframe: `research/park_reframe/2026-03-21_1008_rank26-park-reframe.md`
  - artifacts:
    - `reports/artifacts/scout_regime_triplet_15m/clean_replication_summary.csv`
    - `reports/artifacts/scout_regime_triplet_15m/ethsol_scope_recheck.csv`
    - `reports/artifacts/scout_regime_triplet_15m/ethsol_scope_time_recheck_15bps.csv`

## 为什么本轮又看 Rank 26
- 轮转上，`50+` 与 `80~110` 近两天已连续覆盖；`1~24` 也刚覆盖到 `Rank 21`。
- `Rank 26` 属于 `25~49` 段，而且上次复盘时间是 `2026-03-21 10:08 UTC`，已超过 7 天约束。
- 本轮目标不是重开老结论，而是确认：**在已有 `Rank 26b` 的前提下，最近几天是否出现了足以支持“再切一刀”的新证据。**

## 1) 原 rank 为什么 park？
核心原因没变：`regime_triplet` 当成 strict entry gate 时，确实能留下 pocket，但 pocket 不够稳，尤其扛不过更诚实的 friction / time-bucket 检查。

关键审计证据：
- full scope（BTC/ETH/SOL）下，`strict_up_down` 一度足以升到 `P2`：
  - `6bps/side ≈ +14.65%`
  - `positive_asset_ratio = 2/3`
  - `mean_trades ≈ 141`
  - `mean_no_trade_ratio ≈ 86.58%`
- 但成本一上去就明显塌：
  - `10bps/side ≈ +2.44%`
  - `15/20bps` 已转负
- 最小诚实 recheck（只剥离 BTC，做 `ETH+SOL-only`）后，仍不足以升 `P3`：
  - `15bps/side ≈ +2.29%`，但只剩 `1/2` 资产为正
  - `ETH ≈ +9.89%`，`SOL ≈ -5.31%`
  - `20bps/side ≈ -11.17%`
  - `15bps` 时间桶仍有明显破口：`bucket_1 ≈ -8.44%`

所以原始 `park` 的审计含义必须保留：
**Rank 26 不是没信息，而是把 regime_triplet 写成 strict allow gate 之后，对 friction / 时段分布过敏，无法当作够干净的 queue-facing candidate。**

## 2) 它更像 hard park 还是 soft park？
**仍然更像 `soft park`，但已经比 3/21 更偏硬。**

理由：
- soft 的部分：它确实留下过可解释 pocket，否则不会先升到 `P2`，也不会已经派生出 `Rank 26b`。
- 更偏硬的部分：最自然的一刀已经在 3/21 被消费掉——把 strict gate 降级成 `veto-only shared regime overlay`（`Rank 26b`）。
- 本轮重读 `RECENT_PAPER_SEEDS`、`quant_digests/INDEX` 与 `PARK_REFRAME_QUEUE` 后，没有出现第二条同样自然、且不和 `Rank 26b` 重复的单轴新证据。

## 3) 有没有“可救信号”？
**有残余可救信号，但它没有新增，且仍只收敛到既有 `Rank 26b`。**

残余信号是什么：
- `strict_up_down` 在 low-cost 的确比 baseline 明显更不差，说明 regime 信息量不是零。
- 失败形状也很清楚：它更像“别在明显反向 regime 里硬开仓”的 veto 信息，而不是“只有最优 regime 才许开仓”的 allow 信息。

为什么这次不算新信号：
- 这个角色改写，已经在 `2026-03-21_1008_rank26-park-reframe.md` 被完整消费，并正式写成了 `Rank 26b`。
- 最近几天的新 digest 更像：
  - 把 sentiment / market state 往更上位的 raw-alpha family 或 overlay family 推；
  - 或把别的 gate 主题改写成更窄、更专用的 lane-specific gate。
- 它们**没有提供一条对 Rank 26 独有、且不同于 `veto-only regime overlay` 的新单轴。**

## 4) 最值得改的唯一一刀是什么？
**仍然只有既有那一刀值得保留：`strict entry gate -> veto-only shared regime overlay`。**

也就是现成的 `Rank 26b`：
- long 遇到 `down_regime` 才 veto；
- short 遇到 `up_regime` 才 veto；
- 不再要求“必须处于最优 regime 才 allow”。

本轮判断：
- 这条唯一主修改轴没有失效；
- 但它已经在队列里，**不值得再发明一个 `26c` 或平行新提案。**

## 5) 是否值得形成新的 derived hypothesis？
**不值得。最终结论：`keep_park`。**

更准确地说：
- 原 Rank 26 继续维持 `park`；
- 既有派生 `Rank 26b` 继续保留为唯一诚实 residual；
- 本轮没有足够新证据支持再新增 `Rank 26c` / `Rank 26 reframe 2` 之类的新条目。

## 6) 为什么这次不继续派生
因为如果继续派生，最容易犯的错有两个：
1. **把同一件事换个说法重复写一遍**：例如把 `veto-only overlay` 再包装成 `soft allow gate / asym allow gate / regime context gate`，本质仍是 `26b`。
2. **偷带第二轴**：例如顺手叠 time bucket、asset subset、sentiment extremity、breakout-only lane，这都会违反“每轮只切 1 刀”的约束。

本轮最诚实的做法反而是：
- 承认 `Rank 26` 的 park 结论没被推翻；
- 承认它的唯一自然残余已经被 `Rank 26b` 占住；
- 暂不再造新提案。

## Final verdict for this round
- `verdict`: `keep_park`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park，但比 2026-03-21 更偏硬`

## Minimal audit note
Rank 26 的原始 `park` 结论继续保留。
本轮复核后确认：其唯一自然 residual 仍只是既有 `Rank 26b = regime_triplet veto-only overlay`；最近没有足够新证据支持再诚实派生 `Rank 26c`。

## Git
- 工作区存在大量无关脏文件与未跟踪文件；本轮只做最小必要文档改动，不做 commit。
