# 别把这条 2024 crypto stat-arb repo 当成“大而全笔记本”：它真正值得 intake 的是一个可直接压成 P1 的 carry+momo+breakout 横截面骨架

> Post-hoc identity note（2026-03-24 10:53 UTC）：该对象现已正式分配 `Rank 154`；后续 desk 口径统一写作 `Rank 154 / Crypto-Stat-Arb`。
- 时间：2026-03-24 09:22 UTC
- 类型：2024 GitHub repo / blog 研究 / 源码级可复核 intake
- 主题类型：raw alpha
- 基础 alpha：在 Binance 永续前 30 流动性币种里，把 `carry(24h funding)`、`momentum(10d return)`、`breakout(20d high proximity)` 组合成日频横截面 long-short 权重
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：基本是
- 主题标签：raw-alpha/cross-sectional/momentum/carry/breakout/stat-arb/perps/crypto/repo/blog/daily/binance
- 证据类型：README + notebook + backtest helper 源码

## 1. 这次看了什么
本轮按 desk 的 `fresh intake` 重开前排，认领的是公开 repo：`ryanczm/Crypto-Stat-Arb`。

我重点不是看它回测曲线漂不漂亮，而是看三件事：
1. **是不是独立候选，而不是一堆旧想法拼盘；**
2. **有没有完整策略骨架，而不是只停在 feature 展示；**
3. **有没有最起码的成本/执行诚实性入口。**

结论是：这条线虽然不新鲜到 2026，但作为公开、可复核、可直接压成下一步最小验证的 `fresh intake` 是合格的，而且它的“可交付物”很明确：**一个可 clean-room 重写的 crypto perp 横截面组合框架**。

## 2. 核心结论
- **一句话核心结论：** `Crypto-Stat-Arb` 不是“又一个泛泛量化 notebook”，而是一个可直接进入 `keep_P1` 的完整横截面 raw-alpha 骨架。
- **一句话为什么：** 它已经把 `universe / signal / weighting / funding / fee / trade buffer` 接成闭环，缺的不是策略定义，而是我们自己的最小诚实 follow-up：确认净边是不是主要被 carry 单腿撑着、以及成本后是否仍有 survive 空间。

## 3. 最关键的源码证据
### 3.1 它不是纯概念，已经有完整骨架
README 直接给出对象定义：
- 标的：Binance perpetual futures；
- 宇宙：滚动成交量前 30；
- 因子：carry / momentum / breakout；
- 结构：research notebook + backtest notebook + `rsims.py` 回测执行器。

### 3.2 它的 base alpha 能翻成人话
先把术语翻成人话：
- **carry**：谁的资金费率更极端，可能更有“拥挤定价/补偿”信息；
- **momentum**：过去 10 天涨得更强的币，短期可能继续强或至少能提供排序信息；
- **breakout**：离 20 日新高越近，说明价格结构越强。

作者不是把三者各自单独做策略，而是把它们压成**每天一篮子多空权重**：
- `carry_weight = decile_carry - 5.5`
- `momo_weight = decile_momo - 5.5`
- `breakout_weight = breakout / 2`
- `combined_weight = 0.5*carry + 0.2*momo + 0.3*breakout`

这意味着它更像**横截面 stat-arb 组合 alpha**，不是单币种方向盘。

### 3.3 它已经显式接入成本/执行，不是完全 frictionless 自嗨
在 `stat-arb-backtest.ipynb` / `rsims.py` 里，作者已经放进了两类很关键的诚实项：
- **手续费**：`commission_pct=0.0015`（15bps 单边口径的代码参数，至少说明它没假装零成本）；
- **no-trade buffer**：`trade_buffer=0.05`，避免每天围着目标权重抖动乱换仓；
- **funding 计入**：回测函数 `fixed_commission_backtest_with_funding(...)` 把 funding rates 纳入 period PnL。

这不等于它已经足够真实，但至少说明：**这条线不是只有“因子相关性好看”，而是已经有执行摩擦入口。**

## 4. 为什么它能进 keep_P1，而不是直接 park
### 4.1 进 `keep_P1` 的理由
1. **可独立复现**：repo 自带数据、研究 notebook、回测 notebook；
2. **可直接落地完整策略骨架**：宇宙、信号、组合、费用、buffer 都有；
3. **不是纯 filter/overlay**：base alpha 就是横截面排序后的多空篮子；
4. **跟当前 desk 相关**：属于 `cross-sectional momentum / carry / breakout` 家族，可补 current intake 池，不是旧对象 reopen。

### 4.2 不能直接升 P2 的理由
1. **主要是日频 2019-2024 样本**，离我们当前偏好的 `1m/3m/5m/15m` 研发主战场有距离；
2. **三因子混合后，很容易出现“其实只有 carry 在撑”的伪组合边际**；
3. **作者也承认存在 lookahead / 教学式简化痕迹**，还不能当 admission 级证据；
4. **没有我们自己的 post-cost、分腿归因、近窗诚实复核。**

所以最合理的位置不是 `park`，也不是直接 `P2`，而是：**先留在 `Surviving candidate`，只给它一次最小 decisive follow-up。**

## 5. 紧邻子点：唯一值得补的 follow-up 是什么
只补一个最关键缺口：**做分腿归因 + 成本敏感性 honesty check**。

目标不是大重写，而是直接回答：
- 这条组合边际到底是谁贡献的？
- `momo/breakout` 是真有净贡献，还是只是帮 carry 做包装？
- 在更保守费用/换手假设下，它是 `promote_P2` 还是 `park`？

一个合格的最小 follow-up 可以是：
- 沿用 repo 数据与框架；
- 分别输出 `carry / momo / breakout / combined` 的 post-cost 曲线或最小 summary；
- 至少给两档成本/缓冲敏感性；
- 最终只回答 `promote_P2 / park`。

## 6. desk verdict
**本轮 intake verdict：`keep_P1`。**

### 一句话 desk result
`ryanczm/Crypto-Stat-Arb` fresh intake 已完成并进入 keep_P1：它提供了可独立复现的 crypto perp 横截面 carry+momo+breakout 完整骨架，且已显式接入 funding / fee / trade buffer，但还缺一次最小分腿归因与成本敏感性诚实检查，暂不升 P2。

## 7. 来源
1. Ryan Chew (`ryanczm`) (2024). *Crypto-Stat-Arb*. GitHub Repository.  
   - Repo: https://github.com/ryanczm/Crypto-Stat-Arb
2. Ryan Chew (2024-03-10). *Crypto Stat Arb: Quantifying & Combining Alphas*.  
   - URL: https://analytic-musings.com/2024/03/10/crypto-stat-arb-I/
3. Repo source files inspected directly:  
   - `quantifying-crypto-alphas.ipynb`  
   - `stat-arb-backtest.ipynb`  
   - `rsims.py`
