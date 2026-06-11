# 别把这份 2026 新 repo 只读成“布林带网格模拟器”：对 crypto short-cycle desk，更该先拆的是「deep-quote BB fade × inventory-UNWIND state machine」这条完整 raw alpha 壳——但公开数据最小快检提示：它更像可拆件母板，不是当前优先上线候选
- 时间：2026-04-15 09:58 UTC
- 类型：2026 GitHub 新 repo source audit（GitHub API metadata + `README.md` + `config.py` + `strategy.py` + `portfolio.py` + `monitor.py`）+ Binance USDⓈ-M `15m/1h` 近 `180d` public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：**在 1h Bollinger 宽度推导出的极深报价区外侧分层挂 maker 反转单，成交后不要求价格回到起点，只要求先回一口气；若库存累积过深，则切到 15m `UNWIND` 模式只做去库存。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / mean-reversion / maker / market-making / single-asset / bollinger / deep-quote / inventory-skew / unwind-state-machine / dual-timeframe / binance-perpetual / 15m / 5m / 3m / 1m / repo / public-data / cost / risk
- 证据类型：开源 repo 工程实现 + 公共行情最小便携性快检；**不是**论文级跨样本统计结论，也不是带真实盘口成交回放的 execution study

**先回答 base alpha：这篇东西的 base alpha 不是“布林带碰上下轨就反转”那么简单，也不是“邮件监控器”。它真正的交易母板是：先把挂单放到一个非常深的局部偏离区，赌极端扩张后先回摆一段；如果回摆没来、库存越积越多，就用更快时间框架进入去库存模式。**

## 1. 这次为什么看它
这份 repo 是 `2026-04-12` 刚创建、`2026-04-14` 仍在更新的新仓库，定位很明确：
- 只用 Binance Futures 公共 K 线；
- 不下真实单，只做 20 个 USDM perpetual 的 paper-trading / virtual portfolio；
- 策略主线是 `NORMAL (1h)` + `UNWIND (15m)` 的双时间框架 Bollinger grid；
- 引擎会跟踪虚拟多空库存、反向 TP 挂单、库存偏移、状态切换，并通过邮件发组合摘要。

它跟我们前面 intake 过的 `martin-binance` 同属单资产均值回归 / inventory shell 家族，但又不是完全一回事：
- `martin-binance` 更像 **bounded-bounce reverse-grid × trend veto**；
- 这份 repo 更像 **deep-quote market-making shell × inventory-unwind state machine**。

所以它值得写，不是因为“又一个 grid”，而是因为它把**库存管理和去库存状态机**写得很完整，而且代码里还暴露出一个很关键的 desk 级事实：**README 对策略几何形状的描述，和实际代码不是一回事。**

## 2. 代码里真正的策略几何：不是“在上下轨挂单”，而是在更深的位置挂单
### 2.1 NORMAL 模式的实际报价位置
`strategy.py` / `portfolio.py` 里给出的公式非常清楚：

- `bw = bb_upper - bb_lower`
- `bw_pct = bw / mid`
- `inner = F * bw_pct`
- `outer = max(bw_pct/2, inner*2)`
- 冻结参数里 `F = 1`, `num_layers_calc = 20`, `L = 4`

于是 flat inventory 时：
- `inner = bw_pct`
- `outer = 2 * bw_pct`
- `step = bw_pct / 19`
- 4 个 active layer 实际 offset 是：
  - `1.0000 * bw_pct`
  - `1.0526 * bw_pct`
  - `1.1053 * bw_pct`
  - `1.1579 * bw_pct`

而这份 repo 的 NORMAL BB 设置是：
- 上轨：`mid + 2.3σ`
- 下轨：`mid - 1.7σ`
- 所以总带宽 `bw = 4.0σ`

把两者合在一起翻成人话：

> 它的首层买单/卖单并不在 `-1.7σ / +2.3σ` 那两条带上，而是在**大约 ±4σ** 附近；后 3 层还更深，约到 **±4.63σ**。

也就是说，README 里那张“上轨卖、下轨买”的直观图，对 desk 来说是不够准确的。**真实代码挂的是比带边更远的 deep quotes。**

