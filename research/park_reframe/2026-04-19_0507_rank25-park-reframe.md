# 2026-04-19 05:07 UTC · Rank 25 park reframe review

## 本轮为什么选 Rank 25
- 先按 bot6 固定顺序读了 `docs/TODO.md`、`docs/PARK_REFRAME_QUEUE.md`、`docs/RECENT_PAPER_SEEDS.md`、`research/quant_digests/INDEX.md`、`research/park_reframe/INDEX.md`。
- 本轮仍只处理 1 条已 `park` 的 rank。
- `Rank 50+` 与 `80~110` 号段近几天已连续覆盖很多轮；回到 `1~24 -> 25~49` 轮转时，`Rank 25` 最近一次 bot6 复盘在 `2026-04-11 00:32 UTC`，已超过 7 天，符合“低频重看、避免 7 天内重复同一条”的约束。
- `Rank 25` 也有清楚的历史 residual（`Rank 25b / 25c`），因此适合检查：最近 4 月 18~19 的 breakout / trend-shell 新证据，是否真的能支持再派生一条新的窄 reframe。

## 这次额外回看的材料
- `research/optimization_loop/2026-03-17_0623_rank25-time-redwatch-park.md`
- `research/optimization_loop/2026-04-09_0121_rank25c_ema_context_donchian_primary_fresh_intake_background.md`
- `research/optimization_loop/2026-04-17_2238_rank25c_conditional_freshintake_background_p0_consumed.md`
- `research/quant_digests/2026-04-18_0431_rsi-breakout-trend-shell.md`
- `research/quant_digests/2026-04-18_0558_session-orb-widthgate-shell.md`
- `research/quant_digests/2026-04-19_0446_supertrend-volgate-shortflip-router-alpha.md`

## 1) 原 Rank 25 为什么 park
核心审计结论没有变化：
- 原 `Rank 25 / EMA + Donchian breakout` 不是先死在“完全没 pocket”，而是死在 **time red-watch 反复不诚实**。
- `2026-03-17` 的最小诚实 recheck 已把 blocker 说得很清楚：无论看原主变体邻域，还是诚实缩到 `ETH+SOL-only`，时间结构都反复出现
  - `bucket_1 负`
  - `bucket_2 正`
  - `bucket_3 负`
- 这说明问题不是“某个参数像素没调对”，而是旧写法的 edge 太依赖中段时间 pocket；一旦要求更诚实的时间稳定性，它就不能升到更高优先级。

## 2) 它更像 hard park 还是 soft park
结论：**soft park，但已经非常接近 hard park with consumed residual。**

原因：
- 它确实曾留下一点可讨论残余，不是最初就“一眼纯死”。这也是后来会有 `Rank 25b`（30m regime matrix gate）与 `Rank 25c`（EMA 降级为 HTF context-only）两条窄派生的原因。
- 但这些残余已经被 runtime 真正消费过：
  - `Rank 25c` 已在 `2026-04-09` 被首判收口为 `background / P0`；
  - `2026-04-17` 又被 conditional fresh intake 再次确认：`EMA context-only` 没有修复 `bucket_1负 / bucket_2正 / bucket_3负` 的时间塌陷，只是 shared HTF gate 的岗位重写，不构成新的独立 after-cost pocket。
- 换句话说，`Rank 25` 不是“完全没有可救信号”，而是**唯一自然 residual 已被验证并消费过**，所以现在的 soft park 已经很接近“剩余价值被吃完”的 hard 化状态。

## 3) 还有没有“可救信号”
有，但只剩 **很弱的历史可救信号**，而且已基本被消费：
- 最自然的一刀一直都是：**Donchian breakout 才是主触发，EMA 更像 HTF context gate，而不是和平级 co-trigger。**
- 这条信号本身不是假的；问题在于它只解释了“角色分工更诚实”，没有解释“为什么时间稳定性会因此被修复”。
- `2026-04-09` 与 `2026-04-17` 的后续 intake / follow-up 已经说明：这条 residual 最多只够写成 shared context 语言，不够再单独站成 queue-facing alpha。

本轮把 4 月 18~19 的新证据一起看后，结论反而更收紧：
- `RSI breakout trend-shell` 说明：趋势 / breakout 主题若还有信息，更像 **完整 trend shell**；
- `session ORB width-gate shell` 说明：breakout 主题若还有信息，更像 **session + box-width 条件化的完整 raw alpha 壳**；
- `SuperTrend vol-gate short-flip` 说明：趋势翻转 / breakout 跟随主题若还能活，更像 **ATR trail + vol gate + strongest-only router** 这类新宿主。

这些新证据都没有推翻旧 `Rank 25` 的 park blocker；相反，它们更明确地把“可救主题”推向新的 raw-alpha / shell 宿主，而不是旧 `Rank 25` 再派生一条 `Rank 25d`。

## 4) 最值得改的唯一一刀是什么
如果只允许回答一刀，答案仍然是旧的那一刀：

> **把 EMA 从 co-trigger 降级成 HTF context-only gate，只保留 Donchian breakout 作为唯一主触发。**

但这条一刀已经不是“新的可派生方向”，而是：
- 历史上最自然的 residual；
- 已被 `Rank 25c` 明确表达；
- 又已被后续 intake / follow-up 诚实消费。

因此，本轮不会再把同一刀换个措辞重写成 `Rank 25d`。

## 5) 是否值得形成新的 derived hypothesis
结论：**不值得。最终 verdict = `keep_park`。**

原因很直接：
1. 原 `park` 的审计意义仍然成立，不能推翻。
2. 唯一自然残余已经被 `Rank 25b / 25c` 覆盖，其中 `Rank 25c` 甚至已经过 fresh-intake + follow-up 双重消费。
3. 最近新增的 breakout / trend-shell 证据，救活的是更新的完整宿主，而不是旧 `Rank 25` 的新窄派生。
4. 若此时再写 `Rank 25d`，大概率只是把“旧 residual 已被消费”重新包装，不够诚实。

## 本轮简表
- 原 rank 为什么 park：`EMA + Donchian` 原写法在时间稳定性上反复出现 `bucket_1负 / bucket_2正 / bucket_3负`，不是单点参数问题。
- 更像 hard 还是 soft：`soft park`，但已很接近 `hard park with consumed residual`。
- 有没有可救信号：有，且只剩旧的 `EMA role-split` 残余；但这条线已被 `Rank 25c` 消费并验证不足。
- 最值得改的一刀：`EMA` 降级为 `HTF context-only gate`，`Donchian breakout` 保留为唯一主触发。
- 是否值得新派生：**不值得**。
- 本轮 verdict：**`keep_park`**。

## 对 queue 的写回口径
建议把本轮口径收得很短：
- `Rank 25` 继续保留 `park`；
- 说明它仍属 `soft park`，但更接近 `hard with consumed residual`；
- 明确旧 rank 的唯一诚实 residual 仍只到既有 `Rank 25b / 25c`，而 `Rank 25c` 又已在 4 月中旬被 fresh-intake / follow-up 证明只是 shared HTF context gate 的岗位重写，不足以再诚实派生 `Rank 25d`；
- 同时点出 4 月 18~19 新增的 RSI breakout / session ORB / SuperTrend 证据，更像新的 breakout / trend-shell 宿主，而不是旧 `Rank 25` 的再派生依据。

## 提交说明
- 本轮只做最小必要文档改动。
- 未做 git commit。
- 原因：工作区存在多条与本轮无关的未跟踪 / 脏文件，当前不适合安全 selective commit。
