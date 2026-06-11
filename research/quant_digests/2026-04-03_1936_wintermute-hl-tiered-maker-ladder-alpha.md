# 别把 Wintermute 的 Hyperliquid quoting repo 只读成“鲸鱼挂单观察”：对 short-cycle desk，更该先测的是「symmetric tiered maker ladder × inventory-skew / 外部对冲」这条完整 maker raw alpha
- 时间：2026-04-03 19:36 UTC
- 类型：2026 GitHub 新 repo source audit（GitHub API metadata + `README.md` + `wintermute_hyperliquid_thread.txt` + `scripts/fetch_orders.py` + `scripts/fetch_positions.py` + `scripts/generate_charts.py`）+ Hyperliquid 公共 API live probe
- 主题类型：raw alpha
- 基础 alpha：**被动做市的 spread capture**——在流动性更深、成交更密的币种上，围绕 mid 对称挂出分层 maker 梯子，近端小尺寸运行、远端大尺寸运行；赚的是 **被动成交时吃到的 spread / queue rent**，并用库存对称、分层放量、必要时外部对冲来压 adverse selection。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/maker/market-making/spread-capture/tiered-ladder/inventory-skew/external-hedge/hyperliquid/public-api/microstructure/1m/3m/5m/15m/repo/live-probe/cost/risk
- 证据类型：repo README + source 规则级证据 + 公共 API 实时快照

## 1. 这次看了什么
一句话：

> 这次不是在看“某个大户怎么挂单”，而是在拆一个**可以直接翻译成可交易壳的 maker raw alpha**：`对称分层挂单 + 分市场宽窄价差 + 库存尽量平衡 + 需要时外部 hedge`。

为什么它值得进当前池子：
- 它的 **base alpha 很清楚**，不是讲故事，也不是纯 filter：就是 **maker spread capture**。
- 它天然不是 bar-close 策略，但**非常适合补 desk 目前更偏 taker / stat-arb 的素材池**。
- 它给的是一套**完整可落地骨架**：`entry / exit / sizing / risk / cost` 都能拆出来。
- 数据源是 **Hyperliquid 公共 API**，今天还能直接做 live probe，不需要私有数据才能先走最小验证。

## 2. 先把 base alpha 说清楚
翻成人话：
- 你不是去猜 `BTC` 下一根涨跌；
- 你是在盘口两边**持续摆一套报价梯子**；
- 近 mid 的单更小、更密，目的是多吃流量；
- 远离 mid 的单更大、更宽，目的是在波动更大、被挑中的风险更高时，拿更厚的 spread 补偿；
- 如果库存偏向某一边，就通过 **降低某侧侵略度 / 提高另一侧侵略度 / 外部 venue 对冲**，把 book 拉回更中性。

也就是：

> **这条 alpha 的本体不是方向预测，而是“在有流量的地方，用可控库存去持续出租流动性”。**

这和今天已经很多的 `breakout / z-score / lag-arb` intake 不一样：
- 它是 **maker alpha**，不是 taker alpha；
- 它赚的是 **spread + queue position**，不是 bar close 的方向 drift；
- 它更适合做 `1m / 3m` 高频 sleeve，也能反向服务 `5m / 15m` 策略的执行层与 venue routing。

## 3. 这次看的主材料是什么
### 3.1 主 repo
- **Author / Repo owner**：`0xLoris`
- **Year**：2026
- **Title / Repo**：*Wintermute Hyperliquid Quoting Strategy Analysis*
- **Venue**：GitHub repository
- **DOI**：无
- **Readable URL**：<https://github.com/0xLoris/wintermute-hyperliquid-analysis>
- **Repo URL**：<https://github.com/0xLoris/wintermute-hyperliquid-analysis>
- **GitHub metadata**：created `2026-01-13`；pushed `2026-01-13`；updated `2026-03-15`；stars `31`

### 3.2 直接核对的 source
- `README.md`
- `wintermute_hyperliquid_thread.txt`
- `scripts/fetch_orders.py`
- `scripts/fetch_positions.py`
- `scripts/generate_charts.py`

### 3.3 这次额外做的 live probe
直接用 Hyperliquid 公共 API 复核：
- `POST https://api.hyperliquid.xyz/info` with `{"type":"openOrders","user":...}`
- `POST https://api.hyperliquid.xyz/info` with `{"type":"allMids"}`
- `POST https://api.hyperliquid.xyz/info` with `{"type":"clearinghouseState","user":...}`

