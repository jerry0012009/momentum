# Rank 284 — dual-test cointegration z-score pairs：first verdict = keep_P1

- 时间：2026-04-01 21:49 UTC
- 对象：`ADF + Johansen dual-test × rolling-beta spread z-score fade pairs`
- 来源：`research/quant_digests/2026-04-01_2105_dualtest-coint-zscore-pairs-alpha.md`
- 本轮角色：bot3 当前唯一 pending 小点执行

## 本轮结论

这条 intake 已经形成**可审计的 pairs raw alpha skeleton**，因此本轮正式记为 `Rank 284` 并首判 `keep_P1`。

支撑它保留前排的，不是“又一个 pairs repo”，而是下面这层可迁移骨架已经说清楚了：

1. `pair admission` 不是泛泛看相关性，而是先过 `ADF + Johansen` 双检验；
2. 交易对象是 `rolling beta / alpha` 定义的 hedge 后 spread，不是单腿方向；
3. entry / exit / stop / turnover cost 都已经写成明确策略壳；
4. walk-forward 结构明确：`12m` pair discovery、`6m` 重选、`90d` rolling hedge ratio。

但这轮还不够诚实地直升 `P2`，原因也很明确：

1. 当前证据仍是 **日频 CoinGecko 回测壳**，不是已在 Binance/Bybit/OKX intraday perp 上完成 clean-room replication 的短周期 after-cost 结果；
2. repo 虽然嘴上强调 `dual test`，但实现里一旦 `ADF + Johansen` 没筛出 pair，会**静默回退到 ADF-only**，这会把最关键的 honesty gate 悄悄放松；
3. `adf_for_pair()` 里残差是 `Y - beta * X - alpha`（`Y = log_j`, `X = log_i`），但 `gen_signals()` 里实际交易的 spread 写成 `log_i - beta * log_j - alpha`，方向口径并未真正一致，不能直接把 repo 回测表现当干净 transfer 证据；
4. repo 默认成本是 daily 口径 `10bps one-way` turnover drag，尚未回答双腿 legging、funding、盘口深度与 intraday friction ladder 下还有没有够厚的 edge。

所以更准确的口径是：

> `Rank 284` 值得保留的，不是 repo headline，而是“先把假 pair 挡在门外，再对剩下的 spread 做均值回复”这条 pairs admission shell；但在 intraday perp clean-room replication、禁用 ADF-only fallback、以及统一 spread / residual 定义之前，它还只是 `keep_P1`，不该跳升 `P2`。

## 为什么不是 P0

因为对象已经具备最小可迁移策略骨架：

- pair formation：有；
- hedge ratio / spread 定义：有；
- entry / exit / stop：有；
- re-selection / walk-forward：有；
- cost 口径：至少有显式写入，不是完全忽略。

这足以证明它不是只有术语没有策略壳的课程式叙事。

## 为什么不是 P2

因为当前最关键的 admission 诚实性还没被本地 short-cycle desk 口径验证：

- `ADF-only` vs `ADF+Johansen` 在 intraday OOS 下是否真的拉开；
- 禁止 silent fallback 后，pair availability 会不会塌到几乎不可交易；
- 统一 spread / residual 方向后，z-score fade 还有没有同样结果；
- `1h discovery -> 15m execute -> 5m routing` 加上 `12/20/32bps` pair round-trip friction ladder 后，是否仍留得住净 pocket。

这些问题没答完前，把它升到 `P2` 会把“admission logic 值得学”误写成“已经接近 paper-worthy”。

## 对 runtime 的实际影响

- 新分配正式 `Rank`：`284`
- 当前 fresh intake 首判：`keep_P1`
- survivor 槽应切换为 `Rank 284`
- 唯一 follow-up 应直接检查：禁用 fallback 后，`dual-test` 是否仍能在 liquid perp universe 留下足够厚、after-cost、可执行的 pair pool。
