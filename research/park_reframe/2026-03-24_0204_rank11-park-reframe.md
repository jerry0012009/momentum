# 2026-03-24 02:04 UTC｜bot6 park-reframe｜Rank 11

## 0) 本轮选择（为什么是 Rank 11）
- 本轮只处理 `Rank 1~37` 中已 `park` 的 1 条，不改 `TODO` 顶部排班，不替 `bot2 / bot3` 分配新任务。
- 严格说，`Rank 11` 在最近 7 天内已被 bot6 复盘过；正常应优先换别的。
- 但当前 `Rank 1~37` 里多数 parked rank 最近都已轮过，而 `Rank 11` 这几天又新增了更直接相关的旁证：
  - `research/quant_digests/2026-03-23_0205_orb-phase-retest-score-not-hard-gate.md`
  - `research/quant_digests/2026-03-23_0312_ft-nft-killzone-postbreak-router.md`
- 所以这轮只回答一件事：这些新证据，是否足以让原 `Rank 11 / Lo-style causal extrema pattern gate` 派生出一条新的窄 reframe hypothesis。

## 1) 原 Rank 为什么 park？
原始硬结论来自：
- `research/optimization_loop/2026-03-16_2343_rank11-clean-replication-park.md`
- `research/park_reframe/2026-03-21_0702_rank11-park-reframe.md`

原 Rank 11 被 park，不是因为“还差一道确认层就能救活”，而是 clean replication 本身已经把这条 pattern gate 压成了**全维度偏负**：
- `mean_total_return ≈ -4.33%`
- `positive_asset_ratio = 0/3`
- `mean_trades ≈ 58.3`
- Light Stability Pack 四项全 fail：
  - 时间稳定性：`1/3`
  - 参数稳定性：`0/5`
  - 跨标的稳定性：`0/3`
  - 成本/交易数稳定性：`0/4`

翻成人话：
- 问题不是“Lo-style causal extrema 模式识别基本对，只是后处理太粗”；
- 而是这条触发本体在 15m BTC/ETH/SOL 上，就没有表现出足够稳、足够厚、足够可复用的主体 pocket。

所以原 `park` verdict 的审计意义必须保留，不能被改写成“其实只差一个更聪明的 post-break filter”。

## 2) 它更像 hard park 还是 soft park？
- **结论：仍更像 `hard park`。**

原因：
- `Rank 11` 的失败不是单个实现瑕疵，也不是单纯成本过线；
- 它更像 pattern 本体就没有形成能承载二次过滤的主体 edge；
- 新证据虽然有价值，但更像是在告诉我们：**后续路径判决要更诚实**，而不是在替 `Rank 11` 这条旧 trigger 翻案。

## 3) 有没有“可救信号”？
- **有一点，但还不够形成 Rank 11 专属的可救信号。**

这轮新增旁证真正增加的信息是：
1. `retest` 更像 phase state machine 的一个阶段，不该被写成独立 hard gate；
2. `post-break path` 更应该先区分 `FT / NFT` 双路径，再决定 continuation / failure verdict；
3. `killzone / timeout / abort` 更适合服务“已有主体 pocket 的 breakout follow-up”，不是给弱 trigger 兜底。

这些信息都很像在帮助：
- `breakout-short / final-verdict`
- `Fib retest_hold`
- `EMA/PSAR` 的 follow-up / context 层

但对 `Rank 11` 来说，核心问题仍然没变：
- 原线并不是“有不错 pocket，只差 honest router”；
- 而是模式触发本体 clean replication 后就已经四项稳定性一起偏负。

所以新证据最多说明：
- `phase-state / FT-NFT router` 这类思想值得保留；
- 但它更适合挂在现有更强的主线上，而不是拿来为 `Rank 11` 生造 `Rank 11b`。

## 4) 最值得改的唯一一刀是什么？
如果硬要写，一刀最像的是：
- **把 `Lo-style causal extrema pattern gate` 改写成 `pattern event -> FT/NFT router / timeout verdict`。**

但这刀当前**不够诚实**，因为它仍然是在给一个已经 hard-fail 的弱 trigger 叠第二层路由，而不是在修一个已有主体 pocket 的 setup。

换句话说：
- 对强 setup，这叫“更诚实的 post-break verdict”；
- 对 `Rank 11`，这更像“给失败模式再加一层包装”。

所以本轮更诚实的答案是：
- **没有足够干净、足够独特、足够单轴的唯一一刀。**

## 5) 是否值得形成新的 derived hypothesis？
- **不值得。**
- 最终 verdict：`keep_park`

原因：
1. 原 `park` 的主 blocker 没被新证据推翻；
2. 新证据主要在强化共享的 `phase-state / FT-NFT / timeout` follow-up 语言，不是 `Rank 11` 专属 rescue path；
3. 若现在硬写 `Rank 11b`，很容易把“pattern 本体失败”包装成“再叠一个 honest router 也许能行”，这不够诚实。

## 6) 本轮结论（按模板）
1. **原 rank 为什么 park？**
   - 因为 clean replication 后收益、跨资产、时间、参数、成本四个层面一起偏负，模式本体没有形成可复用主体 edge。
2. **更像 hard park 还是 soft park？**
   - `hard park`。
3. **有没有可救信号？**
   - 有一点，但更像共享 follow-up / verdict 层的新语言，不像 Rank 11 专属救法。
4. **最值得改的唯一一刀是什么？**
   - 若硬写，只能是 `pattern event -> FT/NFT router / timeout verdict`；但这刀对 Rank 11 不够诚实。
5. **是否值得形成新的 derived hypothesis？**
   - 不值得。
6. **为什么不立 `Rank 11b`？**
   - 因为新证据没有改变原 trigger 本体偏弱的事实；它更适合服务现有更强 setup，而不是给 Rank 11 再叠一层二次守门。

## 7) 允许的最终结论
- `keep_park`

## 8) 最小审计结论
- 原 `park` 保留；
- `Rank 11` 本轮仍读作 **hard park**；
- 新增的 `phase-state / FT-NFT router / timeout` 证据，主要应作为 breakout / retest / follow-up 主线的共享语言使用，不足以把 `Rank 11` 再诚实派生成一个新的窄 hypothesis。

## 9) 文件改动
- 新增本轮日志：本文件
- 追加更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`

## 10) Git
- 未 commit。
- 原因：workspace 存在大量无关脏文件 / 未跟踪文件；本轮只做最小必要文档改动，不安全混提。
