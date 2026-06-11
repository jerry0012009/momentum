# 2026-04-16 14:10 UTC — Rank 61 park reframe review

## 本轮对象
- `Rank 61 / lower-TF volume-delta polarity mismatch veto`
- 原始结论保留：`park / evidence pool`
- 本轮输出：`keep_park`

## 为什么这轮看 Rank 61
- 按 `bot6` 当前轮转口径，默认优先复盘 `Rank 50+` 的已 park 条目。
- `Rank 61` 上次 park-reframe 复盘是 `2026-04-05 16:12 UTC`，已超过 `7` 天；近期 `50+` 号段里更适合低频回看的条目不多。
- 4 月 11~14 日新增了三条直接相关的 microstructure 旁证：
  - `2026-04-11_2010_stacked-orderflow-vote-shell.md`
  - `2026-04-13_1523_spreadshock-imbalance-completion-mr-alpha.md`
  - `2026-04-14_0006_smallflow-nolargeconfirm-fade-alpha.md`
- 本轮要回答的不是“订单流主题死没死”，而是：这些新证据是否足以把旧 `Rank 61` 诚实地派生成一个新的窄 reframe hypothesis。

## 1) 原 rank 为什么 park
根据 `2026-03-18_1800_rank61-clean-replication-park.md`：
- 原始想法是把 **setup 前最后 3~5 分钟的 lower-TF volume-delta polarity** 写成一个 shared veto：当 `ema_psar_long / fib_retest_long / breakout_short` 已触发时，若子周期主动量方向与 setup 不一致，就 veto。
- 但最小 clean replication 的结果并没有形成诚实的跨 setup、跨资产增量：
  - `ema_psar_long + opposite_delta_veto`：约 `-3.60%`，且 `trade_count_retention≈38.10%`
  - `fib_retest_long + opposite_delta_veto`：虽约 `+0.71%`，但 `mean_trades≈4.0`、`retention≈36.36%`
  - `breakout_short + opposite_delta_veto`：约 `-3.28%`，且 `positive_asset_ratio=0/3`
- 所以它被 park 的核心原因，不是“阈值还没调对”，而是：**把 lower-TF delta polarity 写成 15m shared veto 这层职责，本身没有形成可迁移的诚实增量。**

## 2) 它更像 hard park 还是 soft park
**结论：`soft park`，但比 4 月 5 日那轮更接近 `hard with consumed residual`。**

为什么还不直接叫 hard park：
- lower-TF signed flow / delta polarity 这个主题本身仍有信息量；
- 原 replication 至少留下过一个很薄的 `fib_retest_long` 正 pocket，说明“入场前参与方向一致性”并非完全空。

为什么又更接近 hard：
- 这个 pocket 依旧太薄，且没有在 `ema_psar_long / breakout_short` 上同步站住；
- 最近 4/11~4/14 的新增证据没有把它拉回“15m shared gate”角色，反而更明确地把 residual value 推向 **1m/3m raw alpha / event-driven microstructure 宿主**；
- 换句话说，主题未死，但旧 `Rank 61` 的角色层已经基本被审计消费。

## 3) 有没有“可救信号”
**有，但不足以救旧 Rank 61；这些信号更像在支持新的 microstructure raw-alpha family。**

### 可救信号 A：stacked order-flow 说明短窗 pressure drift 仍有信息
- `2026-04-11_2010_stacked-orderflow-vote-shell.md` 更支持的是：
  - `CVD trend + recent bar delta + large-trade bias` 这类 **1m/3m short-window directional drift**；
  - `divergence / absorption` 更像 reversal admission / exit，而不是旧 Rank 61 那种 15m setup 前 binary veto。

### 可救信号 B：spread-shock completion 更像事件尾段反打
- `2026-04-13_1523_spreadshock-imbalance-completion-mr-alpha.md` 把主题进一步推向：
  - `spread shock + sustained imbalance -> completion fade`
  - 这属于 **adverse-selection completion 后的事件型 raw alpha**，不是旧 Rank 61 的“给三条 15m archetype 盖章”。

### 可救信号 C：small-flow/no-large-confirm 更像 trade-size decomposition fade
- `2026-04-14_0006_smallflow-nolargeconfirm-fade-alpha.md` 支持的是：
  - `small-size taker surge × no-large-flow confirmation -> short-horizon fade`
  - 它再次说明，真正有交易形状的是 **更快、更窄、可独立下单的 flow divergence alpha**，而不是“最后几分钟 polarity mismatch”这种 shared veto 残余。

## 4) 最值得改的唯一一刀是什么
如果只保留一条“唯一主修改轴”，最诚实的一刀仍然是：

> **把 lower-TF delta polarity 从 `15m shared veto` 改写成 `1m/3m event-driven microstructure raw alpha / execution admission`。**

更直白地说：
- 不再问“它能不能给 `ema/fib/breakout` 做共同门卫”；
- 改问“当短窗主动流 / spread shock / 大小单分歧达到 frozen threshold 时，能不能直接形成快频 continuation/fade 的独立 alpha 原语”。

## 5) 是否值得形成新的 derived hypothesis
**结论：不值得，本轮维持 `keep_park`。**

原因：
- 上面那一刀虽然是唯一诚实方向，但它已经把主语从“旧的 `Rank 61 shared veto`”切换成“新的快频 microstructure raw alpha / execution family”；
- 这不再是一个窄的 `Rank 61b`，而更像新的 fresh intake 宿主；
- 若硬写成 `Rank 61b`，会稀释原 `park` verdict 的审计意义，也会把 bot6 变成“给任何旧 rank 换壳重开”的机器。

## 单轮审查模板回答
### 原 rank 为什么 park？
因为 lower-TF delta polarity 作为 `15m` shared veto 没有形成跨 setup、跨资产的稳定增量；改善主要只留下极薄 pocket，且伴随明显 retention 压缩。

### 它更像 hard park 还是 soft park？
`soft park`，但比 4 月 5 日那轮更接近 `hard with consumed residual`。

### 有没有“可救信号”？
有。最近的 stacked order-flow、spread-shock completion、small-flow-no-large-confirm 证据都说明 flow 主题仍有信息。

### 最值得改的唯一一刀是什么？
把它从 `15m shared veto` 改成 `1m/3m event-driven microstructure raw alpha / execution admission`。

### 是否值得形成新的 derived hypothesis？
不值得。因为这已经不是旧 rank 的诚实窄派生，而是新的 raw-alpha family。

## 对队列的写回结论
- `Rank 61`：`keep_park`
- 建议备注：
  - 原 `park` verdict 保留；
  - 结论为“soft park，但比 4 月 5 日那轮更接近 hard with consumed residual”；
  - 4 月 11~14 日新增的 stacked-orderflow / spread-shock completion / small-flow-no-large-confirm 证据继续说明，该主题若还有 residual value，更像新的 `1m/3m` microstructure raw-alpha / execution family，而不是旧 lower-TF polarity shared veto 的诚实窄派生；
  - 当前不诚实 draft `Rank 61b`。

## 文件与工作区备注
- 本轮只做最小必要写回：新增本日志、更新 `research/park_reframe/INDEX.md`、更新 `docs/PARK_REFRAME_QUEUE.md`。
- 未改 `docs/TODO.md` 顶部排班。
- 当前仓库仍有无关脏文件，本轮不做 commit，避免混提。
