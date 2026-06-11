# rank32b global shadow live-like backtest

口径：global strongest-only；入场按历史 5m bar simulate_entry，出场按 1m K 线逐分钟回放；USDT PnL 用 live-like 100U/40U 仓位换算。

## Horizon: 3 days
- signal_generation_mode: official_close_only
- exit_params: TP 1.75 ATR | SL 1.00 ATR | timeout 120m
- selected_winners: 12
- paper_trades: 12 | closed: 12 | open: 0
- skipped_by_max_concurrent: 0 | skipped_same_symbol: 0 | skipped_same_bar: 0
- realized_return: -0.1485 | marked_return: -0.1485
- live_like_pnl: -6.08 | closed_pnl: -6.08 | mdd: 0.1579
- closed_win_rate: 0.3333

## Horizon: 10 days
- signal_generation_mode: official_close_only
- exit_params: TP 1.75 ATR | SL 1.00 ATR | timeout 120m
- selected_winners: 84
- paper_trades: 81 | closed: 81 | open: 0
- skipped_by_max_concurrent: 1 | skipped_same_symbol: 2 | skipped_same_bar: 0
- realized_return: -0.0889 | marked_return: -0.0889
- live_like_pnl: -5.28 | closed_pnl: -5.28 | mdd: 0.1579
- closed_win_rate: 0.4321

## Horizon: 30 days
- signal_generation_mode: official_close_only
- exit_params: TP 1.75 ATR | SL 1.00 ATR | timeout 120m
- selected_winners: 311
- paper_trades: 296 | closed: 296 | open: 0
- skipped_by_max_concurrent: 1 | skipped_same_symbol: 14 | skipped_same_bar: 0
- realized_return: -0.0474 | marked_return: -0.0474
- live_like_pnl: -3.63 | closed_pnl: -3.63 | mdd: 0.1911
- closed_win_rate: 0.4426

## Horizon: 60 days
- signal_generation_mode: official_close_only
- exit_params: TP 1.75 ATR | SL 1.00 ATR | timeout 120m
- selected_winners: 660
- paper_trades: 632 | closed: 632 | open: 0
- skipped_by_max_concurrent: 4 | skipped_same_symbol: 24 | skipped_same_bar: 0
- realized_return: -0.3487 | marked_return: -0.3487
- live_like_pnl: -44.38 | closed_pnl: -44.38 | mdd: 0.4431
- closed_win_rate: 0.4146

