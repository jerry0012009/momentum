# 2026-03-18 03:08 UTC — Rank 43 ATR retest zone + bounce reclaim：最小 clean replication 后维持 park

## 为什么这次选这个
- 先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 与 `Next 3 bot3 runs` 执行。
- `Run 1 / EMA` 仍处于 `running paper / waiting_not_due`，这一轮不能把 paper refresh 硬做成主点。
- 当前 `P3` continuity 已有日预算约束，`Rank 32b` 也刚完成 `P1 -> P2 -> P3` 三连最小检查，不该继续默认占用 `Scout Seat` 主资源。
- 因此这轮回到 `Run 2 / Rank 43`：把 intake 阶段的 `ATR retest zone + bounce reclaim` 做掉那 **1 次最小 clean replication**，直接给 hard verdict。

## 本轮主点
- **主点**：完成 `Rank 43 / TheVision333/trading-bot` 的 clean-room replication，并补齐最小 `Light Stability Pack`。
- **紧邻子点**：把 verdict 同步回 `docs/TODO.md` 顶板，并生成 reader-facing 网页落点。

## active Scout 边际价值比较
- `P3 continuity`：当前没有新的真实 due-now append/review need，而且有日预算上限，不该继续默认认领。
- `P2 / P1`：本轮 authoritative board 已把 `Rank 43` 作为下一个待执行对象；它比再开新 intake 更接近立即产出 hard verdict。
- `Run 3 / tiny-live plumbing`：只有在 `Run 2` 也被真实 blocker 卡住时才该回退；本轮没有这个 blocker。

## 做了什么
1. 新增最小 clean replication 脚本：
   - `scripts/build_rank43_atr_retest_clean_replication.py`
2. 固定 clean-room 规则：
   - `trade on = confirmed swing breakout -> ATR retest zone -> no deep invalidation -> bounce reclaim`
   - `trade off = 无 breakout / 回踩超时 / 深穿失效 / bounce reclaim 失败`
3. 固定样本与执行口径：
   - `BTC / ETH / SOL`
   - 本地 `120d 15m` cache
   - `1h EMA20/50` 只做 completed-bar 结构过滤
   - `next-bar open`
   - `no-overlap`
   - 固定持有 `8` 根 15m bar
4. 补齐最小 `Light Stability Pack` 四项：
   - 时间稳定性：`time_stability.csv`
   - 参数稳定性：`parameter_stability.csv`
   - 跨标的稳定性：`asset_summary.csv`
   - 成本 / 交易数稳定性：`cost_trade_stability.csv`
5. 产出 reader-facing 网页与 artifact：
   - `reports/site/factors/scout_rank43_atr_retest_bounce_15m/report.html`
   - `reports/artifacts/scout_rank43_atr_retest_bounce_15m/*`
6. 回写指挥板：
   - `docs/TODO.md` 中把 `Rank 43` 从 `admit_to_clean_replication_queue` 更新为最终本轮 verdict。

## 验证 / 证据
### 1) 相对 breakout-only，retest 版本确实更诚实
在 `6bps/side` 下：
- `confirmed_breakout_only`：
  - `mean_total_return ≈ -8.23%`
  - `positive_asset_ratio = 0/3`
  - `mean_false_break_rate ≈ 37.04%`
- `atr_zone0.5_timeout20`：
  - `mean_total_return ≈ +0.61%`
  - `positive_asset_ratio = 1/3`
  - `mean_false_break_rate ≈ 29.79%`

换句话说：**ATR 回踩区 + bounce reclaim` 这层确认，确实比“确认突破就直接追”更干净。**

### 2) 但它还不够干净到进候选池
主变体 `atr_zone0.5_timeout20` 在 `6bps/side` 下虽然转正，但：
- `positive_asset_ratio` 只有 `33.33%`
- 时间稳定性三桶里，中间桶明显转负：
  - `bucket_1 ≈ +2.12% / 66.67%`
  - `bucket_2 ≈ -4.31% / 33.33%`
  - `bucket_3 ≈ +2.74% / 66.67%`
- 成本一上去就重新转负：
  - `10bps/side ≈ -8.54%`
  - `15bps/side ≈ -18.83%`
  - `20bps/side ≈ -27.96%`

所以当前更诚实的读法不是 `P1`，更不是 `paper candidate`，而是：
**它是一个有用的 confirmation layer 证据，但还不是值得继续占 Scout 主资源的候选。**

### 3) 参数邻域没有给出足够强的“稳定平台”
`0.4~0.6 ATR`、`timeout 16~20` 的邻域里，`6bps/side` 只有最紧邻的几组能勉强贴近 0 或略正；一旦成本上调，就整体回到负区。
这说明它目前更像：
- 能改善 false-break rate 的过滤层；
- 但还不是可单独扛 15m alpha 的稳定 fast-lane 候选。

## 硬结论
- **本轮 hard verdict**：`Rank 43 -> park / evidence pool`
- **一句话原因**：它改善了 breakout-only 的假突破率和收益方向，但跨资产与时间 pocket 还不够稳，成本稍微上来就重新塌回负值。

## 风险 / 边界
- 这轮仍是最小 replication，不是完整 deployment-grade strategy study。
- 当前持有期固定为 `8` 根 15m bar，主要用于快筛；不应被误读为最终执行模板。
- 这条线更像“确认层有用”，不等于“确认层本身就足够当 alpha 主信号”。

## 下一步建议
- 若下一轮 `EMA` 仍是 `waiting_not_due`，默认**不要**继续磨 `Rank 43` 文案或 admission wording。
- 按当前顶板，应回到新的 `fresh paper / repo based 5m / 15m crypto intake`；除非出现真实会改变 `Rank 43` 层级的最小检查，否则不该再给它默认预算。

## 产出清单
- `scripts/build_rank43_atr_retest_clean_replication.py`
- `reports/artifacts/scout_rank43_atr_retest_bounce_15m/overall_summary.csv`
- `reports/artifacts/scout_rank43_atr_retest_bounce_15m/asset_summary.csv`
- `reports/artifacts/scout_rank43_atr_retest_bounce_15m/time_stability.csv`
- `reports/artifacts/scout_rank43_atr_retest_bounce_15m/parameter_stability.csv`
- `reports/artifacts/scout_rank43_atr_retest_bounce_15m/cost_trade_stability.csv`
- `reports/artifacts/scout_rank43_atr_retest_bounce_15m/trades_primary_6bps.csv`
- `reports/site/factors/scout_rank43_atr_retest_bounce_15m/report.html`
- `docs/TODO.md`

## 提交情况
- 未提交。
- 原因：工作区存在大量与本轮无关的既有脏文件 / 未跟踪产物；本轮只做 selective write-back，不适合混提。
