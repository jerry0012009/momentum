# 别把这份 Binance 稳定币对 bot 只读成“零费率网格工具”：对 short-cycle desk，更该先保留的是「stablecoin micro-depeg fade × 1 tick take-profit」这条 raw alpha 壳
- 时间：2026-04-17 21:56 UTC
- 类型：2025/2026 GitHub repo source audit（`README.md` + `__main__.py` + `grid_gen.py` + `market_stats.py` + `order_manager.py` + GitHub API metadata）+ Binance Spot `FDUSDUSDC 1m` public-data portability probe（近 45d）
- 主题类型：raw alpha
- 基础 alpha：当稳定币对（这里是 `FDUSD/USDC`）短时滑到近 1 小时区间低位、出现轻微 micro-depeg 时，后面几分钟常有**回到中枢 / 弹回 1 tick** 的均值回复；交易上对应 **低位挂买 → 只吃第一跳反弹 → 很快走人**。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（repo 已给 grid、挂单、止盈、仓位随资金缩放、阈值 gate、fee guard；真实队列位置 / 吃单风险 / 容量还需二次审计）
- 主题标签：raw-alpha / single-asset / relative-value / stablecoin / micro-depeg / mean-reversion / maker / grid / one-tick-tp / fdusd / usdc / binance-spot / 1m / 3m / 5m / 15m / repo / public-data / cost / risk
- 证据类型：repo 源码 + Binance 公共行情最小迁移快检

## 1. 为什么这轮选它
这轮优先级不是再补一个解释型 filter，而是补一条 **base alpha 能一句话说清楚**、而且能直接落成完整策略壳的 raw alpha。

我最后选的是 GitHub 仓库 **wangshaofu / mm_bot**：
- 创建时间：2025-04-15
- 最近更新时间：2026-02-19
- stars：0
- 但不是空 README，它至少给了：grid 生成、市场振幅读取、阈值 gate、订单管理、fee guard、以及完整轮询主循环。

先把它翻成人话：

> **这不是“稳定币对可以做网格”的空话；它真正下注的是：当 `FDUSD/USDC` 这类稳定币对短时掉到局部低位时，后面几分钟经常会先弹回 1 个 tick 左右。**

所以它的本体不是 trend，也不是 funding carry，更不是跨 venue 套利；它就是一条很具体的 **stablecoin micro-depeg mean reversion raw alpha**。

## 2. repo 里真正有价值的部分是什么
### 2.1 base alpha 很清楚：买局部低位，只收第一跳
`grid_gen.py` 和 `__main__.py` 串起来后，repo 的真实逻辑并不复杂：

1. 用最近 `1h` 的 `15m` K 振幅估算当前可交易区间；
2. 在 `best_bid` 下方生成一串买单价格；
3. 价格分配不是均匀的，而是 **U-shaped**：两端挂得更密，中间也保留最小权重；
4. `order_manager.py` 只保留**最靠上的两个可用 grid level**；
5. 买单成交后，立刻把卖单挂在 `buy_price + step`，默认就是 **+1 tick**；
6. 同时用 `last_minute_price + 0.0002` 做 max-buy-threshold，避免价格已经抬高时继续追着挂。

这说明 repo 真正在做的事其实是：

> **抓“稳定币对短时偏离 → 很快回一格”这件事，而不是长期持有或大波段判断。**

### 2.2 它是完整策略壳，不只是信号
这份仓库最值得保留的，不是 `U-shaped` 这个词，而是它把完整壳给齐了：
- entry：在局部低位下方挂 maker buy
- exit：成交后固定 `+1 tick` 卖出
- sizing：总 grid 数随可用资金调整
- admission：价格超过阈值就不再挂
- risk：发现 maker/taker fee 非 0 直接停机
- execution：持续重排订单，只保留最上面的两层

这比很多“只有一个因子公式”的 repo 更适合 desk intake，因为它已经自然回答了：
- 怎么进
- 怎么出
- 什么时候不做
- 为什么必须低摩擦

