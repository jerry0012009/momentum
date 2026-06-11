# 2026-03-25 01:22 UTC · fresh intake · Technical Analysis Meets Machine Learning: Bitcoin Evidence

## 本轮执行小点
- 槽位：`Fresh intake slot`
- 动作：认领 1 个新的 paper 型 raw alpha 候选，并在最小公开证据 + 本地快检口径下直接回答 `park / keep_P1`。
- 认领对象：**José Ángel Islas Anguiano, Andrés García-Medina (2025) / Technical Analysis Meets Machine Learning: Bitcoin Evidence**（arXiv: `2511.00665v1`）

## 最小公开证据
来自 arXiv 摘要的公开信息：
- 比较对象是 `LightGBM`、`LSTM`、`EMA crossover`、`MACD+ADX` 与 `buy-and-hold`；
- 市场对象是 Bitcoin；
- 论文主叙事是 **ML（尤其 LSTM）显著优于技术指标腿与 buy-and-hold**；
- 技术指标腿本身只是 `EMA crossover` 与 `MACD+ADX` 这两条非常常见的 TA 骨架。

## 本地最小快检（BTC-USD, 近 5y, 1d, next-day open 执行, 10bps 单边切仓成本 proxy）
使用项目现有 `.venv` 的 `yfinance/pandas` 做一个诚实但极简的本地 proxy，只复刻论文里最容易落地的两条 TA 腿，不碰其 ML 特征工程、训练/验证切分、或 ETF 事件窗口叙事。结果：

- `EMA(12,26) crossover long-only`：
  - `rows=1824`
  - `trades=58`
  - `final_mult=1.7405`
  - `CAGR=11.73%`
  - `buy-and-hold final_mult=1.3646`
  - `buy-and-hold CAGR=6.42%`
- `MACD+ADX long-only`：
  - `rows=1824`
  - `trades=102`
  - `final_mult=0.8297`
  - `CAGR=-3.67%`
  - 明显跑输 buy-and-hold

## 结论
这篇 paper 的可执行新增信息并不构成新的 raw alpha identity：
1. `EMA crossover` 与 `MACD+ADX` 都是老骨架；
2. 真正看起来“亮眼”的部分在 `LSTM/ML` 侧，但摘要没有给出足够清楚、可诚实冻结的特征/训练/切分/执行 spec；
3. 本地 proxy 还显示其中一条 TA 腿（`MACD+ADX`）在 BTC 日线上连 buy-and-hold 都打不过，另一条 `EMA crossover` 即便有正 alpha，也不足以把这篇 paper 从“泛化老骨架 + ML 结果展示”抬成新的 survivor。

**本轮 verdict：直接 `park`，不分配 Rank，不进入 survivor。**

## 会改变系统认知的一句话
`Technical Analysis Meets Machine Learning: Bitcoin Evidence` 更像是“ML 结果展示 + 两条老 TA 骨架陪跑”，而不是一个提供新可诚实程序化 spec 的 raw alpha，因此直接 park。
