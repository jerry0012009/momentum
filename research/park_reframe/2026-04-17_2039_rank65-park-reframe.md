# 2026-04-17 20:39 UTC — Rank 65 park reframe review

## 本轮对象
- `Rank 65 / perp-stress resetComplete / re-arm gate`
- 原始结论保留：`park / evidence pool`
- 本轮输出：`keep_park`

## 为什么这轮看 Rank 65
- 按当前 `bot6` 轮转规则，仍优先看 `50+`，其中 `Rank 65` 属于 `50~79`。
- 最近 `7` 天内未见 `Rank 65` 被 `bot6` 再复盘，符合低频轮换要求。
- 它属于那种很容易被误读成“再松一点阈值就行”的条目；但过去两周 funding / basis / OI 相关 digest 明显增多，正适合再确认一次：这些新证据到底是在救旧 `Rank 65`，还是只是在把主题外流到别的宿主。

## Read set
### 必读
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`

### 本轮补读
- `research/park_reframe/2026-04-05_1823_rank65-park-reframe.md`
- `research/optimization_loop/2026-03-18_2018_rank65-clean-replication-park.md`
- `research/quant_digests/2026-04-12_0714_negative-funding-boundary-short-alpha.md`
- `research/quant_digests/2026-04-16_1119_fundingbasis-thresholdcollapse-transfer.md`
- `research/quant_digests/2026-04-16_1615_fundingdesign-residual-premiumfade-alpha.md`
- `research/quant_digests/2026-04-16_1731_fundingcarry-hysteresis-thresholdflat-alpha.md`

## 1) 原 rank 为什么 park
原始审计结论来自 `2026-03-18_2018_rank65-clean-replication-park.md`。

`Rank 65` 想表达的是：
- 当 perp 市场刚经历一轮 `stress event`（basis 偏离、OI impulse、wick/volume 异常）后，
- 先不要立刻继续顺着做，而要等到 `resetComplete`（basis 回中性、OI flush、ATR 压缩）出现，
- 再允许现有三条 15m archetype 重新 `re-arm`：
  - `ema_psar_long`
  - `fib_retest_long`
  - `breakout_short`

但它不是“有样本但效果不佳”而被 park；真正的 blocker 更前一层：
- 在最小公开代理、单币、单 venue、strict proxy 定义下，`stress_event` 与 `resetComplete` **几乎没有 coverage**；
- `BTC / ETH / SOL` 的 `stress_events=0`、`reset_complete_bars=0`；
- 所以 `no_gate = stress_pause_only = stress_pause_reset_rearm`，三臂结果完全一致。

也就是说，原 `Rank 65` 被 park，不是因为“主题完全无效”，而是因为：

> **把 perp-stress → resetComplete → re-arm 写成单币 15m shared gate，在最小诚实代理口径下连首层覆盖都站不住。**

## 2) 它更像 hard park 还是 soft park
**本轮判断：仍是 `soft park`，但比 2026-04-05 那轮更接近 `hard with consumed residual`。**

为什么还没直接写成 hard park：
1. funding / basis / OI 这些变量最近仍持续产出新证据，说明衍生品拥挤 / 定价偏离主题本身没死；
2. 原 `coverage fail` 更像“职责层写错”，不等于底层变量完全无信息。

为什么又更接近 hard：
1. 最近新增证据没有把 `single-symbol resetComplete gate` 这层职责救回来；
2. 新证据反而更一致地说明：这些变量要么适合做 **event-driven / raw-alpha 宿主**，要么适合做 **post-cost / hysteresis / admission filter**；
3. 一旦这么改，主语就已经不再是旧 `Rank 65` 的 `stress-reset-rearm` 语义，而是在借新壳给旧 rank 续命。

## 3) 有没有“可救信号”
**有，但这些信号继续指向“主题外流”，而不是救活旧 Rank 65。**

### 可救信号 A：funding boundary / crowding 的事件性仍然有信息
`2026-04-12_0714_negative-funding-boundary-short-alpha.md` 把主题收窄成：
- `most-negative funding coin × settlement-boundary continuation short`
- 更像高 beta alt 的 `1m/3m` 事件驱动短打

这说明衍生品拥挤变量不是没信息，问题是：
- 信息更像 **settlement-boundary event alpha**，
- 而不是单币 `resetComplete` 之后再放行三条共享 setup。

### 可救信号 B：basis/funding 更像 delta-neutral / raw-alpha admission，而不是逐根 shared gate
`2026-04-16_1119_fundingbasis-thresholdcollapse-transfer.md`、
`2026-04-16_1615_fundingdesign-residual-premiumfade-alpha.md`、
`2026-04-16_1731_fundingcarry-hysteresis-thresholdflat-alpha.md`
共同给出的方向很一致：
- 真正值得保留的是 `basis/funding dislocation` 本身的交易对象；
- 关键问题是 `post-cost admission`、`threshold collapse`、`entry/exit hysteresis`；
- 也就是它们更像 **独立 raw-alpha / carry / premium-fade family**，或者更上位的 **admission framework**。

### 这些信号为什么仍然救不了旧 Rank 65
因为它们都没有回答旧 `Rank 65` 的核心问题：

> “单币 perp stress 之后，是否已经 resetComplete，因此可以诚实地对三条 15m archetype 重开闸门？”

最近的新证据回答的是别的问题：
- 哪些 funding/premium dislocation 本身值得交易；
- 哪些 event boundary 值得短打；
- 哪些 admission / hysteresis 框架可以避免阈值塌缩。

它们都不是对旧 `resetComplete/re-arm gate` 的直接修复。

## 4) 最值得改的唯一一刀是什么
如果强行只留 **1 条唯一主修改轴**，最自然的一刀仍然是：

> **把单币 `perp-stress resetComplete / re-arm gate`，改写成 `funding/basis dislocation` 的 post-cost admission / veto 层。**

更具体一点：
- 不再尝试定义某个币“已经 reset 完成、可重新 re-arm”；
- 只在现有 setup 触发时，用 funding/basis dislocation 的可交易性条件做 allow/deny；
- 第一轮只测 `baseline vs post-cost admission / hysteresis veto`，不偷带第二轴。

但问题也正出在这里：
- 这刀已经把主语从 `stress-reset-rearm` 改成了 `tradeability admission`；
- 它更像新的 funding/basis family 公共模块，而不是旧 `Rank 65` 的诚实窄派生。

## 5) 是否值得形成新的 derived hypothesis
**结论：不值得，维持 `keep_park`。**

原因有四条：
1. 原 rank 的失败点是 `single-symbol strict-proxy coverage fail`，这一点没有被新证据推翻；
2. 最近的“可救信号”都在把主题推向新的 event-driven raw alpha、delta-neutral dislocation、或 admission/hysteresis 框架；
3. 这些新方向虽然有价值，但已经不再保留旧 `Rank 65` 的审计边界；
4. 如果现在硬写一个 `Rank 65b`，大概率只是把“旧 gate 失败”改写成“新 family 值得做”，这会稀释原 `park` verdict 的意义。

## 单轮审查模板回答
### 原 rank 为什么 park？
因为在最小公开代理与 strict proxy 定义下，`stress_event -> resetComplete` 几乎没有 coverage，三臂结果完全一致；失败的是 `single-symbol reset/re-arm gate` 这层职责，而不是简单阈值没调好。

### 它更像 hard park 还是 soft park？
`soft park`，但比 2026-04-05 那轮更接近 `hard with consumed residual`。

### 现有证据里是否存在“可救信号”？
有。funding / basis / OI 主题仍然有信息，但它们更像 event-driven raw alpha、delta-neutral dislocation，或 post-cost admission / hysteresis 模块，不再像旧 Rank 65 的 re-arm gate。

### 最值得改的唯一一刀是什么？
把 `perp-stress resetComplete / re-arm` 改写成 `funding/basis dislocation` 的 post-cost admission / veto 层。

### 是否值得形成新的 derived hypothesis？
不值得。因为这条修改已经越过旧 rank 的审计边界，变成新的 family-level 模块，不是诚实的 `Rank 65b`。

## Final verdict
- `keep_park`
- original verdict kept: `park`
- short note: `soft park，但比 4 月 5 日那轮更接近 hard with consumed residual；原 single-symbol stress-reset-rearm gate 的 coverage blocker 没被推翻，而 4 月中旬新增的 funding boundary / threshold-collapse / premium-fade / hysteresis 证据继续说明，衍生品拥挤变量若还有 residual value，也更像新的 event-driven raw-alpha 或 post-cost admission family，而不是足以再诚实派生旧 Rank 65 的 Rank 65b`

## File actions
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`
- 未改：`docs/TODO.md`

## Commit
- 本轮默认不做 commit。
- 原因：仓库存在无关脏文件；本轮只做最小必要文档改动，避免混提。
