# 2026-03-20 13:29 UTC · Rank 122 clean replication → P2 / paper candidate

## 本轮一句话
这轮按 desk 排班先确认 `EMA = waiting_not_due`，随后只认领 **`Rank 122 / ATR compression + ROC ignition short re-arm gate`** 的 **1 次最小 clean replication**，并顺手补了 1 个真正会改变级别判断的最小 `Light Stability Pack` 项（**成本 / 交易数稳定性**）。当前 authoritative hard verdict：**`Rank 122 = P2 / paper candidate`**，但只限 **`strict-only short-side re-arm`**；`mild` 版本不成立，当前仍**不**支持 shared 到 `Fib retest_hold / EMA long`，也**不**支持抢 `Live Seat`。

## 先检查了什么
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 结果：继续 `waiting_not_due`
  - 最近 due 仍约为：`美股 1d+1wk -> 6.5h`、`Crypto 1d+1wk -> 10.5h`、`创业板ETF 1d -> 65.5h`
- repo status：工作区仍很脏，且存在大量与本轮无关的脏文件；本轮不做混提，只落最小必要文件
- 当前顶板：`13:04 UTC` 已把 `Rank 122` 冻结为 `guard-passed / clean replication next`

## 本轮主动作
### 1) 最小 clean-room
固定复用本地 cache：`BTC/ETH/SOL 120d 15m`

统一执行口径：
- `signal 当根及之前数据`
- `next-bar open`
- `no-overlap`
- `hold 4 bars`

比较三臂：
1. `baseline_short = close < prior 20-bar low`
2. `strict_short_rearm = baseline + ATR14/avgATR20 < 0.7 + ROC5 < -0.5%`
3. `mild_short_rearm = baseline + min ATR ratio(last4) < 0.8 + ROC5 < -0.4%`

### 2) 最小 stability 项
只补一个真正改变 dispatch 的检查：
- **成本 / 交易数稳定性**：`6 / 10 / 15 bps per side`

## 结果（核心数字）
### 6 bps / side
- `baseline_short`：`n=890 / mean_net_bps=-7.84 / reentry4=75.84%`
- `mild_short_rearm`：`n=178 / mean_net_bps=-8.58 / reentry4=70.22%`
- `strict_short_rearm`：`n=29 / mean_net_bps=+22.74 / reentry4=65.52%`

### strict 的成本稳定性
- `10 bps / side`：`+14.71 bps`
- `15 bps / side`：`+4.69 bps`

### 6 bps / side 分资产（strict vs baseline）
- `BTC`：`-10.57 -> -3.70 bps`
- `ETH`：`-13.27 -> +0.71 bps`
- `SOL`：`-0.27 -> +56.51 bps`

### 关键读法
- `strict` 版不是只靠 aggregate 假象：相对 baseline，三币都保留了方向一致的 uplift；因此它不该继续留在 `P1 weak candidate`
- 但 `mild` 三币全部成本后仍为负，说明**一旦放宽阈值，这条线并没有形成可 shared 的更诚实版本**
- `strict` 的 `trade retention` 只剩 `3.26%`，说明它当前更像 **高门槛 / 窄口径 short-side re-arm**，不是可广泛部署的 shared gate

## authoritative verdict
**`Rank 122 = P2 / paper candidate`**

翻成人话：
- 可以继续推进，但只配以 **`strict-only narrow paper candidate`** 的身份推进
- 当前还**不能**写成 shared gate
- 当前还**不能**升级为 `Live Seat`
- 下一轮如果继续认领它，默认只配拿 **1 个 truly verdict-changing 的最小时间稳定性检查**；若没爆雷，再给 `P3 / narrow paper pilot` or `park` 的升降级判断

## 本轮产物
### 脚本
- `scripts/build_rank122_atr_roc_rearm_clean_replication.py`

### artifacts
- `reports/artifacts/scout_rank122_atr_roc_short_rearm_15m/overall_summary.csv`
- `reports/artifacts/scout_rank122_atr_roc_short_rearm_15m/asset_summary.csv`
- `reports/artifacts/scout_rank122_atr_roc_short_rearm_15m/trade_log.csv`
- `reports/artifacts/scout_rank122_atr_roc_short_rearm_15m/summary.json`

### reader-facing
- `reports/site/factors/scout_rank122_atr_roc_short_rearm_15m/report.html`
- `reports/site/reading/repo_scout/rank122_atr_roc_short_rearm_clean_replication.html`

## 本轮对 desk board 的写回
已把顶板同步更新为：
- `Rank 122` 从 `P1 / clean replication next` 升到 **`P2 / paper candidate / strict-only narrow candidate`**
- `Next 3` 改为：
  1. `Run 1 = EMA due-check first`
  2. `Run 2 = Rank 122 最小时间稳定性检查`
  3. `Run 3 = 若时间稳定性不过度爆雷，则给出 P3 / park；否则 park + 回 fresh intake`

## 验证
- 已执行并通过：`python3 scripts/build_rank122_atr_roc_rearm_clean_replication.py`
- 已确认输出文件存在：
  - `reports/site/factors/scout_rank122_atr_roc_short_rearm_15m/report.html`
  - `reports/site/reading/repo_scout/rank122_atr_roc_short_rearm_clean_replication.html`
  - `reports/artifacts/scout_rank122_atr_roc_short_rearm_15m/overall_summary.csv`

## 风险 / 保留意见
- 当前 uplift 明显仍带 `strict-only / 极低留存` 属性，不能把它误读成 broad short filter
- `SOL` 的 uplift 最强，说明后续时间稳定性 / regime 稳定性一旦爆雷，应优先直接 `park`
- 这轮没有把 long 侧重新拉回台面；当前 long 侧仍默认视为**不支持**

## 与本轮无关的脏文件
repo 里有大量既有 dirty files；本轮未触碰它们，也不混提。
