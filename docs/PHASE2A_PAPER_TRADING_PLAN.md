# Phase 2a Paper Trading 规划：Event + V4 + Trail 4%

> **状态：IMPLEMENTED — host-level systemd paper/shadow runner 已落地，未接真实下单**
> **日期：2026-05-13 | 参数优化：2026-05-14**
> **关联报告：** [Phase 2a Momentum Ignition Report](https://jp.jerrypsy.top/momentum/paper/rank450/phase2a_momentum_ignition.html)

---

## 0. 已落地实现

| 项目 | 路径 / 命令 |
|------|-------------|
| 配置 | `config/execution/phase2a_event_v4_trail_paper.json` |
| Runner | `scripts/run_phase2a_event_v4_trail_paper.py` |
| Scan | `python3 scripts/run_phase2a_event_v4_trail_paper.py --scan` |
| Monitor | `python3 scripts/run_phase2a_event_v4_trail_paper.py --monitor` |
| Status | `python3 scripts/run_phase2a_event_v4_trail_paper.py --status` |
| Artifacts | `reports/artifacts/paper_phase2a_event_v4_trail/` |
| Status page | `reports/site/factors/paper_phase2a_event_v4_trail/report.html` |
| systemd units | `ops/systemd/momentum-phase2a-event-v4-trail-*.{service,timer}` |
| host-level install | `/etc/systemd/system/momentum-phase2a-event-v4-trail-*.{service,timer}` |
| Run log | `reports/artifacts/paper_phase2a_event_v4_trail/run_log.csv` |
| Monitor marks | `reports/artifacts/paper_phase2a_event_v4_trail/monitor_mark_log.csv` |

当前实现是 **paper/shadow only**：只调用 Binance 公共 API，不读取私钥，不签名，不下真实订单。

运行层面已经从临时后台进程升级为 **宿主机 systemd timer**：

- `momentum-phase2a-event-v4-trail-scan.timer`: 每小时 `:02:15 UTC` 扫描事件和 V4。
- `momentum-phase2a-event-v4-trail-monitor.timer`: 每分钟 `:20 UTC` 检查移动止盈和超时。
- 服务定义安装在 `/etc/systemd/system/`，不依赖当前 Codex 会话或沙箱生命周期。
- runner 使用 `reports/artifacts/paper_phase2a_event_v4_trail/runner.lock` 做单写者文件锁，避免 scan 和 monitor 同时写状态。

网页状态页已经升级为审计面板，包含：

- Runtime/systemd 运行说明。
- Backtest vs Paper 口径对照。
- Signal funnel：event → V4 check → paper entry → paper exit。
- Open positions、closed trades、monitor marks、event log、V4 signal log、slippage audit、rejections、run log。

---

## 1. 策略回顾

### 1.1 核心逻辑（一句话）

> 一个已经暴涨 30%+ 的币，如果在接下来 48 小时内出现"量能二次点火"（成交量突增 3 倍 + 价格涨 1%+），做多，用 4% 移动止盈保护利润。止盈判定使用5分钟K线收盘价（抗噪音），入场滑点超过50bps直接跳过。

### 1.2 策略参数（审计后锁定）

| 参数 | 值 | 来源 |
|------|-----|------|
| Event: rank 阈值 | ≤ 20 | v1.6a 回测 + 审计验证 |
| Event: 24h 收益率 | ≥ 30% | v1.6a 回测 + 审计验证 |
| Event: 24h 成交额 | ≥ $5M | v1.6a 回测 + 审计验证 |
| Event: 冷却期 | 24h/币 | 防止同币重复触发 |
| V4: 成交量突增 | > 3x 前 20 根 1h quote volume 均值 | v1.6a 回测主口径 |
| V4: 价格涨幅 | > 1% (1h bar) | V4 信号定义 |
| V4 信号窗口 | 事件后 1~48h | 回测最优 lag window |
| 止盈方式 | 4% 移动止盈（trailing stop） | 2026-05-14从2%调至4%，原2%被1分钟噪音洗出 |
| 止盈判定价格 | 5分钟K线收盘价 | 2026-05-14新增，替代tick级bid，抗噪音 |
| 滑点容忍 | ≤ 50bps 入场滑点cap | 2026-05-14新增，超50bps直接跳过入场 |
| 入场价 | 信号 K 线收盘价 | 即信号 K 线关闭时下单 |
| 方向 | LONG（做多） | 二次点火=沿原方向 |

### 1.3 审计结论摘要

- **事件检测无偏差**：全量 692 标的独立扫描，与已有叠加层 100% 一致
- **V4 裸信号无效**：中位数仅 +0.04%（事件+V4 是 +0.82%，20 倍差距）
- **结论**：事件上下文是核心 alpha 来源，不可省略

---

## 2. 系统架构

```
┌──────────────────────────────────────────────────────┐
│                   Paper Trading System                │
│                                                       │
│  ┌─────────────┐    ┌──────────────┐   ┌───────────┐ │
│  │  Signal      │    │  Position     │   │  Exit      │ │
│  │  Engine      │───▶│  Manager      │◀──│  Monitor   │ │
│  │  (每小时)     │    │  (持仓管理)    │   │  (每5分钟)  │ │
│  └──────┬──────┘    └──────┬───────┘   └─────┬─────┘ │
│         │                  │                  │       │
│  ┌──────▼──────┐    ┌──────▼───────┐   ┌─────▼─────┐ │
│  │  Binance     │    │  State        │   │  Ledger    │ │
│  │  API         │    │  (JSON)       │   │  (CSV)     │ │
│  └─────────────┘    └──────────────┘   └───────────┘ │
└──────────────────────────────────────────────────────┘
```

### 2.1 三个独立模块

| 模块 | 职责 | 频率 | 实现方式 |
|------|------|------|---------|
| **Signal Engine** | 检测事件 + V4 信号，生成开仓建议 | 每小时整点后 2min | systemd timer |
| **Exit Monitor** | 检查移动止盈，执行平仓 | 每 1 分钟 | systemd timer |
| **Daily Digest** | 汇总日报，发 Telegram | 每天 UTC 00:05 | cron job |

---

## 3. 数据获取方案

### 3.1 实时事件检测（核心创新点）

**关键问题：回测用的是 Binance Vision CSV（离线数据），paper trading 需要实时数据。**

**方案：利用 Binance 公开 API，两个端点组合**

| 端点 | 用途 | 响应 | 速率限制 |
|------|------|------|---------|
| `GET /fapi/v1/ticker/24hr` | 一次拿到所有合约的 24h 涨跌幅 + 成交额 | ~700 行 | 1次/请求，权重 40 |
| `GET /fapi/v1/klines?interval=1h&limit=25` | 获取单个币最近 25 根 1h K 线（用于计算 V4 信号 + 成交量均值） | 25 行 | 每币 1 次 |

**流程：**

```
1. GET /fapi/v1/ticker/24hr → 得到全市场 24h ret + volume
2. 按 24h ret 降序排列 → 计算 rank
3. 筛选 rank ≤ 20 & ret ≥ 30% & vol ≥ $5M → 候选事件
4. 检查冷却期（24h 内同币不重复） → 确认新事件
5. 对新事件标的，GET klines → 检测 V4 信号
6. 如果 V4 触发 → 生成开仓建议
```

**API 调用量估算：**
- ticker/24hr: 1 次/小时，权重 40
- klines: 最多 20 个候选币/小时 × 1 次 = 20 次，权重 1-2
- 总计：~60 权重/小时，远低于 2400/min 限制

### 3.2 价格监控（移动止盈用）

**方案：使用 `/fapi/v1/ticker/bookTicker` 获取可执行 bid/ask**

| 端点 | 用途 | 速率限制 |
|------|------|---------|
| `GET /fapi/v1/ticker/bookTicker?symbol=...` | 获取持仓币 best bid / ask | 低 |

当前实现中，Exit Monitor 每 1 分钟调一次，使用 `bookTicker` 的 bid 作为可执行退出参考价，计算所有持仓的 trailing stop 触发情况，并写入 `monitor_mark_log.csv`。

---

## 4. 信号引擎详细设计

### 4.1 事件检测逻辑

```python
def detect_events(ticker_data: list[dict], state: dict) -> list[Event]:
    """
    ticker_data: Binance /fapi/v1/ticker/24hr 返回值
    state: 持久化状态（含冷却期记录）
    """
    # 1. 过滤掉稳定币、杠杆代币
    symbols = [t for t in ticker_data if is_tradeable_perp(t['symbol'])]
    
    # 2. 按 24h priceChangePercent 排序，计算 rank
    symbols.sort(key=lambda x: float(x['priceChangePercent']), reverse=True)
    for i, s in enumerate(symbols):
        s['rank'] = i + 1
    
    # 3. 筛选事件
    events = []
    for s in symbols:
        ret24 = float(s['priceChangePercent']) / 100  # 百分比→小数
        vol24 = float(s['quoteVolume'])
        if s['rank'] <= 20 and ret24 >= 0.30 and vol24 >= 5_000_000:
            # 4. 冷却期检查
            sym = s['symbol']
            last_event = state.get('last_event', {}).get(sym)
            if last_event and (now - last_event) < timedelta(hours=24):
                continue
            events.append(Event(symbol=sym, ret24=ret24, vol24=vol24, rank=s['rank']))
    return events
```

### 4.2 V4 信号检测逻辑

```python
def detect_v4_signal(symbol: str, klines: list[list]) -> bool:
    """
    klines: Binance /fapi/v1/klines 返回值（最近 25 根 1h K 线）
    检测最新已完成的 1h K 线是否触发 V4 信号
    """
    # klines[-2] 是最新已完成 K 线（[-1] 是当前未完成的）
    # 格式: [open_time, open, high, low, close, volume, close_time, ...]
    bars = klines[:-1]  # 排除未完成的
    if len(bars) < 21:
        return False
    
    latest = bars[-1]
    prev_20 = bars[-21:-1]
    
    close = float(latest[4])
    open_ = float(latest[1])
    vol = float(latest[7])  # quote volume
    
    # 前 20 根已完成 1h K 的平均成交量；实现中使用 quote volume 对齐报告口径
    avg_vol_20 = sum(float(b[7]) for b in prev_20) / 20

    ret = (close - open_) / open_  # 当前 K 线涨幅
    vol_ratio = vol / avg_vol_20 if avg_vol_20 > 0 else 0
    
    return vol_ratio > 3.0 and ret > 0.01
```

### 4.3 V4 信号窗口管理

事件触发后，该币进入"观察窗口"（48 小时），每小时检查一次 V4 信号：

```python
# state 结构
{
    "active_events": {
        "BTCUSDT": {
            "event_ts": "2026-05-13T01:00:00Z",
            "event_ret24": 0.35,
            "expires": "2026-05-15T01:00:00Z"  # 48h 后过期
        },
        ...
    }
}
```

---

## 5. 持仓管理

### 5.1 开仓规则

| 项目 | 规则 |
|------|------|
| 触发条件 | 事件 + V4 信号同时满足 |
| 入场价 | 信号 K 线收盘价（模拟市价单） |
| 入场时间 | 信号 K 线结束后立即（下一个 K 线开盘） |
| Paper 入场价 | `bookTicker` ask，并记录相对信号 close 的滑点 |
| 同币最大持仓 | 1 个（不允许同币加仓） |
| 最大同时持仓 | 5 个 |
| 仓位大小 | 1 个单位（fixed notional，暂定 $25 等值） |

### 5.2 移动止盈（Trailing Stop）逻辑

```
入场价: $100
最高价追踪: max(high_prices_since_entry) — 使用5分钟K线close更新

触发平仓条件:
  最新完成5分钟K线close ≤ 最高价 × (1 - 4%)
  
示例:
  价格涨到 $110 → 止盈线 = $105.60
  5分钟K线close回落到 $105.50 → 触发平仓
  实际利润 = +5.5%（而非回测中的 +10%）
```

**2026-05-14 变更说明：**
- trail_pct 从 2% 调至 4%：原2%在1分钟K线振幅均值151bps的噪音下被频繁洗出
- 判定价格从 tick级bookTicker bid 改为 5分钟K线close：减少噪音敏感性
- 实际退出成交价仍使用 bookTicker bid（模拟真实市价卖出）

**关键设计决策：止盈检查频率**

| 方案 | 优点 | 缺点 |
|------|------|------|
| A: 每 1h（随信号引擎） | 简单，无额外 API 调用 | 可能错过 1h 内的止盈触发 |
| B: 每 1-5min（独立 monitor） | 更接近实际 | 需要额外 systemd timer + API 调用 |
| C: 每 1min（WebSocket） | 最精确 | 复杂度高，维护成本大 |

**实施：方案 B（每 1 分钟）**

理由：
1. 移动止盈的 alpha 来自"截断亏损"，频率太低（1h）会错过很多
2. WebSocket 方案虽然精确但维护成本过高，且 paper trading 不需要毫秒级精度
3. 1 分钟检查一次仍远低于 Binance public API 限制，并能更早暴露止盈、滑点和盘口价差问题

### 5.3 平仓逻辑

```python
def check_trailing_stops(positions: dict, prices_5m: dict, prices_bid: dict) -> list[CloseSignal]:
    closes = []
    for sym, pos in positions.items():
        close_5m = prices_5m[sym]       # 5分钟K线close，用于判定
        bid_price = prices_bid[sym]     # bookTicker bid，用于退出成交
        
        # 更新最高价（用5分钟close）
        if close_5m > pos['high_water_mark']:
            pos['high_water_mark'] = close_5m
        
        # 检查止盈触发（用5分钟close判定）
        trail_price = pos['high_water_mark'] * (1 - 0.04)  # 4% trailing
        if close_5m <= trail_price:
            closes.append(CloseSignal(
                symbol=sym,
                exit_price=bid_price,           # 实际退出用bid
                trail_trigger_price=trail_price,
                high_water_mark=pos['high_water_mark'],
                trigger_close_5m=close_5m       # 记录触发时的5分钟close
            ))
    return closes
```

### 5.4 强制平仓（Hard Timeout）

回测中没有 hard timeout，但 paper trading 建议加上：

| 规则 | 值 | 理由 |
|------|-----|------|
| 最大持仓时间 | 72 小时 | 防止僵尸持仓；回测显示多数交易在 24h 内已止盈 |
| 触发方式 | Exit Monitor 检查 | 到期后按当前价平仓 |

---

## 6. 状态持久化

### 6.1 文件结构

```
reports/artifacts/paper_phase2a_event_v4_trail/
├── state.json                  # 核心状态（持仓、事件、冷却期）
├── ledger.csv                  # 所有已平仓交易记录
├── open_positions.csv          # 当前持仓（每次刷新重写）
├── event_log.csv               # 事件检测日志
├── signal_log.csv              # V4 信号检测日志
├── daily_digest.json           # 日报数据
└── slippage_audit.csv          # 滑点审计记录
```

### 6.2 state.json 结构

```json
{
    "last_run_ts": "2026-05-13T01:02:00Z",
    "active_events": {
        "BTCUSDT": {
            "event_ts": "2026-05-13T01:00:00Z",
            "event_ret24": 0.35,
            "event_rank": 3,
            "event_vol24": 125000000,
            "expires": "2026-05-15T01:00:00Z"
        }
    },
    "open_positions": {
        "ETHUSDT": {
            "entry_ts": "2026-05-13T02:00:00Z",
            "entry_price": 3250.50,
            "event_ts": "2026-05-13T01:00:00Z",
            "signal_price": 3250.50,
            "high_water_mark": 3280.00,
            "notional": 25,
            "expires": "2026-05-16T02:00:00Z"
        }
    },
    "cooldowns": {
        "BTCUSDT": "2026-05-13T01:00:00Z"
    },
    "cumulative_stats": {
        "total_trades": 0,
        "total_pnl_pct": 0.0,
        "win_count": 0,
        "loss_count": 0
    }
}
```

### 6.3 ledger.csv 列定义

| 列名 | 含义 |
|------|------|
| `trade_id` | 唯一 ID（`{symbol}_{entry_ts}`) |
| `symbol` | 交易对 |
| `direction` | LONG |
| `event_ts` | 事件触发时间 |
| `event_ret24` | 事件时 24h 涨幅 |
| `event_rank` | 事件时排名 |
| `signal_ts` | V4 信号触发时间 |
| `entry_ts` | 实际入场时间 |
| `entry_price` | 入场价（信号 K 线收盘价） |
| `exit_ts` | 出场时间 |
| `exit_price` | 出场价 |
| `exit_reason` | `trailing_stop` / `hard_timeout` |
| `high_water_mark` | 持仓期间最高价 |
| `gross_pnl_pct` | 毛利润 % |
| `cost_bps` | 假设单边成本 (bps) |
| `net_pnl_pct` | 扣费后净利润 % |
| `hold_hours` | 持仓时长 |

