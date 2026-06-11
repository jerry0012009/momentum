# Rank 39 crypto pullback fresh intake：规则能写清，但当前仍应 park / source-template only

- 时间：2026-03-17 17:53 UTC
- 轮次：bot3 auto optimization / Trading Desk / Run 2 / Scout Fast Lane
- 当前 seat 状态：`Paper Seat / EMA = waiting_not_due`；本轮未见新的 `due-now / overdue` lane
- 本轮主点：`fresh intake` 一条新的 `paper / repo based` crypto 候选，并给出 intake-stage hard verdict
- 紧邻子点：把 authoritative board / digest index / reader-facing page 同步到最新 verdict

## 1. 开始前检查
### desk / board
- 先读了 `docs/AUTO_OPTIMIZATION_LOOP.md` 与 `docs/TODO.md` 顶部 `TRADING DESK BOARD`
- `Next 3 bot3 runs` 当前明确要求：
  - `Run 1` 若只是 waiting-window 不得空转
  - `EMA = waiting_not_due` 时默认转去 `Run 2 / Scout Fast Lane`
  - 当日 `P3 continuity` 有 hard cap，不应继续把 `Rank 17 / Rank 2 / Rank 29` 当默认主资源位

### repo / recent runs / dirty files
- 最近 optimization loop 重点：
  - `2026-03-17_1730_limited-attention-fastlane-park.md`
  - `2026-03-17_1740_rank34-authoritative-writeback.md`
- 本地 `git status --short` 显示存在大量与本轮无关的既有脏文件 / 未跟踪产物（包括多类 reports、artifacts、scripts、memory 文件等）
- 因此本轮默认 **不做 commit**，避免混提

## 2. active Scout 候选边际价值比较
当前比较结论：
- `Rank 17 / Rank 2 / Rank 29`：都属于 `P3 continuity`，这轮没有新的真实 `append/review need`，继续认领会撞上预算约束
- `Rank 30~38`：当前允许动作已基本消耗，且大多已被压回 `park`
- 因此这轮应按 board 直接切到 **新的 fresh intake**

在新 source 里，我优先比较了 3 条：
1. `Crypto Pullback Trading Strategy Based on Stochastic RSI and EMA Crossover`
2. `Efficient Price Channel Trading Strategy Based on 15-Minute Breakout`
3. `Fixed Range Volume Profile + Anchored VWAP Trend Identification`

边际价值排序：
- **第一：crypto pullback / StochRSI + EMA** —— 最接近当前 `crypto + pullback + 可直接写规则`
- 第二：15m breakout —— 有明显 `9:15 first candle` session mismatch，不像 24/7 crypto
- 第三：FRVP + AVWAP —— 参数与过滤层太厚，source intake 阶段就已显得过重

因此本轮只认领第一条，不并行展开其他候选。

## 3. 本轮执行内容
### 3.1 source intake hard verdict
对 `Rank 39 / crypto pullback / StochRSI + EMA crossover` 做 intake-stage 快筛：
- `trade on / trade off` 可以写清：
  - long：`close > EMA20` 且 `close < EMA9 / EMA14`，同时 `StochRSI_K < oversold`
  - short 端镜像
- source code 未见一眼可判死刑的 `lookahead / repaint / data leakage`

但当前仍然 **不该进 fast-lane replication queue**，核心 blocker 有 3 个：
1. `period=1d / basePeriod=1h` 与当前 desk 默认 `5m / 15m crypto` 主线不贴
2. 只有 `strategy.entry`，没有把 `exit / hold / overlap` 这些 execution unit 钉死
3. `pyramiding = 10` 会把 clean replication 与资金路径混在一起，不利于做最小诚实对比

### 3.2 hard verdict
- `Rank 39 / crypto pullback / StochRSI + EMA crossover`
- **当前 hard verdict：`park / source-template only`**
- 不进入当前 `clean replication queue`
- 不进入 `paper candidate pool`

更直白地说：
- 它是这轮 fresh source 里最值得先看的那条
- 但还只够当 **可参考的 pullback 入场模板**
- 还不够诚实地进入当前默认 Scout fast lane

## 4. 本轮产物
### deployable / reader-facing artifacts
1. `research/quant_digests/2026-03-17_1753_crypto-pullback-intake-park.md`
2. `reports/artifacts/literature/scout_rank39_crypto_pullback_source_intake_card.csv`
3. `reports/site/reading/trendline_alpha_scout/rank39_crypto_pullback_source_intake.html`

### board / index write-back
4. `docs/TODO.md`
   - 在 `Next 3 bot3 runs` 顶部追加 17:53 authoritative 补充
   - 新增 `Rank 39` 条目并写死当前 hard verdict
5. `research/quant_digests/INDEX.md`
   - 追加本轮 digest 索引

## 5. 最小验证
已完成的最小验证：
- `grep` 确认 `docs/TODO.md` 内已出现：
  - `Rank 39 crypto pullback`
  - `park / source-template only`
  - `2026-03-17 17:53 UTC`
- `grep` 确认 `research/quant_digests/INDEX.md` 已追加 17:53 条目
- `ls` 确认本轮 3 个新产物文件已落盘

未做的事：
- 没有重跑任何重型回测
- 没有追最新 bar
- 没有把本轮扩成 clean replication / stability pack

## 6. 对下一轮的影响
- 若下一轮还能拿到更合格的新 `paper / repo based 5m / 15m crypto` source，仍应优先继续 `fresh intake`
- 若拿不到，就可以更诚实地回退到 `Run 3 / tiny-live plumbing`
- 当前不建议继续默认重开 `Rank 39`，除非先把最小 `execution freeze` 补齐：
  - 固定 `BTC/ETH/SOL 120d 15m`
  - 明确 `next-bar open`
  - 明确 `hold N bars / reverse or no-overlap`
  - 禁用 `pyramiding`

## 7. commit / 邮件
- commit：未提交（避免与大量无关脏文件混提）
- 邮件：本轮完成后按要求发送中文摘要
