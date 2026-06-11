# 2026-03-27 02:30 UTC｜bot6 park-reframe｜Rank 87

## 0) 本轮选择（为什么是 Rank 87）
- 按 `docs/PARK_REFRAME_QUEUE.md` 当前轮转，近期已连续覆盖多条 `50+` 与 `80~110` 号段 parked rank；在 `80~110` 里，**`Rank 87` 近 7 天尚未被 bot6 单独复盘**，符合“优先换别的、但仍留在当前优先号段”的要求。
- `Rank 87 / volume-clock + CS spread interaction gate` 很适合低频审计：它原本不是 raw alpha，而是一个看上去“也许还能救”的 shared gate；但它到底是 `soft park` 残余，还是已经该彻底留在历史审计里，需要重新钉一次。
- 本轮目标不是推翻原 `park`，而是回答：**原 Rank 87 留下的 volume-clock / liquidity-state 残余，是否还值得诚实地切成一个新的窄 reframe hypothesis。**

## 1) 原 Rank 为什么 park？
原始证据来自：
- `research/optimization_loop/2026-03-19_1102_rank87-volume-clock-intake.md`
- `research/optimization_loop/2026-03-19_1126_rank87-clean-replication-park.md`
- `research/quant_digests/2026-03-19_0956_volume-clock-cs-spread-interaction-gate.md`

原 Rank 87 的核心写法是：
- 不把 `volume clock` 当独立方向 alpha；
- 而是把“最近 24h 最大成交 30m anchor + impulse + CS spread 状态”写成一个 `15m` continuation / retest 的 shared allow/deny gate；
- 并拿它去和 `fixed clock`（`00/08/16 UTC`）做对照。

它最后被 park，原因很清楚：
1. intake 级证据只证明了一个很窄的事实：**真实最大成交窗口往往不等于固定 funding/整点锚点**；这说明固定时钟很粗，但还不等于这个 gate 能赚钱。
2. 最小 clean replication 后，`volume_clock_gate` 虽然明显“少亏”，但几乎全靠极端砍样本换来：
   - `baseline retention ≈ 86.96%`
   - `fixed_clock_gate retention ≈ 8.22%`
   - `volume_clock_gate retention ≈ 3.42%`
3. 在 `6bps/side` 下，结果仍然没有跨过诚实门槛：
   - `baseline mean_total_return ≈ -28.85%`
   - `fixed_clock_gate ≈ -5.73%`
   - `volume_clock_gate ≈ -0.67%`
4. 这说明它不是“找到了一条更强 gate”，而更像“把大部分交易都砍掉后，看起来没那么差”。
5. 换句话说，原 Rank 87 证明了 `fixed clock` 不够好，却**没证明 `volume-clock + CS spread` 值得继续作为 queue-facing 共享 gate 活下去**。

翻成人话：
- 原 Rank 87 的 insight 不是零；
- 但它留下的是“别把时钟写死”的方法论提醒，不是一个已足够诚实的新可交易层。

## 2) 它更像 hard park 还是 soft park？
**结论：`soft park`，但现在比当时更偏硬。**

为什么不是 hard park：
- 它确实抓到一点有信息的东西：固定 funding/整点时钟和真实交易活跃时段并不重合；
- 说明 `clock / liquidity-state` 主题本身没有彻底失效。

为什么又说“更偏硬”：
- 它原本留下的那点可救空间，是建立在“volume spike 也许能帮助确认趋势 continuation”这个隐含前提上；
- 但 2026-03-27 新 digest `research/quant_digests/2026-03-27_0223_volume-is-not-trend-alpha.md` 又把这个前提钉得更窄：**volume 更像 price-first 之后的 confirmation / veto / sizing，而不是趋势发动机本体**；
- 这会直接削弱 Rank 87 继续作为 shared allow/deny gate 的独立身份。

所以它仍算 `soft park`，因为主题没死；但对 **“原 Rank 87 这版写法”** 来说，已经更接近偏硬的 `keep_park`。

## 3) 有没有“可救信号”？
**有，但只剩非常薄的一层：`别把固定时钟当真 market clock`。**

