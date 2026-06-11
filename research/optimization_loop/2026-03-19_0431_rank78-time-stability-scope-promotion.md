# 2026-03-19 04:31 UTC｜Rank 78 时间稳定性检查与 scope promotion verdict

## 为什么这轮选这个
- 先复核了 `Run 1 / EMA due-check only`：`reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 仍是全 desk 无 `due-now / overdue` lane，最近 due 点仍为 `A股三条 lane -> 2026-03-19 07:00 UTC`，所以 `Paper Seat / EMA` 继续处于 `running paper / waiting_not_due`。
- 顶板最新 `Next 3` 已明确：`Rank 78` 在上一轮最小 clean replication 后已升到 `P2`，本轮只允许再做 **1 个真正会改变 verdict 的最小检查**，默认优先 `时间稳定性 / 成本稳定性` 二选一。
- 由于 clean replication 页面里成本档（`6/10/15bps`）已经可见，而“是否只是单一 pocket 偶然改善”还没有被硬回答，所以这轮把唯一 P2 预算用在 **时间稳定性**，直接回答能否升到 `narrow paper pilot`。

## 这轮做了什么
1. 新增脚本：
   - `scripts/build_rank78_time_stability_scope_check.py`
2. 直接复用上一轮 `Rank 78` clean replication 产出的 `reports/artifacts/scout_rank78_adaptive_no_trade_band_15m/trades.csv`，不重开新 source，也不重跑下载。
3. 固定口径：
   - `6bps/side`
   - 对比 `adaptive_band_q1 vs raw`
   - 按 entry time 切成 3 段时间分桶
4. 生成新 artifact：
   - `reports/artifacts/scout_rank78_adaptive_no_trade_band_15m/time_stability_delta.csv`
   - `reports/artifacts/scout_rank78_adaptive_no_trade_band_15m/scope_promotion_check.csv`
   - `reports/artifacts/scout_rank78_adaptive_no_trade_band_15m/scope_promotion_meta.json`
5. 生成 reader-facing 页面：
   - `reports/site/factors/scout_rank78_adaptive_no_trade_band_15m/time_stability_scope_check.html`
   - `reports/site/reading/repo_scout/rank78_adaptive_no_trade_band_time_stability_scope_check.html`
6. 把最新 verdict 与 `Next 3` 写回 `docs/TODO.md` 顶部交易台指挥板。

## 核心结果
### 时间稳定性 delta（adaptive vs raw）
- `ema_psar_long`
  - **3/3 时间分桶** 都相对 `raw` 改善
  - `early_fail` 也是 **3/3 分桶** 更低
  - 总体：`raw total≈-10.98% -> adaptive≈-4.20%`
  - `mean retention≈86.60%`
- `breakout_short`
  - 只在 **2/3 分桶** 小幅改善，另有 `1/3` 分桶转弱
  - 总体仍是 `adaptive≈-9.95%` 略好于 `raw≈-10.61%`
  - 当前只保留 supporting evidence，不重新把 desk 重心切回 breakout
- `fib_retest_long`
  - **3/3 时间分桶** 都弱于 `raw`
  - 总体：`raw total≈+3.64% -> adaptive≈-2.78%`
  - 这构成当前 shared-gate 叙事的明确 fail

## Hard verdict
**`Rank 78 / adaptive no-trade band / EMA cost survival = promote to narrow paper pilot approved (P3, EMA-only suppression overlay)`**

## 为什么是这个 verdict
- 这轮不是在问“它是不是全 desk shared gate”，而是在问：`P2` 之后它有没有足够诚实地缩成一个能进入窄范围 paper 的 **更小 scope**。
- 答案是：**对 EMA 主线有，对全 desk 没有。**
  - `EMA` 主线已经给出 `3/3` 分桶一致改善 + `early_fail` 一致下降，说明它更像一个可部署的 **EMA-only admission suppression overlay**；
  - `Fib` 则是 `3/3` 分桶都转弱，所以不能继续包装成 `EMA / breakout / Fib` 共用的 shared gate；
  - `breakout_short` 只保留 supporting evidence，但当前默认不再强调 breakout，也不应借此改写 desk 主线。
- 因此这轮最诚实的收口不是继续把它留在泛 `P2` 研究态，而是：**允许它进入 `P3 narrow paper pilot`，但 scope 明确收紧到 `EMA-only suppression overlay`。**

## 对交易台顺序的影响
- `Rank 78` 不再继续占用默认 `Run 2 / Scout 主资源位` 做研究加码。
- 最新顺序应回到：
  1. `Run 1 = EMA due-check only`
  2. `Run 2 = fresh Scout（one-regime-per-session overlay > RECENT_PAPER_SEEDS / quant_digests / validated shortlist 其他 fresh source）`
  3. `Run 3 = 只有 fresh source 也 exhausted、或 Rank 17 / Rank 78 出现真实 status-changing event 需要最小 continuity writeback 时，才动用 1 次低频 P3 continuity 例外`
- 也就是说：`Rank 78` 这条线本轮已经完成了“会改变桌面判断”的那一步，接下来默认不应继续磨同一条线，而应把 Scout 主资源还给 fresh intake。

## 最小验证
- 已实际运行：
  - `python3 /root/clawd/jerry/momentum/scripts/build_rank78_time_stability_scope_check.py`
- 已确认新文件落地：
  - `reports/artifacts/scout_rank78_adaptive_no_trade_band_15m/time_stability_delta.csv`
  - `reports/artifacts/scout_rank78_adaptive_no_trade_band_15m/scope_promotion_check.csv`
  - `reports/site/factors/scout_rank78_adaptive_no_trade_band_15m/time_stability_scope_check.html`
  - `reports/site/reading/repo_scout/rank78_adaptive_no_trade_band_time_stability_scope_check.html`
- 已确认 `docs/TODO.md` 顶板写回成功。

## 风险 / 边界
- 这次 promotion 只适用于 **EMA-only suppression overlay**；不适用于 `fib_retest_long` shared gate 叙事。
- 当前仍只基于 `BTC/ETH/SOL 120d 15m` 样本与上一轮 clean replication 口径，不代表更长样本已经完全无风险。
- `P3` 的意思是允许最小 paper 接线 / 监控 / review，不是允许重新扩大 scope 或回到“万能 shared gate”叙事。

## Commit hash
- 未提交。
- 原因：git 工作区仍有大量与本轮无关的脏文件 / 未跟踪文件，当前不适合安全 selective commit。