---

## 7. 滑点与执行审计

### 7.1 Paper Trading 中的"滑点"含义

Paper trading 不实际执行，所以"滑点"需要模拟或测量：

| 层次 | 方法 | 目的 |
|------|------|------|
| **信号价 vs 市场价** | 信号 K 线收盘后，记录 `close` 和下一根 K 线的 `open` | 测量"收盘到开盘"的跳空 |
| **理论价 vs 等待价** | 记录信号触发时刻和 Exit Monitor 检查时刻的价格差 | 测量检查频率带来的成本 |
| **固定成本假设** | 每笔交易扣 30bps（单边 15bps） | 对标回测的滑点敏感性 |

### 7.2 滑点审计字段

```python
# 开仓时记录
slippage_entry = {
    "signal_close_price": 3250.50,     # 信号 K 线收盘价
    "next_open_price": 3251.00,        # 下一根 K 线开盘价（假设"入场价"）
    "gap_bps": (3251.00 - 3250.50) / 3250.50 * 10000,  # 1.5 bps
    "signal_ts": "2026-05-13T01:00:00Z",
    "monitor_ts": "2026-05-13T01:05:00Z",  # 下次检查时的价格
}

# 平仓时记录
slippage_exit = {
    "trail_trigger_price": 3315.50,    # 移动止盈触发价
    "monitor_detect_price": 3314.00,   # Exit Monitor 检测到的价格
    "slippage_bps": (3315.50 - 3314.00) / 3315.50 * 10000,  # 4.5 bps
}
```

