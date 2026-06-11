# 别把这份 2026 stat-arb repo 只读成“又一个配对模板”：对 short-cycle crypto desk，更该先保留的是「walk-forward cointegrated basket spread fade × regime veto × risk-parity sizing」这条完整 raw alpha 壳
- 时间：2026-04-23 02:48 UTC
- 类型：GitHub / 最小 portability probe
- 主题类型：raw alpha
- 基础 alpha：cointegrated basket spread 的均值回复（spread z-score / OU alpha fade）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：pairs / stat-arb / relative-value / mean-reversion / walk-forward / regime / risk-parity / cost
- 证据类型：工程经验 + public-data portability probe

## 1. 这次看了什么
看的是 2026 GitHub 仓库 `sujith-kamme/statistical-arbitrage-crypto`。它不是只做“找一对 cointegration 然后 z-score 开平仓”，而是把 **Johansen basket 发现、OU alpha、两层 regime filter、bucket/hysteresis 仓位、inverse-vol risk parity、walk-forward 训练/测试切分** 串成了一条完整研究流水线。

## 2. 核心结论
- 这份 repo 的 **base alpha 很清楚**：不是趋势，不是过滤器，而是 **相对价值 spread 偏离后的均值回复**。
- 它最值钱的地方不是“Sharpe 1.76”这串结果本身，而是：**把 pairs/stat-arb 从单对拍脑袋，升级成可滚动重估、可做 admission check 的完整策略壳**。
- repo 自报在 `23` 币日频池里筛到 `18` 币、做 `2~4` 资产 basket、`365d train + 60d test` walk-forward、最终 held-out `~220d` 上 **gross Sharpe 1.95 / net Sharpe 1.76 / 累计 +5.61% / MDD -1.38% / 仅 9 笔 round-trip**；样本不大，但链条完整。
- 我用 Binance USDⓈ-M 公共数据做了一个更贴 desk 的 **最近窗口 portability probe**（8 个 liquid majors，`15m/5m`，rolling pair version）：`15m` 的 `BNB/DOGE` 在 14 笔下约 **+46.37 bps/笔 net**、累计 **+6.49%**；`5m` 的 `ADA/LINK` 在 11 笔下约 **+11.72 bps/笔 net**、累计 **+1.29%**。说明这条 raw alpha 在短周期上 **不是天然死路**。

## 3. 为什么和当前项目有关
这正好补的是当前 desk 很需要的一块：**可直接落地的 stat-arb 完整策略壳**。相比之前很多“pair spread fade”只给 entry/exit，这个仓库多给了 4 个更能复用的组件：
- walk-forward 选篮子，不把 pair 关系当永久不变；
- hard veto（vol spike / ADF breakdown）把“关系失效时先别上”写清楚；
- bucket / hysteresis sizing，避免 z-score 刚碰阈值就满仓来回抖；
- inverse-vol risk parity，把多篮子并行部署时的仓位问题一起解决。

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / stat-arb / 均值回复
- 基础 alpha：cointegrated basket spread 偏离后向均值回归
- regime：spread 仍平稳、half-life 仍在可交易范围、波动未失控
- filter / veto：ADF 失效、短窗波动率相对长窗暴涨、alpha 低于噪声地板时不开仓
- risk / sizing / execution overlay：bucketed sticky sizing / hysteresis / inverse-vol risk parity / 仅在仓位变化时计交易成本

## 4. 可复刻的最小实验
**研究假设**：在 crypto `15m/5m` 上，稳定 cointegrated pair/basket 的 spread 偏离仍会回归，但只应在“关系没坏掉”的 regime 内做。

**最小定义**：
1. 先在 `BTC/ETH/SOL/BNB/XRP/ADA/DOGE/LINK` 上滚动筛 `coint p < 0.1` 且 `ADF p < 0.1` 的 pair；
2. 用 rolling OLS / Johansen weights 构 spread；
3. `z > 2` 做空 spread，`z < -2` 做多 spread，`|z| < 0.5` 或过零平仓；
4. 加一个 hard veto：`short-vol / long-vol > 4` 时禁止新开仓；
5. 先粗扣 round-trip `8 bps`。

**最小回测切口**：
- 资产：先从上面 8 个 liquid majors 开始；
- 周期：`15m` 为主、`5m` 做加速版；
- 样本：最近 `2000~3000` bars 滚动；
- 最先看：**net bps/笔**、**trade count**，再看 cumulative return / Sharpe。

## 5. 风险与保留意见
- repo 的亮眼数字主要来自 **日频 + 很少交易次数**，不能直接拿来外推到高频 desk。
- 我这次 probe 还是 **pair 简化版**，还没把 repo 的 2~4 资产 basket、full walk-forward re-selection、risk-parity portfolio 全量搬过来。
- `DOGE` 在多个 pair 中都显得更活跃，可能既代表更厚的 alpha，也代表更高的执行/滑点风险；上实盘前必须补 maker/taker 分层和容量检查。
- 如果 cointegration 关系在 crypto 里切换太快，真正关键的不是 entry 阈值，而是 **admission / re-selection / veto** 是否足够及时。

## 6. 来源
- Sujith Kamme. (2026). *statistical-arbitrage-crypto*. GitHub.
- Repo URL: `https://github.com/sujith-kamme/statistical-arbitrage-crypto`
- README: `https://raw.githubusercontent.com/sujith-kamme/statistical-arbitrage-crypto/main/readme.md`
- Notebook: `https://raw.githubusercontent.com/sujith-kamme/statistical-arbitrage-crypto/main/labs/research.ipynb`
- 本地 portability probe：`reports/artifacts/literature/walkforward_pairs_portability_probe_2026-04-23.csv`

## 7. 下一步怎么测
下一步不要继续围绕单个 pair 手调阈值，应该直接做一个 **desk 版最小 basket engine**：
1. 把 pair 扩成 `2~3` 资产 basket；
2. 每 `30d` / `45d` 重估一次 cointegration 权重；
3. 把 `ADF breakdown + vol spike` 做成统一 veto；
4. 在 `15m` 上先比较 **固定 1 对 vs top-3 diversified baskets** 的 net trade expectancy；
5. 若 trade count 仍偏少，再下沉到 `5m/3m`，但必须同步加 maker-first / max-hold / turnover 约束。