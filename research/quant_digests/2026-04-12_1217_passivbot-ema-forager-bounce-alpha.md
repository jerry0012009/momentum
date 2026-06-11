# 别把 Passivbot 只读成“自动挂网格机器人”：对 short-cycle desk，更该先测的是「EMA-band overshoot × trailing retrace × volatile-alt forager」这条 raw alpha

- 时间：2026-04-12 12:17 UTC
- 类型：2020-2026 GitHub repo source audit（GitHub API metadata + `README.md` + `docs/configuration.md` + `docs/backtesting.md` + `configs/examples/default_trailing_grid_long_npos10.json` + `src/config/schema.py`）+ Binance USDⓈ-M `15m/5m` public portability probe
- 主题类型：raw alpha
- 基础 alpha：**单资产 downside overshoot 之后的短时回摆 / bounce capture**；repo 真正值得 desk intake 的，不是“会不会自动挂单”，而是 **价格跌穿多条 EMA 构成的下沿带后，等待一小段 retrace 再做 maker-first 回摆收租** 这条 contrarian / mean-reversion alpha，外加 `forager` 只挑高波动币、`wallet exposure / unstuck / HSL` 做风险壳。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/mean-reversion/single-asset/market-making/ema-band/trailing-retrace/forager/volatile-alt/maker-first/grid/perpetual/binance/bybit/1m/5m/15m/repo/public-data/cost/risk
- 证据类型：成熟高信号开源 repo + 明确配置语义 + 公共数据 portability probe

## 1. 这次看它，不是为了再收一张“网格 bot 教程”
先回答一句：**这篇东西的 base alpha 是什么？**

> **base alpha = EMA-band overshoot 之后的短时回摆（bounded bounce / mean reversion），而不是 generic automation framework。**

如果这句答不清，Passivbot 最多只能算执行层或风险壳；但这轮其实答得清：

- `README` 直接写了它**不预测趋势、不跟趋势**；
- 它把自己定义成 **contrarian market maker**；
- 主策略逻辑就是：
  1. 先等价格偏离本地平衡区；
  2. 分层接库存；
  3. 只要回一小口就用 fee-aware take-profit 卸货；
  4. 如果行情一直不回，就靠 exposure cap / unstuck / HSL 控尾部。

翻成人话：

> **它赌的不是“V 字大反转”，而是“跌太急以后，先回一口气”的那段短回摆。**

这就是 raw alpha，不是 filter，也不是纯 execution plugin。

## 2. 为什么这轮值得看它
这轮继续补它，有两个原因：

1. **它是 repo-based 且工程完成度很高。**
   GitHub API 元数据显示：
   - repo：`enarjord/passivbot`
   - 创建：`2020-12-11`
   - 最近 push：`2026-04-11`
   - `1936` stars / `643` forks
   - 不是“一次性回测截图仓库”，而是持续维护中的成熟工程。

2. **它补的是当前素材池里较少见的一类 raw alpha 壳。**
   我们最近已经 intake 了很多：
   - pairs / stat-arb
   - funding / basis / carry
   - cross-sectional loser-bounce
   - order-flow / microstructure

   但像这种：
   - **单资产**
   - **maker-first**
   - **portfolio-style volatile forager**
   - **带明确 exposure / unstuck / HSL 风控语义**

   的成熟 mean-reversion 母板，仍然值得收一张。

## 3. 主来源与最有用的地方
### 3.1 主来源
- **enarjord (2020-2026)**
- **Title:** *Trading bot running on Bybit, Bitget, OKX, GateIO, Binance, Kucoin and Hyperliquid*
- **Venue:** GitHub
- **Readable URL / Repo URL:** <https://github.com/enarjord/passivbot>

本轮实际读到的关键材料：
- `README.md`
- `docs/configuration.md`
- `docs/backtesting.md`
- `configs/examples/default_trailing_grid_long_npos10.json`
- `src/config/schema.py`

### 3.2 README 给的最关键一句
README 里最重要的不是“支持哪些交易所”，而是这句自我定义：

> **It does not try to predict future price movements ... Rather, it is a contrarian market maker.**

这句话非常关键，因为它直接把题目从：
- “有没有趋势预测模型”

拉回到：
- **“价格短时偏离以后，做被动反手库存提供者，能不能吃到回摆补偿？”**

这正是我们 desk 能直接拆的 raw alpha。

## 4. repo 里真正值得搬走的，不是“网格”二字，而是这 4 个结构件
## 4.1 EMA band 是 admission anchor，不是装饰
`docs/configuration.md` 明确写了：

