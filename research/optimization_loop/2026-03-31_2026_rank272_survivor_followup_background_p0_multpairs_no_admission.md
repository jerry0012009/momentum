# Rank 272 — survivor follow-up 完成，回 background/P0

- Time: 2026-03-31 20:26 UTC
- Slot acted on: `Surviving candidate`
- Target: `Rank 272 / plateau-first parameter selection + in-trade ADF kill-switch pairs`
- Source intake: `research/optimization_loop/2026-03-31_1936_rank272_pairs_plateau_adf_killswitch_intake_keep_p1.md`
- Artifact: `reports/artifacts/rank272_survivor_followup_multpairs.json`
- Cost sensitivity drill-down: `reports/artifacts/rank272_survivor_followup_selected_costs.json`
- Verdict: `用尽唯一 follow-up 后不升 P2，转 background/P0`

## What changed system belief

`Rank 272` 的 survivor follow-up 已经把“单对 proxy 还活不活”推进到更诚实的多 pair clean-room 口径：在 Binance USDⓈ-M `5m` 公开数据上，对 `ETH-LINK / ETH-SOL / ETH-BNB / SOL-AVAX / ADA-XRP / DOGE-XRP` 六组高流动 perp pairs 做统一 train/test 切分、同一组 `roll / entry / stop` 网格、同一 `10bps` spread-package 成本、以及 `no kill-switch` 对比 `ADF/timeout kill-switch` 后，结果显示 **可迁移的存活 pocket 并不成组成立**。绝大多数 pair 在 `10bps` 下就没有稳定正的 plateau，唯一明显厚的 pocket 主要集中在 `DOGE-XRP`，`SOL-AVAX` 只剩很薄的边，`ETH-LINK`/`ETH-SOL`/`ETH-BNB`/`ADA-XRP` 不足以支持 admission。与此同时，`ADF/half-life timeout` 更像缩短持仓时长的 risk overlay，而不是稳定提升净边的 admission 组件：它常常缩短 duration，却并未形成“降低 tail 且保住 net edge”的可复用正增益。因此，这条线目前最诚实的结论不是升 `P2`，而是承认它仍主要停留在少数局部 pair pocket，尚未证明成组可迁移、也尚未证明 kill-switch 带来决定性的 post-cost 优势。

## Method

- 数据：Binance USDⓈ-M perpetual 公开 `5m` klines，最近 `1500` bars，前半训练 / 后半测试。
- pair 池：`ETH-LINK`、`ETH-SOL`、`ETH-BNB`、`SOL-AVAX`、`ADA-XRP`、`DOGE-XRP`。
- spread：训练段 log-price OLS beta-hedged residual。
- 网格：`roll ∈ {72,96,120,144}`，`entry ∈ {1.5,1.75,2.0,2.25,2.5}`，`stop ∈ {3.0,3.5,4.0,4.5,5.0}`。
- 成本：统一 `10bps` spread-package round-trip proxy；对最优候选另做 `15/20bps` 敏感性检查。
- 退出：
  - baseline：均值回复或 z-stop；
  - overlay：在 baseline 上叠加 `ADF` 复检失败 streak + `2×half-life timeout`。

## Key observations

### 1) “多 pair 成组可迁移”没有成立

六组 pair 中，只有两组在 `10bps` 下还能看到正 pocket：

- `DOGE-XRP`
  - `plateau_share_no_kill = 0.99`
  - `plateau_share_kill = 0.80`
  - `10bps` 下 best no-kill 约 `+85.8 net bps/trade`，`15bps` 约 `+80.8`，`20bps` 约 `+75.8`
- `SOL-AVAX`
  - `plateau_share_no_kill = 0.41`
  - `plateau_share_kill = 0.08`
  - `10bps` 下 best no-kill 约 `+13.0 net bps/trade`，`15bps` 约 `+8.0`，`20bps` 约 `+3.0`

其余四组：

- `ETH-LINK`：plateau 基本塌到只剩零星参数格；best case 很薄，overlay 后更弱；
- `ETH-SOL`：`10bps` 下全网格不成立；
- `ETH-BNB`：接近打平但整体仍负；
- `ADA-XRP`：全网格不成立。

这说明当前证据更像“少数局部 pair 还能活”，而不是“plateau-first pairs skeleton 已经能在一组高流动 perp pairs 上稳定迁移”。

### 2) kill-switch 没证明自己是 admission 增益，更多只是风险覆盖层

`ADF/timeout kill-switch` 的主要作用，是把 median hold 压短；但它没有稳定地产生“更低 tail loss 且更高 post-cost net edge”的统一增益：

- `ETH-LINK`：overlay 后由微正变微负；
- `SOL-AVAX`：大部分配置下 overlay 明显压掉 plateau，只有很窄的一组参数还能小幅为正；
- `DOGE-XRP`：overlay 仍为正，但净边明显低于 no-kill 基线；
- 其他 pair：多数只是更快止损 / 超时退出，没有把 admission 级别证据补齐。

因此更诚实的读法是：`in-trade ADF + timeout` 目前可保留为 **risk overlay 候选**，但不足以作为把该对象升到 `P2` 的 decisive blocker-clearing evidence。

### 3) 15bps 也没把它推成可复用 admission skeleton

对最有希望的三组做 `15/20bps` drill-down 后：

- `DOGE-XRP` 仍很厚，但它更像单一局部 pocket；
- `SOL-AVAX` 到 `15bps` 已接近打平，`20bps` 只剩极薄残边；
- `ETH-LINK` 在更诚实的 overlay 版本下 `15bps` 已转负。

这不满足 survivor follow-up 预设的升级标准：没有证明“一组高流动 perp pairs 在 `10~15bps` 分腿成本后仍保留可复用 plateau pocket”。

## Final verdict

`Rank 272` 的唯一 survivor follow-up 已用尽。当前最诚实结论是：

- `plateau-first` 依然是值得记住的方法论；
- `ADF/half-life timeout` 依然是值得保留的风险覆盖层候选；
- 但作为一个要升 `P2` 的 pairs/stat-arb admission skeleton，它还没有证明自己能在多 pair 上稳定跨过 `10~15bps` 成本壳，也没有证明 kill-switch 带来决定性的 post-cost admission 增益。

因此本轮不升 `P2`，直接把 `Rank 272` 移回 `background/P0`。
