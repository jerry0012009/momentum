# 不是把 Polymarket 当情绪滤镜，而是直接做 time-to-expiry raw alpha：late-entry binary continuation

- 主题类型：raw alpha
- 基础 alpha：`hard-expiry 15m binary market` 在临近到期时的“共识侧继续占优”惯性
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 先回答一句：这篇东西的 base alpha 是什么？
这轮真正值得 intake 的 **base alpha** 很简单：**在 15 分钟硬到期二元市场里，离结算越近、且盘口已经明显偏向某一侧时，市场“赢家侧”往往继续占优；如果这时价格还没涨到极端贵位，就可以直接做一条 late-entry continuation 策略。**

这不是拿 Polymarket 给别的 BTC perp 策略做 filter；它本身就是一条 **可独立回测、可独立下单、可独立风控** 的 raw alpha。后面当然也能再反过来给主 desk 做 cross-market sidecar，但第一性应该先把它当 **独立 alpha** 看。

---

## 为什么这轮值得写它
最近 digest 池里已经有不少：pairs、basis/funding、盘口 continuation、盘口反转、ETF/Polymarket cross-market lead-lag。**但“硬到期二元市场自身的 time-to-expiry alpha” 还没有单独拆干净。**

这条题材这轮值得做，原因有 4 个：

1. **raw alpha 清楚**：不是宏观解释，不是情绪综述，就是“临近到期、领先侧继续赢”的直接交易规则；
2. **完整壳子现成**：这份 2026 新 repo 已经把 entry window、价格门槛、sizing、flip-stop、stop-loss、execution 都写出来了；
3. **公开数据就能先做最小实验**：Gamma API 能取 market metadata / outcome，CLOB websocket 能取盘口；
4. **和 2026-04-02 01:17 那篇 Polymarket × Binance lagged mispricing 不重复**：那篇核心是跨市场 lead-lag；这篇核心是 **Polymarket 自身** 的 time-to-expiry continuation。

---

## 主要来源

### 1) 主来源：2026 新仓库
- **Owner / Year**: Mephisto-Grumpy, 2026
- **Title**: `4coinsbot`
- **Type**: GitHub repo
- **Readable URL**: https://github.com/Mephisto-Grumpy/4coinsbot
- **Repo URL**: https://github.com/Mephisto-Grumpy/4coinsbot
- **Created / Updated**: 2026-03-27 / 2026-03-31
- **关键文件**:
  - `README.md`
  - `src/strategy.py`
  - `src/data_feed.py`
  - `src/trader.py`
  - `config/config.example.json`

### 2) 公共市场数据 / 结算来源
- **Provider / Year**: Polymarket, 2026 live market API
- **Title**: `btc-updown-15m-*` recurring 15m crypto markets
- **Type**: public market metadata / outcome API
- **Readable URL**: https://gamma-api.polymarket.com/events?slug=btc-updown-15m-1775126700
- **说明**:
  - 当前 live BTC 15m market 显示：
    - `bestBid = 0.43`
    - `bestAsk = 0.44`
    - `liquidityClob ≈ 24410.53`
    - 整个 series `volume24hr ≈ 8.65m`
    - `orderPriceMinTickSize = 0.01`
    - `orderMinSize = 5`
  - 当前 market title: `Bitcoin Up or Down - April 2, 6:45AM-7:00AM ET`

### 3) 结算锚点
- **Provider**: Chainlink BTC/USD data stream
- **Readable URL**: https://data.chain.link/streams/btc-usd
- **用途**: repo 与 live market metadata 都明确写了 15m BTC binary 的 resolution source，用来做事后 outcome 对齐。

> 这轮最值钱的不是“预测市场很热闹”，而是：**它给了一个天然 hard-expiry、天然 bounded payoff、天然 15m event-clock 的可执行 alpha 载体。**

---

## 这份 repo 真正给出的，不是机器人外壳，而是一条完整策略壳

### 1) entry window 直接锁在最后 240 秒
`src/strategy.py` 里最重要的一条不是“买 favorite”，而是：

- `entry_window_sec = 240`
- 也就是 **只在最后 4 分钟** 允许入场；
- 当前系列本身是 `15m` recurring market，所以本质上就是在一个 **固定 900 秒生命周期** 的硬到期产品里，只做后段 continuation。

翻成人话：**这不是全天随机扫信号，而是只在“离结算足够近、信息差已经高度压缩”的时段下注。**

### 2) 方向不是拍脑袋，而是直接跟当前 favorite
repo 定义：
- `favorite = 'UP' if up_ask > down_ask else 'DOWN'`
- `confidence = abs(up_ask - down_ask)`
- 当 `confidence >= 0.30` 才允许入场

也就是说，它不是在赌“赔率更便宜的一边均值回归”，而是明确押 **当前更贵的一边继续赢**。

这就是这条 alpha 的本体：**binary momentum / continuation into expiry**。

