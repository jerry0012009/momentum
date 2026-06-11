# 别把 ETF 只当日线新闻：5m 里 `ETF 先行强度` 更像 breakout-short / Fib / EMA-PSAR 的 shared regime gate
- 时间：2026-03-19 05:01 UTC
- 类型：论文 + 外部数据
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/etf-flow/price-discovery/regime/filter/position-sizing/paper/crypto/5m/15m
- 证据类型：论文证据 + 快速工程复核

## 1. 这次看了什么
这次主看 **Azhar Mohamad (2025)** 的 5 分钟论文（ETF 与 BTC 现货谁先发现价格），并用 **Guliyev & Ahmadova (2025)** 的 ETF 资产-价格协整结果补“低频资金压力”地基，再用公开 Yahoo 5m 数据做了一个最小复核。

## 2. 核心结论
- **一句话核心结论：** 对 5m/15m 来说，ETF 不只是“宏观背景音”，它可以被做成一层可计算的 **先行强度 gate（filter+sizing）**，专门服务 breakout/fib/EMA-PSAR 的放行与降权。
- **一句话说明它怎么证明：** 论文用 5m 价格发现指标（IS/CS/ILS）直接测“谁先动”，再用日频协整验证“ETF 资金规模与 BTC 价格有长期绑定关系”，不是靠主观叙事。
- Mohamad (2025) 在 2024-01-11~2024-10-11 的 5m 数据上显示：**IBIT/FBTC/GBTC 对 BTC spot 的 ILS 领先约 85% 时段**（论文原文表述）。
- 同文中交易份额变化也支持“ETF 成为主导交易入口”：IBIT 20d 平均成交份额从 **47.6%** 上升到 **71.3%**，GBTC 从 **22.8%** 降到 **7.7%**，FBTC 从 **16.0%** 降到 **10.5%**。
- Guliyev & Ahmadova (2025) 用 352 个交易日（2024-01-11~2025-05-16）做 FMOLS/DOLS/CCR：ETF 资产与 BTC 价格 **10% 显著性下协整成立**，长期弹性约 **1.27~1.32**（LTNF 系数）。
- 我们用公开 Yahoo 5m 做的 60d 快检（IBIT+FBTC+GBTC 美元成交额加权）也有同方向信号：
  - `corr(ETF_t, BTC_{t+1}) = 0.213` vs `corr(BTC_t, ETF_{t+1}) = 0.028`
  - 1 小时滚动窗里 ETF 领先占比约 **80.7%**
  - 高 ETF 脉冲（|ret| z>1）时，BTC 未来 3 根同向命中约 **57.5%**（全样本约 53.9%）

## 3. 为什么和当前项目有关
- 对 `V3 final-verdict / breakout-short follow-up`：可把“是否处在 ETF 主导时段”作为 continuation 放行条件，减少无主导资金时的假延续。
- 对 `Fibonacci confirmation / retest_hold`：回踩守住后若 ETF 先行方向不一致，可直接降权或 veto，避免“价位对了、资金没跟”的假确认。
- 对 `EMA / PSAR raw alpha focus`：不改主信号，只加一层**成本友好**的仓位闸门（aligned 放大，conflict 缩仓），优先解决 OOS 生存与角色分工问题。
- 这题比继续微调单一入场参数更值钱：它是三条收口线可共用的上层状态变量。

## 4. 可复刻的最小实验
- 研究假设：15m 主信号若叠加 `ETF lead regime`，post-cost 质量优于裸信号；尤其能改善 follow-up 的假突破/假跌破。
- 一个可计算定义（5m 执行层）：
  - `etf_ret = Σ(w_i * ret_i)`，`i∈{IBIT,FBTC,GBTC}`，`w_i` 为当根美元成交额权重
  - `lead_edge = corr_12(etf_ret_t, btc_ret_{t+1}) - corr_12(btc_ret_t, etf_ret_{t+1})`
  - `impulse_z = zscore_288(|etf_ret|)`
  - `ETF_lead_regime = (lead_edge > 0.08) & (impulse_z > 1.0)`
- 接到三条线的执行规则（先测最小版）：
  1) breakout-short follow-up：方向一致 + regime=true 才满仓；regime=false 半仓；方向冲突 veto。
  2) fib retest_hold：仅在 regime 支持方向时允许“确认后加仓”。
  3) EMA/PSAR：`size_mult = 1.25/0.75/0.0`（同向/中性/反向）。
- 最小回测切口：BTC/ETH/SOL perp，近 180d，15m 产信号、5m 执行，含手续费与滑点。
- 最该先看：`post-cost Sharpe`、`false_break_ratio`、`MAE<1R 占比`。

## 5. 风险与保留意见
- 论文样本主要覆盖 ETF 上市后的新制度期，结构性变化（政策/交易时段/参与者）可能让系数漂移。
- Mohamad 使用 Bitstamp + LSEG；我们快检用 Yahoo 代理，存在交易时段与微观噪声差异，不应直接当生产参数。
- ETF 领导性在极端加密原生事件（交易所/链上事故）下可能失效，需加事件黑名单。
- 协整结果显著性在 10% 水平，说明“有信号但不该神化”，更适合当 overlay 而非主入场。

## 6. 来源
1) Mohamad, A. (2025). *Do Bitcoin ETFs Lead Price Discovery Following their Introduction in the Bitcoin Market?* Computational Economics.
- DOI: https://doi.org/10.1007/s10614-025-10998-x
- Readable URL: https://link.springer.com/article/10.1007/s10614-025-10998-x
- PDF URL: https://link.springer.com/content/pdf/10.1007/s10614-025-10998-x.pdf
- Repo URL: N/A（论文）

2) Guliyev, T., & Ahmadova, A. (2025). *From Flows to Value: Cointegration Between Bitcoin Spot ETF Assets and Bitcoin Price.* Ledger.
- DOI: https://doi.org/10.5195/ledger.2025.393
- Readable URL: https://ledger.pitt.edu/ojs/ledger/article/view/393
- PDF URL: https://ledger.pitt.edu/ojs/ledger/article/download/393/331
- Repo URL: N/A（论文）

3) 快速复核数据（公开）
- Yahoo Finance Chart API (5m):
  - https://query1.finance.yahoo.com/v8/finance/chart/IBIT?range=60d&interval=5m
  - https://query1.finance.yahoo.com/v8/finance/chart/FBTC?range=60d&interval=5m
  - https://query1.finance.yahoo.com/v8/finance/chart/GBTC?range=60d&interval=5m
  - https://query1.finance.yahoo.com/v8/finance/chart/BTC-USD?range=60d&interval=5m
- 快检结果文件：`reports/artifacts/literature/tmp_etf_lead_quickcheck_60d.csv`
