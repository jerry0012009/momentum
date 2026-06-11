# 别把这份 2026 趋势仓只读成“又一个突破系统”：对 short-cycle crypto desk，更该先拆的是「20-bar breakout × dual momentum × ATR expansion」这条完整 raw alpha 壳
- 时间：2026-04-20 11:29 UTC
- 类型：GitHub / repo source audit
- 主题类型：raw alpha
- 基础 alpha：已处于上行结构且波动开始扩张的币，在 `20-bar` 新高突破后更容易继续走，而不是立刻回落
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/trend/momentum/breakout/dual-momentum/atr-expansion/portfolio-ranking/correlation-gate/binance/15m/1h/repo/public-data/cost/risk
- 证据类型：GitHub 工程证据 + Binance public-data portability probe

## 1. 这次看了什么
这次主材料是 2026 GitHub 仓库 **`azuzxx9-jpg/quant-trade-system-v1`**。最值得 short-cycle desk intake 的，不是整套系统，而是其中可单独拆出来的一条完整趋势 sleeve：

- `20-bar breakout`
- `20/60-bar dual momentum`
- `ATR expansion`
- bull-regime gate
- 再接 `next-open` 入场、初始止损、partial take-profit、trailing stop、time stop、组合风险预算与相关性约束

一句话核心结论：**这不是“看到新高就追”的裸 breakout，而是“只追已经在加速、且波动真的在扩张”的 breakout。**

一句话说明它怎么证明：**repo 把 entry / exit / sizing / risk / cost 全写成了可执行规则；再用 Binance Spot `1h/15m` 做最小 portability probe，可以直接看这条 alpha 核心是否有迁移价值。**

## 2. 核心结论
- **base alpha 很清楚，是 raw alpha，不是 filter。** 本体是：`close > SMA20 > SMA50`、`ADX >= 18`、`ATR/close` 处于过去 `120` 根里的较高分位、且价格突破前 `20` 根高点，同时 `20-bar momentum > 3%`、`60-bar momentum > 5%`。
- **它优先服务“趋势延续”，不是反转。** 人话就是：只有当趋势已经走起来、而且最近还在加速时，突破才更值得追。
- **这条线自带完整策略骨架。** repo 不只给 entry，还定义了：`next-open + 5bps` 入场滑点、`min(SMA20 - 1.1*ATR, signal-bar low)` 初始止损、`+2.2R` 先止盈一半、随后 break-even 防守、`5*ATR` trailing stop、`96 bars` time stop、`4bps` fee、组合 risk budget 与 correlation gate。
- **最小 portability probe 显示：它更像“需要 universe/ranking/correlation gate 才成立”的 trend sleeve。** 我沿用 repo 的核心逻辑，用 Binance Spot `BTC/ETH/BNB/SOL` 做简化 isolated sleeve 快检：
  - `1h`：`ETH` 约 `26` 笔、累计 `+6.63%`、平均每笔 `+0.38%`、PF `1.22`；`SOL` 接近打平；`BTC/BNB` 为负。
  - `15m`：`BTC` 约 `8` 笔、累计 `+1.88%`、胜率 `75%`、PF `1.63`；`ETH/SOL/BNB` 整体偏弱。
- **所以最该学的不是“照抄参数”，而是三件事：**
  1. breakout 必须配 acceleration（双动量）
  2. vol expansion 不是装饰，而是防假突破的 admission
  3. 组合层的 ranking / correlation gate 可能比 entry 本身更决定成败

## 3. 为什么和当前项目有关
这条线和当前 desk 很对口，因为它补的是一类**可直接落地的趋势 raw alpha 壳**，而不是又一个只能当 shared gate 的旁支：

- 对 `5m/15m` 研发，它提供了一个清楚的母信号：**先用更高一级周期确认“趋势在加速”，再决定短周期要不要追 breakout**。
- 对当前素材池，它补的是 **trend / momentum / breakout** 族里更完整的一支：不是只看触发，而是把 `entry / exit / sizing / risk / cost` 一起写清楚。
- 对后续实盘组件拆解，它特别有价值的地方是：**单币 alpha 未必广谱有效，但 top-N ranking + correlation gate 很可能能救活一条本来“铺开就亏”的趋势 sleeve。**

