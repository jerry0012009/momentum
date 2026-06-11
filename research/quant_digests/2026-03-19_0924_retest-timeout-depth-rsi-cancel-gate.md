# 别把 retest_hold 写成“触位后二次确认”：`timeout + depth invalidation + RSI path-memory` 更像 15m continuation 的 shared cancel gate
- 时间：2026-03-19 09:24 UTC
- 类型：GitHub
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/retest/timeout/depth-invalidation/rsi/path-memory/confirmation/filter/repo/crypto/5m/15m
- 证据类型：repo 代码规则（工程证据）+ 待验证最小实验

## 1. 这次看了什么
这轮主看 **TheVision333 (2026) 的 `trading-bot` 仓库**，重点文件是 `strategy/retest_signals.py`。最值得迁移的不是“又一套 breakout 信号”，而是它把 retest 写成了一个可取消的 pending-state 生命周期：
**有等待时限（timeout）、有过深失效（depth invalidation）、有回踩过程动量约束（RSI path-memory）**。

## 2. 核心结论
1. **一句话核心结论：** retest 不是“碰到位 + 反弹一根”就算成立，而应该先过一个“是否仍有效”的取消闸门（TTL + 深度失效 + 过程动量）。
2. repo 给了很清楚的参数化骨架（可直接复现）：
   - `RETEST_TIMEOUT_CANDLES = 20`
   - `RETEST_ATR_MULT = 0.5`（回踩容忍区）
   - `RETEST_DEPTH_ATR_MULT = 1.0`（过深直接取消）
   - `RSI_RETEST_FLOOR/CEIL = 40/60`（回踩过程动量约束）
3. 这套规则本质是 **cancel gate**，不是新主信号：先决定“这次 retest 还配不配交易”，再决定是否执行 follow-up。
4. **一句话证明方式：** 作者在代码里用显式状态机（watching → in_retest → reclaim / cancel）逐 bar 推进，并强制只使用当根及之前信息，执行在 next-bar open。

## 3. 为什么和当前三条收口线有关
- **V3 breakout-short follow-up**：突破后如果 long relief 走得过深或拖太久，直接取消 follow-up，减少“迟到追空”。
- **Fibonacci confirmation / retest_hold**：Fib 触位后若在时限内无法完成 reclaim，或先发生 >1 ATR 的反向破坏，`hold` 直接判失败，不再硬解释。
- **EMA / PSAR raw alpha focus**：EMA/PSAR 继续做方向触发；这层只负责 veto/cancel，优先解决成本后存活而非提高裸信号频率。

## 4. 下一步怎么测（5m/15m 最小实验）
### 4.1 数据与公开性
- 数据源：Binance/Bybit 公共 OHLCV（公开可得）
- 更新频率：5m / 15m
- 首轮样本：BTC/ETH/SOL，`180d IS + 60d OOS`

### 4.2 最小可复现实验口径
保持现有三条 archetype 的方向逻辑不变，仅替换 retest 确认层：
- A 组：baseline（触位 + reclaim 即通过）
- B 组：A + `timeout`（N=20）
- C 组：B + `depth invalidation`（>1 ATR 取消）
- D 组：C + `RSI path-memory`（long 不破 40 / short 不上 60）

统一执行冻结：`signal当根及之前 + next-bar open + no-overlap + 6/10/15 bps per side`。

### 4.3 首轮判据
优先看：
- `false_reclaim_ratio`（确认后 3~4 bars 内反向收回）
- `post_cost_expectancy`
- `trade_count_retention`

首轮过线建议（相对 A）：
- `false_reclaim_ratio` 下降 ≥10%
- `trade_count_retention` ≥45%
- `post_cost_expectancy` 不恶化（最好改善）

## 5. 风险与保留意见
- 当前证据主要来自工程规则，不是已完成的独立 OOS 结果；
- `N=20 / 0.5ATR / 1ATR / RSI40/60` 只是迁移起点，不应直接当最优参数；
- 若不同币种最优阈值差异过大，应优先做“分档/分层参数”，不要硬统一；
- 这条线应定位为 **confirmation / veto / cancel layer**，不是替代 breakout/Fib/EMA-PSAR 主逻辑。

## 6. 来源
1. **TheVision333. (2026). _trading-bot_. GitHub.**
   - Venue: GitHub
   - DOI: N/A
   - Readable URL: <https://github.com/TheVision333/trading-bot>
   - Repo URL: <https://github.com/TheVision333/trading-bot>
2. **核心实现：`strategy/retest_signals.py`**
   - Readable URL: <https://github.com/TheVision333/trading-bot/blob/main/strategy/retest_signals.py>
   - Raw URL: <https://raw.githubusercontent.com/TheVision333/trading-bot/main/strategy/retest_signals.py>
3. **相关实现：`strategy/market_structure.py` / `strategy/mtf.py` / `config.py`**
   - <https://github.com/TheVision333/trading-bot/blob/main/strategy/market_structure.py>
   - <https://github.com/TheVision333/trading-bot/blob/main/strategy/mtf.py>
   - <https://github.com/TheVision333/trading-bot/blob/main/config.py>
