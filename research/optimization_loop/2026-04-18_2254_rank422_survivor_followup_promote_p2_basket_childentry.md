# Rank 422 survivor follow-up -> promote_P2

- Time: 2026-04-18 22:54 UTC
- Target: `Rank 422 / 21:00–23:00 UTC fixed-window drift`
- Action: survivor 唯一 follow-up；只做最小 admission 收口检查：把原始 `EW6` 窗口漂移压到去弱币 basket（剔除 `XRP`）与最小 child-entry（`delay-one-bar` / `21:15` 入场）口径，直接回答它是否足够进入 `P2`。

## 本轮最小检查

### 1) 去弱币 basket：`EW5 = BTC/ETH/SOL/BNB/DOGE`
先前 fresh intake 已确认 `XRP` 在 `21:00–23:00 UTC` 上明显偏弱（原始 probe 仅 `+6.42bps/day`、rank `8/96`，而 `BTC/ETH/SOL/BNB/DOGE` 都在各自强簇前列）。

因此这轮直接把 survivor admission 收敛到去弱币 basket：
- `EW5 base (21:00 open -> 23:00 open)`：`mean=+13.54bps/day`，`win_rate=56.99%`，`t=3.14`
- 按 round-trip friction 压缩后：
  - `net4 ≈ +9.54bps/day`
  - `net8 ≈ +5.54bps/day`
  - `net12 ≈ +1.54bps/day`

这说明一旦剔除最弱币，组合并没有塌，反而较原 `EW6` 更干净，after-cost 余量也更适合 admission。

### 2) 最小 child-entry：`delay-one-bar` 并未摧毁 edge
为了避免它只依赖“21:00 正点一把梭”，这轮补了最便宜的 child-entry honesty：
- `delay-one-bar`: `21:15 open -> 23:00 open`
- 样本：同样近 `379` 天、同一 `EW5`

结果：
- `EW5 delay-one-bar`：`mean=+13.55bps/day`，`win_rate=58.31%`，`t=3.53`
- friction 后：
  - `net4 ≈ +9.55bps/day`
  - `net8 ≈ +5.55bps/day`
  - `net12 ≈ +1.55bps/day`

也就是说，把入场延后一根 `15m` 后，净边际没有被破坏，反而统计稳定性略好；因此这条线的价值并不只依赖单一 `21:00` timestamp。

### 3) 额外 sanity check：简化 pullback 入口没有明显更优，但也未推翻主线
再补一个不扩题的最小变体：
- `first red 21:15 else 21:00`
- `EW5 mean=+13.15bps/day`，`win_rate=55.67%`，`t=3.31`

这说明当前最便宜、最稳妥的 child-entry 不是复杂 pullback 规则，而是简单 `delay-one-bar`；但关键结论不变：**主线 edge 在最小 child-entry 下仍然成立。**

## 单币层观察
- `BTC`: `base +9.21bps`；`delay +8.77bps` —— 略降但仍稳
- `ETH`: `base +16.87bps`；`delay +15.51bps` —— 仍明显为正
- `SOL`: `base +12.50bps`；`delay +14.63bps` —— delay 后更强
- `BNB`: `base +12.23bps`；`delay +12.46bps` —— 基本不变
- `DOGE`: `base +16.91bps`；`delay +16.41bps` —— 略降但仍明显为正

没有出现“去掉 XRP 后只剩单一币支撑”或“child-entry 一压就全体转负”的情况。

## verdict
`Rank 422 / 21:00–23:00 UTC fixed-window drift` 的 survivor 唯一 follow-up 已诚实收口：在剔除弱币 `XRP` 后，`BTC/ETH/SOL/BNB/DOGE` 的 `EW5` 仍保留 `~+13.5bps/day` gross，且最小 child-entry（`21:15 delay-one-bar`）并未摧毁 edge、`net8` 仍约 `+5.5bps/day`；因此它已不只是裸 fixed-clock 提示，而是足够具体、可进入 admission 的 `time-of-day raw alpha`，本轮直接 `promote_P2`。
