# 别把 liquidation cascade 只当 overlay：这份 2025 新 repo 更值得先复现的是「跨币共振暴跌后的 panic mean reversion」raw alpha，但原 exit 有前视
- 时间：2026-03-23 21:07 UTC
- 类型：2025 GitHub 新仓库 + 近 5 年论文地基 + Binance 公共数据最小快检
- 主题类型：raw alpha
- 基础 alpha：跨币共振暴跌后的短周期 panic mean reversion（疑似 liquidation cascade 后的超跌反弹）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha/mean-reversion/liquidation-cascade/panic-reversal/cross-asset/event-driven/volume/binance/crypto/5m/15m
- 证据类型：工程经验（新 repo 规则 + 本地快检）+ 论文证据（volatility cascade / short-term reversal 背景）

## 1. 这次看了什么
先回答 base alpha：**这篇东西的 base alpha 不是 filter，而是“多币种同步暴跌 + 放量”后，价格常出现短周期超跌反弹。**

本轮主看 2025 新仓库 **kazan04/Crypto-Stat-Arb**。它给出的不是复杂 ML，而是一套很直白的事件驱动骨架：
- 用 `1h/2h` 累计跌幅 + 放量分位 + `>=3` 个资产同时触发，定义“疑似 liquidation cascade”
- 在 crash bar 收盘做多
- 吃后续 1h/2h 的反弹

但这份仓库最值钱的地方，不是它 README 里的高收益数字本身，而是：**它把“liquidation-like panic event”写成了可复现的 raw alpha 事件定义。**

## 2. 核心结论
- **一句话结论：** “跨币共振暴跌后的 panic mean reversion”值得进 raw alpha 池，而且对 `5m/15m` 很友好；但原仓库 exit 直接用了未来 1h 收益来决定持有期，不能原样当成可交易完整策略。  
- **一句话证明方式：** repo 给了完整规则；我把它翻到 Binance USDT-M 公共数据上做 honest quick check，发现 **entry 逻辑有边，真正该先重做的是 exit 和组合归一化**。

最关键 4 个数据点：
1. repo README 样本（`2023-01-01 ~ 2024-01-31`）写的是：**98 笔、总收益 50.71%、Sharpe 1.81、MaxDD -20.45%**。  
2. 但 repo 的“adaptive exit”其实是：**若未来 1h 收益 > 2% 就持有 1h，否则持有 2h** —— 这是明显前视。  
3. 我用 **最近 120 天、15m、18 个 Binance USDT-M 合约**做平移快检后，得到 **122 笔 asset-level trades / 14 个事件时点**；改成 **固定持有 4 根 bar（1h）** 后，`mean net ≈ +1.83%/trade`、`win rate ≈ 72.95%`，反而**好于** repo 的前视 adaptive 版本（`+1.78%`、`69.67%`）。  
4. 再下钻到 **最近 60 天、5m、10 个合约**，固定持有 **1h / 2h** 分别约为 **`+3.85% / +3.60%` 每笔**；但这仍是 **asset-level 累加**，还没做事件级资金归一化。

## 3. 为什么和当前 desk 直接相关
- 这是 **raw alpha**，不是又一层 veto / overlay。
- 它天然适合短周期 desk：
  - 数据只要 **公开 OHLCV** 就能先跑最小实验；
  - 若以后要升级，再接 **force liquidation / OI / taker flow** 做增强版即可。
- 它补的是我们当前池子里较少的 **event-driven mean reversion**，和 pairs / XS / carry 是互补的，不是同一类东西重复 intake。

## 3.5 策略拆解（必填）
- 方向属性：单资产执行 + 跨资产共振确认；本质是 event-driven mean reversion
- 基础 alpha：panic selloff / liquidation-like cascade 后的超跌反弹
- regime：高杠杆、拥挤、短时波动骤升阶段更强
- filter / veto：
  - 至少 `N` 个资产同步触发
  - 当前 bar 成交量高于滚动高分位
  - 连续事件冷却期 / 大宏观事件 blackout
- risk / sizing / execution overlay：
  - 事件级资金上限（不要把同一时点 10+ 个币都当独立资金）
  - 固定持有 `1h/2h`、triple-barrier 或回归到 VWAP/EMA 的 honest exit
  - 成本必须显式计入 taker fee + 滑点；极端行情还要加 gap 风险