### 7.3 累积滑点监控

日报中会包含：
- 近 7 天平均入场滑点 (bps)
- 近 7 天平均出场滑点 (bps)
- 与回测假设（30bps）的对比
- 滑点是否吃掉了 alpha 的警告

---

## 8. Cron / Timer 设计

### 8.1 Signal Engine Timer

```ini
# /etc/systemd/system/momentum-phase2a-event-v4-trail-scan.timer
[Unit]
Description=Run Phase2a Event+V4 Trail Paper Scan after each hourly close

[Timer]
OnCalendar=*-*-* *:02:15
Persistent=true

[Install]
WantedBy=timers.target
```

```ini
# /etc/systemd/system/momentum-phase2a-event-v4-trail-scan.service
[Unit]
Description=Phase2a Event+V4 Trail Paper Scan

[Service]
Type=oneshot
WorkingDirectory=/root/clawd/jerry/momentum
ExecStart=/root/clawd/jerry/momentum/.venv/bin/python /root/clawd/jerry/momentum/scripts/run_phase2a_event_v4_trail_paper.py --scan
```

### 8.2 Exit Monitor Timer

```ini
# /etc/systemd/system/momentum-phase2a-event-v4-trail-monitor.timer
[Unit]
Description=Run Phase2a Event+V4 Trail Paper Exit Monitor every minute

[Timer]
OnCalendar=*-*-* *:*:20
Persistent=true

[Install]
WantedBy=timers.target
```

