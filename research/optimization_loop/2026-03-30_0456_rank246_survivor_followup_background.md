# 2026-03-30 04:56 UTC · Rank 246 survivor follow-up — clean replication not enough, back to background/P0

- policy read: `docs/BOT2_BOT3_POLICY.md`
- runtime read: `docs/BOT2_BOT3_STATE.md`
- executed cycle item: `Rank 246 / false structural reclaim short failure-followthrough`
- scope rule: 只执行当前排在最前的 pending 小点；不重排后续 `cycle_plan`

## 本轮要回答的唯一问题
`Rank 246 / false structural reclaim short failure-followthrough` 作为当前唯一合法 survivor，是否能在冻结同一 `BTC/ETH/SOL, 120d, 15m, 6bps/side` 与同一事件锚定义下，留下独立、干净、可复现、且不靠极端砍样本的成本后 pocket，从而值得升 `P2`？

## replication 口径
- 复用 `scripts/build_rank31_chanlun_second_buy_clean_replication.py` 的同一 clean-room 数据与事件锚：
  - universe：`BTC / ETH / SOL`
  - sample：`120d`
  - bar：`15m`
  - fee：`6bps/side`（并额外看 `20bps/side` sanity）
  - 原事件：`structural_higher_low_reclaim`
- survivor 只做这一刀：
  - 先检测原 long-side `structural reclaim` 事件；
  - 若在固定 `4 bars` lookahead 内出现 `close back under reclaim level`，把它视为 `false reclaim`；
  - 在该失败 bar 的 `next-bar open` 做 `short`，持有 `8 bars`；
  - 不叠加第二层 regime/filter/exit 轴，不回退成泛 failure family。

## 关键结果
### 6bps/side
- `BTC`: `41` 笔，`win_rate=43.9%`，`avg_net_ret≈-0.18%`，`total_return≈-7.30%`
- `ETH`: `53` 笔，`win_rate=35.8%`，`avg_net_ret≈-0.30%`，`total_return≈-15.22%`
- `SOL`: `75` 笔，`win_rate=46.7%`，`avg_net_ret≈-0.18%`，`total_return≈-12.96%`
- cross-asset 汇总：`mean_total_return≈-11.83%`，`positive_asset_ratio=0/3`，`mean_trades≈56.3`

### 20bps/side sanity
- `BTC total_return≈-17.37%`
- `ETH total_return≈-26.93%`
- `SOL total_return≈-29.46%`
- cross-asset 汇总：`mean_total_return≈-24.59%`，`positive_asset_ratio=0/3`

## 这一步改变系统认知的地方
1. **它不是“太少样本、先留着再说”的那种 survivor。**
   - 三个资产合计已有 `169` 笔交易；
   - 但 `6bps/side` 下三腿全部为负，说明问题不是“只差多看几笔”。
2. **false reclaim 的 short followthrough 没有形成独立 pocket。**
   - 若这条 residual 真有独立信息，至少应出现跨资产不全灭、或某一腿能明显盖过成本；
   - 现在 `positive_asset_ratio=0/3`，且连 `BTC` 这条最接近中性的腿也仍为负。
3. **因此它更像原 long reclaim 失败边界的副产物，而不是值得升级的新对象。**
   - 这满足本轮 success criterion 的否定分支：replication 不干净，且没有留下足够独立增量；
   - survivor 预算应当当场用尽，而不是继续拖成第二次 follow-up。

## 正式结论
- `Rank 246 / false structural reclaim short failure-followthrough`：**不升 `P2`，回 `background/P0`**。
- 原因不是缺数据，而是固定口径下已经给出足够干净的负结论：
  - `6bps/side` 三资产全负；
  - `positive_asset_ratio=0/3`；
  - 交易数并不稀薄；
  - 加到 `20bps/side` 只会更差。

## Runtime writeback
- `Surviving candidate slot.current_target -> none`
- `Surviving candidate slot.followup_budget_remaining -> 0`
- `Fresh intake slot.current_target -> none`
- `Background pool.latest_parked -> Rank 246 survivor follow-up 用尽后回 background/P0`
- `cycle_plan[1]` 写成 `done`，并把结果收口为：`Rank 246` 的唯一 survivor clean replication 已确认三资产成本后全负，不升 `P2`，回 `background/P0``

## 本轮 reader-facing 变化
有真实推进：`Rank 246` 完成了唯一允许的 survivor follow-up，并得到正式层级结论（不升 `P2`，回 `background/P0`）；因此应刷新首页并发送邮件摘要。
