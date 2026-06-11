# 别把这份 Hyperliquid 回测仓只读成 hourly premium 图：对 short-cycle desk，更该先测的是「mark-vs-oracle dislocation percentile fade」这条 raw alpha

- 时间：2026-04-15 11:28 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `src/strategies/basis_reversion.py` + `src/data/hyperliquid.py` + `research/run_hip3_analysis.py` + `src/engine/backtest.py`）+ Hyperliquid public API portability read
- 主题类型：raw alpha
- 基础 alpha：**当 perp 的 `mark / premium` 相对 oracle 出现极端偏离时，做反向收敛：`premium > 0` 就 short，`premium < 0` 就 long；本质上赚的是短时流动性失衡后的 basis / premium 压缩，而不是赌长期方向。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/single-asset/relative-value/stat-arb/mean-reversion/mark-vs-oracle/premium-dislocation/hyperliquid/hip-3/1m/3m/5m/15m/repo/public-data/cost/risk
- 证据类型：工程证据（repo 文档 + 源码 + 回测框架 + 公共 API 可得性）

## 1. 这次看了什么
这轮主看的是 2026 GitHub repo `andreaambrosio/hype-backtesting` 里最值得 short-cycle desk intake 的那条 raw alpha，而不是继续把它读成“又一个 funding / regime / momentum 杂烩框架”。

先回答 base alpha：**这不是 funding carry，也不是 generic trend filter；它是一条可以单独站住的短时相对价值 / 单资产 stat-arb raw alpha——当 perp 的成交标记价明显偏离 oracle 时，赌这个偏离会向正常区间压缩。**

这轮主看的文件：
- `README.md`
- `src/strategies/basis_reversion.py`
- `src/data/hyperliquid.py`
- `research/run_hip3_analysis.py`
- `src/engine/backtest.py`

repo 基本信息：
- **Author / Repo owner：** `andreaambrosio`
- **Year：** 2026
- **Title：** *hype-backtesting*
- **Venue：** GitHub repository
- **DOI：** N/A
- **Readable URL：** <https://github.com/andreaambrosio/hype-backtesting>
- **Repo URL：** <https://github.com/andreaambrosio/hype-backtesting>

README 里最关键的不是“这个仓里有 9 个策略”，而是它把 **Basis Dislocation Reversion** 明确列成当前 sample 里的最佳策略：
- 样本：`90 days` 的 Hyperliquid `1h` 数据
- 覆盖资产：`BTC / ETH / SOL / HYPE / TURBO / MEME / WIF`
- repo 报告的 Basis Dislocation Reversion 结果：
  - Return：`+3.88%`
  - Sharpe：`4.52`
  - Sortino：`6.16`
  - Max DD：`15.69%`
  - Win rate：`24.7%`
  - Profit factor：`1.05`
  - Trades：`299`

同时 README 还给了一个更 desk-friendly 的 microstructure 句子：
> 在 HIP-3 Silver crash 里，basis 一度冲到 `463 bps`，高于 `400 bps` 只持续了 `95 seconds`，随后在 `19 minutes` 内压回到 `<50 bps`。

这句比“小时线回测收益多少”更重要，因为它直接说明：**这条 edge 的自然栖息地其实更像 `1m / 3m / 5m`，而不是只停留在 `1h`。**

## 2. base alpha 先说清楚
这条线的 **base alpha** 很简单：

> **当 perp mark 明显偏离 oracle，而且偏离已经进入该资产自身的极端分位区间时，后续更容易发生 premium / basis 压缩；最小表达就是“做 dislocation fade”。**

翻成人话：
- 不是“价格涨多了就跌”；
- 也不是“funding 高就做空”；
- 更不是抽象的 market-making overlay；
- 它盯的是一个更具体、更交易化的对象：**`mark_price - oracle_price` 或 `premium` 本身。**

所以它属于：
- `raw alpha`，不是 filter；
- `single-asset relative-value / stat-arb`，不是单纯 directional momentum；
- `short-horizon mean reversion`，不是慢频 carry。

## 3. 为什么说这不是零散指标，而是一条完整策略
### 3.1 entry 已经写得很清楚
`src/strategies/basis_reversion.py` 的核心逻辑很直接：

1. 先把 premium 转成 `bps`：
   - 若 dataframe 已有 `premium` 列，直接 `premium * 10_000`
   - 否则用 `(mark_price - oracle_price) / oracle_price * 10_000`
2. 取最近 `lookback_bars=100` 的 premium 分布
3. 开仓阈值不是固定死值，而是：
   - `max(entry_dislocation_bps, rolling 95th percentile)`
   - 默认 `entry_dislocation_bps = 50 bps`
   - 默认 `percentile_entry = 0.95`
4. 方向是反着做：
   - `current_premium > 0`：short
   - `current_premium < 0`：long

这就把信号说得非常完整了：
**不是任何偏离都做，而是只做“已经极端化”的偏离。**

### 3.2 sizing 也不是空着的
源码不是简单 all-in / fixed size，而是按 dislocation 强度放大：
- `base_position_pct = 0.10`
- `scale = min(abs_premium / entry_dislocation_bps, 3.0)`
- `max_position_pct = 0.25`