### 2.2 一个更关键的细节：`2.3 / 1.7` 的非对称，在 NORMAL 初始挂单里几乎没起到 README 宣称的作用
repo 自己在 `strategy.py` 注释里说：
> lower band 更靠近中轨，所以 buy orders 会在更小跌幅下触发。

但从代码公式看，flat inventory 的 NORMAL 挂单只吃 `bw = upper - lower`，而 `2.3 + 1.7 = 4.0`，和对称 `2.0 + 2.0 = 4.0` 的总宽度一样。

因此至少在 **flat inventory 的 NORMAL 初始网格** 下：
- `2.3/1.7` 不会把买单往现价方向拉近；
- 它不会让 long side “更容易触发”；
- 它真正影响更明显的地方，反而是 `UNWIND` 模式下的目标位，以及 README 的叙事呈现。

这个发现很重要，因为它直接改变我们对这条 alpha 的理解：

> 它不是“偏多友好的非对称布林带抄底壳”，而更接近一个**总宽度固定、深外侧报价、库存累积后再切换去库存**的状态机策略。

## 3. 完整策略壳长什么样
### 3.1 进场：deep quote 分层接极端偏离
- 每边 4 层 active orders；
- 每层默认 `$1000` notional；
- `num_layers_calc = 20`，但只启用最靠内的前 4 层；
- `max_pos_mult = 15`，即总可承受头寸上限约为 `15 × unit_size`。

这不是“频繁小剥头皮”，而是：
- 平时很久没事；
- 真有大偏离才触发；
- 一旦开始触发，策略会把库存逐步摊开。

README 自己也承认两年回测里**平均每对约 0.4 fills/day**，说明它故意把报价挂得很远，不是高频小价差回补。

### 3.2 出场：counter TP + 自动轧差
每当一个非 close order 成交：
- 会按当前带宽与 `counter_mult = 2.0` 放置反向 TP；
- `spread = max(counter_mult * offset_now, 4 * maker_fee)`；
- maker fee 固定写成 `2bps`；
- long/short 库存可以自动 `try_offset()` 做内部轧差。

翻成人话：

> 它不是“等价格完全回到起点再说”，而是把每次成交都转成一个新的库存片段，再给这片库存挂一个能覆盖成本、并尽量吃到局部回摆的反向 TP。

### 3.3 风控：不是先挡住趋势，而是先让你进，再在库存过深时强制去库存
repo 的硬风控核心不在 admission gate，而在状态机：
- 当 `|net_units| >= E = 6` → 进入 `UNWIND`
- 当 `|net_units| < X = 3` → 退出 `UNWIND`

`UNWIND` 模式下：
- 不再继续正常双边铺网格；
- 切到 `15m BB(120, ±2.0σ)`；
- 仅挂 close-only orders，把库存往 `mid / band edge` 方向卸。

这和 `martin-binance` 的逻辑差异非常明显：
- `martin-binance` 更强调**趋势 veto，尽量别开错第一枪**；
- 这份 repo 更强调**开了也没关系，仓位太深时切换到专门的去库存模式**。

## 4. 最小便携性快检：recent Binance perp 上，这个壳的“先回一口气”并不算漂亮
我补了一个非常克制的 public-data probe：
- 标的：`BTCUSDT / ETHUSDT / SOLUSDT`
- 数据：Binance USDⓈ-M 公共 `15m` / `1h` K 线
- 窗口：近 `180d`
- 事件定义：当 `15m` bar 触到 repo 公式生成的 **L0 deep quote**（不是 README 图示带边）
- 聚类：`8h` 内连续触发算同一 episode
- 检查：后续 `8h / 24h` 内，是否至少回到对应 `1h` 带边；以及 `24h` 内是否回到 `mid`

先强调：
- 这**不是**完整 PnL backtest；
- 也**不是**严格复刻 repo 的逐层成交 / TP / UNWIND 全流程；
- 它只是回答一个最基本问题：**这么深的单子打到以后，近期市场里“先回一口气”的统计基础够不够。**

### 4.1 结果摘要
**BTCUSDT**
- long 侧：`7` 个 episode；`24h` 内回到对应下轨仅 `43%`；回到中轨 `0%`
- short 侧：`4` 个 episode；`24h` 内回到上轨 `25%`；回到中轨 `25%`

