# 别把这份 2026 `cryptoarb` repo 继续只读成 funding 套壳：对 desk 更该先测的是「positive perp-premium shock × spot-perp basis reversion」raw alpha，BTC/ETH 先降级

- 时间：2026-03-31 17:14 UTC
- 类型：quant_digest
- 主题标签：raw-alpha/basis/spot-perp/mean-reversion/perp-premium/positive-basis-only/binance/link/avax/btc/eth/5m/15m/repo/public-data/cost
- 证据类型：2026 GitHub 仓库 source audit（README + `config/main.yaml` + `strategies/basis_revert.py`）+ Binance Spot / USDⓈ-M Perpetual 公共 `5m/15m` 本地最小快检

- 主题类型：raw alpha
- 基础 alpha：同一资产的 spot-perp basis（尤其是 **perp 相对 spot 的正溢价冲高**）在短周期内会向常态回归
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1. 这次看了什么
这次主材料不是论文，而是一份刚更新的 2026 新 repo：**`gencersarp/cryptoarb`**。它 headline 写的是 market-neutral arbitrage research framework，里面同时放了 funding、basis、perp-perp、stat-arb 几条线。

但如果按我们当前 desk 的优先级来读，这份 repo 最值得先拎出来做独立 digest 的，不是 funding 壳子本身，而是其中更容易快速最小复现的一支：**spot-perp basis mean reversion**。

更具体地说，这次真正该进素材池的 base alpha 不是“所有 basis 都能 fade”，而是：

**当 perp 相对 spot 的正 premium 冲得足够高、又还没进入结构性失衡时，后续更可能回落；对我们 desk，更可交易的第一版不是双边对称 basis fade，而是先做 `positive basis only` 的 `short perp / long spot`。**

## 2. 为什么这次值得进研究池
结合最近几轮学习进展，我们已经补了很多：
- current+next funding carry；
- async funding clock；
- perp-perp funding differential；
- same-underlier multi-quote；
- 多种 pairs / stat-arb / percentile entry。

但当前素材池里，**“短周期 spot-perp basis 自身是不是一个独立 raw alpha”** 这块还不够清楚。

这份 repo 值得补的地方在于：
1. **base alpha 很清楚**：不是 filter，不是 overlay，就是 basis 偏离本身的回归；
2. **可直接落地成完整结构**：entry / exit / sizing / stop / max hold / cost shell 都能写；
3. **和现有 funding / premium / multi-quote 素材天然互补**：basis 是它们中间最接近“可直接下手的相对价值腿”的那层；
4. **很适合做快速 falsification**：用公开 Binance spot + perp 数据，几分钟就能知道这条线在 majors 上是肥是瘦。

## 3. 先回答一句：这篇东西的 base alpha 是什么？
**base alpha = 同一资产 perp 相对 spot 的 basis 偏离会均值回复；其中对 desk 最友好的第一版，是 `perp 贵得过头 → short perp / long spot` 的正 basis 回归。**

所以它本质上是：
- `relative-value`
- `stat-arb`
- `mean reversion`
- 但交易对象不是两只 coin 的 spread，而是 **同一资产 spot vs perp 的溢价差**。

## 4. 核心来源
### 4.1 主仓库
- **Author / Owner**：Gencer Sarp
- **Year**：2026（repo 创建于 2026-03-29，2026-03-31 有更新）
- **Title**：*CryptoArb — Production-Grade Crypto Market-Neutral Arbitrage Framework*
- **Venue**：GitHub repository
- **DOI**：无
- **Readable URL / Repo URL**：https://github.com/gencersarp/cryptoarb

### 4.2 这次实际重点看的文件
- `README.md`
- `config/main.yaml`
- `strategies/basis_revert.py`

### 4.3 本地最小快检数据源（公开可得）
- **Binance Spot klines**：`https://api.binance.com/api/v3/klines`
- **Binance USDⓈ-M Perpetual klines**：`https://fapi.binance.com/fapi/v1/klines`
- 更新频率：秒级 / 毫秒时间戳，落到 `5m / 15m` 完全够用

## 5. 仓库里最该拿走的硬点
### 5.1 repo 已经把 basis MR 写成了很清楚的策略骨架
`strategies/basis_revert.py` 的逻辑非常直白：
- `basis = (perp_price - spot_price) / spot_price`
- basis z-score 太高：`short perp / long spot`
- basis z-score 太低：`long perp / short spot`
- `exit_z` 回归就平
- `stop_z` 超限就砍
- 再配 `max_hold_bars`

也就是说，这不是综述材料，而是已经非常接近可复现策略说明书。

### 5.2 repo 默认参数给了一个完整的“第一版策略壳”
`config/main.yaml` 对 `BasisMeanRevert` 的默认设置是：
- `zscore_lookback = 48`
- `entry_z = 2.0`
- `exit_z = 0.5`
- `stop_z = 3.5`
- `max_hold_bars = 36`
- `position_size_pct = 0.35`
- `max_open_positions = 2`

