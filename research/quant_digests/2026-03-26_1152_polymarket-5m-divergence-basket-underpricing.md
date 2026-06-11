# 别把 Polymarket 5m crypto UP/DOWN 仓库只读成“自动下注机器人”：更该先测的是「硬到期二元分歧 basket underpricing」完整 raw alpha

- 时间：2026-03-26 11:52 UTC
- 类型：2026 GitHub 新仓库 + Polymarket 公共 CLOB / Gamma API
- 主题类型：raw alpha
- 基础 alpha：当 `BTC_UP + ETH_DOWN` 或 `BTC_DOWN + ETH_UP` 这类 **5 分钟双腿 basket 的合成买入价**落入经验低价带（repo 默认 `0.70~0.82`）时，买入两腿并持有到当轮 `5m` 结算，赚 **hard-expiry payout** 与 entry cost 的差额，而不是赌单腿方向
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/relative-value/pairs/binary-basket/hard-expiry/polymarket/btc/eth/xrp/5m/1m/3m/repo/external-data
- 证据类型：2026 GitHub 仓库代码级审阅 + 公共 API 可得性

先把 **base alpha** 说清楚：**这不是“看 BTC/ETH 会不会分歧”的嘴炮故事，也不是情绪面板。它更像一条有固定到期时间的两腿相对价值策略：只在 basket 合成成本足够便宜时买入，等 5 分钟结算兑现。**

## 1. 这次看了什么
主线材料是 GitHub 仓库：

- **andrew-cao-zc (2026), _Polymarket Pair Trading Bot_**
- Readable URL：`https://github.com/andrew-cao-zc/polymarket-pair-trading`
- Repo URL：`https://github.com/andrew-cao-zc/polymarket-pair-trading`

我重点看了 `README.md`、`strategy.py`、`config.py`、`risk_manager.py`、`data_fetcher.py`。

仓库最值钱的地方，不是 README 里那句“crypto 高相关，所以分歧会回归”，而是它已经把**完整交易骨架**写出来了：
- 市场周期固定 `300s`
- 组合触发价带：`0.70 <= combo_price <= 0.82`
- 每方向最多 `2` 笔、每周期总共最多 `4` 笔
- 最后 `30s` 禁止新开仓
- 默认手续费 `0.7%`
- 默认日亏损上限 `$50`

## 2. 核心结论
- **一句话核心结论**：这份仓库真正可 intake 的，不是“预测谁涨谁跌”，而是“买便宜的 5 分钟双腿二元 basket，靠硬到期结算兑现错价”。
- **一句话证明方式**：证据主要来自 repo 代码本身——entry、exit、trade cap、closing-window、daily-loss 都已经明确写成规则，不是只停留在概念图。
- 对 desk 最可复用的点，是它把 **hard-expiry、固定持有期、双腿合成成本、最后 30 秒 veto、每周期 trade cap** 这套框架一次性给齐了。
- 但仓库里也有一个很重要的**诚实风险信号**：`strategy.py` 真正使用的是 `0.70~0.82` 的组合阈值，而 `config.py` 里还留着 `PRICE_RANGE_MIN=0.38 / PRICE_RANGE_MAX=0.44 / COST_THRESHOLD=0.45` 这套并未被主策略调用的旧参数，说明实现存在**参数漂移 / 配置未收口**问题，live PnL 不能直接照单全收。

## 3. 为什么和当前项目有关
这条线和我们现在的 desk 有 3 个直接关系：

1. 它是**独立 raw alpha**，不是 filter 假装成 alpha；
2. 它属于我们正在补的 **relative value / pairs** 家族，但不是传统 perp spread，而是 **binary basket + hard expiry** 的新变体；
3. 即使未来不做 Polymarket，本仓库里“固定结算时钟 + 双腿合成成本 + late-entry veto + 每周期限频”这套治理，也能迁移到 `BTC-ETH`、`leader-laggard`、`event-driven spread` 的 `1m/3m/5m` 设计里。

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / pairs / 事件驱动
- 基础 alpha：低价双腿二元 basket underpricing
- regime：5 分钟到期、流动性足够、盘口可同时成交的 crypto event 市场
- filter / veto：`combo_price` 落入低价带；最后 `30s` 不开新仓；可加 active-hours 过滤
- risk / sizing / execution overlay：固定 `BET_SIZE=$5`、每方向 `max 2`、每周期 `max 4`、`MAX_DAILY_LOSS=$50`、必须防单腿成交不对称

## 4. 可复刻的最小实验
**研究假设**：当 `BTC_UP + ETH_DOWN` 或 `BTC_DOWN + ETH_UP` 的合成价格足够便宜时，5 分钟到期后的实际 payout 之和，平均上高于 entry cost + fee。

**数据源 / 公开性 / 更新频率**：
- `https://gamma-api.polymarket.com`
- `https://clob.polymarket.com`
- 都是公开端点；repo 已给出抓取路径；盘口更新接近实时，结算周期固定 `5m`

**最小口径**：
- 标的：先只做 `BTC/ETH`，后扩到 `BTC/XRP`
- 频率：`1s~5s` 级抓盘口，按 `5m` 周期结算
- 入场：每轮开盘后 `30~60s` 开始观察；若 `combo_price ∈ [0.70, 0.82]` 则买入；最后 `30s` 禁开
- 出场：只持有到当轮结算
- 先看 3 个指标：**费后单笔 EV、0/1/2 payout 分布、双腿同时成交率**

如果这 3 个数里，**双腿同时成交率**先垮掉，说明问题不在 alpha 想法，而在 execution feasibility。

## 5. 风险与保留意见
- README 把 edge 解释成“分歧概率 + 均值回归”，这个说法**偏粗糙**；真正该算的是两腿 token 的合成定价与实际结算值，而不只是看分歧频率。
- 单腿先成交、另一腿滑点或没成交，会把本来 market-neutral 的想法直接扭成方向暴露。
- 参数漂移（README / `strategy.py` / `config.py` 不完全一致）说明仓库更像可研究 skeleton，不应直接相信截图收益。
- 这条线最适合先做 **paper trading / replay**，不适合一上来当 production alpha。

## 6. 来源
- **andrew-cao-zc. (2026). _Polymarket Pair Trading Bot_. GitHub repository.**
  - Readable URL: `https://github.com/andrew-cao-zc/polymarket-pair-trading`
  - Repo URL: `https://github.com/andrew-cao-zc/polymarket-pair-trading`
- **Polymarket public endpoints（由 repo `config.py` / `data_fetcher.py` 调用）**
  - Gamma API: `https://gamma-api.polymarket.com`
  - CLOB API: `https://clob.polymarket.com`

## 7. 下一步怎么测
先别急着相信 repo 的盈利截图。**第一步就做 30 天 `BTC/ETH` 回放**：逐轮记录 `combo_price`、结算 payout、双腿是否都能成交、费后 EV；如果 `0/1/2 payout` 分布看起来还行，但双腿同时成交率太差，就立刻把这个主题从“可交易 alpha”降级成“execution-sensitive 候选”。
