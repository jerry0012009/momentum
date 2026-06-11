# bot3 optimization loop — watchlist top-score rotation fresh intake first verdict（2026-04-14 00:50 UTC）

## 本轮执行小点
- target: `research/quant_digests/2026-04-13_2044_watchlist-topscore-rotation-shell.md`
- action: fresh intake first-verdict + 1 条 honesty/execution 子检查（top-score 轮动是否含排序前视/未来窗泄漏）

## 读取与核验
- digest: `research/quant_digests/2026-04-13_2044_watchlist-topscore-rotation-shell.md`
- probe summary: `reports/artifacts/quant_digests/multi_pair_watchlist_rotation_probe_summary_2026-04-13.json`
- probe script: `reports/artifacts/quant_digests/2026-04-13_multi_pair_watchlist_rotation_probe.py`

## 关键证据（统一成本口径）
- `15m` 主口径（max_positions=3）: `207` 笔，`avg_net_bp = -22.87 bps`，`sum_net_bp = -4734 bps`
- `5m` 主口径（max_positions=3）: `252` 笔，`avg_net_bp = -28.07 bps`，`sum_net_bp = -7074 bps`
- capacity sweep（1/2/3/5 仓）在 `15m` 与 `5m` 全部仍为负，未出现费后转正口径

## honesty / execution realism 子检查（最小 decisive）
检查 `2026-04-13_multi_pair_watchlist_rotation_probe.py` 的信号与成交时序：
1. 指标仅由当前及历史 bar 构造（RSI/EMA/rolling volume），未读取 future bar；
2. `buy_signal` 在 bar `i` 判定，实际入场价使用 `i+1` 的 `next_open`；
3. `sell_signal` 触发时同样使用 `i+1` 的开盘价出场；
4. top-score 排名只在当下候选集合内排序，不调用未来收益字段。

结论：本轮未发现“排序前视/未来窗泄漏”这一单一 honesty blocker；负收益结论并非由明显前视错误造成。

## 本轮 verdict
`watchlist top-score rotation × pullback-resumption` 在当前 Binance majors portability 口径下费后持续为负，且最小 honesty 子检查未发现可一键翻转结论的前视漏洞；本轮 first verdict 收口为 `background/P0`（不进入 `keep_P1`，不分配 rank）。

## 回写动作
- 更新 `BOT2_BOT3_STATE.md`：
  - `Fresh intake slot.latest_result` / `latest_result_record` 指向本结论；
  - `Background pool.latest_parked` / `latest_parked_record` 指向本对象；
  - `cycle_plan` 第 3 小点写入 result 并置 `status: done`。
