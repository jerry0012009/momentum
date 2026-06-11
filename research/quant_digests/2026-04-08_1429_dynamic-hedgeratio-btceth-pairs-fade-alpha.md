# 别把这份 2025 实时 pairs repo 只读成 dashboard：对 short-cycle desk，更该先测的是「dynamic hedge ratio spread × z-score fade」这条 BTC/ETH raw alpha

- 时间：2026-04-08 14:29 UTC
- 类型：GitHub repo source audit + Binance Spot public `1m/5m` portability probe
- 主题类型：raw alpha
- 基础 alpha：`BTC/ETH dynamic hedge-ratio spread mean reversion`
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是，但当前 repo 需补 sizing / hard risk / execution realism
- 主题标签：pairs / stat-arb / relative-value / mean-reversion / dynamic-hedge-ratio / zscore / BTC / ETH / 1m / 5m / repo / public-data / cost / risk
- 证据类型：工程经验 + 本地最小可移植性验证

## 1. 这次看了什么
这次主看 **KulkarniPushakar (2025)** 的 GitHub 仓库 **Real-Time Crypto Pair Trading Analytics Platform**（commit `fb49d7b`，repo 更新时间 `2025-12-17`）。source audit 重点覆盖：`README.md`、`analytics/hedge_ratio.py`、`analytics/spread.py`、`analytics/zscore.py`、`analytics/backtest.py`、`analytics/runner.py`、`analytics/resample.py`、`analytics/ADF_test.py`、`analytics/rolling_corr.py`。

一句话先说：**这份 repo 真正值钱的不是“实时看板”，而是它把 short-cycle pairs 最核心的 raw alpha 明确拆成了——动态对冲比率先把 BTC/ETH 两腿对齐，再做 spread 的 z-score 回归。**

## 2. 核心结论
- **base alpha 很清楚**：不是做方向预测，而是做 **相对价值回归**——当 `BTC - β_t * ETH` 的动态 spread 偏离过大，就赌它回到中线。
- repo 的关键不是固定 OLS，而是把 **Huber / TheilSen / Kalman 风格动态 hedge ratio** 放进主流程；这更适合 crypto 短周期里相关性和 beta 会漂移的现实。
- 它已经把短周期最常见的辅助件补齐了：**tick → `1s/1m/5m` resample、rolling correlation、ADF、spread、z-score、entry/exit backtest skeleton**。也就是说，这不是“pairs 概念笔记”，而是可直接迁到我们 desk 的实验骨架。
- 我做的本地 portability probe（Binance Spot 公共 `BTCUSDT/ETHUSDT`）显示：**dynamic beta 明显比 static beta 更能压缩 spread 噪声**。最近样本里：
  - `1m`：spread std 约从 `29.42 bps` 压到 `3.58 bps`
  - `5m`：约从 `94.38 bps` 压到 `8.21 bps`
- 用一个很粗的 `z_entry=2 / z_exit=0` 最小回测壳快检：
  - `1m`：约 `172` 笔，毛 `+9.65 bps/trade`，按双腿 `8 bps` 粗成本后仍约 `+1.65 bps/trade`
  - `5m`：约 `198` 笔，毛 `+21.72 bps/trade`，按双腿 `8 bps` 后约 `+13.72 bps/trade`
- 但别误会：**这还不是 production verdict**。这个 probe 仍然偏乐观，因为我用的是同步 bar close spread、零冲击、无 funding、无 next-bar execution lag 的简化口径；它现在更像“raw alpha 没死”，不是“可以直接上钱”。

## 3. 为什么和当前项目有关
它和我们当前主线的关系非常直接：这不是又一个 breakout / pullback filter，而是**可独立复现的完整 pairs raw alpha 候选**。而且它正好补的是 desk 现在最该继续积累的那块：
- raw alpha 家族里的 **pairs / stat-arb / relative value**
- 可快速压缩到 `1m / 3m / 5m / 15m` 的最小实验
- 还能顺手服务后续的 shared gate（corr、ADF、liquidity、execution veto）

一句话核心结论：**对 BTC/ETH 这种高相关腿，先做动态 beta 对齐，再做 spread fade，比直接拿固定 ratio/z-score 更像能活下来的短周期 pairs 原型。**

一句话证明方式：**repo 给了完整工程骨架，我再用 Binance 公开 `1m/5m` 数据做了最小移植快检，先看 spread 压缩，再看成本前后每笔期望。**

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / pairs / market-neutral
- 基础 alpha：`dynamic hedge-ratio spread mean reversion`
- regime：高相关、spread 仍近似可回归的阶段
- filter / veto：rolling corr、ADF、liquidity、极端 news / gap veto
- risk / sizing / execution overlay：beta-neutral notional sizing、z-score capped sizing、max holding bars、cost hurdle、next-bar / maker-first 执行

## 4. 可复刻的最小实验
**研究假设**：对 `BTC/ETH`，动态 hedge ratio 比 static beta 更能产出可交易的短周期 spread fade。

**一个可计算定义**：
1. 用 `1m` 或 `5m` close 计算 `log(BTC)`、`log(ETH)`；
2. 用递归/Kalman 风格方法估 `β_t`；
3. 定义 `spread_t = log(BTC_t) - β_t * log(ETH_t)`；
4. `z_t` 超过 `±2` 开仓，回到 `0` 平仓，附加 `max_hold`；
5. 统一按双腿 round-trip `6~12 bps` 做 friction ladder。

**最小回测切口**：
- 资产：`BTCUSDT / ETHUSDT`
- 周期：先 `5m`，再降到 `1m/3m`
- 样本：最近 `30~90d` 连续 Binance Spot 或 perp

**最该先看**：
- `post-cost expectancy / trade`
- `trade count` 与 `median hold`

## 5. 风险与保留意见
- 当前快检对 fill 太友好，必须换成 **next-bar open / bid-ask side execution** 再看。
- `1m` 上看起来能活，不代表加上 queue / latency 后还活。
- BTC/ETH 是最容易的一对，后续不能只盯这一对；要扩到 `BTC-ETH` 之外的 majors peer set。
- dynamic beta 若更新太快，可能把可交易偏离“吸掉”；若太慢，又会退化成滞后的 static ratio，需要参数稳定性检查。
- 真正的 production 版本必须补：**notional neutrality、hard stop、pair admission、rolling correlation floor、ADF survival、成本分层**。

## 6. 来源
1. **KulkarniPushakar. (2025). _Real-Time Crypto Pair Trading Analytics Platform_. GitHub repository.**
   - Readable URL：`https://github.com/KulkarniPushakar/Real-Time-Crypto-Pair-Trading-Analytics-`
   - Repo URL：`https://github.com/KulkarniPushakar/Real-Time-Crypto-Pair-Trading-Analytics-`
2. **Source audit files**
   - `README.md`
   - `analytics/hedge_ratio.py`
   - `analytics/spread.py`
   - `analytics/zscore.py`
   - `analytics/backtest.py`
   - `analytics/runner.py`
   - `analytics/resample.py`
   - `analytics/ADF_test.py`
   - `analytics/rolling_corr.py`
3. **Binance Spot public market data**
   - Klines API：`https://api.binance.com/api/v3/klines`

## 7. 下一步怎么测
先别扩 universe，先做一个最干净的 A/B：
1. `static beta` vs `dynamic beta`
2. `close-to-close` vs `next-bar-open`
3. 成本从 `4 / 8 / 12 bps` 三档往上压
4. 再加一层最便宜的 pair admission：`rolling corr floor + ADF veto`

如果这四步后 `5m` 还能保住正的 post-cost expectancy，这条就有资格进更正式的 pairs replication 池。