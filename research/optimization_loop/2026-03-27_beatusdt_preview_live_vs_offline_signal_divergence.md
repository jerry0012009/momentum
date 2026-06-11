# BEATUSDT preview live vs offline replay 信号分叉专项

日期：2026-03-27
范围：只看 rank32b / `ema_cross_plus_slope_floor` / BEATUSDT，重点解释为什么 live preview 会触发、而 offline preview replay 不触发。

## 结论先说

这不是“同一个 preview 规则在不同数据上偶尔抖动”，而是 **live preview 和 offline preview replay 现在并不是同一套信号生成实现**。

最关键的分叉点是：

- **live preview** 在 `src/momentum/execution/canary32b/signal_adapter.py::_build_preview_signal()` 里，
  会把“当前未收盘 15m partial bar”直接拼进 15m bars，随后调用
  `build_rank32b_frame_from_bars()` → `get_signal()`。
- **offline preview replay** 在 `scripts/build_rank32b_unclosed15m_preview_backtest.py::build_preview_minutes()` 里，
  用另一套手工实现的 preview 公式逐分钟重放。

两边名字都叫 preview，但**核心参考值并不完全一致**。

## 这次定位到的主因

### 主因：live preview 会把当前 partial bar 污染到“上一根 15m bar 的 EMA 参考值”里

live preview 的链路是：

1. 取当前 bucket 的 recent 1m bars
2. 逐分钟构造 current partial 15m bar
3. 把它 append 到历史 15m bars 末尾
4. 调 `build_rank32b_frame_from_bars()`

而 `build_rank32b_frame_from_bars()` 内部是：

- 对 15m bars 做 `resample("1h").last()`
- 然后算小时级 EMA
- 再 `merge_asof(..., direction="backward")` 回填到 15m rows

问题在于：

**当当前小时里已经存在 partial 15m bar 时，这个 partial bar 会成为该小时的 `last()`，从而把本小时 EMA 提前更新。**

随后 `merge_asof(backward)` 会把这个“已经被 partial 更新过的小时 EMA”回填到同一小时内更早的 15m row 上。

结果就是：

- live preview 在判定 `prev_close >= prev_fast` / `prev_close <= prev_fast` 时，
- 用到的 `prev_fast` 不是“上一根 completed 15m bar 当时真实看到的 EMA”，
- 而是**已经吃进当前 partial bar 信息后的 EMA**。

这会让 cross 条件被提前翻转，制造出 replay 里不存在的 live preview 信号。

## BEATUSDT 两个明确分叉样本

### 样本 1：2026-03-26 16:15 bucket

live preview 首次触发时间：`2026-03-26 16:17:00Z`

当时 live-like 计算：

- `prev_close = 0.5989`
- `prev_fast = 0.598869`
- 所以 `prev_close >= prev_fast` 为 **True**
- 当前 close = `0.5899`，且 slope 条件也满足
- 因此 live preview 触发 short

但 offline preview replay 同一分钟的参考值是：

- `prev15_close = 0.5989`
- `prev15_fast = 0.599726`
- 所以 `prev15_close >= prev15_fast` 为 **False**
- 因此 offline preview **不触发**

也就是说，这一笔不是市场数据本身不一致，而是：

**同一 bucket、同一分钟、同样 close 下，live 用的“上一根 EMA”比 offline 更低，低到了足以让 cross 条件翻面。**

### 样本 2：2026-03-26 22:45 bucket

live preview 首次触发时间：`2026-03-26 22:53:00Z`

live-like：

- `prev_close = 0.5928`
- `prev_fast = 0.592702`
- `prev_close >= prev_fast` 为 **True**
- live preview 触发 short

offline preview replay：

- `prev15_close = 0.5928`
- `prev15_fast = 0.593150`
- `prev15_close >= prev15_fast` 为 **False**
- offline preview **不触发**

这和 16:15 那笔是同一个根因。

## 为什么 14:30 / 12:15 这些 bucket 两边都能触发？

因为这些 bucket 下，`prev_close` 对 EMA 的越过更明显：

