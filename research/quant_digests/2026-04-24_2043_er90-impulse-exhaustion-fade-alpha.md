# 别把 Harvest 里的 `ER-90` 只读成“高胜率口号”：对 short-cycle crypto desk，更该先拆的是「短时 ATR impulse exhaustion × RSI5 extreme × failure-to-extend fade」这条 mean-reversion raw alpha 壳
- 时间：2026-04-24 20:43 UTC
- 类型：GitHub repo source audit（`README.md` + `strategies/er90.py` + `core/models.py` + `ml/base_strategy.py`）
- 主题类型：raw alpha
- 基础 alpha：短时过度冲击后的衰竭反转。先找 `5m`（必要时退化到 `1h`）里最近 `2h` 的快速单边 impulse，再用 `RSI(5)` 极值、量能冲高回落、以及“不再创新高/新低”的 failure-to-extend 结构，去做下一段回归。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / single-asset / mean-reversion / exhaustion / impulse / atr / rsi5 / failure-to-extend / volume-spike-decay / btc / eth / 5m / 15m / 1m / repo / cost / risk
- 证据类型：repo source audit

## 1. 这次看了什么
这次看的是 **GareBear99 (2024), `Harvest — Multi-Timeframe Crypto Trading System`** 里的 `strategies/er90.py`。

这个仓表面上很像“多引擎 + 大量生产就绪文档”的整套交易系统，但对当前 desk 更值得单拎出来的，不是它的系统包装，而是里面这条相对少见、而且确实适合短周期实验的 **ER-90 / Exhaustion Reversion** 线。

它不是去追趋势，也不是单纯做 RSI 超买超卖；它真正想抓的是：

**短时间内走得太急、成交量先冲后衰、而且价格已经开始“推不动了”的那一小段衰竭反转。**

这比再补一个“EMA 对齐 + MACD 确认”的 trend 壳，更符合这轮你希望优先补的 `mean reversion / raw alpha` 方向。

## 2. base alpha 先说清楚
这篇东西的 **base alpha 是清楚的**：

**短时单边冲击后的衰竭回归（exhaustion reversion）。**

翻成人话：
- 价格先在很短时间里冲得过快；
- 情绪和追单把 `RSI(5)` 顶到极端；
- 但最新几根 K 已经没有继续刷新极值，说明“最后一把力气”开始耗尽；
- 于是押注下一段不是继续加速，而是先回一段。

所以它是标准的：
**single-asset / mean-reversion / exhaustion-fade raw alpha**。

不是 overlay，不是纯 filter，也不是“用 RSI 解释行情”的附属模块。

## 3. 上游代码到底写了什么

## 3.1 设计意图：先找“冲得太快”的那一下
`er90.py` 的文档字符串把信号写得很明确：
- 最近 `< 2h` 内价格 impulse 达到 `1.5~2.0 × ATR`
- `RSI(5)` 极端
- volume spike 后转弱
- failure to extend high / low

也就是说，作者不是在做“便宜就买、贵了就空”的平庸反转，而是在找 **冲刺末端**。

## 3.2 但实际源码比注释更宽松
真正值得 desk 注意的是：**实现代码比口头描述更宽松。**

在 `core/models.py` 里，默认参数已经被放松到：
- `er90_impulse_atr_min = 1.0`
- `er90_rsi_upper = 65`
- `er90_rsi_lower = 35`
- `er90_max_trades_per_day = 3`

而 `er90.py` 的实际 `check_entry()` 里，更关键的问题是：
- 代码确实计算了 `impulse`
- 也计算了 `volume_spiked / volume_declining`
- 也计算了 `failed_to_extend_high / low`
- **但当前版本并没有把这些条件真正硬性并入最终入场判定**

最终入场逻辑被简化成了：
- `rsi_signal > upper` 且 `rsi_1h > 50` → `SHORT`
- `rsi_signal < lower` 且 `rsi_1h < 50` → `LONG`

也就是说：
**代码里的“真正可执行 alpha”已经退化成“短周期 RSI 极值 + 1h 同向背景”的反转壳；而 impulse / volume / failure-to-extend 更像是作者原本想保留、但暂时没有真正接上的 admission 层。**

这点很重要，因为它决定了我们该怎么读这份材料：
- 不要把 README / 注释里的完整故事，直接当成已经被代码严格实现；
- 但也不要因此把它整份丢掉——因为它依然给了一个很好的 **可补全 alpha 骨架**。

