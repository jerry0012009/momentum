# Rank 422 / 21:00–23:00 UTC fixed-window drift fresh intake keep_P1

- Time: 2026-04-18 22:05 UTC
- Target: `research/quant_digests/2026-04-18_0940_us-session-twowindow-drift-alpha.md`
- Action: fresh intake 最小首判；只补 1 个最小 honesty / execution realism blocker：把 majors basket 的 `21:00–23:00 UTC` fixed-window drift 压到 `4/8/12bps` friction ladder，并核对相邻窗口鲁棒性，回答它是否仍是可独立承接的 raw alpha，而不是只剩泛 session 提示。

## 本轮最小检查
使用 digest 已落好的公开 artifact：
- `reports/artifacts/quant_digests/2026-04-18_tod_21_23_utc_probe_summary.csv`
- `reports/artifacts/quant_digests/2026-04-18_tod_2h_window_scan.csv`
- `reports/artifacts/quant_digests/2026-04-18_tod_21_23_utc_probe.json`

### 1) friction ladder
`EW6` 组合在 `21:00–23:00 UTC` 的 gross mean 为 `+12.8971bps/day`。
按最小 round-trip friction 直接压缩后：
- `net4 ≈ +8.90bps/day`
- `net8 ≈ +4.90bps/day`
- `net12 ≈ +0.90bps/day`

这说明它不是“gross 看着显著、成本一压就完全消失”的那类极薄 pocket；至少在公开 majors basket 口径下，直到 `12bps` 仍未被完全吃光。

### 2) 相邻窗口鲁棒性
这条线不是单一 timestamp 巧合，而是美股晚段附近的正 drift 窗簇：
- `BTC`：`20:15–22:15 = +10.26bps(rank1)`，`21:00–23:00 = +10.10bps(rank2)`，`20:30–22:30 = +9.08bps(rank3)`
- `ETH`：`21:00–23:00 = +17.43bps(rank1)`，`20:15–22:15 = +15.69bps(rank2)`，`20:30–22:30 = +15.15bps(rank3)`
- `SOL`：`21:00–23:00 = +13.39bps(rank2)`，`21:15–23:15 = +13.21bps(rank3)`，`21:30–23:30 = +12.72bps(rank4)`
- `BNB`：`21:30–23:30 = +14.41bps(rank1)`，`21:00–23:00 = +12.51bps(rank2)`，`21:15–23:15 = +10.67bps(rank3)`
- `DOGE`：`21:00–23:00 = +17.55bps(rank1)`，`20:45–22:45 = +15.21bps(rank2)`，`20:15–22:15 = +13.25bps(rank3)`
- `XRP` 明显偏弱：`21:00–23:00 = +6.42bps(rank8)`，不应默认纳入首批 basket。

## verdict
`21:00–23:00 UTC fixed-window drift` 在公开 `15m` majors basket 上，经过最小 `4/8/12bps` 成本梯度后仍保留正向净边际，而且相邻窗口呈现连续强簇，不是只靠单一 timestamp 巧合支撑；因此本轮 fresh intake 诚实收口为 `keep_P1`，分配正式 `Rank 422`，保留为一个可独立承接的 `time-of-day raw alpha`，后续唯一 survivor follow-up 应优先聚焦 `basket admission / 去掉弱币(XRP) / child entry`，而不是重做同一维度的 gross 证明。