## 4. 本地最小快检（公开可得数据）
### 4.1 数据源、公开性、更新频率、实验口径
- 数据源 A：`kazan04/Crypto-Stat-Arb` 仓库规则与 notebook（公开）
- 数据源 B：Binance USDT-M Futures `klines`（公开 REST，无需 API key）
- 更新频率：支持 `5m/15m/1h`；本轮快检用了 `15m` 与 `5m`
- 最小实验口径：
  - `15m`：最近 120 天，18 个合约，`1h=4 bar`，`2h=8 bar`
  - `5m`：最近 60 天，10 个合约，`1h=12 bar`，`2h=24 bar`
  - 事件定义：沿用 repo 的 `5%/8%` 跌幅、7 天滚动成交量分位、`>=3` 资产同触发
  - 成本：按 repo 口径先扣 **20 bps round-trip**

### 4.2 快检解读
- **entry 有料，exit 要重写。** 15m 上固定 `1h/2h` 持有都不差，说明 repo 真正值钱的是 event definition，不是它的 adaptive hold。  
- **结果高度事件簇集。** 15m 的 122 笔 asset-level trades 其实只来自 **14 个事件时点**，平均每次 **8.7 个资产** 同时触发，最大一次 **17 个资产**；所以 README 那种“把每个资产回报直接累加”更像 alpha intake 证据，不是可直接上实盘的组合报表。  
- **更像“事件篮子策略”，不是单笔独立下注。** 真正落地时，应按“每个事件”分配总风险，再做事件内 cross-sectional 分仓。

## 5. 风险与保留意见
- repo 原版 exit 有前视，不能原样当作完整策略。  
- 本轮快检仍是 **asset-level** 记账，不是 event-level 资本曲线；收益数字偏乐观。  
- 极端下跌里真实成交常伴随滑点、冲击、延迟，20 bps 可能低估。  
- 这类策略天然依赖“大波动日”；平静期会很稀疏，必须接受 pocket 化分布。

## 6. 下一步怎么测（直接可执行）
1. **先做 event-level 回测**：把同一时间戳的多币信号合并成一个事件篮子，限制总风险 `1R`，别再逐资产裸累加。  
2. **重做 honest exit**：优先比较 `固定 1h / 固定 2h / triple-barrier / VWAP reclaim`，不要再用未来收益选持有期。  
3. **补 5m 强化版**：加入 `forceOrder`、OI jump 或 taker imbalance，看能否把“疑似 liquidation”从价格代理升级成更干净的事件判别。  
4. **做容量与成本压力**：把 round-trip 成本从 `20 bps` 提到 `35/50 bps`，并加事件 bar 的 gap-slip 惩罚，看 edge 是否仍存活。

## 7. 来源
1. **Kaza, N. (2025). _Crypto-Stat-Arb / Crypto-Liquidation-Cascades_. GitHub repository.**  
   - Repo URL: https://github.com/kazan04/Crypto-Stat-Arb  
   - Notebook URL: https://raw.githubusercontent.com/kazan04/Crypto-Stat-Arb/main/Liquidation%20Cascade%20Project%20-%20Nitish%20Kaza.ipynb
2. **Gradojevic, N., & Tsiakas, I. (2021). _Volatility cascades in cryptocurrency trading_. Journal of Empirical Finance.**  
   - DOI: `10.1016/j.jempfin.2021.04.005`  
   - Readable URL: https://doi.org/10.1016/j.jempfin.2021.04.005
3. **Zaremba, A., Bilgin, M. H., Long, H., Mercik, A., & Szczygielski, J. J. (2021). _Up or down? Short-term reversal, momentum, and liquidity effects in cryptocurrency markets_. International Review of Financial Analysis.**  
   - DOI: `10.1016/j.irfa.2021.101908`  
   - Readable URL: https://doi.org/10.1016/j.irfa.2021.101908

## 8. 本地复现产物
- `reports/artifacts/quant_digests/liquidation_cascade_20260323/summary.csv`
- `reports/artifacts/quant_digests/liquidation_cascade_20260323/summary_5m.csv`
- `reports/artifacts/quant_digests/liquidation_cascade_20260323/trades.csv`
- `reports/artifacts/quant_digests/liquidation_cascade_20260323/meta.json`
