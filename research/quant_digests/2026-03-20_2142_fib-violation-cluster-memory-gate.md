# 别把 Fib retest_hold 写成“单次触位就确认”：`violation-cluster + 1-bar memory` 更像 15m 的 honest gate
- 时间：2026-03-20 21:42 UTC
- 类型：论文
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/fib/violation-cluster/downtrend/confirmation/filter/paper/crypto/5m/15m
- 证据类型：论文证据（Financial Innovation 全文）

## 1. 这次看了什么
这轮主看 **Gurrib, Nourani, Bhaskaran (2022)** 的论文《Energy crypto currencies and leading U.S. energy stock prices: are Fibonacci retracements profitable?》。我这次不拿它的 headline（“Fib 是否盈利”）当主结论，而是抽一个更适合我们 desk 的旁支：**Fib 水平被连续击穿时，是否应直接否决“retest_hold 成立”**。

## 2. 核心结论（先说人话）
- **一句话核心结论：** Fib 回踩确认不该只看“这根碰没碰到位”，还要看“前 1~2 根是否刚发生同向击穿”，否则很容易把延续失效误判成 hold。  
- **一句话证明方式：** 作者把价格击穿（violation）按上/下行趋势拆开，并统计 `t-1/t-2/t-3` 的连续击穿关系，发现**连续击穿主要集中在最近 1 个 bar**，且在下行阶段更频繁。  
- 样本是 **2017-11 ~ 2020-01** 的日频数据，覆盖 **10 只美股能源股 + 4 只能源加密资产**；虽然不是我们的 15m crypto 口径，但“连续击穿记忆”这个机制可迁移。  
- 论文给出一个很可执行的细节：在能源股里，出现过 **14 次**“当前跌破 23.6%，且 1 天前先破 38.2%”的链式击穿；往前看 2 天、3 天后，这类连续击穿明显变少。  
- Fib + 50 日均线 crossover 的组合并没有稳定变好，反而常出现**交易数下降甚至接近无交易**（作者也提醒这会让 Sharpe 失真），这对我们是警示：别轻易把确认层叠成“稀疏到不可交易”。

## 3. 为什么这轮值得优先做（对齐三条收口线）
这轮直接服务三条收口线，且优先级不低于继续泛找新题：
1. **Fibonacci confirmation / retest_hold：** 这是直接命中；把“触位确认”升级成“触位 + 最近击穿记忆”的更诚实定义。  
2. **V3 breakout-short follow-up：** 若下行阶段本就高发连续击穿，那么“刚破后再回踩失败”更像 continuation，不该过早判成反转。  
3. **EMA / PSAR raw alpha focus：** EMA/PSAR 更适合作为 overlay 去约束 Fib 的误判（例如只在同向趋势中接受 hold），而不是独立接管入场。

## 4. 15m 最小可复现实验（下一步怎么测）
**目标：** 给 `Fib retest_hold` 增加一个“最近击穿记忆”确认/否决层，看它能否减少假 hold。

- 资产：`BTC/ETH/SOL` perpetual  
- 周期：`15m`（可加 `5m` 做执行层）  
- 成本：`6/10/15 bps per side`  
- 执行：`next-bar open + no-overlap`

### 实验三臂（只跑 first verdict）
1. `A: Fib baseline`  
   - 现有 retest_hold 规则，不加记忆项。
2. `B: Fib + violation-cluster veto`  
   - 定义击穿：收盘穿过回踩层（先试 0.5/0.618）超过 `epsilon=0.1*ATR(14)`；  
   - 若 `t-1` 已有同向击穿，则当前 hold 信号 veto；若 `t-1,t-2` 连续击穿，则强 veto。  
3. `C: B + EMA/PSAR role overlay`  
   - Fib 仍是主触发；EMA slope / PSAR side 仅做 admission，不新增方向。

### 先看 4 个指标
- `post_cost_expectancy`  
- `false_hold_ratio@4bars`（入场后 4 根内反向击穿）  
- `trade_count_retention`（不能为了好看把交易数砍没）  
- `timeout_share`（若超时占比高，说明“守住”定义仍过宽）

## 5. 风险与保留意见
- 论文主样本是能源相关资产的**日频**，不是 5m/15m crypto；本轮只能迁移“机制”，不能迁移收益数。  
- 文中部分资产出现极端 Sharpe，本质与交易过少相关，不能当可复制绩效。  
- 论文没有开源 repo，复现需我们自行实现规则口径。  
- 若 `B/C` 让交易数明显塌陷，应先放松 veto 强度（如仅 veto `t-1`，不 veto `t-2`）。

## 6. 来源
1. **Gurrib, I., Nourani, M., & Bhaskaran, R. K. (2022). _Energy crypto currencies and leading U.S. energy stock prices: are Fibonacci retracements profitable?_ Financial Innovation.**  
   - DOI: <https://doi.org/10.1186/s40854-021-00311-8>  
   - Readable URL: <https://jfin-swufe.springeropen.com/articles/10.1186/s40854-021-00311-8>  
   - PDF URL: <https://jfin-swufe.springeropen.com/counter/pdf/10.1186/s40854-021-00311-8>  
   - Repo URL: `N/A (paper-based)`
2. **Binance Developers. USDⓈ-M Futures Kline/Candlestick Data**（用于 5m/15m 最小实验数据）  
   - URL: <https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data>

## 7. 下一步怎么测（一句话）
先把 `Fib retest_hold` 从“单次触位”升级成“触位 + 最近 1~2 bar 击穿记忆”的 B 臂，与 baseline 做同口径成本对比；若 `false_hold_ratio@4bars` 明显下降且交易数仍可用，再考虑升为 shared confirmation。