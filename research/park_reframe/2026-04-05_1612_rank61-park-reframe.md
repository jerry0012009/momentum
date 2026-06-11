# 2026-04-05 16:12 UTC — Rank 61 park reframe review

## 本轮对象
- `Rank 61 / lower-TF volume-delta polarity mismatch veto`
- 原始结论保留：`park / evidence pool`
- 本轮输出：`keep_park`

## 为什么这轮看 Rank 61
- 按 `bot6` 当前轮转口径，默认优先复盘 `Rank 50+` 的已 park 条目。
- 最近 7 天内，`Rank 50 / 51 / 52 / 54 / 55 / 57 / 58 / 59 / 62 / 73 / 80 / 87 / 103` 已被低频复盘；`Rank 61` 近期未被 `bot6` 触碰，且仍处在 `50~79` 号段。
- 这条线也具备一个表面上“看起来像还能救”的点：lower-TF signed flow / delta polarity 在直觉上并不荒谬，容易让人误以为只差实现细节，因此值得低频做一次“到底是旧 rank 可救，还是主题已经外流”的审计。

## 1) 原 rank 为什么 park
根据 `2026-03-18_1740_rank61-source-intake.md` 与 `2026-03-18_1800_rank61-clean-replication-park.md`：
- 原始想法是把 **setup 前最后 3~5 分钟的 lower-TF volume-delta polarity** 写成一个 shared veto：
  - long setup 需要子周期 delta 同向；
  - short setup 需要子周期 delta 同向；
  - 若 polarity mismatch，则 veto / 延后。
- 但最小 clean replication 后，结果并没有形成诚实的跨 setup、跨资产增量：
  - `ema_psar_long + opposite_delta_veto`：成本后仍约 `-3.60%`，且 `trade_count_retention≈38.10%`；
  - `fib_retest_long + opposite_delta_veto`：虽然约 `+0.71%`，但 `mean_trades≈4.0`、`retention≈36.36%`，更像薄 pocket；
  - `breakout_short + opposite_delta_veto`：仍约 `-3.28%`，且 `positive_asset_ratio=0`。
- 所以原 rank 被 park，不是因为“还没找到合适阈值”，而是因为：**这层 lower-TF polarity 作为 15m shared veto 的职责不够诚实，改善主要没有跨 lane 站住。**

## 2) 它更像 hard park 还是 soft park
**结论：`soft park`，但现在比原 park 时更偏硬。**

为什么还不直接叫 hard park：
- lower-TF signed flow / delta polarity 这件事本身并非伪命题；
- 原 replication 至少留下了一个很薄的 `fib_retest_long` 正 pocket，说明“参与方向一致性”并非完全没信息。

为什么又明显更偏硬：
- 这个 pocket 太薄，而且没有在 `ema_psar_long / breakout_short` 上同步出现；
- 原 rank 的 shared-veto 角色已经被审计过：一旦写回三条 15m archetype 共用门卫，就更像切样本，而不是稳定 gate；
- 最近新增证据把同主题不断往 **1m/3m microstructure raw-alpha / execution family** 推，而不是支持旧 rank 这层 shared 角色。

## 3) 有没有“可救信号”
**有，但很弱，而且不支持直接救原 rank。**

### 可救信号
1. `fib_retest_long` 上存在薄的正 pocket，说明“pre-entry participation alignment”不是完全无信息；
2. 最近新增的 microstructure 证据持续说明 signed flow / OFI / depth imbalance 主题本身仍有生命力：
   - `2026-04-02 extreme OFI / trade-flow continuation`：主题更像单资产极短周期 raw alpha；
   - `2026-04-04 signed-flow imbalance maker-conviction`：主题更像 `1m -> 5m` 可独立下单的 signed-flow alpha；
   - `2026-04-05 top20 depth imbalance × tight-spread continuation`：进一步把价值重心推向更快的 order-book / execution layer。

### 但这些信号为什么救不了旧 Rank 61
- 它们共同支持的是：**快频 microstructure 自身能做主语**；
- 它们并不支持：**把“最后 3~5 分钟 delta polarity”继续写成一个横跨 `ema/fib/breakout` 的 15m shared veto**；
- 换句话说，主题没死，但旧 rank 的职责层写错了。

## 4) 最值得改的唯一一刀是什么
如果只允许保留一条“唯一主修改轴”，那它应该是：

> **把 lower-TF delta polarity 从 `15m shared veto` 改写成 `1m/3m 单资产 microstructure admission / execution alpha`。**

也就是：
- 不再问“它能不能给三条 15m setup 当共同门卫”；
- 改问“当极短窗口 signed flow / depth imbalance 足够同向时，能不能直接形成快频 continuation / maker-skew / execution-timing 原语”。

## 5) 是否值得形成新的 derived hypothesis
**结论：不值得，本轮维持 `keep_park`。**

原因不是主题完全没价值，而是：
- 上面那一刀虽然是最诚实的方向，但它已经把主语从“旧的 Rank 61 shared veto”切换成“新的快频 microstructure raw alpha / execution family”；
- 这更像一个新的 fresh intake 主题，而不是对原 rank 的窄派生；
- 若硬把它写成 `Rank 61b`，会稀释原 `park` verdict 的审计意义，也会把 bot6 变成“帮任何 old rank 换壳重开”的机器。

因此，本轮最诚实的做法不是 draft 一个伪窄派生，而是明确记录：
- `Rank 61` 原结论保留；
- 它只剩下主题层面的 residual value；
- 这些 residual value 更自然外流到新的 microstructure raw-alpha / execution intake，而不是旧 rank 的 derived hypothesis。

## 单轮审查模板回答
### 原 rank 为什么 park？
因为 lower-TF delta polarity 作为 15m shared veto 没有形成跨 setup、跨资产的稳定增量；改善只留下很薄的局部 pocket，且伴随明显 retention 压缩。

### 它更像 hard park 还是 soft park？
`soft park`，但已明显向 `hard park` 偏移。

### 有没有“可救信号”？
有。`fib_retest_long` 薄 pocket + 最近连续出现的 signed-flow / OFI / depth imbalance 新证据，说明主题本身没死。

### 最值得改的唯一一刀是什么？
把它从 `15m shared veto` 改成 `1m/3m 单资产 microstructure admission / execution alpha`。

### 是否值得形成新的 derived hypothesis？
不值得。因为这已经不是原 rank 的诚实窄派生，而更像新的 fresh intake 家族。

## 对队列的写回结论
- `Rank 61`：`keep_park`
- 建议备注：
  - 原 `park` verdict 保留；
  - 结论为“soft park，但明显更偏硬”；
  - 最近新增的 signed-flow / OFI / depth-imbalance 证据说明，该主题若还有残余价值，更像新的 `1m/3m microstructure raw-alpha / execution family`，而不是旧 lower-TF polarity shared veto 的诚实窄派生；
  - 当前不足以诚实派生 `Rank 61b`。

## 文件与工作区备注
- 本轮只做最小必要写回：新增本日志、更新 `research/park_reframe/INDEX.md`、更新 `docs/PARK_REFRAME_QUEUE.md`。
- 未改 `docs/TODO.md` 顶部排班。
- 当前仓库存在无关脏文件，本轮不做 commit，避免混提。
