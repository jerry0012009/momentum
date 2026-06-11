# 2026-04-04 11:40 UTC — Rank 59 park reframe

## 本轮选择
- 当前 `bot6` 轮转仍优先看 `Rank 50+`；最近 7 天已覆盖 `50/51/52/54/57/58/62/67/79/84/87/101/103` 等条目，而 `Rank 59` 上次低频复盘是 `2026-03-27 12:22 UTC`，已超过 7 天。
- 过去 24h 又新增了更直接的短周期趋势壳旁证（`Wilder RSI breakout × EMA200/ADX/volume × fast exit`、`dual-SuperTrend × EMA50 × volume gate`），值得再判断一次：原 `Ichimoku Kijun + cloud-side continuation gate` 是否还保留一个诚实的新窄派生空间。

## 读集
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/park_reframe/2026-04-04_0924_rank58-park-reframe.md`
- `research/park_reframe/2026-04-04_0706_rank32-park-reframe.md`
- `research/optimization_loop/2026-03-18_1537_rank59-source-intake.md`
- `research/optimization_loop/2026-03-18_1557_rank59-clean-replication.md`
- `research/optimization_loop/2026-03-18_1640_rank59-time-stability-park.md`
- `research/park_reframe/2026-03-27_1222_rank59-park-reframe.md`
- `research/quant_digests/2026-04-03_2141_wilder-rsi-fast-exit-trend-shell-alpha.md`
- `research/quant_digests/2026-04-04_1050_dual-supertrend-nonfiring-alpha.md`

## 原 rank 为什么 park
原 `Rank 59` 想做的是：
- 用 `Ichimoku` 的 `Kijun` 与 `cloud-side` 充当 15m continuation 的 shared 结构确认层；
- 让它横向服务 `ema_psar_long / fib_retest_long / breakout_short` 等 lane；
- 核心故事不是独立 raw alpha，而是“价格已回到云外 / 站稳 Kijun 时，顺趋势 continuation 更可信”。

但 clean replication + time-stability 的审计结论已经很清楚：
- 在 `ema_psar_long` 上，`cloud_side` / `kijun+cloud_side` 只留下“少亏一些”的薄残余；
- 在 `fib_retest_long` 上，改善主要靠**极端砍样本**，`kijun+cloud_side` retention 只剩约 `6.06%`；
- 在 `breakout_short` 上几乎没有修好问题；
- 便宜 time-stability 后，`ema_psar_long / cloud_side` 也是前两桶偏负、只在最后一桶转正，不像稳定主轴。

翻成人话：
**原 Rank 59 不是完全没信息，而是只在很窄、很晚、很 setup-specific 的 pocket 留下残余，不足以继续撑住“跨 setup 的 shared continuation gate”这个岗位。**

## 它更像 hard park 还是 soft park
**结论：`soft park`，但现在比 3/27 那轮更偏硬。**

为什么仍算 soft park：
- `Kijun / cloud-side` 至少不是纯未来函数或明显假命题；
- 它确实留下了“慢趋势上下文可能有信息”的残余。

为什么现在更偏硬：
- 这点残余越来越不像 `Rank 59` 自己还能诚实派生的新 rank；
- 最近新证据把“慢趋势确认”继续上移到**更完整的 trend-shell raw alpha 宿主**，而不是回流到旧 shared gate 写法。

## 有没有可救信号
**有，但已更明显地不属于 `Rank 59` 本体。**

当前还能保留的可救信号只有一条：
- `Ichimoku` 留下的不是“再加一道 continuation gate”，而是**慢趋势 / trend-readiness context** 这层语义仍可能有信息。

但最近新增旁证进一步说明，这条残余更适合待在新的完整趋势壳里：
1. `2026-04-03_2141_wilder-rsi-fast-exit-trend-shell-alpha.md`
   - 强调的是 `RSI breakout × EMA200/ADX/volume allow × fast exit` 这类**完整 short-cycle trend shell**；
   - 这里的长均线 / 趋势确认角色，本质上已经覆盖了 Rank 59 想表达的“先确认慢趋势，再谈 continuation”。
2. `2026-04-04_1050_dual-supertrend-nonfiring-alpha.md`
   - 虽然源码现状几乎不触发，但它同样把“慢趋势确认”摆在**完整 raw alpha 宿主**里（dual ST + EMA50 + volume），而不是摆成跨三条 lane 复用的 shared gate。

所以可救的不是：
- 再写一个 `Rank 59b`，继续做 `Ichimoku` shared gate；

而是：
- 承认 `Rank 59` 留下的慢趋势语义，更适合被新的 trend shell 宿主吸收。

## 最值得改的唯一一刀是什么
如果只保留 **1 条唯一主修改轴**，本轮最值得改的一刀仍然是：

**把 `Ichimoku Kijun + cloud-side` 从 shared continuation gate 继续降级成更慢的 HTF context-only trend-bias / trend-readiness overlay。**

但这刀本轮**不值得再单独写成新的 `Rank 59b`**，原因有三：
1. 这不是新故事，本质上仍是在重复 `Rank 25c / Rank 35b` 一类“慢趋势线更像 context、不像平级触发器”的角色改写；
2. 最近新增的趋势壳证据（Wilder RSI / dual SuperTrend）又把这层语义进一步抬升到新的完整 raw-alpha 宿主；
3. 若现在硬写 `Rank 59b`，只会把“慢趋势 context gate”换个 `Ichimoku` 外壳重讲一遍，削弱原 `park` verdict 的审计边界。

## 是否值得形成新的 derived hypothesis
**不值得。最终结论：`keep_park`。**

原因：
- 原 `park` blocker 没被推翻：作为跨 setup shared continuation gate，它仍然主要靠薄 pocket / 大幅砍样本减亏；
- 唯一诚实修改轴只是继续降级成慢趋势 context-only 角色，而这条路已被既有提案与更近的新 trend-shell 证据吸收；
- 最近新证据的方向更像“开新 trend-shell family”，不是“再诚实派生一个 Rank 59b”。

## 模板回答
1. **原 rank 为什么 park？**
   - 因为 `Kijun / cloud-side` 作为 shared continuation gate 只在 `ema_psar_long` 留下薄残余，在 `fib_retest_long` 上主要靠极端砍样本、在 `breakout_short` 上几乎无效，而且时间稳定性不足。
2. **更像 hard park 还是 soft park？**
   - `soft park`，但比上次复盘更偏硬。
3. **有没有可救信号？**
   - 有；但更像慢趋势 / trend-readiness context 语义仍有信息，不像 `Rank 59` 本体还能再诚实派生。
4. **最值得改的唯一一刀是什么？**
   - 把 `Ichimoku Kijun + cloud-side` 从 shared continuation gate 继续降级成 HTF context-only trend-bias / trend-readiness overlay。
5. **是否值得形成新的 derived hypothesis？**
   - 不值得。

## 最小审计结论
- 保留原 `park` verdict；
- `Rank 59` 本轮仍记为 **`keep_park`**；
- 它留下的不是值得新写 `Rank 59b` 的独立残余，而是应继续由既有 `EMA context-only` 提案与更近的新趋势壳宿主承接的慢趋势语义。

## Git
- 当前 repo 存在无关脏文件；本轮只做 park-reframe 所需最小文本更新，不改 `docs/TODO.md`，也不做混合提交。
