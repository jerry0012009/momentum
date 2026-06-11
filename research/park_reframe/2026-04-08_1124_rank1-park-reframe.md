# 2026-04-08 11:24 UTC · Rank 1 park reframe review

## Scope
- source rank: `Rank 1 / τ-band / no-trade breakout filter`
- original authoritative verdict stays: `park / evidence pool`
- this round only asks: **在不推翻原 `park` 的前提下，最近的新 breakout 证据，是否足以让 `Rank 1` 再诚实派生出一个新的窄 reframe hypothesis？**

## Read set
- required:
  - `docs/TODO.md`
  - `docs/PARK_REFRAME_QUEUE.md`
  - `docs/RECENT_PAPER_SEEDS.md`
  - `research/quant_digests/INDEX.md`
  - `research/park_reframe/INDEX.md`
- recent park-reframe references:
  - `research/park_reframe/2026-04-08_0820_rank84-park-reframe.md`
  - `research/park_reframe/2026-04-08_0344_rank14-park-reframe.md`
  - `research/park_reframe/2026-04-08_0019_rank28-park-reframe.md`
- needed evidence:
  - `research/optimization_loop/2026-03-16_0912_scout-rank1-honest-recheck.md`
  - `research/park_reframe/2026-03-23_2151_rank1-park-reframe.md`
  - `research/optimization_loop/2026-03-30_0529_rank1_outside_persistence_intake_blocked_absorbed_by_rank94.md`
  - `research/quant_digests/2026-04-05_2127_freshhigh-recency-state-machine-alpha.md`

## Why this rank this round
- 本轮在最近已覆盖 `80~110` 后，回到 `1~24` 号段。
- `Rank 1` 最近一次 bot6 复盘是 `2026-03-23 21:51 UTC`，已超过 7 天。
- 它仍是一个典型案例：原 rank 本体已 park，但 residual 曾被写成 `Rank 1b`，随后又被运行态里的 `Rank 94` 同题吸收，适合低频确认一次：现在还有没有必要再从 `Rank 1` 身上切出新的单轴。

## 1) 原 rank 为什么 park？
原 `Rank 1` 被 park，不是因为 breakout 后确认完全没价值，而是因为 **把静态 `τ-band` 写成 breakout 的 standalone rescue** 没有站住：

- honest recheck 后，`confirm2of3_tau_010` 虽比 `raw_breakout` 少亏；
- 但在 `BTC / ETH / SOL | 120d | 15m | post-cost` 口径下，绝对收益仍为负；
- 它最多证明“第一根 break 直接追不够诚实”，没证明“静态 τ-band 本身就是可继续前推的 alpha”。

翻成人话：
**原 Rank 1 的 blocker 不是 breakout 主题彻底没信息，而是 `static tau-band breakout confirmation` 这层写法太薄、太像 execution guard，撑不起独立 rank。**

## 2) 它更像 hard park 还是 soft park？
**soft park，但对原 Rank 1 本体读法已明显更偏 hard。**

- soft 的部分：breakout 后需要额外确认 / persistence 这件事本身没死；
- 更偏 hard 的部分：`static τ-band` 作为独立 rescue 线已经被审计得差不多了，不像还值得再磨第二遍。

## 3) 有没有“可救信号”？
**有，但不是新的，而且已基本被消费。**

唯一真正站得住的可救信号，早就被收敛成既有 `Rank 1b`：
- `replace static tau-band breakout confirmation with a two-stage outside-persistence continuation gate`

但随后运行态又明确写过：
- `Rank 1` 这条 residual 已被 `Rank 94 / two-bar outside-range follow-through gate` 吸收；
- 而 `Rank 94` 自己也已经 clean replication 后回 `park / evidence_pool`。

这说明：
- `outside-persistence` 作为唯一诚实 residual 是存在的；
- 但它已经被“写出来、跑过、再压回 park”完整消费过一轮。

## 4) 最近有没有新增证据，足以支持新的唯一修改轴？
**没有。相反，新证据更像在把 breakout 主题往新的 raw-alpha 宿主外推。**

本轮新读到的 `fresh-high recency state machine` 证据，给出的重点不是“再给 breakout 加一个小确认滤镜”，而是：
- fresh-high 的“新鲜度 / 年龄”本身可以成为完整的状态机 alpha；
- stale-high 还能进一步翻成 short / flat 的衰减壳；
- 这更像一个新的、完整的 trend / breakout raw-alpha family。

因此它对 `Rank 1` 的意义更像：
- 再次证明“breakout 主题还活着”；
- 但活法更像新的 `fresh-high / recency-state` 宿主，
- **而不是再从原 `τ-band` rank 身上诚实切出 `Rank 1c`。**

## 5) 最值得改的唯一一刀是什么？
对 **原 Rank 1** 来说，最值得改、也已经被消费掉的唯一一刀仍然是：

**把 static τ-band 改写成 two-stage outside-persistence continuation gate。**

但这条轴已经经历了：
1. park-reframe draft（`Rank 1b`）
2. runtime duplicate absorption（`Rank 94`）
3. clean replication 后重新压回 `park`

所以本轮没有出现第二条同样诚实、且仍属于原 `Rank 1` 宿主的新单轴。

## 6) 是否值得形成新的 derived hypothesis？
**不值得。结论：`keep_park`。**

原因：
1. 原 Rank 1 的唯一诚实 residual 已被 `Rank 1b -> Rank 94` 这条链完整消费；
2. 最近的新 breakout 证据更像新的 full-shell / state-machine raw-alpha family，而不是旧 `τ-band` rank 的再救援；
3. 若现在再 draft `Rank 1c`，大概率只是在重复 `1b / 94`，或者偷换到新的 fresh-high 宿主上，不诚实。

## 7) trade on / trade off（本轮为何不再 draft）
因此本轮更诚实的做法是：
- **trade on**：承认 breakout 后 persistence / outside-confirmation 仍有 residual value，但这部分已经被既有 residual 与 runtime duplicate 吸收；
- **trade off**：放弃继续从原 Rank 1 身上硬造 `1c`，接受新的 breakout 证据更适合去服务新的 raw-alpha family，而不是回头翻案旧 rank。

## Final verdict for this round
- `verdict`: `keep_park`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park, but the original static tau-band reading is now clearly closer to hard park`

## One-line audit note
原 Rank 1 的唯一诚实残余早已被既有 `Rank 1b` 与运行态里的 `Rank 94` 同题吸收并再次压回 `park`；最近 breakout 新证据继续把主题推向新的 `fresh-high / recency-state` raw-alpha 宿主，不足以再诚实派生 `Rank 1c`。

## Git
- 本轮不做 commit。
- 原因：git 工作区存在大量与本轮无关的既有脏文件 / 未跟踪文件，不适合安全 selective commit。
