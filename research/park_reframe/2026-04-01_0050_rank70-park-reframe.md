# 2026-04-01 00:50 UTC — Rank 70 park reframe review

- Rank: `70`
- Theme: `fast-entry / slow-exit handoff spine`
- Original status: `park`（authoritative verdict 保留）
- This round verdict: `keep_park`

## 为什么这轮看它
- 按 `bot6` 当前低频轮转，默认仍优先补看 `Rank 50+` 里最近 `7` 天未复盘的 parked rank。
- `Rank 70` 在 `2026-03-18` 完成 source intake + minimal clean replication 后被压回 `park / evidence pool`，但之后还没有进入 `bot6` 的 park-reframe 审查。
- 它也适合做一次低频复盘：原命题是典型的“post-entry 管理层看起来合理，但 shared 写法未站住”的对象；而最近的新证据（尤其 `PSAR trailing role` 与 `trend/pullback correlation shell`）又正好能回答：**可救的是 Rank 70 本体，还是只是把主题继续上移成 setup-specific exit discipline / full-stack raw-alpha family。**

## 本轮补读
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/optimization_loop/2026-03-18_2312_rank70-clean-replication-park.md`
- `research/park_reframe/2026-03-27_1702_rank62-park-reframe.md`
- `research/park_reframe/2026-03-30_1805_rank35-park-reframe.md`
- `research/quant_digests/2026-03-18_2250_fast-entry-slow-exit-handoff-spine.md`
- `research/quant_digests/2026-03-20_1004_psar-trailing-role-not-default-exit.md`
- `research/quant_digests/2026-03-29_2242_trend-pullback-correlation-shell-alpha.md`

## 原 rank 为什么 park
原 `Rank 70` 想表达的是：
- 不再继续给三条 lane 发明新 entry；
- 而是给 `breakout_short / fib_retest_long / ema_psar_long` 三条 archetype 共用一条 **两段式 exit spine**：
  - 前 `2~3` 根先用 fail-fast 做生死检查；
  - 若 trade 已活过前段，或者顺向走出最小 MFE，再 handoff 到更慢的 `Donchian / Chandelier` trailing。 

原 minimal clean replication 把它压回 `park`，原因很集中：
1. `handoff` 只在 `ema_psar_long` 上相对 baseline 少亏：
   - `base≈-5.55%`
   - `handoff≈-1.96%`
   - 但仍然没有转正；
2. `fib_retest_long` 真正拉开差距的是 `all_slow_trailing`，不是两段式 `handoff`：
   - `base≈+0.88%`
   - `slow≈+5.91%`
   - `handoff≈-1.66%`；
3. `breakout_short` 上三种改写都更差：
   - `base≈-2.58%`
   - `fast≈-4.57%`
   - `slow≈-4.38%`
   - `handoff≈-4.71%`；
4. 主变体 `handoff_exit` 还伴随较高的利润回吐：
   - `mean_giveback_after_handoff≈78.60%`
   - `mean_handoff_rate≈60.83%`
   - `10bps/15bps` 成本下 aggregate 继续恶化。

翻成人话：
**Rank 70 被 park，不是因为“先快后慢”的 exit 哲学完全没信息，而是因为把它写成三条 lane 共用的 shared handoff spine 并不诚实：EMA 只是少亏，Fib 真正留下的是另一种更纯的 slow trailing pocket，而 breakout-short 则直接被拖坏。**

## 它更像 hard park 还是 soft park
我的判断：**`soft park`，但已经明显朝 hard park 那边偏。**

为什么不是 hard park：
- 原 clean replication 至少证明了一个方向：post-entry 管理层并非全无信息；
- `ema_psar_long` 的确受益于“别全程用同一把快刀砍单”；
- `fib_retest_long` 也说明“趋势单活下来后，慢 exit 可能比固定 8-bar hold 更合理”。

为什么又说它偏 hard：
- 这些残余并不支持原命题的 `shared handoff spine`；
- `Fib` 活下来的不是 handoff，而更像 `setup-specific slow trailing`；
- `breakout_short` 没被救活，说明 shared 角色已经破功；
- 近几天的新证据也在持续把价值上移：
  - 一部分上移到 **setup-specific exit / fail-safe discipline**（如 `PSAR trailing role`）；
  - 另一部分上移到 **完整 trend/pullback raw-alpha skeleton**，而不是继续在 Rank 70 这条 exit overlay 血缘里细切。

所以：
- 对“entry 后先快认错、活下来再慢拿”这个主题本身，仍是 soft park；
- 对原 `Rank 70` 这版三路共用的 queue-facing shared overlay，已经很偏 hard。

## 有没有“可救信号”
**有，但不够 distinct。**

### 可救信号 A：`ema_psar_long` 上确实有一点 handoff / failure-protocol 残余
- `handoff` 相比 baseline 少亏，说明 continuation trade 在前几根 bar 之后，管理时钟确实值得分层；
- 这与 `Rank 62` 的结论相呼应：**快认错 / failure protocol 有信息，但更像 continuation 自己的本地纪律，不像 shared overlay。**

### 可救信号 B：`fib_retest_long` 真正像样的是 `slow trailing`，不是 `handoff`
- 这说明“回踩确认后让 winner 多活一会儿”也许有意义；
- 但它留下的更像 long-side pullback / trend trade 的 setup-specific 持仓管理，而不是一条三路通用 spine。

### 可救信号 C：最近新证据更支持上移到更完整 family
- `2026-03-20` 的 `PSAR trailing role` 已明确：PSAR trailing 更像可选 fail-safe，而不是 shared 默认 exit；
- `2026-03-29` 的 `trend continuation × pullback re-entry × correlation-budget shell` 又进一步说明：如果趋势 / 回调主题要活，活下来的更像 **完整 raw-alpha skeleton**，不是单独再给旧 rank 补一根共享 handoff spine。

所以这轮的关键信号不是“Rank 70 还差一刀”，而是：
**残余是有的，但它已经分裂成 setup-specific exit discipline 与更上位的 full-stack raw-alpha family，不再自然收敛回一个新的 `Rank 70b`。**

## 最值得改的唯一一刀是什么
如果只保留 **1 条唯一主修改轴**，最值得改的一刀是：

**把 `shared fast-entry / slow-exit handoff spine` 降级成 `Fib retest_long / trend-pullback long` 专用的 slow-exit hold-extension overlay，不再服务 breakout_short，也不再坚持 handoff 必须是核心形态。**

也就是：
- 不再假装同一套 handoff 可以横向服务三条 lane；
- 优先承认 `Fib` 留下的不是 `handoff`，而是更窄的 `slow trailing after confirmed hold`；
- `EMA` 上的快认错残余则更像 `Rank 62` 那种本地 failure protocol，而不该再强绑到 Rank 70 里。

但也正因为如此，本轮不 draft：
- 这条“一刀”已经明显在退出原 `Rank 70` 的 shared 身份；
- 它会与既有 `Rank 62`（EMA 本地 fail-fast discipline）以及 `Rank 35b / trend-pullback full-stack family` 高度接近；
- distinctness 不够，容易变成重复记账。

## 是否值得形成新的 derived hypothesis
**本轮结论：不值得，维持 `keep_park`。**

原因：
1. 原 `park` 的审计意义仍然很强，不能推翻；
2. 原 shared `handoff spine` 已被 clean replication 审清：跨 lane 不统一，尤其 breakout-short 直接更差；
3. 唯一自然残余已拆成两部分：
   - `EMA continuation` 的本地 failure protocol（更像 `Rank 62` 的血缘）；
   - `Fib / trend-pullback long` 的 slow-exit hold extension（更像 `Rank 35b` 与更新的 full-stack trend/pullback family 的血缘）；
4. 继续硬写 `Rank 70b`，大概率只是把已有近邻 residual 换壳挂回 Rank 70，不够 distinct，也不够诚实。

## 本轮按模板回答
1. **原 rank 为什么 park？**
   - 因为 `shared handoff spine` 没有形成跨 lane 的统一增量：`EMA` 只是少亏，`Fib` 真正有效的是 `all_slow_trailing` 而不是 handoff，`breakout_short` 更是整体变差。
2. **它更像 hard park 还是 soft park？**
   - `soft park`，但对原 shared 写法已明显偏 hard。
3. **有没有“可救信号”？**
   - 有；主要是 `EMA continuation` 的本地快认错纪律，以及 `Fib / trend-pullback long` 的 slow trailing hold-extension 残余。
4. **最值得改的唯一一刀是什么？**
   - 把 `shared handoff spine` 降级成 `Fib / trend-pullback long` 专用的 slow-exit hold-extension overlay。
5. **是否值得形成新的 derived hypothesis？**
   - 不值得。
6. **为什么不写 `Rank 70b`？**
   - 因为唯一自然残余已经分别漂向 `Rank 62` 式本地 failure protocol 与 `Rank 35b / 更上位 trend-pullback raw-alpha family`，当前不够 distinct，容易重复记账。

## 最终结论
- `Rank 70` 原 `park` verdict：**保留**
- 本轮状态：**`keep_park`**
- 一句话总结：
  - **Rank 70 仍是 soft park，但对原 `shared fast-entry / slow-exit handoff spine` 读法已明显偏 hard；它留下的残余已分裂成 EMA 本地 failure discipline 与 long-side slow-exit hold-extension，两者都更像应被近邻 residual / 更上位 trend-pullback raw-alpha family 吸收，而不是再诚实派生出 `Rank 70b`。**

## 对 queue 的最小写回建议
- `docs/PARK_REFRAME_QUEUE.md`：追加一条 recently reviewed
- `research/park_reframe/INDEX.md`：追加本轮索引
- 默认不改 `docs/TODO.md`

## Git / 工作区备注
- 当前工作区存在大量与本轮无关的共享脏文件；本轮只做最小文本写回，不做 commit。
