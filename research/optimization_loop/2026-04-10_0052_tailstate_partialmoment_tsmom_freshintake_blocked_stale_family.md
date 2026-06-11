# 2026-04-10 00:52 UTC — tail-state partial-moment router × intraday TSMOM fresh intake blocked as stale family replay

## 本轮对象
- 当前小点：`research/quant_digests/2026-04-10_0010_tailstate-partialmoment-tsmom-router-alpha.md`
- 执行动作：检查它是否真是新的 `fresh intake`，还是已存在 `UPM/LPM tail-quadrant managed TSMOM` 家族的低杠杆重写

## 读取与对照
- 当前 pending digest：`research/quant_digests/2026-04-10_0010_tailstate-partialmoment-tsmom-router-alpha.md`
- 既有近亲 digest：`research/quant_digests/2026-04-04_1158_tail-moment-managed-tsmom-alpha.md`
- 核心重复点：两者都来自同一篇 `Liu, Lu, Wang (2021), Asymmetry, tail risk and time series momentum`，都把对象定义为 `TSM sign baseline + UPM/LPM quadrant router / reverse-aware managed trend alpha`。

## 为什么本轮不能把它当 fresh intake
1. **对象同源且策略骨架同一条。**
   - 旧 digest 已经明确写出：`过去 J 根收益符号定义 TSM 方向 + 近 n 根 UPM/LPM 四象限决定 follow / flat / reverse`。
   - 新 digest 只是把同一篇 paper 换成更口语化标题，并把 `四象限 + S1/S2` 缩成 `align-only veto / flip-on-conflict` 的最小 probe 叙述。
2. **新 digest 没有引入会改变 family identity 的新决定性证据。**
   - 它补了 Binance `15m/5m` 快检数值，但这些数值本质上仍是在给同一家 `tail-moment managed TSMOM` 家族补 portability 旁证，不足以把对象改判为一条全新 raw alpha。
3. **按 policy，fresh intake 不能拿既有 family 的低杠杆重复补厚来占前排。**
   - 当前更诚实的处理是把这一步记为 `stale replay blocked`，并把前排 fresh intake 让给下一条真正未首判的对象。

## 本轮结论
- 结论：`2026-04-10_0010_tailstate-partialmoment-tsmom-router-alpha.md` 不是新的 fresh intake；它与 `2026-04-04_1158_tail-moment-managed-tsmom-alpha.md` 属于同一 `managed TSMOM / UPM-LPM tail router` family，只是用 crypto `15m/5m` portability probe 重新包装，不足以形成独立前排对象。
- 因此本轮不分配新 rank，不给 `keep_P1`，直接把当前小点收口为 `blocked`。
- fresh intake 应前移到下一条未首判对象：`research/quant_digests/2026-04-09_2254_btceth-betaneutral-costaware-pairs-shell.md`。

## 会改变系统认知的一句话
`tail-state partial-moment router × intraday TSMOM` 不是新的 fresh intake，而是既有 `UPM/LPM managed TSMOM` 家族的低杠杆 replay；本轮按 stale family blocked 收口，并把 fresh intake 前移到 `spread fade × beta-neutral sizing / funding-aware cost shell`。
