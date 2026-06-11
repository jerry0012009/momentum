# 2026-03-23 06:07 UTC · Rank 146 / structure verdict optimizer frozen-skeleton cut

- 严格遵循：`docs/TODO.md` 顶部 `TRADING DESK BOARD` + `docs/AUTO_OPTIMIZATION_LOOP.md`
- 本轮类型：`Scout / Run 1 / fresh intake reserve -> 唯一允许的 frozen-skeleton decisive cut`
- 主点：`Rank 146 / structure verdict optimizer`
- 紧邻子点：判断这刀之后它是否还该继续占默认 primary，还是把主资源让回 compare anchor。

## 0. 先判 interrupt
- `Paper / 正在自动运行` 顶板未写入新的 `stale / error / refresh 失步 / ledger 爆雷 / open-position 异常 / red-watch`。
- `tiny-live / live-shadow plumbing` 也未见新的 blocking anomaly。
- 因此本轮不抢 interrupt，继续按 `Next 3 bot3 runs` 执行 `Rank 146` 的唯一允许首刀。

## 1. 本轮实际执行了什么
执行脚本：
- `python3 scripts/build_repo_ema_adx_vol_skeleton_clean_replication.py`

产物：
- `reports/artifacts/scout_repo_ema_adx_vol_skeleton_15m/overall_summary.csv`
- `reports/artifacts/scout_repo_ema_adx_vol_skeleton_15m/asset_summary.csv`
- `reports/artifacts/scout_repo_ema_adx_vol_skeleton_15m/time_stability_summary.csv`
- `reports/artifacts/scout_repo_ema_adx_vol_skeleton_15m/summary.csv`
- `reports/site/factors/scout_repo_ema_adx_vol_skeleton_15m/report.html`

冻结口径：
- 资产：`BTC / ETH / SOL`
- 周期：`15m`
- 样本：本地 `120d` cache
- 执行：`next-bar open + no-overlap + hold 8 bars`
- 对照臂：`ema_stack_only / adx_di_gate / volume_gate / range_filter_gate / full_stack`
- 成本：重点看 `6bps/side`，并同步给出 `10/15/20bps`

## 2. 结果摘要（最关键）
`6bps/side` 下：
- `EMA stack only`：mean total return 约 `-72.52%`，`positive_asset_ratio = 0/3`，mean trades 约 `1170.3`
- `+ADX gate`：约 `-54.10%`，`0/3`，trade retention 约 `53.08%`
- `+volume gate`：约 `-43.16%`，`0/3`，trade retention 约 `38.90%`
- `+range filter`：约 `-52.14%`，`0/3`，trade retention 约 `68.98%`
- `full stack`：约 `-18.93%`，`0/3`，trade retention 仅约 `17.97%`

分资产看 `full stack @ 6bps/side`：
- `BTC`：约 `-13.99%`，false-start 约 `72.54%`
- `ETH`：约 `-14.05%`，false-start 约 `74.12%`
- `SOL`：约 `-28.76%`，false-start 约 `78.10%`

时间稳定性（`full_stack @ 6bps/side`）：
- `bucket_1`：mean total return 约 `-2.59%`，positive asset ratio `1/3`
- `bucket_2`：约 `-7.49%`，positive asset ratio `1/3`
- `bucket_3`：约 `-9.95%`，positive asset ratio `0/3`

## 3. 这刀真正回答了什么
这刀没有证明“优化器没用”；它回答的是一个更窄但更重要的问题：

> **仅仅因为有一个会做结构+参数堆叠的 repo，并不等于结构就会被自动洗白。**

至少对这份 repo 自带的 `EMA-ADX-VOL` 15m skeleton 来说：
- 改善主要来自 **大幅砍交易数**，不是形成稳定正 pocket；
- `full stack` 虽然比最原始 `EMA stack only` 少亏很多，但仍然 **全资产为负**；
- false-start 也没有被压到可以让人放心的水平；
- 因而它更像一个 **execution veto 模板**，不是可直接升格的结构救火器。

## 4. 对 Rank 146 的 desk verdict
### 本轮 verdict
- **`Rank 146 = keep_P1 / one frozen-skeleton cut spent / no promote yet`**

### 为什么不是 `promote_P2`
因为 intake 时给它的唯一升层条件是：
- 至少有 1 个固定 skeleton 在 `BTC/ETH/SOL` rolling OOS 里，给出更高 positive-fold ratio，且参数/结构排序不乱跳。

而这轮最接近的 frozen-skeleton 代理结果是：
- `positive_asset_ratio` 依然 `0/3`
- `full-stack retention` 只有约 `18%`
- 时间分桶也没有给出稳定正 pocket

所以它没有触发升层证据。

### 为什么也暂不直接 `park`
因为这轮只打到了 **repo 内置的一种 EMA-ADX-VOL skeleton**；
它还没有真正覆盖到 desk 当前最关心的另外几类骨架：
- `EMA + PSAR fail-safe`
- `Donchian breakout + EMA context`
- 更接近 `breakout-short / Fib retest` 的 continuous-parameter routing

因此更诚实的处理不是直接宣布 Rank 146 整体死亡，而是：
- **先停止把它当默认 primary**；
- 若后续要继续，只允许把它拿去做一次更贴近 `Rank 111`/主线 skeleton 的最短 decisive compare。

## 5. 轻量 scorecard
- `usefulness = 2/3`
- `time_stability = 0/3`
- `cross_asset_stability = 0/3`
- `cost_trade_stability = 1/3`
- `deployability = 0/3`
- `hard-fail flags = no_positive_asset_pocket; full_stack_retention_collapse; false_start_still_high; single_repo_skeleton_only`
- `recommended_action = keep_P1`
- `why_now = 这刀先把“优化器存在 ≠ 结构能被自动洗白”说死，避免 Rank 146 因为方法层想象继续霸占默认 primary。`
- `main_weakness = 当前只验证了 repo 内置 EMA-ADX-VOL skeleton，尚未对 desk 更贴近的 EMA+PSAR / breakout-context skeleton 做最短 apples-to-apples compare。`

## 6. 回写顶板后的 desk 读法
- `Rank 146` 继续保留在 active Scout，但口径已从 `fresh intake admitted` 收紧到 **`one frozen-skeleton cut spent / no promote yet`**。
- 下一轮默认不再继续给它单独 Run 1；更合理的是转去做：
  - `Rank 146 vs Rank 111` 的最短 decisive compare，或
  - 直接把默认主资源让回 `Rank 111` 这类 evidence anchor。

## 7. 本轮结论
这轮最小 decisive cut 已完成，而且给出了明确否定式信息：
- Rank 146 目前**没有**因为 repo 自带的 optimizer skeleton 就获得升层资格；
- 它仍可留在 `keep_P1`，但默认只配当方法证据储备，不应继续占默认 primary。
