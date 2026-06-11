# 别把 wick rejection 只当 K 线形态：`body-vs-wick` 非对称 veto 更像 breakout-short / Fib / EMA-PSAR 的 shared failure filter
- 时间：2026-03-19 06:32 UTC
- 类型：GitHub + 本地快速复核
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/wick-rejection/body-wick-ratio/continuation/failure/filter/repo/crypto/15m
- 证据类型：仓库源码规则 + 公开行情快检（中等证据）

## 1. 这次看了什么
这次主看 **Janis174756/Binance-Futures-Trading-Bot（2026，GitHub）**。这个仓库本身不是学术论文，但有一个对我们 desk 很实用的“旁支”：
- `breakout` 用了非常朴素的 `20` 根区间突破（`close > rolling_high(20)` / `close < rolling_low(20)`）
- `candle_wick` 用了可计算的拒绝结构：比较 `upper_wick / lower_wick` 与 `body`

对当前三条收口线最有价值的不是“照搬策略”，而是把它提炼为一个 **post-entry veto**：
**当 breakout / retest / EMA-PSAR 触发后，若当根或次根出现反向 wick-rejection，就降权或拒单。**

## 2. 核心结论
- **一句话核心结论：** `wick-veto` 更像“非对称过滤器”而不是通用双向增强器；在我们快检里，它对 short follow-up 更有帮助。  
- **一句话说明它怎么证明：** 仓库给了可复现的 wick/body 判定规则；本地用 Binance 公开 15m 数据做 3 币种快检后，short 侧 continuation 成功率提升而 long 侧没有同等改善。
- 本地 15m 快检（BTC/ETH/SOL，各 1500 bars，breakout=20，高低点前移一根）结果：
  1. **Short 侧**：3-bar 同向延续率从 **40.91% (n=176)** 提升到 **43.40% (n=159)**（+2.49 pct，交易数约 -9.7%）。
  2. **Long 侧**：3-bar 延续率从 **37.10% (n=186)** 到 **36.31% (n=168)**（小幅变差）。
  3. 这意味着 `wick-veto` 更适合先服务 **breakout-short follow-up / failure**，不建议无脑双向同权套用。

## 3. 为什么和当前项目有关
- **V3 final-verdict / breakout-short follow-up**：最直接。突破后若出现“反向拒绝 wick”（例如 short 触发后出现明显下影拒绝），优先 veto，可减少末端追空失败。
- **Fibonacci confirmation / retest_hold**：在 retest_hold 的确认 bar 上加 wick 质量检查（“守住”但伴随强反向拒绝形态可降级），可减少假守住。
- **EMA / PSAR raw alpha focus**：不改主触发，只加轻量 post-trigger veto，比继续堆同层新指标更省成本，也更符合“主信号 vs 覆盖层”分工。

## 4. 可复刻的最小实验（下一步怎么测）
### 研究假设
在 15m 上，`wick-veto` 对 short continuation 的改善强于 long，可作为三条线共享的 failure 过滤层（尤其先落地在 short 侧）。

### 可计算定义（先做便宜版本）
- `body = abs(close-open)`
- `upper_wick = high - max(open,close)`
- `lower_wick = min(open,close) - low`
- `bearish_rej = upper_wick > body and lower_wick < body`
- `bullish_rej = lower_wick > body and upper_wick < body`
- breakout-short veto：若 short 触发 bar 或下一 bar 出现 `bullish_rej`，则拒单或 half-size。

### 最小回测切口
- 标的：BTC/ETH/SOL perpetual
- 周期：15m
- 样本：滚动 120d + 60d OOS
- 成本：沿用现有 friction（fee+slippage）
- 对照组：`baseline` vs `wick-veto-short-only` vs `wick-veto-both-sides`

### 第一轮优先指标
- `post_cost_expectancy`
- `false_follow_ratio`（4~8 bars 内反向收回）
- `trade_retention`
- `MAE<1R 占比`

### 下一步怎么测（明确动作）
1. 先仅接入 **breakout-short**，不改出场与其他过滤层；
2. 若 short 侧 `false_follow_ratio` 下降且 `trade_retention` 不崩，再迁移到 Fib retest 与 EMA/PSAR；
3. 最后做 `short-only` 与 `both-sides` 的 OOS 对比，避免把 long 侧劣化引入系统。

## 5. 风险与保留意见
- 来源是工程仓库，不是论文 OOS 结论；应定位为“高可复现假设”，不是已验证 alpha。
- wick/body 阈值对不同币种波动结构敏感，不能直接生产化。
- 本地快检只是单层事件统计，尚未叠加完整仓位/出场/资金费率。

## 6. 来源
1. **Janis174756. (2026). _Binance-Futures-Trading-Bot_. GitHub Repository.**
   - Venue: GitHub
   - DOI: N/A
   - Readable URL: https://github.com/Janis174756/Binance-Futures-Trading-Bot
   - Repo URL: https://github.com/Janis174756/Binance-Futures-Trading-Bot
   - Strategy code URL: https://raw.githubusercontent.com/Janis174756/Binance-Futures-Trading-Bot/main/strategies/trading_strats.py

2. **Binance Futures Public Klines（公开行情）**
   - 数据源：Binance Futures REST API（公开可得）
   - 公开性：公开接口，无私有授权
   - 更新频率：15m K 线可实时拉取
   - URL: https://fapi.binance.com/fapi/v1/klines

3. **本地快速复核结果**
   - 文件：`reports/artifacts/literature/tmp_breakout_wick_rejection_quickcheck_15m_1500bars_20260319.csv`
   - 口径：`BTC/ETH/SOL`，各 1500 根 15m bar，breakout 窗口 20，比较有/无 wick-veto 的 3-bar follow-through