注意它的原始数据频率是 **8h**，所以这些数值**不能直接照抄**到 `5m / 15m`。但结构本身很值得保留：
- 先定 basis 统计窗口；
- 用极端分位/极端 z admission；
- 用回归阈值退出；
- 用 stop_z 和 max-hold 把错误 pocket 限死。

### 5.3 这份 repo 的价值，不只是信号，还有交易壳
它在 `config/main.yaml` 里同时给了很重要的落地约束：
- 1-bar execution delay
- cost stress 1.5x
- maker fill probability 55%
- slippage 0.5~18 bps
- max drawdown 10%
- max leg divergence 35 bps
- orphan protection: max unhedged 1 bar

这意味着它对我们真正有价值的地方，不只是“basis 可以回归”这句话，而是：
**它把一个可执行的 market-neutral shell 先搭出来了。**

## 6. 本地最小快检：最有价值的不是“能不能做”，而是“该做哪一边、哪类币”
我用 Binance Spot + Binance USDⓈ-M Perpetual 公共 `5m/15m` 数据，做了一个非常粗但方向够用的 transfer check：
- 信号：rolling basis z-score 极值；
- 逻辑：1 bar delay；
- 收益：用 perp-leg return 减 spot-leg return 近似 spread PnL；
- 成本：双腿每次调仓按 taker+slip 的保守口径计入。

### 6.1 15m majors：BTC / ETH 不肥，after-cost 基本不值得继续重仓读
过去约 31 天、`15m` quick check 里：
- **BTC basis |p95| ≈ 6.71 bps**
- **ETH basis |p95| ≈ 6.66 bps**

这个厚度对 short-cycle 来说太薄。
即使逻辑方向没错，绝大部分边也会被双腿成本吃掉。

### 6.2 5m mid-cap pockets：LINK / AVAX 比 BTC / ETH 更像候选
过去约 17 天、`5m` quick check 里：
- **LINK basis |p95| ≈ 14.72 bps**
- **AVAX basis |p95| ≈ 15.45 bps**
- 而 BTC / ETH 还是只有 **~7 bps** 左右

翻成人话：
- majors 的 basis 贴得太紧；
- 中等活跃度但 perp 溢价偶尔能拉开的币，才更像我们能摸到的 pocket。

### 6.3 对称双边做法不如先做 `positive basis only`
本地 `5m` 快检里，`positive basis only`（只做 `perp 贵 → short perp / long spot`）比对称双边更像 desk-friendly 版本：

#### LINK（`5m`, 约 17 天）
- trades：**7**
- gross：**+1.09%**
- costs：**0.98%**
- net：**+0.11%**
- Sharpe：**~1.08**

#### AVAX（`5m`, 约 17 天, `positive basis only`）
- trades：**5**
- gross：**+0.77%**
- costs：**0.70%**
- net：**+0.07%**
- Sharpe：**~1.01**

#### 对照：BTC / ETH（`5m`, `positive basis only`）
- BTC net：**-1.75%**
- ETH net：**-1.32%**

这组数的重点不是“已经能上线”，而是：
**同样的 basis fade 骨架，在 majors 上多半只是成本捐赠；在某些 mid-cap 上，至少开始出现“gross 能盖住一部分成本、净值接近转正”的味道。**

## 7. 对 desk 最重要的重读：不要把它写成对称 basis fade，要先单边化
如果直接照教科书写成：
- basis 太高就 short perp / long spot
- basis 太低就 long perp / short spot

那在 desk 侧会立刻碰到两个现实问题：
1. **负 basis 那一边更依赖 spot short / borrow 能力**；
2. **短周期里负 basis 侧经常既薄又难做，执行不如正 basis 侧顺手。**

所以 repo 对我们真正有价值的“旁支想法”是：

**先把 basis MR 做成 `positive basis only` 的 one-sided raw alpha，再把 negative side 留作后续扩展。**

这就从“理论上对称”变成了“desk 上更容易真的做”。

## 8. 怎么把它拆成完整策略
### 8.1 Entry
先定义：
- `basis_t = (perp_t - spot_t) / spot_t`
- `z_t = zscore(basis_t)`

第一版建议：
1. 只做 `basis_z >= entry_z`
2. 同时要求 `basis_abs_bps > roundtrip_cost_bps + safety_buffer`
3. spot/perp 两边盘口深度都够
4. 近几根 bar 没有极端跳价 / 无成交异常

### 8.2 Exit
先用最朴素三层：
1. `abs(z) <= exit_z`
2. `abs(z) >= stop_z`
3. `bars_held >= max_hold`

### 8.3 Sizing
先别花哨：
- 基础仓位按 `abs(z) / entry_z` 线性放大，但 capped；
- 再乘一个 `basis_abs_bps / cost_hurdle_bps` 的 pocket 质量因子；
- 再乘一个 depth cap。