- `ema_span_0`, `ema_span_1` 的单位都是 **分钟**；
- 额外再算一个几何均值 EMA；
- 三条 EMA 一起构成：
  - `ema_band_lower = min(emas)`
  - `ema_band_upper = max(emas)`

也就是说，repo 的 admission 不是“跌 x% 就买”这么粗。
它先定义了一个**动态平衡区**，然后问：

> **当前价格是不是已经跌穿这条下沿带 enough？**

默认 long example 里的关键参数是：
- `ema_span_0 = 770`
- `ema_span_1 = 210`
- `entry_initial_ema_dist = 0.0097`
- `entry_grid_spacing_pct = 0.033`
- `entry_grid_spacing_volatility_weight = 2.4`

翻成人话：

> 不是固定离均线 `1%` 就永远一样地接，而是 **EMA 锚 + 波动加权 spacing** 一起决定“这次跌得算不算够深”。

## 4.2 trailing entry 的本质，是“先别接飞刀，等它回一小口”
README 对 trailing entry 的解释很直白：

- 价格先越过某个 threshold；
- 之后再出现一定比例的 retracement；
- 这时才真正下 re-entry order。

这对 desk 特别重要，因为它比很多 naive mean reversion 更诚实：

- 不是一碰深偏离就抄；
- 而是要看到**至少一点点回摆迹象**，才让库存开始展开。

所以它的第一句可交易翻译其实是：

> **deep overshoot + small retrace > pure deep overshoot**。

## 4.3 close 逻辑赌的不是大反转，而是“小回一口就够”
默认 long config 里：
- `close_grid_markup_start = 0.00634`
- `close_grid_markup_end = 0.0094`
- `close_grid_qty_pct = 0.51`
- 还可配 `close_trailing_*`

也就是说，repo 的核心不是“等它回到原点”，而是：

> **只要库存均价附近能反弹一点点，就先主动把货卸掉。**

这也是它和很多“均线回归”课件的区别：
- 不是追求大波段；
- 是追求**高频次、小幅度、maker-first 的 bounce harvest**。

## 4.4 Forager 决定了：这条 alpha 默认不该在所有币上一视同仁地打
README 直接写了 `Forager`：

- 用最近 `1m` candles 的 normalized relative range 定义 volatility；
- 动态挑最 volatile 的 markets。

默认 long config 里也明确：
- `forager_score_weights.volatility = 1.0`
- `forager_volatility_ema_span = 225`
- `n_positions = 10`
- `total_wallet_exposure_limit = 1.25`

这点很重要，因为它直接告诉我们：

> **Passivbot 不是“看到 stretch 就在全 universe 全开”，而是更像只去最活跃、最容易给回摆的币上收租。**

这也是这轮 public probe 最后会得出的核心结论之一。

## 5. 风控不是附属品，而是这条 alpha 能不能活下来的必要条件
repo 的风控语义很完整：

- `total_wallet_exposure_limit`
- `risk_wel_enforcer_threshold`
- `risk_twel_enforcer_threshold`
- `unstuck_*`
- `hsl_*`（equity hard stop loss）

特别是 README 对 `unstucking` 的描述很 desk：

> 对长期卡住的库存，不是永远死扛，而是**分批小亏实现，把最接近当前价的 stuck inventory 优先卸掉**。

这说明什么？

说明 repo 作者非常清楚：
- alpha 本体是 bounce capture；
- 但真正的死法，是**单边趋势里库存越积越深**。

所以它从一开始就不是“只要均值回归就行”的天真模型，而是：

> **raw alpha + exposure governance + gradual damage control** 的完整策略。

## 6. public portability probe：把它压到 Binance perp `5m/15m` 后，哪里还能活？
本地 artifacts：
- `/root/clawd/jerry/momentum/reports/artifacts/literature/passivbot_trailing_grid_probe_2026-04-12_summary.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/passivbot_trailing_grid_probe_2026-04-12_asset.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/passivbot_trailing_grid_probe_2026-04-12_detail.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/passivbot_forager_alt_probe_2026-04-12_summary.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/passivbot_forager_alt_probe_2026-04-12_symbol.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/passivbot_forager_alt_probe_2026-04-12_detail.csv`

### 6.1 先说我怎么做的
我没有假装完整复刻 Passivbot，而是先做一版**desk-friendly honest port**：

- 数据：Binance USDⓈ-M perp 公共 `5m / 15m` K 线
- 区间：`2025-10-01` 到 `2026-04-12`
- 币种：
  - 广义 baseline：`BTC/ETH/SOL/BNB/XRP/DOGE`
  - forager alt pocket：`ETH/BNB/XRP/SOL`
