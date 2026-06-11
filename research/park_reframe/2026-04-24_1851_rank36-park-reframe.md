# 2026-04-24 18:51 UTC · Rank 36 park reframe

## Scope
- source rank: `Rank 36 / recent-return sign vs history-drift honesty gate`
- original status kept: `park`
- this round verdict: `keep_park`
- review reason:
  - 本轮仍只处理 `1` 条已 `park` rank；
  - 虽然 `Rank 36` 在最近 `7` 天内刚复盘过一次，但 2026-04-23 新增了三条更贴近该主题的旁证：`path smoothness × trend continuation`、`low-MAX continuation quality`、`intraday continuation × market-characteristics`；
  - 本轮要确认的是：这些新证据是否足以把 old `Rank 36` 从“污染诊断卡”重新拉回 queue-facing 窄派生。

## Files read this round
### Required
1. `docs/TODO.md`
2. `docs/PARK_REFRAME_QUEUE.md`
3. `docs/RECENT_PAPER_SEEDS.md`
4. `research/quant_digests/INDEX.md`
5. `research/park_reframe/INDEX.md`

### Recent park-reframe context
- `research/park_reframe/2026-04-24_0246_rank30-park-reframe.md`
- `research/park_reframe/2026-04-17_2303_rank36-park-reframe.md`

### Rank-specific source notes
- `research/optimization_loop/2026-03-17_1653_rank36-clean-replication-park.md`

### Nearby evidence consulted
- `research/quant_digests/2026-04-23_0432_shapeaware-trendscore-portability-verdict.md`
- `research/quant_digests/2026-04-23_0502_max-momentum-lottery-spike-filter-alpha.md`
- `research/quant_digests/2026-04-23_1249_global-intraday-tsmom-marketchar-portability.md`

## What Rank 36 originally tried to do
原始 `Rank 36` 不是完整 raw alpha，而是一张很便宜的 honesty / decomposition 卡：
- `recent_sign_only`
- `history_drift_only`
- `recent_and_drift_agree`

它真正想回答的是：
> 15m 上看起来像 own-past continuation 的东西，究竟是在吃真正的 recent continuation，还是只是把更慢的 drift / path contamination 换了个说法。

## Why it was parked
原 clean replication 的 blocker 没有变：
- `recent_sign_only @ 6bps/side ≈ -53.20%`
- `history_drift_only @ 6bps/side ≈ -18.13%`
- `recent_and_drift_agree @ 6bps/side ≈ -49.58%`
- `recent_and_drift_agree` 的三段 time buckets 也都没有给出值得继续投预算的 pocket。

所以 old `Rank 36` 被 park，不是因为“路径 / 趋势质量”这个母主题彻底没信息，而是因为：
1. 它只证明了 contamination concern 真实存在；
2. 没证明这张 `recent sign vs drift` honesty gate 本身能长成 queue-facing 主语；
3. 一旦往前走，自然就会滑向新的 `path-quality / continuation-quality / market-state` raw-alpha 或 router family。

## Hard park or soft park?
**本轮判断仍是：`keep_park`，且更像 `hard park with consumed residual`。**

为什么：
- 旧 Rank 36 剩下的价值基本只够做“别把 contaminated recent sign 误写成 alpha”的审计提醒；
- 4 月 23 日的新证据虽然继续支持“走势质量比分段裸收益更重要”，但它们给出的主语已经不是 old `Rank 36`，而是新的 `path-smoothness / low-MAX / market-characteristics admission` 宿主；
- 这意味着 residual value 继续外流，而不是回流到 old rank 本体。

## Is there a rescue signal?
**有，但只是主题级可救信号，不是旧 rank 级可救信号。**

### A. shape-aware trend score
`2026-04-23_0432_shapeaware-trendscore-portability-verdict.md` 说明：
- 同样是过去涨了，路径更平滑、更单调的那类 continuation 更值得追；
- 但当前更像新的 `path smoothness × continuation` raw-alpha / router，而不是把 old `recent_sign_only` 诚实修成 `Rank 36b`。

