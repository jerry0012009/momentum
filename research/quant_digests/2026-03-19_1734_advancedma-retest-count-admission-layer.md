# 别把第一次回踩就算确认：`retestCount>=2` 更像 breakout-short follow-up 的 admission layer，对 Fib / EMA long 只算减亏、不算翻正
- 时间：2026-03-19 17:34 UTC
- 类型：GitHub + 本地代理快检
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/retest-count/min-retests/admission/filter/repo/crypto/15m
- 证据类型：repo 规则（工程证据）+ 公开行情代理快检

## 1. 这次看了什么
这轮看的是 **Simone Gitter (2025) 的 `AdvancedMA-Toolkit`**。我没有照搬它整套 `14 MA + retest zones + Auto-RR` 的指标生态，而是只抽一个更贴近当前 desk 三条收口线的问题：

**repo 明确把“要不要等第二次回踩”写成了参数。**

源码里能直接看到这几项：
- `Enable Retest System`
- `Repeat signals on each retest`
- `Retest Zone %`
- `Min Retests for Signal`
- `Use Patterns Confirmation`

其中最值得偷的不是“又一个 MA 工具包”，而是这句非常具体的执行语义：

> **先把回踩定义成 zone，再决定最少要几次 retest 才允许发信号。**

这正好击中我们现在的模糊点：
- breakout-short follow-up 到底要不要等“第一次上抽没杀死它、第二次再确认”；
- Fib / retest_hold 到底是一碰位就接，还是该把第一次触位看成 probe、第二次才当 admission；
- EMA / PSAR continuation 到底是“方向对就直接上”，还是至少要有一次没被打穿的 retest 记忆。

## 2. 核心结论
1. **一句话核心结论**：`retestCount>=2` 值得测，但它**不是三条线共享的万能 gate**；在这轮 15m 代理口径里，它更像 **breakout-short follow-up 的 admission layer**，对 Fib / EMA long 侧只能算“减亏”，还不够格升成通用放行条件。  
2. **一句话证明方式**：我把 repo 的 `Min Retests for Signal` 思路，映射成一个公开 Binance Futures 15m 代理实验：`20-bar breakout -> level zone retest -> 第一次/第二次有效 retest close back across level -> next-bar open -> hold 4 bars -> round-trip 12bps`，看第二次回踩是否更诚实。  
3. 公开行情代理快检（BTC/ETH/SOL，近 1500 根 15m K）结果：
   - **long pooled**：`first_touch` 的 `mean_net_bps_h4 = -26.5bps`，到 `second_touch` 变成 **`-15.1bps`**；`hold4` 仅 **46.4% -> 49.2%**，`fail_close4` **55.1% -> 49.2%**，样本 `69 -> 59`。也就是：**少亏一点，但还没翻正。**
   - **short pooled**：`first_touch` 的 `mean_net_bps_h4 = -2.2bps`，到 `second_touch` 变成 **`+0.3bps`**；`fail_close4` **36.6% -> 34.4%**，样本 `82 -> 64`。也就是：**短侧更像真的被 second-touch 改善了。**
   - **cross-asset mean（更诚实）**：short 侧从 **`-2.22bps -> +1.67bps`**；但不是全币一致——BTC short **`-16.1 -> +3.3bps`**、ETH short **`+8.4 -> +8.5bps`**，SOL short 反而 **`+1.0 -> -6.8bps`**。
4. 这说明它更像在回答：**“第一次回踩要不要先当 probe，而不是立刻当确认？”** 对 short follow-up，答案偏向 **值得等一下**；对 long retest_hold，答案更像 **不能只靠 retest 次数**。

## 3. 为什么它直接服务当前三条收口线
- **V3 final-verdict / breakout-short follow-up（最直接）**：这条最像 short 侧的 post-break path 过滤。第一次上抽没死，不代表就该追；**第二次再回抽、还能收回 level 下方**，更接近“反抽衰减后继续下行”的 follow-up 条件。当前代理结果里，它也是唯一接近从负到正翻过去的一侧。  
- **Fibonacci confirmation / retest_hold**：这轮给 Fib 的启发不是“第二次触位就一定更好”，而是相反——**如果只多加一个 retest count，long 侧改善有限**。所以 Fib 更像要把 `retestCount` 放进 **确认分层**，而不是单独 hard gate。  
- **EMA / PSAR raw alpha focus**：EMA / PSAR 继续负责方向读法；`retestCount` 更适合放在 **触发后的 admission delay**，尤其是 short / breakdown follow-up。对 long continuation，当前证据不支持把“等第二次回踩”直接升级成 shared rule。  