### 8.3 Daily Digest Cron

```bash
# 每天 UTC 00:05 发送日报到 Telegram
5 0 * * * /root/clawd/jerry/momentum/.venv/bin/python3 /root/clawd/jerry/momentum/scripts/run_phase2a_daily_digest.py
```

---

## 9. 已知风险与局限性

### 9.1 Paper Trading 无法完美模拟的环节

| 环节 | 回测假设 | 现实差异 | 影响程度 |
|------|---------|---------|---------|
| **入场执行** | 信号 K 线 close 价成交 | Paper 使用 `bookTicker` ask 模拟市价买入 | 中（记录滑点） |
| **移动止盈精度** | 回测按历史路径近似 | Paper 每 1min 用 `bookTicker` bid 检查一次 | 低到中（记录 mark log） |
| **流动性** | 无限深度 | 大单可能有 market impact | 低（$1000 小单） |
| **API 延迟** | 即时 | 网络延迟 + 处理时间 | 低（1min 监控频率内） |

### 9.2 数据依赖风险

| 风险 | 描述 | 缓解措施 |
|------|------|---------|
| Binance API 限速 | 692 币的 klines 可能超限 | 只对候选事件币（最多 20 个）查 klines |
| API 宕机 | 维护期无法获取数据 | 记录失败，不产生虚假信号 |
| 交易对下架 | 新币可能被下架 | 检查 `/fapi/v1/exchangeInfo`，过滤 inactive |

