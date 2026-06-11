# 别把 `retest tolerance` 绑在 `stop-loss%` 上：这会把风险预算误当信号过滤；对 15m 更合理的是“几何容差与风险预算解耦”
- 时间：2026-03-20 14:29 UTC
- 类型：GitHub 仓库 + 本地代理快检
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/retest/tolerance/stop-loss/coupling/execution/risk-overlay/repo/crypto/15m
- 证据类型：工程证据（仓库源码）+ 公开行情代理快检

## 1) 这次看了什么
这轮主看两个 breakout/retest 仓库里一个很容易被忽略、但非常影响 15m 结果可解释性的旁支：**retest 的几何容差（是否算“回踩到位”）到底要不要和 stop-loss 百分比绑死**。

- `komilovmDev/Breakout-and-Retest-Strategy`：`main.py` 里把 `retest_tolerance` 直接设成 `sl_pct`，等于把“入场几何容差”和“风险预算”强耦合。
- `wwakeford/breakout-retest-backtest`：`ENTRY_TOLERANCE`（入场区）与 `POSITION_SIZE/stop`（风险）是分开的，结构上更容易做角色化测试。

这件事和三条收口线都直接相关：
- breakout-short follow-up：确认容差不应跟风险预算同步漂移；
- Fib retest_hold：是否“触位成立”是几何问题，不应由仓位风险参数偷改；
- EMA/PSAR raw alpha：若容差随 stop 一起动，会把“策略改风险”误写成“信号变好了/变坏了”。

## 2) 核心结论（先说人话）
- **一句话核心结论**：在 15m 上，把 `tolerance = stop%` 会导致“调风险预算时，入场样本和表观 alpha 一起漂移”；容差与 stop 应该解耦，分别调参。
- **一句话证明方式**：先用两份仓库代码做工程对照，再在本地 `BTC/ETH/SOL` 的 rank76 baseline 事件上做 8-bar 代理快检，比较“耦合模式 vs 固定容差模式”的样本与收益漂移。

## 3) 最关键数据点（本地 15m 代理）
口径：
- 数据：`reports/artifacts/scout_rank76_intraday_clock_polarity_15m/*`
- 事件：`fib_retest_long / ema_psar_long / breakout_short` baseline，共 `198` 笔
- 评估：`entry_idx` 后 `8 bars` signed return（long 正向，short 取反）
- 距离：`dist = |signal_price - level| / level`，其中 level 分别取 `fib_618 / ema15 / breakout_anchor`

结果（全样本）：
1. **耦合模式（`tol = stop`）非常敏感**：
   - `stop=0.3%`：`n=58`，`win8=36.2%`，`mean8=-12.2 bps`
   - `stop=0.5%`：`n=110`，`win8=42.7%`，`mean8=-4.0 bps`
   - `stop=0.8%`：`n=149`，`win8=49.7%`，`mean8=+15.7 bps`
2. **同样只是在改风险预算，耦合模式却把样本从 58 拉到 149**（+157%），这说明它不是纯风险调节，而是在偷偷改 admission 规则。
3. setup 维度也同向：
   - `ema_psar_long`：耦合下 `mean8` 从 `-1.1 bps (tol=0.3%)` 到 `+31.3 bps (tol=0.8%)`
   - `fib_retest_long`：从 `-15.7 bps` 到 `+15.8 bps`
   - `breakout_short`：三个容差下都偏弱（约 `-10~-18 bps`），提示 short 侧更不该靠“放宽容差”硬救。

> 含义：如果不解耦，你很难判断“是信号改好了”，还是“只是把容差放宽导致样本变了”。

## 4) 对三条收口线的直接落地
- **V3 final-verdict / breakout-short follow-up**：
  先冻结 `follow-up geometry tolerance`（例如按 ATR 或固定 bp），再单独调 short 风险预算；否则 short 侧会被参数耦合放大噪声。
- **Fibonacci confirmation / retest_hold**：
  `是否触位` 用几何容差定义；`仓位/止损` 用风险预算定义，二者拆开后，Fib 的确认层才可审计。
- **EMA / PSAR raw alpha focus**：
  若继续探索 raw alpha，先强制“容差参数独立于 stop 参数”，避免把风险旋钮当信号旋钮。

## 5) 下一步怎么测（最小可执行）
做一个 **2×3 小矩阵**（15m 信号，5m/15m 可各跑一轮）：
1. 容差层（独立）：`tol ∈ {0.3%, 0.5%, 0.8%}` 或 `tol = k * ATR`（k=0.15/0.25/0.35）
2. 风险层（独立）：`stop ∈ {0.3%, 0.5%, 0.8%}`（或 ATR stop）

分别在三条线统计：
- `post_cost_expectancy (6/10/15 bps per side)`
- `trade_count_retention`
- `false_follow_ratio@4/8 bars`
- `parameter_interaction_penalty`（容差×止损交互项）

判决规则：
- 若交互项显著，说明当前“信号层和风险层未分离”；
- 只有交互收敛后，才允许讨论“这条线是否真的有新增 alpha”。

## 6) 风险与保留
- 本轮是代理快检，不是完整撮合级回测；
- `komilovmDev` 仓库规模较小（工程启发价值 > 统计证据价值）；
- 当前样本窗口偏短，后续需滚动 OOS 验证“解耦后稳定性”。

## 7) 来源（paper/repo 信息化列出）
1. komilovmDev. (2025, accessed 2026). *Breakout-and-Retest-Strategy*. GitHub repository.  
   - Authors: GitHub user `komilovmDev`  
   - Year: 2025 (repo updated 2025-11)  
   - Title: Breakout-and-Retest-Strategy  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: <https://github.com/komilovmDev/Breakout-and-Retest-Strategy>  
   - Repo URL: <https://github.com/komilovmDev/Breakout-and-Retest-Strategy>  
2. komilovmDev. (2025, code). *smart-breakout-strategy/src/main.py*, *strategy.py*, *indicators.py*.  
   - 关键点：`retest_tolerance = sl_pct`，并在 `is_retest(..., tolerance_percent)` 中直接用于几何区间。  
   - Readable URL: <https://github.com/komilovmDev/Breakout-and-Retest-Strategy/tree/main/smart-breakout-strategy/src>  
   - Repo URL: <https://github.com/komilovmDev/Breakout-and-Retest-Strategy>
3. wwakeford. (2025, accessed 2026). *breakout-retest-backtest*. GitHub repository.  
   - Authors: GitHub user `wwakeford`  
   - Year: 2025  
   - Title: breakout-retest-backtest  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: <https://github.com/wwakeford/breakout-retest-backtest>  
   - Repo URL: <https://github.com/wwakeford/breakout-retest-backtest>
4. wwakeford. (2025, code). *config.py* / *strategy.py* / *utils.py*.  
   - 关键点：`ENTRY_TOLERANCE` 与 `POSITION_SIZE`/stop 逻辑分离，可独立调 admission 与 risk。  
   - Readable URL: <https://github.com/wwakeford/breakout-retest-backtest/blob/main/config.py>  
   - Repo URL: <https://github.com/wwakeford/breakout-retest-backtest>
5. Binance Futures 公共 K 线（本地缓存来源）  
   - Title: USDⓈ-M Futures Market Data (Kline/Candlestick)  
   - Venue: Binance Developers  
   - DOI: N/A  
   - Readable URL: <https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data>  
   - Repo URL: N/A

## 8) 本轮产物
- `reports/artifacts/quant_digests/retest_tolerance_stop_coupling_proxy_2026-03-20.csv`
- `reports/artifacts/quant_digests/retest_tolerance_stop_coupling_summary_2026-03-20.csv`
