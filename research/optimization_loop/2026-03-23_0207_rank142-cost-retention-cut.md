# 2026-03-23 02:07 UTC — Rank 142 / hammer-engulf retest quality gate / 15m 成本-留存诚实检查

- 严格遵循：`docs/TODO.md` 顶部 `TRADING DESK BOARD` + `docs/AUTO_OPTIMIZATION_LOOP.md`
- 本轮类型：`Scout / P1 一次便宜诚实检查`
- 范围控制：仅 **1 个主点（Rank 142）** + **1 个紧邻子点（无；只对同一 family 做最小三臂成本检查）**。

## 0. 先判 interrupt
按顶板要求，本轮先检查是否出现真实 interrupt：
- `Paper / 正在自动运行` runner 顶板未写入新的 `stale / error / refresh 失步 / ledger 爆雷 / open-position 异常 / red-watch`
- `tiny-live / live-shadow plumbing` 顶板未写入新的 blocking anomaly

因此本轮不抢占默认队列，继续执行 `Run 1`：在 `Rank 142 / Rank 125 / Rank 112 / Rank 111` 中重新选边际价值最高者。

## 1. 为什么这轮继续给 Rank 142 那唯一一刀
对比当前 active set：
- `Rank 125`：已有 `clean replication + cost_trade_stability + explicit three-arm`，读法稳定在 `keep_P1 / budget used`
- `Rank 112`：核心问题仍是 `kept:veto` 极度失衡，若不重写 family 定义，再补一刀边际低
- `Rank 111`：已有显式三臂与替代 strict arm，结论仍停在“有点区分度、但不够稳”
- `Rank 142`：仍处在 `fresh intake` 之后、且顶板明示只允许再给 **1 次便宜诚实检查** 的阶段

因此这轮最有杠杆的动作仍是：
**把 `Rank 142` 从“故事上像 long-side quality gate”推进到“成本后是否还值得继续留在 active Scout”**。

## 2. 本轮最小检查设计
不做 5m execution，不扩成完整回测；只做 intake 文档里授权的最小三臂 / 四臂成本检查：
- `long / base_retest`
- `long / pattern_gate`（`hammer OR engulf`）
- `short / base_retest`
- `short / engulf_only`

统一口径：
- 样本：`Binance Futures BTC/ETH/SOL 最近 120d / 15m`
- 入场：`next-bar open`
- 判决：`+1.5 ATR / -1 ATR / 8 bars first-hit`
- 成本：`6 / 10 / 15 bps per side`
- 重点读法：`post-cost avg_pnl_r`、`trade retention`

产物：
- `reports/artifacts/scout_rank142_hammer_engulf_retest_15m/event_log.csv`
- `reports/artifacts/scout_rank142_hammer_engulf_retest_15m/cost_summary.csv`
- `reports/artifacts/scout_rank142_hammer_engulf_retest_15m/retention_by_asset.csv`
- `reports/artifacts/scout_rank142_hammer_engulf_retest_15m/arm_delta_summary.csv`
- `reports/artifacts/scout_rank142_hammer_engulf_retest_15m/meta.json`

## 3. 核心结果
### 3.1 long 侧：pattern gate 确实更像“少做但更干净”
`BTC/ETH/SOL` 合并后：
- `long / base_retest`：`306` 笔
- `long / pattern_gate`：`102` 笔
- `trade_retention = 33.33%`

净 `avg_pnl_r`（每边成本）：
- `6bps`：`-0.3500 -> -0.2587`（改善 `+0.0913R`）
- `10bps`：`-0.6047 -> -0.4929`（改善 `+0.1118R`）
- `15bps`：`-0.9230 -> -0.7856`（改善 `+0.1374R`）

解释：
- 它确实在做“留下更干净的 long retest”这件事；
- 但 **成本后仍整体为负**，还没到能往 `P2` 或 `P3` 误读的地步。

### 3.2 short 侧：只留 bearish engulf 也只是“少亏”，不是正 edge
`BTC/ETH/SOL` 合并后：
- `short / base_retest`：`368` 笔
- `short / engulf_only`：`108` 笔
- `trade_retention = 29.35%`

净 `avg_pnl_r`（每边成本）：
- `6bps`：`-0.4538 -> -0.3701`（改善 `+0.0837R`）
- `10bps`：`-0.6750 -> -0.5916`（改善 `+0.0834R`）
- `15bps`：`-0.9516 -> -0.8686`（改善 `+0.0830R`）

解释：
- `short_engulf_only` 比先前“把倒锤也混进去”诚实得多；
- 但它本质仍是 **减少伤害**，不是产生可部署 short gate 的充分证据。

### 3.3 本轮真正改变了什么读法
本轮最重要的变化不是“Rank 142 变强了”，而是把它从 intake 叙事推进到一个更硬的边界：

> **Rank 142 的正确读法现在更明确了：它是一个“能改善口袋质量，但不足以穿越成本”的 long-side selective filter。**

也就是说：
- 它不是 shared gate
- 它不是 pre-paper candidate
- 它暂时也不是值得继续吃第 2 刀预算的 `P1`

## 4. Lightweight scorecard
- `usefulness`: **medium** — 解决了“它到底只是故事，还是成本后仍有一点筛选价值”的问题
- `time_stability`: **unknown-weak** — 仍只有 `120d / 15m`，未过滚动窗口
- `cross_asset_stability`: **weak-medium** — 不是全币种统一强；仍偏 ETH/SOL 驱动
- `cost_trade_stability`: **weak** — 所有成本层净值仍为负，虽然 long/short 都比 base 改善
- `deployability`: **low** — 适合当研究层的条件过滤想法，不适合送 paper
- `hard-fail flags`:
  - `post_cost_negative_all_arms`
  - `retention_below_35pct`
  - `not_shared`
  - `short_side_not_independent_edge`
- `recommended_action = park`
- `why_now`: 这是 Rank 142 在 desk 规则下唯一还值得做的一刀；做完后就能诚实决定是否继续占 active Scout 资源
- `main_weakness`: 改善幅度存在，但无法穿越成本，且 trade retention 偏低

## 5. 结论（authoritative for this run）
**`Rank 142 / hammer-engulf retest quality gate = park`**。

不是因为它完全没用，而是因为：
1. 它只证明了“少做一些会更少亏”；
2. 没证明“成本后仍有独立可部署 pocket”；
3. 在当前 desk 资源约束下，不该继续吃第 2 刀预算。

因此，本轮后它应从：
- `P1 / fresh intake / active compare admitted`

更新为：
- `P0 / park / evidence only`

## 6. 对顶板的最小写回建议
只做最小局部修改即可：
1. 把 `Rank 142` 从 active compare 移到 `park / evidence only`
2. 在 `最近关键 evidence` 增加本轮一句话：
   - `15m` 成本-留存检查显示 long/short 都只是“少亏”，成本后仍无正 pocket，因此 `Rank 142 = park`
3. `Next 3` 不再把 `Rank 142` 当默认优先比较对象；下一轮回到 `Rank 125 / 112 / 111` 与后续 fresh reserve 的再比较

## 7. 本轮未做的事
- 未碰任何健康 autonomous paper runner
- 未做 `EMA` routine due-check
- 未扩成 `5m execution` 或完整 walk-forward
- 未把结果误写成 `promote_P2/P3`