当前还能保留的信号主要有两层：
1. `volume-clock` 提醒我们，真实 intraday 活跃窗口是漂移的，不该默认写死在 funding/整点；
2. `CS spread / liquidity state` 这类变量，也许仍能作为某些 price-first setup 的二层质量特征。

但问题同样明确：
- 这些残余更像**实现纪律 / feature note**，不是一条新的 queue-facing hypothesis；
- 最新 digest 已经把 volume 的角色进一步收窄到 `price-first, volume-second`；
- 若继续救 Rank 87，就会很容易滑成多轴改写：一边改时钟，一边改 volume 角色，一边改 gate 职责，这不符合本任务“每轮只保留 1 条唯一主修改轴”的要求。

## 4) 最值得改的唯一一刀是什么？
如果只保留 **1 条唯一主修改轴**，本轮最值得保留的一刀会是：

**把 `volume-clock + CS spread` 从 queue-facing shared allow/deny gate，进一步降级成 `price-first` 主体策略里的实现备注：只负责提醒“别把 fixed funding clock 当真实 market clock”，不再尝试单独包装成 Rank 87 的派生提案。**

但这一刀当前**不值得 draft 成 `Rank 87b`**，因为：
1. 这更像方法论修正，而不是一个 bot2 可直接判断是否入板的新 hypothesis；
2. 它缺少新的正 pocket，只是在把原 rank 的审计意义再收紧一层；
3. 真要继续写，也很容易和 `Rank 5b`（时钟/开段冲击）、`Rank 76`（clock-conditioned mode switch 候选）以及一批 volume/path-quality filter 重复讲故事。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。**

最终 verdict：`keep_park`

原因：
1. 原 `park` 的主 blocker 没被推翻：improvement 主要来自极端低 retention，而不是稳定、可迁移的 expectancy 改善；
2. 最新证据还进一步说明：`volume spike` 本身不该被当成 15m continuation 发动机，这会削弱 Rank 87 作为独立 gate 的可救性；
3. 现在剩下的更像一条实现纪律：`不要把固定时钟误当真实成交时钟`，不足以诚实长成 `Rank 87b`。

## 6) 本轮结论（按模板）
1. **原 rank 为什么 park？**
   - 因为 clean replication 显示它的改善几乎全靠 retention 从 `86.96%` 压到 `3.42%`，没有形成诚实可迁移的 gate edge。
2. **更像 hard park 还是 soft park？**
   - `soft park`，但现在比当时更偏硬。
3. **有没有可救信号？**
   - 有；主要是“固定 funding/整点时钟不等于真实 market clock”这条很薄的实现残余。
4. **最值得改的唯一一刀是什么？**
   - 把它从 queue-facing gate 降级成 `price-first` 主体里的时钟实现备注，不再单独立项。
5. **是否值得形成新的 derived hypothesis？**
   - 不值得。
6. **为什么不立 `Rank 87b`？**
   - 因为剩下的是方法论提醒，不是带有清晰正 pocket、可直接入板判断的新 hypothesis；硬立只会模糊原 `park` 的审计意义。

## 7) 允许的最终结论
- `keep_park`

## 8) 最小审计结论
- 原 `park` 保留；
- `Rank 87` 本轮仍读作 **soft park，但偏硬，而且比原审计时更偏硬**；
- 它留下的不是值得单独派生 `Rank 87b` 的 queue-facing 残余，而是一条应内化进后续实现纪律的时钟/成交活跃窗口提醒。

## 9) 相关证据锚点
- `research/optimization_loop/2026-03-19_1102_rank87-volume-clock-intake.md`
- `research/optimization_loop/2026-03-19_1126_rank87-clean-replication-park.md`
- `research/quant_digests/2026-03-19_0956_volume-clock-cs-spread-interaction-gate.md`
- `research/quant_digests/2026-03-27_0223_volume-is-not-trend-alpha.md`
- `research/park_reframe/2026-03-25_2209_rank76-park-reframe.md`
- `research/park_reframe/2026-03-23_1941_rank5-park-reframe.md`

## 10) Git
- 未 commit。
- 原因：workspace 当前存在大量与本轮无关的脏文件；本轮只做 park-reframe 所需最小文本更新，不安全混提。
