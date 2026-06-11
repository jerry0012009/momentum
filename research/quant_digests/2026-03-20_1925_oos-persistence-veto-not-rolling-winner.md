# 别把“最近最优规则”直接滚动上实盘：OOS 持续性证据更支持把 EMA/PSAR 放在 overlay，并给 breakout-short / Fib 设置低换手确认层
- 时间：2026-03-20 19:25 UTC
- 类型：论文
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/oos/persistence/transaction-cost/rolling-selection/filter/paper/crypto/5m/15m
- 证据类型：论文证据

## 1. 这次看了什么
这轮看的是 **Kevin Rink (2023)** 的大样本技术规则研究。headline 是“技术规则有没有预测力”，但这次我们只拿一个更贴近 desk 的旁支问题：**能不能把“最近一段最优参数/最优规则”直接滚动到下一段实盘**。

## 2. 核心结论
- **一句话核心结论：** 对 15m 来说，“recent winner 直接滚动”更像过拟合放大器；EMA/PSAR 现阶段更适合做 `admission/fail-fast overlay`，不该继续当独立主触发。  
- **一句话怎么证明：** 论文在 `6406` 条规则、`23` 个发达市场 + `18` 个新兴市场上做了多重检验、成本敏感性和 OOS 持续性检验，结果显示 in-sample 好看，但 OOS 持续性显著塌陷。

关键数据点（直接可迁移）：
1. **样本与规则规模**：`6406` 条规则（RSI/filter/MA/SR/channel breakout 五大类）跨 `41` 个市场、最长 `66` 年。  
2. **成本一加就塌**：single-trip 成本到 `20 bps` 时，仍有显著规则的市场只剩 `5/23`（发达）和 `4/18`（新兴）。  
3. **OOS 最近最优失效**：在 `25 / 50 bps` single-trip 成本下，OOS 显著跑输 buy-and-hold 的市场分别达到 `14` 与 `18` 个；组合层面 50 bps 时 excess Sharpe 约为 `-0.315`（发达）/`-0.507`（新兴）/`-0.385`（全市场）。

## 3. 为什么和三条收口线直接相关
- **V3 final-verdict / breakout-short follow-up**：不要再把“最近最好的一组 breakout follow-up 参数”直接滚动；先做稳定性与换手约束，否则是把噪声当 verdict。  
- **Fibonacci confirmation / retest_hold**：Fib 更适合当低换手确认层（减少高频切换），而不是参与“滚动挑最优触发器”的主信号竞赛。  
- **EMA / PSAR raw alpha focus**：当前更应定位为角色层（admission / fail-fast / veto），而不是继续按“独立主 alpha + 滚动最优参数”推进。

## 4. 可复刻的最小实验（5m/15m）
### 假设
`rolling winner` 在 15m 上会显著高估可部署性；`stable trigger + EMA/PSAR overlay` 更抗 OOS 退化。

### 设计（当天可跑）
- 标的：`BTC/ETH/SOL` perpetual  
- 周期：`15m`（可加 5m 执行层）  
- 成本：`6 / 10 / 15 bps per side`  
- 评估窗口：滚动 `train 60d / test 14d`（至少 6 个滚动窗）

三臂对照：
1. `A`：breakout-short / retest_hold 固定模板（不滚动挑最优）  
2. `B`：每窗在候选集中挑“最近最优”后滚动到下一窗（rolling winner）  
3. `C`：A 的触发不变 + EMA/PSAR 仅做 overlay（admission/fail-fast）

必看指标：
- `post-cost expectancy`  
- `OOS decay ratio`（test/train）  
- `turnover` 与 `trade-count retention`  
- `false-follow-through@4bars`（尤其 breakout-short）

**判决门槛（最小版）**：若 B 的 OOS decay 明显差于 A/C，且成本后优势不稳定，则把“rolling winner 主流程”降级为研究工具，不进入主流程。

## 5. 风险与边界
- 论文主样本是股票指数，不是 crypto perpetual；我们借的是“方法学证据”（OOS 持续性与成本约束），不是收益数值本身。  
- 这轮不是否定 EMA/PSAR，而是限制其角色：先当 overlay，等看到跨窗口净收益稳定再考虑升格。  
- breakout-short 的 short 侧仍需单独评估，不能用 long 侧稳定性替代。

## 6. 来源
1. **Rink, K. (2023). _The predictive ability of technical trading rules: an empirical analysis of developed and emerging equity markets_. Financial Markets and Portfolio Management, 37, 403–456.**  
   - Authors: Kevin Rink  
   - Year: 2023  
   - Title: The predictive ability of technical trading rules: an empirical analysis of developed and emerging equity markets  
   - Venue: Financial Markets and Portfolio Management  
   - DOI: `10.1007/s11408-023-00433-2`  
   - Readable URL: `https://doi.org/10.1007/s11408-023-00433-2`  
   - Open PDF URL: `https://link.springer.com/content/pdf/10.1007/s11408-023-00433-2.pdf`  
   - Repo URL: `N/A (paper)`
