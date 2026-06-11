# 2026-03-28 03:14 UTC — Rank 3 park reframe review

- source rank: `Rank 3 / third-touch + EMA/MACD confluence`
- current authoritative verdict in `docs/TODO.md`: `park / evidence pool`
- this round verdict: `keep_park`
- original park verdict kept: `yes`

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- recent reframe logs:
  - `research/park_reframe/2026-03-27_2102_rank12-park-reframe.md`
  - `research/park_reframe/2026-03-27_1902_rank83-park-reframe.md`
  - `research/park_reframe/2026-03-27_1702_rank62-park-reframe.md`
- needed evidence:
  - `research/optimization_loop/2026-03-16_0838_scout-rank3-first-verdict.md`
  - `research/optimization_loop/2026-03-16_1434_scout-rank3-parameter-stability-park.md`
  - `research/quant_digests/2026-03-19_0316_trendln-paired-channel-breach-gate.md`
  - `research/quant_digests/2026-03-22_2339_janis-breakout-ema-role-gate.md`
  - previous bot6 note: `research/park_reframe/2026-03-19_0644_rank3-park-reframe.md`

## Why this rank
- 本轮按用户要求只看 `Rank 1~37` 的 parked 条目。
- `Rank 3` 上次由 bot6 复盘是 `2026-03-19 06:44 UTC`，距离当前已超过 7 天，满足低频复看条件。
- 它仍是一个容易让人“想再救一次”的条目：原始 best slice 并非深负，而是靠极严结构确认把噪声砍到几乎没有。
- 但重新对照后，结论没变：**这条线最主要的问题仍是极端稀疏，不是差一刀小修。**

## 1) 原 Rank 为什么会 park
原 Rank 3 被 park，不是因为 third-touch + EMA/MACD 完全没信息，而是因为它留下的是一个**过薄到不够策略层 admission 的 pocket**。

关键原始证据：
- `2026-03-16_0838` first verdict 最好变体 `third_touch_plus_ema_macd`
  - `mean_total_return≈+0.78%`
  - `mean_false_break_ratio=0.00%`
  - `positive_asset_ratio=1/3`
  - `mean_trades≈0.33` 笔/资产
- `2026-03-16_1434` parameter stability park
  - `positive_neighbor_floor`: pass（`7/7` positive）
  - `cross_asset_neighbor_floor`: **fail**（`0/7` 达到 `>=2/3` 正资产）
  - `trade_count_neighbor_floor`: **fail**（`0/7` 达到 `>=1 mean trades/asset`）

翻成人话：
- 这条线确实把 `raw_breakout` 的大量假突破噪声砍掉了；
- 但砍得太狠，最后只剩一个几乎不交易、也没有跨资产厚度的漂亮小口袋；
- 所以被 park 的，不是“trendline confirmation 这个大方向完全错”，而是**`Rank 3` 这种极窄 third-touch 直接当 entry skeleton 的写法不够诚实。**

## 2) 它更像 hard park 还是 soft park
**更像 `hard park`。**

原因：
- blocker 很集中，而且是底层 blocker：不是某个成本档位、某个币、某个 time bucket 单独拖累；
- 真问题是样本厚度太薄，跨资产可迁移性也没有成立；
- 一旦要求最基本的 cross-asset / trade-density honesty，它就站不住。

所以它不像“实现太粗，只差一刀角色修正”；
更像“原命题已经把结构过滤收得过窄，窄到失去 queue-facing alpha 的最小厚度”。

## 3) 有没有可救信号
**有很弱的可救信号，但不足以支撑新的 derived hypothesis。**

可救信号只剩两点：
1. 它相对 `raw_breakout` 确实能明显压掉假突破；
2. 最近新增的旁证仍支持“EMA / 结构确认更像 context/follow-up gate”，并不支持完全裸追 breakout：
   - `2026-03-19 trendln paired-channel breach + reclaim-hold`：更像 post-break follow-up gate；
   - `2026-03-22 Janis breakout EMA role gate`：更像 EMA 应降级成 context gate，而不是与 breakout 平级双触发。

但这些信号为什么仍不够：
- 它们救的是“结构/EMA 该放在哪一层”这个上位主题；
- 并没有救回 `Rank 3` 自己的核心问题：**third-touch 本体太稀、太薄、太不跨资产。**

也就是说，新证据更像继续证明：
- 如果还有价值，也该写进更通用的 breakout follow-up / context gate family；
- 而不是诚实地再派生一个 `Rank 3b`，继续让 third-touch 当主角。

## 4) 最值得改的唯一一刀是什么
**唯一还说得过去的一刀，是把 `third-touch + EMA/MACD` 从 direct entry gate，彻底降级成更通用的 post-break structure/context filter。**

但本轮仍然**不把这刀写成 `Rank 3b`**，原因很明确：
1. 这已经不再是“对 Rank 3 的窄修”，而是在把它拆散后并入更上位的 breakout/context family；
2. 这条角色改写已经被近邻证据大幅消费：
   - `Rank 30b` 已经承接了 trendline / channel 的 follow-up hold-reclaim 语言；
   - `Rank 25c` 已经承接了 EMA 更像 context gate、不是 co-trigger 的角色分工；
   - `Rank 31 / 33 / 53` 与近几天的 failure / verdict 证据，也已经覆盖了结构确认失败后的更诚实读法。
3. 如果现在硬写 `Rank 3b`，本质会变成“把已被别的 rank 吸收的角色再复制一遍”，审计上不干净。

## 5) 是否值得形成新的 derived hypothesis
**不值得。本轮结论：`keep_park`。**

理由：
- 原 `park` 审计意义依旧很强：Rank 3 已经清楚说明“过滤很干净”不等于“形成可交易厚度”；
- 最近新增证据没有给出一个属于 Rank 3 自己、且未被别的 rank 消费掉的唯一新轴；
- 最自然的救法已经外溢到上位 breakout/context/failure-routing 家族；
- 因此当前最诚实的动作，是继续保留 Rank 3 的 `hard park` 结论，而不是为了显得勤奋硬写 `Rank 3b`。

## 6) 本轮最终回答
- 原 Rank 为什么 park：因为 third-touch + EMA/MACD 虽压掉大量噪声，但只留下极薄、极稀、缺乏跨资产厚度的 pocket；
- 它更像：`hard park`；
- 可救信号：有，但只剩“结构确认/EMA 更适合做 context 或 follow-up gate”这一类上位残余；
- 最值得改的唯一一刀：**把 Rank 3 从 direct entry gate 彻底降级成更通用的 post-break structure/context filter**；
- 是否值得形成新的 derived hypothesis：**不值得**；
- 本轮最终结论：`keep_park`。

## 7) Minimal audit note
本轮不是推翻 2026-03-19 对 Rank 3 的判断，而是确认：
- 最近新证据没有让 `third-touch` 本体重新变厚；
- 它只进一步证明这类信息更适合被更通用的 breakout/context family 吸收；
- 因此 Rank 3 仍应继续作为“结构确认过度切样本”的反例证据保留，而不是派生新的 queue-facing hypothesis。

## 8) 文件与提交流程说明
- 本轮只更新 `research/park_reframe/INDEX.md`、`docs/PARK_REFRAME_QUEUE.md` 与本日志；
- 默认不改 `docs/TODO.md` 顶部排班；
- 本轮未做 git commit：工作区存在大量与本轮无关的脏文件与未跟踪文件，当前不适合安全地 selective commit。