### 9.3 策略本身的风险

| 风险 | 描述 | 缓解措施 |
|------|------|---------|
| **样本量不足** | 回测中 ~200 笔/year | 需要 6-12 个月 paper 才能有统计意义 |
| **市场环境变化** | 牛市 → 熊市，事件频率和 alpha 可能改变 | 日报中监控事件频率 |
| **alpha 衰减** | 更多人发现类似模式 | 长期监控 PF 和 winrate 趋势 |

---

## 10. 实施步骤（确认后执行）

### Phase 0: 基础设施（Day 1）

1. 创建目录结构 `reports/artifacts/paper_phase2a_event_v4_trail/`
2. 编写 `scripts/phase2a_signal_engine.py` — 信号引擎主脚本
3. 编写 `scripts/phase2a_exit_monitor.py` — 止盈监控脚本
4. 编写 `scripts/phase2a_daily_digest.py` — 日报生成脚本
5. 创建 systemd timer × 2 + service × 2
6. 端到端 dry-run 测试（获取真实 API 数据，验证信号检测逻辑）

### Phase 1: 首周观察（Week 1）

7. 启动 paper trading，记录首周所有信号和持仓
8. 每天检查日报，确认无 bug
9. 对比"如果按回测规则执行"和"实际 paper 结果"的差异

