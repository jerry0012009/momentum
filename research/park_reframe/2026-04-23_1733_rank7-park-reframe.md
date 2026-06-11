# 2026-04-23 17:33 UTC · Rank 7 park reframe

## Selected rank
- `Rank 7 / adaptive trend combo`
- selection note:
  - 本轮继续严格只处理 `1` 条已 `park` 的 `Rank 1~37`。
  - 近期 `50+` 与 `80~110` 已连续覆盖，随后回到 `1~24`。
  - `Rank 7` 上次 bot6 复盘是 `2026-04-15 10:59 UTC`，当前已超过 `7` 天门槛。
  - 且 4 月 21 日又出现了与该主题直接相关的新证据：`CTREND XS tech-stack` 与 `triple EMA stack × RSI veto × ATR bracket`，足以再回答一次：这些证据究竟是在救旧 Rank 7，还是继续把主题推向新的 full-shell / raw-alpha 宿主。

## Source evidence read
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/optimization_loop/2026-03-16_2221_rank7-clean-replication-park.md`
- `research/park_reframe/2026-04-15_1059_rank7-park-reframe.md`
- `research/quant_digests/2026-04-21_0405_cttrend-xs-techstack-alpha.md`
- `research/quant_digests/2026-04-21_1358_tripleema-rsi-atr-stack-alpha.md`

## 1) 原 rank 为什么 park？
原 `Rank 7` 被 park 的审计结论不变。

根据 `2026-03-16_2221_rank7-clean-replication-park.md`：
- 它失败的不是“趋势/状态信息完全没用”，而是 **把 adaptive combo 写成 `15m` bar-level direct blended entry vote** 这件事不成立；
- 唯一看起来不差的 `fixed_priority` 版本，依赖极端稀疏交易：`mean_no_trade_ratio≈98.60%`；
- 一旦放松到更可交易的密度，代表性版本就一起转负：
  - `state_weighted_vote ≈ -21.75%`
  - `equal_vote ≈ -33.68%`
  - 两者 `positive_asset_ratio = 0/3`
- 参数邻域也没站住：Light Stability Pack 里 `parameter stability = fail`。

所以原 `park` 的核心意思仍是：
> **旧 Rank 7 不能再被诚实地读成一个统一、可部署的 direct combo entry engine。**

## 2) 它更像 hard park 还是 soft park？
- **本轮判断：`soft park`，但对旧 Rank 7 本体已更接近 `hard park with consumed residual`。**

为什么还保留 soft：
- 被否掉的是“direct blended vote”这个岗位，不是 trend / alignment / readiness 主题本身；
- 它历史上确实留下过两个诚实 residual：`Rank 7b`（one-regime-per-session overlay）与 `Rank 7c`（mid-score band-pass alignment overlay）。

为什么又更接近 hard：
- 旧 Rank 7 唯一自然 residual 已经被 `7b / 7c` 吃掉；
- 4 月 21 日新证据没有把主题拉回“旧 combo 再切一刀”，反而继续说明：真正还能活的，是新的完整 trend shell、router 或 parent-signal 宿主。

## 3) 有没有“可救信号”？
- **有，但继续远离旧 Rank 7 本体。**

### A. `2026-04-21_0405_cttrend-xs-techstack-alpha.md`
这条新证据保留下来的主语是：
- **多时域技术状态聚合** 更适合做 `cross-sectional scorer / router`；
- 甚至分钟级 naive 聚合本体并不适合直接当主 alpha；
- 也就是“技术组合”还能活，但更像排序层、路由层，而不是单币 `15m` 直接投票开仓层。

### B. `2026-04-21_1358_tripleema-rsi-atr-stack-alpha.md`
这条新证据更直接说明：
- `EMA stack` 这类组合变量若还有信息，也更像 **trend raw-alpha 的 parent signal**；
- `RSI` 更像不过热 veto；
- 真正要补的是 `5m pullback / breakout child trigger`、execution 与 gate，而不是把多个技术组件再压成一个统一 direct vote。

所以，本轮“可救信号”的诚实表述是：
> **adaptive / technical combo 主题还活，但它活着的方式更像新的 trend-shell、router、或 parent-signal 宿主，而不是旧 Rank 7 再派生一个新的 Rank 7d。**

## 4) 最值得改的唯一一刀是什么？
如果只谈旧 `Rank 7` 最值得保留的唯一一刀，仍然只是：

**把 adaptive trend combo 从 direct blended entry vote 降级成 setup 触发后的 alignment overlay。**

也就是既有 `Rank 7c` 的那条轴：
- 不让 combo 自己直接开仓；
- 只在现有 setup 已触发后，再用 alignment score 做中段放行、尾部降仓或 veto。

但这已经不是新轴：
- 它已被 `Rank 7c` 明确表达；
- 本轮 4 月 21 日新证据也没有给出比 `7c` 更独立、更新的唯一主修改轴。

## 5) 是否值得形成新的 derived hypothesis？
- **本轮结论：`keep_park`。**

原因：
1. 原 `park` 审计对象是 `adaptive trend combo as direct entry vote`，这个失败没有被推翻；
2. 旧 Rank 7 唯一诚实 residual 仍只到既有 `Rank 7b / 7c`；
3. 4 月 21 日新增的 `CTREND XS tech-stack` 与 `triple EMA stack` 证据，继续把“技术组合”主题抬升到新的 router / parent-signal / full-shell 宿主；
4. 若现在硬写 `Rank 7d`，大概率只是：
   - 重复 `7b / 7c`；或
   - 偷换成新的 trend-shell / ranking alpha，破坏 queue 简洁性与原 `park` 的审计意义。

## Final verdict
- `verdict`: `keep_park`
- `original_verdict_kept`: `park`
- `one-line note`: `soft park，但对原 adaptive blended entry vote 读法已更接近 hard with consumed residual；4 月 21 日新增的 CTREND XS tech-stack 与 triple-EMA stack 新证据继续说明 combo 主题若还有信息，更像新的 router / parent-signal / trend-shell 宿主，而不是足以从旧 Rank 7 再诚实派生 Rank 7d。`

## File actions
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`
- 未改：`docs/TODO.md`

## Commit
- 本轮默认不做 commit。
- 原因：只做最小必要文档改动；仓库长期存在无关脏文件，避免混提。
