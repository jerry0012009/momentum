# 2026-04-14 10:46 UTC — Rank 403 survivor 唯一 follow-up（30~50 liquid alts × 2/3/4-bar 降频）

## 本轮执行小点
- `cycle_plan` 第 2 项（首个 pending）：`Rank 403 / top-half-liquidity XS loser-bounce shell`
- 动作：在 30~50 liquid alts 横截面执行 2/3/4-bar 降频复核（统一 taker 成本 + 1-bar lag），并补 1 条最小 honesty 检查（排序与持仓对齐不使用同窗未来信息）

## 最小执行与产物
- 产物：`reports/artifacts/optimization_loop/rank403_survivor_followup_30to50alts_2_3_4bar_2026-04-14.json`
- 数据口径：Binance USDⓈ-M `5m`，按 24h quote volume 取前 50 个 USDT perpetual 作为“30~50 liquid alts”代理横截面。
- 策略口径：`reversal_score = -rolling(H=3) return sum`，横截面双边各 `q=20%`，`cost=4bps`，执行使用 `lag=1`。

## 关键结果（会改变系统认知）
- 在更宽 50 币液体横截面下，降频并未把 Rank 403 壳体拉回可交易净后：
  - `rebalance every 2 bars`: `-3.31 bps/bar`
  - `rebalance every 3 bars`: `-4.05 bps/bar`
  - `rebalance every 4 bars`: `-4.85 bps/bar`
- 最小 honesty 检查：
  - 使用 policy 口径 `lag=1`（realistic）与不现实 `lag=0` 对照（same-bar 对齐）时，`lag=0` 未给出“更好到可翻盘”的结果（`-4.92 bps/bar`），说明本轮结论不依赖同窗前视伪优势。

## 结论与槽位动作
- `Rank 403` survivor 唯一 follow-up 已执行且预算归零；在扩大横截面 + 降频后仍被统一成本口径压穿，故本轮按规则直接收口为 `background/P0`（不升 `P2`）。
- `Surviving candidate slot` 释放为 `none`，对象回到 `Background pool`。
