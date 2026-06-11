# 2026-04-14 21:14 UTC — Rank 8 park reframe review

- 时间：2026-04-14 21:14 UTC
- 对象：`Rank 8 / EMA shielding / threshold + retest_hold`
- 本轮结论：`keep_park`
- 原 `park` verdict：保留，不推翻

## 本轮为什么看 Rank 8
- 本轮严格回到 `Rank 1~37` 的 parked rank 范围内。
- `Rank 8` 上次 park-reframe 复盘是 `2026-04-07 14:59 UTC`，已超过 `7` 天。
- 4 月上旬之后又有两条直接相关的新证据会影响判断：
  - `research/optimization_loop/2026-04-09_1125_rank8b_fresh_intake_background_absorbed.md`
  - `research/optimization_loop/2026-04-08_0430_rank363_htf_ema_rsi_pullback_intake_keep_p1.md`
- 本轮要回答的是：**这些新证据会不会让旧 `Rank 8` 诚实地长出新的窄 reframe（例如 `Rank 8c`），还是只会进一步确认“到 `Rank 8b` 为止就够了”。**

## 本轮补读
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/optimization_loop/2026-03-16_2229_ema-shielding-park.md`
- `research/park_reframe/2026-03-23_0704_rank8-park-reframe.md`
- `research/park_reframe/2026-04-07_1459_rank8-park-reframe.md`
- `research/optimization_loop/2026-04-09_1125_rank8b_fresh_intake_background_absorbed.md`
- `research/optimization_loop/2026-04-08_0430_rank363_htf_ema_rsi_pullback_intake_keep_p1.md`

## 1) 原 rank 为什么 park？
原 `Rank 8` 被 park 的原因没有变化：
- 原始实现是 `fixed threshold + retest_hold` 的 EMA shielding 写法；
- clean replication 虽然显示 `retest_hold` 比 `raw_cross` 少亏很多，但仍没有达到可诚实重开的门槛；
- 真正被否掉的是 **固定 band + 原始 trigger 角色** 这套实现，不是“EMA 附近别乱做”这个主题完全没信息。

原始 hard evidence 仍然成立：
- `raw_cross @ 6bps ≈ -15.76%`
- `threshold_005 @ 6bps ≈ -15.54%`
- `retest_hold @ 6bps ≈ -6.50%`
- `positive_asset_ratio = 0/3`
- `Light Stability Pack` 四项全 fail（时间 / 参数 / 跨标的 / 成本）

所以原 `park` 的审计意义仍然是：
> **失败的是旧 Rank 8 的 fixed-band 写法，而不是 EMA shielding / no-trade 角色本身。**

## 2) 它更像 hard park 还是 soft park？
本轮判断：**`soft park`，但对旧 Rank 8 本体的读法已经更接近 hard。**

原因：
- 对原 `fixed threshold + retest_hold` 本体，证据已经很充分，不值得再反复续命；
- 但它确实留下过一条自然 residual：把 `fixed threshold` 改写成 `adaptive ATR-scaled no-trade band`；
- 只是这条 residual 也已经在后续运行里被消费并收口，而不是继续长成新的独立宿主。

更直白地说：
- 对原 Rank 8 本体：已经很硬；
- 对“EMA shielding 主题完全死了没有”：还没硬死，所以整体仍更像 `soft park`。

## 3) 现有证据里有没有“可救信号”？
**有，但可救信号仍只到既有 `Rank 8b` 为止。**

### 可救信号 A：唯一自然 residual 仍是 adaptive band
旧 rank 最自然的一刀一直都很明确：
- fixed `0.5%` band 基本没起作用；
- 若保留 shielding 主题，最诚实的残余就是 **`fixed threshold -> adaptive ATR-scaled no-trade band`**；
- 这条 residual 已经被 `Rank 8b` 吸收。

### 可救信号 B：但 `Rank 8b` 已在运行态收口为 background / P0
`2026-04-09_1125_rank8b_fresh_intake_background_absorbed.md` 已把最关键的 runtime truth 说清楚：
- `Rank 8b` 的最诚实位置只是 **EMA-only suppression gate**；
- 它没有长成独立 queue-facing pocket；
- 它已被 `volatility / tradeability overlay / trend-shell` family 吸收。

这意味着：
- 有 residual；
- 但 residual 已被消费，不再支持继续诚实派生 `Rank 8c`。

### 可救信号 C：4 月 8 日的新 intake 反而进一步说明主题已迁移到新宿主
`Rank 363 / HTF EMA gate × 15m RSI pullback continuation` 的价值在于：
- EMA 主题仍然活着；
- 但它更自然地活在 **新的 trend-shell raw alpha 宿主** 里；
- 主语已经变成 `HTF trend established -> LTF shallow pullback continuation`，而不是旧 Rank 8 的 shielding / threshold 写法。

所以这轮真正应当记住的是：
> **EMA 主题没死，但它现在更自然地活在新的 trend-shell / pullback 宿主里，而不是旧 Rank 8 血缘下再开 `8c`。**

## 4) 最值得改的唯一一刀是什么？
如果今天仍然只允许保留一刀，答案还是同一条：

> **把 `fixed EMA shielding threshold` 改成 `adaptive ATR-scaled no-trade band`。**

但这条一刀本轮**不值得再 draft**，原因也已经很明确：
1. 它早就被 `Rank 8b` 明确表达过；
2. `Rank 8b` 又已在 `2026-04-09` 的 first verdict 中收口为 `background / P0`；
3. 因而当前不存在第二条仍然诚实、且不同于 `Rank 8b` 的主修改轴。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论仍是 `keep_park`。**

原因：
- 原 `park` blocker 没有被推翻；
- 旧 rank 唯一诚实 residual 仍只到 `Rank 8b`；
- `Rank 8b` 也已经在运行态被收口为 family-absorbed 的 suppression gate；
- 4 月新增证据继续把 EMA 主题推向新的 trend-shell / pullback raw-alpha 宿主，而不是支持从旧 Rank 8 再诚实派生一条新的 `Rank 8c`。

## 6) 按模板直答
1. **原 rank 为什么 park？**  
   因为 `fixed threshold + retest_hold` 这版 EMA shielding 虽比 `raw_cross` 少亏，但 post-cost 仍为负，且时间/参数/跨标的/成本四项稳定性全部失败。

2. **它更像 hard park 还是 soft park？**  
   `soft park`，但对旧 Rank 8 本体的读法已经更接近 hard。

3. **有没有“可救信号”？**  
   有，但唯一自然 residual 仍只是既有 `Rank 8b`；而 `Rank 8b` 又已在 2026-04-09 被收口为 `background / P0 / family absorbed`。

4. **最值得改的唯一一刀是什么？**  
   `fixed threshold -> adaptive ATR-scaled no-trade band`。

5. **是否值得形成新的 derived hypothesis？**  
   不值得。

## 最终结论
- `keep_park`
- original verdict kept: `park`
- short note: `soft park，但对旧 Rank 8 本体已更接近 hard；唯一诚实 residual 仍只是既有 Rank 8b，而 Rank 8b 又已于 2026-04-09 fresh-intake first verdict 收口为 background / P0 / family absorbed；4 月新增证据继续说明 EMA 主题若还有信息，更像新的 trend-shell / pullback raw-alpha 宿主，因此当前不诚实 draft Rank 8c。`

## 对 queue 的最小写回
- `research/park_reframe/INDEX.md`：追加本轮索引；
- `docs/PARK_REFRAME_QUEUE.md`：只追加一条最近复盘记录；
- 不新增 `Rank 8c`；
- 不改 `docs/TODO.md` 顶部排班。

## Git / 提交
- 本轮不做 commit。
- 原因：共享工作区仍有大量无关脏文件；本轮只做最小必要文档更新，避免混提。
