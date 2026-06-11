# Rank 289 — survivor follow-up exhausted — background/P0

- 时间：2026-04-02 06:02 UTC
- 对象：`Rank 289 / vol-normalized ROC shock × EMA displacement × volume confirmation`
- 本轮动作：执行 survivor 的唯一一次 decisive follow-up
- 结论：`follow-up exhausted，退回 background/P0`

## 本轮只执行的 cycle item
对 `Rank 289` 做一次去优化 `15m` clean-room baseline：比较 `shock only / +EMA / +EMA+volume / +EMA+volume+displacement` 四层 ablation，并在 `BTC/ETH/SOL` 上检查 `10/20/30 bps` 往返成本梯度后是否仍保留可迁移 after-cost pocket。

## clean-room 口径
- 样本：现有 `120d` Binance perp `15m` cache（`BTCUSDT / ETHUSDT / SOLUSDT`）
- signal：
  - `roc = close / close[-24] - 1`
  - `shock` 定义为 `|roc| > 1.5 × rolling_std(roc, 96)`
- admission ablation：
  1. `shock_only`
  2. `shock_ema`
  3. `shock_ema_volume`
  4. `shock_ema_volume_displacement`
- 固定去优化参数：`EMA=48`、`volume_ma=48`、`displacement threshold = 1.0 × ret_std × sqrt(48)`
- 执行 proxy：信号后下一根开盘入场，固定持有 `8` 根 `15m` bar，做往返成本 `10/20/30 bps`
- overlap 处理：持仓窗口内不重复开新仓

## 结果摘要
### 1) 全部变体在 10/20/30bps 下都没有跨资产 after-cost pocket
聚合结果（3 资产均值）：

- `shock_only`
  - `10bps`: `-10.83 bps/trade`
  - `20bps`: `-20.83 bps/trade`
  - `30bps`: `-30.83 bps/trade`
- `shock_ema`
  - `10bps`: `-10.44 bps/trade`
  - `20bps`: `-20.44 bps/trade`
  - `30bps`: `-30.44 bps/trade`
- `shock_ema_volume`
  - `10bps`: `-12.71 bps/trade`
  - `20bps`: `-22.71 bps/trade`
  - `30bps`: `-32.71 bps/trade`
- `shock_ema_volume_displacement`
  - `10bps`: `-10.66 bps/trade`
  - `20bps`: `-20.66 bps/trade`
  - `30bps`: `-30.66 bps/trade`

在所有成本层级里，`positive_assets = 0/3`；也就是说，`BTC/ETH/SOL` 没有任何一个资产留下正的 total net return。

### 2) full admission 并没有把这条线救活成可迁移 edge
最接近 repo 叙事的 `shock_ema_volume_displacement`：

- `BTC`: `10/20/30bps` 下分别约 `-10.34 / -20.34 / -30.34 bps/trade`
- `ETH`: `-21.16 / -31.16 / -41.16 bps/trade`
- `SOL`: 毛收益仍有一点残留（约 `+9.52 bps/trade`），但一进 `10bps` 往返成本就变成 `-0.48 bps/trade`，`20bps` 后为 `-10.48 bps/trade`

这说明 admission layer 并没有稳定提炼出一个可以跨 `BTC/ETH/SOL` 迁移的 post-cost pocket；它最多只是在 `SOL` 上留下一个非常薄、轻成本即归零的残余。

### 3) 它更像 repo/WFO 驱动的 family skeleton，不像已证明存在的 desk-level raw alpha
- `shock_only` 与 `shock_ema` 并没有在 clean-room baseline 下显出可靠正边；
- `+volume` 甚至进一步恶化；
- `+displacement` 只是在减少交易数后让部分毛收益变得没那么差，但依然过不了 after-cost 诚实线；
- 因此当前看不到“distinct 的 shock continuation alpha 已经存在，只差进一步 admission”的证据，更像是 repo 里依赖 WFO/优化壳的 family skeleton。

## 本轮改变系统认知的话
`Rank 289` 的 survivor follow-up 已经诚实收口：去优化 `15m` clean-room baseline 下，`shock only / +EMA / +EMA+volume / +EMA+volume+displacement` 在 `BTC/ETH/SOL` 与 `10/20/30bps` 成本梯度上全部未留下可迁移的 after-cost pocket，因此这条 `vol-normalized shock continuation` 当前不升 `P2`，而是 `follow-up exhausted -> background/P0`。

## 产物
- 脚本：`scripts/build_rank289_survivor_followup.py`
- artifact：
  - `reports/artifacts/rank289_survivor_followup/summary_by_asset_variant_cost.csv`
  - `reports/artifacts/rank289_survivor_followup/aggregate_variant_cost.csv`
  - `reports/artifacts/rank289_survivor_followup/decision.json`
