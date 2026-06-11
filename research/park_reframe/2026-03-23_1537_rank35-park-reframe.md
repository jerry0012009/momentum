# 2026-03-23 15:37 UTC · Rank 35 park reframe review

## Scope
- Source rank: `Rank 35 VWAP pullback + trend-template qualifier`
- Original verdict stays: `park / evidence pool`
- This round only asks: **after the newer EMA role-split evidence, should Rank 35 spawn a new narrower reframe beyond the already drafted `Rank 35b`?**

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- Needed evidence:
  - `research/optimization_loop/2026-03-17_1248_rank35-clean-replication-park.md`
  - `research/park_reframe/2026-03-21_0232_rank35-park-reframe.md`
  - `research/quant_digests/2026-03-23_0234_apextrend-ema-role-split-breakout-primary.md`

## Why this rank this round
- `Rank 1~37` 里已 `park` 的条目，近几天基本都轮过一遍；这轮只能优先挑 **虽已复盘过，但今天又出现新旁证** 的旧条目，而不是机械重刷同一结论。
- `Rank 35` 上一次 park-reframe 是 `2026-03-21 02:32 UTC`，距离本轮已超过 48h；同时 `2026-03-23` 新增的 ApexTrend digest 正好再次碰到原线最核心的问题：**EMA 到底该当主触发，还是只该做 context / confirm / exit 角色层。**
- 这轮问题不是推翻原 `park`，而是判断：**这条新证据是否足以把原来的 `35b` 再推进成新的 `35c`。**

## 1) 原 rank 为什么 park？
原 `Rank 35` 被 park，不是因为 higher-tf bias 全无信息，而是因为它想验证的更完整故事——**higher-tf bias + RSI pullback reclaim + VWAP reclaim**——没有通过 desk 的诚实门槛。

原 clean replication 的核心 blocker 很集中：
- `combo_long_only` 交易密度极薄：`mean_trades≈3.7~4.0`
- `time-pocket honesty` 中段 bucket 明确翻负
- `bias_plus_vwap_reclaim` 对 anchor 明显敏感：
  - `utc_day @ 6bps≈+8.69%`
  - `funding_8h @ 6bps≈-0.51%`
- 真正还留下少量可读 pocket 的，反而是 **删掉 VWAP 后的 `bias_plus_rsi_pullback`**：`6bps≈+2.71%`、`positive_asset_ratio≈100%`、`mean_trades≈12`

所以原 `park` 的审计意义很清楚：
**失败点主要不在“顺势回调”这个故事本身，而在 `VWAP reclaim` 这道确认过稀、且 anchor-sensitive。**

## 2) 它更像 hard park 还是 soft park？
**更像 `soft park`。**

原因：
- higher-tf bias + pullback timing 没有全线塌掉；
- 原失败更像“把 gate 摆错岗位”，不是主题彻底失效；
- 也正因为如此，之前已经自然收敛出 `Rank 35b`：**去掉 VWAP reclaim，只保留 higher-tf bias + RSI pullback reclaim。**

但它也不是还能无限细分的那种 soft park：
- 最自然的一刀其实已经被 `35b` 消费；
- 再往下切，很容易把单轴复盘漂成多轴加料。

## 3) 有没有“可救信号”？
**有，但仍然只是支持既有 `35b`，不构成新的独立主轴。**

本轮新增信号来自 `2026-03-23_0234_apextrend-ema-role-split-breakout-primary.md`：
- 新 repo 里，EMA 真正有价值的用法不是“均线自己触发进场”，而是拆成：
  - `macro gate`
  - `momentum confirm`
  - `fast exit`
- 真正按扳机的仍是 breakout，本质上是在强化一句旧判断：
  **EMA 更像角色层，不像 standalone primary trigger。**

映射回 `Rank 35`：
- 这条证据并没有替 `VWAP reclaim` 正名；
- 反而进一步说明，原 `Rank 35` 里最容易失真的部分，正是把额外确认层堆得太重，导致样本被压到极薄；
- 换句话说，可救信号仍然是：
  **保留 trend context + 保留最小 RSI 回踩恢复，删掉最重、最 assumptions-sensitive 的 VWAP reclaim。**

## 4) 最值得改的唯一一刀是什么？
**仍然是旧结论：删掉 `VWAP reclaim`，保留 higher-tf bias + RSI pullback reclaim。**

也就是：
- 唯一最值得保留的修改轴，依然是 `Rank 35b` 已经写下的那一刀；
- 今天的新 EMA 角色分工证据，只是在更高一层再次证明：
  **EMA / context 类变量更适合做岗位分工，不适合继续往原 Rank 35 上叠新触发门。**

翻成人话：
- `35b` 解决的是“把最不诚实、最敏感的那道门去掉”；
- ApexTrend 新证据只是在说“别再把辅助结构写回主触发层”；
- 它不足以再派生出一个新的 `35c`。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论：`keep_park`。**

更准确地说：
- 原 `Rank 35` 的 `park` 继续保留；
- 已存在的 `Rank 35b` 继续足够代表这条主题最自然、最诚实的窄 reframe；
- 本轮新增证据只会把 desk 纪律再收紧成一句：
  **EMA 继续留在 context / confirm / exit 角色层，不要再顺手给 Rank 35 叠第二刀。**
- 当前不应再额外派生 `Rank 35c`，否则会把原本单轴复盘漂成多轴大改。

## Final verdict for this round
- `verdict`: `keep_park`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park`

## Minimal audit note
This round does **not** overturn the original `park`, and it does **not** add `Rank 35c`.
The new EMA role-split evidence only reinforces the already drafted `Rank 35b`: keep EMA-like logic in a supporting role and do not rebuild the original Rank 35 around heavier confirmation layers.

## Git
- 本轮只做最小必要文档改动；未做 commit。
- 原因：工作区存在大量无关脏文件与未跟踪文件，当前不适合安全地 selective commit。
