# bot3 optimization loop log — 2026-04-13 12:36 UTC

## 执行小点
- target: `research/quant_digests/2026-04-13_1145_localextrema-branchsplit-long-router-alpha.md`
- action: fresh intake first-verdict（统一成本口径费后边际 + 触发密度 + 1 条 honesty/execution realism 检查）

## 最小证据
数据源：`reports/artifacts/quant_digests/2026-04-13_localextrema_probe_metrics.csv`

在统一 `12 bps round-trip` 成本口径下，按分支独立看 best horizon：
- `BTCUSDT 15m / max_branch / h=24`: gross `+35.05 bps`，net `+23.05 bps`，`20` 笔（`0.167` 笔/天）
- `ETHUSDT 15m / max_branch / h=24`: gross `+63.27 bps`，net `+51.27 bps`，`18` 笔（`0.150` 笔/天）
- `ETHUSDT 5m / min_branch / h=36`: gross `+55.83 bps`，net `+43.83 bps`，`34` 笔（`0.283` 笔/天）
- `SOL` 各分支在该口径下均未保留稳定正费后边际（不纳入首批可交易 universe）

结论：该对象在 majors（BTC/ETH）分支化路由下具备可交易的费后 pocket 与非稀疏触发密度，不应判为 `background/P0`。

## honesty / execution realism 子检查（仅 1 条）
检查脚本：`reports/artifacts/quant_digests/2026-04-13_localextrema_probe.py`

- 信号窗使用 `close.shift(1).rolling(...).max/min()`：极值阈值仅依赖历史已完成 bar，不含当前 bar 未来信息。
- 入场定义为 `entry_idx = i + 1` 且 `next_open`：信号在 bar close 生成，下一根开盘成交，不是同 bar 幻想成交。
- `no-overlap` 已开启，避免同一段波动被重复计数。

判定：本轮未发现“分支切换依赖未来确认/不可成交切换”的单一致命 honesty blocker。

## 本轮 verdict
- 分配新正式 `Rank 398`（next unused integer）
- 对象结论：`keep_P1`
- 唯一 survivor follow-up blocker：在 `majors-only` 下完成 `6/10/15 bps per-side` 成本阶梯的分支独立稳健性复核（含 horizon 敏感性），确认正边际不只由单 horizon 偶然驱动。

一句会改变系统认知的话：
`Rank 398` 在统一 `12bps round-trip` 口径下已显示 BTC/ETH 分支化费后正边际且触发密度可交易，故 fresh intake 首判为 `keep_P1` 并进入 survivor 单次跟进队列。
