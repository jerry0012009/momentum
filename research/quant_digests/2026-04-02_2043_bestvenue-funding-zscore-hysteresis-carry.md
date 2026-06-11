# 别把 cross-venue funding carry 继续写成“扫最肥 funding 就上”：这份 2026 repo 更该先抄的是「best-venue funding z-score + hysteresis / min-hold」两腿 cash-and-carry 完整策略
- 时间：2026-04-02 20:43 UTC
- 类型：2026 GitHub 仓库（README + strategy / notebook / 风控部分细读）+ carry 论文链路
- 主题类型：raw alpha
- 基础 alpha：在多个 venue 中挑出当下最肥、且相对自身历史显著偏离的 funding/basis 机会；做空高正 funding 的 perp、做多现货，或在极端负 funding 时反向做多 perp、做空/替代现货，对冲方向后赚 funding 与 basis 回归
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / carry / funding / basis / relative-value / stat-arb / spot-perp / cross-venue / hysteresis / min-hold / hyperliquid / binance / 5m / 15m / 1m / 3m / repo / paper / public-data / cost
- 证据类型：开源策略仓库 + notebook 回测结果 + 学术 carry 链路

## 1. 这次看了什么
这次主材料不是再找一篇“funding 会不会预测价格”的解释型 paper，而是直接 intake 一个**可独立复现、可完整落地的 carry/funding raw alpha 策略仓库**：

- **PietroC21 (2026), _Crypto-PerpetualFutures_**, GitHub repo
- 核心实现文件：`strategy.py`、`strategy_cross.py`
- 关键 notebook：`notebook.ipynb`、`notebook_cross.ipynb`、`FINAL_Notebook.ipynb`

它最值得 desk 抄的地方，不是“funding 高就去收息”这句废话，而是把 raw alpha 真正拆成了完整策略骨架：
1. **venue 选择**：不是固定 Binance，而是每个时点按币种去找 `best funding rate`
2. **信号**：不是看 funding 绝对值，而是看 **相对自身历史的 z-score 偏离**
3. **退出**：不是一碰回落就平，而是用 **zero-cross + min-hold** 控 turnover
4. **风险**：OI gate、VIX gate、SPY drawdown gate
5. **成本**：把 perp + spot 双腿 taker fee 明确写进 PnL

对我们 desk 来说，这个题是合格的 **raw alpha**，不是 filter/overlay 伪装货。

## 2. 这条东西的 base alpha 到底是什么
一句话先说清：

> **base alpha = cross-venue、delta-neutral 的 funding/basis carry。**

更具体一点：
- 当某个币在某个 venue 的 perp funding **显著高于它自己的常态**时，说明这个 perp 被追得过热；
- 此时做 **short perp + long spot**，拿 funding，并等 perp/spot 关系向常态回归；
- 当 funding **显著为负**时，反向做 **long perp + short/替代现货**；
- 但不是见到 funding 高就上，而是要先过：
  - `z_entry` 阈值
  - OI 流动性 gate
  - 宏观风险 gate
  - `min_hold + z_exit`，避免来回被手续费打死。

所以它不是单纯“票息策略”，而是：
**carry 机会选择 + 偏离标准化 + 持有治理 + 成本约束** 的完整 raw alpha。

## 3. repo 里最值得 desk 抄的，不是 carry 本身，而是这个“可活下来”的策略写法
### 3.1 交易骨架
`strategy_cross.py` 的核心逻辑可以直接翻成人话：
1. 对每个币，把各 venue funding 统一到可比口径（repo 里做了 1h/8h 归一）
2. 每个时点取 `best_fr = max(|fr|)`，保留方向
3. 对 `best_fr` 做滚动 z-score（默认 lookback `270` 个 8h 周期，约 90 天）
4. 只有当 `|z| > 2.0` 才开仓
5. 方向约束：
   - `best_fr > 0` → short perp / long spot
   - `best_fr < 0` → long perp / short/替代现货
6. 平仓不是“z 回到 1.9 就走”，而是：
   - **z 回到 0 附近**
   - 且**至少持有 3 个 8h 周期（24h）**
7. 权重默认可做 fixed-weight 或 equal-invested
8. 成本里明确扣：**perp taker fee + spot taker fee**

这比“跨 venue 扫 funding 排名”更值钱，因为它已经把 **entry / exit / sizing / risk / cost** 全都落地了。

### 3.2 对 desk 最有价值的 branch idea
我觉得这份 repo 最值得收进素材池的旁支，不是“多 venue 有更多 carry”，而是：

> **carry alpha 要先做“偏离标准化 + 退出去抖 + 最低持有期”，否则 gross edge 很容易死在双腿成本里。**

也就是说，真正该复现的不是“highest funding scanner”，而是：
- `best venue selection`
- `best_fr z-score`
- `hysteresis / min_hold`
- `explicit two-leg cost`