如果问“为什么这题比继续翻旧派生假设更值”：因为它来自 **fresh repo source**，而且补的是三条线共同缺的一块执行语义——**回踩到底是一次确认，还是两次确认。**

## 4. 下一步怎么测（5m / 15m 最小实验）
### 4.1 数据与公开性
- 数据源：`AdvancedMA-Toolkit` 仓库规则 + Binance Futures 公共 K 线 API  
- 公开性：公开可得  
- 更新频率：5m / 15m（本轮先做 15m 代理）  
- 本轮产物：
  - `reports/artifacts/quant_digests/advancedma_retest_count_proxy/event_log.csv`
  - `reports/artifacts/quant_digests/advancedma_retest_count_proxy/asset_summary.csv`
  - `reports/artifacts/quant_digests/advancedma_retest_count_proxy/overall_summary.csv`
  - `reports/artifacts/quant_digests/advancedma_retest_count_proxy/summary_snapshot.json`

### 4.2 最小可复现实验口径（建议先做这个）
不要把它先升成三线共享 hard gate，先做**方向拆分**：

1. **breakout-short follow-up**
   - 在当前 `V3 final-verdict / follow-up` 上新增 `min_retests_before_entry ∈ {1,2}`；
   - 统一冻结：`signal bar close 后 -> next-bar open -> hold 8 bars -> 6/10/15bps per side`；
   - 只看 3 组：`baseline / second-touch only / second-touch + candle-quality(CL V或body-wick)`。

2. **Fib confirmation / retest_hold**
   - 不要单测 `second-touch only`；
   - 只测 `touch_count` 作为 admission score 子项，跟 `volume / reclaim / small-body` 绑一起；
   - 对照：`reclaim-only / reclaim+volume / reclaim+volume+touch_count>=2`。

3. **EMA / PSAR raw alpha**
   - long 侧默认不要强制 `>=2`；
   - short 或 breakdown 侧才允许先做 `1 vs 2 touches` 的 cheap honesty check；
   - 若 `trade_count_retention < 70%` 且收益没明显改善，直接降级为 setup-specific overlay。

先看 5 个指标：
- `post_cost_expectancy`
- `trade_count_retention`
- `hold8_rate`
- `fail_close_ratio`
- `time-pocket stability`

## 5. 风险与保留意见
- 源 repo 是 **工程实现 + TradingView 指标生态**，不是论文；证据强度来自“规则写得足够清楚、能快速做代理快检”，不是正式跨市场统计检验。  
- 本轮代理实验用的是 **20-bar breakout level retest**，不是你三条线的原始信号本体；所以当前结论应读成 **执行层启发**，不是最终策略 verdict。  
- `second_touch` 本身会天然降样本；如果后续 OOS 发现收益改善主要来自“少交易”，而不是失败率真下降，应把它降级成 **short-side admission delay**，不要硬说成 shared alpha。  
- 跨资产分化已经出现：SOL short 这轮是反例，说明这条线更像 **state / asset dependent**，不是 universal truth。

## 6. 来源
1. **Simone Gitter. (2025). _AdvancedMA Toolkit_.**
   - Venue: GitHub / TradingView
   - DOI: N/A
   - Readable URL: <https://github.com/SimoneGitter/AdvancedMA-Toolkit>
   - Repo URL: <https://github.com/SimoneGitter/AdvancedMA-Toolkit>
2. **核心源码**：`src/AdvancedMA_Toolkit_Private.pine`
   - 关键字段：`retestEnabled`、`repeatSignals`、`retestPct`、`minRetests`、`usePatterns`
   - Readable URL: <https://github.com/SimoneGitter/AdvancedMA-Toolkit/blob/main/src/AdvancedMA_Toolkit_Private.pine>
   - Raw URL: <https://raw.githubusercontent.com/SimoneGitter/AdvancedMA-Toolkit/main/src/AdvancedMA_Toolkit_Private.pine>
3. **仓库说明**：`README.md`
   - 关键词：`Advanced retest zones`、`Filter stack`、`Dual signals`
   - Readable URL: <https://github.com/SimoneGitter/AdvancedMA-Toolkit/blob/main/README.md>
4. **仓库元数据（创建/更新时间）**
   - URL: <https://api.github.com/repos/SimoneGitter/AdvancedMA-Toolkit>
5. **公开行情数据源**
   - Binance Futures Klines API: <https://fapi.binance.com/fapi/v1/klines>