### B. low-MAX continuation quality
`2026-04-23_0502_max-momentum-lottery-spike-filter-alpha.md` 说明：
- 真 continuation 更像低尖刺、非 lottery 的路径；
- 它救的是“把 spike-heavy 假强势和平滑真强势拆开”的新 momentum-quality host；
- 主语已经变成 `recent return + spike quality`，不是 old `recent sign vs drift` 诊断卡。

### C. market-characteristics gate
`2026-04-23_1249_global-intraday-tsmom-marketchar-portability.md` 说明：
- 裸 `30m -> 30m` continuation 在 crypto liquid majors 上更像手续费陷阱；
- 真正留下的信息是高波动 / 更可交易 market-characteristics admission；
- 这继续把 residual value 推向新 `market-state gate / router`，而不是救活 old `Rank 36` 本体。

### 小结
因此本轮真正的可救信号只能写成：
> **路径质量 / 尖刺质量 / 市场特征 admission 仍有信息，但它们已经属于新的 continuation-quality family；它们没有把 old `Rank 36` 的 honesty gate 救回队列。**

## The single best modification axis
如果只允许保留 **1 条唯一主修改轴**，本轮答案仍然只能是：

> **把 old `Rank 36` 彻底降级成 `continuation contamination / path-quality decomposition diagnostic note`。**

但这不是 queue-facing hypothesis：
- 它不产生新的独立 tradeable 主语；
- 它只是在提醒后续方向线：先拆 `recent sign` 里混进来的 drift / smoothness / spike / market-state，再决定该归到哪个新 family。

## Should this become a derived hypothesis now?
**不值得。最终结论：`keep_park`。**

原因：
1. **原 blocker 没被推翻。** old `Rank 36` 仍然不是可交易主语，只是诚实地证明了 contamination 问题存在。
2. **新证据救的是新宿主。** 4 月 23 日三条 digest 都在把 residual value 推向新的 path-quality / low-MAX / market-characteristics host。
3. **没有新的单轴仍以 Rank 36 为主语。** 若现在硬写 `Rank 36b`，本质是在把“研究 hygiene 规则”伪装成“新候选”。
4. **原 park 的审计意义应保留。** old `Rank 36` 应继续作为“别把 contaminated recent sign 当 alpha”的负面教材，而不是再被包装成待认领条目。

## Trade on / trade off if revisited later
> 本轮不 draft，只记录若以后再碰该主题时，什么才是诚实边界。

- trade on:
  - 保留 `path smoothness / low-MAX / market-characteristics admission` 作为新 continuation-quality family 的研究入口；
  - 这些变量可以服务新的 raw-alpha / router / host-local admission。
- trade off:
  - 放弃 old `Rank 36` 作为 standalone queue-facing hypothesis；
  - 也放弃把 contamination diagnostic 换语法包装成新的 `Rank 36b`。

## Bottom line
1. **原 rank 为什么 park？**
   - 因为 `recent_sign_only / history_drift_only / recent_and_drift_agree` 在 15m 上都没站住，证明了污染问题，却没长成可推进 alpha。
2. **更像 hard 还是 soft park？**
   - 现在更像 **`hard park with consumed residual`**。
3. **有没有可救信号？**
   - 有，但只是主题级：路径质量、尖刺质量、市场特征 admission 仍有信息；它们不属于 old `Rank 36` 本体。
4. **最值得改的唯一一刀是什么？**
   - 只剩把它彻底降级成 `contamination / decomposition diagnostic note`。
5. **是否值得形成新的 derived hypothesis？**
   - **不值得；本轮继续 `keep_park`。**

## File-update / commit note
- 本轮只做 park-reframe 侧最小必要文档更新：本日志、`research/park_reframe/INDEX.md`、`docs/PARK_REFRAME_QUEUE.md`。
- 未改 `docs/TODO.md` 顶部排班。
- 共享工作区存在大量与本轮无关的脏文件，本轮不做 commit，避免混提。