**ETHUSDT**
- long 侧：`9` 个 episode；`24h` 内回到下轨 `33%`；回到中轨 `11%`
- short 侧：`8` 个 episode；`24h` 内回到上轨 `12.5%`；回到中轨 `12.5%`

**SOLUSDT**
- long 侧：`10` 个 episode；`24h` 内回到下轨 `30%`；回到中轨 `0%`
- short 侧：`6` 个 episode；`24h` 内回到上轨 `83%`；回到中轨 `33%`

### 4.2 这组结果说明什么
这组结果至少说明三件事：

1. **这套报价真的很深。**
   近 `180d` 三个主流币总共也没多少次 episode，和 README 里“fill 不频繁”是同方向的。

2. **recent 长侧 bounce 质量并不强。**
   至少在这 180 天里，BTC/ETH/SOL 的 long 侧 episode 后，`24h` 内连“先回到 1h 下轨”都不算稳，更别说回中轨。

3. **short 侧在个别币上反而更像样。**
   尤其 SOL 这段样本里，short 侧“打到深卖单后再回到上轨”的概率明显高于 long 侧。也就是说，这条壳的可交易性可能比 README 暗示的“对称双边都可做”更偏**择币 + 择边**。

我的 desk 级翻译是：

> 这条策略最近不是“深跌就弹、深涨也回”那种双边通吃结构；更像一个**极深报价库存壳**，要么靠更完整的逐层 TP / UNWIND 才能活，要么就必须做成择边版，而不能直接按 README 的双边直觉照抄。

## 5. 它和 `martin-binance` 的关系：同家族，但这条更适合拆组件，不适合当当前主力母板
### 5.1 共同点
两者都属于：
- 单资产短周期均值回归；
- maker-first / inventory-based；
- 不是赌完全反转，而是赌“先回一口气”；
- 都把 TP、库存、网格重建写成了完整交易壳。

### 5.2 关键差异
**`martin-binance`** 更像：
- reverse-grid bounce shell
- adaptive width
- fee-aware TP
- **趋势 veto 是主角之一**

**`crypto-grid-trading-sim`** 更像：
- deep quote BB fade
- inventory skew
- **UNWIND 去库存状态机**
- public-kline paper simulation / email monitor infra

### 5.3 如果只能保留一个优先 intake
就当前证据强度和 recent portability 来看：

> **`martin-binance` 仍然是更强的“主 digest / 主母板”；这份新 repo 更适合作为“库存去化状态机 + 代码审计反例”补进研究池。**

原因很简单：
- `martin-binance` 至少把“什么时候别开新逆势库存”这个 admission 问题写清楚了；
- 这份新 repo 更像“先进、再靠状态机善后”；
- 在 recent 主流 perp 样本里，后者的 long 侧 bounce 统计基础并不漂亮。

## 6. 这份 repo 最值得复用的，不是 README 里那张图，而是这 4 个可拆件
### 6.1 `NORMAL → UNWIND` 双模式状态机
这是它最有价值的部分。
很多均值回归壳死，不是因为第一枪一定错，而是因为：
- 错了以后还继续按同一逻辑加；
- 没有一个明确的“从赚钱模式切到去库存模式”的开关。

这份 repo 把那个开关写得非常硬：库存过深就换挡。这个思想很值得移植到：
- reverse-grid
- pairs spread fade
- basis z-score fade
- maker inventory shell

### 6.2 `try_offset()` 的多空内部轧差思路
它的虚拟持仓不是简单净仓位，而是显式维护：
- `long_size / long_avg`
- `short_size / short_avg`
- 自动 offset 后把 PnL realize 掉

这对我们做多腿库存管理、或将来做 spot/perp 两腿 inventory accounting，都很有参考价值。

### 6.3 `orders_fingerprint()` / changed-pair digest 这类研究监控基础设施
虽然这不属于 base alpha，但对内部研究很实用：
- 哪些 pair 真有结构变化；
- 哪些只是轻微重报价，不值得 spam；
- 如何把多品种虚拟 book 压成一封能读的 digest。

### 6.4 明确暴露“叙事 ≠ 代码”的审计价值
这可能是本次最值得记住的 lesson：

