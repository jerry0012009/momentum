# 别把这份 2021 intraday momentum repo 只读成“相对强弱选币脚本”：对 short-cycle crypto desk，更该先回答的是「hourly winner-rotation × 4-asset cohort selection」这条 raw alpha 到底是轮动素材还是手续费陷阱

- 时间：2026-04-23 12:15 UTC
- 类型：2021 GitHub repo source audit（`Crypto_MOMO.R` + repo metadata）+ Binance USDⓈ-M public-data portability probe（8 liquid majors，`15m/5m`）
- 主题类型：raw alpha
- 基础 alpha：**在一个小币种 cohort 里，刚刚走出最强过去收益的那一只，下一小时仍更可能继续跑赢同 cohort 其他币；交易上做“每小时只拿 cohort 内过去 60-bar 动量最强者”的 winner-rotation。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-sectional/relative-strength/momentum/winner-rotation/cohort-selection/hourly-rebalance/15m/5m/repo/public-data/cost/risk
- 证据类型：repo code + public-data portability probe

## 1. 这次看了什么
主线材料：
- **Author / Repo Owner：** `jgQuantScripts`
- **Year：** 2021
- **Title：** `Crypto-Momentum-Backtesting`
- **Venue：** GitHub repository
- **DOI：** N/A
- **Readable URL：** <https://github.com/jgQuantScripts/Crypto-Momentum-Backtesting>
- **Repo URL：** <https://github.com/jgQuantScripts/Crypto-Momentum-Backtesting>
- **Raw code URL：** <https://raw.githubusercontent.com/jgQuantScripts/Crypto-Momentum-Backtesting/main/Crypto_MOMO.R>

repo 元数据补充：
- 描述：`Momentum using intraday data`
- 创建时间：`2021-06-12`
- 语言：`R`
- 仓库内容非常薄：主逻辑基本都在一个 `Crypto_MOMO.R` 文件里，外加一个 `CRYPTO_CLOSES_15min.rds` 数据文件。

先把 base alpha 说清楚：
> **这不是“单币 time-series momentum”那种只看自己涨跌延续的故事，而是一个更具体的 cross-sectional raw alpha：每小时在一个小 cohort 里选过去 60 根 bar 最强的那只，赌它下一小时继续当 winner。**

翻成人话：
- 不是“全市场一起做多动量”；
- 而是“在 4 个币里，每小时只拿那个刚刚最强的币”；
- 它更像一个 **relative-strength rotation**，而不是经典 breakout 系统。

---

## 2. repo 到底在做什么
`Crypto_MOMO.R` 的核心逻辑很直接：
1. 读入 `15m` close 数据；
2. 计算每个币过去 `60` 根 bar 的离散收益（也就是过去 `15h` 的动量）；
3. 每隔 `1h` 重平衡一次；
4. 在一个 4 币组合里，选过去 `60-bar` 动量最高的那只；
5. 持有下一小时；
6. 穷举所有 4 币组合，事后挑出表现最好的组合。

这套东西的优点是：
- **很好复现**；
- **信号语义很干净**；
- 可以自然迁到我们 desk 的 `15m`，也能往 `5m` 做快一档版本。

但它也有两个明显问题：
- repo 里是 **事后挑最优 4 币组合**，很容易带进 selection bias；
- 没看到明确的交易成本、滑点、换手惩罚，实盘可行性要自己补。

---

## 3. 一句话结论 + 为什么值得进研究池
- **一句话结论：** 这条线作为 raw alpha 候选是成立的，因为 base alpha 很清楚、实现也极薄；但按我这轮在 Binance majors 上做的 portability probe，它现在更像“可复现轮动素材”，还不是“过费后可直接上线”的现成策略。
- **为什么仍值得进池：** 因为它给的是一个非常清楚的 research primitive——**cohort 内 winner-rotation**。这个 primitive 后面可以继续接：leader strength threshold、dispersion gate、carry veto、execution throttle、top-2 spread filter。

---

## 4. 本轮最小 portability probe（忠于 repo 语义）
### 4.1 数据与口径
我用了项目里现成缓存做一版“尽量忠于原 repo”的快检：

- `15m` 数据：`BTC/ETH/BNB/SOL/XRP/ADA/DOGE/LINK`
- `5m` 数据：`BNB/ETH/SOL/XRP/ADA/DOGE/LINK/AVAX`
- 数据源：Binance USDⓈ-M public kline cache
- 组合数：每个频率都穷举 `8 选 4 = 70` 个 cohort