- 即使用 offline 那套更严格/更“未污染”的 `prev15_fast`
- cross 条件依然成立

所以这不是“所有 preview 都不一致”，而是：

**当上一根 close 离 fast EMA 很近时，live 这套 partial 污染会把边界样本推过线，导致多出一批 replay 不承认的 preview 信号。**

## 目前确认的 same / different

### 一样的部分

- 同一个交易对：BEATUSDT
- 同一个策略变体：`ema_cross_plus_slope_floor`
- 同一个 slope floor：`0.0004`
- 同方向结构要求：
  - short 要求 `ema_fast_1h < ema_slow_1h`
  - slope 同向且 fast slope 小于负门槛
- 当前 bar close 必须站在 fast EMA 的正确一侧

### 不一样的部分

#### 1. 信号实现不是同一个函数

- live：`signal_adapter._build_preview_signal()` + `build_rank32b_frame_from_bars()` + `get_signal()`
- offline：`build_preview_minutes()` 自己重写 preview 条件

这是架构层面的 parity 风险。

#### 2. live 的 prev_fast 会被 current partial hour 提前污染

这是本次定位到的**主要根因**。

#### 3. 时间戳语义有 1 分钟偏移

- live preview 用的是 `minute_row.open_ts`
- offline preview 用的是该分钟的 `close_ts`

例如 live 会记成 `16:17`，offline replay 对应的是 `16:18 close`。

这不是造成“触发/不触发”分叉的主因，但会让对账更乱。

#### 4. ATR 计算口径也不完全一样

- live：在 partial 15m frame 上直接 `compute_atr14(frame)`
- offline：`13 根历史 completed TR + 当前 partial TR` 组合成 `atr14_partial`

这次 BEAT 的“有无信号”主要不是 ATR 决定的，但 ATR 仍然会影响后续 TP/SL 对照。

#### 5. live 只看“当前 bucket 的 first preview”，offline 会把整段历史逐分钟 replay

live 更像流式实时判定；offline 更像历史扫描器。

## 这件事为什么可怕

因为它意味着：

> 你现在看到的并不是“同一策略在 live 和 replay 上结果不同”，而是“live 和 replay 根本没有完全共用同一套 preview 信号引擎”。

所以如果不先修 parity：

- preview live 赚钱/亏钱，不能直接归因给执行
- replay 好看/难看，也不能直接拿来验证 live
- 两边其实在比不同东西

## 建议的修复方向

### 方向 A（推荐）：抽一个唯一 preview engine，live / replay 共用

目标：

- 输入统一：历史 completed 15m + 当前 bucket 1m partial path
- 输出统一：
  - 是否触发
  - 首次触发时间
  - 方向
  - signal_price
  - 关键诊断字段（prev_close / prev_fast / fast_slope / slow_slope）

让 live 和 offline 都走同一个函数，彻底消灭实现漂移。

### 方向 B：先修 live 里的 EMA 污染问题

至少要保证：

- `prev_fast` / `prev_slow` / `prev_mid`
- 取自“上一根 completed 15m bar 在当时的真实状态”
- 不允许当前 partial bucket 反向改写上一根 bar 的参考值

### 方向 C：补 parity regression tests

建议至少固定下面两组 case：

- `BEATUSDT | 2026-03-26T16:15:00Z`
- `BEATUSDT | 2026-03-26T22:45:00Z`

要求：

- live preview 模拟结果 == offline preview replay 结果
- 首次触发分钟一致
- 关键诊断字段一致（允许小数误差，但不允许方向/布尔条件分叉）

## 当前阶段结论

这次 BEAT 的专项已经能明确回答：

1. **是的，live preview 和 offline preview replay 现在触发规则不一样。**
2. **不是抽象意义上的“不一样”，而是已经定位到一个明确实现缺陷：current partial hour 污染了 previous 15m EMA 参考值。**
3. **BEAT 只是把这个问题放大暴露出来；它不一定是唯一受影响的币。**

下一步如果继续做，建议直接进入“修 parity + 回归验证”阶段，而不是继续先讨论交易表现。因为信号层没对齐前，PnL 对照会一直掺假。
