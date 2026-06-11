# 2026-03-20 00:54 UTC — Rank 103 confirmed extremum honest fib anchor clean replication -> park

## Run 1 -> Run 2 执行
- Run 1：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 结果：`EMA = waiting_not_due`
  - 当前没有 `due-now / overdue` lane
  - 最近 due：`A股三条 lane -> 2026-03-20 07:00 UTC`（约 `6.2h`）
- `manual_narrow_paper_last_run_summary.json` 最新一次仍是 `new_closed_trades_appended=0`
- 因此按顶板当前 authoritative `Next 3`，本轮合法主动作就是：
  - `Scout Seat / Rank 103 / confirmed extremum honest fib anchor`
  - 只做 `1 次最小 clean replication`

## 开轮检查
- branch：`master`
- repo 工作区仍有大量与本轮无关的既有脏文件：`git status --short | wc -l = 1608`
- 最近 optimization logs：
  - `2026-03-20_0034_rank103-confirmed-extremum-intake.md`
  - `2026-03-20_0009_ema-crypto-due-refresh.md`
  - `2026-03-19_2338_rank102-time-stability-park.md`
- 本轮不混提、不清理历史脏文件

## Active Scout 候选边际比较（先比较后认领）
1. **`Rank 103 / confirmed extremum honest fib anchor`**
   - 顶板已明确：若 `EMA` 仍 `waiting_not_due`，本轮就只给它那 1 次最小 clean replication
   - 它当前边际价值最高，因为它直接回答上游 anchor 口径是否值得继续占 queue-facing 主资源位
2. **`post-break sign-flip density`**
   - 保留为下一位 fresh paper reserve
   - 只有当 `Rank 103` clean replication 直接 hard-fail / exhausted，才轮到它
3. **`prebreak higher-low pressure ladder context gate` / 旧 `P1 evidence_pool` / `P3 continuity` / `tiny-live plumbing`**
   - 当前都不该抢这轮主资源

结论：本轮只认领 `Rank 103` 的 clean replication，不并开第二条候选。

## 本轮认领
- 主点：`Rank 103 / confirmed extremum honest fib anchor`
- 紧邻子点：把 hard verdict、reader-facing 页面、`TODO` 顶板一次写齐

## Clean replication 口径
- **输入样本**：`reports/artifacts/quant_digests/confirmed_extremum_anchor_proxy/`
  - `event_summary.csv`
  - `summary_snapshot.json`
- **复用 reference**：`reports/artifacts/scout_rank100_fib_depth_shallow_mid_15m/band_summary.csv`
  - 用已冻结的 `Fib-depth` band-level `avg_net_ret / success_rate` 作为最轻量 `post_cost` proxy
- **固定比较对象**：
  1. `provisional-anchor`
  2. `confirmed-anchor`
- **本轮只回答的最小问题**：
  - `38.2-79` 可交易回踩带的 `admit_rate` 是否明显变化
  - `bucket_shift_rate` 有多大
  - 这些新增 admit 事件是否足以把 proxy `post_cost_expectancy` 推过 0
- **不做**：
  - 不追新 bar
  - 不重拉数据
  - 不把它强行扩成完整 stability pack
  - 不再打开第二条 fresh candidate

## 结果
### 1) 主结论
**`Rank 103 = park / evidence pool`**。

### 2) 为什么不是 promote_to_P2
- `confirmed-anchor` 的确让更多事件进入可交易回踩带：
  - `provisional admit_rate ≈ 6.75%`
  - `confirmed admit_rate ≈ 17.53%`
- `bucket_shift_rate ≈ 12.59%`
  - 其中 `promoted_to_admit_rate ≈ 10.78%`
  - `demoted_out_of_admit_rate = 0%`
- 但关键的 queue-facing 问题没过门槛：
  - `provisional proxy post_cost_expectancy ≈ -4.09bps`
  - `confirmed proxy post_cost_expectancy ≈ -4.01bps`