### 3) 不是无脑追高，还留了 price cap
repo 同时要求：
- `price_max = 0.92`

意思很直白：**favorite 虽然可以追，但不能追到离 1 美元 payout 太近。**

这个 price cap 很关键，因为 binary 市场最容易犯的错，就是把 95c 以上的“看起来快赢了”误当成高胜率低风险，结果吃到 tail flip。

### 4) 还加了一层交易可执行性约束
repo 里还有两个很实用的 gate：
- `entry_frequency_sec = 7`
- `max_spread = 1.05`（用 `up_ask + down_ask` 控制二元盘口总宽度 / 摩擦）

这意味着它已经天然在做两件事：
1. 避免高频重复打单；
2. 避免在盘口太烂、两边 ask 合起来明显偏贵时追价。

对于短周期 desk，这类“别在太差的盘口里做对的方向”本身就很值钱。

---

## 最关键的参数，不是故事，而是这些数字
repo 已经把最小可复现参数给得很具体：

1. **入场窗口**：最后 `240s`
2. **最小方向差**：`|up_ask - down_ask| >= 0.30`
3. **最高追价**：`favorite_price <= 0.92`
4. **时间分层仓位**：
   - `>180s`: `8` contracts
   - `120~180s`: `10` contracts
   - `<120s`: `12` contracts
5. **单 market 最大投入**：`300 USD`
6. **单笔最大订单**：`150 USD`
7. **flip-stop 阈值**：`0.48`
8. **固定止损**：BTC / ETH / SOL `-12 USD`，XRP `-11 USD`

这些参数的价值在于：**它已经不是“我觉得 Polymarket 可以做做看”，而是一套能直接进 backtest / paper trading 的完整壳。**

---

## 为什么我把它归类成 raw alpha，而不是 filter / overlay
因为这里的入场逻辑本身就是闭环的：

- 市场对象固定：`BTC / ETH / SOL / XRP` 的 recurring `15m` hard-expiry binary
- 时钟固定：只做最后 `240s`
- 方向固定：跟随当前 favorite
- 价格条件固定：只在 `confidence` 足够大、但 `favorite_price` 还没贵到离谱时入场
- 出场固定：结算 / flip-stop / stop-loss
- sizing 固定：按剩余时间分层

这就已经是一条**可独立复现、可独立交易、可独立做资金管理**的策略。

它当然也能服务主 desk：例如把 Polymarket 的临近结算 favorite 侧，当成 BTC/ETH perp 在最后 `1m/3m` 的外部确认层。但那是 **secondary use-case**，不是 primary classification。

---

## 和当前 short-cycle desk 的关系

### 1) 最自然的是 `15m`
这条 alpha 的原生周期就是 `15m`，因为产品本身就是 recurring `15m` market。

### 2) `1m / 3m / 5m` 不是拿来改主信号，而是拿来做 execution / 子窗口切片
对当前 desk，更合理的映射方式是：
- **15m**：定义主 alpha（是否进场）
- **5m**：把最后 240s 切成 `240~180 / 180~120 / 120~0` 三段
- **3m / 1m**：做更细的 timing、观测 favorite 是否稳定、是否发生 favorite flip

换句话说，这条策略不是“把 15m 信号下采样成 1m”；而是 **15m alpha + 1m/3m execution refinement**。

### 3) 它补的是 desk 里还不够多的一类原始素材
最近我们的 raw alpha 素材池里，已经很多：
- perp / spot / basis / funding
- order-book continuation / reversal
- pairs / relative value
- ETF / Polymarket cross-market lead-lag

但 **hard-expiry binary continuation** 这种“时间离结算越近越有信息”的 alpha 壳，依然不多。它和 perpetual 那些无限期产品是不同的物种，值得单独占一个坑位。

---

## 最小可复现实验应该怎么做

## 数据源
- `Gamma API`：市场列表、slug、resolution、outcome、liquidity、best bid/ask、min tick、min size
- `CLOB websocket`：盘口更新（repo 用的是 `wss://ws-subscriptions-clob.polymarket.com/ws/market`）
- `Chainlink stream`：结算参考说明（用于核对规则）

## 公开性
- 市场数据读取是公开可得；
- 真正下单才需要 Polymarket API credentials；
- 所以 **最小研究实验不需要先有交易权限**。

## 更新频率
- recurring market：每 `15m` 一个新市场
- websocket：近实时盘口更新
- metadata / outcome：可轮询获取

## 最小实验口径
我建议不要一上来卷复杂模型，先做 3 步：

### 实验 1：纯 repo 参数复刻
按 repo 原参数直接回放：
- 市场：BTC / ETH / SOL / XRP
- 只做最后 `240s`
- `confidence >= 0.30`
- `favorite_price <= 0.92`
- 分层 size：`8 / 10 / 12`
- exit：到期结算 or `flip_stop <= 0.48` or fixed stop-loss

