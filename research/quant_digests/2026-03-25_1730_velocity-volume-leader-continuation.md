# 别把“涨速+放量”只写成一句追涨口号：这份 2025 新仓库更该先测的是「动态阈值 leader continuation + 二段式入场」完整 raw alpha
- 时间：2026-03-25 17:30 UTC
- 类型：2025 GitHub 新仓库 + TSMOM / intraday momentum literature 地基
- 主题类型：raw alpha
- 基础 alpha：短周期 price-velocity breakout 之后的 leader continuation（强势币在放量但未极端超买时，后续 `15m~4h` 继续延续）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/trend/momentum/leader-continuation/price-velocity/volume-confirmation/sector-rotation/two-stage-entry/atr/position-sizing/risk/binance/spot/perpetual/1m/3m/5m/15m/repo/paper
- 证据类型：仓库实现 + 文献地基（工程经验/待验证）

## 1. 这次看了什么
先回答一句：**这篇东西的 base alpha 是什么？**

不是“板块轮动 filter”，也不是“ATR 风控壳子”，而是：**短周期强势币在 price-velocity 突破后，若同时伴随放量、且尚未极端过热，后面一小段时间往往还有 continuation 可以吃。**

这次主材料是 **yeshunyi (2025), _crypto-momentum-strategy_**。它不是学术论文型材料，而是一份把 **entry / exit / sizing / risk / execution** 都写进代码的完整工程仓库。对当前 desk 来说，最值钱的不是“又一个追涨 bot”，而是它把 **leader continuation** 这条 raw alpha 写成了一个可立即开最小实验的完整骨架：
- 用 **BTC ATR** 决定看 `5m / 10m / 15m` 哪个涨速窗口；
- 用 **涨速阈值 + 量比 + RSI** 选出真正像 leader 的币；
- 再用 **二段式入场**、`ATR` 目标和总风险约束，避免把“看到拉升就梭哈”当策略。

## 2. 核心结论
- **一句话核心结论：** 这条线值得进 raw alpha 池，而且它不是“纯解释型 trend 研究”，而是已经接近可直接 desk 化的 **完整 short-horizon leader continuation skeleton**。
- **一句话它怎么证明：** 仓库代码把信号、仓位、止损、总风险、板块集中度、黑名单和执行节奏都写出来了；虽然还缺严格 OOS 证据，但已经足够支撑一个 `5m/15m` admission 级最小复现。

我从 README、`signal_generator.py`、`market_analyzer.py`、`risk_manager.py` 里抽出来，最有信息量的不是空泛口号，而是下面这些**可直接落成实验参数**：

1. **动态信号窗口不是固定的。**
   - 若 `BTC ATR > 5%`：看 `5m` 涨速，阈值 `3%~5%`
   - 若 `3% <= BTC ATR <= 5%`：看 `10m` 涨速，阈值 `2%~3%`
   - 若 `BTC ATR < 3%`：看 `15m` 涨速，阈值 `1.5%~2.5%`
   - 亚洲时段额外把阈值再抬 `+0.5%`；周末则降 `-0.3%`

2. **它不是只看价格，至少有一层“别追到最热那一下”的约束。**
   - 量比必须 `> 1.5`
   - `RSI > 75` 直接过滤
   - 信号评分里，`momentum` 最多给 `40` 分，`volume` 给 `25` 分，热门板块给 `15` 分，`RSI` 最多给 `10` 分
   - 板块分数也不是拍脑袋：`0.4*平均涨幅 + 0.3*龙头涨幅 + 0.3*量比增长`

3. **风险壳子写得比一般“追涨脚本”完整。**
   - 单笔风险上限 `2%`
   - 总风险上限 `15%`
   - 单一板块占比上限 `40%`
   - `BTC ATR > 7%` 时暂停新开仓
   - 黑名单会剔除：`7d max drawdown > 25%` 或 `30d volume < $1,000,000`
   - 仓位大小不是固定手数，而是 `risk_budget / 2% stop`，再按 market state 做 `1.2x / 0.7x / 0.5x` 调整

翻成人话：**真正值得先测的不是“某币拉了 3% 就追”，而是“在高/中/低波动状态下，用不同涨速窗口挑 leader，再用 volume / RSI / 板块强度做第二层筛，最后把进场做成试探 + 确认两段”。**

## 3. 为什么和当前项目直接相关
- 这次补的是 **raw alpha 素材池**，不是再补一个 overlay。基础 alpha 非常清楚：**leader continuation**。
- 它和当前 desk 的时间尺度也对得上：
  - `5m / 15m` 是主频；
  - `1m / 3m` 更适合作为执行分片，而不是把 alpha 本体继续压碎。
- 它还能自然服务两条后续分支：
  1. **单币 continuation**：强币本身继续走；
  2. **cross-sectional winner basket**：把同时满足条件的强势币做 winner basket，相对弱币做对冲或至少做相对评分排序。
- 按 backlog 的优先级看，它比继续加一个 shared gate 更值钱，因为它本身就是一条可独立运行的趋势/动量类 raw alpha 骨架。

## 3.5 策略拆解（必填）
- 方向属性：短周期单币/多币 continuation，可扩成 cross-sectional winner basket
- `entry`：
  1. 按市场波动状态决定看 `5m / 10m / 15m` 哪个涨速窗口；
  2. 若 `ret_window > threshold` 且 `volume_ratio > 1.5` 且 `RSI < 75`，生成候选信号；
  3. 第一段入场先上 `50%`；
  4. 第二段仅在**突破前高且 RSI 仍未过热**时补另外 `50%`。
- `exit`：
  - 固定止损：`-2%`
  - 盈利目标：`1.5 * ATR`（上限 `10%`）
  - 浮盈超过 `+3%` 后，止损上移到成本价
  - README 提示平均持仓时间控制在 `4h` 以内，可加 time stop
