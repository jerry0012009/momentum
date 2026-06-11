# Rank 186 — runner incrementalized and health verified

时间：2026-03-27 13:58 UTC

## 这次改了什么
`Rank 186 / CME expiry postfix short BTC` 的 runner 原先每分钟都会：
- 回刷 2025-01 到当前月的全部闭合事件窗口
- 同时抓当前 top-of-book

这会让一个**月频 exact-time 事件策略**在绝大多数“非事件窗口”时段，产生不必要的重复 market-data 拉取。

本轮已把其改成 **incremental + cache-first**：

1. **历史闭合月份：cache once, reuse thereafter**
   - 每个月度事件窗口（`event-2m` 到 `exit+5m`）落到
     `reports/artifacts/paper_rank186_cme_expiry/cache/rank186_event_window_YYYY_MM.csv`
   - 若 cache 已完整覆盖 entry/exit 所需 bar，则后续运行**直接复用**，不再重复请求 Binance `1m` klines

2. **当前 live month：只在真实事件监控窗口内做增量补 bars**
   - 监控窗口定义为：`[event-10m, event+125m]`
   - 只有在这个窗口内，runner 才会做 `1m` incremental append
   - 窗口外默认 `live_window_mode = idle_outside_event_window`，不拉 `1m` K 线

3. **盘口 book 也不再无脑每分钟抓**
   - 窗口外跳过
   - 窗口内才按需抓取；并允许复用近期 snapshot

---

## 为什么仍保留 1m scheduler
结论：
- **不需要**全年/月内全时段每分钟拉 `1m` K 线
- 但 **保留 1m scheduler 是合理的**，因为：
  1. 这是一个 exact-time 月频事件策略，entry 口径是 `+5m`
  2. live window 只有很短一段（事件前后约 135 分钟）
  3. 在这段短窗口内，`1m` cadence 仍是最自然、最诚实的监控频率

因此最终设计不是“降成粗频率 timer”，而是：
- **保留 1m timer**
- **把 market-data 拉取改成 window-gated incremental polling**

也就是说：
> `1m scheduler` 仍在，但 `1m kline pull` 只在真正需要的时候发生。

---

## 实测验证
### 首跑（seed cache）
- 首跑会把历史闭合月份 seed 到本地 cache
- 当次网络调用：`closed_month_network_calls = 14`
- 这是一次性冷启动成本，不是持续成本

### 第二次运行（cache reuse）
- 在非事件窗口重复执行时：
  - `closed_month_network_calls = 0`
  - `live_window_network_calls = 0`
  - `total_network_calls_this_run = 0`
  - `book_mode = skip_outside_event_window`
  - `live_window_mode = idle_outside_event_window`

这证明增量化已经真正生效，不是名义上的优化。

### 健康性验证
- 手动 `systemctl start momentum-rank186-paper-refresh.service`：成功
- 随后 timer 自然触发一轮：成功
- 最近一次自然触发验证：
  - `ExecMainStartTimestamp=2026-03-27 13:56:25 UTC`
  - `ExecMainExitTimestamp=2026-03-27 13:56:26 UTC`
  - `ExecMainStatus=0`
  - `Result=success`

---

## 结果
`Rank 186` 现在的更诚实读法是：
- 仍然是 **1m scheduler 的 monthly exact-time event runner**
- 但不再是“全年每分钟都在重复回刷历史 + 拉实时 K 线”
- 已升级为：
  - **historical cache reuse**
  - **live-window incremental append**
  - **outside-window zero-kline-pull**

这比原来的实现更符合该策略本身的月频/事件驱动属性，也更节省 API 资源。