## 3.3 风险与仓位参数是完整的
尽管 entry 逻辑被简化了，风险层倒是写得相当完整：

默认配置（`core/models.py`）里：
- 杠杆：`10x ~ 20x`
- 单笔风险：`0.25% ~ 0.5%` equity
- 止盈：`0.8% ~ 1.2%`
- 止损：`0.6% ~ 0.9%`
- 每日最多亏损次数：`1`
- 每日最多交易次数：`3`

而 `_calculate_execution_intent()` 实际做的是：
- 取上述范围中值作为执行参数；
- 根据止损距离反推仓位；
- 再做 notional 上限和 liquidation buffer 校验；
- 如果爆仓价离 stop 太近，还会自动降杠杆。

这意味着它不是只有“信号点子”，而是已经把：
**entry / stop / tp / sizing / leverage safety** 这一整套落地结构写出来了。

## 4. 为什么和当前 desk 直接相关
这轮你明确要求：如果能补 `mean reversion / cross-sectional / relative value / stat-arb / pairs`，就不要继续困在固定趋势形态里。

ER-90 值得进研究池，原因有四个：

### 4.1 它补的是最近相对缺的 raw alpha 类型
最近 digest 已经连续有：
- pairs / stat-arb
- funding / carry
- EMA / MACD / pullback continuation
- Bollinger / RSI 传统均值回归

而 **“冲高衰竭 / 冲低衰竭”** 这种 **impulse-end exhaustion fade**，和普通 band-touch fade 不是一回事：
- 后者更偏“静态偏离回归”；
- 前者更偏“情绪冲刺末端的动力耗尽”。

这两类信号在短周期里经常长得像，但交易分布、持仓时长和最怕的市场状态并不一样。

### 4.2 它天然适合做 `5m` 主信号、`1m/3m` 子执行
ER-90 的核心叙事就是：
- 用 `5m` 看最近 `2h` 是否发生过快冲刺；
- 用更细粒度去抓“不再创新高/新低”的衰竭点；
- 然后吃一段短回归。

所以它非常适合：
- `5m` 做 alpha 识别
- `1m/3m` 做 child execution / early exit / stop tightening

这正好贴合你说的默认 desk 频段。

### 4.3 它可以和现有 trend sleeve 形成互补
趋势策略最怕“追在末端”；
ER-90 恰恰是去抓“末端已经开始推不动”的那一下。

所以它和现有 trend / breakout sleeve 有天然互补性：
- trend 在扩张段赚钱；
- ER-90 在扩张结束的第一段均值回归赚钱。

### 4.4 它给了一个很好的“代码与叙事错位”样本
这个仓对 desk 还有一个额外价值：

**它提醒我们，很多 repo 的 README 讲的是完整版故事，但真正跑的代码只实现了其中一半。**

这类材料不是没用，反而很适合我们这种 desk：
- alpha 胚子已经有了；
- 可执行壳也有；
- 缺的只是把 admission 层真正接回去。

## 5. 策略拆解（必填）
- 方向属性：single-asset / mean-reversion / exhaustion fade
- 基础 alpha：短时 price impulse 过快后，下一段衰竭回归
- 当前源码里的实际入场：`RSI(5)` 极值 + `1h` RSI 背景方向确认
- 更适合 desk 的完整版入场：`2h impulse / ATR` + `RSI5` 极值 + volume spike-decay + failure-to-extend
- sizing：按 stop distance 反推仓位，风险约束在 equity 的 `0.25%~0.5%`
- risk / execution：`0.8%~1.2%` take-profit，对应 `0.6%~0.9%` stop；每日 loss / trade cap；杠杆安全缓冲
- 推荐 desk 映射：`5m` 识别衰竭，`1m/3m` 执行进出与 tighter stop

## 6. 对 short-cycle crypto 的 desk 读法
这条线最值得学的，不是“RSI 极值可以反手”，而是下面这句更精确的话：

**不是所有极值都该反；更该反的是“刚冲完、量能开始掉、价格也推不出新极值”的那种极值。**

把它拆开，其实是四层：
1. **速度层**：先确认最近涨/跌太快；
2. **拥挤层**：RSI 已到极端，说明追单已经很满；
3. **衰竭层**：量能回落、价格不再创新极值；
4. **风控层**：只吃第一段回归，不赌大级别反转。

如果只保留第 2 层，策略就很容易变成“逆势硬接刀”；
如果把 1 / 3 / 4 层补齐，它就更像一个可交易的短周期 raw alpha。

