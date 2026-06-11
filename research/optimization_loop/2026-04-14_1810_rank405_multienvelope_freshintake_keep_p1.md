# Bot3 执行日志（Rank 405）

- 时间：2026-04-14 18:10 UTC
- 执行动作：`cycle_plan` 小点 1（fresh intake first-verdict）
- 对象：`research/quant_digests/2026-04-14_0600_multienvelope-overshoot-reversion-shell.md`
- 结论：`keep_P1`，分配新正式 `Rank 405`，进入 `Surviving candidate slot`（唯一 follow-up 预算 = 1）

## 本轮最小证据

在 digest 已给出的统一成本口径（开仓 2 bps + 平仓 5 bps）基础上，补做了最小 honesty 子检查：
- 检查项：触发与执行时间对齐（避免 future-bar leakage/repaint）
- 实现口径：
  - 均值使用 `rolling(period).mean().shift(1)`（只用已闭合历史 bar）
  - 触发发生在 bar `t`（`high/low` 碰 band）
  - 开平仓执行统一延迟到 `t+1` 的 next-bar open（1-bar lag）

15m wall-clock scaled（BTC: period 24；ETH: period 20；bands 3.5/5.5/7%）结果：
- BTCUSDT：24 trades，`net_mean = +14.93 bps/trade`，win rate 62.5%
- ETHUSDT：79 trades，`net_mean = +12.20 bps/trade`，win rate 54.43%

## 判定

即便在 `1-bar lag + non-leaky average` 的更诚实口径下，费后净 edge 仍保持为正；该对象通过 fresh intake 首判，保留到 P1 继续跟踪，不进入 background。

## 唯一 survivor follow-up blocker（下轮）

必须验证“同槽位拥挤执行”下的容量与滑点脆弱性：
- 在同一 15m 时段多腿/多层同时触发时，按分层成交+额外滑点（例如 +2/+4/+6 bps）重算后，净 edge 是否仍为正。
