# 别再让三条收口线全靠 volume / flow 才决定能不能做：`ADX > 20 + ER > 0.20` 更像 15m 的 price-only trend-readiness gate
- 时间：2026-03-19 00:55 UTC
- 类型：GitHub
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/adx/efficiency-ratio/anti-chop/regime/filter/repo/crypto/15m
- 证据类型：源码证据 + 工程迁移假设
- 证据强度提示：**中等偏弱**（规则写得很清楚，但 repo 默认跑 `4h`，不是直接在 `15m crypto` 上给过 OOS 证明）

## 1. 这次看了什么
这次看的是 **pupedator (2026), _Binance Futures AI Trading Bot_**。表面上它是个 Claude 驱动的合约 bot，但对当前 desk 真正值钱的，不是 AI 那层，而是它在最前面先放了一个很朴素的 **price-only regime gate**：**`ADX < 20` 直接不做，`Efficiency Ratio < 0.20` 也直接不做。**

翻成人话：**先别急着问方向，先问这段价格是不是“真的在走”。** 如果只是上下抖、来回磨，breakout-short follow-up、Fib retest_hold、EMA/PSAR raw continuation 都容易被拖进假延续和来回止损。

## 2. 核心结论
- **一句话核心结论：** 对我们现在的三条收口线，更值得先测的不是再加一层外部数据，而是先给它们共用一个 **公开可得、只吃 OHLCV 的 anti-chop / trend-readiness gate**。
- **一句话说明它怎么证明：** 不是靠论文，而是 repo 源码把 `ADX < 20`、`ER < 0.20` 写成 hard gate，还额外把 `ER > 0.40` 当成 conviction 加分，足够直接转成最小实验。
- repo 的免费规则层很清楚：总分 `12` 分，`>= 8` 才放行；其中 `ADX` 和 `ER` 不是普通加分项，而是先做 **一票否决**。
- `ER` 的定义非常适合 desk：`ER_20 = abs(close_t - close_t-20) / sum(abs(diff(close)), 20)`。越接近 `1`，说明这 20 根更像单向推进；越接近 `0`，说明只是来回抖。
- 这套读法对我们最有价值的地方在于：**它不和现有 VWAP / OI / liquidation / volume gate 冲突，反而能成为更便宜的前置过滤层。** 先用 price-only gate 挡掉烂环境，再决定要不要让更贵、更复杂的 gate 出场。

## 3. 为什么这轮值得先写
这题没有偏离主线，反而正好补主线的一个空缺：最近几轮 digest 已经给三条线补了很多 **volume / flow / structure / external-data** 型 overlay，但还缺一个足够便宜、足够朴素、能先回答“当前是不是趋势口袋”的 shared spine。

- 对 **`V3 final-verdict / breakout-short follow-up`**：它回答的是“这次 break 后到底有没有 follow-through 质量”，避免在横盘边缘硬追最后一脚。
- 对 **`Fibonacci confirmation / retest_hold`**：它能把“看起来像守住、其实只是区间内回弹”的回踩单独筛掉。
- 对 **`EMA / PSAR raw alpha focus`**：它特别适合做 raw lane 的第一层 allow/deny gate，因为只用价格路径，不需要额外数据接入成本。

如果要回答“为什么它比继续帮三条线堆新 filter 更值得”，答案是：**因为我们现在更缺一个 shared 的 `先看环境是否可顺势` 骨架，而不是第 8 个各自不同的小 veto。**

## 4. 可复刻的最小实验
### 研究假设
当 `15m` 主信号出现时，若同时满足 `ADX14 >= 20` 且 `ER20 >= 0.20`，则后续 `4~8` 根的 continuation 质量、成本后期望值和 false-break 生存率会优于未过滤样本；若再要求 `DI` 方向一致，提升可能更明显。

### 一个可计算定义
先冻结现有 trigger，不改 entry 形状，只测 gate：
- `trend_ready_long = (adx14 >= 20) & (er20 >= 0.20) & (plus_di > minus_di)`
- `trend_ready_short = (adx14 >= 20) & (er20 >= 0.20) & (minus_di > plus_di)`
- 可再做一版更强过滤：`er20 >= 0.40` 视为 high-conviction bucket，而不是先直接 hard veto

其中：
- `adx14` 用 Wilder 口径
- `er20 = abs(close - close.shift(20)) / rolling_sum(abs(diff(close)), 20)`
- long/short 的 `DI` 用来做方向一致性确认，不和主 trigger 抢角色

### 最小回测切口
- 标的：`BTC / ETH / SOL` perpetual
- 周期：`15m`
- 样本：近 `180~365d`
- 执行：`next-bar open`，`no-overlap`
- 对照组：
  1. baseline（无 gate）
  2. `ADX >= 20` only
  3. `ER >= 0.20` only
  4. `ADX + ER`
  5. `ADX + ER + DI alignment`

### 第一轮最该看什么
- `post_cost_expectancy`
- `forward_4bar / 8bar median return`
- `false_break_ratio`（入场后 2~4 根内反向失守的比例）
- `trade_retention`（过滤后交易数还剩多少）

## 5. 风险与保留意见
- 这不是论文，是新 repo；它证明的是“规则可清楚写出来”，不是“已在 15m crypto 上稳定赚钱”。
- repo 默认 `TIMEFRAME = 4h`，所以我们只能**偷它的 gate 逻辑**，不能把整套参数直接照搬到 `15m`。
- `ADX` 和 `ER` 都是慢指标；如果阈值卡太死，可能会把 breakout-short 最早的 expansion 段错杀掉。所以第一轮最好先做 **bucket / 分层**，别一上来就只测 hard cutoff。
- `ER` 很适合识别“价格有没有真推进”，但不负责告诉你方向；方向还是应由 breakout / retest / EMA-PSAR 主信号自己决定。

## 6. 下一步怎么测
最直接的一步：**别把它当 standalone 新策略，先把它接成三条线的 shared pre-filter。**

具体顺序建议：
1. 先挂到最干净的 `EMA / PSAR raw lane`，看 `flip-to-fail` 是否先明显下降；
2. 若结果像样，再借给 `breakout-short follow-up`；
3. 最后再接到 `Fib retest_hold`，看它能不能减少“看似守住、实则横盘震荡”的坏单。

如果 `ADX + ER` 这层已经能明显改善 `trade survival`，后面的 VWAP / OI / liquidation / volume gate 就更适合改成 **二层 refinement**，而不是继续承担“判断市场有没有在走”的一层职责。

## 7. 来源
1. **pupedator. (2026). _Binance Futures AI Trading Bot_. GitHub.**
   - Readable URL: https://github.com/pupedator/binance-futures-ai-bot
   - Repo URL: https://github.com/pupedator/binance-futures-ai-bot
   - GitHub API metadata: https://api.github.com/repos/pupedator/binance-futures-ai-bot
2. **README / strategy summary**
   - Raw URL: https://raw.githubusercontent.com/pupedator/binance-futures-ai-bot/master/README.md
   - 关键阈值：`ADX > 20`、`ER > 0.20`、`ER > 0.40` conviction bonus、signal score `>= 8/12`
3. **源码细节**
   - `signals/generator.py`: https://raw.githubusercontent.com/pupedator/binance-futures-ai-bot/master/signals/generator.py
   - `features/indicators.py`: https://raw.githubusercontent.com/pupedator/binance-futures-ai-bot/master/features/indicators.py
   - `features/feature_engineer.py`: https://raw.githubusercontent.com/pupedator/binance-futures-ai-bot/master/features/feature_engineer.py
