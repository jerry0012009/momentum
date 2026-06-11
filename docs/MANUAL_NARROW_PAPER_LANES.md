# Manual Narrow Paper Lanes

目的：把 `Rank 2 / Rank 17 / Rank 29 / Rank 32b` 这些已经从 Scout 升格、并进入 `Paper / 正在自动运行` 的 crypto 15m 候选，改成**专属定时 refresh + 独立状态页** 的 autonomous paper-trade 形态，而不是继续依赖 bot2 / bot3 的提示词去催。

## 数据源
- 默认：**Binance spot 15m klines**
- 资产：
  - `Rank 2`：BTC / ETH / SOL
  - `Rank 17`：ETH / SOL（BTC 继续排除在 narrow pilot 外）
  - `Rank 29`：BTC / ETH / SOL
  - `Rank 32b`：BTC / ETH / SOL

## 启动（只做一次）
```bash
cd /root/clawd/jerry/momentum
python3 scripts/run_manual_narrow_paper_lanes.py --init-from-now
```

这一步会：
- 重新用 Binance 15m 数据计算当前所有已接入 lane（现含 Rank 2 / 17 / 29 / 32b）；
- 把当前**已闭合**的历史 trade 当成启动水位线；
- 从“现在开始”记录后续新闭合的 paper trades；
- 不会把历史 120~150 天的旧 trades 整段灌进新的手动 ledger。

## 默认运行方式：专属 cron 自动刷新
默认应由**专属 narrow-paper cron**运行下面这个入口，而不是再让 bot2 / bot3 反复思考这些已自跑的 paper lane：
```bash
cd /root/clawd/jerry/momentum
bash scripts/run_manual_narrow_paper_lanes_cron.sh
```

这一步会：
- 再抓一次 Binance 15m；
- 重新计算所有已接入 lane；
- 只把**自启动以来新闭合**的 trades 追加到账本；
- 更新每条 lane 的最新状态和未闭合头寸快照；
- 重建并发布独立状态页；
- 同步重建并发布 Rank29 相关联的页面（`rank29_shadow_dashboard`、`rank29_monitoring_hub`、`clean replication main report`），避免 narrow-paper artifacts 已刷新但 Rank29 前台还停在旧快照。

## 如需人工临时补跑
```bash
cd /root/clawd/jerry/momentum
python3 scripts/run_manual_narrow_paper_lanes.py --refresh
bash scripts/publish_rank29_shadow_dashboard.sh
```

## 产物
都在：
`reports/artifacts/manual_narrow_paper_lanes/`

关键文件：
- `manual_narrow_paper_state.json`
  - 当前水位线（每条 lane 记到哪个 `exit_ts`）
- `manual_narrow_paper_closed_trades.csv`
  - 启动后新闭合、已追加到账本的 trades
- `manual_narrow_paper_status.csv`
  - 每条 lane 当前最新状态（sample_end / latest_closed_exit / cumulative return / open position）
- `manual_narrow_paper_open_positions.csv`
  - 若最新样本尾部还留有未正式闭合的 paper 头寸，会记在这里
- `manual_narrow_paper_last_run_summary.json`
  - 最近一次运行摘要

## 口径说明
- 这是 **paper-only narrow pilot tracking**，不是实盘、也不是 tiny-live。
- 默认现在由**专属 cron**自动刷新；bot2 / bot3 不需要继续把主思考资源花在这些 P3 lane 的日常续写上。
- 因为每次 refresh 都会从 Binance 重算并用水位线去重，所以即使偶尔人工补跑，**启动后的已闭合 trades 也不会丢。**
- `Rank 17` 仍然只跑 **ETH + SOL**；BTC 继续保持 excluded / parked leg。
- `Rank 29` 已于 `2026-04-04` 降为 **`P0 archived`**：strict-causal 复盘确认旧口径存在 future leak / hindsight contamination，因此不再属于有效的 P3 narrow pilot。
- `Rank 29 gate shadow` 也同步归档：仅保留作历史审计与反例材料，不再视为可继续推进的 paper overlay。
- 若后续要重启 `Rank 29` 家族，必须以新的 strict-causal 定义另立候选，不能沿用当前 archived baseline / shadow 的历史 headline。
- `Rank 2` 当前沿用的是 **`combo_all`** 的 P3 口径。
- `Rank 32b` 当前沿用的是 **`ema_cross_plus_slope_floor`** 的 full-scope P3 口径。
- 如果要区分 `baseline / gate shadow / orderbook shadow` 三者分别回答什么问题，请看：`docs/RANK29_SHADOWS.md`