## 3.5 策略拆解（必填）
- 方向属性：单资产顺势 / 趋势延续
- 基础 alpha：`20-bar breakout × 20/60-bar dual momentum × ATR expansion`
- regime：仅在 bull structure（`close > SMA20 > SMA50`）且 `ADX >= 18` 时激活
- filter / veto：若 `ATR/close` 不在高分位、或最近动量不足，则 veto；组合层再加 symbol ranking 与 rolling correlation cap
- sizing / risk：按每笔固定风险预算；初始止损取 `min(SMA20 - 1.1*ATR, signal-bar low)`；`+2.2R` 先减半；剩余走 `5*ATR` trail；`96 bars` time stop；研究期先按 round-trip `10~15bps` 摩擦测试
- cost：repo 显式写了 `4bps fee` 与 `5bps` 入场滑点；迁移到 crypto perp 时至少要做 `6/10/15bps` friction ladder

## 4. 可复刻的最小实验
- 数据源：Binance Spot / USDⓈ-M public klines
- 最小实验口径：`BTC/ETH/SOL/BNB`，先做 `1h` 母信号，再测 `15m` child trigger
- 一个可计算定义：
  - `regime = close > SMA20 > SMA50 and ADX >= 18`
  - `breakout = close > rolling_high(20)`
  - `mom20 = close / close[-20] - 1 > 3%`
  - `mom60 = close / close[-60] - 1 > 5%`
  - `atr_expansion = ATR/close >= rolling_percentile_55(120)`
  - 满足时下一根开盘做多；止损 / partial / trailing / time stop 按上面骨架执行
- 最该先看：
  1. `post_cost_return_per_trade`
  2. `PF / max drawdown / positive-asset-ratio`
  3. `all-universe` vs `top1/top2 ranking` vs `BTC/ETH-only`

## 4.5 下一步怎么测
1. **先做 desk 版二层结构**：把 `1h` 当母信号，`15m` 只负责更细的 breakout trigger，看是不是比直接在 `15m` 裸追更稳。  
2. **把固定 `3%/5%` 阈值改成 ATR-normalized 或 rolling percentile**，避免不同币波动不可比。  
3. **做 top-N ranking / correlation gate A/B**：比较“全铺开”与“只做 strongest 1~2 个币”，验证组合层到底救不救 alpha。  
4. **补 friction ladder**：`6 / 10 / 15 bps` 三档，确认这条线是不是只在低费率 / maker-ish 执行下才成立。  
5. **扩到 perp 与 majors-only universe**：优先 `BTC/ETH/SOL`，避免先被边缘币的高噪音拖垮。

## 5. 风险与保留意见
- 当前 portability probe 说明“可迁移思路存在”，不等于已经证明“广谱可实盘”。单币结果分化很大，说明它不是闭眼可铺的 broad trend alpha。
- 这条线的 repo 原始时间框架更高，直接压到 `15m` 后容易让噪音放大；所以更合理的读法是 **`1h` 母信号 + `15m` 子执行**，而不是把 `15m` 裸信号抬成主策略。
- 如果不加 ranking / correlation gate，趋势腿经常会“同时买到高度相关的一篮子”，回撤会被同步放大。

## 6. 来源
- **Author / Year / Title / Venue**：`azuzxx9-jpg` (2026), *quant-trade-system-v1*, GitHub repository
- **DOI**：N/A
- **Readable URL**：https://github.com/azuzxx9-jpg/quant-trade-system-v1
- **Repo URL**：https://github.com/azuzxx9-jpg/quant-trade-system-v1
- **关键源码**：
  - `src/strategies/trend_long.py`
  - `src/portfolio.py`
  - `main.py`
- **公开数据源**：Binance public klines（公开可得、分钟/小时级更新、可直接映射 `15m/1h` 最小实验）