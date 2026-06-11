# PyTrendline Event Validation v3 — visible-line event study (brief spec)

## Goal
研究 **当时已经可见的 support / resistance 线** 上发生的结构事件，是否能预测未来收益；同时尽量避免未来函数。

## Why v3 exists
v2 证明了 `side`（support vs resistance）有结构差异，但 v2 的事件时间很多是 **回填出来后才在窗口里被看到**，不适合直接解释为可实时交易信号。

v3 改成：
- 先定义 **as-of 可见线**
- 再定义 **价格与这条可见线的互动事件**
- 收益从 **signal 确认后的下一根 bar open** 开始算

## Core decisions
1. **研究对象**：visible-line events（不是回填事件）
2. **主 breakout 定义**：close-based cross（更保守）
3. **horizons**：6h / 24h / 48h / 72h
4. **起算点**：signal bar 之后下一根 bar open
5. **主结果**：raw + purged 两套并列输出

## Event taxonomy
### Raw events
- `support_touch_raw`
- `support_breakout_raw`
- `resistance_touch_raw`
- `resistance_breakout_raw`

### Confirmed events
为了响应“touch / break 之后 1~2 根 K 线也要纳入研究”的要求，v3 额外定义：
- `support_rebound_confirm_1`
- `support_rebound_confirm_2`
- `resistance_rebound_confirm_1`
- `resistance_rebound_confirm_2`
- `support_breakout_confirm_1`
- `support_breakout_confirm_2`
- `resistance_breakout_confirm_1`
- `resistance_breakout_confirm_2`

## Anti-lookahead rules
1. bar `t` 的事件，只能使用 **`t-1` 时刻已经可见的线**
2. 不允许“同一根 bar 既生成线又用它来触发交易”
3. raw 事件在 bar `t` 识别，收益从 `t+1 open` 开始算
4. confirm_1 / confirm_2 事件分别在 `t+1` / `t+2` 才算被确认，收益从对应确认 bar 的下一根 open 开始算
5. 结果同时输出 raw 与 purged（最长 horizon 去重）

## First implementation boundary (v3a)
考虑 pytrendline 运行代价，首版使用 **stepwise visible snapshots**：
- 每隔 `snapshot_step_bars` 重新计算一次可见线
- 在两次重算之间，用上一批可见线监控 touch / breakout / confirmation 事件

这不是最终的逐 bar engine，但它已经满足：
- 线必须先可见
- 事件必须后发生
- 收益必须从事件确认后才开始计算

## Success criteria
如果某类事件要进入后续 alpha baseline 候选，至少应满足：
- purged 后仍保留清晰方向
- 多资产同号占比较高
- 24h 或 48h horizon 有稳定效应
- raw → confirm 后不是只靠样本收缩才“变好看”
