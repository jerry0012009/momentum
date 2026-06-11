# 2026-03-30 18:05 UTC · Rank 35 park reframe review

## 本轮对象
- `Rank 35 / VWAP pullback + trend-template qualifier`
- 本轮结论：`keep_park`
- 原 verdict 保留：`park`

## 为什么这轮看它
- 继续按 `bot6` 低频轮转处理 `Rank 1~37` 已 park 条目。
- `Rank 35` 上次 bot6 复盘是 `2026-03-23 15:37 UTC`，已超过最近 `7` 天回避窗口。
- 它已经有过唯一自然派生 `Rank 35b`，这轮要确认的是：最近一周的新 trend / pullback 证据，会不会诚实地打开 `Rank 35c`，还是反而进一步说明原主题更适合上移到更完整的 raw-alpha family。

## 本轮补读
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/optimization_loop/2026-03-17_1248_rank35-clean-replication-park.md`
- `research/park_reframe/2026-03-17_2222_rank35-park-reframe.md`
- `research/quant_digests/2026-03-29_2242_trend-pullback-correlation-shell-alpha.md`
- `research/quant_digests/2026-03-30_1728_bear-shock-short-alt-lag-pocket.md`

## 1) 原 Rank 为什么 park？
原 Rank 35 想表达的是：
- 先用 `1h/4h` 趋势模板限定 long-only 顺风环境；
- 再等 `RSI pullback + VWAP reclaim` 作为回调后再接回去的 admission；
- 执行口径是 `next-bar open + fixed 8-bar hold`。

原 clean replication 已经把 blocker 审得很清楚：
- `combo_long_only` 只剩极薄样本，`mean_trades≈3.7~4.0`；
- 中间 time bucket 明确翻负；
- `bias_plus_vwap_reclaim` 对 anchor 很敏感：`utc_day @ 6bps≈+8.69%`，但 `funding_8h @ 6bps≈-0.51%`；
- 真正留下薄 pocket 的不是整套 `VWAP reclaim + RSI pullback`，而是删掉 VWAP 后的 `bias_plus_rsi_pullback`（`6bps≈+2.71%`，`positive_asset_ratio≈100%`，`mean_trades≈12.0`）。

所以它被 park 的核心原因不是“顺势回调主题彻底不行”，而是：
**原 Rank 35 这版 `VWAP reclaim + trend-template` 包装太依赖 anchor、太稀疏，也不足以形成可部署的 pullback entry。**

## 2) 它更像 hard park 还是 soft park？
- 本轮判断：**soft park，但比 2026-03-23 更偏硬。**

原因：
- soft 的部分仍然成立：`higher-tf bias + RSI pullback` 至少留下了一点 modest pocket，说明“顺势回调再进”这个主题不是完全空的；
- 但更偏硬的部分也更清楚了：原 Rank 35 唯一自然的一刀——删掉 VWAP reclaim——已经被 `Rank 35b` 消费过；现在再往下切，很容易从“窄 reframe”滑成“换骨架重讲一个趋势 raw alpha”。

## 3) 有没有“可救信号”？
**有，但主要只够确认旧 residual，不够打开新派生。**

### 可救信号 A：旧 residual 仍然是 `Rank 35b`
原 park-reframe 已经把最自然的残余钉住了：
- `Rank 35b = remove VWAP reclaim; keep higher-tf bias + RSI pullback reclaim`
- 它对应的证据就是 `bias_plus_rsi_pullback` 这条 modest positive pocket。

这说明：
- 原 Rank 35 真正剩下的，不是 VWAP 语义；
- 而是更简单的 `顺势环境 + pullback reclaim`。

### 可救信号 B：新证据更支持“完整 trend / pullback raw alpha family”
`2026-03-29_2242_trend-pullback-correlation-shell-alpha.md` 给出的不是 `Rank 35` 式的小 gate，而是一整套：
- bull-regime breakout continuation
- pullback re-entry
- correlation-budget shell
- risk / sizing / trailing / portfolio overlay

它在回答的是：
**如果趋势回调主题要活，更诚实的形态像完整 raw alpha skeleton，而不是再给旧的 VWAP pullback admission 叠一层小修补。**

### 可救信号 C：更近的新证据继续把机会往事件型 / raw-alpha family 上移
`2026-03-30_1728_bear-shock-short-alt-lag-pocket.md` 虽然是 cross-asset bear-short，不是 Rank 35 同题材，但它再次强化了同一种 desk 方向：
- 当新证据真的足够强时，最近更常见的是直接形成 **可独立交易的 raw alpha**；
- 而不是继续把旧 park rank 包装成越来越薄的 shared admission / micro-reframe。

所以这轮的关键信号不是“Rank 35 还差一刀”，而是：
**顺势回调主题没死，但活下来的更像完整 trend / pullback raw-alpha family，不像原 Rank 35 这条 VWAP pullback 血缘还能再诚实分叉出 `35c`。**

## 4) 最值得改的唯一一刀是什么？
如果今天只允许保留 **1 条唯一主修改轴**，答案仍然还是旧答案：

**删除 `VWAP reclaim`，保留 `higher-tf bias + RSI pullback reclaim`。**

但这条唯一一刀已经被 `Rank 35b` 消费过了。

所以本轮最重要的判断不是“还能不能再想出一刀”，而是：
- **唯一自然的一刀没有变；**
- **既然这一刀已经被记录为 `Rank 35b`，现在就不诚实再写 `Rank 35c`。**

## 5) 是否值得形成新的 derived hypothesis？
- 结论：**不值得。**
- 本轮最终 verdict：`keep_park`

原因：
1. 原 Rank 35 的唯一自然 residual 已被 `Rank 35b` 基本消费；
2. 最近一周的新证据没有给它打开新的 `VWAP pullback` 单轴；
3. 相反，新证据继续表明：**trend / pullback 主题若要重开，更像应上移到完整 raw-alpha skeleton，而不是继续在 Rank 35 血缘里派生 `35c`。**

## 6) trade on / trade off（为什么不 draft）
如果现在硬写 `Rank 35c`，最像的写法只会变成：
- `trade on`：把顺势突破、回调再进、组合 risk budget、correlation gate 等完整骨架一起收进来；
- `trade off`：放弃 Rank 35 原本那条以 `VWAP reclaim + trend-template` 为中心的局部 admission 叙事。

这已经不是对原 rank 的**单轴窄 reframe**，而是在换 family。

所以本轮不 draft，不是因为主题没价值；
而是因为 **再写 `35c` 会污染原 `park` verdict 的审计边界。**

## 本轮最终判断
- 原 rank 为什么 park：因为 `VWAP reclaim + RSI pullback + trend-template` 这版包装 anchor 敏感、交易过稀，中段 bucket 也不诚实；
- 更像 `hard park` 还是 `soft park`：`soft park，但比 2026-03-23 更偏硬`；
- 有没有可救信号：有，但主要仍是既有 `Rank 35b` 那条 residual；
- 最值得改的唯一一刀：仍然是“删除 VWAP reclaim，保留 higher-tf bias + RSI pullback reclaim”；
- 是否值得形成新的 derived hypothesis：`不值得`；
- 本轮结论：`keep_park`。

## 对 queue 的实际含义
- `Rank 35` 原 `park` verdict 继续保留。
- `Rank 35b` 仍是它唯一自然、且已被记录过的窄派生；当前不新增 `Rank 35c`。
- 最近新证据只说明：**trend / pullback 主题的残余价值更像上移到完整 raw-alpha family，而不是继续在 Rank 35 血缘里细切。**
- 默认不改 `docs/TODO.md` 顶部排班。

## Git / 提交说明
- 本轮不做 git commit。
- 原因：工作区存在大量与本轮无关的共享脏文件，而且 `docs/PARK_REFRAME_QUEUE.md` 处于共享更新面上，当前不适合安全 selective commit。
