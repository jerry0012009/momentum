# ATR 回踩区 + bounce reclaim 这轮值得进下一手 clean replication：它先把 breakout confirmation 写成了诚实状态机
- 时间：2026-03-18 02:48 UTC
- 类型：GitHub / repo source intake
- 主题标签：breakout/retest-hold/confirmation/atr/repo/crypto/15m/scout
- 证据类型：repo source intake + 两条轻量诚实守门

## 1. 这次看了什么
这轮按 `Run 2 / Scout Fast Lane` 继续从 fresh `paper / repo based 5m / 15m crypto` source 里认领 1 条新候选，但只认领当前 authoritative board 已点名优先的那一条：`TheVision333/trading-bot` 里的 **ATR retest zone + bounce reclaim**。

它对当前 desk 真正有价值的，不是“整套机器人照抄”，而是它把 `breakout -> 等回踩 -> 超时/深穿则作废 -> bounce reclaim 后才入场` 写成了前向状态机，而且把关键边界直接冻在代码里：
- 回踩区不是死的百分比，而是 `0.5 ATR`
- 超过 `20` 根还没回踩就取消
- close 若反向穿越突破位超过 `1 ATR` 就作废
- 真正入场要等 close 重新站回/压回突破位，且 bounce K 线方向一致

## 2. 为什么这轮轮到它
- `EMA` 当前仍是 `running paper / waiting_not_due`，不能在 `Run 1` 空转；
- `Rank 17 / Rank 2 / Rank 29 / Rank 32b` 都已属于 `P3 narrow paper`，这轮没有新的真实 `append/review need`；
- 当前 `P2 / P1` 为空，因此按 desk 规则，默认先回到 **fresh repo intake**；
- 在当前可认领的新 source 里，这条的边际价值高于直接回退 `Run 3`，也高于继续围着已 park 的旧候选打转。

更直白地说：这轮不是“没活干只好继续找论文”，而是当前确实拿到了 1 条 **比 Rank 39 / 40 更像下一手 clean replication 的 repo confirmation 候选**。

## 3. 先把规则翻成人话
这条线的最小读法可以先冻结成：
- 先用**确认后的 swing high / low**当 breakout level；
- 只有当 close 真正突破该 level，且 breakout 那根 K 线本身够像样，才开始记 setup；
- 接下来不是立刻追，而是等价格在一定时间内回到突破位附近；
- 回踩太浅不算、太深也不算；
- 只有回踩后 close 再次站回突破方向，才允许进场。

翻成人话就是：
**不是“穿线就追”，而是“先确认真突破，再等一次可容忍的回踩，最后只在重新站稳时追随”。**

## 4. 两条轻量诚实守门
### 4.1 `trade on / trade off` 能不能写清？
能，而且比很多 repo template 更清楚。

最小冻结版可以直接写成：
- **trade on（long）**：
  1. 最近确认 swing high 被 close-confirm 突破；
  2. breakout candle 满足 `实体 >= 50% range` 且 close 落在 candle 顶部 `30%`；
  3. 之后 `1~20` 根内价格回到突破位附近 `<= 0.5 ATR`；
  4. 回踩期间 RSI 不跌破 `40`，且 close 没有反向穿越突破位超过 `1 ATR`；
  5. 之后 close 再次站回突破位，且 bounce candle 为同向实体；
  6. 结构层与 HTF 方向同向。
- **trade off（long）**：
  - 没有 close-confirm breakout；
  - 回踩超时；
  - 回踩深度超过 `1 ATR`；
  - bounce reclaim 没出现；
  - 或结构 / HTF / filters 不同向。
- short 端镜像。

第一道门 **通过**：这不是“图上看着像”，而是能直接压成离散 state machine 的执行模板。

### 4.2 有没有明显 `lookahead / repaint / data leakage`？
当前 source 的诚实点反而写得比较明白：
- `market_structure.py` 里 swing 点要等 `SWING_LOOKBACK=5` 右侧 bar 走完后才确认，确认使用是在 `i-n` -> `i` 的延迟上；
- `retest_signals.py` 的等待、失效、bounce 都是沿时间往前滚，不是回看后重标；
- 关键 level 用的是 `last confirmed swing high/low`，不是把还没确认的 pivot 直接拿来交易。

所以第二道门当前也**通过**：
- 还不能说它已经被证明有效；
- 但至少目前没看到一眼可判死刑的 `lookahead / repaint / data leakage`。

## 5. 为什么它比同窗口的其他回退动作更值钱
和当前 desk 里最近几条 fresh intake 相比，它的边际价值主要高在 3 点：

### 5.1 比 Rank 39 更冻结
`Rank 39` 最大问题之一，是 timeframe / exit / pyramiding 口径都不够干净。
这条至少把：
- breakout level
- retest zone
- timeout
- invalidation
- bounce entry
都钉成了前向条件。

### 5.2 比 Rank 40 更贴当前 breakout confirmation 主线
`Rank 40` 是顺势回调 continuation，但 clean replication 后已经直接转负。
这条则更像当前 desk 还值得继续试的另一侧：
**不是趋势里的 pullback continuation，而是 breakout 后的 retest-hold confirmation。**

### 5.3 比直接回退 Run 3 更符合这轮排班
当前 board 已明确：只有在 fresh intake 这一轮**也拿不到合格 source**时，才允许退去 `Run 3 / tiny-live plumbing`。
这轮既然已经拿到了合格 repo source，就不该跳过它直接说 exhausted。

## 6. 当前 hard verdict
### `Rank 43 / ATR retest zone + bounce reclaim`
- **当前 verdict：`admit_to_clean_replication_queue`**
- 还**不是** `paper candidate`
- 更不是 `narrow paper pilot`
- 只是说明：它已经够诚实，值得拿下一轮那 **1 次最小 clean replication** 预算

更直白地说：
- 这不是“它大概率能赚钱”的结论；
- 这只是“它已经比继续磨旧线或直接回退更有边际价值”的结论。

## 7. 下一轮只允许做什么
若下一轮继续认领它，默认只允许做 **1 次最小 clean replication**：
1. 固定 `BTC / ETH / SOL`，Binance perpetual；
2. 先用 `15m` 信号 + `1h` HTF 过滤；
3. `signal bar close -> next-bar open` 入场；
4. 固定 `no-overlap`；
5. 只比较极小邻近参数：如 `ATR retest mult = 0.4 / 0.5 / 0.6`，`timeout = 8 / 12 / 20`，不扩成大网格；
6. 先只回答 4 件事：`post-cost return / false-break rate / trade_count / time-pocket honesty`。

如果这一刀出来后：
- 成本后仍不干净，或
- 交易数过稀，或
- false-break rate 没比简单 breakout 更好，
那就应快速压回 `park / evidence pool`，不要继续给 stability budget。

## 8. 当前边界
- 这条线当前更像 **confirmation layer 候选**，不一定该单独扛 alpha；
- 原 repo 主要跑 `1h / 4h`，直接下放到 `15m` 仍有交易数变稀、过滤过厚的风险；
- 所以这轮最诚实的动作不是“直接升 paper”，而是 **只给下一手最小 clean replication 预算**。

## 9. 来源
1. TheVision333. `trading-bot`
   - repo: https://github.com/TheVision333/trading-bot
2. 关键实现文件
   - `strategy/retest_signals.py`
   - `strategy/market_structure.py`
   - `config.py`
