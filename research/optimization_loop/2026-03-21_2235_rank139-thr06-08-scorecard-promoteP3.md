# bot3 optimization loop — Rank139 thr_mult(0.6 vs 0.8) + scorecard → promote_P3 (2026-03-21 22:35 UTC)

## Context / Command board anchor
- Source: `jerry/momentum/docs/TODO.md` 顶部 **TRADING DESK BOARD（authoritative，2026-03-21）**
- 本轮按 `Next 3 bot3 runs`：Run1 → Run2 → Run3

---

## Run 1 — EMA due-check first（Paper Seat）
结论：**无 due-now / overdue**，因此合法切去 Scout Seat。

```
[ema-refresh-guard] fast-precheck：所有 lane 的 next_expected_close_utc 仍在未来，跳过本轮 full rebuild。
[ema-refresh-history] fast-precheck 已跳过 history 追加；下一根 completed bar 到来前，ema_paper_trading_refresh_history.csv 不会出现新 rows。
[ema-refresh-guard] 当前没有 due-now / overdue lane。最靠前的 lane 如下：
- Crypto 1d+1wk（BTC/ETH/SOL） | waiting_not_due | 约 1.4 小时 后到点
...
[ema-refresh-guard] require-due 已开启：当前仍应等待下一根 completed bar，而不是伪造 refresh。
```

---

## Run 2 — Scout Seat / Rank139：固定 baseline + thr_mult {0.6, 0.8} 对比
### 产物落点
- Artifact：`reports/artifacts/scout_rank139_cusum_event_bar_confirm_veto_15m/summary_by_arm.csv`
- Page：`reports/site/factors/scout_rank139_cusum_event_bar_confirm_veto_15m/report.html`

### 关键读数（BTC/ETH/SOL 15m, net@6bps）
从 `summary_by_arm.csv` 摘要：

- baseline（无 confirm/veto）：
  - mean_net@6bps = **-0.1548%**（负）

- thr_mult=0.6：
  - confirm_same_dir_only：trades=52，retention=0.3688，mean_net@6bps=**+0.1909%**，positive_ratio_net=0.50
  - veto_opp_dir：trades=66，retention=0.4681，mean_net@6bps=**+0.1957%**，positive_ratio_net=0.4848

- thr_mult=0.8：
  - confirm_same_dir_only：trades=43，retention=0.3050，mean_net@6bps=**+0.5363%**，positive_ratio_net=0.6047
  - veto_opp_dir：trades=70，retention=0.4965，mean_net@6bps=**+0.3423%**，positive_ratio_net=0.5143

### 对比结论（只为升格决策服务）
- **0.6 vs 0.8**：
  - 0.6：更高 retention，较温和 uplift；
  - 0.8：retention 更低，但 uplift 更强（confirm 同向尤其明显）。
- baseline 本身是负的，而 confirm/veto 变体能把 net 拉正 → Rank139 更像一个 **post-entry 的 event-confirm/veto layer**（适配多条主策略），而不是独立 alpha。

---

## Run 3 — 硬结论分支：promote_P3（narrow paper pilot）
### Hard verdict
- **promote_P3（进入 narrow paper pilot）**
- 但先限定成“最小接线 + 最小监控”，不做扩展宇宙/扩参数。

### Minimal P3 spec（仅 1 页、可执行）
**定位**：Rank139 = post-entry 事件确认/否决层（confirm/veto overlay），用于提升基线策略的净收益质量。

**Frozen choices（先冻结）**
- Universe：BTC/ETH/SOL perp/spot 统一口径（沿用当前 clean replication 数据源口径）
- Bar：15m
- Arms（只保留 2 条，不再扩）：
  1) `confirm_same_dir_only @ thr_mult=0.8`（强 uplift 版本）
  2) `confirm_same_dir_only @ thr_mult=0.6`（更稳 retention 版本）
- Cost：6bps（对齐现有报表口径）

**Trade-on / Trade-off（最小诚实检查，P3 必做）**
- 规则：只允许用 **entry 之后** 的事件做 confirm/veto；所有特征计算必须以 `t_entry` 之后的 bar 为起点（严禁偷看未来 bar close）。
- 监控：
  - 每次 refresh 输出：retention、mean_net@6bps、positive_ratio_net、same_dir_first / opp_dir_first / timeout 结构占比。

**Promotion Scorecard（5项 0~3 分 + hard-fail）**
- 1) 方向一致性（事件语义是否稳定、能解释）：**2/3**
- 2) 成本后仍为正（net@6bps）：**3/3**（thr 0.6 / 0.8 均为正）
- 3) 留存（retention 是否过低）：**1/3**（0.8 约 0.305 偏低；0.6 约 0.369 勉强）
- 4) 可移植性（作为 overlay 能否跨 baseline）：**2/3**（机制上像 shared layer，但需在至少 1 条 baseline 上小样本验证）
- 5) 实盘可监控性（指标是否清晰、能做红灯）：**2/3**

Hard-fail flags（当前未触发，但 P3 必须持续守）
- leakage / 使用 entry 前信息（任何证据出现立刻 park）
- uplift 仅在单一 pocket、且一旦更换月份/成本就塌陷（触发则降级回 P2）

### 下一步（只列 1 个）
- **把 Rank139 挂进 narrow paper lane（P3）做 1 次最小 refresh 验证**：只跑 BTC/ETH/SOL、只对比 thr 0.6 vs 0.8 的 confirm_same_dir_only，两次 refresh 内若无稳定 uplift → 回退 keep_P2/park。

---

## Notes
- 本轮严格不展开新 Scout 候选；只推进 Rank139。
