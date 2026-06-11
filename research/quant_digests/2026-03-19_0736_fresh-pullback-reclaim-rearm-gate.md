# 别把 continuation / retest 的再进场写成“信号还亮着就继续追”：`fresh pullback → reclaim` 状态机更像 15m 的 shared re-arm gate
- 时间：2026-03-19 07:36 UTC
- 类型：GitHub
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/pullback/reclaim/rearm/state-machine/atr/trailing-stop/repo/crypto/15m
- 证据类型：repo 代码 + repo 自报回测结果 + 可执行最小实验设计

## 1. 这次看了什么
这轮选的是一个很新的仓库：
- **Adam / Adamski13 (2026)**
- **Trend Pullback System (TPS) v1**
- GitHub repo: `Adamski13/trend-pullback-system`

它表面上是一个日线 `200 SMA + 21 EMA` pullback 系统，但对我们 desk 真正值钱的，不是把整套日线参数照搬到 15m，而是它在 `src/strategy.py` 里把回踩/再进场写成了一个很干净的**状态机**：
**先发生一次真正的 pullback（价格穿回 EMA 另一侧）→ 记录这次 pullback 极值 → 只有 reclaim 回来才触发入场 → 触发后立刻 reset，下一次必须重新经过 fresh pullback 才能再进。**

## 2. 核心结论
1. 这份 repo 最值得偷的不是 `EMA21` 或 `SMA200` 本身，而是 `was_below_ema_long / was_above_ema_short` 这种 **armed → reclaim → reset** 交易状态机。
2. 这比“信号还亮着就继续追”更诚实：**没有 fresh reset，就不给第二次入场资格**。它天然适合做 `continuation / retest` 的 re-arm gate。
3. repo 里的 stop 也不是抽象的“走坏了”，而是直接锚在 **pullback extreme ± 0.5 ATR**；这对 15m 最小实验很友好，因为 invalidation 能写得很硬。
4. 作者在 `PROJECT_STATUS.md` 里还给了一个值得参考的诚实点：加入 frictions 后，repo 自报 **BTC-USD 仍为正（CAGR 3.01% → 2.92%）**，但系统并不“普适”，利润也高度集中在少数大趋势单上。换成人话：**它更像抓 continuation convexity，不像高频连续开火模板。**

## 3. 为什么和当前三条收口线有关
这轮值得做，因为它不是另开新宇宙，而是直接给三条线补一个共同缺口：**什么时候算 re-armed，可以再打一枪？**

- **V3 breakout-short follow-up**：不要在同一段下跌里一根接一根追空；更像该先等一次 relief rally（例如回到 EMA 上方/附近），再看重新失守时才重开 short。
- **Fibonacci confirmation / retest_hold**：不要把“碰到 0.5 / 0.618”直接算守住；更诚实的是先经历一次回踩状态，再等 reclaim 才确认 hold 成立。
- **EMA / PSAR raw alpha focus**：不要把 raw flip 做成 always-on 开关；先 reset，再 reclaim，能明显减少连续假翻单。

一句话：**这不是新 alpha，本质上是三条线都能共用的“再上膛”规则。**

## 4. 下一步怎么测（5m/15m 最小实验）
### 4.1 数据与公开性
- 数据源：Binance / Bybit 公共 OHLCV
- 公开性：公开可得
- 更新频率：5m / 15m
- 首轮样本：BTC / ETH / SOL，最近 180 天

### 4.2 最小实验口径
对每条 archetype 都保留原方向逻辑，只替换“二次进场 / follow-up 资格”这一层：

- **A 组（baseline）**：当前原始 entry / re-entry 规则
- **B 组（re-arm gate）**：只有在发生 `fresh pullback` 后，才允许下一次 continuation / retest entry
- **C 组（re-arm + hard invalidation）**：B 组 + stop 固定为 `pullback_extreme ± 0.5 ATR`

可先冻结成下面这个共享状态机：
- `armed_long = bias_long 且 close < ema21`（或触达 Fib 回踩区后落回 EMA 下方）
- `trigger_long = armed_long 且 close > ema21`
- `armed_short = bias_short 且 close > ema21`
- `trigger_short = armed_short 且 close < ema21`
- 一旦触发，`armed_*` 立即清空；没有新的穿越，不允许连续再进。

### 4.3 首轮优先看什么
- `post_cost_return`
- `3-bar fail rate`
- `trade_count_retention`
- `avg MAE / MFE after re-entry`

首轮过线标准（相对 baseline）：
- `3-bar fail rate` 下降 10% 左右
- `trade_count_retention` 仍保留 50%~70%
- `post_cost_return` 不明显恶化

## 5. 风险与保留意见
- 这份 repo 的主样本是**日线**，不能把它当成 15m 已验证答案；
- 其回测结果目前是 repo 自报，不是我们独立复核；
- `200 SMA`、pyramiding、daily trend context 不一定要照搬，当前更值得迁移的是**状态机语义**，不是整套参数；
- 如果把“fresh pullback”定义得太宽，会重新退化成追涨杀跌；定义得太窄，又会把交易数砍空。

## 6. 来源
1. **Adam / Adamski13 (2026).** *Trend Pullback System (TPS) v1*. GitHub.
   - Repo URL: <https://github.com/Adamski13/trend-pullback-system>
2. **核心实现文件**：`src/strategy.py`
   - Readable URL: <https://github.com/Adamski13/trend-pullback-system/blob/main/src/strategy.py>
   - Raw URL: <https://raw.githubusercontent.com/Adamski13/trend-pullback-system/main/src/strategy.py>
3. **项目说明 / 回测口径**：`PROJECT_STATUS.md`
   - Readable URL: <https://github.com/Adamski13/trend-pullback-system/blob/main/PROJECT_STATUS.md>
   - Raw URL: <https://raw.githubusercontent.com/Adamski13/trend-pullback-system/main/PROJECT_STATUS.md>