信号定义：
- lookback：过去 `60` 根 bar 收益
- rebalance：每 `1h`
- 选币：cohort 内 past-return 最大者
- 持有：下一小时
- 成本假设：先看 gross，再粗看 `8 bps round-trip` net

对应到不同周期：
- `15m`：`60` 根 = `15h` lookback，持有 `4` 根 = `1h`
- `5m`：`60` 根 = `5h` lookback，持有 `12` 根 = `1h`

产物：
- `reports/artifacts/literature/intraday_rotation_repo_probe_15m_2026-04-23.csv`
- `reports/artifacts/literature/intraday_rotation_repo_probe_5m_2026-04-23.csv`
- `reports/artifacts/literature/intraday_rotation_repo_probe_summary_2026-04-23.json`

### 4.2 关键结果（先给 4 个数）
#### `15m` 原版口径
1. **最佳 4 币组合（gross）**：`ETH/SOL/XRP/BNBUSDT` 近似对应的 cohort，`mean gross = +3.05 bps/trade`。  
2. **这个最佳组合胜率**：`51.38%`，说明不是完全没边，但 edge 很薄。  
3. **同组合在 `8 bps` round-trip 下**：`mean net = -4.95 bps/trade`。  
4. **70 个 4 币组合里，`positive net` 比例 = `0%`**，中位数组合 `mean net = -7.08 bps/trade`。

#### `5m` 快一档口径
1. **最佳 4 币组合（gross）**：`BNB/ETH/SOL/LINK`，但 `mean gross = -0.25 bps/trade`。  
2. **也就是说连毛边都没看见**，更别说过费。  
3. **70 个组合全部 net 为负**。  
4. **中位数组合 `mean net = -10.68 bps/trade`**，明显比 `15m` 更差。

翻成人话：
- 这条 winner-rotation 在 `15m` majors 上 **有一点点 gross continuation 味道**；
- 但厚度不够，直接拿来每小时硬轮动，手续费基本吃光；
- 往 `5m` 压之后，边更薄，当前看更像纯 fee trap。

---

## 5. 这条 raw alpha 对当前 desk 的真实意义
### 5.1 它不是“现成策略”，但也不是废料
这条线最大的价值不是“repo 已经给了答案”，而是：
- 它把一个很清晰的 alpha primitive 抽出来了：**小 basket 内的相对强弱延续**；
- 这和我们现在已经积累的很多单币 trend / MR / pair fade 素材不一样；
- 它更像一个 **cross-sectional router**，可以作为：
  - 单币趋势信号的上层选币器；
  - trend shell 的 universe selector；
  - 或者反过来，作为“什么时候不要追 leader”的反例基线。

### 5.2 它服务的是哪类 raw alpha
它服务的是：
- `cross-sectional momentum`
- `relative-strength rotation`
- `leader-laggard allocation`

而不是：
- pairs / stat-arb 的价差回归；
- 也不是 funding / basis carry。

所以它适合放进 **raw alpha 素材池**，但当前证据更像“等待改造的底胚”。

---

## 6. 为什么 repo 原版容易失真
repo 原版最需要小心的地方有 4 个：

1. **事后挑组合**  
   先穷举所有 4 币组合，再挑历史表现最好的组合，这很像把“选币 alpha”和“择样本 alpha”混在一起了。

2. **只有 long one winner，没有 cash / no-trade 状态**  
   每小时都必须选一只，这会把很多“没 edge 的小时”也硬做掉。

3. **没做 leader-vs-runner-up 强度约束**  
   如果第一名只比第二名强一点点，这种相对强弱排序很可能只是噪声。

4. **成本没被正视**  
   这种 hourly rotation 的换手天然高，若没有 maker 优先、top-2 spread threshold、冷却期，极易被成本吃死。

---

## 7. 如果要把它改造成 desk 可用版本，优先改哪几刀
### 7.1 不要再“每小时硬选一个”
先加一个 **leader strength gate**：
- `mom_rank1 - mom_rank2 >= threshold`
- 或 `rank1 zscore >= threshold`

只有 leader 明显领先时才轮动。

### 7.2 不要让 cohort 固定后验最优
改成两层：
- 上层：按近 `N` 天流动性 / 成交额 / funding 稳定性先选可交易 cohort；
- 下层：再在 cohort 内做 relative-strength rotation。

### 7.3 让 `15m` 做父信号，`5m` 做子执行
当前 probe 已经暗示：
- `15m` 上还有一点 gross edge；
- `5m` 直接当父信号太薄。