- `sizing`：
  - 单笔风险预算 `2%`
  - 总风险 `15%`
  - 板块集中度上限 `40%`
  - 依据 signal score 和 market state 调仓，而不是所有信号等权
- `risk / veto`：
  - `BTC ATR > 7%` 暂停开新仓
  - 黑名单：近期大回撤、成交量过小
  - 熊市只允许高分信号（代码里直接要求 `score >= 70`）
- `execution`：
  - 扫描周期 `5` 分钟
  - 冰山阈值与最小下单额已配置（`min_order_amount=10`）
  - 对 desk 更合理的改写是：信号在 `5m/15m` 生成，执行下沉到 `1m/3m` maker-first / TWAP

## 4. 可复刻的最小实验
### 数据源
1. **Binance Spot 或 Binance USDⓈ-M Futures Klines**（公开可得）
   - spot: `https://api.binance.com/api/v3/klines`
   - futures: `https://fapi.binance.com/fapi/v1/klines`
   - 更新频率：公开接口，支持 `1m / 3m / 5m / 15m`
2. **GitHub 仓库源码**
   - Repo：`https://github.com/yeshunyi/crypto-momentum-strategy`

### 最小实验口径
- `universe`：先做 `BTC/ETH/SOL/BNB/XRP/ADA/DOGE/LINK/AVAX/LTC`，后续再扩到 top-30 USDT 对
- `market regime`：用 BTC `14d ATR%` 或 `1d` realized range 代理仓库里的 market ATR
- `signal`：
  1. 根据 regime 选择 lookback = `5m / 10m / 15m`
  2. 要求 `ret_lb > threshold_regime`
  3. `volume_ratio > 1.5`
  4. `RSI < 75`
- `entry`：
  - 第一段：下一根开 `50%`
  - 第二段：若未来 `1~3` 根内突破 signal-bar high，则补到 `100%`
- `exit`：
  - `-2% SL`
  - `+1.5 ATR TP`
  - `+3%` 以后移 breakeven
  - `max_hold = 16 根 15m` 或 `48 根 5m`
- 最先看四个指标：
  1. `gross bps / trade`
  2. `net bps / trade`（至少先跑 `4 / 8 / 12 bps` round-trip）
  3. `trade frequency / day`
  4. `post-entry 1 bar / 3 bar / 12 bar drift`

## 5. 下一步怎么测
1. **先做最小 honest version，不要把板块和社交数据一次性全塞进去。** 先只保留 `dynamic lookback + threshold + volume_ratio + RSI` 四件套，确认 base alpha 是否成立。  
2. **把二段式入场单独做 A/B。** 比较“信号即满仓” vs “50% 试探 + 突破前高再补仓”，看它到底是在提高胜率，还是只是在拖慢成交。  
3. **把单币 continuation 和 winner basket 分开测。** 若单币层面太薄，可以改成同一时点只做 top-`k` leaders，转成 cross-sectional winner basket。  
4. **做 regime 分桶。** 关键不是全样本平均，而是看 `BTC ATR <3 / 3~5 / >5` 三档里哪一档真正留下 edge。  
5. **执行层下沉。** 信号保留在 `5m/15m`，但撮合改成 `1m/3m maker-first`，否则这类 thin edge 很容易全死在 taker cost。  
6. **加“第二天不追同一币”拥挤约束。** 强势 leader continuation 很容易退化成 late-chasing，必须看 repeated-entry decay。

## 6. 风险与保留意见
- 这份仓库最强的是**骨架完整**，不是**证据极强**；目前还看不到严格 walk-forward / OOS / capacity 审计。  
- 板块、社交热度、黑名单等模块里有明显工程 shortcut，不能把 repo 自带设定直接当事实。  
- `BTC ATR` 作为全市场 regime 代理有点粗糙；若拿去做 multi-asset leader，最好补 cross-sectional realized-vol / funding / breadth。  
- 这条线最容易犯的错，就是把“leader continuation”做成“任何大涨都追”；实际上它更像**动态阈值下的稀疏 continuation alpha**。  
- 若 `5m` 频段成本后不够厚，不代表策略死了；更可能说明正确落点是 `15m` 信号 + `1m/3m` 执行，而不是把 alpha 本体继续切碎。

## 7. 来源
1. **yeshunyi. (2025). _crypto-momentum-strategy_. GitHub repository.**  
   - Repo URL: `https://github.com/yeshunyi/crypto-momentum-strategy`  
   - Readable URL: `https://github.com/yeshunyi/crypto-momentum-strategy/blob/main/README.md`

2. **Moskowitz, T. J., Ooi, Y. H., & Pedersen, L. H. (2012). _Time series momentum_. Journal of Financial Economics, 104(2), 228–250.**  
   - DOI: `10.1016/j.jfineco.2011.11.003`  
   - Readable URL: `https://doi.org/10.1016/j.jfineco.2011.11.003`

3. **Gao, L., Han, Y., Li, S. Z., & Zhou, G. (2018). _Market Intraday Momentum_. Journal of Financial Economics, 129(2), 394–414.**  
   - DOI: `10.1016/j.jfineco.2018.05.009`  
   - Readable URL: `https://doi.org/10.1016/j.jfineco.2018.05.009`

4. **Li, Z., Sakkas, A., & Urquhart, A. (2022). _Intraday time series momentum: Global evidence and links to market characteristics_. Journal of Financial Markets, 57.**  
   - DOI: `10.1016/j.finmar.2021.100619`  
   - Readable URL: `https://doi.org/10.1016/j.finmar.2021.100619`

## 8. 本地产物
- `research/quant_digests/2026-03-25_1730_velocity-volume-leader-continuation.md`
