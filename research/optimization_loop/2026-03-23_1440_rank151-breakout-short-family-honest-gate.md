# 2026-03-23 14:40 UTC · Rank 151 / breakout-short family honest gate

- 严格遵循：`docs/TODO.md` 顶部 `TRADING DESK BOARD`、`docs/AUTO_OPTIMIZATION_LOOP.md`、`docs/BOT2_BOT3_OPERATING_CARD.md`
- 本轮路径：`Scout`
- 本轮范围：只做 **1 个主点 + 1 个紧邻子点**

## 0. 顶板判路
- `Paper / 待开启自动运行 = empty`
- 本轮未发现 `stale / error / refresh drift / ledger/open-position anomaly / red-watch`
- 因此继续按顶板 `Next 3 bot3 runs / Run 1 = Rank 151 的单 family honest gate` 执行

## 1. 为什么这轮做这件事
`Rank 151` 前两轮已经完成：
1. fresh intake admitted
2. 本地 frozen A/B/C cut（generic breakout proxy）

现在最短、最 decisive 的下一刀，不是继续改阈值，而是把既有 frozen `q20 / q80` 直接落到 **1 条真实 desk family** 上，看它能不能从“generic 好看”变成“family 上也站得住”的守门证据。

这轮选择的 family：**`breakout-short`**。

## 2. 本轮实际动作
新建并执行：
- `scripts/build_rank151_breakout_short_family_honest_gate.py`

输入：
- `reports/artifacts/quant_digests/ewmac_breakout_alignment_20260323/event_table.csv`
- `reports/artifacts/quant_digests/ewmac_breakout_alignment_20260323/thresholds.json`

冻结阈值：
- `q20 = -1.1560`
- `q80 = 1.6414`

A/B/C：
- `A = baseline`
- `B = hard_positive (align_score > 0)`
- `C = band_pass (q20 < align_score <= q80)`

成本层：
- `6 / 10 / 15 bps per side`

## 3. 主结果（breakout-short family）
来自：`reports/artifacts/scout_rank151_breakout_short_family_honest_gate_15m/pooled_summary.csv`

### 6bps/side（primary）
- `baseline`
  - `trades = 1727`
  - `retention = 100.0%`
  - `mean_net_bps = -3.47`
  - `total_net_bps = -5988.72`
  - `positive_asset_ratio = 1/3`
- `hard_positive`
  - `trades = 1054`
  - `retention = 61.0%`
  - `mean_net_bps = -3.62`
  - `total_net_bps = -3813.55`
  - `positive_asset_ratio = 1/3`
- `band_pass`
  - `trades = 1033`
  - `retention = 59.8%`
  - `mean_net_bps = +5.55`
  - `total_net_bps = +5732.22`
  - `positive_asset_ratio = 3/3`

### 成本敏感性
- `10bps/side`：`band_pass = -2.45 bps`，但仍优于 `baseline = -11.47 bps` 与 `hard_positive = -11.62 bps`
- `15bps/side`：三臂都转负，`band_pass = -12.45 bps`，仍明显好于 `baseline = -21.47 bps`

## 4. 紧邻子点：按资产看是不是单币幻觉
来自：`reports/artifacts/scout_rank151_breakout_short_family_honest_gate_15m/asset_summary.csv`

### 6bps/side by asset
- `BTCUSDT`
  - baseline `-7.25 bps`
  - hard_positive `-9.06 bps`
  - band_pass `+0.29 bps`
- `ETHUSDT`
  - baseline `+3.61 bps`
  - hard_positive `+2.92 bps`
  - band_pass `+15.60 bps`
- `SOLUSDT`
  - baseline `-5.85 bps`
  - hard_positive `-3.85 bps`
  - band_pass `+2.05 bps`

结论：
- 这不是只靠单一币种撑起来的假象；
- `band_pass` 在三条资产上都比 `baseline` 更好，且在 primary cost 下把三资产口径都拉到非负/转正；
- `hard_positive` 则没有给出同等质量的 family uplift。

## 5. 本轮最值钱的结论
1. **Rank 151 已经拿到第一条真正像样的 desk-family honest gate。**
   - 之前它只有 generic proxy 上的 frozen A/B/C；
   - 现在在 `breakout-short` family 上，`band_pass` 明确优于 `baseline / hard_positive`。
2. **这条线当前最诚实的角色，不是“越强越追”，而是“中段分数放行，极端尾部别追”。**
   - `hard_positive` 依旧不行；
   - 真正有效的是 `band_pass`，也就是承认高尾部常常更像 late-chase。
3. **它开始具备从 `keep_P1` 往 `P2` 靠近的资格，但还差一刀。**
   - 当前已有：generic frozen cut + 1 条 family honest gate；
   - 还缺：时间稳定性或第二 family 复核，才能更诚实地讨论是否升 `P2`。

## 6. 简短 scorecard
- `usefulness = 3/3`
- `time_stability = 2/3`
- `cross_asset_stability = 3/3`
- `cost_trade_stability = 2/3`
- `deployability = 2/3`
- `recommended_action = keep_P1 but stronger`
- `why_now = 顶板明确要求 Rank 151 先完成首条 desk-family honest gate；breakout-short 是当前最直接、最可验证的第一条 family。`
- `main_weakness = primary cost 下结论很干净，但 10/15bps 后 edge 明显衰减；且还没有时间稳定性/第二 family 复核。`

## 7. 本轮新增产物
- 日志：`research/optimization_loop/2026-03-23_1440_rank151-breakout-short-family-honest-gate.md`
- artifact：
  - `reports/artifacts/scout_rank151_breakout_short_family_honest_gate_15m/trades.csv`
  - `reports/artifacts/scout_rank151_breakout_short_family_honest_gate_15m/asset_summary.csv`
  - `reports/artifacts/scout_rank151_breakout_short_family_honest_gate_15m/pooled_summary.csv`
  - `reports/artifacts/scout_rank151_breakout_short_family_honest_gate_15m/family_honest_gate_meta.json`
- 页面：
  - `reports/site/factors/scout_rank151_breakout_short_family_honest_gate_15m/report.html`
  - `reports/site/reading/repo_scout/rank151_breakout_short_family_honest_gate.html`

## 8. 一句话结论
`Rank 151` 已不只是 generic proxy 上“看起来有戏”的 reserve；在 **breakout-short family** 上，它第一次给出了可审计、跨 BTC/ETH/SOL 一致方向的 honest gate 证据：**band-pass 明显优于 baseline / hard-positive**。当前最诚实的 desk 口径应更新为：`keep_P1 but stronger / 已完成首条 family gate / 下一刀优先做时间稳定性或第二 family 复核。`
