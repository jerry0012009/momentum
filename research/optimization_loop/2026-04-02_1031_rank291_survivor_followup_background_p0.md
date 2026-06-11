# Rank 291 / ΔKVSI × Korea-led continuation / offshore fade — survivor follow-up verdict (`background/P0`)

- Time: 2026-04-02 10:31 UTC
- Executor: bot3 auto loop
- Source intake: `research/quant_digests/2026-04-02_0522_kvsi-korean-venue-share-regime-gate.md`
- Prior state: `P1 surviving candidate`
- Follow-up verdict: `survivor budget exhausted -> background/P0`

## This round's one question
这轮不再重复讲“韩盘份额可能重要”的故事，只做一个最小 A/B：
**把 `ΔKVSI` 真挂到一条明确 base alpha 上，看它到底更像 `trend continuation gate`、`offshore fade veto`，还是只是韩盘叙事包装。**

我用现成 artifact：
- `reports/artifacts/quant_digests/2026-04-02_kvsi_proxy_probe/kvsi_proxy_panel_5m.csv`
- 样本仍是同一段 public-data probe：`2026-03-29 18:00 UTC ~ 2026-04-02 05:15 UTC`
- 对象：`Binance BTCUSDT perp`

## Minimal A/B wiring used this round
我没有新造复杂策略，只冻结一个最便宜的 base alpha：

1. **base alpha = BTC 15m continuation / fade A/B**
   - `trail15` = 过去 3 根 `5m` 已实现收益之和（即上一段 `15m` 方向）
   - `fwd15` = 未来 3 根 `5m` 收益（artifact 里的 `fut_ret_3`）
2. **continuation arm**
   - 若 `trail15 > 0`，做多未来 `15m`
   - 若 `trail15 < 0`，做空未来 `15m`
3. **fade arm**
   - continuation 的反向镜像
4. **gate 口径**
   - 主看 `ΔKVSI z-score`（不是 level）
   - `gate_on_q80 = d_kvsi_z >= 80% 分位`
   - `gate_off_q20 = d_kvsi_z <= 20% 分位`

这是刻意收得很窄的 desk-side cheap test：
它只回答 **“当韩盘份额变化很强时，最便宜的 BTC 15m 顺势/逆势 A/B 有没有变得更像样”**，不回答共享到 ETH/SOL follower、也不回答多 venue 精确定义。

## Raw result
关键阈值（样本内）：
- `q20 ≈ -0.670`
- `q80 ≈ +0.681`
- `q10 ≈ -1.156`
- `q90 ≈ +1.157`

### 1) 全样本上，这个 base alpha 本体并不强
- continuation：`-0.22 bps`
- fade：`+0.22 bps`

也就是说：**不加 gate 的 15m BTC“沿上一段方向继续做”本身是负的。**

### 2) 高 `ΔKVSI` 时，确实出现了一个“顺着上冲别急着反打”的味道
当 `d_kvsi_z >= q80`：
- continuation：`+0.52 bps`
- fade：`-0.52 bps`

更极端的 `top decile`：
- continuation：`+3.02 bps`
- fade：`-3.02 bps`

### 3) 但这个味道并不是对称 shared continuation，而是**偏单边的 up-impulse continuation / short-fade veto**
把上一段 `15m` 分成涨跌两类后：

#### prior 15m up
- 全样本 continuation：`-0.28 bps`
- `gate_on_q80` continuation：`+1.87 bps`
- `gate_off_q20` continuation：`-1.33 bps`

这说明：
**当上一段已经往上，且 `ΔKVSI` 强时，未来 15m 更像 continuation；至少在这份超短样本里，做空 fade 明显更不该贸然开。**

#### prior 15m down
- 全样本 continuation：`-0.17 bps`
- `gate_on_q80` continuation：`-0.53 bps`
- `gate_off_q20` continuation：`+0.93 bps`

这说明：
**它并没有对称地支持“韩盘变强 -> 下跌 continuation 更好”。**
相反，在这份 probe 里，高 `ΔKVSI` 时，向下 continuation 更差，未来 15m 平均反而偏正。

## Honest readthrough
因此，这轮 follow-up 的最诚实读法不是：
- “Rank 291 已证明自己是 shared continuation gate”，也不是
- “它已经能独立升到 P2 继续 admission”。

更准确的是：
1. `ΔKVSI` **不是纯空气**；
2. 它在这份最小 A/B 里确实留下了一点 **“risk-on / Korea-led upward continuation”** 的影子；
3. 但这个影子当前更像 **BTC 单腿、超短样本、偏上行单边的 veto / allow 信号**；
4. 还远远不够支撑它作为一个可共享到 `BTC/ETH/SOL momentum + leader-follower + shock-reversal` 的前排 `P2` 对象继续占资源。

换句话说：
**这轮终于把它挂到了一个明确 base alpha 上，但答案偏向“它有一点 bullish continuation / short-fade veto 味道”，而不是“它已经是可升 P2 的 shared regime gate”。**

## Why it does NOT promote to P2
按 policy，这条 survivor 只允许一次 truly decisive follow-up。
这一刀之后，缺口仍然很大：
- 还是只有 **BTC 单腿**；
- 还是只有 **约 4 天 public-data probe**；
- 还没有 `ETH/SOL follower` 或 `BTC -> alt lead-lag` 挂接；
- `Upbit vs Binance` 仍是粗 proxy，不是更完整的 `Korea vs global` 定义；
- 最关键的是：这轮结果显示它当前更像 **局部 bullish veto / allow overlay**，还没有长成 policy 想要的 **shared gate 主语**。

所以继续把它保留在 survivor / 前排，只会变成“再补一点叙事”的拖延。

## Runtime effect
- `Rank 291` 的 survivor follow-up 预算已用完。
- 本轮不升 `P2`。
- 对象退出前排，回到 `background/P0`。

## One-line result
`Rank 291` 的唯一 follow-up 已把 `ΔKVSI` 挂到最便宜的 BTC 15m A/B 上：结果显示它更像 **上冲时的 continuation allow / short-fade veto**，而不是可共享到多条 desk 主线的对称 shared gate；样本仍短、范围仍窄，故 survivor 预算用完后最诚实的结论是回 `background/P0`，不升 `P2`。
