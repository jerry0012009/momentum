# Rank 71 / EMA-VWAP-ATR-volume graded admission score minimal clean replication（park）

## 轮次定位
- 时间：2026-03-18 23:45 UTC
- 席位：`Scout Seat`
- 本轮主点：`Run 2 / Rank 71 minimal clean replication`
- 紧邻子点：`TODO 顶板顺序刷新`

## 开始前检查
- `Run 1 / EMA due-check`：`reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 仍无新的 `due-now / overdue` lane；最早仍是 `Crypto 1d+1wk -> 2026-03-19 00:00 UTC / due_soon`。
- `P3 continuity`：`reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json` 最新一次仍是 `new_closed_trades_appended=0`，没有新的 status-changing event。
- 上一轮 `Rank 71` 已完成 source intake + 两条轻量诚实守门，并被顶板明确写成 `guard-passed / admit_to_clean_replication_queue`；因此这轮合法主动作不是继续磨 wording，也不是回头挤占 `P3 continuity`，而是把它允许的那一手最小 clean replication 跑完。
- git 工作区仍有大量与本轮无关的脏文件 / 未跟踪文件；本轮只新增 `Rank 71` clean replication 对应脚本、artifact、reader-facing 页面、TODO 写回与本轮日志，不做混提。

## 这轮实际做了什么
### 1. 新增最小 clean replication 脚本
- 脚本：`scripts/build_rank71_ema_vwap_atr_volume_score_clean_replication.py`
- 固定复用本地 `BTC/ETH/SOL 120d 15m` cache，不追新 bar，不做额外下载。
- 只接现成 `EMA / PSAR raw lane`，不把 score 偷渡成新的独立策略。
- 统一执行口径：`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`。

### 2. 冻结的三臂对照
- `baseline`：现成 `EMA / PSAR raw lane`
- `score>=60`：保留原 lane，只在原信号上叠 `trend_pass + admission_score>=60`
- `score>=75`：同上，但提高到 `>=75`

### 3. 冻结的 graded score 定义
四块各 `25` 分，总分 `0~100`：
- `EMA spread / ATR`
- `price-VWAP distance / ATR`
- `volume > SMA20`
- `ATR14 > ATR14-MA14`

换成人话：不是改 entry，而是问“这笔 continuation 到底有多像样”。

### 4. 产出 reader-facing / artifact
- 因子页：`reports/site/factors/scout_rank71_ema_vwap_atr_volume_score_15m/report.html`
- 阅读页：`reports/site/reading/repo_scout/rank71_ema_vwap_atr_volume_score_clean_replication.html`
- 关键 artifact：
  - `reports/artifacts/scout_rank71_ema_vwap_atr_volume_score_15m/overall_summary.csv`
  - `reports/artifacts/scout_rank71_ema_vwap_atr_volume_score_15m/bucket_summary.csv`
  - `reports/artifacts/scout_rank71_ema_vwap_atr_volume_score_15m/component_summary.csv`
  - `reports/artifacts/scout_rank71_ema_vwap_atr_volume_score_15m/trade_log.csv`

### 5. 写回 queue-facing 顺序
- `docs/TODO.md` 顶板已写入 `2026-03-18 23:45 UTC` 最新块。
- `Rank 71` 这轮已消耗完允许的那次 minimal clean replication，因此顺序重置为：
  - `Run 1 = EMA due-check only`
  - `Run 2 = fresh source 比较 realized-vol mid-band cost-survival gate > PSAR close-confirmed follow-up gate`
  - `Run 3 = 若新的 fresh source 已 guard-passed，则给它 1 次最小 clean replication；否则才回退到 Rank 35b > Rank 16b > tiny-live plumbing`

## 结果（hard verdict）
**`Rank 71 / EMA-VWAP-ATR-volume graded admission score = park / evidence pool`**

## 为什么是这个 verdict
这轮最直白的结论不是“graded score 完全没用”，而是：**它改善了 fail-rate，也减少了亏损，但还没有形成足够干净、足够单调的质量分层，不能诚实地升格。**

### 三臂主结果（6bps/side）
- `baseline`
  - `mean_total_return≈-5.41%`
  - `post_cost_expectancy≈-0.16%`
  - `flip_to_fail_rate≈48.15%`
  - `mean_trades≈34.7`
- `score>=60`
  - `mean_total_return≈-1.70%`
  - `post_cost_expectancy≈-0.04%`
  - `flip_to_fail_rate≈38.02%`
  - `trade_retention≈70.28%`
- `score>=75`
  - `mean_total_return≈-0.11%`
  - `post_cost_expectancy≈+0.02%`
  - `flip_to_fail_rate≈34.83%`
  - `trade_retention≈60.64%`

### baseline bucket 分层（6bps）
- `<60`
  - `mean_total_return≈-1.30%`
  - `post_cost_expectancy≈-0.09%`
  - `flip_to_fail_rate≈63.52%`
- `60~74`
  - `mean_total_return≈-3.53%`
  - `post_cost_expectancy≈-0.80%`
  - `flip_to_fail_rate≈66.67%`
- `>=75`
  - `mean_total_return≈-0.79%`
  - `post_cost_expectancy≈-0.01%`
  - `flip_to_fail_rate≈35.93%`

### 更诚实的读法
1. `score>=60 / >=75` 确实比 baseline 少亏，也更少早死，这说明 **graded gate 不是完全空想**；
2. 但关键 bucket 没有呈现足够干净的单调关系：`60~74` 这档反而比 `<60` 更差，说明当前四块等权 + session VWAP 的口径还不够稳定；
3. `score>=75` 的改善，很大一部分仍来自明显缩样本（只保留约 `60.64%` 的交易）；
4. 到 `10/15/20bps` 后，三臂仍整体为负，说明它还没强到足以给出 `P1/P2` 升格。 

换成人话：**这条线更像“有一点方向对了，但还不够诚实”，不是当前 desk 可以继续默认消耗 Scout 预算的存活候选。**

## 对 desk 的影响
- `Rank 71` 现在更像一个值得记住的 framing：`continuation` 可能确实该从 binary 改写成 graded score；
- 但按当前最小 clean replication 结果，它还不该继续占默认 fast-lane；
- 因为这轮已经把它允许的那次 minimal clean replication 用掉了，下一轮更诚实的动作不是继续磨它，而是回到新的 fresh source：
  - `realized-vol mid-band cost-survival gate`
  - `PSAR close-confirmed follow-up gate`
- `Paper Seat / EMA` 仍按 `waiting_not_due / due_soon` 处理；本轮没有任何理由回头挤占 `P3 continuity`。

## 最小验证
- 已实际运行：`python3 scripts/build_rank71_ema_vwap_atr_volume_score_clean_replication.py`
- 脚本成功退出并打印：
  - `generated_at=2026-03-18 23:45 UTC`
  - `verdict=park / evidence pool`
- 已核对以下文件存在并写入：
  - `reports/artifacts/scout_rank71_ema_vwap_atr_volume_score_15m/overall_summary.csv`
  - `reports/artifacts/scout_rank71_ema_vwap_atr_volume_score_15m/bucket_summary.csv`
  - `reports/site/factors/scout_rank71_ema_vwap_atr_volume_score_15m/report.html`
  - `reports/site/reading/repo_scout/rank71_ema_vwap_atr_volume_score_clean_replication.html`
- 已确认 `docs/TODO.md` 顶板新增 `2026-03-18 23:45 UTC` 写回块。

## 风险 / 边界
- 这轮只回答 `EMA / PSAR raw lane + session VWAP + 四块等权 score` 的最小迁移，不代表更换 `anchored VWAP` 或重调权重后一定仍然失败；
- 但在当前 desk 规则下，这些都已经超出允许预算；本轮应该先如实给出 hard verdict，而不是继续替它找借口；
- 目前最值得记住的不是“score 不行”，而是 **`60~74` 这档很不诚实**，这提示后续若要重开，优先该检查的是 score 结构 / VWAP anchor，而不是马上加更多指标。

## 提交
- 未提交（工作区有大量与本轮无关的脏文件，避免混提）。