### Phase 2: 滑点审计（Week 2-4）

10. 积累足够样本后，分析实际滑点分布
11. 与回测的 30bps 假设对比
12. 如果滑点显著高于 30bps，考虑调整策略或放弃

### Phase 3: 决策点（Month 2-3）

13. 积累 ~50+ 笔交易后，计算实际 PF、winrate、median
14. 与回测结果对比（预期：PF 可能低于 4.34，但仍应 >1.5）
15. 决定是否进入实盘

---

## 11. 开放问题（需要 Jerry 决定）

1. **仓位大小**：当前为每笔 $1,000 notional，后续是否按风险预算动态调整？
2. **最大同时持仓**：当前为 5 个，是否需要按市场波动或相关性动态收缩？
3. **Hard timeout**：当前 72 小时，是否需要针对不同事件 rank/ret 分层？
4. **Telegram 通知**：开仓/平仓时是否即时通知？还是只在日报中汇总？
5. **Paper vs backtest 偏差阈值**：累计多少笔后触发复盘？建议 30 笔初筛、50 笔正式评估。

---

## 变更日志

详见 `docs/PHASE2A_CHANGELOG.md`。每次参数/逻辑变更必须在该文件中记录，供回测同步参考。

---

> **下一步：持续观察 paper/shadow 审计面板；累计样本后对照 Phase2a 回测口径做正式质量复盘。**