### 8.4 Risk
至少要有：
1. **orphan protection**：任一腿掉线最多允许裸露 1 bar；
2. **leg divergence cap**：超阈值直接强平；
3. **venue health veto**：spot/perp 任何一边 API 或流动性异常就停；
4. **funding clock awareness**：不要在 funding 结算前后把偶发 jump 错当常规均值回复。

### 8.5 Cost
这类 alpha 最怕“逻辑对、净值死”。
所以至少要做三套：
- maker 乐观版
- taker 保守版
- mixed realistic 版

并且必须按 **双腿 roundtrip** 算：
- perp fee/slip
- spot fee/slip
- 可能的 borrow / financing
- 资金占用

## 9. 对 `1m / 3m / 5m / 15m` 的正确映射
### 9.1 5m 是当前最自然的最小实验频率
原因很简单：
- 1m 太容易被微观噪音和 quote 抖动淹没；
- 15m 在 majors 上又可能太慢、太薄；
- 5m 正好能保留一些 basis pocket，又没把 turnover 放大到最夸张。

### 9.2 15m 更适合先做 falsification card
这次 quick check 已经很说明问题：
- BTC / ETH 的 15m basis 厚度不够；
- 如果 15m majors after-cost 都留不住边，那就不该继续把这条线当 universal alpha。

### 9.3 1m / 3m 目前先别直接上主回测
先做：
- 盘口深度
- 盘口恢复时间
- 结算前后 basis 冲高回落的 microstructure path

等这些搞清，再把频率往下压。

## 10. 数据公开性与最小可复现实验口径
### 10.1 数据源
- Binance Spot klines
- Binance USDⓈ-M Perpetual klines

### 10.2 公开性
- 完全公开
- 无需私有 API key 就能先做最小实验

### 10.3 更新频率
- 秒级/毫秒时间戳，聚合到 `5m / 15m` 没问题

### 10.4 最小复现实验
#### 实验 A：5m positive-basis-only 单币 pocket screen
- universe：`BTC, ETH, SOL, DOGE, LINK, AVAX, ...`
- signal：`basis_z >= 2.5`
- action：`short perp / long spot`
- exit：`z <= 0.5` 或 `z >= 3.5` 或 `max_hold`
- 目标：先看哪类币 `gross > cost`

#### 实验 B：15m majors falsification
- 只做 BTC / ETH
- 目标不是赚钱，而是确认“majors basis 太薄”是否稳定成立
- 如果稳定为负，就把 majors 从这条线的主战场里降级

#### 实验 C：funding-clock conditional basis MR
- 只在 funding 前后固定窗口内允许 admission
- 检查 basis 回归是否更集中发生在结算时钟附近
- 若成立，它仍然是 raw alpha，只是 admission 更精确

## 11. 它和当前素材池怎么拼
我认为它最适合放在这里：

1. **raw alpha 本体**：
   - `positive perp-premium shock → spot-perp basis reversion`
2. **可复用 gate / overlay**：
   - funding 结算时钟
   - depth collapse veto
   - orphan/leg divergence protection

也就是说：
- raw alpha 是 basis 本身的回归；
- 时钟和执行约束只是把 pocket 做得更干净。

## 12. 局限与风险
1. **repo 默认是 8h 频率，不可机械照抄到 5m/15m**。
2. **本地 quick check 很粗**：只是最小转译，不是正式 walk-forward。
3. **mid-cap pocket 虽然更厚，但 trade count 偏少**：容量和稳定性都要继续验证。
4. **negative basis 侧未必 desk-friendly**：若 borrow/short 代价高，就不该一上来做对称结构。
5. **spot/perp 任何一腿执行失败都会把 market-neutral 变方向暴露。**

## 13. 我建议的“下一步怎么测”
1. **先把 universe 扩到 15~30 个 spot+perp 同时可交易资产**，做 `5m positive-basis-only` 横截面筛选；
2. **先看 gross-vs-cost，不先看 Sharpe 美观度**；
3. **只保留 `basis |p95|` 明显高于 roundtrip 成本的币**；
4. **对 LINK / AVAX 做更严格 walk-forward**，检查 pocket 是否只集中在少数 funding 时钟或波动 regime；
5. **把 negative-basis side 单独拆出去**，等确认 borrow/融资/spot short 可做，再决定是否并回完整双边策略。

## 14. 一句话结论
这份 2026 `cryptoarb` repo 对 desk 最有价值的，不是把 funding / basis / stat-arb 全都一起抄，而是先诚实拆出一条更能快速复现的 raw alpha：**只做 `perp 贵得过头` 的 spot-perp basis 回归，而且第一版优先看 LINK / AVAX 这类 mid-cap pocket，BTC / ETH 先降级。**

## 15. 来源链接
- Repo：https://github.com/gencersarp/cryptoarb
- Binance Spot klines：https://api.binance.com/api/v3/klines
- Binance USDⓈ-M Perpetual klines：https://fapi.binance.com/fapi/v1/klines
