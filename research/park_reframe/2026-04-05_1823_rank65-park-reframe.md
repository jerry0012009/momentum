# 2026-04-05 18:23 UTC — Rank 65 park reframe review

## 本轮对象
- `Rank 65 / perp-stress resetComplete / re-arm gate`
- 原始结论保留：`park / evidence pool`
- 本轮输出：`keep_park`

## 为什么这轮看 Rank 65
- 按 `bot6` 当前轮转口径，默认优先复盘 `Rank 50+` 的已 park 条目。
- 最近 7 天内，`Rank 50 / 51 / 52 / 54 / 55 / 57 / 58 / 59 / 61 / 62 / 73 / 80 / 87 / 103` 已被低频复盘；`Rank 65` 近期未见 `bot6` 单独复盘，且仍处在 `50~79` 号段。
- 这条线也值得补一次审计：它当初不是“效果差一点”，而是**最小公开代理口径下连 coverage 都没有**；这类条目很容易被误读成“再调阈值就行”，所以需要明确回答一次——它到底还有没有诚实的窄 reframe。

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/optimization_loop/2026-03-18_1940_rank65-source-intake-guard-passed.md`
- `research/optimization_loop/2026-03-18_2018_rank65-clean-replication-park.md`
- `research/quant_digests/2026-03-20_0511_basis-dislocation-short-veto.md`
- `research/quant_digests/2026-03-21_0302_funding-oi-crowding-breadth-overlay.md`
- `research/quant_digests/2026-03-23_1632_perp-premium-gap-mean-reversion-fullstack.md`

## 1) 原 rank 为什么 park
根据 `2026-03-18_1940_rank65-source-intake-guard-passed.md` 与 `2026-03-18_2018_rank65-clean-replication-park.md`：
- 原始想法是把 **perp stress event 之后是否已经 resetComplete、能否重新 re-arm** 写成三条 15m archetype 的 shared gate：
  - `ema_psar_long`
  - `fib_retest_long`
  - `breakout_short`
- 最小 clean replication 的定义很明确：
  - `stress_event = |basis| 偏离 + OI impulse + wick/volume 异常`
  - `resetComplete = basis 回中性 + OI flush + ATR 压缩`
  - 数据只用公开可得的单交易所代理（spot/perp basis + OI + ATR/volume），统一 `next-bar open + no-overlap + hold 8 bars`。
- 但跑完后不是“效果一般”，而是更早一步就失败了：**strict proxy 下完全没有事件 coverage**。
  - `BTC-USD: stress_events=0, reset_complete_bars=0`
  - `ETH-USD: stress_events=0, reset_complete_bars=0`
  - `SOL-USD: stress_events=0, reset_complete_bars=0`
- 所以三臂结果在 6bps/side 下完全一样：`no_gate = stress_pause_only = stress_pause_reset_rearm`。

翻成人话：
- 原 rank 被 park，不是因为“有事件但没效果”；
- 而是因为：**把单币 perp-stress→resetComplete→re-arm 写成 15m shared gate，在当前最小公开代理口径下连第一层 coverage 都立不住。**

## 2) 它更像 hard park 还是 soft park
**结论：`soft park`，但已经明显偏硬。**

为什么还保留一点 soft：
1. 原 clean replication 明确记录过：如果显著放松阈值，`ETH/SOL` 会出现少量事件；说明“perp stress / reset”主题本身不一定是伪命题。
2. basis / funding / OI 这组衍生品变量本身最近仍持续有信息量，不是已经被市场完全榨干的死变量。

为什么又明显偏硬：
1. 原 rank 的失败是 **coverage fail**，不是可微调的小 pocket fail；
2. 一旦需要明显放松阈值、换 venue、补 liquidation feed 或跨所拼接，实际上就已经离开了原 source-intake 冻结的最小诚实定义；
3. 最近新增证据支持的也不是“把单币 resetComplete gate 再微调一下”，而是把主题改写成别的职责层。

## 3) 有没有“可救信号”
**有，但它们更像主题外流，不支持直接救原 Rank 65。**

### 可救信号 A：basis / OI 主题仍有信息量
- `2026-03-20_0511_basis-dislocation-short-veto.md` 说明：极端负基差 × OI 不扩张，更像 `breakout_short` 的 `no-short gate`；
- `2026-03-21_0302_funding-oi-crowding-breadth-overlay.md` 说明：funding × OI 更诚实的宿主，是 **cross-symbol crowding breadth overlay**，而不是单币逐根阈值；
- `2026-03-23_1632_perp-premium-gap-mean-reversion-fullstack.md` 进一步说明：若把 basis / premium 当主语，它甚至更像一条可独立落地的短周期 raw-alpha family。

### 但这些信号为什么救不了旧 Rank 65
因为它们共同指向的是：
1. **单币、逐根、strict proxy 的 resetComplete/re-arm gate 并不是最自然的角色层**；
2. 若保留 shared filter 语义，更像 `cross-symbol crowding breadth overlay`；
3. 若保留衍生品 dislocation 语义，更像新的 `premium/basis mean-reversion raw alpha`；
4. 这两条都已经不是原 Rank 65 的那层“stress_event 后能否 re-arm”的职责。

## 4) 最值得改的唯一一刀是什么
如果只保留一条“唯一主修改轴”，最诚实的一刀会是：

> **把单币 perp-stress resetComplete / re-arm gate，降级成 cross-symbol funding × OI crowding breadth shared size/veto overlay。**

也就是：
- 不再逐根判断某个币“刚经历 stress 后是否 reset 完成”；
- 改成在 15m bar close 上，看 top-liquid perp universe 的 `funding × OI` 拥挤广度，作为 long/short continuation 的仓位折扣或 veto 层；
- 让它服务现有 setup，而不是继续伪装成一个单币 event-reset gate。

## 5) 是否值得形成新的 derived hypothesis
**结论：不值得，本轮维持 `keep_park`。**

原因：
1. 上面那一刀虽然是最自然的救法，但它已经把主语从“单币 stress-reset-rearm”改成了“横截面 crowding breadth overlay”；
2. 这会抹平原 `park` verdict 的审计意义——原 verdict 失败的是 `single-symbol resetComplete gate`，不是 funding/OI 主题整体失败；
3. 这条唯一可救轴，与现有 overlay family 已明显接近：
   - `Rank 21b` 已占了更上位的 low-frequency risk overlay 位置；
   - `Rank 4c` 已占了 spread-dislocation shared overlay 位置；
   - 再硬写一个 `Rank 65b`，更像 overlay family 的重复开枝，而不是 bot2 可直接判断的全新窄对象。
4. 若后面真的要追，更诚实的做法应是：
   - 要么作为新的 `funding/OI breadth overlay` fresh intake；
   - 要么直接去追 `premium/basis` raw-alpha family；
   - 而不是借 `Rank 65` 的名义续命。

## 单轮审查模板回答
### 原 rank 为什么 park？
因为在最小公开代理口径下，`stress_event -> resetComplete` 连 coverage 都没有，三臂结果完全相同；失败点是单币 reset/re-arm gate 这层职责本身，而不是简单的参数没调对。

### 它更像 hard park 还是 soft park？
`soft park`，但已经明显偏硬。

### 有没有“可救信号”？
有。basis / funding / OI 主题最近仍有信息量；但这些信息更支持 crowding breadth overlay 或 premium/basis raw alpha，不支持原 Rank 65 的单币 re-arm gate。

### 最值得改的唯一一刀是什么？
把单币 `perp-stress resetComplete / re-arm gate` 改写成 `cross-symbol funding × OI crowding breadth shared size/veto overlay`。

### 是否值得形成新的 derived hypothesis？
不值得。因为这已经不是原 rank 的诚实窄派生，而且与现有 overlay family 高度接近。

## Final verdict
- `keep_park`
- original verdict kept: `park`
- short note: `soft park，但已明显偏硬；原 Rank 65 的 blocker 是单币 strict proxy 下 coverage 不成立，而最近新增 funding / OI / premium 证据又把主题推向 cross-symbol crowding overlay 或独立 basis raw-alpha family，不足以再诚实派生 Rank 65b`

## File actions
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`
- 未改：`docs/TODO.md`

## Commit
- 本轮默认不做 commit。
- 原因：仓库存在无关脏文件；本轮只做最小必要文档改动，避免混提。
