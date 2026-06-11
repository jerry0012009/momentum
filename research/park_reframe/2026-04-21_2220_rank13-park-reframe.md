# 2026-04-21 22:20 UTC — Rank 13 park reframe review

- loop: `bot6 park-reframe`
- source rank: `Rank 13 / partial-moment asymmetry TSMOM gate`
- current authoritative verdict: `park / evidence pool`
- this round verdict: `keep_park`
- original park verdict kept: `yes`

## Why this rank this round
- 本轮按用户约束回到 `Rank 1~37` 里挑 1 条已 `park` 条目，而不是做 bot2 desk review / bot3 主循环。
- `Rank 13` 上次 bot6 复盘是 `2026-04-13 12:43 UTC`，已超过 7 天；近期低号 rank 里 `Rank 9 / 31 / 19 / 27 / 15 / 3 / 6 / 37 / 33 / 22 / 32 / 16 / 35 / 14 / 25 / 21 / 18 / 26 / 12 / 11` 等已更近覆盖，本轮不重复。
- 4 月 18 日新增 `partialmoment-tsmom-reversal-overlay` digest 重新把 Liu, Lu, Wang (2021) 的 UPM/LPM 四区动作表讲清楚，足够检查：它是否能把旧 `Rank 13` 从 `park` 中再派生出一个新的窄 `Rank 13c`。

## Read set used this round
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- prior reframe log: `research/park_reframe/2026-04-13_1243_rank13-park-reframe.md`
- original audit: `research/optimization_loop/2026-03-17_0038_rank13-asymmetry-tsmom-park.md`
- new evidence: `research/quant_digests/2026-04-18_0508_partialmoment-tsmom-reversal-overlay.md`
- original artifacts spot-check: `reports/artifacts/scout_asymmetry_tsmom_15m/*` summary files referenced by the audit

## 1) 原 rank 为什么 park？
`Rank 13` 被 park 的原因仍然很明确：它把 partial-moment / tail asymmetry 写成了 **standalone 15m sign-momentum + partial-moment guard**，但 clean replication 与 Light Stability Pack 一起失败。

原始审计里的关键事实仍成立：
- primary `pm_guard_100 @ 6bps/side` 约 `mean_total_return ≈ -71.90%`；
- `positive_asset_ratio = 0/3`；
- `mean_max_drawdown ≈ -75.70%`；
- 时间、参数、跨标的、成本四类 stability gate 一起 fail；
- guard 相比裸 sign-momentum 只是“少亏”，不是可交易 alpha。

所以原 `park` verdict 的审计意义必须保留：失败的是 **把 partial moments 当独立方向/救场策略**，不是证明 partial moments 在任何 risk layer 里都无信息。

## 2) 它更像 hard park 还是 soft park？
本轮判断：**`soft park`，但对旧 Rank 13 本体已接近 hard with consumed residual。**

还保留 soft 的原因：
- 4 月 18 日 digest 进一步确认 UPM/LPM 可用于识别 TSMOM reversal / close-out / veto 状态；
- partial-moment 主题本身仍可能服务 trend / breakout / continuation 母体。

更接近 hard 的原因：
- 这个主题的唯一诚实残余已由既有 `Rank 13b` 表达：把 standalone gate 降级为 `RS+/RS- realized-semivariance directional veto / sizing overlay`；
- 新 digest 讲清的是“UPM/LPM 四区动作表应依附于已有 TSM 母体”，不是“旧 15m sign-momentum standalone gate 只差一个小修补”；
- 若再写 `Rank 13c`，很容易只是把同一个 partial-moment overlay 换名重提，稀释 `Rank 13b` 与原 park 结论。

## 3) 有没有“可救信号”？
有，但它仍然是**角色层可救**，不是旧 rank 本体可救。

可救信号：
- UPM/LPM 的双尾高位可作为混乱段 close-out / no-entry；
- 单侧尾部翘起可提示原 momentum 方向更容易被 reversal 打脸；
- 这类信息更适合做 trend continuation / breakout / TSMOM shell 的 reversal veto、size-down 或 close-only overlay。

但这些信号没有推翻原审计：
- 原 Rank 13 已经测试过把 partial moments 直接挂到 15m sign-momentum 上，结果失败；
- 4 月 18 日的新读法反而更强调“它不是独立 alpha，本质依附于已有 TSM 母体”；
- 因此它最多强化既有 `Rank 13b` 的合理性，不足以诚实拆出新的 `Rank 13c`。

## 4) 最值得改的唯一一刀是什么？
若只问“主题还能怎么诚实使用”，唯一一刀仍是：

> **把 partial-moment asymmetry 从 standalone entry / sign-momentum guard 降级为 existing trend/continuation setup 上的 reversal veto / close-only sizing overlay。**

但这不是本轮新增一刀；它已经被 `Rank 13b` 的 `directional veto / sizing overlay` 消费。4 月 18 日 digest 提供的 UPM/LPM 四区动作表，更像 `Rank 13b` 第一轮实验可选实现细节，而不是一个新的 queue-facing `Rank 13c` 主轴。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论为 `keep_park`。**

原因：
1. 原 `park` blocker 没变：standalone sign-momentum + partial-moment guard 仍是稳定性全 fail；
2. 新 evidence 是同一 partial-moment / TSMOM 主题的更清楚解释，不是独立的新证据链；
3. 唯一诚实角色改写已由 `Rank 13b` 覆盖；
4. 新 draft 会与 `Rank 13b` 高重叠，且更像实现细节膨胀而不是新的窄 hypothesis。

## Direct answers required by the brief
- **原 rank 为什么 park？**
  - 因为 standalone 15m sign-momentum + partial-moment guard 在收益、回撤、时间、参数、跨标的、成本上一起失败；只是相对少亏，不是可交易 alpha。
- **它更像 hard park 还是 soft park？**
  - `soft park`，但旧 Rank 13 本体已接近 hard with consumed residual。
- **有没有可救信号？**
  - 有；UPM/LPM 对 trend reversal / close-out / veto 仍可能有信息，但它服务的是既有 trend/continuation 母体或 `Rank 13b`，不是旧 standalone gate。
- **最值得改的唯一一刀是什么？**
  - 仍是把 partial moments 降级成 reversal veto / sizing overlay；该轴已由 `Rank 13b` 消费。
- **是否值得形成新的 derived hypothesis？**
  - 不值得；不 draft `Rank 13c`。

## Final verdict
- `final_status = keep_park`
- `original verdict kept = park`
- short note:
  - `soft park，但旧 Rank 13 本体已接近 hard with consumed residual；4 月 18 日 UPM/LPM reversal-overlay digest 强化的是 partial moments 作为 trend/continuation 母体的 veto/close-only layer，而不是支持旧 standalone gate 再派生 Rank 13c；既有 Rank 13b 仍覆盖唯一自然残余。`

## Queue action
- keep `Rank 13` parked
- keep existing `Rank 13b` as the only queue-facing residual
- do **not** draft `Rank 13c`
- do **not** modify `docs/TODO.md`

## Git / commit note
- 本轮只做 park-reframe 所需最小文本更新。
- 当前共享工作区已有大量无关脏文件，且 `docs/PARK_REFRAME_QUEUE.md` / `research/park_reframe/INDEX.md` 本身已有未提交改动；本轮不做 commit，避免把前序未提交内容混入。