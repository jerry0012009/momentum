# 2026-04-08 08:20 UTC · Rank 84 park reframe review

## Scope
- source rank: `Rank 84 / volume-price interaction admission layer`
- original authoritative verdict stays: `park / evidence pool`
- this round only asks: **在不推翻原 `park` 的前提下，4 月初新增的 microstructure / absorption 证据，是否足以把 `Rank 84` 再诚实派生出一个新的窄 reframe hypothesis？**

## Read set
- required:
  - `docs/TODO.md`
  - `docs/PARK_REFRAME_QUEUE.md`
  - `docs/RECENT_PAPER_SEEDS.md`
  - `research/quant_digests/INDEX.md`
  - `research/park_reframe/INDEX.md`
- recent park-reframe references:
  - `research/park_reframe/2026-04-08_0344_rank14-park-reframe.md`
  - `research/park_reframe/2026-04-08_0019_rank28-park-reframe.md`
  - `research/park_reframe/2026-04-07_2055_rank33-park-reframe.md`
- needed evidence:
  - `research/optimization_loop/2026-03-19_0902_rank84-volume-price-intake.md`
  - `research/optimization_loop/2026-03-19_0937_rank84-clean-replication-park.md`
  - `research/park_reframe/2026-03-19_1539_rank20-park-reframe.md`
  - `research/quant_digests/2026-04-04_1748_orderbook-pressure-downbar-reversal-alpha.md`
  - `research/quant_digests/2026-04-04_0849_signed-flow-imbalance-maker-conviction-alpha.md`

## Why this rank this round
- 当前轮转优先带仍在 `80~110`；`Rank 84` 上次 bot6 复盘是 `2026-04-01 03:07 UTC`，已超过 7 天。
- 它仍是一个典型“主题未必死，但原角色已经被审计吃掉”的 parked rank，适合低频再确认一次：是否还值得从原 rank 身上再切一刀。
- 4 月初新增的 order-book / signed-flow 证据，正好能回答：这些证据是在救 `Rank 84`，还是只是在继续证明它更适合外流到新的微观结构 raw-alpha 宿主。

## 1) 原 rank 为什么 park？
原 `Rank 84` 被 park，不是因为“量价交互完全没信息”，而是因为它被写成了一个 **shared volume-price interaction admission layer**，但最小 clean replication 只留下很薄、且不够独立的改善：

- `baseline @ 6bps/side`：`mean_total_return≈-1.97%`
- `interaction_admission`：`mean_total_return≈-1.40%`，`retention≈93.55%`
- `interaction_sizing`：`mean_total_return≈-1.35%`，`mean_size≈0.966`

翻成人话：
- interaction 版本确实比 baseline / single-volume 略少亏；
- 但改善幅度很薄，且主要不是靠发现一条新 alpha，而更像“轻微砍掉差单、轻微缩尺码”；
- 它没有证明自己值得作为一个独立 queue-facing rank 继续往前推。

所以原 `park` 必须保留：
**失败的是 Rank 84 这条“shared volume-price interaction admission layer”写法，而不是量价 / 吸收 / microstructure 主题从此彻底失效。**

## 2) 它更像 hard park 还是 soft park？
**soft park，但对原 Rank 84 本体读法已明显更偏 hard。**

- soft 的部分：量价交互、吸收、订单流参与度这些主题仍有信息；
- 更偏 hard 的部分：原 Rank 84 这层 `15m shared admission layer` 职责，已经被 clean replication 审计得差不多了，残余太薄，不像还值得继续从原壳里榨出第二条 queue-facing 假设。

## 3) 有没有“可救信号”？
**有，但不是新的，也不在原 Rank 84 壳里。**

真正还站得住的可救信号，其实早在 3 月 19 日就已经被更诚实地收敛成了 `Rank 20b`：
- 不再把量价关系写成“自己就是一条 rank”；
- 而是把它降级成更泛化的 `volume-price interaction shared admission layer`。

而 4 月初新增的证据（尤其 `5m 下跌 + 买压失衡 → 30~60m 反弹`、以及 `1m signed trade imbalance × 5m forward return` 这一类）继续说明：
- 量价 / 买压 / 吸收 主题没有死；
- 但真正更强的宿主越来越像 **`1m/3m/5m` microstructure raw alpha / execution layer**；
- 它们更像新的事件驱动反转或 directional conviction 宿主，而不是还留在原 Rank 84 这种 `15m shared admission` 语义里。

## 4) 最值得改的唯一一刀是什么？
对 **原 Rank 84** 来说，最值得改、也已经被消费掉的唯一一刀仍然是：

**把“独立的 volume-price interaction rank”降级成更广义的 shared admission / sizing layer。**

但这条唯一修改轴已经被既有 `Rank 20b` 基本吸收；
本轮没有看到第二条既 distinct、又仍属于原 `Rank 84` 宿主的诚实单轴。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论：`keep_park`。**

原因：
1. 原 Rank 84 的唯一诚实 residual 已基本被 `Rank 20b` 消费；
2. 4 月新增证据继续把主题往更快、更事件化、更 raw 的 microstructure / absorption family 外推，而不是留在旧 `Rank 84` 壳里；
3. 如果现在硬 draft `Rank 84b`，大概率只是在重复 `20b`，或者偷换成新的 `1m/3m` microstructure raw-alpha intake，这会稀释原 rank 的审计边界。

## 6) trade on / trade off（本轮为何不再 draft）
若强行再派生，最容易滑向两类不诚实写法：
- 把已经被 `Rank 20b` 吸收的 shared admission 角色，再换壳讲一遍；
- 或把新的 `1m/3m` order-flow / absorption raw alpha 误包进旧 `Rank 84` 名下。

因此本轮更诚实的做法是：
- **trade on**：承认量价 / 吸收主题仍有 residual value，但它更适合去服务新的 microstructure raw-alpha family；
- **trade off**：放弃继续从原 Rank 84 身上硬造 `84b`，接受原 `15m shared admission` 读法已经基本审计完毕。

## Final verdict for this round
- `verdict`: `keep_park`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park, but the original shared-admission reading is now clearly closer to hard park`

## One-line audit note
原 Rank 84 的唯一诚实修改轴早已被既有 `Rank 20b` 吸收；4 月新增的吸收 / signed-flow 证据继续把主题推向更快的 microstructure raw-alpha / execution 宿主，不足以再诚实派生 `Rank 84b`。

## Git
- 本轮不做 commit。
- 原因：git 工作区存在大量与本轮无关的既有脏文件 / 未跟踪文件，不适合安全 selective commit。
