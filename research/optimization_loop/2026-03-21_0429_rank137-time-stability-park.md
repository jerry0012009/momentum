# 2026-03-21 04:29 UTC — Rank 137 时间稳定性最小裁决：park

## 本轮一句话
先按 desk 规则做 `EMA due-check first`；结果仍是 `waiting_not_due`，因此本轮合法切到 `Scout Seat`，把 **Rank 137 / state expiry latency budget gate** 的唯一剩余最小检查（`confirm_window_12` 时间稳定性）跑完并落板。硬结论：**`park`，下一轮回 fresh intake。**

## 先检查了什么
- `git status --short`
  - repo 仍有大量与本轮无关脏文件，继续 **不混提**。
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 返回口径：当前没有 `due-now / overdue` lane；最靠前仍是 `Crypto 1d+1wk（BTC/ETH/SOL）`，约 `19.5h` 后到点。
  - 该命令在 `require-due` 下以非零码退出属于预期的“当前不该 refresh”信号，不是运行错误。
  - 含义：`EMA` 继续 `running paper / waiting_not_due`，所以本轮主资源位应切去 `Scout Seat`，不能空转。

## 本轮主点
### 认领对象
- `Rank 137 / state expiry latency budget gate`
- 当前层级：`P1`
- 本轮允许动作：**只做 1 个最小 stability-style verdict check**

### 为什么还是它
- 顶板 `Next 3 bot3 runs` 明确写的是：若 `EMA` 仍 `waiting_not_due`，就先把 `Rank 137` 的最小 stability verdict 补完。
- 这条线已经完成 clean replication，继续补 intake / wording 没价值；真正会改变 verdict 的只剩这 1 手。

## 做了什么
执行：
- `python3 scripts/build_rank137_time_stability_verdict.py`

该脚本只检查 `confirm_window_12`，不重开大研究：
- 样本：`BTC / ETH / SOL perpetual`，`15m`，`test split`
- 切法：按时间顺序分成 `early / mid / late` 三桶
- 成本：`6 / 10 / 15 bps per side`
- 对照：`baseline_no_expiry`

并同步产出：
- `reports/artifacts/scout_rank137_state_expiry_latency_budget_15m/time_stability_bucket_summary.csv`
- `reports/artifacts/scout_rank137_state_expiry_latency_budget_15m/time_stability_asset_summary.csv`
- `reports/artifacts/scout_rank137_state_expiry_latency_budget_15m/time_stability_setup_summary.csv`
- `reports/artifacts/scout_rank137_state_expiry_latency_budget_15m/time_stability_scorecard.csv`
- `reports/artifacts/scout_rank137_state_expiry_latency_budget_15m/time_stability_summary.json`
- `reports/site/factors/scout_rank137_state_expiry_latency_budget_15m/time_stability_verdict.html`
- `reports/site/reading/repo_scout/rank137_state_expiry_latency_budget_time_stability.html`

## 最关键结果
### 时间稳定性三桶（`confirm_window_12`）
#### 6bps
- `early`：`-6.13 bps/trade`
- `mid`：`+27.51 bps/trade`
- `late`：`-19.79 bps/trade`

#### 10bps
- `early`：`-14.13 bps/trade`
- `mid`：`+19.49 bps/trade`
- `late`：`-27.78 bps/trade`

#### 15bps
- `early`：`-24.13 bps/trade`
- `mid`：`+9.46 bps/trade`
- `late`：`-37.76 bps/trade`

### 读法
- 三个成本层里都只有 `mid` 时间桶为正；`early / late` 一直是负。
- 这说明 uplift 不是稳定分布在时间轴上，而是明显依赖单一 pocket。
- 失败率虽然继续下降，但收益改善并没有形成可推广的 desk 级 shared gate。

### 资产广度补充（6bps）
- `mid` 桶里 `BTC / ETH / SOL` 三资产都转正。
- 但 `early` 与 `late` 各只剩 `1` 个正资产，广度也没跨桶站稳。

## 轻量 Scorecard（本轮新增）
- `usefulness = 1`
- `time_stability = 1`
- `cross_asset_stability = 1`
- `cost_trade_stability = 1`
- `deployability = 0`
- `hard_fail_flags = single_pocket_dependency, post_cost_collapse`
- `recommended_action = park`
- `why_now = 最小时间稳定性裁决已经足够回答“该不该继续给预算”`
- `main_weakness = 只有中段时间桶转正，early/late 继续为负`

## 当前硬结论
**`Rank 137 / state expiry latency budget gate = park（P0）`**

原因：
1. clean replication 证明它不是空故事；
2. 但最小时间稳定性裁决显示，改善主要集中在单一时间 pocket；
3. 成本抬到 `10 / 15bps` 后，依旧没有跨桶稳住；
4. 因此不值得继续占用 `P1/P2` 预算，更不该继续讲故事式打磨。

## 对交易台指挥板的最小 write-back
已更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`：
- `Scout Seat 当前主点` 改成 `fresh intake next`
- `Rank 137` 从主资源位移到 `P0 / park`
- `Next 3 bot3 runs` 改成：`EMA due-check -> fresh intake next -> exhausted 时才 tiny-live fallback`
- `最近关键 evidence` 补入本轮 `park` 裁决

## 网页可见落点
- 因子页：`reports/site/factors/scout_rank137_state_expiry_latency_budget_15m/time_stability_verdict.html`
- 阅读页：`reports/site/reading/repo_scout/rank137_state_expiry_latency_budget_time_stability.html`
- 指挥板镜像：`docs/TODO.md`（后续由首页 index / site mirror 显示最新状态）

## 最小验证
已实际执行：
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- `python3 scripts/build_rank137_time_stability_verdict.py`

## 风险 / 边界
- 本轮没有做 fresh intake；这是刻意遵守顶板顺序，先把 `Rank 137` 的最后一手 verdict check 收口。
- `park` 不等于永远删除，而是按当前 desk 预算口径，不再继续给这条线主资源位。
- 若以后出现更强外部证据，可作为新 rank / 新 framing 重新进入，而不是继续沿用当前 shared-gate 叙事硬撑。

## 下一步建议
1. 下一轮若 `EMA` 仍 `waiting_not_due`，直接回 `fresh intake next`。
2. fresh intake 默认只认领 `paper / repo based 5m/15m crypto` 的 1 条新候选。
3. 只有 fresh intake 也真实 exhausted，才允许切到 `tiny-live plumbing` fallback。

## Commit hash
- 未提交。
- 原因：工作区存在大量与本轮无关脏文件；本轮只做局部 verdict artifact、reader-facing 页面与 desk board write-back，不适合混提。
