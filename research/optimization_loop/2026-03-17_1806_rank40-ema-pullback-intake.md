# Rank 40 EMA pullback source intake：这次先给下一手 clean replication 预算，不急着直接 park

- 时间：2026-03-17 18:06 UTC
- 轮次：bot3 auto optimization / Trading Desk / Run 2 / Scout Fast Lane
- 当前 seat 状态：`Paper Seat / EMA = waiting_not_due`；当前未见新的 `due-now / overdue` lane
- 本轮主点：从新的 repo source 里认领 1 条更像下一手 clean replication 的 fresh intake，并给出 authoritative hard verdict
- 紧邻子点：把结论同步到 `docs/TODO.md` 顶板、quant digest index 和 reader-facing 网页

## 1. 开始前检查
### desk / board
- 先读了 `docs/AUTO_OPTIMIZATION_LOOP.md` 与 `docs/TODO.md` 顶部 `TRADING DESK BOARD`
- 当前顺序仍然是：
  - `Run 1`：EMA 若无 `due-now / overdue` 不得空转
  - `Run 2`：Scout Fast Lane 继续比较 active 候选边际价值
  - `Run 3`：只有当本轮拿不到合格 source 时才诚实回退
- 当前对 active Scout 的边际价值判断：
  - `Rank 17 / Rank 2 / Rank 29` 仍是 `P3 continuity`，当前没有真实 `append/review need`
  - `Rank 30~39` 当前允许动作基本已消耗，且多数已被压回 `park`
  - 因此本轮继续留在 `Run 2 / Scout Fast Lane` 合规

### repo / recent runs / dirty files
- 最近几轮重点：`Rank 37 -> Rank 38 -> Rank 39` 的 fast-lane fresh intake / clean replication / park
- 当前 git 工作区仍有大量与本轮无关的既有脏文件 / 未跟踪产物
- 因此本轮默认 **不做 commit**，避免混提

## 2. active fresh source 边际价值比较
本轮实际比较了 3 条新的 repo source（均来自 `fmzquant/strategies`）：
1. `EMA Pullback Strategy`
2. `Keltner Channel Pullback Strategy`
3. `VWAP Deviation Band and Volatility Filter Trading Strategy`

当前 desk 语境下的排序：
- **第一：EMA Pullback Strategy**
  - 规则短
  - pullback 语义清楚
  - 至少带了 `pullback swing stop + 2R take-profit` 这层最小交易单元
- 第二：Keltner Channel Pullback
  - 能写方向和回抽，但 exit / hold 仍偏松
- 第三：VWAP deviation band + volatility filter
  - session anchoring 重、结构层太厚，source intake 阶段就显得过拟合风险偏高

因此本轮只正式认领第一条，不并行展开其余两条。

## 3. 本轮执行内容
### 3.1 source intake hard verdict
对新的 `Rank 40 / EMA pullback / three-EMA trend continuation` 做 intake-stage 快筛：
- `trade on / trade off` 能写清：
  - long：总体趋势仍偏多，价格先走出顺势方向，随后回踩短 EMA 但不深穿过滤 EMA，并在形成更高低点后重新站回短 EMA
  - short 端镜像
- 当前 source 描述未见一眼可判死刑的 `lookahead / repaint / data leakage`
- 相比 `Rank 39`，它更接近当前 fast-lane 需要的 execution freeze：
  - 不只是 entry idea
  - 还给了 `回调 swing stop`
  - 以及 `2R take-profit`

### 3.2 hard verdict
- `Rank 40 / EMA pullback / three-EMA trend continuation`
- **当前 hard verdict：`admit_to_clean_replication_queue`**
- 还不进入 `paper candidate pool`
- 但值得拿下一轮唯一一次最小 clean replication 预算

更直白地说：
- 这不是说它已经被证明有效
- 而是说：与当前已 park 的新 source 相比，它终于达到“值得下一手真正跑一个最小 clean-room yes/no 检查”的诚实程度

## 4. 本轮产物
### deployable / reader-facing artifacts
1. `research/quant_digests/2026-03-17_1806_rank40-ema-pullback-intake.md`
2. `reports/artifacts/literature/scout_rank40_ema_pullback_source_intake_card.csv`
3. `reports/site/reading/quant_digests/2026-03-17_1806_rank40-ema-pullback-intake.html`

### board / index write-back
4. `docs/TODO.md`
   - 在 `Next 3 bot3 runs` 顶部补 `2026-03-17 18:06 UTC` authoritative note
   - 新增 `Rank 40` 条目并写死当前 verdict = `admit_to_clean_replication_queue`
5. `research/quant_digests/INDEX.md`
   - 追加本轮 digest 索引

## 5. 最小验证
已完成的最小验证：
- 运行 `python3 scripts/build_quant_digest_site.py`
- 确认已生成：
  - `reports/site/reading/quant_digests/2026-03-17_1806_rank40-ema-pullback-intake.html`
  - `reports/site/reading/quant_digests/report.html`
- `grep / 读取` 确认 `docs/TODO.md` 已出现：
  - `2026-03-17 18:06 UTC`
  - `Rank 40 EMA pullback / three-EMA trend continuation`
  - `admit_to_clean_replication_queue`
- 确认 source intake card 与 digest 文件已落盘

未做的事：
- 没有重跑任何重型回测
- 没有追最新 completed bar
- 没有把这轮扩成 clean replication / stability pack

## 6. 对下一轮的影响
- 若下一轮继续留在 `Run 2 / Scout Fast Lane`，默认应先给 `Rank 40` 那 **1 次最小 clean replication**：
  - 固定 `BTC/ETH/SOL 120d 15m` cache
  - `signal bar close -> next-bar open`
  - `no-overlap`
  - `pullback swing stop + 2R target`
  - 只回答 `post-cost return / positive_asset_ratio / trade_count / time-pocket honesty`
- 若这一刀结果不干净，应快速压回 `park / evidence pool`
- 默认不要继续回头磨 `Rank 39`，也不要在 tiny-live 同义文档上空转

## 7. commit / 邮件
- commit：未提交（避免与大量无关脏文件混提）
- 邮件：本轮完成后按要求发送中文摘要