### 2.3 它本质上是 maker-ish，不适合被误读成 taker alpha
repo 里最关键的安全护栏之一，是 `check_trading_fees()`：
- maker fee 或 taker fee 只要不是 `0`
- bot 就直接报警并退出

这其实已经把作者的真实判断写死了：

> **这条 edge 本来就薄，必须尽量站在 maker 一侧吃回弹；一旦改成正常 fee / taker 口径，很可能马上死。**

所以正确读法不是“又一个稳定币小网格”，而是：

> **一个对摩擦极端敏感的微观均值回复 raw alpha 壳。**

## 3. public portability probe：这条 alpha 在公开数据里还像不像活的
为了不把源码故事直接当结论，我补了一个很小但够用的 public-data probe。

### 3.1 快检口径
- 数据源：Binance Spot 公共 `FDUSDUSDC 1m klines`
- 样本：近 `45d`，共 `64,800` 根 `1m` bars
- 价格背景：均价约 `0.99963`，区间约 `0.9986 ~ 1.0025`
- 1 小时振幅的 `p95` 约 `0.0005`（约 `5` ticks）

我没有假装能从 K 线完整复盘真实挂单队列，而是只验证一句最核心的话：

> **当价格滑到近 1 小时区间低位后，后面 15 分钟里，是否经常能先反弹 `+1 tick`？**

### 3.2 对应的最小 signal 定义
选了一个尽量贴近 repo 精神、但能用公共 K 线复现的定义：
- 看前 `60m` 的 rolling high / low
- 当前 close 必须满足：
  - `close <= previous_60m_low + 0.0002`
  - `close_location <= 0.2`（也就是落在最近 1 小时区间底部 20%）
  - `close <= prev_close`（仍在往下滑）
- 开仓后：
  - 只要未来 `15m` 内任一 bar 的 high 先打到 `entry + 0.0001`，就按 `+1 tick` 走
  - 否则第 `15m` close 超时离场
- 信号按 **非重叠** 统计

### 3.3 结果：gross 是活的，但只适合极低摩擦
这条最小版规则在近 `45d` 上给出：
- 交易数：`1,293`
- `+1 tick` 命中率：`93.0%`
- 平均 gross：`+0.886 bps / 笔`
- 中位数 gross：`+1.001 bps / 笔`
- 平均持有：`3.83 分钟`
- `p90` 持有：`11 分钟`
- 累计 gross：约 `+11.45%`

这组数最值钱的地方不是“赚了多少”，而是形状非常像 repo 假设：
- 大部分单子不是吃大波段；
- 而是 **很快回 1 tick 就走**；
- 拿久了，优势并不会线性放大。

### 3.4 成本敏感度：1 bps 附近就是生死线
我又补了一个简单 friction ladder：
- `0 bps` round-trip：平均 net 约 `+0.886 bps / 笔`
- `0.5 bps` round-trip：平均 net 约 `+0.386 bps / 笔`
- `1.0 bps` round-trip：平均 net 约 `-0.114 bps / 笔`
- `2.0 bps` round-trip：平均 net 约 `-1.114 bps / 笔`

一句话结论非常直接：

> **这条 edge 不是“费后也很厚”的 alpha，而是典型的低摩擦微观口袋；round-trip 一过 `1 bps`，大概率就不值钱了。**

这也反过来解释了 repo 为什么把 **零费率 guard** 写成硬约束，而不是可选项。

## 4. 这条线和当前 desk 有什么直接关系
### 4.1 它补的是一个此前 intake 里不算多的 raw alpha 家族
最近素材池里：
- pairs / stat-arb / funding / options / prediction-market / microstructure 已经很密；
- 但 **稳定币对微脱锚均值回复** 这种“极短、极薄、极 execution-sensitive”的 raw alpha 壳并不多。

它跟一般 breakout / momentum 完全不是一回事，也不是把某个 filter 硬包装成 alpha。

