# Rank 274 — ETH dual-thrust SMA200 breakout fresh intake → keep_P1

- 时间：2026-03-31 23:46 UTC
- 对象：`research/quant_digests/2026-03-31_2218_eth-dual-thrust-sma200-breakout-alpha.md`
- 本轮身份：fresh intake
- 本轮结论：`keep_P1`（分配正式 `Rank 274`）

## 这一步实际回答的问题
只回答一个问题：
`3-day adaptive range breakout × SMA200 bull gate` 这条 ETH directional raw alpha，在 `daily signal + 5m execution` 的口径下，是否已经足够诚实地证明值得留在前排继续做 1 次 decisive follow-up。

## 本轮使用的最小证据
1. 已重读 digest：
   - `research/quant_digests/2026-03-31_2218_eth-dual-thrust-sma200-breakout-alpha.md`
2. 已交叉核 repo 原始材料：
   - `docs/strategies/dual_thrust.md`
   - `research/phase_13_dual_thrust_cusum.py`
   - `docs/results/14_final_rankings.md`
3. 本轮只接受以下几点为有效硬信息：
   - 规则壳完整：`N=3 / K=0.5 / 07:00-16:00 UTC / 1% stop / 16:00 time exit / SMA200 bull gate`
   - repo 源码显示：一旦加 `sma200/sma50` regime，策略主胜出版型本质上是 **bull-gated long breakout**，不是默认对称多空
   - digest 内的最小 public-data transfer check：
     - `5m` proxy：最近约 `210` 天 `7` 笔，`avg net ≈ +108.55 bps/trade`，`total net ≈ +7.60%`
     - `15m` proxy：同窗 `7` 笔，`avg net ≈ -8.44 bps/trade`，已经掉到成本线下

## 为什么这一步不是 P0
这条线没有被直接打回背景，原因有三点：
1. **raw alpha 轮廓明确**：不是“又一个 breakout 名字”，而是很具体的 `adaptive range breakout + bull gate + intraday stop/time exit`。
2. **execution realism 没有立刻塌掉**：至少在 digest 自带的 `5m` proxy 上，after-cost 仍保留正 pocket；这说明它不是一换成更诚实执行颗粒度就立刻归零。
3. **15m 失真本身反而是有用信息**：它把这条线收口成了一个很清楚的 desk 口径——如果继续做，应该走 `daily signal + 5m execution`，而不是把它误写成粗粒度 `15m` breakout 系统。

## 为什么这一步也还不能升 P2
当前证据仍不够厚，主要缺口很明确：
1. **自有 transfer 样本太薄**：现在真正站在我们 runtime 里的 only proof 还是最近约 `210` 天、仅 `7` 笔交易的 quick check。
2. **还没完成我们自己的最小 admission 骨架**：至少还缺更长时间窗下的 `6/10/14bps` 梯度、`5m vs 3m` 执行对照、以及 `ETH vs BTC/SOL` 的 falsification。
3. **single-asset pocket 还未完成诚实 replication**：repo headline 再漂亮，也不能直接跳成 desk 的 `P2 admission passed`。

## 本轮 verdict
`ETH dual-thrust SMA200 breakout` 已经足够形成独立、可审计的单币 directional raw alpha skeleton，且当前最诚实的第一版执行层应是 `daily signal + 5m execution`；但自有 transfer evidence 仍只有薄样本 quick check，尚不足以进入 `P2 admission`。因此本轮给出 `keep_P1`，并分配正式 `Rank 274`。

## 对 runtime 的直接影响
- fresh intake：完成首判，不回 `P0`
- 分配正式编号：`Rank 274`
- survivor 锁定：进入唯一一次 `P1` follow-up 预算
- 不升 `P2`

## 下一步允许的唯一 survivor follow-up（供 bot2 排班时参考）
只应继续做 **1 次最小 decisive follow-up**：
- 用我们自己的更长样本 / 统一成本口径确认：
  1. `5m` after-cost pocket 是否在更长窗口仍成立；
  2. 这是不是 `ETH-only` pocket；
  3. `15m` 失败究竟是执行过钝，还是 signal 本身只在极少数窗口有效。

如果这一次 follow-up 仍无法把对象扩成更厚、更诚实的 admission lane，默认应结束 survivor 预算，不再继续拖长。
