# Rank 267 / crypto factor momentum × size/vol rotation intake keep_P1
- 时间：2026-03-31 09:19 UTC
- 执行角色：bot3
- 触发来源：人工续跑（"请继续"）
- 对象：`crypto factor momentum × size/vol rotation`
- 依据：`docs/BOT2_BOT3_POLICY.md`、`docs/BOT2_BOT3_STATE.md`、`research/quant_digests/2026-03-31_0828_crypto-factor-momentum-sizevol-rotation-alpha.md`

## 本轮执行小点
读取 digest 后，主语可以被明确锁定为：
- `cross-sectional factor sleeves (size / low-vol / short-horizon momentum)`；
- 再对这些 sleeves 自身做 `winner-minus-loser rotation / factor momentum`；
- 交易形态是独立的 `market-neutral / relative-value raw alpha`，不是泛多因子综述，也不是把已有单币动量策略换个说法。

## 为什么它可以进入 fresh intake，而不是直接回 background
这条线已经给出了可独立审计的最小策略骨架：
1. **交易对象**：Binance USDⓈ-M perpetual 的主流流动性币池；
2. **横截面排序**：`size proxy / dollar-volume-vol proxy / short-horizon momentum` 三个 sleeves；
3. **组合层**：最近表现更强的 sleeve 加权，弱 sleeve 降权或停权；
4. **执行层**：低频 sleeve refresh（如 `4h`）+ `15m` TWAP 进场；
5. **风险与成本口径**：美元中性 / BTC beta 近中性、单币上限、容量约束、统一 fee/slippage 假设。

换句话说，它不是只有“因子为什么可能有效”的解释层，而是已经能收口成一条可独立跑的 raw alpha 主语。

## 这轮为什么不直接升 P2
虽然主语完整，但当前证据仍主要停留在：
- 学术文献对 crypto 横截面 `size / momentum / volatility` 与 `factor momentum` 的支持；
- digest 给出的 desk-friendly 可执行 spec；
- 尚未看到在 **当前 desk 数据口径 / 当前 perp universe / 当前成本假设** 下的第一轮最小 replication 结果。

也就是说，它现在回答了“像不像一条独立策略”，但还没回答最关键的 admission 问题：
> 在 Binance perp 的现实 universe 与成本下，静态 sleeves 是否真的有净边？factor rotation 又是不是增益，而不是只是 paper story？

在没有这一步之前，直接升 `P2` 会偏快；但把它打回 `background/P0` 又不诚实，因为它已经明显超过“纯概念草图”的阶段。

## 结论
因此本轮给它正式分配 `Rank 267`，并作 fresh intake 首判：

> `Rank 267：fresh intake 首判完成；crypto factor momentum × size/vol rotation 已可明确收口成“横截面 size / low-vol / 短周期 momentum sleeves + sleeve-level winner rotation”的独立 market-neutral raw alpha skeleton，具备清楚的 universe / ranking / hold / execution / cost 骨架，因此进入前排并记 keep_P1；但当前仍缺少基于 Binance perp 现实 universe 与统一成本口径的最小 replication，暂不直升 P2。`

## 对 runtime 的直接影响
- `Fresh intake slot` 更新为 `Rank 267`；
- `Surviving candidate slot` 锁定为 `Rank 267`，并保留 **唯一 1 次** decisive follow-up；
- 后续若继续执行，默认只允许做一个最小会改 verdict 的检查：
  - `3 sleeves (size / low-vol / momentum) × 现实 perp universe × 统一 taker/slippage 假设` 的 first replication；
  - 重点回答：**静态 sleeve 是否已有净边，rotation 是否带来增益，还是只有 momentum sleeve 存活、其余只是解释层。**
- 在这次 follow-up 诚实收口前，不应继续把别的新 intake 拉进前排覆盖它。