这套骨架以后也能迁移到：
- 单 venue spot-perp carry
- perp-perp funding divergence
- futures calendar spread
- basis mispricing 的 event pocket 执行

## 4. repo 给了什么硬证据
我挑几个最有信息量、而且和策略是否能活下来直接相关的数字。

### 4.1 不同 venue 的 funding 肥度确实差很多
`notebook_cross.ipynb` 里给的 BTC 示例（8h 口径）显示：
- **Binance 平均 funding：`0.73 bps / 8h`**
- **GateIO：`4.00 bps / 8h`**
- **Hyperliquid：`1.30 bps / 8h`**

更关键的是，repo 统计到：
- **7 币 2023+ 的 Binance 平均 8h funding 约 `0.59 bps`**
- **best-exchange 平均 8h funding 约 `6.68 bps`**
- 相当于 **`+1041.6%` uplift**，也就是多出 **`6.10 bps / 8h`** 的可收息空间

这说明：
**venue routing 不是小修小补，而是 carry alpha 的主收益来源之一。**

### 4.2 这不是“看起来赚钱、扣完费归零”的 paper fantasy
同一个 notebook 的 baseline cross-exchange 结果：
- **Gross CAGR：`17.6%`**
- **Net CAGR：`13.9%`**
- **Ann. Vol：`1.85%`**
- **Sharpe：`2.56`**
- **Sortino：`14.08`**
- **Max Drawdown：`3.62%`**
- **Profit Factor：`6.62`**

而且 repo 还给了一个特别有用的生存线指标：
- 双腿总费率设定：**perp `4.5bps` + spot `10bps` = `14.5bps`**
- 平均每周期 turnover：**`0.0203`**
- **Break-even total fee：`67.5bps`**

这组数字的意义很直接：
**按 repo 的持仓治理和换手控制，这条策略不是“只差 0.1bp 就死”的 fragile edge。**

### 4.3 单 venue carry 不一定活，但 cross-venue + 持有治理能明显改善
repo 的单 venue / cross-venue 对比也很有启发：
- 单 venue 版本在扣费后，表现明显弱得多
- cross-venue 版本的改进，核心不只是多了 venue，而是多了：
  - 更肥的 funding 源
  - 更好的偏离标准化
  - 更低的无效换手

我的理解：
**这份 repo 实际上是在证明“carry 不是没有 alpha，真正决定死活的是你怎么把 alpha 从 gross 变成 net”。**

### 4.4 风险分布并没有崩成“卖保险曲线”
Section 4 notebook 里给的日频风险统计：
- **95% VaR：约 `-0.72% / 日`**
- **95% CVaR：约 `-0.75% / 日`**

这个结果当然不能直接照单全收，但至少说明 repo 不是靠极少数超级大胜日硬撑一条脆弱权益曲线；它更像一条低波动、靠 carry 累积的 market-neutral 收益流。

## 5. 和我们 `1m / 3m / 5m / 15m` desk 的关系：它是 raw alpha，但不是“逐根快节奏主信号”
这点要说清，不然容易把东西读歪。

### 5.1 它为什么仍然值得进 short-cycle 素材池
因为它满足 3 个关键条件：
1. **base alpha 非常清楚**：carry / funding / basis
2. **可以独立成完整策略**：不是只给 filter
3. **执行层能直接映射到 5m/15m，甚至 1m/3m**

但它的自然时钟不是每根 1m bar，而是：
- funding 更新时钟（1h / 8h）
- basis 偏离累计时钟
- 交易执行时钟（5m / 15m 更合适）

所以我会把它定位成：
> **慢信号、快执行的 raw alpha sleeve**

而不是硬伪装成“每根 3m 都能发信号的 scalp 模型”。

### 5.2 对短周期 desk 的正确用法
- **15m**：最适合做主执行频率
- **5m**：适合做入场拆单 / 微观结构择时
- **1m/3m**：更适合 execution veto，而不是主信号重算

换句话说：
- signal generation 可以是 `1h / funding-event aware`
- execution & inventory control 可以放在 `5m / 15m`
- 这完全符合我们 desk 的“慢 alpha + 快执行”框架

## 6. 公开数据、更新频率、最小复现实验口径
这条题主要依赖公开交易所数据，公开性没问题。

### 6.1 数据源
repo 使用的主数据层包括：
- 各交易所 **perp funding rate**（公开）
- 各交易所 **spot / perp 价格**（公开）
- **open interest**（大多公开可拿）
- 宏观 gate 用的 **VIX / SPY / RFR**（公开）

### 6.2 更新频率
- **Funding**：交易所通常按 **1h 或 8h** 更新/结算
- **Spot / perp 价格**：可拿到 **1m 甚至 tick 级**
- **OI**：不同 venue 粒度不同，通常 `5m~1h`