- 也就是说：它证明了 **“锚点画早会把回踩看浅”**，却没有证明 **“把锚点改成 confirmed 后，就足以形成值得部署的 shared gate”**。

### 3) side 拆开看
- **long**：
  - `admit_rate: 7.72% -> 17.84%`
  - `proxy expectancy: -4.03bps -> -3.81bps`
  - 有改善，但仍没过 0
- **short**：
  - `admit_rate: 5.85% -> 17.25%`
  - `proxy expectancy: -4.15bps -> -4.20bps`
  - admit 增加，但质量反而略差

换成人话：这条线当前更像 **measurement correction / honest anchor**，而不是值得继续占 active Scout 预算的独立 queue-facing 候选。

## 当前硬结论
- **`Rank 103 = park / evidence pool`**
- desk 读法收口为：
  - `confirmed anchor` 值得保留成 Fib / failure verdict / EMA continuation 的上游口径修正
  - 但当前证据不足以把它继续升到 `P2 / paper candidate`
  - 因此不再继续给它 stability pack，也不继续让它占 `Scout Seat`

## 本轮交付（deployable artifact）
- 脚本：
  - `scripts/build_rank103_confirmed_extremum_clean_replication.py`
- artifact：
  - `reports/artifacts/scout_rank103_confirmed_extremum_honest_fib_anchor_15m/anchor_compare_summary.csv`
  - `reports/artifacts/scout_rank103_confirmed_extremum_honest_fib_anchor_15m/side_compare_summary.csv`
  - `reports/artifacts/scout_rank103_confirmed_extremum_honest_fib_anchor_15m/shift_summary.csv`
  - `reports/artifacts/scout_rank103_confirmed_extremum_honest_fib_anchor_15m/bucket_proxy_reference.csv`
  - `reports/artifacts/scout_rank103_confirmed_extremum_honest_fib_anchor_15m/verdict_summary.csv`
- reader-facing 页面：
  - `reports/site/factors/scout_rank103_confirmed_extremum_honest_fib_anchor_15m/report.html`
  - `reports/site/reading/repo_scout/rank103_confirmed_extremum_honest_fib_anchor_clean_replication.html`

## 对顶板的直接影响
- `Paper Seat = EMA / running paper / waiting_not_due`
- `Live Seat = 暂空`
- `Rank 103 = P0 / park / evidence pool`
- 当前 active Scout 顺序应改写为：
  1. `post-break sign-flip density`
  2. `prebreak higher-low pressure ladder context gate`
  3. 旧 `P1 evidence_pool`
  4. `P3 continuity sidecar`
  5. `tiny-live plumbing`
- 当前最新 `Next 3`：
  1. `Run 1 = EMA due-check only（优先盯 A股三条 lane -> 2026-03-20 07:00 UTC）`
  2. `Run 2 = 若 EMA 仍 waiting_not_due，则切 post-break sign-flip density 的 source intake + 两条轻量诚实守门`
  3. `Run 3 = 若 post-break sign-flip density guard-pass，则只给它 1 次最小 clean replication；若它也 hard-fail / exhausted，则切 prebreak higher-low pressure ladder context gate；只有 fresh source 也 exhausted，才允许回退旧 evidence pool > P3 continuity > tiny-live plumbing`

## 最小验证
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 如实确认当前还是 `waiting_not_due`
- `python3 scripts/build_rank103_confirmed_extremum_clean_replication.py`
  - 成功产出 artifact 与 reader-facing 页面
- 回读以下文件，确认已写入成功：
  - `reports/artifacts/scout_rank103_confirmed_extremum_honest_fib_anchor_15m/verdict_summary.csv`
  - `reports/site/reading/repo_scout/rank103_confirmed_extremum_honest_fib_anchor_clean_replication.html`
  - `docs/TODO.md`

## 备注
- 本轮没有并开 `post-break sign-flip density`
- 本轮没有触发 `P3 continuity` 或 `tiny-live plumbing`
- 没有发生 `edit exact text 不匹配` fallback
- 工作区仍有大量历史脏文件；本轮未尝试整理、提交或覆盖这些无关改动
