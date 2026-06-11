# Classical carry + dynamic leverage shell：把 funding carry 从“APR 看板”推进到可下场的完整策略壳
- 时间：2026-04-24 01:40 UTC
- 类型：GitHub
- 主题类型：raw alpha
- 基础 alpha：positive funding carry（long spot / short perp 的 delta-neutral 收租）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / carry / funding / basis / delta-neutral / leverage / staking-extension / Binance / CoinGlass / 8h / 15m / 5m
- 证据类型：工程经验 + repo 回测结论

## 1. 这次看了什么
看了一个 2025 EPFL 项目仓 `matthias-wyss/crypto-carry-trade-strategies`。它不是只做 funding 可视化，而是把 **classical carry、staking-enhanced carry、Pendle PT-stETH carry、drawdown / leverage 分析、跨市场阶段对照** 放在同一套研究里。

## 2. base alpha 先说清楚
这篇东西的 **base alpha 很清楚**：

**当 perp 资金费率长期为正时，做 `long spot + short perp` 的 delta-neutral carry，主要收益来自 funding；若在 ETH 上再叠 staking APR，则是同一 raw alpha 的收益增强版。**

所以它首先是 **raw alpha**，不是 filter，也不是纯 overlay。

## 3. 核心结论
- 这份仓最值得 desk 拿走的，不是 Pendle 叙事，而是最朴素那层：**BTC / ETH 正 funding carry 本身就是可独立站住的完整策略壳**。
- README 给的关键结论很直接：**BTC 和 ETH funding 在样本里超过 85% 时间为正**，说明它不是只在个别时点才出现的偶发 pocket。
- 他们还给了一个很实用的旁支：**ETH staking-enhanced carry 平均比纯 funding carry 多约 3.9% 收益增强**。这对我们不是主线，但说明 raw alpha 上面确实能叠第二收益腿。
- 更重要的是，作者明确指出：**dynamic leverage adjustment 能在保留竞争力收益的同时降低回撤**。对 desk 来说，这比单纯再找一个更花的 carry 变体更有价值，因为它直接补齐了 entry / sizing / risk 这一整层。

## 4. 为什么和当前 desk 直接相关
当前 bot7 优先补的是 **可独立复现、可直接落地的 raw alpha**。这份材料符合得比表面上更好：

- raw alpha 清楚：正 funding carry
- entry 清楚：只在 funding 为正且足够厚时开 `long spot / short perp`
- exit 清楚：funding pocket 消失、basis 反向、风险约束触发时平仓
- sizing 清楚：可做固定杠杆，也可做动态 leverage 调整
- risk 清楚： liquidation risk、funding volatility、basis 偏移
- cost 清楚：手续费、借币/保证金占用、调仓摩擦

它虽然不是逐根 5m 信号，但仍然是 **可直接进入实盘素材池的 raw alpha**；`5m / 15m` 在这里承担的是 **child execution / hedge timing / add-reduce cadence**，不是把低频 carry 硬装成高频主信号。

## 5. 对我们真正有价值的可迁移部分
### 5.1 先只拿 classical carry，不急着碰 staking / Pendle
对当前 desk，最干净的第一步不是复刻整套 DeFi 扩展，而是先保留：
- 标的：BTC / ETH，必要时扩到 liquid majors
- 方向：`long spot + short perp`
- admission：仅当 annualized funding 明显为正，且连续性足够好时入场
- veto：basis / premium 过大、盘口太薄、借贷/保证金成本不划算时不开

### 5.2 dynamic leverage adjustment 比“更高 APR”更值得先测
这份 repo 最容易被忽略、但更适合现在 desk 的旁支，是：
- 不把 carry 看成“有正 funding 就满杠杆收租”
- 而是把杠杆当作 **风险预算旋钮**：当 funding pocket 变薄、basis 扩大、波动抬升时降杠杆
- 这比继续找第 N 个 carry 变体更像真实可部署组件

换句话说：**base alpha 还是 funding carry，但更值得今天就拆出来做最小实验的，是 carry × dynamic leverage 这条完整策略壳。**

