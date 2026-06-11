# console2002/polymarket-momentum-bot fresh intake（2026-03-24 15:02 UTC）

## Intake target
- Repo: `console2002/polymarket-momentum-bot`
- URL: <https://github.com/console2002/polymarket-momentum-bot>
- Claimed idea: 利用 Polymarket 15 分钟加密预测市场在剧烈方向波动时对现货价格反应存在 30-90 秒滞后，做短持有 momentum lag arbitrage。

## What I checked
- GitHub 搜索结果：该 repo 仅 1 star，最近更新时间 2025-12-13。
- README 明确给出的公开口径包括：
  - 目标市场：BTC / ETH / SOL / XRP 的 15 分钟 up/down Polymarket 市场；
  - 入场逻辑：`<1 分钟内 >2%` 现货大波动 + `>=3%` implied probability gap；
  - 出场逻辑：gap 收敛到 `<1%` 或持有到 12 分钟；
  - 资金管理：1-5% 仓位、最多 3 笔并发、10% 回撤停机；
  - 宣传口径：`99%+ accuracy`、`50-150% per trade`。

## Honesty check
这次只做 fresh intake 级别的最小诚实判断，不进入重度 admission。

公开材料里目前缺的不是“小修小补”，而是能支撑 `keep_P1` 的最基本证据：
1. **没有 fee-aware / slippage-aware backtest 输出**：README 给了回测命令，但没有任何已完成样本结果、交易分布、成本后收益、容量或成交约束汇总。
2. **没有 clean-room 样本边界**：看不到训练/调参区间与评估区间，也看不到 walk-forward / out-of-sample 划分。
3. **没有 execution realism 证据**：这个 alpha 本质依赖极短滞后窗口，但公开材料只写了“market buy / market sell + liquidity >$1k”，没有展示盘口穿透、抢跑、撮合失败、成交延迟、价格冲击后的残余 edge。
4. **宣传收益口径过猛但无配套证明**：`99%+ accuracy` 与 `50-150% per trade` 这类数字如果没有完整样本与成交约束，默认不能当作可信研究结论。
5. **reader-facing artifact 不足**：当前公开内容主要是 README 级策略叙述 + 工程骨架，不是已经完成的诚实研究结果。

## Verdict
`console2002/polymarket-momentum-bot` 本轮 fresh intake 结论为 **direct park**，不进入 `Surviving candidate slot`。

## One-sentence result
`console2002/polymarket-momentum-bot`：公开材料停留在高收益宣传与工程骨架，缺少成本后回测、clean-room 样本边界与超短滞后执行真实性证据，因此 fresh intake 直接 park，不给 `keep_P1`。
