# 别把 breakout-short 的 final verdict 写成“跌破后继续追”：`outside-close → back-inside-close` 更像 15m 的 failure 判决层
- 时间：2026-03-19 10:59 UTC
- 类型：GitHub
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/post-break-path/failure-verdict/reentry/sequence-extreme/risk-overlay/repo/crypto/5m/15m
- 证据类型：repo 代码规则（工程证据）+ 待验证最小实验

## 1. 这次看了什么
这轮看的是 **Harro Moen (MoDiggler75, 2026)** 的仓库 `crypto-trading-bot`，重点文件是 `backtest_breakout_retest.py`。它有个很适合当前 desk 的旁支想法：

> 先等价格 **收盘突破区间外**，再等它 **收盘回到区间内**；这一下不是“继续追趋势”，而是把刚才那次 break 当成一次可交易的 failure event。

脚本把这个逻辑写成了显式状态机：`waiting_for_breakout -> tracking_top/bottom_sequence -> re-entry signal`，并把风控绑定到 breakout 后那段 `sequence` 的极值。

## 2. 核心结论
1. **一句话核心结论**：对 `V3 breakout-short follow-up` 来说，`outside-close -> back-inside-close` 更像 **post-break failure verdict**，比“看到破位就默认 continuation”更诚实。
2. **一句话证明方式**：源码明确要求先出现区间外收盘，再出现区间内收盘才触发；并把止损固定在 breakout 序列极值，止盈固定 `2R`，不是主观画图。
3. 关键可迁移骨架（来自代码）：
   - 先用前 4 小时区间高低定义 `zone_high/zone_low`；
   - `close > zone_high` 进入 `tracking_top_sequence`，`close < zone_low` 进入 `tracking_bottom_sequence`；
   - 若随后 `close` 回到区间内（`zone_low <= close <= zone_high`），把这次外扩判成 failure，触发反向单；
   - 风险锚：`SL = sequence_high/low`，`TP = 2 * SL distance`。
4. 这条线最像给我们补的是 **判决层**，不是主 alpha：它回答“这次 break 是否已被市场否决”。

## 3. 为什么和当前三条收口线直接相关
- **V3 final-verdict / breakout-short follow-up**：可直接作为“是否继续追空”的反向判决。若下破后很快 `back-inside-close`，就该把 continuation 降级甚至反手，不该再硬追。
- **Fibonacci confirmation / retest_hold**：当 Fib retest 看似守住，但随后出现“先外扩再收回区间”的路径时，可作为 hold 失败的强否决条件。
- **EMA / PSAR raw alpha focus**：EMA/PSAR 继续负责方向与触发；这层负责在 post-break 路径上做 **entry veto / reversal overlay**，降低“破位后一脚追在末端”的成本消耗。

## 4. 可复刻的最小实验（5m/15m）
### 4.1 数据与公开性
- 数据源：Binance Futures 公共 K 线（`/fapi/v1/klines`）
- 公开性：公开可得
- 更新频率：5m / 15m
- 首轮样本：BTC/ETH/SOL，`180d IS + 60d OOS`

### 4.2 最小可计算定义
以 15m 为主（5m 做触发细化）：
1. 定义 rolling 区间边界（先用 `N=16` 根 15m，约 4 小时）；
2. 事件 A（outside close）：`close_t > high_range_t` 或 `< low_range_t`；
3. 事件 B（back-inside close）：在接下来 `M` 根（先用 `M=1~4`）出现 `low_range <= close <= high_range`；
4. 仅当 A→B 成立，记为 `failure verdict` 事件；
5. 方向映射：
   - 顶部外扩后回内：优先 short / short follow-up veto for longs
   - 底部外扩后回内：优先 long / long follow-up veto for shorts

### 4.3 对照组与判据
- A组：现有 breakout/fib/ema-psar baseline
- B组：A + `outside->inside` failure verdict（binary veto）
- C组：B + sequence-extreme 风险分档（按 overshoot 深浅调仓）

首轮只看三项：
- `false_follow_ratio`（入场后 4 bars 内反向收回）
- `post_cost_expectancy`（6/10/15 bps per side）
- `trade_count_retention`

建议过线：相对 A，`false_follow_ratio` 下降 ≥8%，且 `trade_count_retention` ≥40%，同时 expectancy 不恶化。

## 5. 风险与保留意见
- 该仓库主实现混用美股时段与 Yahoo 数据口径，不能原样当 crypto 生产模板；
- 代码参数是工程默认值（如 `risk_per_trade=5%`、`max_position_value=30%`、`2R`），不代表我们 desk 最优；
- 这是规则证据，不是已验证 OOS 绩效；
- 若实验显示它只在个别币对有效，应降级为“币对特异 overlay”，不做全局硬规则。

## 6. 来源
1. **Harro Moen (MoDiggler75). (2026). _crypto-trading-bot_.**
   - Venue: GitHub
   - DOI: N/A
   - Readable URL: <https://github.com/MoDiggler75/crypto-trading-bot>
   - Repo URL: <https://github.com/MoDiggler75/crypto-trading-bot>
2. **关键实现：`backtest_breakout_retest.py`**
   - Readable URL: <https://github.com/MoDiggler75/crypto-trading-bot/blob/master/backtest_breakout_retest.py>
   - Raw URL: <https://raw.githubusercontent.com/MoDiggler75/crypto-trading-bot/master/backtest_breakout_retest.py>
3. **辅助实现：`backtest_4hr_rsi_retest.py`（同仓库中的 retest 状态机变体）**
   - Readable URL: <https://github.com/MoDiggler75/crypto-trading-bot/blob/master/backtest_4hr_rsi_retest.py>
   - Raw URL: <https://raw.githubusercontent.com/MoDiggler75/crypto-trading-bot/master/backtest_4hr_rsi_retest.py>
4. **仓库元数据（API）**
   - URL: <https://api.github.com/repos/MoDiggler75/crypto-trading-bot>
   - 参考字段：`created_at=2026-01-17`，`pushed_at=2026-02-07`
