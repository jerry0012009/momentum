# 别把这份 2021 market-neutral repo 只读成“老式 pairs 教程”：对 short-cycle desk，更该先测的是「EMA-band ratio spread × corr/vol gate × 双腿对冲执行」这条完整 raw alpha

- 时间：2026-04-07 12:06 UTC
- 类型：GitHub repo source audit（`README.md` + `main_me.py` + `strategy2.py` + `strategy4.py` + `executor.py` + `broker.py`）
- 主题类型：raw alpha
- 基础 alpha：同一交易时钟下，两资产价格比值（`asset1/asset2`）偏离其 EMA 中枢后，存在回归；通过相关性与波动门槛过滤，再用多空对冲腿吃回归段。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / pairs / stat-arb / relative-value / mean-reversion / ratio-spread / corr-gate / volatility-gate / binance-futures / 15m / repo / execution / risk
- 证据类型：工程经验

## 1. 这次看了什么
这次看的是 **Dzenan Hamzic (2021)** 的 GitHub 仓库 **`dzenanh/crypto-derivative-trading-engine`**。虽然仓库较早，但它不是“只给信号公式”的半成品，而是把可交易链条写全了：
- `strategy2.py` / `strategy4.py`：信号定义（ratio spread + band + gate）
- `executor.py`：按周期取 K 线、更新信号并路由到执行
- `broker.py`：双腿开平仓、仓位切换、杠杆/数量处理、资金划转

其中最适合当前 desk 直接 intake 的，不是泛化“market-neutral”口号，而是 `strategy2.py` 这条更具体的 raw alpha 壳。

## 2. 核心结论
- **一句话核心结论：** 这份 repo 真正可复用的核心是“**ratio spread 回归本体 + corr/vol 双门槛 + 双腿切换执行**”，而不是单纯 Bollinger 带穿越。
- **一句话证明方式：** 证据来自源码级闭环：`strategy2.py` 明确定义 entry/exit；`main_me.py` 给出默认资金参数；`executor.py` 固定取 `15m`、`7d`、`80 bars`；`broker.py` 明确双腿下单与翻仓路径。
- `strategy2` 的参数是可直接抄到 first verdict 的：`std=1.1`、`ma_length=60`、`std_length=80`、`roll_correlation_len=30`、`corr_coef=0.8`、`volatility=0.001`。
- 入场不是裸带宽：
  - long spread：`spread < lower_band` 且 `corr > 0.8` 且 `volatility > 0.001`
  - short spread：`spread > upper_band` 且 `corr > 0.8` 且 `volatility > 0.001`
- 出场也清晰：都回到 `middle_band`（中轨）即平仓。
- 默认标的是 `RSRUSDT / SXPUSDT`，周期是 `Client.KLINE_INTERVAL_15MINUTE`；`main_me.py` 默认 `moneyAmount=20`（每策略资金参数），`trade_mode="DRYRUN"`。
- 执行层不是“只打印信号”：`broker.py` 里双腿切换是显式的（`1 -> 0 -> -1` 或反向），并做 `moneyAmount/2` 分腿；下单前用 `mark price` 算数量并乘 `0.995` 留安全边际，默认 `leverage=1`、`CROSS`。

## 3. 为什么和当前项目有关
这条线和当前 `momentum` 主线高度相关，原因是它补的是 **可直接复现的 pairs/stat-arb 原料**，而不是再做解释型综述：
1. **base alpha 清晰**：ratio spread 回归（raw alpha），不是 filter 伪装。
2. **短周期兼容**：默认 `15m`，可自然压缩到 `5m/3m`。
3. **可落地完整策略**：entry / exit / sizing / execution / risk 都已有代码骨架。
4. **适合做“快验证”**：参数量有限，先跑 first verdict 再谈复杂配对筛选。

## 3.5 策略拆解（必填）
- 方向属性：relative value / pairs / mean reversion
- 基础 alpha：`asset1/asset2` ratio spread 偏离中枢后回归
- regime：相关性仍有效且 spread 波动未塌陷的时段
- filter / veto：`corr > 0.8` + `spread volatility > 0.001`（strategy2）
- risk / sizing / execution overlay：双腿对冲、分腿资金（`moneyAmount/2`）、翻仓前先平、数量按标记价+精度取整、`0.995` 安全折减

## 4. 可复刻的最小实验（下一步怎么测）
**研究假设：** `strategy2` 的 “ratio band + corr/vol gate” 在 crypto `15m` 上可形成成本前可见的 spread 回归 edge，并可部分迁移到 `5m`。

**最小实验口径（公开数据可做）：**
- 标的：先复现 repo 默认 `RSRUSDT/SXPUSDT`，再扩到 5~10 组高流动性候选 pair
- 周期：`15m`（主）+ `5m`（迁移）
- 信号：严格按源码参数（`1.1σ`、`60/80`、`corr 30`、`corr>0.8`、`vol>0.001`）
- 执行：按 bar close 触发、下一根开盘成交（先做保守 fill）
- 成本：先 8/12/20 bps 三档 friction ladder

**先看 3 个指标：**
1. post-cost spread return（成本后）
2. trade count & holding bars（机会是否够）
3. leg imbalance / flip loss（翻仓损耗是否吞噬 edge）

若 `15m` 成立、`5m` 退化明显，则下一步只把 `5m` 当触发层，把 `15m` 保留为 direction gate。

## 5. 风险与保留意见
- 仓库年份较早（2021），参数可能贴合当期市场微结构，**不能直接假设今天仍稳健**。
- 默认 pair（`RSR/SXP`）存在流动性/结构变化风险，必须做 rolling pair admission。
- 源码里未见完整手续费/滑点建模细节（主要是执行数量安全折减），所以 first verdict 一定要先补 friction ladder。
- 相关性门槛是静态阈值（`0.8`），容易在 regime 切换时过严/过松，后续可做分位阈值替代。

> **最值得复用/复现的点：** 不是某个“神阈值”，而是“raw alpha（ratio MR）+ gate（corr/vol）+ 双腿执行”的完整拆解方式。

## 6. 来源
1. **Hamzic, D. (2021). _crypto-derivative-trading-engine_. GitHub Repository.**
   - Venue：GitHub
   - DOI：N/A
   - Readable URL：`https://github.com/dzenanh/crypto-derivative-trading-engine`
   - Repo URL：`https://github.com/dzenanh/crypto-derivative-trading-engine`
   - 最近提交（本地 clone）：`11299d3`（2021-06-01）
2. **关键源码（raw）**
   - `strategy2.py`：`https://raw.githubusercontent.com/dzenanh/crypto-derivative-trading-engine/main/diversifly/components/products/strategies/strategy2.py`
   - `strategy4.py`：`https://raw.githubusercontent.com/dzenanh/crypto-derivative-trading-engine/main/diversifly/components/products/strategies/strategy4.py`
   - `main_me.py`：`https://raw.githubusercontent.com/dzenanh/crypto-derivative-trading-engine/main/main_me.py`
   - `executor.py`：`https://raw.githubusercontent.com/dzenanh/crypto-derivative-trading-engine/main/diversifly/components/core/executor.py`
   - `broker.py`：`https://raw.githubusercontent.com/dzenanh/crypto-derivative-trading-engine/main/diversifly/components/core/broker.py`
