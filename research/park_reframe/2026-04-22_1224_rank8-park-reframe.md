# 2026-04-22 12:24 UTC — Rank 8 park reframe review

- 时间：2026-04-22 12:24 UTC
- 对象：`Rank 8 / EMA shielding / threshold + retest_hold`
- 本轮结论：`keep_park`
- 原 `park` verdict：保留，不推翻

## 本轮为什么看 Rank 8
- 本轮严格回到 `Rank 1~37` 的 parked rank 范围内。
- `Rank 8` 上次 park-reframe 复盘是 `2026-04-14 21:14 UTC`，已超过 `7` 天。
- 4 月 21 日又新增两条更贴近该主题的旁证：
  - `research/quant_digests/2026-04-21_1358_tripleema-rsi-atr-stack-alpha.md`
  - `research/quant_digests/2026-04-21_1548_ichimoku-tenkankijun-cross-feetrap.md`
- 本轮要回答的是：**这些更新会不会让旧 `Rank 8` 诚实地长出新的窄 reframe（如 `Rank 8c`），还是只会进一步确认“到 `Rank 8b` 为止就够了”。**

## 本轮补读
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/optimization_loop/2026-03-16_2229_ema-shielding-park.md`
- `research/optimization_loop/2026-04-09_1125_rank8b_fresh_intake_background_absorbed.md`
- `research/park_reframe/2026-04-14_2114_rank8-park-reframe.md`
- `research/quant_digests/2026-04-21_1358_tripleema-rsi-atr-stack-alpha.md`
- `research/quant_digests/2026-04-21_1548_ichimoku-tenkankijun-cross-feetrap.md`

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
本轮判断：**`soft park`，但对旧 Rank 8 本体已更接近 `hard park with consumed residual`。**

原因：
- 对原 `fixed threshold + retest_hold` 本体，证据已经足够硬；
- 它曾留下唯一自然 residual：`fixed threshold -> adaptive ATR-scaled no-trade band`；
- 但这条 residual 已被既有 `Rank 8b` 消费，并在后续 fresh-intake first verdict 中收口为 `background / P0 / family absorbed`；
- 因此现在的“soft”，更多只是在说 EMA 主题本身没死，而不是说旧 `Rank 8` 还值得继续长新旁支。

## 3) 现有证据里有没有“可救信号”？
**有，但可救信号仍只到既有 `Rank 8b` 为止。**

### 可救信号 A：唯一自然 residual 仍是 adaptive band
旧 rank 最自然的一刀始终没变：
- fixed `0.5%` band 基本没起作用；
- 若保留 shielding 主题，最诚实的残余就是 **`fixed threshold -> adaptive ATR-scaled no-trade band`**；
- 这条 residual 已经被 `Rank 8b` 吸收。

### 可救信号 B：但 `Rank 8b` 已被运行态收口
`2026-04-09_1125_rank8b_fresh_intake_background_absorbed.md` 已把 runtime truth 讲清楚：
- `Rank 8b` 的最诚实位置只是 **EMA-only suppression gate**；
- 它没有长成独立 queue-facing pocket；
- 它已被 `volatility / tradeability overlay / trend-shell` family 吸收。

### 可救信号 C：4 月 21 日新证据继续把 EMA 主题往新 raw-alpha 宿主上推
这轮新增的两条 digest，给出的方向其实更“去血缘化”：

1. `triple EMA stack × RSI veto × ATR bracket`
   - 说明 EMA stack 作为 **trend parent signal** 仍有 gross pocket；
   - 但同一份 probe 也明确写出：`15m` gross 只薄薄为正，扣成本后不是 broad taker alpha；
   - 更诚实的读法是：EMA 堆叠属于新的 trend raw-alpha baseline，需要 volume / regime / execution 再加工，而不是旧 `Rank 8` 的 shielding 阈值线再开 `8c`。

2. `Ichimoku Tenkan/Kijun cross`
   - 也说明“快慢趋势状态切换”在 `5m/15m` 仍有一点 gross 厚度；
   - 但 net 依然被成本吃掉，更自然的定位是 **parent direction / trend state**，而不是裸 trigger；
   - 这进一步强化的是“EMA/趋势信息更像新 shell 的 parent-state”，不是旧 `Rank 8` 继续派生的第二刀。

所以本轮真正应当记住的是：
> **EMA 主题没死，但它现在更自然地活在新的 trend-shell / parent-state raw-alpha 宿主里，而不是旧 Rank 8 血缘下再开 `8c`。**

## 4) 最值得改的唯一一刀是什么？
如果今天仍然只允许保留一刀，答案还是同一条：

> **把 `fixed EMA shielding threshold` 改成 `adaptive ATR-scaled no-trade band`。**

但这条一刀本轮**不值得再 draft**，原因也已明确：
1. 它早就被 `Rank 8b` 明确表达过；
2. `Rank 8b` 又已在 `2026-04-09` 的 first verdict 中收口为 `background / P0`；
3. 当前不存在第二条仍然诚实、且不同于 `Rank 8b` 的主修改轴。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论仍是 `keep_park`。**

原因：
- 原 `park` blocker 没有被推翻；
- 旧 rank 唯一诚实 residual 仍只到 `Rank 8b`；
- `Rank 8b` 也已经被运行态吸收，没有长成独立 queue-facing pocket；
- 4 月 21 日新证据虽然继续证明 EMA / 趋势状态有信息，但它们救活的是新的 trend parent-signal / raw-alpha shell 宿主，而不是支持从旧 `Rank 8` 再诚实派生 `Rank 8c`。

## 6) 按模板直答
1. **原 rank 为什么 park？**  
   因为 `fixed threshold + retest_hold` 这版 EMA shielding 虽比 `raw_cross` 少亏，但 post-cost 仍为负，且时间/参数/跨标的/成本四项稳定性全部失败。

2. **它更像 hard park 还是 soft park？**  
   `soft park`，但对旧 `Rank 8` 本体已更接近 `hard park with consumed residual`。

3. **有没有“可救信号”？**  
   有，但唯一自然 residual 仍只是既有 `Rank 8b`；而 `Rank 8b` 又已在 2026-04-09 被收口为 `background / P0 / family absorbed`。

4. **最值得改的唯一一刀是什么？**  
   `fixed threshold -> adaptive ATR-scaled no-trade band`。

5. **是否值得形成新的 derived hypothesis？**  
   不值得。

## 最终结论
- `keep_park`
- original verdict kept: `park`
- short note: `soft park，但对旧 Rank 8 本体已更接近 hard with consumed residual；唯一诚实 residual 仍只是既有 Rank 8b，而 Rank 8b 又已于 2026-04-09 fresh-intake first verdict 收口为 background / P0 / family absorbed；4 月 21 日新增的 triple-EMA / Ichimoku 旁证继续说明 EMA / 趋势状态若还有信息，更像新的 trend parent-state / raw-alpha shell 宿主，因此当前不诚实 draft Rank 8c。`

## 对 queue 的最小写回
- `research/park_reframe/INDEX.md`：追加本轮索引；
- `docs/PARK_REFRAME_QUEUE.md`：只追加一条最近复盘记录；
- 不新增 `Rank 8c`；
- 不改 `docs/TODO.md` 顶部排班。

## Git / 提交
- 本轮不做 commit。
- 原因：共享工作区仍有无关脏文件；本轮只做最小必要文档更新，避免混提。