## 6. 可复刻的最小实验
### 最小实验 A：classical carry 主壳
- 假设：**Binance BTC/ETH 的正 funding pocket 在扣掉手续费后仍能留下正 carry。**
- 数据：
  - Binance USDⓈ-M `fundingRate`
  - Binance spot / perp klines
  - 可选加 `premiumIndex` 做 basis 过滤
- 频率映射：
  - 主信号：8h funding
  - 执行与风控：`15m` 为默认，必要时细到 `5m`
- 最小规则：
  1. `annualized_funding > th1` 且最近 `N` 个 funding 点为正
  2. 开 `long spot + short perp`
  3. 若 `annualized_funding < th2`、basis 反向扩张或达到时间止盈/止损则退出

### 最小实验 B：dynamic leverage overlay
- 目标：验证 **动态杠杆是否真能降回撤而不明显毁掉净收益**
- 做两个版本：
  - `v1`: 固定 1x notional hedge
  - `v2`: leverage 随 `funding_strength / basis_vol / realized_vol` 分档
- 先看三个指标：
  - 成本后年化 carry
  - 最大回撤
  - 单位保证金收益（return on margin）

## 7. 下一步怎么测
1. **先只做 BTC / ETH classical carry**，不要一上来混 staking / Pendle。
2. 用 Binance 公共 funding + kline，做 `2024-01-01 ~ now` 的 8h parent / 15m child-exec 回放。
3. 先比较三档 admission：
   - 只要 funding > 0
   - funding 年化 > `5%`
   - funding 年化 > `10%` 且过去 `3` 个 funding 点持续为正
4. 再比较两档 leverage：固定 notional vs 动态 leverage。
5. 若 BTC/ETH 过线，再扩到 `SOL / XRP / DOGE / ADA` 这类 funding 更活跃但波动更大的币，观察 **高 funding 是否只是高风险补偿**。

## 8. 风险与保留意见
- 这份仓的强项是策略壳完整，不是严格学术检验；因此证据强度更接近 **高质量工程研究**，不是正式论文。
- README 里提到的 `>85% 正 funding`、`staking +3.9%`、`动态杠杆降回撤` 都是很好的 intake 信号，但仍需要我们自己按 Binance 真实成本口径重算。
- staking / Pendle 分支更像 **收益增强或产品化扩展**；若当前目的是补 raw alpha 素材池，应先把 classical carry 这层单独跑通。
- 这类策略最大的假象是“APR 很稳”；真正会咬人的地方其实是 **basis 扩张、爆仓路径、交易对冲摩擦和保证金占用**。

## 9. 一句话总结
**这份 repo 最值钱的不是“还能拿 staking 利息”，而是它把最朴素的 funding carry 明确写成了一个可落地的完整策略壳，并提示我们下一步该优先测试 `carry × dynamic leverage`。**

## 10. 来源（尽量结构化）
- Source A（主来源，仓库）
  - Authors：Matthias Wyss, Loris Tran, Massimo Berardi, Vincent Ventura, Alexandre Huou
  - Year：2025
  - Title：Crypto Carry Trade Project
  - Venue：EPFL FIN-413 course project / GitHub repository
  - DOI：N/A
  - Readable URL：https://github.com/matthias-wyss/crypto-carry-trade-strategies
  - Repo URL：https://github.com/matthias-wyss/crypto-carry-trade-strategies
- Source B（仓库说明）
  - Key repo claims used：BTC/ETH funding positive over 85% of time；staking-enhanced carry average outperformance about 3.9%；dynamic leverage adjustment reduces drawdowns while maintaining competitive returns
  - Readable URL：https://raw.githubusercontent.com/matthias-wyss/crypto-carry-trade-strategies/main/README.md
- Source C（可独立复现实验的数据源）
  - Provider：Binance USDⓈ-M public API
  - Data：`fundingRate`, `premiumIndex`, spot/perp klines
  - Public availability：公开可得
  - Update frequency：funding 8h；价格可到 `1m`
  - Readable URL：https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Get-Funding-Rate-History
