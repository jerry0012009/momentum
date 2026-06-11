# Rank 216 / Hyperliquid funding-aware multi-window TSMOM × edge gate survivor follow-up → keep P1 后转 background

- 时间：2026-03-28 10:17 UTC
- 对象：`Rank 216 / Hyperliquid funding-aware multi-window TSMOM × edge gate`
- 本轮动作：执行唯一一次 survivor follow-up
- 本轮结论：`keep_P1 后转 background`

## 本轮回答的问题
修正 `OI_USD` universe 与 funding-realism 后，这条对象在 `15m` 上是否仍比裸 `TSMOM` 留下独立 post-cost 净边，足以继续升到 `P2`？

## 最小诚实复算
我按 digest 里约定的 honest transfer，直接用 Hyperliquid 公共 API 做了一次轻量四臂复算：
- universe：`dayNtlVlm >= 10M` 且 `OI_USD = openInterest × midPx >= 5M`
- 当前 corrected universe 共 `12` 币：`BTC, ETH, HYPE, SOL, XRP, TAO, ZEC, FARTCOIN, kPEPE, LIT, BCH, WLD`
- bar：最近约 `30` 天、`15m` 频率，共 `2881` 根公共 K 线
- 信号：`[24, 96, 288]` bars 多窗口收益 z-score 平均，裁到 `[-2, 2]`
- 四臂：`裸 TSMOM` / `+ funding penalty` / `+ edge gate` / `全部叠加`
- 收益口径：下根 bar 收益 + 实际 funding 收付近似（按已发布 funding rate 折算到 15m） - 换手成本
- 成本口径：沿 repo trade-gate 近似，平均手续费 + 固定滑点合计约 `4.455 bps / side`

## 四臂结果（最近约 30 天，12 币 corrected universe，15m）
- `裸 TSMOM`：`total_return = -11.53%`，`ann_sharpe = -3.84`，`avg_turnover = 0.170`
- `+ funding penalty`：`total_return = -11.53%`，`ann_sharpe = -3.84`，`avg_turnover = 0.170`
- `+ edge gate`：`total_return = -11.51%`，`ann_sharpe = -3.57`，`avg_turnover = 0.199`
- `全部叠加`：`total_return = -11.51%`，`ann_sharpe = -3.57`，`avg_turnover = 0.199`

## 关键读法
1. **修正 universe 后，这条对象没有留下可独立升级的 post-cost 净边。**
   - 四臂全都还是明显负收益；没有出现“修完口径后就能升 P2”的层级变化。
2. **funding penalty 在当前 15m transfer 上几乎不改变系统认知。**
   - 样本内 `avg_abs_signal ≈ 0.7418`
   - 方向性 funding penalty 的 `1h` 平均幅度只有 `0.000012`，中位数 `0.000003`，最大值也只有 `0.000221`
   - 这解释了为什么 `裸 TSMOM` 与 `+ funding penalty` 的结果几乎完全重合：当前这层更多像 carry hygiene，而不是能单独抬升 alpha 的核心判别器。
3. **edge gate 也没有把它从“亏钱趋势壳”救成 admission-ready 对象。**
   - raw arm 下约 `79.9%` 的 coin-bar 仍能通过 gate；说明它没有形成强力筛选，更多只是轻度裁剪。
   - 加 gate 后表现只从 `-11.53%` 微调到 `-11.51%`，远不够支撑升 `P2`。
4. **因此这次 follow-up 的诚实结论不是 promote，而是收口。**
   - 这条 repo 仍保留一个值得记住的设计母版：`TSMOM × funding-awareness × edge gate × execution shell`。
   - 但在修正 `OI_USD` universe 并把 funding 收付按更接近真实的口径落进收益后，它并没有留下独立、可 admission 的 15m post-cost edge。

## 为什么不是 promote_P2
- survivor follow-up 已经直接回答了最关键问题：修正 `OI_USD` universe 与 funding-realism 后，四臂都没有留下足以升到 `P2` 的净边。
- `funding penalty` 对结果几乎零增量，`edge gate` 也只做很弱的裁剪，没有产生层级变化。
- 在这种结果下继续把它留在前排，只会把“完整工程壳”误当成“已过 admission 的 raw alpha”。

## 为什么不是 drop_to_background（P0）
- 它不是被证明为伪命题；更准确地说，是**当前 honest transfer 没证明它有足够强的独立 edge**。
- 作为后续 desk 设计模板，`TSMOM + carry hygiene + execution gate` 这套拆法仍值得保留记忆，但不值得继续占用前排 survivor / P2 资源。

## 本轮正式 verdict
`Rank 216 / Hyperliquid funding-aware multi-window TSMOM × edge gate` 的唯一 survivor follow-up 已诚实收口：修正 `OI_USD` universe 并把 funding 收付按更接近真实的口径落进 `15m` 四臂复算后，`裸 TSMOM / + funding penalty / + edge gate / 全部叠加` 最近约 30 天在当前 `12` 币 corrected universe 上都没有留下可独立升级的 post-cost 净边，其中 funding penalty 几乎不改变结果、edge gate 也只做弱筛选，因此这条对象本轮按 `keep_P1 后转 background` 退出前排，保留为设计母版而不是继续升 `P2`。
