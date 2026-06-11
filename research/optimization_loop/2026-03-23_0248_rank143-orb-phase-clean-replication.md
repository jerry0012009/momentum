# 2026-03-23 02:48 UTC — Rank 143 / ORB phase retest state-machine + score gate 最小 clean replication

- 严格遵循：`docs/TODO.md` 顶部 `TRADING DESK BOARD` + `docs/AUTO_OPTIMIZATION_LOOP.md`
- 本轮类型：`Scout / Run 1 / 当前 primary 的唯一最小 clean replication`
- interrupt 判定：未见 `Paper / 正在自动运行` runner 的真实 `stale / error / refresh 失步 / ledger 爆雷 / open-position 异常 / red-watch`，也未见 tiny-live / live-shadow blocking anomaly；因此本轮不抢 interrupt。

## 1. 本轮问题与实验口径
只回答顶板写死的一个问题：

> `Rank 143` 到底只是“retest 不该独立硬门”的 **phase-quality skeleton**，还是还能保留为 active Scout。

最小对照四臂：
- `A = 二元 retest_hold`
- `B = phase state machine（breakout -> retest -> bounce + timeout/abort，不加 score）`
- `C = phase state machine + score>=60`
- `D = phase state machine + score>=70`

统一口径：
- `BTC / ETH / SOL`
- `15m cache / pseudo-session breakout`
- `next-bar open / no-overlap`
- 成本层：`6 / 10 / 15 bps per side`
- 输出：`trade_count_retention`、`continue / fail / timeout share`、`post-cost expectancy`、`12-bar / 24-bar invalidation ratio`

## 2. 6bps 主结论（先说人话）
结论很直接：**四臂都没把这条线从“结构表达更诚实”推进到“可留 active Scout”的程度。**

- `D(score>=70)` headline 最不差：`mean_total_return = -9.83%`
- 但它只是靠更强过滤把 `trade_count_retention` 压到 `39.72%`
- 三个资产在 `6bps` 下仍然 **全部负收益**，`positive_asset_ratio = 0/3`
- `post-cost expectancy` 仍为负：`-0.15%`
- `12-bar / 24-bar invalidation ratio` 也没有出现真正像样的下降：`60.51% / 66.16%`

因此这轮最诚实的 desk call 不是 `keep_P1`，而是：

> **`Rank 143 = park`**。它证明了“retest 不该继续写成独立硬门”，但**没有证明 phase state machine + score 在当前 15m crypto clean replication 下值得继续占 Scout 主资源**。

## 3. 主表（6bps）
| arm | mean_total_return | positive_asset_ratio | trade_count_retention | continue_share | fail_share | timeout_share | post-cost expectancy | invalidation_12 | invalidation_24 | mean_trades |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A_binary_retest | -14.66% | 0.00% | 59.31% | 50.88% | 23.53% | 17.03% | -0.11% | 60.38% | 63.29% | 147.7 |
| B_phase_only | -14.13% | 0.00% | 56.59% | 56.72% | 26.18% | 17.10% | -0.11% | 59.49% | 63.51% | 140.3 |
| C_phase_score60 | -11.15% | 0.00% | 42.52% | 42.52% | 34.77% | 22.71% | -0.15% | 61.45% | 66.48% | 79.3 |
| D_phase_score70 | -9.83% | 0.00% | 39.72% | 39.72% | 36.46% | 23.82% | -0.15% | 60.51% | 66.16% | 70.7 |

## 4. 分资产读法（6bps）

### A_binary_retest
| asset | total_return | trades | trade_count_retention | continue_share | fail_share | timeout_share | post-cost expectancy | invalidation_12 | invalidation_24 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BTC-USD | -12.78% | 148 | 58.04% | 49.41% | 27.06% | 14.90% | -0.09% | 58.78% | 61.49% |
| ETH-USD | -5.47% | 143 | 58.85% | 51.03% | 23.05% | 18.11% | -0.04% | 55.24% | 57.34% |
| SOL-USD | -25.74% | 152 | 61.04% | 52.21% | 20.48% | 18.07% | -0.19% | 67.11% | 71.05% |

### B_phase_only
| asset | total_return | trades | trade_count_retention | continue_share | fail_share | timeout_share | post-cost expectancy | invalidation_12 | invalidation_24 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BTC-USD | -15.57% | 142 | 55.91% | 55.91% | 29.13% | 14.96% | -0.12% | 60.56% | 64.79% |
| ETH-USD | -4.92% | 135 | 55.56% | 55.56% | 26.34% | 18.11% | -0.03% | 53.33% | 56.30% |
| SOL-USD | -21.90% | 144 | 58.30% | 58.70% | 23.08% | 18.22% | -0.17% | 64.58% | 69.44% |

