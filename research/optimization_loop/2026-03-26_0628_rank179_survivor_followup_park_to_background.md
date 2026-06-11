# Rank 179 / basis-xs-cheap-vs-rich-alpha — survivor follow-up 收口（park_to_background）

- Time: 2026-03-26 06:28 UTC
- Target: `Rank 179 / basis-xs-cheap-vs-rich-alpha`
- Slot before action: `Surviving candidate slot`
- Verdict: `park_to_background`
- Artifacts:
  - `reports/artifacts/rank179_basis_survivor_followup_20260326/summary.json`
  - `reports/artifacts/rank179_basis_survivor_followup_20260326/portfolio_summary.csv`
  - `reports/artifacts/rank179_basis_survivor_followup_20260326/asset_summary_12bps.csv`

## 本轮只回答的一句话
`Rank 179 / basis-xs-cheap-vs-rich-alpha` 的唯一 survivor follow-up 已诚实收口为 `park_to_background`：当这条 `long cheap basis / short rich basis` 横截面 carry 骨架改用更诚实的 `premiumIndex/price` basis proxy、`next-bar open`、`non-overlap` 与保守组合成本后，8 币样本下所有主规格都转为负净边，当前不足以升入 `P2`。

## 这次 follow-up 怎么做的
只做 survivor 该做的最小 decisive 检查，不扩题：

- universe：`BTC / ETH / BNB / SOL / XRP / ADA / DOGE / LINK`
- 数据：Binance USDⓈ-M 公共 `15m klines` + `15m premiumIndexKlines`
- 更诚实 basis 口径：`basis_bps = premiumIndex_close / price_close * 10000`
- 组合表达：每个 rebalancing 时点做 `long 2 lowest basis / short 2 highest basis`
- 执行：`next-bar open` 入场
- 持有：固定 `16` 或 `32` 根 `15m` bars
- 非重叠：只保留 `ts[::hold]` 的 rebalancing 时点，避免 overlap 把样本抹厚
- 成本：直接按组合 round-trip 扣 `8 / 12 / 16 bps`

## 主结论
### 1) 最初 digest 里看起来最像样的 `16-bar signal + 32-bar hold`，在更诚实口径下翻成负值
- `strict_16x32 @ 12 bps`：
  - `n_port_trades = 280`
  - `mean_net_bps = -12.53`
  - `win_rate = 34.64%`
  - `t_stat = -3.03`
  - `positive_symbol_ratio_12bps = 14.29%`

也就是说，之前 short sample + 粗 proxy 下看起来像正边的那条主规格，一旦把执行与成本写诚实，已经不是“边际变薄”，而是直接**负净边且符号反了**。

### 2) 不是只有一个参数点坏掉，而是本轮主规格全线为负
`portfolio_summary.csv` 里：

- `8 bps` 成本下，`16/16`、`16/32`、`32/16`、`32/32`、`64/16`、`64/32` 全部负值
- `12 bps` 成本下，全部更差，最好一档也只有 `-10.98 bps`
- `16 bps` 成本下，全部进一步走弱

这回答了 survivor 这一步真正该回答的问题：
**不是“还有没有某个参数 pocket 勉强能讲故事”，而是这条 alpha 本体在更诚实 desk 口径下能不能维持正号。当前答案是否定的。**

### 3) 跨资产也不支持它进入 P2
以 `12 bps` 口径看，正 net 基本只剩零星小样本口袋：

- `BNBUSDT` 在部分 `32-bar hold` 规格下略正（约 `+3.85 ~ +6.74 bps`）
- 其余主腿大多为负，尤其 `ADA / DOGE / ETH` 明显拖累
- `positive_symbol_ratio_12bps` 最好也只有 `28.57%`

这说明当前 surviving 的对象——也就是 **横截面 `long cheap / short rich basis` 本体**——并没有给出足够跨资产稳定的证据。剩下的只是个别币种 pocket，不足以把整个骨架送进 `P2`。

## 为什么这次不是 promote_P2
进入 `P2` 至少要有“这条骨架本体还活着”的基础。当前没有：

1. **effectiveness**：保守成本后全线负净边
2. **cross-asset stability**：正 net 币种占比很低
3. **time/parameter stability**：不止一个参数点坏，是主要规格整体翻负
4. **honesty / execution realism**：一旦从粗 `premiumIndex close` 排名改到更诚实 `premiumIndex/price + next-bar open + non-overlap`，原先正值结论失效

所以这一步不该再拖成 `keep_P1`，也不足以升 `P2`。

## 为什么这次也不是 re-scope
policy 只允许在**存在唯一明确 re-scope 方向**时才从更高层往回收。当前 survivor follow-up 看到的并不是一个统一、清晰、可直接改写成新对象的单一方向，而是：

- 少数币种 pocket（主要偏 `BNB`，偶发 `XRP` 小样本）
- 其余主腿与组合总体都不支持原骨架

这更像未来若要继续，应把 `single-asset / subset-specific basis pocket` 作为**新的 intake** 单独立项，而不是把当前 `Rank 179` 强行续命。

## 对 runtime 的直接影响
- `Surviving candidate slot` 清空
- `Rank 179 / basis-xs-cheap-vs-rich-alpha` 移入 `Background pool`
- 当前被否定的是：**`long cheap basis / short rich basis` 这条横截面 basis carry 本体**
- 没有升级到 `P2`，也没有产生新的 `P3 / paper launch` 目标

## 单句结果（供 state / cycle_plan 回写）
`Rank 179 / basis-xs-cheap-vs-rich-alpha` 的唯一 survivor follow-up 已诚实收口为 `park_to_background`：当这条 `long cheap basis / short rich basis` 横截面 carry 骨架改用更诚实的 `premiumIndex/price` basis proxy、next-bar open、non-overlap 与保守组合成本后，8 币样本下所有主规格都转为负净边，当前不足以升入 `P2`。