本轮本地 artifact：
- `reports/artifacts/quant_digests/2026-04-03_wintermute_hyperliquid_summary_live.csv`
- `reports/artifacts/quant_digests/2026-04-03_wintermute_hyperliquid_ladder_live.csv`
- `reports/artifacts/quant_digests/2026-04-03_wintermute_hyperliquid_positions_live.csv`

## 4. repo 真正给了什么策略骨架
## 4.1 Entry：围绕 mid 的双边分层挂单
`fetch_orders.py` 的分析口径很直接：
- 先拉全市场 `openOrders`；
- 再拉 `allMids`；
- 对每个市场拆成 `bids` / `asks`；
- 计算：
  - `best_bid / best_ask`
  - `spread_pct`
  - `bid_notional / ask_notional`
  - `avg_bid_spacing / avg_ask_spacing`
  - 各层距离 mid 的 `distance_from_mid_bps`

这意味着策略的最小 entry 单元其实很清楚：
- 每个市场同时维护 bid / ask 两侧；
- 每侧有多层价格；
- 每层有不同 size；
- 离 mid 越远，size 越大、spacing 越宽。

换句话说：

> **entry 不是“出信号后开仓”，而是“持续维护一个可成交的流动性曲面”。**

## 4.2 Sizing：小近大远，不同币种宽度不同
README 给的 January 2026 观察值：
- 总 quoted notional 约 **$199M**
- **1,732** resting orders
- **76** 个市场
- 约 **11 个 size tiers**
- 相邻层级 size 典型增幅 **2.5x ~ 2.8x**

repo 作者举的例子：
- BTC：从 `0.05 BTC` 近端小单，逐层放大到 `27.5 BTC`
- ETH：从 `2 ETH` 逐层放大到 `500 ETH`
- 小币明显给更宽的 spread、更少的 orders

这背后的 sizing 逻辑非常 desk-friendly：
1. **近端层**：更像流量层，吃更多成交机会；
2. **远端层**：更像保险层，只有在价差厚、补偿高时才接更大单；
3. **币种层**：大盘币窄、小盘币宽；不是“一套 bps 打天下”。

## 4.3 Risk：核心不是“预测对”，而是“别被库存拖死”
README 和 thread 都反复强调两件事：
- quoted book 在 notional 上接近对称；
- perp inventory 实际会累积，而且**不等于方向押注**。

repo 的解释是：
- maker book 尽量保持 bid / ask 接近均衡；
- 真正成交后的库存会在本 venue 累积；
- 专业做市商通常需要在别的 venue / 现货 / 永续仓位上做再平衡。

也就是说：

> **risk 管理的重点不是“止损一笔单”，而是“整个库存曲线别单边漂移失控”。**

这对我们非常重要，因为很多看起来“spread 很肥”的 maker 想法，死法都一样：
- fill 看起来很顺；
- 但被动成交其实持续偏在同一侧；
- 库存开始单边堆积；
- 真正亏钱不是单次 spread，而是 inventory + adverse selection。

## 4.4 Cost：宽 spread 本身就是成本补偿，不是事后美化
这类策略不能只看名义 spread，必须同时看：
- maker fee / rebate
- 被动成交后到 mid 的瞬时 adverse selection
- quote refresh / cancel 频率
- 外部 hedge 的 taker 成本
- 小币的冲击成本与 stale quote 风险

repo 虽然不是一套可直接回放 fill 的 production engine，但已经把最关键的 economics 讲明白了：
- **大盘币**：更窄 spread，靠更高成交率吃量；
- **小盘币**：更宽 spread，靠更厚补偿覆盖 adverse selection；
- **库存不平**：不是靠“相信会回来”，而是靠更对称 book 或外部 hedge。

## 5. 这次 live probe 看到了什么
为了避免只转述 README，我直接拉了 2026-04-03 的实时快照。结果和 repo 的 January 2026 结论方向一致，而且规模还更大。

### 5.1 当前 live snapshot headline
- **1,783** open orders
- **82** quoted markets
- quoted notional 约 **$206.8M**
- bid side notional 约 **51.8%**，ask side 约 **48.2%**

这说明 repo 里说的“近对称双边 book”不是一次性截图，而是今天仍能观察到的结构。

### 5.2 当前 top quoted markets（live）
- `BTC`：约 **$89.1M** quoted notional，**104** orders，best spread 约 **3.90 bps**
- `ETH`：约 **$43.6M**，**105** orders，best spread 约 **1.95 bps**
- `SOL`：约 **$16.9M**，**39** orders，best spread 约 **2.62 bps**
- `XRP`：约 **$16.8M**，**38** orders，best spread 约 **4.56 bps**

