# 2026-03-27 14:42 UTC — Rank 56 park reframe review

- Rank: `56`
- Theme: `liquidation-map path overlay`
- Original status: `park`（authoritative verdict 保留）
- This round verdict: `keep_park`

## 为什么这轮看它
- 按当前 `PARK_REFRAME_QUEUE` 轮转规则，优先处理 `Rank 50+`。
- 最近 7 天内已复盘 `Rank 50/51/52/53/54/55/57/58/59`，但**未复盘 Rank 56**，符合“低频补位、不重复打同一条”的要求。

## 原 rank 为什么 park
参考：
- `research/optimization_loop/2026-03-18_1315_rank56-source-intake-guard-passed.md`
- `research/optimization_loop/2026-03-18_1342_rank56-clean-replication-p1.md`
- `research/quant_digests/2026-03-18_1255_liquidation-map-path-overlay.md`
- artifact：`reports/artifacts/scout_rank56_liquidation_map_path_overlay_15m/overall_summary.csv`

原始故事是：把 liquidation map 降级成 `cluster_path_score`，给 `breakout_short / fib_retest_long / ema_psar_long` 做 shared path overlay，而不是把它当独立方向神图。

但最小 clean replication 的结果很清楚：
- `breakout_short`：三臂都明显负，`base≈-2.49% / gate≈-2.02% / size≈-2.85%`
- `fib_retest_long`：基本零附近或转负，`base≈+0.03% / gate≈-0.22% / size≈-0.04%`
- `ema_psar_long`：只有很薄的 residual，`base≈+1.63% / gate≈+0.74% / size≈+1.69%`
- `binary_path_gate` 的改善主要来自**大幅砍样本**（如 EMA 只剩约 `41.7%` retention），而不是稳定提升 total return
- `size_tilt` 只在 EMA long 勉强不差，但对 breakout_short / fib 没有形成可迁移增量

所以原审计把它压回 `P1 weak candidate / evidence pool` 是合理的：
**它证明了 liquidation path 这件事“也许有信息”，但没有证明“作为 15m shared overlay 的这版写法值得继续排队”。**

## 它更像 hard park 还是 soft park
我会把 Rank 56 定义为：**soft park，但偏硬**。

原因：
1. 不是 hard park，因为 liquidation / crowding / forced-flow 主题本身没有死；
2. 但又偏硬，因为 **Rank 56 自己这版角色定义**（对三条 setup 做对称 shared path overlay）已经被 clean replication 审得比较充分，残余很薄；
3. 若继续从原框架内部微调阈值、窗口、density 算法，大概率只是继续在“砍样本美化”里打转。

## 有没有可救信号
有，但这个可救信号**不属于原 Rank 56 这版写法的诚实延长线**。

还能看到的唯一残余是：
- liquidation 信息更像在**事件驱动 / crowding 共振 / forced-flow**场景里有用，
- 而不是在常规 `15m` continuation / retest setup 上做一个对称、全天候、三路共用的 path overlay。

换成人话：
**它更像“极端时候会不会继续被挤”的事件因子，不像“平时每一单都该多看一眼的路况分”。**

这和后续新证据是一致的：
- `2026-03-24_0631_liquidation-consensus-cascade-continuation-alpha.md` 已把 liquidation 主题往 `funding + OI + cluster proximity` 的 event-driven raw alpha 方向收拢；
- 这条线后来也已经以更上位、也更诚实的形式进入新的 raw-alpha family（而不是停留在 Rank 56 这种 shared overlay 角色里）。

## 最值得改的唯一一刀是什么
如果只谈“主题真正还剩什么信息量”，唯一值得保留的一刀其实是：

**把 `symmetric shared path overlay` 改成 `event-driven liquidation consensus / cascade continuation`。**

但这刀有两个问题：
1. 它已经不是对 Rank 56 的窄 reframe，而是**角色层级变化 + 信号栈扩展**（要引入 funding、OI、cluster proximity 共识）；
2. 这条主修改轴已经被后续更诚实的新 family / 新 rank 吸收，不适合再伪装成一个 `Rank 56b`。

所以，本轮虽然能指出“最值得改的一刀”，但结论恰恰是：
**这不是一个该从 Rank 56 再派生的新 queue-facing hypothesis。**

## 是否值得形成新的 derived hypothesis
**不值得。**

原因：
- 会推着我们把原本的 `liquidation-map path overlay` 偷换成另一条更大、更事件驱动、也更接近 raw alpha 的新东西；
- 那会模糊原 `park` verdict 的审计意义；
- 而且 desk 里已经存在更诚实的 liquidation raw-alpha 入口，不需要再造一个 `Rank 56b` 去重复表达同一主题。

## 本轮结论
- 结论类型：`keep_park`
- 原 rank 为什么 park：因为 clean replication 显示这版 `cluster_path_score` shared overlay 在三条 setup 上缺乏一致 post-cost 增量，改善主要来自砍样本，不足以继续排队
- 更像 hard 还是 soft：`soft park，但偏硬`
- 可救信号：liquidation 主题在**事件驱动 forced-flow**里可能还有信息，但这已偏离 Rank 56 的原角色
- 最值得改的唯一一刀：`从 symmetric path overlay 改成 event-driven liquidation consensus / cascade continuation`
- 是否值得形成新的 derived hypothesis：`否`；这条轴已属于更上位的新 family，不诚实再写成 `Rank 56b`

## 对 queue 的最小写回建议
只做最小更新：
- `docs/PARK_REFRAME_QUEUE.md`：追加一条 recently reviewed
- `research/park_reframe/INDEX.md`：追加本轮索引
- 不改 `docs/TODO.md`

## Git / 工作区备注
- 当前工作区存在大量与本轮无关的既有脏文件；本轮不做混合提交。