### 4.2 它非常适合做 execution realism 教材
这条线的价值，不只是“也许能赚点 tick”，更在于它几乎是 execution realism 的标准教材：
- 你有没有 maker 权限 / 低费率？
- 你挂在 top two levels，真的能成交多少？
- 一旦回补不足 1 tick，会不会全被时间成本和撤单噪声吃掉？
- 容量上去后，你会不会自己把 edge 踩平？

也就是说，它天然逼着 desk 把 **alpha / fee / queue / capacity** 四件事拆开看清楚。

### 4.3 它还能反过来服务其他更复杂的 maker-ish 思路
后面如果再测：
- microprice 偏移做市
- stablecoin quote imbalance
- 跨 stablecoin 相对价值
- event-driven maker fade

都很适合先拿这条线做 baseline：

> **如果连最简单的 stablecoin micro-depeg fade 都跑不通，复杂版本多半只是换了个更贵的故事。**

## 5. 策略拆解
- 方向属性：单资产 / 相对价值 / 逆势均值回复
- 基础 alpha：`FDUSDUSDC` 短时落到近 1h 区间低位后，未来几分钟高概率先反弹 `+1 tick`
- regime：稳定币对仍处于窄幅、连续撮合、未发生结构性脱锚的正常微观环境
- filter / veto：`last_minute_price + 0.0002` max-buy-threshold；只挂 top-two valid grid levels；fee 非 0 直接停机
- risk / sizing / execution overlay：U-shaped grid 分配、资金约束下动态 grid 数、maker-only 倾向、成交后固定 `+1 tick` exit

## 6. 下一步怎么测
这条线下一步不该直接上“大回测美化”，而该先补 3 个最小但决定性的 realism test：

1. **order-book replay / top-of-book fill test**  
   用 Binance `depth` 或 `aggTrades` 级数据，测 top-two grid level 的真实成交概率，而不是只看 K 线 high 有没有摸到。

2. **queue-sensitive friction ladder**  
   不只测 `0 / 0.5 / 1.0 / 2.0 bps`，还要把“挂单没排到、被动成交比例下降、撤单重挂损耗”一起建进去。

3. **多 stablecoin 对横向对照**  
   复制到 `USDC/USDT`、`FDUSD/USDT`、`USDC/FDUSD` 的可交易 venue / session 上，判断它是不是只在 `FDUSDUSDC` 这个局部环境成立。

如果这三步里：
- queue realism 后仍接近 `0.5 bps` 以上净边，
- 且不同稳定币对还能复现，
那它就值得升级成 desk 的 **maker micro-alpha 素材**；否则更适合保留为 execution / capacity 研究样本。

## 7. 风险与保留意见
- **最大风险不是方向错，而是成交假设太乐观。** K 线能打到 `+1 tick`，不等于你的挂单真能排到。
- **这条线极度依赖低摩擦。** 公开 K 线 probe 已经显示：`1 bps` round-trip 左右就接近净负。
- **稳定币对有制度性风险。** 真遇到信用事件或结构性脱锚，这类“均值回复”假设会突然失效。
- **样本属于 2026 近 45 天局部环境。** 还需要更长历史和更细粒度订单簿验证，不能直接当长期稳定印钞机。

## 8. 来源
- wangshaofu. (2025/2026). *mm_bot*. GitHub repository.  
  Repo URL: `https://github.com/wangshaofu/mm_bot`
- Binance Spot public market data.  
  Klines endpoint: `https://api.binance.com/api/v3/klines?symbol=FDUSDUSDC&interval=1m`

## 9. 这轮产物
- 研究笔记：`research/quant_digests/2026-04-17_2156_stablecoin-microdepeg-grid-shell.md`
- Probe summary：`reports/artifacts/quant_digests/2026-04-17_fdusdusdc_microdepeg_probe_summary.json`
- Probe trades：`reports/artifacts/quant_digests/2026-04-17_fdusdusdc_microdepeg_probe_trades.csv`
- Cost ladder：`reports/artifacts/quant_digests/2026-04-17_fdusdusdc_microdepeg_probe_costs.csv`