很直观：
- 资金还是高度集中在最流动的几个币；
- 但不同币的 spread / spacing 已经明显分层；
- 这不是“一个统一参数”的做法，而是按 market quality 分 bucket。

### 5.3 当前分层 size 也还能看见
我按 repo 同样的思路，把相近 size 聚成 tier 后做了粗分组。结果：
- `BTC` 双边大约能看出 **5~6 个**主要 size 组，组间典型放大量级约 **2.0x ~ 2.24x**
- `XRP` 双边大约 **5 个**主要组，组间放大量级约 **2.72x ~ 2.78x**
- `HYPE` 这类更偏中小盘的市场，层数更少，但组间放大更陡

注意：这只是从静态挂单 sizes 推回的近似 tier grouping，不是 fill-based 的真实 production 参数。但它足以说明：

> **repo 所说“tiered size ladder”在 live 盘面上仍然能看到，而不是 README 编出来的故事。**

### 5.4 quote 对称，不等于 inventory 平
`clearinghouseState` live probe 显示，这个地址的显式 perp inventory 依然很重，例如：
- `BTC` 约 **$12.6M long**
- `ETH` 约 **$8.0M short**
- `SOL` 约 **$7.5M short**
- `HYPE` 约 **$5.4M short**

这再次提醒：
- **book 对称** 是 quote 层的目标；
- **库存中性** 则要看更大的全局 book，单一 venue 上很可能并不平。

这正是我们该学的地方：

> 不要把“挂单对称”误会成“风险已经中性”；真正的中性通常要靠多市场、多账户或外部 hedge 才成立。

## 6. 这条 alpha 为什么比继续补一篇普通 filter 更值得
先回答用户要求的那句：

> **因为它本身就是可独立复现、可直接落地的完整 raw alpha，不是只能服务别人的 gate。**

而且它补的是现在素材池里相对少的一类：
- maker spread capture
- inventory-managed quoting
- execution-layer raw alpha

这类 alpha 的价值在于：
1. 它不依赖“下根 K 线方向猜对”；
2. 它可和 trend / MR / stat-arb 并列，形成独立收益来源；
3. 它还能反过来给你别的策略提供 execution benchmark：
   - 什么时候应该被动挂？
   - 什么时候必须主动吃？
   - 哪类币值得给更深层 ladder？

## 7. 它和 `1m / 3m / 5m / 15m` 的关系怎么落
严格说，它不是一条“15m 收盘后决策”的 alpha；但完全可以映射到当前 desk 时钟：

### 7.1 `1m / 3m`：主运行层
适合放在：
- quote refresh
- inventory skew 调整
- enable / disable maker sleeve
- 大小盘不同 ladder 宽度的快速切换

### 7.2 `5m / 15m`：上层 gate / 预算层
适合放在：
- 是否允许小盘币继续挂深层大单
- realized vol / funding / event 风险是否过高
- maker 预算向大盘币或某几个主流币集中
- inventory cap 是否收紧

最实用的读法不是“把它硬改成 15m bar 策略”，而是：

> **`1m / 3m` 负责 quote 与 inventory 控制，`5m / 15m` 负责风险预算与是否开机。**

## 8. 对我们最有价值的不是“照抄 Wintermute”，而是先抄这 4 个组件
### 8.1 组件 A：按市场质量分 bucket
最先抄的不是某个绝对 bps，而是：
- `BTC/ETH` 一档
- `SOL/XRP` 一档
- 其余小盘一档

每档有不同：
- 基础 spread
- 层数
- 远端 size 放大倍率
- 最大库存上限

### 8.2 组件 B：近端小、远端大
这比“所有层同 size”强得多，因为：
- 近端 fill 多，但 adverse selection 更频繁；
- 远端 fill 少，但补偿也更厚；
- 不同层 size 不分化，会让你的 inventory 曲线很难控。

### 8.3 组件 C：quote 对称优先，inventory 另管
不要把“已经做空很多仓位了，所以 ask 删光”这种东西混进 quote alpha 本体。
更稳妥的做法是：
- quote book 尽量保持近对称；
- 当库存超过阈值，再触发轻度 skew 或外部 hedge；
- 不要一开始就把 maker 壳完全变成 directional book。

### 8.4 组件 D：先在 HL 单 venue 做被动 alpha 验证，再谈 cross-venue hedge
第一步别一上来就追 Wintermute 的全局结构。最小复现完全可以先做：
- 单 venue：Hyperliquid
- 单币：BTC / ETH / SOL
- 单侧 / 双侧都测
- 先看 gross maker alpha 是否存在
- 再决定要不要补 CEX hedge 腿

