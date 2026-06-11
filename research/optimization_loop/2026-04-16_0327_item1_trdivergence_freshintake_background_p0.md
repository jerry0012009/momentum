# 2026-04-16 03:27 UTC — item1 `TR divergence × vol-price fade` fresh-intake first verdict

## 执行动作
- 对 `research/quant_digests/2026-04-16_0055_trdivergence-volprice-fade-alpha.md` 执行 first-verdict。
- 口径：统一 `t+2` 执行延迟 + 单边 `4/6/8 bps` 成本，且拆分 `Asia/EU/US` 分时段。
- honesty/execution realism 最小核对：用 `gross/turnover` 计算可承受的盈亏平衡单边成本（maker/taker 可复制性下限）。

## 证据与产物
- 输入轨迹：`reports/artifacts/quant_digests/2026-04-16_true_range_divergence_probe_*_15m.csv`
- 新产物：`reports/artifacts/optimization_loop/2026-04-16_trdivergence_t2_cost468_session_eval.json`

核心结果（t+2）：
- 组合等权 `net_bps/bar`：
  - cost4: `-0.0542`
  - cost6: `-0.0783`
  - cost8: `-0.1025`
- 分时段（组合等权）在三档成本下均为负：
  - Asia: `-0.0420 / -0.0663 / -0.0905`
  - EU: `-0.0421 / -0.0626 / -0.0831`
  - US: `-0.0783 / -0.1060 / -0.1338`
- 单资产在 cost4 下也全部为负（BTC/ETH/SOL/BNB 全负）。

honesty/execution realism：
- 盈亏平衡单边成本（`gross/turnover`）
  - BTC: `-1.76 bps`
  - ETH: `-1.81 bps`
  - SOL: `+0.80 bps`
  - BNB: `+0.83 bps`
- 结论：即便走 maker-first，所需单边成本上限也仅约 `<=0.8bps`（且两大核心币 BTC/ETH 为负阈值），与可复制执行现实不匹配。

## 本轮结论（first verdict）
`TR divergence × vol-price fade` 在统一 `t+2 + 4/6/8bps` 与 Asia/EU/US 口径下未形成可复制费后 pocket；并且 maker/taker 诚实核对显示可承受摩擦阈值过低，故本轮 fresh intake 直接收口为 `background/P0`（不进入 survivor，不分配 Rank）。