更合理的 desk 化方式是：
- `15m` 决定谁是 leader；
- `5m` 只负责找 pullback / spread / taker-flow 比较好的入场点。

### 7.4 加 dispersion / trend-quality gate
只在以下条件开闸：
- cohort 内横截面离散度够大；
- leader 自己的 path smoothness / ADX / volume expansion 达标；
- funding 没有严重反向挤压。

也就是说，它更适合和现有 trend primitive 拼成一个组合，而不是单独裸跑。

---

## 8. 可直接落地的完整策略壳（改造版，不是 repo 裸版）
## 8.1 Entry（入场）
每小时检查一次 liquid cohort：
1. 计算过去 `60-bar` return；
2. 找 rank1 / rank2；
3. 若 `rank1-rank2` 差值超过阈值，且 leader 自身 trend-quality 达标，则只做多 rank1；
4. 若达不到阈值，则空仓。

### 8.2 Exit（出场）
- 固定 `1h` time stop；
- 或 leader 跌出 cohort 第一名就提前离场；
- 或 `5m` 子执行层出现 momentum failure / volume fade 就先撤。

### 8.3 Sizing（仓位）
- `size ~ edge_score / realized_vol`
- 用 inverse-vol 控波动，不要固定仓位
- 单币上限 + 组合上限同时设

### 8.4 Risk（风控）
- funding / basis 明显逆风时降杠杆
- cohort 内高度相关时，避免叠加已有同方向仓位
- 单小时内连续换手过多时启用 cooldown

### 8.5 Cost（成本）
至少要分三档看：
- `4 bps`
- `8 bps`
- `12 bps`

若只有 `4 bps` 才勉强为正，这条线就只能留在“maker-first / selective-entry”层，不应裸做。

---

## 9. 下一步怎么测（必做）
1. **先做 no-trade 版本**：只在 `rank1-rank2` 差值进入前 `20%` 强档时开仓，看 `trade count` 会掉多少、`net bps/trade` 能否抬上来。  
2. **做 cohort ex-ante 化**：不要历史最优 4 币组合，改成“最近 7d 成交额前 N + funding 正常 + 最小价位步长合适”的真实可交易 cohort。  
3. **做 `15m parent / 5m child` 双层实验**：父层决定 leader，子层只在 `5m` pullback 或 micro breakout 再入。  
4. **和简单基线对照**：对比“固定 BTC/ETH/SOL/BNB cohort”与“动态最优 cohort”，看 selection bias 占了多少。  
5. **加入 shared gates**：把 `dispersion`、`funding veto`、`volume expansion`、`trend smoothness` 分别做 A/B，看哪个能真正把 gross 边抬成 net 边。  
6. **检查 top-2 spread 的解释力**：如果 leader 和 runner-up 差距不大时全为噪声，那这个策略本质就不是 rotation，而是“只做 leader 明显领先的稀疏 continuation”。

---

## 10. 结论（给当前 desk 的一句人话）
这份 repo 值得保留，不是因为它已经证明“hourly 追强”能赚钱，而是因为它把一个很干净的 raw alpha primitive 摆在桌上：

> **cohort 内 winner-rotation 可能确实有一点点 continuation，但裸跑厚度太薄；如果不加 no-trade、leader-strength、cost-aware execution，它更像手续费陷阱。**

所以当前最合理的定位不是“直接上线策略”，而是：
- **保留为 raw alpha 素材池的一条 cross-sectional momentum 底胚**；
- 然后优先做 `15m parent + 5m child + strength gate` 的 desk 化改造。

---

## 11. 来源
1. **jgQuantScripts (2021). _Crypto-Momentum-Backtesting_. GitHub repository.**
   - Readable URL: <https://github.com/jgQuantScripts/Crypto-Momentum-Backtesting>
   - Repo URL: <https://github.com/jgQuantScripts/Crypto-Momentum-Backtesting>
   - Raw code URL: <https://raw.githubusercontent.com/jgQuantScripts/Crypto-Momentum-Backtesting/main/Crypto_MOMO.R>
   - Repo metadata API: <https://api.github.com/repos/jgQuantScripts/Crypto-Momentum-Backtesting>
2. **本地 portability probe 产物**
   - `reports/artifacts/literature/intraday_rotation_repo_probe_15m_2026-04-23.csv`
   - `reports/artifacts/literature/intraday_rotation_repo_probe_5m_2026-04-23.csv`
   - `reports/artifacts/literature/intraday_rotation_repo_probe_summary_2026-04-23.json`
