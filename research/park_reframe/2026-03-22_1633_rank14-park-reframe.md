# 2026-03-22 16:33 UTC · Rank 14 park reframe review (revisit)

## Scope
- Source rank: `Rank 14 / cross-asset TSMOM confirmation gate`
- Original authoritative verdict stays: `park / evidence pool`
- This round only asks: **是否值得在不推翻原 park 的前提下，派生出 1 条新的窄 reframe hypothesis**

## Why revisit Rank 14 (7-day rule note)
- Rank 14 上次已在 `2026-03-20 03:00 UTC` 做过 park-reframe，且当时结论是 `keep_park`（原因：最自然的“cross-asset breadth/regime gate”修改轴已被 `Rank 6b / Rank 28b` 消费）。
- 本轮之所以仍回头看 Rank 14：**出现了新的、与 6b/28b 不同的可救信号** —— `directional breadth coherence`（2026-03-22 新 digest），它更像“continuation 质量 veto（且多空不对称）”，而不是“外部先行 price discovery”或“alt-vs-BTC RS breadth”。

## Read set
- required:
  - `docs/TODO.md`
  - `docs/PARK_REFRAME_QUEUE.md`
  - `docs/RECENT_PAPER_SEEDS.md`
  - `research/quant_digests/INDEX.md`
  - `research/park_reframe/INDEX.md`
- needed evidence:
  - `research/optimization_loop/2026-03-17_0052_rank14-cross-asset-tsmom-park.md`（原 park 证据）
  - `research/quant_digests/2026-03-22_1558_crossmarket-directional-breadth-coherence-gate.md`（新可救信号）
  - prior reframe log: `research/park_reframe/2026-03-20_0300_rank14-park-reframe.md`

---

## 1) 原 rank 为什么 park？
Rank 14 原始写法是 **本币 sign-momentum + peer-basket 同频共振确认** 的 confirmation gate（把 cross-asset 同向当作“救活 standalone sign-momentum”的确认层）。

它被 park 的核心不是“跨资产永远无用”，而是这条最小实现被 clean replication 审计成**硬负且更差**：
- primary variant（`peer_dual_gate`）在 `6bps/side` 下跨资产大幅为负（均值回撤/收益都很差），甚至劣于 baseline 的 `sign(momentum)`；
- `Light Stability Pack` 时间/参数/跨标的/成本稳定性一起 fail。

=> 因此原 `park` 必须保留：**把“同频 peer confirm”当作 15m sign-momentum 的 standalone confirmation rescue，这条路已经被审计消费。**

## 2) 它更像 hard park 还是 soft park？
**soft park（带 hard core）。**
- hard 的部分：原 Rank 14 作为“standalone sign-momentum + 三币同步确认”的交易形状，已经是 hard fail。
- soft 的部分：cross-asset 信息仍可能有残余价值，但更可能以“shared continuation 质量 veto / regime context”的角色存活，而不是原来的同频确认。

## 3) 有没有“可救信号”？
**有，且是本轮 revisit 的唯一理由：**

新 digest（`2026-03-22_1558_crossmarket-directional-breadth-coherence-gate.md`）给出一个更便宜、更诚实的 cross-asset 读法：
- 不再问“另外两币是否和我同向（peer confirm）”；
- 改问：**在信号前 1 小时，主流币的 5m return 在目标方向上的一致性有多高（directional breadth coherence）**。

关键点：它更像 **continuation 质量的 veto**，而不是方向预测。
- 低一致性桶显著更差；
- 且多空不对称：当前证据显示 long 侧更受益（low breadth 下 long 更差）。

## 4) 最值得改的唯一一刀是什么？
**唯一主修改轴：把 Rank 14 从“peer-basket 同频确认 gate”改写成“directional breadth coherence 的 long-side continuation veto”。**

为了保持单轴与审计清晰，本轮建议第一刀只做：
- **只接 long lanes**（优先 `Fib retest_hold long` 与 `EMA/PSAR continuation long`）；
- 当 `dir_breadth_1h <= 0.45` 时：`veto new long entries`；
- short lane 本轮先不接（避免同时引入“多空镜像 + 阈值 + sizing”第二轴）。

## 5) 是否值得形成新的 derived hypothesis？
**值得。结论：`derived_hypothesis_drafted`。**

理由：
- 不推翻原 park：原 Rank 14 的“peer confirm 救 sign-momentum”失败结论完全保留；
- 这条新线索与 `Rank 6b（外部代理 price discovery）/ Rank 28b（alt-vs-BTC RS breadth）` 不同：它是 **方向一致性（coherence）作为 continuation veto**，且天然允许多空不对称；
- 只改 1 轴（角色与定义），实现成本低，可做 strict A/B。

---

## Proposed derived hypothesis (queue-only draft)
- `proposed_rank`: `Rank 14b`
- `source_rank`: `Rank 14`
- `single modification axis`: `replace peer-basket same-direction confirmation with a directional-breadth-coherence long-side continuation veto (dir_breadth_1h low -> veto long)`
- `trade on`:
  - 事件锚：不改现有 base setups，只做 shared gate
  - 变量定义（对每个 long setup 事件 t，方向 d=+1）：取 `BTC/ETH/SOL` 在 `(t-60m, t]` 的 5m returns，计算 `dir_breadth_1h = mean( sign(ret)==d )`
  - gate：当 `dir_breadth_1h <= 0.45` 时 **veto 新 long entry**；否则按 baseline 执行
  - 第一轮只测：`baseline` vs `veto-only gate`（不加 half-size、不卡 short、不卡第二层 regime stack）
- `trade off`:
  - 放弃“peer confirm 自己就是救活 sign-momentum 的 confirmation gate”的旧 Rank 14 读法；
  - 代价是：trade density 会下降，且存在“砍单美化”风险；因此必须 strict A/B 并报告 `trade_retention` 与 `false_follow_ratio`，不允许顺手改 entry/exit/universe。
- `why now`:
  - 2026-03-20 的 reframe 之所以不派生 Rank 14b，是因为当时最自然的 axis 已被 `Rank 6b/28b` 消费；
  - 但 2026-03-22 新增的 `directional breadth coherence` 证据提供了**不同的、且更贴 continuation 质量 veto 的单轴改写**，值得保留成 queue-only draft。
- `suggested_initial_state`: `source intake / clean replication next`

## Final verdict for this round
- `verdict`: `derived_hypothesis_drafted`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park` (with a hard-fail core on the original peer-confirm form)

## Minimal audit note
This round does **not** reopen Rank 14 itself.
It keeps the original `park` intact. The only new move is a narrow role/definition swap: **`Rank 14b = directional breadth coherence (1h) as a long-side continuation veto gate.`**

## Git
- 本轮只做最小必要文档改动；不做 commit（工作区存在大量无关未跟踪文件）。
