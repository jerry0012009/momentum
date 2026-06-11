# 2026-03-31 00:35 UTC — Rank 88 park reframe review

## 为什么这轮看 Rank 88
- 继续遵循 `bot6` 轮转：近期 `50~79` 与部分 `1~37` 已连续覆盖，本轮切到尚未被 `park_reframe` 复盘的 `80~110` 号段旧 parked rank。
- `Rank 88 / macro-event blackout + size-down risk overlay` 还没进入 `bot6` 低频复盘记录；且最近几天又新增了两组与“时钟 × 宏观事件”直接相关的新证据，值得确认一次它到底是在救原命题，还是已经迁移成别的 family：
  1. `2026-03-26_0106_fomc-event-clock-veto-size-down-overlay.md`
  2. `2026-03-29_1022_utc-schedule-macro-timestamp-gate.md`
  3. `2026-03-29_1358_rank238_first_verdict_keep_p1_utc_schedule_macro_shared_gate.md`
  4. `2026-03-29_1411_rank238_survivor_followup_exhausted_background.md`
- 目标不是替 `bot2 / bot3` 接手这些新线，而只是判断：原 `Rank 88` 还有没有诚实的单轴可救空间。

## 本轮补读
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/optimization_loop/2026-03-19_1149_rank88_macro_event_overlay_intake.md`
- `research/optimization_loop/2026-03-19_1201_rank88-clean-replication-park.md`
- `research/quant_digests/2026-03-19_1128_macro-news-event-blackout-risk-overlay.md`
- `research/quant_digests/2026-03-26_0106_fomc-event-clock-veto-size-down-overlay.md`
- `research/quant_digests/2026-03-29_1022_utc-schedule-macro-timestamp-gate.md`
- `research/optimization_loop/2026-03-29_1358_rank238_first_verdict_keep_p1_utc_schedule_macro_shared_gate.md`
- `research/optimization_loop/2026-03-29_1411_rank238_survivor_followup_exhausted_background.md`

## 1) 原 Rank 为什么 park？
原 `Rank 88` 想做的是：
- 不改 base setup 的方向逻辑；
- 只把 `FOMC / CPI` 一类公开事件日程映射成 `15m` 级 `blackout / size-down / hybrid` shared overlay；
- 服务 `ema_psar_long / fib_retest_long / breakout_short` 三条线。

原始 clean replication 把口径压得已经很小：
- `BTC / ETH / SOL 120d 15m`
- `next-bar open + no-overlap + hold 8 bars`
- 成本 `6 / 10 / 15 bps per side`
- 四臂对照：`baseline / blackout[-1h,+1h] / size_down_0.5x / hybrid[-30m,+30m] blackout + (+30m,+120m) size_down`

结论也很直接：
1. **事件窗覆盖的交易太少。**
   - `pm1h_trade_share ≈ 0.81%`
   - 说明原 shared overlay 不是在系统性治理三条主线，只是在碰极少数 bar。
2. **最好的变体也没改善 post-cost 结果。**
   - `size_down_0.5x` 仍约 `-30.57%`
   - baseline 约 `-28.85%`
   - `blackout[-1h,+1h]` 约 `-32.29%`
   - `hybrid` 约 `-30.83%`
3. **没有哪一条 archetype 被明显修好。**
   - `breakout_short` 只是一点点少亏；
   - `ema_psar_long / fib_retest_long` 都没出现 shared benefit。

翻成人话：
**原 Rank 88 被 park，不是因为“宏观时间戳完全没信息”，而是因为它当时那版 `15m 三线共用 blackout/size-down overlay` 太稀、太泛、也没有带来诚实的跨 lane 增量。**

## 2) 它更像 hard park 还是 soft park？
结论：**soft park，但现在已经明显比原审计时更偏 hard。**

原因：
- 宏观事件时钟这个主题本身并没有死；
- 但最近新增证据已经把它重新拆成两条更诚实的路径：
  1. **更窄的事件专用执行 / 风险 overlay**（如 `FOMC 14:00 ET veto + size-down`）；
  2. **更宽的 UTC 时钟 / 宏观时间戳 shared gate family**。
- 问题在于：这两条新路径都已经不再等于原 `Rank 88` 的那版“15m 三线共用 generic blackout/size-down”。

所以它还不是 classic hard park——因为主题没死；
但对“继续诚实派生 `Rank 88b`”这件事来说，它已经很偏 hard 了。

## 3) 现有证据里有没有“可救信号”？
**有，但更像主题迁移，不像原命题可救。**

### 可救信号 1：FOMC 事件时钟本身仍然很真实
`2026-03-26_0106_fomc-event-clock-veto-size-down-overlay.md` 给出的证据很强：
- FOMC statement 后首个 `1h / 15m` 的波动与成交显著放大；
- 这条线更像**低频但高影响的 event-clock execution / risk overlay**；
- 它适合做 `taker veto / maker widen / cooldown / re-arm`，而不只是简单 `blackout`。

对 `Rank 88` 的含义：
- 说明“scheduled macro event”确实值得写进系统；
- 但正确主语更像 **FOMC 专用 event-risk management**，不是原来那种把 `FOMC/CPI` 混成一层 generic shared overlay 的粗写法。

### 可救信号 2：UTC schedule × macro timestamp 是更上位的新 family
`2026-03-29_1022_utc-schedule-macro-timestamp-gate.md` 进一步指出：
- 真正更通用的对象，可能是 `minute-of-hour + hour-of-day + weekday + macro window` 组合成的 `schedule_score`；
- 它服务 continuation admission 与 reversal veto，而不是只服务原 `Rank 88` 的三条 lane。

这对 `Rank 88` 的含义是：
- 宏观时间戳的残余价值，已经在往**更上位 shared timing map** 漂移；
- 原 rank 的血缘边界正在变弱。

### 但新增证据也顺手证明了：原命题不好救
最关键的是 `Rank 238` 的最小 survivor follow-up 已经做过一次 decisive 检验：
- `2026-03-29_1411_rank238_survivor_followup_exhausted_background.md`
- 在 frozen `schedule_score` 下，continuation 与 reversal 两侧都没留下 gated > baseline > inverse 的 post-cost 分层。

这说明：
- “更宽的 shared timing gate” 也不是轻松就能落地；
- 原 `Rank 88` 更没有理由再靠“generic blackout/size-down”续命。

## 4) 最值得改的唯一一刀是什么？
如果硬保留原线血缘，唯一还算诚实的一刀只能是：

**把 generic `macro blackout + size-down` 改成 `FOMC-only event-clock execution veto + cooldown/re-arm overlay`。**

也就是：
- 不再把 `CPI/FOMC/各种事件窗` 混成一个共享黑窗；
- 只保留 `FOMC 14:00 ET` 这一类证据最强、时点最确定、冲击最可复核的事件；
- 把动作从单纯 `不开仓/半仓` 改成更像 execution discipline：`T-30m~T` 缩仓、`T~T+15m` 禁 taker、`T+15m~T+60m` cooldown、再按 realized state re-arm。

但这刀**本轮不值得写成新的 derived hypothesis**，因为：
1. 它已经不再是原 `Rank 88` 的“窄修补”，而更像一条新的专用 event-clock overlay 主语；
2. 最近 digest 已经把这条线单独表达得更完整；
3. 若现在再写 `Rank 88b`，大概率只是把已经迁移出去的 residual 硬绑回旧编号，削弱原 `park` verdict 的审计边界。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。**

本轮结论：`keep_park`

## 为什么不是 `soft_reframe_candidate`
因为这次不是“还有一点 distinctness，先留个候选 note”；
而是更像：
- 原 `Rank 88` 的 residual value 已经分裂成两条别的东西：
  1. `FOMC-only` 的事件专用 execution / risk overlay；
  2. 更上位的 `UTC schedule × macro timestamp` shared timing family；
- 前者已经能被更诚实地单独命名；
- 后者又已经做过最小 decisive follow-up 且没站住。

换句话说，**原命题的最佳剩余，并不属于“Rank 88b”这种旧血缘派生。**

## 本轮按模板回答
1. **原 rank 为什么 park？**
   - 因为原 `15m` 三线共用 `blackout / size-down / hybrid` overlay 在事件窗覆盖率极低（约 `0.81%` 交易）下，四臂都没带来诚实的 post-cost 改善，也没有哪条 archetype 被明显修好。
2. **它更像 hard park 还是 soft park？**
   - `soft park`，但比原审计时更偏 hard。
3. **有没有“可救信号”？**
   - 有；但信号在指向 `FOMC-only` 事件执行 overlay 和更上位的 `UTC schedule × macro timestamp` family，而不是救原 `Rank 88` 本身。
4. **最值得改的唯一一刀是什么？**
   - 若硬改，只能收窄成 `FOMC-only event-clock execution veto + cooldown/re-arm overlay`。
5. **是否值得形成新的 derived hypothesis？**
   - 不值得。
6. **为什么不写 `Rank 88b`？**
   - 因为这条唯一可救轴已经迁移成更独立的新主语；硬写成 `88b` 会模糊原 `park` 的审计边界，也与后续更专用的 event-clock 线重叠。

## 最终结论
- 原 `park` verdict：**保留**
- 本轮状态：**`keep_park`**
- 一句话总结：
  - **Rank 88 不是在证明“宏观事件时钟没用”，而是在证明“generic 15m shared blackout/size-down overlay”这版写法不诚实；最近新增证据把残余价值分别迁移到更窄的 FOMC-only execution overlay 与更上位的 UTC schedule family，当前不诚实再派生 Rank 88b。**

## 对 queue 的最小写回
- `research/park_reframe/INDEX.md`：追加本轮索引；
- `docs/PARK_REFRAME_QUEUE.md`：只追加一条最近复盘记录；
- 不新增 `Rank 88b`；
- 不改 `docs/TODO.md` 顶部排班。

## Git / 提交
- 本轮未提交。
- 原因：工作区长期存在大量无关脏文件；本轮只做最小必要文本改动，避免混提。