先看：
- hit rate
- 平均单笔 ROI
- 最大回撤
- 按 coin 分桶结果
- 按 `favorite_price` 分桶结果

### 实验 2：把“favorite 是否稳定”加进去
repo 当前只看此刻 favorite，不看它是不是刚翻过来。

下一步要测：
- 入场前 `30 / 60 / 90` 秒里，favorite 是否保持同侧
- `favorite flip count` 是否越低越好
- 连续同向报价时间越长，是否胜率更高

如果成立，这会让策略从“追当前最贵一边”升级成“追 **稳定共识** 最贵一边”。

### 实验 3：把它反向移植成主 desk 的 external sidecar
这一步别和主实验混：
- 先独立验证 Polymarket raw alpha 是否成立；
- 再看最后 `180s / 120s / 60s` 的 favorite-side 是否对 Binance / Coinbase / Hyperliquid 的 BTC/ETH `1m` 收盘方向有附加信息。

也就是：**先把它当 alpha，本体成立后再当 signal donor。**

---

## 我最建议先测的 4 个假设

### 假设 1：`120~0s` 不一定比 `240~120s` 更好
repo 用更靠近结算的区间给更大 size（`8 -> 10 -> 12`）。

这在直觉上没毛病，但真实回测里可能出现两种情况：
- 越靠近结算，信息越准，胜率更高；
- 但越靠近结算，盘口越贵、翻车更痛，risk-adjusted 反而不一定更优。

所以先别默认后 120 秒一定最好。

### 假设 2：`favorite_price 0.75~0.88` 可能是最好区间
太低的 favorite，说明市场还没形成共识；
太高的 favorite，说明赔率已经太差。

真正可能最甜的，也许不是 repo 的整段 `<=0.92`，而是一个中间甜蜜区。

### 假设 3：SOL / XRP 可能比 BTC / ETH 更需要更严格 liquidity gate
repo 里已经默认把 XRP 关掉了，说明作者自己也知道流动性差异很大。

所以别只做 overall 回测，一定要按 coin 分层：
- 胜率
- spread
- 可成交量
- stop-loss 触发率

### 假设 4：favorite flip-stop 会比固定止损更关键
在 binary 市场里，最大的风险未必是慢慢亏，而是“原本的 favorite 瞬间失宠”。

所以 `flip-stop` 很可能比固定 `-12 USD` 更重要。这个要优先测谁先触发、谁更贡献回撤控制。

---

## 风险与失败模式

1. **最后几分钟追价最容易吃赔率劣化**
   - 方向对了，也可能因为买得太贵而没有赔率；
2. **favorite 突然翻转**
   - 这正是 binary 市场最恶的 tail risk；
3. **盘口深度看起来够，真实吃单不一定够**
   - live market metadata 有 `min size / tick / best bid-ask`，但真实成交量和抢单速度仍要单独测；
4. **跨币种流动性差异很大**
   - BTC/ETH 可能能做，SOL/XRP 可能更像噪音多、盘口薄；
5. **别把这个 alpha 误读成“能预测现货价格”**
   - 它先是 Polymarket 自身的 binary continuation，能否迁移到 perp 是第二层问题。

---

## 结论
如果只用一句话总结：

**这份 2026 新 repo 最值得 desk intake 的，不是“又一个 Polymarket bot”，而是把 `hard-expiry 15m binary momentum` 写成了完整可复现策略壳：最后 240 秒、跟随 favorite、要求 30c 以上方向差、但不追超过 92c 的贵票，再配分层 sizing、flip-stop 和固定止损。**

它满足这轮优先级里最重要的几条：
- **raw alpha 清楚**
- **可独立复现**
- **可直接落完整策略**
- **公开数据可拿**
- **和现有 Polymarket cross-market digest 不重复**

所以这轮我会把它归到：**值得进 short-cycle 素材池的完整 raw alpha 候选**。

---

## 下一步怎么测
直接按下面顺序，不要跳：

1. **抓 14~30 天 BTC / ETH / SOL / XRP 15m recurring market 数据**
   - market slug
   - `up_ask / down_ask / bestBid / bestAsk`
   - `seconds_till_end`
   - 盘口更新频率
   - 最终 outcome
2. **1:1 复刻 repo 参数**，先做 honest baseline；
3. **做 3 个最重要的参数扫**：
   - `entry_window`: `240 / 180 / 120 / 60`
   - `min_confidence`: `0.20 / 0.25 / 0.30 / 0.35`
   - `price_max`: `0.80 / 0.85 / 0.88 / 0.92`
4. **单独评估 favorite stability**：过去 `30~90s` 是否频繁 flip；
5. **最后才做 transfer**：看它能否给 Binance / Hyperliquid 的 `1m/3m` 收盘方向提供附加信息。

如果第一轮 baseline 都跑不出像样赔率，再讨论它是不是只能退化成 cross-market filter；但在 baseline 之前，不要先把它降级成 filter。
