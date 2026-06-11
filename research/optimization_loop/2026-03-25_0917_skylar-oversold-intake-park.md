# 2026-03-25 09:17 UTC — Skylar oversold-volume reversal fresh intake：先 `park`，不进 P1

## 本轮执行对象
- slot: Fresh intake slot
- candidate: 2026-03-25 quant digest《Skylar oversold volume reversal transfer check》
- source: `research/quant_digests/2026-03-25_0719_skylar-oversold-volume-reversal-transfer-check.md`
- policy动作: 只回答 `park / keep_P1`，不额外扩展排班

## 最小公开证据
- 这条线的 base alpha 很清楚：`1h` 内单币出现明显急跌，且成交量显著高于过去 `24h` 均值时，后续 `4h~24h` 可能出现 oversold bounce。
- 原始来源不是空泛想法，而是给了完整 entry / hold / cost / no-overlap 骨架的 2025 GitHub 新仓库 `skylarshi123/crypto-stat-arb`。
- 这类单资产、事件驱动、反转型 raw alpha 符合当前 fresh intake 的范围：不是旧 background pool reopen，也不是解释层 / 过滤层伪装成 alpha。

## 本地快检（诚实可执行性）
本轮不再停留在仓库自报收益，而是直接看它在当前 desk 关心的 Binance perp 口径下是否还能活：

1. digest 已完成最小 transfer test：`BTC/ETH/SOL/AVAX`，信号在 `1h` 形成、执行落到下一根 `15m`，显式计入 `40 bps round-trip`；
2. 默认阈值 `ret_1h<=-2% & vol_ratio>=1.5` 下，`1h / 4h / 12h / 24h` 四档平均单笔净收益全部为负；
3. 唯一剩下的正值线索只出现在极端 pocket：`shock<=-5% & vol_ratio>=4` 的 `12h` 持有约 `+4.07%`，但样本只有 `5` 笔；
4. 这说明当前能被诚实读出的不是“默认版值得留 front slot”，而是“默认版 transfer fail，只剩极端 capitulation pocket 值得以后单独重开”。

## 收口判断
**结论：先 `park`，不进 `keep_P1`。**

改变系统认知的一句话：
> 这条 `急跌 + 放量后反弹` raw alpha 的问题不是 source 不完整，而是它在当前 Binance perp / 15m desk transfer 里默认版已经先判负，只剩极端 capitulation pocket 的小样本正值线索，因此本轮应直接 `park`，不占用 survivor 资源。

## 对 runtime 的直接影响
- Fresh intake slot: 继续 `vacant`
- Surviving candidate slot: 不生成新 survivor
- Active P2 slot: 保持 `none`
- cycle_plan 第 1 项: `done`
- cycle_plan 第 2~4 项: 因第 1 项未产出 `keep_P1`，本轮应转为 `blocked`

## 为什么这不是整条线永久作废
这不是说“oversold 反弹”永远没价值，而是说：
- 当前最宽的默认定义（`-2% + 1.5x volume`）在 desk transfer 下不成立；
- 若未来要重开，正确方向应是 **极端清算 / 投降式反弹 pocket**，并且要和 `funding / OI flush / 更快执行` 一起测；
- 在那之前，把它留在 background research 比把它误升成 `keep_P1` 更诚实。
