# 别把这份 2025/2026 LOB repo 只读成 execution infra：对 short-cycle desk，更该先测的是「persistent L1 imbalance × signed-flow autocorr continuation」

- 时间：2026-04-07 06:40 UTC
- 类型：GitHub / microstructure analytics / execution toolkit
- 主题类型：raw alpha
- 基础 alpha：**当盘口一侧队列持续占优、且主动成交方向在短时间内连续同向时，mid-price 在接下来极短窗口里更容易继续朝占优一侧漂移。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha / microstructure / order-book / imbalance / signed-flow / continuation / btc / binanceus / 1m / 3m / 5m / repo / public-data / cost
- 证据类型：工程经验

## 1. 这次看了什么
这次看的是 **Mansoor Mamnoon (2025/2026)** 的 GitHub 仓库 **`limit-order-book`**。表面上它像一个“高性能 LOB 引擎 + VWAP/TWAP/POV 回放框架”，但对我们 desk 更值钱的其实是 repo 里那条更容易复现的 raw alpha 线：`python/olob/microstructure.py` 会直接产出 **impact curves、signed order-flow autocorrelation、以及 short-horizon drift vs. L1 imbalance deciles**。

也就是说，这份仓库不该只被读成 execution 基础设施；它其实把一个很朴素、但适合短周期 desk 的命题写得很清楚：**盘口失衡如果只是瞬时快照，价值有限；但若它和主动成交同方向持续出现，就更像可以被交易的 continuation alpha。**

## 2. 核心结论
- **一句话核心结论：** 这份 repo 最值得 intake 的不是 TWAP/VWAP 示例，而是 **“L1 队列失衡 × signed-flow persistence” 这条 microstructure raw alpha 候选**。
- **一句话证明方式：** 作者没有只给口头叙事，而是把 raw analytics 做成可重复脚本，直接在真实 BTCUSDT 样本上输出 **drift-vs-imbalance、impact、order-flow autocorr** 三类证据，再把成本/执行层接到同一代码库里。
- repo 自带 `microstructure_summary.json` 显示：**signed order-flow lag-1 autocorr ≈ `0.326`**，不是接近 0 的白噪声；这说明主动买卖方向在极短窗口里有明显簇集，适合和 queue imbalance 一起读，而不是孤立看单个 snapshot。
- 同一份 summary 把 **drift-vs-imbalance** 明确写成 **`horizon_ms = 500`、`grid_ms = 1000`** 的短窗分析；这很重要，因为它提醒我们：这条 alpha 的原生尺度不是 15m 指标，而是**先在秒级成立，再看能不能迁移成 1m/3m/5m 的聚合触发器**。
- README/仓库元数据还给了一个很实用的配套事实：引擎声称能处理 **`20.7M msgs/sec`**、延迟 **`p50=0.04µs` / `p99≈1µs`**。这不是 alpha 证据本身，但意味着它不是“讲故事用 repo”，而是一个能把 **alpha → impact → execution budget** 串起来的实验骨架。

## 3. 为什么和当前项目有关
这条线和当前 `momentum` 直接相关，因为它补的是我们 raw alpha 素材池里的 **microstructure continuation** 分支，而且不是只给“信号”，还顺手给了 **成本 / 冲击 / 执行约束**。

更重要的是，它对当前 desk 的启发不是“马上去卷亚毫秒做市”，而是更务实的改写：
1. 保留 **queue imbalance + signed flow persistence** 作为 raw alpha 本体；
2. 把 repo 的 **impact 曲线** 改读成 size cap / trade veto；
3. 把秒级信号聚合成 `1m / 3m / 5m` 可测的 bar-level admission，而不是硬装成 tick-by-tick production 系统。

## 3.5 策略拆解（必填）
- 方向属性：**单资产 / microstructure / continuation**
- 基础 alpha：**持续的 L1 bid/ask 失衡 + 同向主动成交簇集，会推着未来短窗 mid-price 继续朝该方向漂移**
- regime：**只在 spread 较窄、深度未塌、冲击成本不过高时启用；高波动清算段默认降级**
- filter / veto：**若 spread 扩大、impact 预算超阈值、或 imbalance 只是单点尖峰而非持续状态，则不做**
- risk / sizing / execution overlay：**按 impact budget 限制名义仓位；优先 next-bar open / maker-ish 进入；固定 time stop + sign-flip exit；若预估冲击 > 预期 edge 的 1/3，直接 veto**

## 4. 可复刻的最小实验
**研究假设：** 秒级的 `persistent imbalance × signed flow` continuation，能迁移成 BTC/ETH/SOL 上 `1m / 3m` 可测的短周期 directional alpha。

**一个可计算定义：**
```python
imb_t = bid_sz1_t / (bid_sz1_t + ask_sz1_t) - 0.5
flow_t = sum(sign_i * qty_i for trades in last_5s)
persist_t = mean(1[imb_{t-k}>q90] for k in 0..59)
score_t = persist_t * sign(flow_t) * 1[abs(flow_t)>q70]
```
把秒级 `score_t` 在 1 分钟内聚合；若该分钟里大部分切片都同向，则在下一根 `1m` 或 `3m` 开盘入场。

**最小回测切口：**
- 标的：Binance / Bybit BTC、ETH、SOL 永续
- 数据：公开 depth / aggTrades 或等价 L2 + trade feed
- 周期：先 `1m`，再测 `3m`，最后看 `5m` 是否还活
- 规则：
  - long：上一分钟 `persist_t` 高于历史 `q90`，且 `flow_t > q70`
  - short：对称反手
  - exit：持有 `1~3` 根、或 `score` 翻转、或 hit time stop
- 先看两项：
  1. **post-cost mean / hit rate**
  2. **trade count retention after spread+fee+impact veto**

## 5. 风险与保留意见
- **原生 alpha 尺度很短。** repo 主要证据在 `500ms~1000ms` 量级；能否平移到 `1m/3m/5m`，必须实测，不能脑补。
- **L1 很容易脏。** spoof、撤单、缺口深度、不同交易所的撮合细节，都会让“表面失衡”失真，所以 persistence 比单点 snapshot 更重要。
- **样本来自 BinanceUS，不等于 Binance global。** 可迁移，但不能默认强度一致。
- **execution 才是生死线。** 这条 alpha 若不能在 size/impact 上过关，很容易变成“方向对了，钱没赚到”。

> **最值得复用/复现的点：不是把 repo 当做市/执行 demo，而是直接复用它那套 `drift vs imbalance + oflow autocorr + impact` 三件套，把 microstructure raw alpha 和成本约束放进同一个 first verdict。**

## 6. 来源
1. **Mansoor Mamnoon. (2025/2026). _limit-order-book_. GitHub repository.**  
   - Repo URL：`https://github.com/mansoor-mamnoon/limit-order-book`
   - Readable URL：`https://github.com/mansoor-mamnoon/limit-order-book`
2. **`python/olob/microstructure.py`（repo 内原始分析脚本）**  
   - Readable URL：`https://github.com/mansoor-mamnoon/limit-order-book/blob/main/python/olob/microstructure.py`
3. **`analytics/microstructure_summary.json`（repo 内示例输出）**  
   - Readable URL：`https://github.com/mansoor-mamnoon/limit-order-book/blob/main/analytics/microstructure_summary.json`
4. **仓库 README / repo metadata（性能、回放与回测范围说明）**  
   - Readable URL：`https://github.com/mansoor-mamnoon/limit-order-book/blob/main/README.md`