### C_phase_score60
| asset | total_return | trades | trade_count_retention | continue_share | fail_share | timeout_share | post-cost expectancy | invalidation_12 | invalidation_24 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BTC-USD | -10.76% | 78 | 41.05% | 41.05% | 38.95% | 20.00% | -0.14% | 66.67% | 69.23% |
| ETH-USD | -6.28% | 81 | 42.86% | 42.86% | 33.86% | 23.28% | -0.08% | 51.85% | 56.79% |
| SOL-USD | -16.39% | 79 | 43.65% | 43.65% | 31.49% | 24.86% | -0.22% | 65.82% | 73.42% |

### D_phase_score70
| asset | total_return | trades | trade_count_retention | continue_share | fail_share | timeout_share | post-cost expectancy | invalidation_12 | invalidation_24 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BTC-USD | -7.18% | 69 | 38.12% | 38.12% | 40.88% | 20.99% | -0.11% | 63.77% | 66.67% |
| ETH-USD | -7.47% | 73 | 40.33% | 40.33% | 35.36% | 24.31% | -0.10% | 52.05% | 57.53% |
| SOL-USD | -14.83% | 70 | 40.70% | 40.70% | 33.14% | 26.16% | -0.23% | 65.71% | 74.29% |


## 5. 轻量 scorecard（本轮必须补）
- `usefulness`: **medium** — 这轮确实回答了“retest 不该继续当独立 hard gate”，并把 `phase -> score` 的 cleaner expression 跑了一遍。
- `time_stability`: **weak** — 没看到会随着过滤变强而出现稳定改善；更像全时段一起变少、一起少亏。
- `cross_asset_stability`: **weak** — `BTC / ETH / SOL` 在 `6bps` 下全部仍负，没出现 1 个稳定正 pocket。
- `cost_trade_stability`: **weak** — 从 `6 -> 10 -> 15bps` 逐层恶化，所有 arms 全程为负。
- `deployability`: **low** — 可以当研究表达层，但不值得进 `P2/P3`，更不该接 paper wiring。
- `hard-fail flags`:
  - `all_assets_negative_at_6bps`
  - `trade_retention_collapse_when_scored`
  - `timeout_not_meaningfully_repaired`
  - `invalidation_not_improved_enough`
  - `score_helps_less_than_it_filters`
- `recommended_action = park`
- `why_now`: 因为这刀已经足够回答它的唯一值钱问题：**该不该继续留在 active Scout**。答案是否定的，继续磨只会重复“过滤更强 -> 少亏一点 -> 仍不够”。
- `main_weakness`: phase skeleton 能改善叙事，但**没有产生可部署的成本后 pocket**；score 进一步只是压样本，不是创造 alpha。

## 6. desk verdict
### 正式结论
- `Rank 143 / ORB phase retest state-machine + score gate`
- 从 `P1 / active compare admitted（current primary）` 更新为：
  - **`P0 / park / evidence only`**

### 为什么不是 keep_P1
1. `B` 比 `A` 只带来非常小的 headline 改善（`-14.66% -> -14.13%`），不足以证明 skeleton 自身有继续挖的边际价值；
2. `C / D` 虽 headline 更不差，但本质是交易保留率掉到 `42.52% / 39.72%` 后的“少亏一点”；
3. `continue / fail / timeout` 结构没有出现足够新的 deployable 轮廓；
4. 三资产全负，且 `12-bar / 24-bar invalidation` 没给出真正可升格的稳定性改善。

### 本轮真正留下来的东西
留下来的不是候选本身，而是一句更清楚的 desk 语言：

> **以后不要再把 `Fib retest_hold` 写成独立 hard gate。**
> 它更像 `phase-quality skeleton / scoring language`，但在当前 clean replication 下，这种表达还不配继续占用 active Scout 预算。

## 7. 对 TODO 顶板的最小写回建议
只做最小局部修改：
1. 在 `Recent evidence` 补 1 条本轮 hard verdict；
2. 把 `Active Scout` 里的 `Rank 143` 从当前 primary 改成 `P0 / park / evidence only`；
3. 把 `Next 3` 的 `Run 1` 从 `Rank 143` 切到 `Rank 140 / Rank 125 / Rank 112 / Rank 111` 的下一最有杠杆对照点。

## 8. 产出落点
- script: `scripts/build_rank143_orb_phase_clean_replication.py`
- artifacts:
  - `reports/artifacts/scout_rank143_orb_phase_retest_15m/summary.csv`
  - `reports/artifacts/scout_rank143_orb_phase_retest_15m/asset_summary.csv`
  - `reports/artifacts/scout_rank143_orb_phase_retest_15m/trades.csv`
- site: `reports/site/factors/scout_rank143_orb_phase_retest_15m/report.html`
