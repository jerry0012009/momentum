# 2026-04-19 09:55 UTC｜Rank 14 park reframe

## 本轮处理对象
- `Rank 14 / cross-asset TSMOM confirmation gate`
- 原始结论保持：`park`
- 本轮结论：`keep_park`

## 为什么这轮仍看 Rank 14
- 按轮转本应尽量避开最近 `7` 天已复盘条目；但 `Rank 14` 上一轮复盘后，又出现了 **2026-04-19 的同主题新证据**：`research/quant_digests/2026-04-19_0224_crossmarket-intraday-tsmom-breadth-basket-alpha.md`。
- 这条新证据与旧 Rank 14 的主题高度相关：都在问“own intraday continuation 是否会被 broad cross-market agreement 强化”。
- 本轮只回答一个问题：这条新证据，是否足以从旧 `Rank 14` 再诚实派生新的窄 reframe hypothesis（如 `Rank 14c`）。

## 原 Rank 为什么被 park
回看原始 clean replication（`research/optimization_loop/2026-03-17_0052_rank14-cross-asset-tsmom-park.md`）：
- 原设定是把 `peer-basket same-direction confirmation` 直接接到单币 sign-momentum 上，测试 `peer_1h_gate / peer_4h_gate / peer_dual_gate / peer_dual_strict` 等最小门；
- 结果不是“略差但仍有 pocket”，而是 **跨 BTC/ETH/SOL、跨成本、跨时间桶一起偏负**；
- 主变体 `peer_dual_gate` 连 baseline `sign(momentum)` 都没救回，说明 blocker 不是参数没拧好，而是 **把 peer-basket 同向当成 15m 单币 continuation 的直接 confirmation gate，这个职责本身就站不住**。

## 它更像 hard park 还是 soft park
- 本轮仍判：**soft park，但比 2026-04-15 那轮更接近 hard park with consumed residual**。
- 理由：
  1. 原 Rank 14 本体的 blocker 没被推翻；
  2. 唯一还算诚实的残余，仍只到既有 `Rank 14b`：把“同向确认”降级为 **directional-breadth-coherence long-side veto-only gate**；
  3. 新证据没有把这条残余重新抬升成独立 queue-facing 假设，反而继续说明：cross-market 信息若有价值，更像新的 **breadth basket / ranking / raw-alpha 宿主**，不是旧 gate 的再包装。

## 现有证据里有没有“可救信号”
有，但仍只有旧的那一条：
- **可救信号不是新的 `Rank 14c`，而是既有 `Rank 14b` 所代表的 residual**；
- 也就是把 peer same-direction 从“放行确认”改写成 **long-side breadth coherence 很差时才 veto** 的 cheap fallback / local veto。

本轮新证据（`2026-04-19_0224`）虽然显示：
- `15m` 的 **long-only breadth-confirmed continuation basket** 有 pocket；
- cross-market agreement 作为 raw alpha 母题仍有信息；

但它救活的形状是：
- **broad-breadth long-side basket**；
- **等权一篮子 continuation raw alpha**；
- 更接近新的完整宿主，而不是“给单币 sign-momentum 再叠一道 peer 同向 gate”。

## 最值得改的唯一一刀是什么
- 若未来还保留 Rank 14 家族的唯一修改轴，**仍只能是既有 Rank 14b 那一刀**：
  - `peer-basket same-direction confirmation`
  - → `directional-breadth-coherence long-side veto-only gate`
- 本轮**没有**比这更诚实的新单轴。

## 是否值得形成新的 derived hypothesis
- **不值得。**
- 本轮结论：`keep_park`，不诚实派生 `Rank 14c`。

### 为什么不值得
1. 2026-04-19 的新 digest 证明的是 **breadth-confirmed long basket** 更像独立 raw alpha；
2. 它没有修复旧 Rank 14 的核心失败点：`peer gate` 对单币 continuation 没有独立正增量；
3. 既有 `Rank 14b` 已经完整表达旧 Rank 14 唯一自然 residual；
4. 若现在硬写 `Rank 14c`，本质会变成把“新的 breadth basket raw alpha”误写成“旧 Rank 14 的窄 reframe”，不符合审计边界。

## trade on / trade off（仅作为 keep_park 审计说明）
- **trade on：** 保留一个很弱但仍诚实的 residual note——cross-asset breadth coherence 可能作为 long-side veto-only 质量层存在；
- **trade off：** 放弃把 broad breadth confirmation 继续写成旧 Rank 14 的 queue-facing 新派生，因为这样会混淆“旧 gate residual”和“新 raw-alpha 宿主”两件事。

## 本轮结论（供队列写回）
- `verdict = keep_park`
- 建议短注：
  - 原 `park` 保留；
  - 结论=`soft park，但比 4 月 15 日那轮更接近 hard with consumed residual；2026-04-19 新增的 cross-market intraday TSMOM breadth-basket 证据继续说明 cross-asset continuation 主题若还有信息，更像新的 broad-breadth long-only basket / ranking raw-alpha 宿主，而不是足以从旧 Rank 14 再诚实派生 Rank 14c；既有 Rank 14b 仍是唯一可留 residual，但只配 cheap fallback。`

## Git / 提交
- 未提交。
- 原因：`git status` 显示工作区存在大量与本轮无关的共享脏文件，不适合安全做 selective commit。

## 邮件短标题
- `Rank 14 继续 park，breadth basket 不等于 14c`