- 15m 版把默认 `210 / 770 min` EMA 映射成约 `14 / 51` bars
- 信号：
  1. 价格 low 跌穿 `ema_band_lower`
  2. stretch 至少达到 `max(固定门槛, 波动倍数 × normalized range)`
  3. bar close 落在本 bar 上半区，近似“出现 retrace”
  4. 下一根 open 进场
- 出场：
  - 先用更 desk 化的固定 TP 代理：`+40 bps`
  - 最多持有 `2` 根 `15m`（约 `30m`）
- 成本：
  - 粗 maker round-trip：`8 bps`

注意：

> **这不是 full fill simulator。** 没有 queue priority、没有 partial fill、没有多档 inventory。它只是回答：把 Passivbot 的 base alpha 抽出来后，price-level 上有没有 first-pass portability。

### 6.2 先看坏消息：宽 universe 直译版不行
如果把它粗暴地压到 `BTC/ETH/SOL/BNB/XRP/DOGE` 六币宽 universe：

- `15m` baseline gross 平均约 **`-2.41 bps/笔`**
- maker 粗扣后约 **`-10.41 bps/笔`**
- `5m` 更差，maker 粗扣后约 **`-9.84 bps/笔`**

这说明：

> **Passivbot 的 alpha 绝不是“看到 stretch 就在所有主流币上无脑接”。**

也说明如果把 repo 只读成“反向网格机器人”，你会很容易做出一个负边际版本。

### 6.3 真正有信号的地方：volatile-alt forager pocket
当我开始更认真地保留 repo 的 `forager` 思路——
即：
- 不看全市场；
- 只看更高波动的 alt；
- 只做更深的 overshoot；
- 只在 retrace 更明显时接；

情况就变了。

#### Variant A：`alt4_balanced`
标的：`ETH/BNB/XRP/SOL`

规则：
- `stretch >= max(1.2%, 2.5 × vol)`
- `close_in_range >= 0.85`
- `TP = +40 bps`
- 最多持有 `30m`

结果：
- **`141` 笔**
- gross 平均约 **`+4.81 bps/笔`**
- 胜率约 **`68.1%`**
- 但 maker 粗扣后仍约 **`-3.20 bps/笔`**

这说明：

> **alpha 本体有，但还不够；必须更像真正的 forager。**

#### Variant B：`alt4_extreme`
再把 stretch 做深：
- `stretch >= max(1.5%, 3.0 × vol)`
- 其余相同

结果：
- **`56` 笔**
- gross 平均约 **`+13.66 bps/笔`**
- 胜率约 **`69.6%`**
- maker 粗扣后约 **`+5.65 bps/笔`**

这已经从“有 raw alpha 但费后不够”变成：

> **在 deep-stretch alt pocket 里，至少 price-level first pass 是费后可活的。**

#### Variant C：`alt4_extreme_top2vol`
如果进一步要求：
- 同时刻只做 `ETH/BNB/XRP/SOL` 里 **vol rank top-2** 的币
- 仍然要求 extreme stretch

结果：
- **`29` 笔**
- gross 平均约 **`+19.90 bps/笔`**
- 胜率约 **`79.3%`**
- maker 粗扣后约 **`+11.88 bps/笔`**

但要诚实说：
- 样本已经不大；
- maker fill 假设仍偏理想化；
- 这个结果更适合被读成 **“值得进下一轮 replication”**，还不是 production verdict。

### 6.4 各币分布说明了什么
在更深的 forager pocket 里：
- `XRP / ETH / BNB / SOL` 都能给出正的 gross 边际；
- `BTC` 反而不亮眼；
- `DOGE` 在宽 universe 里经常拖后腿。

这和 repo 的自述高度一致：

> 它不是“majors 通吃的均值回归公式”，更像**高波动 alt inventory harvest shell**。

## 7. 这轮最重要的结论
这轮最值钱的不是“Passivbot 能不能直接照搬”，而是这 3 句：

### 结论 1
**base alpha 很清楚：就是 EMA-band overshoot 后的短时回摆，不是 generic bot infra。**

### 结论 2
**宽 universe 的 naive port 明显不行；不保留 `forager` 思路，就会把 alpha 做死。**

### 结论 3
**真正可 intake 的，不是“全币反向网格”，而是「volatile-alt deep stretch × trailing retrace × maker-first TP」这个更窄、更深、更 honest 的版本。**

如果要给 desk 一个一句话落点，我会写成：

> **Passivbot 最适合 desk intake 的，不是全自动网格，而是 `15m` 父信号上的 volatile-alt deep overshoot bounce shell；`forager` 不是锦上添花，而是 alpha 本体的一部分。**