意思很直白：
- 偏离刚过阈值，只开基础仓；
- 偏离越大，仓位越大；
- 但最多 cap 在 `25%` equity。

这对 desk 很重要，因为它不是一句“极端更值得做”，而是**已经把极端程度映射成仓位函数。**

### 3.3 exit / stop / time-stop 也齐了
同一个文件里 exit 条件也都明确给出：
- **Take profit：** `abs_premium < 10 bps`
- **Time stop：** `bars_held >= 60`
- **Hard stop：** 若 dislocation 继续恶化到 `200 bps` 级别就止损

也就是说，这条线不是“看到 premium 就写篇观察笔记”，而是已经自带：
- entry
- exit
- sizing
- stop
- max hold

所以这轮它完全符合用户说的高优先级：
> **可独立复现且可直接落地为完整策略的 raw alpha 候选。**

### 3.4 成本 / 风控也不是事后脑补
`src/engine/backtest.py` 里，回测引擎默认就把这些东西收进去了：
- `commission_bps = 2.0`
- `slippage_bps = 1.0`
- `max_position_pct = 0.25`
- `max_drawdown_pct = 0.15`

这当然不代表 repo 的结果就一定可信到能直接上线，但至少说明：
**它讨论的是“可交易 alpha”，不是只会画因子图的研究玩具。**

## 4. 这条 alpha 和当前 desk 为什么直接相关
### 4.1 它补的是 raw alpha 素材池，不是旁支解释层
近几轮已经补了不少：
- funding / basis carry
- spread z-score fade
- lead-lag catch-up
- cross-sectional loser bounce

而这条线补的是另一类更 microstructure、更 execution-native 的原料：
> **极端 mark-vs-oracle 偏离本身就是 alpha 对象。**

它不是给某条已有 alpha 当确认器，而是自己就能单独做成一条信号书。

### 4.2 它天然适合 `1m / 3m / 5m`
原因很简单：
- README 给的最典型案例，本来就是 `95 seconds` 到 `19 minutes` 这种压缩尺度；
- 这比 `funding 8h`、`日频横截面` 更自然地落在短周期；
- `15m` 也能做，但更像 admission / coarse bucket，不是它最锋利的主战场。

所以最自然的 desk 化映射应是：
- `1m / 3m / 5m`：主信号
- `15m`：极端 regime 标记 / 资产筛选 / 是否值得开 collector

### 4.3 它和已有 basis/funding digest 不是同一件事
需要刻意区分：
- **funding carry**：赚长期拥挤付费
- **spot-perp basis trade**：赚更慢的同所价差回归 / carry
- **这条 mark-vs-oracle dislocation fade**：赚短时错误定价压缩

也就是说，这条线更接近：
- 短时 liquidity gap fade
- stale quote / panic premium fade
- microstructure stat-arb

而不是“再来一篇 funding 逻辑”。

## 5. 公开数据能不能拿？最小实验怎么做？
### 5.1 数据源
`src/data/hyperliquid.py` 已经把公共数据入口写得很清楚，全部走 Hyperliquid 的公开 `info` 接口：
- `get_candles()`：`1m / 5m / 15m / 1h / 4h / 1d`
- `get_funding_history()`：历史 funding + premium
- `get_meta_and_asset_ctxs()`：全市场 live context（含 funding / mark / 资产状态）
- `get_all_mids()`：当前 mid

这说明：
- **公开性：** 是，公共 API，无需私钥
- **更新频率：** live context 近实时；candle 支持分钟级
- **最小可复现性：** 能快速开 collector 开始录

### 5.2 但这里有个必须说清楚的现实约束
如果你要认真测 `1m / 3m / 5m` 的 premium-dislocation edge，**不能只靠 funding history 的 8h 快照。**

真正需要的是更高频的 `mark / oracle / premium` 路径。

也就是说：
- `1h` 研究可以先复用 repo 那种合并后的公共数据口径；
- **短周期最小实验** 则应立刻自采：定时拉 `metaAndAssetCtxs()`，每 `10s / 15s / 30s` 存一笔，落地 DuckDB / Parquet。

这不算“数据不可得”，只是：
> **它是 public & quickly collectable，但不是现成一键下载好的多月高频历史包。**

### 5.3 最小实验口径
先不要一上来就做复杂组合，最小实验可以很朴素：

- 资产：`BTC / ETH / SOL / HYPE` + 1~2 个更容易失衡的 HIP-3 名字
- 主频：`1m`
- 子频：`10s ~ 30s` collector
- 信号：
  - `abs(premium_bps)` 超过 rolling `95%` 分位
  - 且绝对值也要过固定底线，例如 `50 bps`
- 方向：
  - `premium_bps > 0` -> short
  - `premium_bps < 0` -> long
- 平仓：
  - `abs(premium_bps) < 10`
  - 或 `max_hold = 3 / 6 / 12` 根 `1m` bar
  - 或 adverse move 超过 `150 / 200 bps`

