# Rank 318 — survivor follow-up: background/P0

- Time: 2026-04-03 23:17 UTC
- Target: `Rank 318 / Polymarket final-window lag arb`
- Action: survivor one-shot maker-first honesty follow-up
- Verdict: `background/P0`

## Why this changes system belief
`Rank 318` 的 raw alpha 主语仍然成立，但 repo 当前给出的 maker-first 证据壳并不诚实支撑 `promote_P2`：它把最关键的 final-window 深度 / maker fill / edge decay 问题留在口头假设里，而不是落成能改变 admission 的执行证据。具体来说，paper execution 只是把 maker 单直接按 `signal.poly_price + 0.5 * simulated_slippage` 记成成交；未建模挂单不成交、queue position、盘口撤单、临近到期剩余秒数里的 edge decay，也没有把未成交订单当成主要损失来源写进分析层。因此这条线当前更像“值得保留概念”的 binary lag-repair 假说，而不是已经通过 honesty follow-up 的可升级候选，本轮应诚实收口到 `background/P0`。

## Evidence from source
1. **paper mode 默认把 maker 当作近似必成交**
   - `executor.py` 的 `_execute_paper()` 在 `use_maker_orders=True` 时，只把滑点减半后直接生成 `OPEN` 仓位；没有任何 maker fill probability / queue / cancel / partial-fill 模型。
   - 这意味着 paper 表现天然会高估 late-window maker economics，因为真正最容易失败的“挂进去但 8 秒内根本不成交”在 paper 里被抹平了。

2. **live maker 逻辑本身暴露了唯一 decisive blocker，但 repo 没给 blocker 的证据**
   - `executor.py` live 路径里，maker 单只等待 `8s`；不成交就直接取消并返回 `None`。
   - 这说明决定策略是否诚实成立的核心不是 fair value 公式本身，而是：最后 `120s→3s` 窗口里，多少 edge 能在 `8s` 内以 maker 方式真正变成 fill。
   - 但 repo 没提供按剩余时间 bucket / edge bucket / 盘口深度分层的 maker fill 统计，也没给出 5m vs 15m 的成交可得性证据。

3. **analysis 层也没有把未成交 / fill scarcity 当成主指标**
   - `analyze.py` 主要基于已闭合 trades 计算 WR / PnL / realized edge。
   - 它没有把“信号触发后实际 maker 成交率”“因超时取消而错失的 edge”“最后窗口里盘口容量不足导致的不可成交”作为 admission 主轴。
   - 所以现有分析更像在评估“假设已经成交后的赔率方向对不对”，不是在评估 desk 真正关心的 `maker-first honesty`。

4. **配置口径自身也提示这还是采样中的 paper shell，而不是已诚实可迁移的最小正 edge**
   - `config.py` 一方面写 `PAPER PHASE`、把交易窗口扩到 `120s` 以便“collect more data”，另一方面仍保留 `taker_fallback_min_edge_pct = 6.0`、`maker_fill_timeout_sec = 8.0`。
   - 这反而说明 repo 作者自己也知道关键问题是最终窗口里的成交与衰减，而当前材料没有给出能穿过该问题的 public evidence。

## Decision
- 不升 `P2`：因为 survivor follow-up 本该回答的唯一问题——`5m/15m final-window binary lag repair` 在 maker-first、真实临近到期执行约束下，是否仍留有最小可诚实 paper 化正 edge——当前没有被 source 诚实回答。
- 不做开放式 `keep_P1`：survivor 预算只有一次，继续停留只会重复同一 honesty axis。
- 因此本轮直接收口到 `background/P0`。

## Runtime impact
- `Rank 318` removed from `Surviving candidate slot`
- `Surviving candidate slot` cleared to `none`
- `Background pool` latest parked updated to `Rank 318`
- `Fresh intake slot` remains `research/quant_digests/2026-04-03_1425_hyperliquid-public-trigger-cluster-alpha.md`
