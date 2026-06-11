# 2026-03-23 14:33 UTC · Rank 150 / breakout-short family honest gate

- 路径判断：`Scout`
- 认领动作：沿着顶板 `Next 3 bot3 runs / Run 1 = Rank 150 的单 family A/B/C honest gate`，补做 **第二 family 复核**
- 本轮只推进：
  1. **主点**：把 `Rank 150 / DFA Hurst persistence gate` 落到 **breakout-short proxy family**，检查 shared persistence gate 能否跨 family 复现；
  2. **紧邻子点**：给出简短 scorecard，并把结果落成 reader-facing 页面。

## 1) 为什么本轮走这条
- `Paper / 待开启自动运行 = empty`，所以不走 `Paper launch`。
- 当前没有 `stale / error / refresh drift / ledger/open-position anomaly / red-watch`，所以不走 `Interrupt`。
- `Rank 150` 上一轮已经在 `EMA / PSAR` family 拿到一次 `keep_P1 but stronger`，但紧接着的时间稳定性检查显示 uplift 主要集中在最近一个月。
- 因此当前最短、最 decisive 的下一刀，不是继续调 Hurst 阈值，而是问：
  - **这层 persistence gate 能不能跨第二个 desk family 复现？**

## 2) 本轮实际动作
新建并执行：
- `scripts/build_rank150_breakout_short_family_honest_gate.py`

产出：
- `reports/artifacts/scout_rank150_breakout_short_family_honest_gate_15m/pooled_summary.csv`
- `reports/artifacts/scout_rank150_breakout_short_family_honest_gate_15m/asset_summary.csv`
- `reports/artifacts/scout_rank150_breakout_short_family_honest_gate_15m/bucket_mix_primary_cost.csv`
- `reports/artifacts/scout_rank150_breakout_short_family_honest_gate_15m/family_honest_gate_meta.json`
- `reports/site/factors/scout_rank150_breakout_short_family_honest_gate_15m/report.html`
- `reports/site/reading/repo_scout/rank150_breakout_short_family_honest_gate.html`

## 3) 固定口径
- 数据：`BTC/ETH/SOL 120d 15m cache`
- Family：`breakout-short proxy`
- Gate：复用 `Rank 150 / DFA window=192`
  - `low < 1.4319`
  - `high > 1.5423`
- A/B/C：
  - `A = baseline`
  - `B = high_only`
  - `C = low_veto_mid_half`
- 执行冻结：`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`
- 成本：主看 `6bps/side`，并补 `10/15bps` 敏感性。

## 4) 主结果（6bps/side）
### pooled
- `baseline`
  - `trades = 489`
  - `retention = 97.2%`
  - `mean_net_ret ≈ +0.0047% / trade`
  - `total_net_return ≈ +2.29%`
  - `positive_asset_ratio = 2/3`
- `high_only`
  - `trades = 161`
  - `retention = 25.0%`
  - `mean_net_ret ≈ -0.2290% / trade`
  - `total_net_return ≈ -36.86%`
  - `positive_asset_ratio = 1/3`
- `low_veto_mid_half`
  - `trades = 306`
  - `retention = 52.8%`
  - `mean_net_ret ≈ -0.1178% / trade`
  - `total_net_return ≈ -36.06%`
  - `positive_asset_ratio = 0/3`

### by asset（6bps/side）
- `BTC`：baseline 已亏，gate 两臂更差，`high_only` 尤其明显恶化。
- `ETH`：baseline 近乎持平略正；`high_only` 也只小幅为正，力度不够抵消其它资产拖累。
- `SOL`：baseline 本来最强，gate 两臂反而把结果打坏。

## 5) 这轮最值钱的结论
1. **Rank 150 的 persistence gate 没有跨第二 family 复现。**
   它在 `EMA / PSAR` family 上有 uplift，但换到这条 `breakout-short proxy` 上，`high_only` 和 `low_veto_mid_half` 都明显差于 baseline。
2. **这会把当前 desk 读法收紧成“family-specific evidence, not shared gate”。**
   更诚实的结论不是“shared persistence layer 已成型”，而是：
   - `Rank 150` 目前只证明了在 `EMA / PSAR` 那条单 family 上有一定信息；
   - 一旦要求它跨 family 复现，证据立刻变弱甚至反向。
3. **因此下一轮若还给 Rank 150 预算，不该继续包装 shared gate 故事。**
   最合理的用法是把它暂时留在 `EMA / PSAR` 的 family-level overlay 语境里，而不是推进成更普适的 `P2` 候选。

## 6) 简短 scorecard
- `usefulness = 3/3`
- `time_stability = 1/3`
- `cross_asset_stability = 1/3`
- `cost_trade_stability = 1/3`
- `deployability = 1/3`
- `recommended_action = keep_P1`
- `why_now = EMA family uplift 已有但时间稳定性偏弱；这时最 decisive 的下一刀就是第二 family 复核。`
- `main_weakness = persistence gate 目前无法跨 family 复现，且在 breakout-short proxy 上对 SOL/BTC 有明显负贡献。`

## 7) 对 desk board 的含义
本轮最重要的不是又多了一页页面，而是给了 `Rank 150` 一个更硬的边界：

> **它当前更像 `EMA / PSAR` family-specific overlay 线索，而不是可共享到 breakout-short 的 desk-wide persistence gate。**

更准确的当前定位：
- `Rank 150 = P1 / keep_P1 / EMA family evidence real / second-family replication failed / not yet P2`
