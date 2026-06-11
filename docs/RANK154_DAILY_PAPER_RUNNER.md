# Rank 154 Daily Paper Runner

目标：把 `Rank 154 / Crypto-Stat-Arb` 从旧的 refresh-only 占位 sidecar，升级成**每天自动续跑的 forward paper 组合线**。

## 现在会做什么
- 每天用 **Binance USDT-M perpetual** 的已完成日线 + funding 数据重算一次。
- 先按 guard 过滤：
  - 只保留纯字母 base（过滤 `1000XXX` / 稳定币类 base）
  - 上市历史至少 `180` 天
- 在 guard 后样本里按 **rolling 30d quote volume** 选前 `30` 个币。
- 计算三条横截面信号：
  - `carry` = 当日 funding 聚合
  - `momo` = 10 日动量
  - `breakout` = 离 20 日新高有多近
- 用 `0.5 carry + 0.2 momo + 0.3 breakout` 合成目标权重。
- 执行口径：
  - 每边成本 `5 bps`
  - 单币绝对权重上限 `10%`
  - 调仓 buffer `1% weight`
- 记录：决策、调仓、持仓、equity curve、费用、funding、理由与证据。

## 运行入口
```bash
cd /root/clawd/jerry/momentum
python3 scripts/run_rank154_crypto_stat_arb_paper_runner.py --init-from-now
python3 scripts/run_rank154_crypto_stat_arb_paper_runner.py --refresh
```

或走 scheduler 包装层：
```bash
python3 scripts/run_rank154_crypto_stat_arb_paper_sidecar_refresh.py
```

## systemd
- timer: `ops/systemd/momentum-rank154-paper-sidecar-refresh.timer`
- service: `ops/systemd/momentum-rank154-paper-sidecar-refresh.service`
- 默认计划：`00:20 UTC` 每天跑一次

## 主要产物
都在：
`reports/artifacts/paper_rank154_crypto_stat_arb_runner/`

关键文件：
- `rank154_paper_state.json`
- `rank154_paper_status.csv`
- `rank154_paper_equity_curve.csv`
- `rank154_paper_decisions.csv`
- `rank154_paper_rebalance_trades.csv`
- `rank154_paper_open_positions.csv`
- `rank154_paper_universe_snapshot.csv`
- `rank154_paper_universe_excluded.csv`
- `rank154_paper_last_run_summary.json`

页面：
- `reports/site/factors/paper_rank154_crypto_stat_arb_runner/report.html`

## 边界
- 这是 **paper-only**，不是 live trading。
- 它会记录 forward 决策和 forward PnL，但不声称和真实成交完全等价。
- 如果后续要推向 tiny-live，应再补更严格的成交/滑点/风控层，而不是直接把这条纸面线当实盘。 
