# Rank 210 / predicted funding sign -> carry on/off / reverse intake keep_P1

- Time: 2026-03-28 03:19 UTC
- Target: `research/quant_digests/2026-03-28_0020_predicted-funding-sign-carry-switch-alpha.md`
- Action type: fresh intake
- Verdict: `keep_P1`
- Assigned Rank: `210`

## 为什么这条线通过 fresh intake
1. **alpha 本体是明确的 carry timing 状态机，不只是 narrative 包装。** repo 主报告和 `managed_basis_strategy/ml_basis_strategy.py` 都把对象写成：`predicted funding > threshold -> 持有/重建 long spot + short perp`，`predicted funding <= threshold -> 退出`。这说明真正要回答的问题是“carry 该不该 timed on/off”，而不是“模型好不好看”。
2. **它确实回答了一个独立的 desk 问题。** always-on carry 的核心痛点就是负 funding 小时要不要继续扛；这条线给出的不是 overlay，而是直接重写 carry 的持仓开关，所以它属于独立 raw alpha，而不是给别的策略贴创可贴。
3. **第一轮 desk 化成本很低。** 小时级 funding sign、5m/15m 执行映射、成本闸门、A/B 基线都能直接写清楚；即使先不做 reverse carry，也能先回答 `predict-negative -> flat` 是否比 always-on 更诚实。

## 为什么只到 keep_P1，不直接升 P2
1. **repo 的 sign 预测成绩离“总是猜正 funding”并没有拉开决定性差距。** 该样本里正 funding 占比 71.21%；如果永远预测正 funding，正类 F1 约为 `0.8318`。仓库给出的最佳 `1h LSTM F1 = 0.8397`，只高了约 `0.008`。这说明当前证据更像“利用了样本正偏置并改善了部分负 funding 识别”，还没强到足以直接当成 desk-ready timing engine。
2. **最诱人的 `reverse carry` 还停留在概念层。** 主报告把 `negative -> reverse` 写成 *possible*，但代码真正落地的是 `predict-negative -> exit` 的 on/off 版本；也就是说，repo 已经证明的是“少扛负 funding”这个方向值得测，不是“反向 carry 已被验证”。
3. **执行 realism 仍偏弱。** 主报告里 funding 分析样本写 `2025-01-01 ~ 2025-05-13`，实验段又写成 `2023-01-01 ~ 2025-05-05`；最佳 APY 同时伴随 `11x~41x+` 的极激进杠杆；`mb_hl_strategy.py` 的 observation builder 也把 Binance 价格直接喂给 `SPOT` 与 `HEDGE.mark_price`，更像 funding-only 研究骨架，而不是已审计的 spot/perp 执行回测。

## 唯一 survivor follow-up 应该问什么
只做一次便宜但 decisive 的 follow-up：
- 资产：先 `ETH`，再用 `BTC` 做 transfer check；
- baseline：
  1. `always-on long spot + short perp`
  2. `current-sign persistence / always-positive` 这种最笨基线
  3. `predict-negative -> flat`
- 执行：整点预测，下一根 `5m` 或 `15m` bar 执行；
- 成本：至少分成 `funding-only / +fees / +spread / +borrow-transfer` 四档；
- 唯一问题：**把评价口径从 F1 换成实际 funding-cashflow 之后，这条 sign-timed carry 还能不能诚实打赢 always-on 与 naive sign baseline？**

## Result sentence
`Rank 210 / predicted funding sign -> carry on/off / reverse` intake passed as `keep_P1`: 它保留了一条真实的 funding-carry timing raw alpha，但当前 repo 证据主要只证明“少吃部分负 funding 小时”值得继续测，还不足以证明可 desk 化的 reverse-carry edge。