## 7. 可复刻的最小实验
### 最小研究假设
**在 liquid crypto perp 上，最近 `2h` 内发生过快单边 impulse 的 `5m` 片段里，如果再要求 `RSI(5)` 极值 + failure-to-extend，是否能形成 fee 后仍存活的 exhaustion reversion raw alpha。**

### 最小实验口径
1. 标的：`BTCUSDT / ETHUSDT / SOLUSDT perp`
2. 主频：`5m`
3. 子执行：`1m` 或 `3m`
4. lookback：近 `90~180d`
5. impulse 定义：最近 `24` 根 `5m`（即 `2h`）内，净位移或极值位移达到 `1.0 / 1.5 / 2.0 × ATR(14)`
6. exhaustion admission：
   - 做空：`RSI(5) > 65/70/75`，且最近 `2~3` 根 K 没有继续创新高
   - 做多：`RSI(5) < 35/30/25`，且最近 `2~3` 根 K 没有继续创新低
7. volume admission：上一根 volume 明显放大，当前根 volume 开始回落
8. 出场：
   - 第一版先用 repo 的固定 bracket：`TP 0.8~1.2% / SL 0.6~0.9%`
   - 第二版改成“回到 EMA9 / VWAP / 短均值就平”
9. 成本：先跑单边 `2 / 4 / 6 / 10 bps` friction ladder

### 第一轮先看什么
- fee 后 Sharpe / PF / maxDD
- 平均持仓 bars
- 趋势日 vs 震荡日表现
- `BTC / ETH / SOL` 是否风格一致
- 加上 failure-to-extend 后，hit rate 是否明显提升

## 8. 下一步怎么测
1. **先把 repo 当前“宽松版”逻辑原样复刻**：
   - `RSI(5)` 极值
   - `1h` RSI 背景
   - 固定 bracket exit
   先确认最朴素可执行版本到底有没有 edge。

2. **再把作者注释里提到、但代码没真正接上的 admission 层补回去**：
   - impulse ≥ `N × ATR`
   - volume spike then decay
   - failure-to-extend

3. **做 4 组递进对照**：
   - A：只有 RSI 极值
   - B：RSI 极值 + 1h 背景
   - C：B + impulse filter
   - D：C + failure-to-extend + volume-decay

4. **把 exit 分成两类单独测试**：
   - 固定 `TP/SL bracket`
   - 均值回归型 exit（回 EMA / VWAP / 中轨）
   因为 ER-90 的核心不一定是“大止盈”，更可能是“只吃第一段回归，快进快出”。

5. **如果 `5m` 成立，再往 `3m/1m` 压缩执行，而不是直接把 alpha 本体粗暴搬到 `1m`。**

## 9. 风险与保留意见
- 这份材料最值得留的，是 alpha 结构；不是它对 win-rate 的口头宣称。`er90.py` 注释里写“85-92% win rate”，但这不能当作已验证事实。
- 当前实现与注释存在明显错位：真正执行逻辑比叙事更简化，这意味着 repo 结果如果好，未必来自作者声称的那整套 exhaustion 机制。
- 这类策略最怕“强趋势里极值继续极值”；因此第二轮实验必须单独测 trend regime 伤害，而不是只看全样本平均。
- 高杠杆是部署选择，不是 alpha 本体。对 desk 来说，应先验证 **不加高杠杆时信号本身是否过线**。

## 10. 一句话总结
**Harvest 里真正值得 desk 吸收的，不是 ER-90 那句“高胜率反转”口号，而是这条很适合 `5m -> 1m/3m` 最小实验的 raw alpha 骨架：先找短时冲刺，再找衰竭证据，最后只吃第一段回归。**

## 11. 来源
- Author / Year / Title / Venue
  - GareBear99. (2024). *Harvest — Multi-Timeframe Crypto Trading System*. GitHub repository.
  - Focused component: `strategies/er90.py` (`ER-90` / Exhaustion Reversion)
  - Venue: GitHub
  - DOI：无
  - Readable URL：https://github.com/GareBear99/Harvest
  - Repo URL：https://github.com/GareBear99/Harvest
- Key source files used
  - README：https://raw.githubusercontent.com/GareBear99/Harvest/main/README.md
  - ER90 source：https://raw.githubusercontent.com/GareBear99/Harvest/main/strategies/er90.py
  - Config / risk params：https://raw.githubusercontent.com/GareBear99/Harvest/main/core/models.py
  - Base strategy defaults：https://raw.githubusercontent.com/GareBear99/Harvest/main/ml/base_strategy.py
