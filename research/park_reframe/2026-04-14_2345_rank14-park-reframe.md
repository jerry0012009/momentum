# 2026-04-14 23:45 UTC · Rank 14 park reframe review

## Scope
- Source rank: `Rank 14 / cross-asset TSMOM confirmation gate`
- Original authoritative verdict stays: `park / evidence pool`
- This round only asks: 在不推翻原 `park` 的前提下，`Rank 14` 是否还值得再派生一个新的窄 reframe hypothesis

## Why revisit Rank 14 (7-day rule note)
- `Rank 14` 上次在 `2026-04-08 03:44 UTC` 已做过一轮 park-reframe；按默认 7 天规则，本不该优先重看。
- 本轮仍回头看的唯一理由：出现了 **新的 4 月证据**，且都继续落在 cross-asset / lead-lag 主题上：
  - `research/quant_digests/2026-04-10_1729_spotfutures-pricediscovery-perp-followthrough-alpha.md`
  - `research/quant_digests/2026-04-14_1914_crosscrypto-leaderbucket-laggercatchup-alpha.md`
- 这两条新增证据都说明“跨资产 / 跨市场信息扩散”主题仍有信息，但也都更像 **新的 raw-alpha 宿主**，因此值得低频复核：它们是否真的足以从旧 `Rank 14` 再诚实切出 `Rank 14c`。

## Read set
- required:
  - `docs/TODO.md`
  - `docs/PARK_REFRAME_QUEUE.md`
  - `docs/RECENT_PAPER_SEEDS.md`
  - `research/quant_digests/INDEX.md`
  - `research/park_reframe/INDEX.md`
- needed evidence:
  - `research/optimization_loop/2026-03-17_0052_rank14-cross-asset-tsmom-park.md`
  - `research/park_reframe/2026-03-22_1633_rank14-park-reframe.md`
  - `research/optimization_loop/2026-03-30_0425_rank14_residual_not_new_fresh_intake.md`
  - `research/park_reframe/2026-04-08_0344_rank14-park-reframe.md`
  - `research/quant_digests/2026-04-10_1729_spotfutures-pricediscovery-perp-followthrough-alpha.md`
  - `research/quant_digests/2026-04-14_1914_crosscrypto-leaderbucket-laggercatchup-alpha.md`

## 1) 原 rank 为什么 park？
原 `Rank 14` 的主语是：**把 peer-basket 同频共振当作 15m sign-momentum 的 confirmation gate**。

原 clean replication 已把这条写法审计得很清楚：
- `peer_dual_gate` 一类最小实现不但没救活 baseline sign-momentum，反而更差；
- 时间 / 参数 / 跨标的 / 成本稳定性一起 fail；
- 说明问题不只是阈值没调好，而是 **“同频 peer confirm 能救 15m momentum” 这层职责本身没站住**。

因此原 `park` 必须保留：
**失败的是 Rank 14 这条“peer confirm rescue sign-momentum”写法，而不是所有 cross-asset 信息都永远无用。**

## 2) 它更像 hard park 还是 soft park？
**soft park，但对原 Rank 14 本体读法已明显更偏 hard。**

- hard 的部分：原始 `peer-basket same-direction confirmation` 作为 15m shared confirmation gate，已经被 clean replication 吃干净；
- soft 的部分：cross-asset 信息残余仍存在，但更像会外流到别的宿主（leader-lagger ranking、spot-perp price-discovery follow-through、session handoff / catch-up raw alpha），而不是继续留在原 Rank 14 壳里。

## 3) 有没有“可救信号”？
**有，但仍不是新的 Rank 14 级 residual。**

原线唯一真正站得住的可救信号，早已在 2026-03-22 被收敛成既有 `Rank 14b`：
- 把 `peer confirm` 改写成 **directional breadth coherence 的 long-side continuation veto**；
- 随后又在 2026-03-30 被 runtime truth 明确收口为：
  - `cheap fallback only`
  - `not a new front-slot fresh intake`

而本轮新增阅读到的 4 月证据虽然继续说明 cross-asset 主题没死，但它们救活的对象明显不是旧 `Rank 14`：
- `2026-04-10` 的 spot/perp price discovery 更像 **同标的跨市场 directional shell**；
- `2026-04-14` 的 cross-crypto paper probe 更像 **leader-basket shock × lagger catch-up ranking**。

也就是说：
- 有信息量的，不是“peer-basket same-direction confirmation”这条旧写法；
- 而是 **新的 leader/follower / price-discovery raw-alpha 宿主**。

## 4) 最值得改的唯一一刀是什么？
对 **原 Rank 14** 来说，最值得改、且已经被消费掉的唯一一刀仍然是：

**把 peer-basket same-direction confirmation 改写成 directional-breadth-coherence long-side continuation veto。**

这条唯一主修改轴已经被 `Rank 14b` 吸收；
本轮没有看到第二条同样诚实、且与 `14b / 6b / 28b / 新 raw-alpha lead-lag family` 明确区分开的新单轴。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论：`keep_park`。**

原因：
1. 原 Rank 14 的唯一诚实 residual 已被 `Rank 14b` 消费，并于 3 月底被收口为 `cheap fallback only`；
2. 4 月新增证据继续把主题往 **新的 cross-market / cross-sectional raw-alpha 宿主** 外推，而不是留在旧的 15m peer-confirm gate 语义里；
3. 若现在再 draft `Rank 14c`，大概率只是把“cross-asset lead-lag / price-discovery 主题还活着”误写成“原 Rank 14 还能再救一次”，这不诚实。

## 6) trade on / trade off（本轮为何不再 draft）
若强行再派生，最容易滑向两类不诚实写法：
- 把 `leader bucket -> lagger catch-up` 这种 **新的 cross-sectional raw alpha family** 误包进旧 `Rank 14` 壳；
- 或在 `Rank 14b` 之外再顺手叠 `leader set / session slot / price discovery / lagger veto` 多轴大改。

因此本轮更诚实的做法不是新 draft，而是明确：
- **trade on**：承认 cross-asset 主题仍有信息，但它现在更适合服务新的 raw-alpha 宿主；
- **trade off**：放弃继续从原 Rank 14 身上榨出 `14c` 的冲动，接受旧 `peer-confirm` 家族在 queue-facing 意义上已经基本被审计消费。

## Final verdict for this round
- `verdict`: `keep_park`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park, but the original peer-confirm reading is now clearly closer to hard park`

## One-line audit note
原 Rank 14 的唯一诚实窄救法仍只到既有 `Rank 14b` 为止，而 `Rank 14b` 又已在 runtime truth 中被收口为 `cheap fallback only`；4 月新增的 cross-asset 证据继续说明主题仍有信息，但它救活的是新的 leader-laggard / price-discovery raw-alpha 宿主，而不是足以再诚实派生 `Rank 14c`。

## Git
- 本轮不做 commit。
- 原因：工作区存在大量与本轮无关的未跟踪脏文件，不适合安全 selective commit。
