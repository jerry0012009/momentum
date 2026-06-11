# 2026-04-01 01:18 UTC — Rank 275 survivor follow-up：order-book confidence-threshold directional alpha 用尽预算，回 background/P0

- target: `Rank 275 / order-book confidence-threshold directional alpha`
- action: 执行唯一 survivor follow-up；只回答这条 `order-book / taker-flow imbalance × confidence threshold` 在当前已落地 public-data proxy 与显式成本壳下，是否已经形成至少一个不依赖理想化执行的 after-cost pocket
- success_criterion: 若更细 microstructure proxy 与分层成本壳下至少出现一个可审计、after-cost 为正且不是单一理想化假设撑起来的 pocket，则升 `P2`；否则 survivor follow-up 用尽并回 `background/P0`
- verdict: `background/P0`

## 本轮用到的直接证据
1. fresh intake 首判记录：
   - `research/optimization_loop/2026-04-01_0040_rank275_orderbook_confidence_threshold_keep_p1.md`
2. 原始 digest：
   - `research/quant_digests/2026-03-31_2320_orderbook-confidence-threshold-direction-alpha.md`
3. 已落地 artifact：
   - `reports/artifacts/quant_digests/confidence_threshold_orderflow_proxy_20260331/threshold_summary.csv`
   - `reports/artifacts/quant_digests/confidence_threshold_orderflow_proxy_20260331/per_symbol_top20_conf.csv`
   - `reports/artifacts/quant_digests/confidence_threshold_orderflow_proxy_20260331/meta.json`

## 这一步实际收口的问题
不再讨论论文 headline，也不再泛泛说“方向可能对”。本轮只收口一件事：

> 当前这条线有没有形成至少一个 **不靠单一理想化 maker 假设** 才成立的 after-cost pocket？

## 成本壳重述（直接按现有 gross 结果重算）
当前 artifact 已给出各 confidence bucket 的 `avg_gross_bps/trade`。把它们放进三层执行壳：

- `all taker`：round-trip `10 bps`
- `maker+taker`：round-trip `6 bps`
- `conservative maker-maker`：round-trip `4 bps`

按 `avg_net_bps = avg_gross_bps - round_trip_cost_bps` 直接重算：

| confidence bucket | gross bps/trade | all taker 10bps | maker+taker 6bps | conservative maker-maker 4bps |
|---|---:|---:|---:|---:|
| 全样本 | 0.82 | -9.18 | -5.18 | -3.18 |
| top 30% | 1.93 | -8.07 | -4.07 | -2.07 |
| top 20% | 2.78 | -7.22 | -3.22 | -1.22 |
| top 15% | 3.72 | -6.28 | -2.28 | -0.28 |
| top 10% | 5.04 | -4.96 | -0.96 | +1.04 |
| top 5% | 7.00 | -3.00 | +1.00 | +3.00 |

## 这张表说明了什么
### 1) `all taker` 口径下完全不过线
这个结论没有歧义：`10bps` round-trip 下所有 bucket 都是负的。

### 2) 非纯 maker 的现实壳下，也只剩一个极薄 pocket
如果把“不是纯理想化 maker”理解成至少允许一侧 taker、另一侧 maker，那么 `maker+taker 6bps` 下：
- top `10%` 仍是 `-0.96 bps/trade`
- 只有 top `5%` 勉强剩 `+1.00 bps/trade`

这不是一个足够厚、足够诚实的 admission 结果。理由很直接：
- coverage 只剩 `5%`
- 这 `+1 bps/trade` 没包含 fill shortfall、queue miss、adverse selection、滑点波动
- 一点点执行摩擦上浮就会重新转负

换成人话：**它不是“已经找到可迁移 pocket”，而是“刚好在一层偏乐观但不算最乐观的壳上露头”**。

### 3) 真正明显转正的区间仍主要依赖 `maker-maker`
`conservative maker-maker 4bps` 下：
- top `10%` 约 `+1.04 bps/trade`
- top `5%` 约 `+3.00 bps/trade`

但这正是上一轮已经明确不能直接当成 survivor 通行证的地方：**如果正 pocket 主要由 maker-ish 执行壳撑起来，而不是在更宽松一点的现实执行假设下也能站住，它就还不能进 `P2 admission`。**

## 单币侧没有补出能扭转结论的证据
`per_symbol_top20_conf.csv` 在当前已落地的 `10bps round-trip` 口径下，`BTC/ETH/SOL/ADA/XRP/DOGE/BNB/LINK` top `20%` 全部为负；最好的 `LINK` 也仍是约 `-5.72 bps/trade`。

这意味着当前不是“某个币已经清楚活下来，只是 pooled 平均把它冲淡”，而是 **连单币层也还没给出一个足够硬的现实 pocket**。

## 本轮 exit decision
Rank 275 的 survivor 唯一 follow-up 到这里已经足够收口：

1. `confidence threshold` 方向成立，这一点没变；
2. 但当前 runtime 真正落地的证据仍然只是：
   - gross 随 confidence 单调上升；
   - `all taker` 全负；
   - `maker+taker` 只有 top `5%` 勉强 `+1 bps/trade`；
   - 更清楚的正值仍主要靠 `maker-maker 4bps` 壳；
3. 因而现在还不能诚实地说它已经形成了一个“不是单一理想化假设撑起来”的 after-cost pocket。

## 为什么这一步不是 keep_P1 / keep_P2
按照 policy，这个 survivor 只有 1 次 decisive follow-up 预算。现在预算已经用完，而且结论没有产生层级升级。

此时最诚实的处理不是继续拖成长线 microstructure 研究，而是承认：

> **Rank 275 当前只能证明 admission rule 的方向对，但还没证明在现实执行壳下存在足够厚的可迁移 net edge。**

因此本轮正式收口为：**`Rank 275` survivor follow-up 用尽，不升 `P2`，回 `background/P0`。**

## 对 runtime 的直接影响
- `Fresh intake slot`：清空，不再锁定到 `Rank 275`
- `Surviving candidate slot`：清空，follow-up 预算归零
- `Active P2 slot`：保持 `none`
- `Background pool.latest_parked`：更新为 `Rank 275`

## 一句话结果
**Rank 275 证明了“高 confidence admission”这件事方向没错，但直到目前为止，after-cost 正 pocket 仍主要靠 maker-ish 假设撑着；在 survivor 唯一 follow-up 用尽后，它最诚实的去向是回 `background/P0`，而不是硬拖进 `P2`。**
