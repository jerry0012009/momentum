# BTC COIN-M carry rollover shell · fresh intake first verdict = background / P0

- Time: 2026-04-07 15:30 UTC
- Target: `research/quant_digests/2026-04-07_1334_btc-coinm-carry-rollover-shell.md`
- Cycle action: 作为下一条具体 fresh intake，判断 `positive-basis carry × 15m slot execution × rollover/rehedge shell` 是否真形成了独立于既有 `carry / basis` 家族的完整可迁移 raw alpha 壳，还是只是把熟悉的 cash-and-carry 常识包装成更完整执行流程
- Verdict: `background / P0`

## 为什么这一步要直接收口
这条 digest 写得完整，工程壳也比普通“basis 会收敛”叙述诚实得多：它把 `正 basis carry -> 15m 分片执行 -> 临近到期 rollover -> delta rehedge` 串成了一条能跑的持仓链。

但按当前 bot2/bot3 policy，fresh intake 要保留到 `keep_P1`，必须提供一个**独立于既有家族、值得继续占用 survivor 配额**的新 raw alpha 主语。这里真正的 alpha 仍然是：

> **现货 vs 季度合约的正 basis 向到期收敛。**

`15m slot execution / rollover / rehedge` 的价值，更多是把这条老 carry trade 写成一个更完整的执行外壳，而不是生成一个新的 raw alpha pocket。也就是说：

1. **主语不新。** 它仍是标准 `carry / basis convergence` 家族，不是新独立因子。
2. **增量主要在工程壳，不在 alpha 本体。** `child-order / rollover / delta drift control` 是重要实现细节，但更像旧 carry 线的 deployment shell。
3. **short-cycle 映射也不改变身份。** 15m/1m/5m 在这里主要承担执行与风控时钟，不把对象变成新的 short-cycle directional/raw-alpha 语义。
4. **当前 front-slot 资源更应该留给真正新主语。** 若把这种“老 alpha + 更完整实现”也保留到 survivor，会稀释 `keep_P1` 的含义。

## 结论
因此，这一步的诚实 first verdict 应直接写成：

> `positive-basis carry × 15m slot execution × rollover/rehedge shell` 并未形成独立于既有 `carry / basis` 家族的新 raw alpha 主语；它提供的是更完整的 cash-and-carry 工程壳，而不是值得单独占用 survivor 配额的新前排对象，因此本轮直接记为 `background / P0`。

## Runtime write-back
- `Fresh intake slot.latest_result` 应更新为本次 first verdict
- `Fresh intake slot.source_record` 指向本次 digest
- `Fresh intake slot.latest_result_record` 指向本日志
- `Background pool.latest_parked` 更新为本对象
- `cycle_plan` 第 2 条写回 `done`
