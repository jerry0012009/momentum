# 2026-04-15 16:12 UTC｜Rank 14 park reframe

## 本轮处理对象
- `Rank 14 / cross-asset TSMOM confirmation gate`
- 原始结论保持：`park`
- 本轮结论：`keep_park`

## 为什么这轮仍看 Rank 14
- 按轮转本来应尽量避开最近 7 天已复盘条目；但 `Rank 14` 在 `2026-04-14 23:45 UTC` 之后又出现了**新的同主题外部证据**，因此这轮允许做一次低频复看，而不是机械跳过。
- 本轮只回答：这些新证据是否足以从旧 `Rank 14` 再诚实派生一条新的窄 reframe hypothesis（即 `Rank 14c` 一类）。

## 原 Rank 为什么被 park
回看原始 clean replication（`2026-03-17_0052_rank14-cross-asset-tsmom-park.md`）：
- 原设定是把 `peer-basket same-direction confirmation` 直接接到单币 momentum 上，测试 `baseline_sign_mom / peer_1h_gate / peer_4h_gate / peer_dual_gate / peer_dual_strict`；
- 结果不是“略差但有 pocket”，而是**跨 BTC/ETH/SOL、跨成本、跨时间桶一起偏负**；
- `peer_dual_gate` 连 baseline 都没救回，说明问题不是小调参，而是**把 cross-asset 共振当成 15m 直接 confirmation gate 这层职责放错了**。

## 它更像 hard park 还是 soft park
- 仍判为 **soft park，但比 2026-04-14 那轮更接近 hard**。
- 理由：
  1. 原 Rank 14 本体的 blocker 没被推翻；
  2. 唯一还算诚实的残余，仍只到既有 `Rank 14b`：把“同向确认”降级为 **directional-breadth-coherence long-side veto-only gate**；
  3. `Rank 14b` 自己虽然在 `2026-03-23` 的单臂验证里出现过 `baseline -16.36 bps -> veto +3.80 bps @ 6bps` 的局部改善，但 retention 只有约 `59.6%`，且改善明显偏 `SOL`，更像 **cheap fallback / local veto**，还远不到足以反推旧 Rank 14 本体应重开。

## 本轮新增证据
### 1) 2026-04-15 02:37｜`BTC-beta-neutral residual momentum ranking`
- 新证据把“cross-asset continuation”继续推向 **de-beta 后的横截面 ranking raw alpha**；
- 它真正有信息的地方，是先把 `BTC` 市场因子剥掉，再做 residual momentum 排名，而不是用 peer-basket 同向去给单币 `15m` continuation 直接投确认票；
- 而且该 digest 的 first verdict 也明确提示：**去 beta 能减噪，不等于 `15m` 直译就能赚钱**。

### 2) 2026-04-15 14:36｜`30d top-quintile × 7d weekly rotation`
- 这条新证据继续说明横截面 continuation 主题本身没死；
- 但它活着的形状是 **slow rotation / ranking / beta overlay**，不是旧 Rank 14 那种“同一时点 peer basket 同向就允许单币 momentum”写法；
- recent liquid-major perp first verdict 仍明显偏负，也再次提醒：**主题有信息 ≠ 旧 gate 写法可救**。

## 有没有“可救信号”
有，但**只有一条旧的、且已知很薄的可救信号**：
- 不是再做新的 `Rank 14c`；
- 而是继续承认既有 `Rank 14b` 代表的那条唯一残余：
  - **把 peer same-direction confirmation 改写成 long-side directional breadth coherence 的 veto-only gate**；
  - 也就是只在 `dir_breadth_1h` 很差时否决 continuation long，而不是把跨资产信息当 standalone confirmation。

这条残余为什么没有被本轮升级：
- 它已经被 draft 过；
- 也已经拿到过一次最小验证；
- 新增证据没有把它从“cheap fallback / local veto”推进到更强的 queue-facing 独立候选，反而继续把同主题上移到新的 **ranking / de-beta / price-discovery raw-alpha 宿主**。

## 最值得改的唯一一刀是什么
- 若未来还要保留 Rank 14 家族的唯一修改轴，**仍然只能是既有 Rank 14b 那一刀**：
  - `peer-basket same-direction confirmation`
  - → `directional-breadth-coherence long-side veto-only gate`
- 本轮**没有**比它更诚实的新单轴。

## 是否值得形成新的 derived hypothesis
- **不值得。**
- 结论：当前不诚实派生 `Rank 14c`。
- 原因：
  1. 新证据救活的是新的 raw-alpha 宿主，而不是旧 Rank 14 gate；
  2. 既有 `Rank 14b` 已经完整表达了唯一自然 residual；
  3. 该 residual 的 runtime truth 仍只支持把它当便宜 fallback / local veto，而不是再往前派生一条新 queue-facing hypothesis。

## 本轮结论（供队列写回）
- `verdict = keep_park`
- 建议短注：
  - 原 `park` 保留；
  - 结论=`soft park，但比昨晚那轮更接近 hard；4 月 15 日新增的 residual-momentum / weekly XS momentum 证据继续说明 cross-asset continuation 主题若还有信息，也更像新的 ranking / de-beta raw-alpha 宿主，而不是足以从旧 Rank 14 再诚实派生 Rank 14c；既有 Rank 14b 仍是唯一可留 residual，但只配 cheap fallback。`

## 文件改动
- 新增本日志：`research/park_reframe/2026-04-15_1612_rank14-park-reframe.md`
- 追加更新：
  - `research/park_reframe/INDEX.md`
  - `docs/PARK_REFRAME_QUEUE.md`

## 邮件摘要建议标题
- `Rank 14 维持 park，不派生 14c`