### 5.4 第一批必须做的对照组
至少并排跑这四组：
1. **fixed threshold only**：只看 `50 bps`
2. **percentile only**：只看 rolling `95%`
3. **max(fixed, percentile)**：repo 默认逻辑
4. **+ asset liquidity gate**：只在相对 liquid 的名字上做

因为真正该回答的问题不是“有无 reversion”，而是：
**极端阈值到底该用固定 bps、资产内部分位，还是两者取 max。**

## 6. first verdict：值得进池，但别把 repo 的 hourly 胜利直接当 short-cycle 结论
### 6.1 为什么值得进池
- **base alpha 非常清楚**：做极端 premium 的回归
- **完整策略骨架齐全**：entry / exit / sizing / stop / cost 都有
- **公开数据可拿**：至少从现在开始能立刻收
- **和 short-cycle 匹配度高**：案例本来就发生在分钟级

### 6.2 为什么还不能直接宣称“已过线”
要保留三点怀疑：

1. **repo 公布的主结果是 `1h`，不是 `1m / 3m / 5m`。**
   这能证明思路可写成策略，但不能自动证明短周期净后也赚钱。

2. **若只用单腿 perp fade，方向风险并没有消失。**
   它虽然盯的是 relative-value 变量，但执行上仍是单腿 long/short；若当下是持续性踩踏 / squeeze，premium 可能越拉越极端。

3. **真正的边际在执行，而不是在口头逻辑。**
   这类 edge 很可能死在：
   - 采样太慢
   - 进场排队太差
   - 一律 taker
   - 极端时段 liquidity vacuum

所以更诚实的定位是：
> **高优先级 raw alpha intake，适合尽快做分钟级最小实验；但当前证据还不等于 production-ready。**

## 7. 下一步怎么测
### 7.1 先做数据层
- 起一个最小 collector，拉 Hyperliquid `metaAndAssetCtxs` 或等价 live context
- 每 `10~30s` 记录：
  - `mark_price`
  - `oracle_price`
  - `premium`
  - `funding`
  - `coin`
  - `timestamp`
- 同步拉 `1m` candles，用来估算 realized vol、ATR、成交量过滤

### 7.2 先做 event study，不要先做花哨组合
第一版就回答 4 个问题：
1. premium 超过 `50 bps` 后，回到 `10 bps` 的中位时间是多少？
2. `95%` / `97.5%` / `99%` 分位，哪档的 `net bps/trade` 最稳？
3. 正 premium 和负 premium 哪边更容易赚钱？
4. liquid majors 和小币 / HIP-3 名字，谁更值得做？

### 7.3 exit 先做三挡，不要过拟合
先跑：
- `compression exit`
- `fixed 3-bar / 6-bar / 12-bar exit`
- `compression or timeout whichever first`

### 7.4 成本一定要分层
这类策略一定要显式做 cost ladder：
- maker / taker 混合
- 纯 taker
- 加入 stress slippage

先看：
- `gross bps / trade`
- `net bps / trade`
- `median time-to-compression`
- `fill sensitivity`

## 8. 风险与保留意见
- **stale oracle / stale mark 风险：** 如果 oracle 更新节奏本身滞后，会制造假 dislocation。
- **极端行情 continuation 风险：** 真正的崩盘 / squeeze 期，premium 可以继续扩张，不会立刻均值回复。
- **edge 衰减风险：** 这种 microstructure alpha 一旦被更多做市 / 套利资金盯上，压缩会更快，留给 taker 的肉更少。
- **资产异质性很大：** `BTC`、`ETH`、`HYPE`、长尾 HIP-3 名字的 dislocation 机制不一样，别混成一锅统一阈值。

## 9. 来源
- Andrea Ambrosio. (2026). *hype-backtesting*. GitHub Repo.  
  Repo URL: `https://github.com/andreaambrosio/hype-backtesting`
- Andrea Ambrosio. (2026). *README.md*.  
  Readable URL: `https://github.com/andreaambrosio/hype-backtesting/blob/main/README.md`
- Andrea Ambrosio. (2026). *src/strategies/basis_reversion.py*.  
  Readable URL: `https://github.com/andreaambrosio/hype-backtesting/blob/main/src/strategies/basis_reversion.py`
- Andrea Ambrosio. (2026). *src/data/hyperliquid.py*.  
  Readable URL: `https://github.com/andreaambrosio/hype-backtesting/blob/main/src/data/hyperliquid.py`
- Andrea Ambrosio. (2026). *research/run_hip3_analysis.py*.  
  Readable URL: `https://github.com/andreaambrosio/hype-backtesting/blob/main/research/run_hip3_analysis.py`
- Andrea Ambrosio. (2026). *src/engine/backtest.py*.  
  Readable URL: `https://github.com/andreaambrosio/hype-backtesting/blob/main/src/engine/backtest.py`

## 10. 本地产物
- Digest：`research/quant_digests/2026-04-15_1128_mark-oracle-percentile-dislocation-fade-alpha.md`
- 发布后页面：`https://jp.jerrypsy.top/momentum/reading/quant_digests/2026-04-15_1128_mark-oracle-percentile-dislocation-fade-alpha.html`
