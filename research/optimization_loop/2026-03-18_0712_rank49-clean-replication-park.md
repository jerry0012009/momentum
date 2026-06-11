# 2026-03-18 07:12 UTC — Rank 49 funding/basis crowding gate 最小 clean replication 后压回 park

## 1）为什么这轮选这个
- 先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 与 `Next 3 bot3 runs` 检查当前席位。
- `07:01 UTC` 那轮已真实消化 A 股 `EMA due-now` refresh；最新 `ema_paper_trading_due_guardrail_snapshot.csv` 重新回到无 `due-now / overdue` lane，因此本轮 `Paper Seat / EMA` 属于 **`running paper / waiting_not_due`**。
- 按当前权威顺序，本轮应从 `Run 1` 自动切到 **`Run 2 / Rank 49 minimal clean replication`**，而不是继续挤占 `P3 continuity`。
- active Scout 边际价值比较（本轮）：
  - `Rank 49`：fresh、paper + public API、直接服务 short-continuation 执行过滤；
  - `Rank 35b`：queue-only fallback；
  - 结论：**`Rank 49 > Rank 35b`**，因此主资源位给 `Rank 49`。

## 2）本轮只认领 1 个主点
### 主点
- 对 **`Rank 49 / funding-basis crowded-long unwind gate`** 做唯一允许的 **最小 clean replication**。

### 紧邻子点
- 把 hard verdict 写回 `docs/TODO.md` 的 `Next 3` 权威区，刷新下一轮顺序。

## 3）做了什么改动
### 3.1 新增 clean replication 脚本
新增：
- `scripts/build_rank49_funding_basis_crowding_clean_replication.py`

冻结口径：
- 样本：`BTC/ETH/SOL`，本地 `120d 15m` cache
- 外部数据：Binance 公共 `fundingRate` + `premiumIndexKlines`
- 数据诚实性：只使用入场前最后一个已发布值；执行统一 `next-bar open + no-overlap + hold 8 bars`
- 两条 short base setup：
  - `ema_short`
  - `breakdown_short`
- 三个 overlay 变体：
  - `no_gate`
  - `crowded_long_only`
  - `already_crowded_short_veto`
- 成本梯度：`6 / 10 / 15 / 20 bps per side`

### 3.2 产出 artifact / 网页落点
生成：
- `reports/artifacts/scout_rank49_funding_basis_crowding_15m/overall_summary.csv`
- `reports/artifacts/scout_rank49_funding_basis_crowding_15m/asset_summary.csv`
- `reports/artifacts/scout_rank49_funding_basis_crowding_15m/time_pocket_summary.csv`
- `reports/artifacts/scout_rank49_funding_basis_crowding_15m/trade_log.csv`
- `reports/artifacts/scout_rank49_funding_basis_crowding_15m/signal_event_counts.csv`
- `reports/artifacts/scout_rank49_funding_basis_crowding_15m/*_crowding_features.csv`
- `reports/site/factors/scout_rank49_funding_basis_crowding_15m/report.html`

### 3.3 写回权威指挥板
- 更新 `docs/TODO.md`
- 把 `Rank 49` 本轮 replication 的 hard verdict 写回 `Next 3 bot3 runs`
- 下一轮顺序重置为：
  - `Run 1 = EMA due-check only`
  - `Run 2 = fresh source intake（按 7.10 先查 RECENT_PAPER_SEEDS / quant_digests / validated shortlist）`
  - `Run 3 = Rank 35b（若 fresh intake 仍 exhausted） / tiny-live plumbing`

## 4）验证 / 证据
执行命令：
```bash
python3 /root/clawd/jerry/momentum/scripts/build_rank49_funding_basis_crowding_clean_replication.py
```

### 4.1 主读法（`ema_short + crowded_long_only @ 6bps`）
- `mean_total_return≈-6.47%`
- `positive_asset_ratio=0/3`
- `mean_trades≈28.3`
- `mean_false_break_4bars_rate≈49.32%`
- `trade_count_retention≈6.16%`

结论：不是“少量砍噪音后转正”，而是 **靠显著砍样本后仍未转正**。

### 4.2 `already_crowded_short_veto` 也没到可升格程度
- `ema_short + already_crowded_short_veto @ 6bps`
  - `mean_total_return≈-15.23%`
  - `positive_asset_ratio=0/3`
  - `mean_trades≈123.3`
  - 虽然明显好于 `ema_short + no_gate≈-40.50% / mean_trades≈460`，但仍远未到 paper candidate 口径。

### 4.3 另一条基线（`breakdown_short`）同样不够诚实
- `breakdown_short + crowded_long_only @ 6bps`
  - `mean_total_return≈-0.52%`
  - `positive_asset_ratio≈33.33%`
  - `mean_trades≈6.7`
  - `trade_count_retention≈5.91%`
- time-pocket：`bucket_2≈+6.97% / 100% positive_asset_ratio`，但 `bucket_3≈-11.20% / 0%`，说明 pocket 非常不稳定。

结论：这条线更像 **“只在个别 pocket 少亏或偶有正 pocket 的过滤器证据”**，不够支持升到 `paper candidate`。

## 5）本轮硬结论
- **`Rank 49 / funding-basis crowded-long unwind gate = park / evidence pool`**
- 它最多说明：`funding/premium crowding` 对 short continuation 可能有一点“少亏型过滤”价值；
- 但当前证据不支持把它当成 desk 默认 overlay，更不支持继续占用默认 Scout 主资源位。

## 6）风险 / 边界
- 这是最小 clean replication，不是最终 execution verdict；
- 当前只用了 Binance 公共 funding + premium proxy，没有引入更重的 basis term structure / OI / long-short ratio 联合建模；
- 但按当前 desk 规则，这一轮已足够回答“它值不值得继续占 fast-lane 预算”——答案是否定的。

## 7）下一步建议
1. 若下一轮 `EMA` 仍 `waiting_not_due`，按 `7.10` 先做 **fresh source intake**，不要继续磨 `Rank 49`。
2. 优先从：
   - `docs/RECENT_PAPER_SEEDS.md`
   - `research/quant_digests/INDEX.md`
   - `reports/artifacts/literature/validated_alpha_shortlist_2026-03-10.md`
   再认领 1 条新 source。
3. 只有 fresh intake 仍真实 exhausted，才回退到 `Rank 35b / tiny-live plumbing`。

## 8）Commit hash
- 本轮未提交。
- 原因：git 工作区存在大量与本轮无关的脏文件 / 未跟踪文件，当前不适合安全 selective commit。
