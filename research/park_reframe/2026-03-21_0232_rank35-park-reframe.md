# 2026-03-21 02:32 UTC · Rank 35 park reframe review

## Scope
- Source rank: `Rank 35 VWAP pullback + trend-template qualifier`
- Original verdict stays: `park / evidence pool`
- This round only asks: **after the newer RSI-memory evidence, should Rank 35 spawn a new narrower reframe beyond the already drafted `Rank 35b`?**

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- Needed evidence:
  - `research/optimization_loop/2026-03-17_1248_rank35-clean-replication-park.md`
  - `research/park_reframe/2026-03-17_2222_rank35-park-reframe.md`
  - `research/quant_digests/2026-03-21_0041_phase-wide-rsi-memory-retest-gate.md`

## Why this rank this round
- 在 `Rank 1~37` 里，已 `park` 的条目近 7 天基本都已被 `bot6` 复盘过；这轮只能优先挑 **有新证据** 的旧条目，而不是机械重复。
- `Rank 35` 正好有一条新旁证：`phase-wide RSI memory`，它直接碰到了原线里“RSI 回踩确认到底该怎么写”的核心部位。
- 但这轮问题不是“能不能推翻原 park”，而是：**这条新证据会不会自然导向一个新的 `35c`，还是只会强化‘到 35b 为止就够了’的判断。**

## 1) 原 rank 为什么 park？
原 `Rank 35` 被 park，不是因为 higher-tf long bias 本身完全没方向，而是因为它想验证的那套更严格故事——**higher-tf bias + RSI pullback reclaim + VWAP reclaim**——没有通过 desk 的诚实门槛。

原 clean replication 里最关键的 blocker 很集中：
- `combo_long_only` 交易密度极薄：`mean_trades≈3.7~4.0`
- 中间时间桶翻负，说明 pocket 不稳
- `bias_plus_vwap_reclaim` 对 anchor 明显敏感：
  - `utc_day @ 6bps≈+8.69%`
  - `funding_8h @ 6bps≈-0.51%`
- 真正留下较像样 pocket 的，反而是 **删掉 VWAP 后的 `bias_plus_rsi_pullback`**：`6bps≈+2.71%`、`positive_asset_ratio≈100%`、`mean_trades≈12`

所以原 `park` 的审计意义很清楚：
**失败点主要不在“顺势回调”这个故事本身，而在 `VWAP reclaim` 这道确认既过稀又 anchor-sensitive。**

## 2) 它更像 hard park 还是 soft park？
**更像 `soft park`。**

原因：
- higher-tf bias + pullback timing 并没有全线塌掉；
- 原失败更像“包装错了 / gate 放错了”，而不是主题彻底死透；
- 这也是为什么之前已经诚实收敛出 `Rank 35b`：删掉最不稳的 `VWAP reclaim`，保留 higher-tf bias + RSI pullback reclaim。

但它又不是这轮就该继续派生的“软到还能无限切”的 soft park：
- 因为最自然的一刀其实已经被 `35b` 消费；
- 再继续派生，极容易把原本单轴问题拆成多轴漂移。

## 3) 有没有“可救信号”？
**有，但不是新的独立可救主轴，而是对既有 `35b` 的补充旁证。**

本轮新增的可救信号来自 `2026-03-21_0041_phase-wide-rsi-memory-retest-gate.md`：
- `RSI` 真正有信息的，不是“只看触发当根”，而是看**整段回踩阶段是否破坏了动量结构**；
- 对 15m crypto，仓库默认 `40/60` 近乎不过滤，更有区分度的起步阈值是：
  - long：`min RSI >= 55`
  - short：`max RSI <= 44`
- 这条证据说明：**RSI 这部分确实还能写得更诚实**。

但关键点也正好在这里：
- 这更像是在细化 `35b` 里“RSI pullback reclaim` 该如何冻结”的实现口径；
- 它不像一个新的、足够独立的 `35c` 主修改轴；
- 因为一旦把 `Rank 35` 再派生成“VWAP 删除 + RSI phase-memory 阈值重标”，就已经不是单一修改轴了，而是在 `35b` 基础上再加第二刀。

## 4) 最值得改的唯一一刀是什么？
**如果今天重新只允许说一刀，仍然是旧结论：删掉 `VWAP reclaim`，保留 higher-tf bias + RSI pullback reclaim。**

也就是：
- 最值得改的唯一主轴，仍然是 `Rank 35b` 已记录的那一刀；
- 新的 `phase-wide RSI memory` 更像这条线将来若被认领时的**参数/冻结细化提示**，而不是新的派生 rank 名义。

翻成人话：
- `35b` 解决的是“把最不诚实的门删掉”；
- 新 RSI memory 只是在说“剩下这道 RSI 门怎么写更像样”；
- 它不值得再升格成 `35c`。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论：`keep_park`。**

更准确地说：
- 原 `Rank 35` 的 `park` 继续保留；
- 已存在的 `Rank 35b` 继续保留，足够代表这条主题最自然的窄 reframe；
- 本轮新增证据只说明：若未来 bot2 真的认领 `35b`，优先把 RSI 从“单根值”冻结成“phase-wide memory + 55/44 起步阈值”的细化版本；
- 但当前**不应**再额外派生 `Rank 35c`，否则会把单轴复盘漂移成多轴加料。

## Final verdict for this round
- `verdict`: `keep_park`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park`

## Minimal audit note
This round does **not** overturn the original `park`, and it does **not** add `Rank 35c`.
The newest RSI-memory evidence is useful, but only as a downstream freezing hint for the already drafted `Rank 35b`; it is **not** clean enough to justify a second derived hypothesis.

## Git
- 本轮只做最小必要文档改动；未做 commit。
- 原因：工作区存在大量无关脏文件与未跟踪文件，当前不适合安全地 selective commit。