## 9. 最小可复现实验怎么做
这是本轮最重要的落地部分。

### 实验 1：HL 单 venue maker alpha 可行性
**目标**：先判断“被动出租流动性”本身是不是 gross positive。

- 数据源：Hyperliquid 公共接口
  - `allMids`
  - `l2Book`
  - `recentTrades` / 可成交回报流
- 标的：`BTC`, `ETH`, `SOL`
- 频率：原始采样 `1s~5s`；汇总观察口径按 `1m / 3m`
- 策略壳：
  - 双边各 `3~5` 层
  - `BTC/ETH` 用窄 ladder，`SOL` 用更宽 ladder
  - 近端小 size，远端大 size
- 评估：
  - fill rate
  - fill 后 `5s / 30s / 60s` adverse selection
  - gross spread capture
  - 按 quote age 分 bucket 的 stale-quote loss

### 实验 2：inventory-skew 是否真能救 PnL
**目标**：别只看 fill，多看库存怎么把钱亏回去。

- 在实验 1 基础上，加 3 个 inventory 规则版本：
  1. 完全对称
  2. 轻度 skew（库存超阈值才偏）
  3. 超阈值直接暂停某侧近端 quote
- 观察：
  - inventory drift
  - max notional inventory
  - PnL 波动
  - 是否显著降低 adverse selection 后的单边累积亏损

### 实验 3：`5m / 15m` 风险预算层
**目标**：把 maker 壳和当前 desk 时钟接上。

- `5m` gate：近 5m realized vol / spread widening 是否超阈值
- `15m` gate：是否只保留大盘币 ladder，关掉小盘深层挂单
- 对比：
  - always-on maker
  - `5m vol gate`
  - `15m risk-budget gate`

如果这一步有效，说明它不仅是高频原型，还能成为 desk 统一执行组件。

## 10. 风险与容易自欺的地方
### 10.1 静态 open orders ≠ 真正赚钱
repo 和 live probe 都主要是**静态挂单截面**。它们能证明：
- 结构存在；
- 参数分层存在；
- inventory 管理意识存在；

但**不能直接证明净利润**。真正决定输赢的是：
- 哪些层最常被 hit；
- 被 hit 后多久回 mid；
- hedge 成本是否吃掉全部 gross spread；
- quote 更新是否足够快。

### 10.2 别把“鲸鱼能做”当成“我们也能做”
Wintermute 能承受：
- 更高的数据刷新频率
- 更复杂的 hedge 路由
- 更大的库存资本
- 更多 venue 的对冲通道

所以 desk 的诚实切法应该是：

> **先证明“小号版 symmetric tiered maker ladder”在少数大盘币上 gross 不烂，再考虑复杂化。**

### 10.3 小盘币最容易把人骗进 adverse selection
看 README 会很容易被“小盘 spread 很宽”吸引，但这恰恰是最危险的错觉。
宽 spread 不代表更好赚，很多时候只是：
- 盘口更薄；
- 价格更跳；
- 你的 quote 更容易 stale；
- 真成交时，对手往往更“有信息”。

所以第一轮实验最好反着来：
- **先 BTC / ETH**
- 再 SOL
- 小盘最后再上

## 11. 本轮结论
我会把这条线的 verdict 写得很直接：

> **值得进入 raw alpha 素材池，而且优先级不低。**

不是因为它已经被证明能复刻 Wintermute 的收益，而是因为：
- base alpha 清楚；
- source 足够新；
- 公共 API 今天就能 live probe；
- 结构可以直接拆成完整策略；
- 它补的是当前 desk 相对稀缺的 maker/execution 型 raw alpha。

如果只保留一句话给后续复现同学：

> **先别学“全市场鲸鱼画像”，先学“BTC/ETH/SOL 的双边分层 maker ladder + 库存阈值 skew + `5m/15m` 风险预算层”。**

## 12. 下一步怎么测
按优先级只做这三步，不扩题：
1. **先做 `BTC/ETH/SOL` 的 HL 单 venue maker simulator**：采 `1s~5s` 数据，比较 `3层/5层`、`对称/轻度 skew`。
2. **先只做 gross + fee + adverse selection**：不要一开始就塞跨 venue hedge，先确认 maker alpha 本体没死。
3. **再加 `5m/15m` gate**：看高波动时关掉小盘深层 quote 是否真改善 net outcome。

若这三步里，第 1 步就已经 gross negative，就不用浪费时间讲更大的 Wintermute 全局故事；若第 1 步 gross positive、第 2 步仍能存活，再值得补外部 hedge 腿。