### 6.3 最小可复现实验口径
如果我们现在要 desk 化，最小实验完全可以这样做：
1. 选 `BTC / ETH / SOL / BNB / XRP / DOGE / AVAX`
2. venue 先做 `Binance / Bybit / OKX / Hyperliquid` 四家
3. 每小时或每个 funding 结算时点更新 `best_fr`
4. 用过去 `30~90` 天做滚动 z-score
5. 在 **下一个 5m 或 15m bar** 执行
6. 持有到：
   - z-score 回到 0 附近
   - 或达到最小持有期
   - 或触发 basis / inventory / venue 风险止损
7. 成本必须至少拆成：
   - perp taker / maker
   - spot taker / maker
   - 资金占用与借币/现货成本
   - 滑点
   - missed fill / partial fill

## 7. 下一步怎么测
我建议别先做“大而全 6 venue 生产版”，而是按下面顺序测。

### Step 1：先测 carry 本体能不能在我们口径下存活
目标：验证 `best_fr z-score` 是否比“原始 funding 排名”更稳。

A. 三个 baseline 同时跑：
- `raw best_fr level`
- `best_fr z-score`
- `best_fr z-score + min_hold`

B. 频率：
- signal 更新：`1h`
- execution：`5m / 15m`

C. 输出重点：
- gross / net CAGR
- turnover
- break-even fee
- 按币、按 venue 的 PnL 分解

### Step 2：再测“Hyperliquid/高频 funding venue 的边际价值”
要回答的不是“HL 好不好”，而是：
- 有没有哪类币几乎总是 HL 提供最肥 funding？
- 这些机会在真实成交上有没有容量/滑点问题？
- 若只保留 `top liquidity venues`，alpha 会掉多少？

### Step 3：把 min-hold 改写成 desk 版本
repo 的 `3 × 8h = 24h` 最小持有期对我们太慢，desk 版建议直接扫：
- `1 funding window`
- `2 funding windows`
- `4 funding windows`
- `fixed 6h / 12h / 24h`

我们真正要找的是：
**哪种持有治理，能在不显著伤害 carry 收入的前提下，把换手和腿数砍到最低。**

### Step 4：最后才加 gate / overlay
优先顺序：
1. **stale mark / stale OI veto**
2. **exchange concentration cap**
3. **basis drift stop**
4. **market stress throttle**

不要一上来就把一堆宏观 gate 混进去，不然你根本分不清是 raw alpha 有效，还是 gate 在救它。

## 8. 我当前的判断
这条东西我会给一个偏积极的结论：

> **值得进入研究池，而且优先级不低。**

原因不是它“讲 funding 很合理”，而是它符合我们当前最想补的那类题：
- **raw alpha 清楚**
- **完整策略闭环清楚**
- **公开数据可拿**
- **可以直接做最小实验**
- **还能自然拆成 execution / risk / venue routing 的后续组件研究**

同时它也提醒了一个很重要的 desk 现实：

> carry/funding 类 alpha 的关键不只是找到“最肥的一腿”，而是把 **持有治理、换手治理、venue 治理** 做对；否则看上去是 alpha，实际上只是给手续费打工。

## 9. 来源与复现入口
### 主 repo
- **PietroC21 (2026)**, *Crypto-PerpetualFutures*.
  - Repo URL: `https://github.com/PietroC21/Crypto-PerpetualFutures`
  - README: `https://github.com/PietroC21/Crypto-PerpetualFutures/blob/main/README.md`
  - Core strategy files:
    - `https://github.com/PietroC21/Crypto-PerpetualFutures/blob/main/strategy.py`
    - `https://github.com/PietroC21/Crypto-PerpetualFutures/blob/main/strategy_cross.py`
  - Key notebooks:
    - `https://github.com/PietroC21/Crypto-PerpetualFutures/blob/main/notebook_cross.ipynb`
    - `https://github.com/PietroC21/Crypto-PerpetualFutures/blob/main/FINAL_Notebook.ipynb`

### 学术链路（carry 的资产定价地基）
- **Lin William Cong, Zhiheng He, Ke Tang (2022)**, *Staking, Token Pricing, and Crypto Carry*.
  - Venue: working paper
  - Readable URL: `https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4067751`
  - PDF（repo 镜像）: `https://raw.githubusercontent.com/PietroC21/Crypto-PerpetualFutures/main/Cong-Staking-and-Crypto-Carry.pdf`
  - 关键信息：paper 里给出 **long-short carry Sharpe ≈ `1.6`**，说明 crypto carry 作为 risk premium/relative-value 方向本身有坚实地基，但真正 desk 化仍要靠执行与成本治理。

### 这篇 digest 的一句话结论
**这次该 intake 的不是“funding 很高所以去收息”，而是「best-venue carry + z-score 标准化 + hysteresis/min-hold」这套可直接落地、可直接做 5m/15m 执行实验的完整 raw alpha 骨架。**