## 8. 对当前 desk，怎么落成一条完整策略
### 8.1 第一版建议先做 long-only
原因很简单：
- canonical example 本来就是 `default_trailing_grid_long_npos10`；
- 该配置里 short side `total_wallet_exposure_limit = 0`，本质上先把 short 关了；
- 对 crypto perp 来说，做 long-side bounce 通常比 short-side squeeze 更容易先做出稳定 first pass。

### 8.2 desk 版最小可执行 spec
**Universe**
- `ETH / BNB / XRP / SOL`
- 后续可加 `DOGE / AVAX / LINK` 做二轮扩展，但不要一开始就加

**Signal timeframe**
- `15m` 父信号
- `1m / 3m` 子执行

**Entry**
- 计算 `14 / 27 / 51` EMA band（15m 等价映射）
- 仅当：
  - `stretch >= max(1.2%~1.5%, 2.5x~3.0x vol)`
  - bar close 落在本 bar 上沿 `>= 85%`
  - 当前币在 alt universe 里是 realized-vol top-2 或 top-3
- 下一根开始挂第一层被动买单

**Sizing**
- 第一轮别照抄 full martingale
- 先做 `2~3` 层 capped ladder：
  - `1.0x / 1.25x / 1.5x`
- 单名义风险上限建议先压到：
  - `10%~12.5%` wallet exposure

**Exit**
- 第一档 TP：`+40 bps`
- 第二档 TP：`+63.4 bps`（对应 repo 默认 `close_grid_markup_start`）
- 超过 `30m` 未出清则主动减库存

**Risk**
- 不允许无限加层
- 同时开仓数先限制 `<= 2`
- 重新入场前必须经过 cooldown
- 一旦连续两次 deep layer 仍未 bounce，关闭该币当日 re-arm

### 8.3 这条线服务于哪个 raw alpha
它服务的是：
- **single-asset mean reversion**
- 更具体说，是 **inventory-style bounce capture**

而 `forager / HSL / unstuck / wallet exposure` 都是在保护这条 raw alpha，不是另一个主题。

## 9. 它和已有“reverse-grid / bounded-bounce”卡的区别
这张卡和一般 reverse-grid / martingale 卡不是一回事，它更强调：

1. **EMA band anchor**，不是只用一个静态百分比带宽；
2. **trailing retrace admission**，不是一碰深偏离就直接接；
3. **forager vol ranking**，不是对全 universe 一视同仁；
4. **portfolio-style exposure governance**，不是单币孤立回测。

也就是说，它更像：

> **短周期 maker-style mean reversion portfolio shell**

而不只是“另一个网格 bot”。

## 10. 我的判断
### 值得 intake 的部分
- `EMA band` admission
- `trailing retrace` 代替盲目抄底
- `forager` 只做 volatile alt pocket
- `maker-first + small bounce TP`
- `unstuck / HSL / wallet exposure` 风控语言

### 不建议直接照搬的部分
- 全 universe 通吃
- 无限层数 / 高杠杆加仓
- 过度乐观的 fill 假设
- 直接把 1m repo 原始逻辑无脑压到 5m 全币

### 当前 verdict
> **值得作为 raw alpha intake，但只应该 intake 它的“deep-stretch alt forager bounce”版本；宽 universe naive 版不合格。**

## 11. 下一步怎么测（最重要）
### A. 做真正的 maker fill honesty check
把这轮的 `+40 bps` TP 事件，改成：
- `1m` child-order replay
- queue-less optimistic fill
- queue-haircut conservative fill
- partial-fill capped fill

先回答：**这轮 `+5.65 ~ +11.88 bps/笔` 的 maker-net 还有多少能留下来。**

### B. 做 layer test，而不是只做单层事件研究
对 `alt4_extreme` 版本做：
- 1 层
- 2 层
- 3 层

比较：
- `TP hit rate`
- `time-to-flat`
- `deepest layer reached`
- `tail loss`

这会告诉我们：

> edge 到底来自 alpha 本体，还是只是来自更激进的 inventory averaging。

### C. 做 forager vs no-forager A/B
固定其他参数不动，只比较：
- 全 alt4 全做
- top-3 vol
- top-2 vol

如果 top-2 / top-3 明显优于全做，就说明：

> **forager 不是 overlay，而是这个 repo 里必须保留的 alpha 组成部分。**

---

### 一句话结论
> **Passivbot 最值得 desk intake 的，不是“自动网格”这个壳，而是「volatile-alt 上 deep EMA-band overshoot 后，等一小段 retrace 再用 maker-first TP 收 bounce」这条 raw alpha；不保留 forager，这条线大概率会被做成负边际。**
