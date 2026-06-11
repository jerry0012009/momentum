# 2026-03-19 22:00 UTC — Rank 100 fib-depth shallow-mid admission gate clean replication

## 本轮先核对的 desk 状态
- repo 工作区仍有大量与本轮无关的既有脏文件；本轮未做 commit，也未混提无关改动。
- 最近 optimization logs：
  - `2026-03-19_2140_rank100-fib-depth-intake.md`
  - `2026-03-19_2130_rank99-time-stability-park.md`
  - `2026-03-19_2053_rank99-clv-clean-replication.md`
- 先实际执行：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 结果：`waiting_not_due`
  - 当前无 `due-now / overdue` lane；最近 due 仍是 `Crypto 1d+1wk（BTC/ETH/SOL）`，约 `2.0h` 后到点。
  - 结论：`Paper Seat = EMA / running paper / waiting_not_due`
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json`
  - `run_at_utc = 2026-03-19T21:33:47Z`
  - `new_closed_trades_appended = 0`
  - 结论：当前没有需要 bot3 插队主资源处理的 `P3 status-changing event`。

## Active Scout 候选边际比较（本轮先比较后认领）
1. **`Rank 100 / fib-depth shallow-mid admission gate`**
   - 上一轮 source intake 已 `guard-passed / admit_to_clean_replication_queue`
   - 顶板当前 `Next 3` 明确要求：若 `EMA` 仍 `waiting_not_due`，本轮就只给它 `1` 次最小 clean replication
   - 它直接回答 desk 当前最实际的问题：Fib 回踩默认该优先 `38-62`，还是继续迷信 `62-79`
2. **`Rank 101 / 3-step volume dry-down long-bias gate reserve`**
   - 当前是紧邻后备，但还没到本轮主资源位
   - 只有当 `Rank 100` clean replication 给出 hard verdict 后，才轮到它做 source intake
3. **旧 `P1 evidence_pool`（`Rank 93 / 90 / 91 / 82 / 80 / 81`）**
   - 当前边际价值低于 `Rank 100 -> Rank 101` 这组 fresh reserve
4. **`P3 continuity` / `tiny-live plumbing`**
   - 当前无真实 `P3` 状态变更，也无 live promoted candidate，不应插队

结论：本轮主资源继续给 `Rank 100`；紧邻子点只做顶板写回与 reader-facing 外显，不并开 `Rank 101`。

## 本轮只认领的主点
- **主点：`Scout Seat / Rank 100 / fib-depth shallow-mid admission gate` 的 1 次最小 clean replication**
- 紧邻子点：把 clean replication 的 hard verdict 写回 `TODO` 顶板，并同步 reader-facing 页面与 artifact

## 本轮 clean replication 口径
- 数据：严格复用 `reports/artifacts/quant_digests/fib_zone_depth_proxy/`
  - `BTC / ETH / SOL`
  - `120d`
  - `15m`
  - `next-bar open`
  - `no-overlap`
  - 成本：`6bps/side`
- 本轮不追新 bar、不改 source intake 的问题定义，只把已有代理快检收口成 desk 级 hard verdict。
- 复现比较臂：
  - 浅中桶：`shallow_mid_38_62`
  - 深桶：`deep_62_79`
  - 同时保留 4 个细带：`38_50 / 50_62 / 62_71 / 71_79`
- 这轮额外固定的诚实指标：
  - `avg_net_ret`
  - `success_rate`
  - `stop_rate`
  - `median_bars_to_touch`

## 最小结果
### 深浅两桶
- `shallow_mid_38_62`
  - `trades = 736`
  - `avg_net_ret ≈ -3.28bps`
  - `success_rate ≈ 32.34%`
  - `stop_rate ≈ 19.84%`
  - `median_bars_to_touch = 4.0`
- `deep_62_79`
  - `trades = 359`
  - `avg_net_ret ≈ -9.63bps`
  - `success_rate ≈ 17.83%`
  - `stop_rate ≈ 44.01%`
  - `median_bars_to_touch = 7.0`

### 细带读法
- `50_62` 是四档里最不差的一档：`avg_net_ret ≈ -1.47bps`
- `38_50` 也明显优于两条 deep 带：`avg_net_ret ≈ -4.58bps`
- `62_71 / 71_79` 都落在更差区间：约 `-9.51bps / -9.78bps`

### 资产拆开后的最诚实读法
- `BTC @ shallow_mid_38_62` 有局部亮点：`avg_net_ret ≈ +1.18bps`
- 但 `ETH / SOL @ shallow_mid_38_62` 仍未整体转正，deep 桶也没有任何资产能给出“深回踩更稳”的统一证据
- 因此它更像 admission 排序问题，而不是独立可升格 edge

## 本轮 hard verdict
- **`Rank 100 / fib-depth shallow-mid admission gate = park / evidence pool`**

### 为什么不是 promote_to_P2
1. `38-62` 虽明显优于 `62-79`，但自己也仍是成本后负值，尚不足以构成 `paper candidate`
2. 最优单带 `50_62` 也只有 `≈ -1.47bps`，更像“少亏排序”而不是可单独部署的 edge
3. 本轮结果更适合作为现有 Fib / EMA / breakout-retest 主线的 **generic retrace ordering**，不适合作为继续占用 Scout 主资源的独立 active candidate

### 为什么也不是 keep_P1
- `Rank 100` 在 source intake 时就已经把 trade on / trade off 说清了；最小 clean replication 之后，问题已不是“它是否有一点 alpha 味道”，而是“这条线是否值得继续独立占预算”。
- 当前答案已经足够硬：**不值得**。应直接 park，并把有用部分折回 desk execution 读法：`38-62` 常态优先，`62-79` 只作条件触发。

## 产物
- script:
  - `scripts/build_rank100_fib_depth_clean_replication.py`
- artifact:
  - `reports/artifacts/scout_rank100_fib_depth_shallow_mid_15m/depth_bucket_summary.csv`
  - `reports/artifacts/scout_rank100_fib_depth_shallow_mid_15m/depth_bucket_asset_summary.csv`
  - `reports/artifacts/scout_rank100_fib_depth_shallow_mid_15m/band_summary.csv`
  - `reports/artifacts/scout_rank100_fib_depth_shallow_mid_15m/band_asset_summary.csv`
  - `reports/artifacts/scout_rank100_fib_depth_shallow_mid_15m/verdict_summary.csv`
- reader-facing:
  - `reports/site/factors/scout_rank100_fib_depth_shallow_mid_15m/report.html`
  - `reports/site/reading/repo_scout/rank100_fib_depth_shallow_mid_clean_replication.html`

## 对顶板的更新结论
- `Rank 100 = park / evidence pool`
- `Fib depth` 对当前 desk 的保留价值：**generic retrace ordering only**
  - `38-62` = 默认常态 admission
  - `62-79` = 只在更强 trend / context 下条件放行
- 最新 `Next 3`：
  1. `Run 1 = EMA due-check only`
  2. `Run 2 = 若 EMA 仍 waiting_not_due，则切 Rank 101 / 3-step volume dry-down long-bias gate 做 source intake + 两条轻量诚实守门`
  3. `Run 3 = 若 Rank 101 已 guard-passed 且 EMA 仍 waiting_not_due，则只给它 1 次最小 clean replication；若 Rank 101 intake 直接 hard-fail / exhausted，则再按 7.10 回 fresh source pool；只有 fresh source 也 exhausted 时才回退到 tiny-live plumbing`

## 最小验证
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 如实确认当前还是 `waiting_not_due`
- `python3 scripts/build_quant_digest_fib_zone_depth_proxy.py`
  - 已成功重建 `fib_zone_depth_proxy` 原始 digest artifact
- `python3 scripts/build_rank100_fib_depth_clean_replication.py`
  - 已成功写出 artifact 与两张 reader-facing 页面
- 读回 `docs/TODO.md`
  - 已确认最新 supplement、Scout verdict 与 `Next 3` 已写回

## 备注
- 本轮没有并开 `Rank 101`；只完成 `1 个主点 + 1 个紧邻子点`
- 本轮没有触发 `P3 continuity` 预算，也没有回头续磨旧 `P1 evidence_pool`
- 工作区仍有大量历史脏文件；本轮未尝试整理、提交或覆盖这些无关改动