> README 说“在布林带上下轨挂单”，但代码实际挂的是更深的 `±4σ` 外侧区；README 说“lower band 更近所以更容易买到”，但 flat NORMAL 初始网格并不直接支持这个叙事。

这类 repo 很适合做 source audit，因为它提醒我们：**开源策略最危险的不是参数差一点，而是你以为自己复刻了 A，实际上代码干的是 B。**

## 7. 当前 verdict
### 7.1 这条线还值不值得进研究池？
值，但位置要摆对。

我的判断是：

> 它值得作为 **raw alpha 壳 + inventory overlay 母板** 进入研究池，但**不该**被当作当前优先级最高的单资产 MR 主线候选。

### 7.2 为什么不把它放更高优先级
因为它当前暴露出 3 个明显问题：
1. **真实挂单位置比叙事深得多**，导致触发稀少；
2. **recent long-side bounce 不够好看**；
3. **没有像 `martin-binance` 那样把 trend-veto 前置到 admission 层。**

### 7.3 它更适合怎样的归宿
我更愿意把它放进下面这个篮子：
- **主标签**：`raw alpha shell / inventory-unwind overlay`
- **用途**：给已有 MR / maker / pairs 库存壳补一个“何时切换到去库存模式”的结构模板
- **不是**：下一条最优先直推 production 的 standalone alpha

## 8. 下一步怎么测
### A. 先做一个更 desk-friendly 的变体，而不是原样照抄
最值得测的是下面这个变体：
- 报价位置不要直接从 `±4σ` 起跳；
- 改成真的围绕 `band edge / 2.0σ / 2.5σ` 分层；
- 保留 `UNWIND` 状态机；
- 加 `trend veto`，不要等到库存积深了才认输。

### B. 做三组对照
1. **repo 原版深报价**
2. **带边附近报价 + UNWIND**
3. **带边附近报价 + trend veto + UNWIND**

如果第 3 组明显比第 1 组好，就说明这份 repo 最有价值的不是它现在的挂单几何，而是**去库存状态机这个组件**。

### C. 明确加 execution realism
这条线尤其要补：
- maker-only / mixed / taker-worst-case friction ladder
- K 线穿价不等于真实成交：要加 missed fill / queue position 假设
- 波动扩大时 spread widening 与滑点恶化

### D. 值得先看的方向：short-only pocket
从 recent `BTC/ETH/SOL` 最小快检看，至少某些样本窗口里，**short 侧比 long 侧更像样**。因此很值得做：
- `short-only` 版本
- 或 `long/short asymmetric admission`
- 或只在 funding / regime / market state 对某一边更友好时放开深报价

## 9. 来源
1. **lindkkk (2026). _crypto-grid-trading-sim_. GitHub repository.**  
   Venue: GitHub  
   DOI: N/A  
   Readable URL: <https://github.com/lindkkk/crypto-grid-trading-sim>  
   Repo URL: <https://github.com/lindkkk/crypto-grid-trading-sim>

2. **`README.md` for `crypto-grid-trading-sim`.**  
   Readable URL: <https://raw.githubusercontent.com/lindkkk/crypto-grid-trading-sim/main/README.md>

3. **`config.py` / `strategy.py` / `portfolio.py` / `monitor.py` for `crypto-grid-trading-sim`.**  
   Readable URLs:  
   - <https://raw.githubusercontent.com/lindkkk/crypto-grid-trading-sim/main/config.py>  
   - <https://raw.githubusercontent.com/lindkkk/crypto-grid-trading-sim/main/strategy.py>  
   - <https://raw.githubusercontent.com/lindkkk/crypto-grid-trading-sim/main/portfolio.py>  
   - <https://raw.githubusercontent.com/lindkkk/crypto-grid-trading-sim/main/monitor.py>

4. **Binance USDⓈ-M public klines (`BTCUSDT/ETHUSDT/SOLUSDT`, `15m/1h`, recent 180d) portability probe, reproduced locally on 2026-04-15 UTC.**  
   Venue: Binance Futures public market data  
   DOI: N/A  
   Readable URL: <https://fapi.binance.com/fapi/v1/klines>
