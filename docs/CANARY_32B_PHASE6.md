# Rank 32b Canary / Phase 6 Auto Runner（可执行闭环）

## 目标
把 32b canary 从“单步实验”推进到“可自动重复执行”的最小闭环：

- signal → risk → entry
- entry 成交后自动挂 exit plan（protective STOP_MARKET + reduce-only TP）
- timeout 触发后自动市价平仓
- 全程落地状态文件 / 事件日志 / 网站看板 JSON

## 本轮重点
1. **单次下单成功率优先**
   - 默认 entry 改为 `MARKET`（可配置），优先保证 canary 小仓位下单可执行。
   - 若切回 `limit_gtx`，支持 TTL 到期后 fallback market。
2. **自动运行可落地**
   - runner 支持重复调用（cron / 手工都可）。
   - 每次先做 pending/live 同步，再处理新信号，避免状态漂移。
3. **离场可控**
   - SL：protective STOP_MARKET（默认 `sl_atr_mult=1.0`）
   - TP：reduce-only LIMIT（当前 heartbeat live 默认 `tp_atr_mult=1.0`、GTC）
   - Timeout：到时自动 reduce-only MARKET 平仓（默认 120 分钟）

## 关键产物
- `scripts/run_rank32b_canary_phase6.py`
- `reports/artifacts/rank32b_canary/phase6_*.json`
  - status / run_summary / recent_orders / recent_positions / recent_closed_trades / warnings / symbol_state
- `reports/artifacts/rank32b_canary/phase6_events.jsonl`

## 配置（`config/execution/rank32b_canary.yaml`）
新增 `phase6`：

- `entry.order_type`: `market`（默认）或 `limit_gtx`
- `entry.ttl_minutes`: limit entry 的超时
- `entry.fallback_to_market_on_ttl`: TTL 到期是否 fallback
- `sizing.desired_notional_usdt`: canary 下单规模（当前 heartbeat live 默认 20U；BTC 单独 100U，ETH 单独 20U）
- `sizing.min_notional_buffer_mult`: 交易所最小可成交名义金额之上的缓冲倍数（默认 1.0）
- `exit.tp_atr_mult`: ATR 倍数目标止盈（当前 heartbeat live 推荐 1.0）
- `exit.sl_atr_mult`: ATR 倍数保护性止损（当前推荐 1.0）
- `exit.fallback_tp_bps_if_no_atr`: 没 ATR 时的兜底 TP
- `exit.fallback_sl_bps_if_no_atr`: 没 ATR 时的兜底 SL
- `exit.timeout_minutes`: 超时平仓阈值（当前推荐 120）

补充：当前 32B 已收口为 **heartbeat live**：真钱只保留 BTC / ETH，其余标的全部退回 shadow。

补充：runner 现在会按 Binance 实际约束计算 **effective min trade floor**，不是只看配置里的 `desired_notional_usdt`。
- ETHUSDT 当前主要受 `MIN_NOTIONAL=20` 约束，实际可成交 floor 大约在 20U 出头。
- BTCUSDT 则经常同时受 `MIN_NOTIONAL=100` 和 `LOT_SIZE=0.001` 影响；当 BTC 价格较高时，最小可成交单往往会被抬到 `0.002 BTC` 这一档，对应远高于 100U。

## 运行方式
```bash
cd /root/clawd/jerry/momentum
python3 scripts/run_rank32b_canary_phase6.py --config config/execution/rank32b_canary.yaml
```

回放当前窗口信号（调试）：
```bash
python3 scripts/run_rank32b_canary_phase6.py --config config/execution/rank32b_canary.yaml --force-replay
```

## 自动运行（systemd 定时器示例）
已提供：
- `ops/systemd/momentum-rank32b-canary-phase6.service`
- `ops/systemd/momentum-rank32b-canary-phase6.timer`

示例安装：
```bash
sudo cp ops/systemd/momentum-rank32b-canary-phase6.service /etc/systemd/system/
sudo cp ops/systemd/momentum-rank32b-canary-phase6.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now momentum-rank32b-canary-phase6.timer
systemctl status momentum-rank32b-canary-phase6.timer
```

## 成功标准
- 能稳定写出 phase6 状态与订单/持仓/平仓 JSON
- 至少一次完成：entry 成功 + exit plan 建立
- 在 timeout 条件下可自动平仓并写入 closed trades
- 运行失败时 warnings 中可定位原因（risk reject / query fail / cancel fail 等）

## 已知限制
- 目前 PnL 为粗算（不含手续费/资金费精算）。
- 未做 exchange-side 全量恢复（例如进程外下单后首次重启的强恢复）。
- 仍建议先在极小 notional 下观察若干轮，再扩大规模。
