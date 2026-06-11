# 别把这份 2026 Polymarket repo 只读成预测市场工具：对 short-cycle desk，更该先测的是「favorite-side VWAP stretch × 60s momentum × hard-expiry continuation」这条 raw alpha

- 时间：2026-04-11 16:17 UTC
- 类型：2026 GitHub repo source audit（GitHub API metadata + `README.md` + `btc-binary-VWAP-Momentum-bot/README.md` + `PROJECT_LOGIC.md` + `CONFIG.md` + `config.json` + `main.py`）+ Polymarket Gamma API live availability probe
- 主题标签：raw-alpha/prediction-market/single-market/microstructure/vwap/momentum/hard-expiry/fixed-window/binary/continuation/polymarket/btc/5m/15m/repo/public-data/cost/risk/execution
- 证据类型：repo source + live public market metadata（repo-based）

- 主题类型：raw alpha
- 基础 alpha：**在 Polymarket `5m/15m` BTC Up/Down 硬到期二元市场里，当“当前 favorite 一侧”的 token 同时满足 `价格处于中高但未过贵区间`、`高于自己近端 VWAP`、`相对 60s 前仍在上冲` 时，这一侧更像会把领先优势延续到结算。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否

## 先回答一句：这篇东西的 base alpha 是什么？
这轮的 **base alpha** 不是“Polymarket 很热闹”，也不是“预测市场可以拿来当情绪滤镜”。

真正要 intake 的，是一条非常具体的 **single-market raw alpha**：

> **在固定 5 分钟 / 15 分钟生命周期的二元市场里，赢家侧 token 如果已经站上自己近端成交均价（VWAP），而且过去 60 秒还在继续变贵，那么这更像是“临近结算的顺势延续”，不是单纯随机噪音。**

翻成人话：
**不是猜最终涨跌，而是看“当前领先那边，是不是还在被继续抢、而且抢得不算过贵”。**

所以它不是：
- 宏观解释；
- shared filter；
- 纯 execution overlay；
- 也不是上一篇那种 `spot-vs-strike fair value` 错价。

它本身就是一条可以单独回放、单独下单、单独算成本的 **raw alpha**。

---

## 为什么这轮值得写，而不是把它当成“又一个 prediction-market bot”
原因有 4 个：

1. **raw alpha 够清楚。**
   不是“favorite 就买”，而是 **favorite-side 自身的成交流是否继续推着它走**。

2. **它原生就是 `5m / 15m`。**
   不需要把日线逻辑硬压成短周期；产品生命周期本来就是我们现在最关心的时间框架。

3. **复现门槛低。**
   市场发现、盘口、trade prints 都能从公开接口拿；研究回放阶段不需要先有下单权限。

4. **它和已写过的 prediction-market digest 不同。**
   - 不是 `strike-gap / fair probability` 错价；
   - 不是 `adjacent-horizon spread`；
   - 不是简单的 `favorite-confidence late entry`；
   - 而是 **同一市场内部、favorite token 自身的 VWAP + momentum continuation**。

也就是说，这轮补的是 **binary microstructure continuation**，不是再写一遍 prediction-market 套壳。

---

## 主要来源

### 1) 主来源：2026 新仓库
- **Owner / Year**: Poly-Tutor, 2026
- **Title**: `polymarket-5min-15min-1hour-arbitrage-trading-bot-tools`
- **Repo URL**: https://github.com/Poly-Tutor/polymarket-5min-15min-1hour-arbitrage-trading-bot-tools
- **Readable URL**: https://github.com/Poly-Tutor/polymarket-5min-15min-1hour-arbitrage-trading-bot-tools
- **Stars / Created / Updated**: `203 stars` / `2026-02-18` / `2026-04-10`
- **本轮重点子目录**:
  - `btc-binary-VWAP-Momentum-bot/README.md`
  - `btc-binary-VWAP-Momentum-bot/PROJECT_LOGIC.md`
  - `btc-binary-VWAP-Momentum-bot/CONFIG.md`
  - `btc-binary-VWAP-Momentum-bot/config.json`
  - `btc-binary-VWAP-Momentum-bot/main.py`

### 2) 公开市场数据路径
- **Provider / Year**: Polymarket Gamma API, 2026 live endpoint
- **用途**: 市场发现、当前 bid/ask、流动性、最小订单约束
- **Readable URL**:
  - 5m 示例：<https://gamma-api.polymarket.com/markets?slug=btc-updown-5m-1775924100&active=true&closed=false>
  - 15m 示例：<https://gamma-api.polymarket.com/markets?slug=btc-updown-15m-1775924100&active=true&closed=false>

### 3) repo 内写明的公开实时数据通道
- **Market websocket**: `wss://ws-subscriptions-clob.polymarket.com/ws/market`
- **Chainlink RTDS channel（repo 文档中给出的实时价格通道）**: `wss://ws-live-data.polymarket.com`
- **作用**:
  - WebSocket 拉 trade prints / BBO
  - RTDS 作为 BTC/USD 锚点与 market clock 对齐参考

> 这轮最值钱的不是“它能自动下单”，而是：**它把一条 5m/15m hard-expiry raw alpha，拆成了可逐项审计的信号层。**

---

## 这份 repo 真正给出的，不只是 bot 外壳，而是一条很具体的入场骨架

### 1) 交易对象直接锁定 `5m / 15m` BTC hard-expiry market
`config.json` 明写：
- `market.interval_minutes = 5`（可切到 `15`）
- slug 规则就是 `btc-updown-5m-<ts>` / `btc-updown-15m-<ts>`

这很关键，因为它不是“先有日内信号，再找地方落地”，而是直接在 **原生短周期固定到期产品** 上交易。

### 2) 它不是买任意一侧，而是先识别当前 favorite
repo 的核心定义是：
- `favorite = price 更高的一侧`
- 只评估 favorite 的 price / deviation / momentum

翻成人话：
**不是在二元市场里做对敲，不是做均值回归，而是明确押“当前看起来更可能赢的那一边”，再看它是不是还在被继续追。**

### 3) 入场不是“只看涨跌”，而是三层同时成立
从 `config.json` / `CONFIG.md` / `main.py` 能拼出它的最小骨架：

- **价格区间**：`min_price = 0.75`，`max_price = 0.88`
- **VWAP 偏离**：`min_deviation_pct = 3`
- **动量窗口**：`momentum_window_sec = 60`
- **VWAP 窗口**：`vwap_window_sec = 30`
- **时间门槛（5m 默认）**：`min_elapsed_sec = 180`
- **禁止太晚入场（5m 默认）**：`no_entry_before_end_sec = 110`

也就是：
1. favorite 不要太便宜（否则说明共识还不够强）；
2. favorite 也不要太贵（否则赔率已经太差）；
3. current price 要明显高于近端成交均价；
4. 过去 60 秒还得继续往上冲；
5. 只在市场生命周期后段做。

这 5 条合起来，才是这条 alpha 的本体。

### 4) 这其实是一种“bounded payoff 里的顺势追价”
在普通 perp 市场里，追涨常常会遇到“上面还有多远”这个问题；
但在二元市场里，收益上限天然被封在 `1.00`。

所以这里最核心的问题不是“还能涨多少”，而是：
**“在 payout 已封顶的前提下，这个价格是不是还没贵到不值得买，但已经出现了明显的流持续推动？”**

repo 用的其实就是这套思路：
- `0.75~0.88` 控制赔率区间；
- `VWAP deviation` 控制“是不是正在被追”；
- `60s momentum` 控制“不是刚好站上去一下就掉下来”。

---

## 最值得记录的硬数字

### 1) 5m 默认参数已经够具体，可以直接做第一轮 replay
从公开 `config.json` 看到的默认值：
- `interval_minutes = 5`
- `min_price = 0.75`
- `max_price = 0.88`
- `min_elapsed_sec = 180`
- `no_entry_before_end_sec = 110`
- `min_deviation_pct = 3`
- `momentum_window_sec = 60`
- `vwap_window_sec = 30`
- `bet_amount_usd = 5`
- `price_offset = 0.02`
- `order_type = FAK`
- `max_retries = 3`
- `hedge.enabled = true`，`hedge_price = 0.02`

这不是“以后可以再加风险管理”，而是 **entry / execution / hedge** 已经被写成了第一版完整壳。

### 2) repo 自己还给了 15m 的参数映射建议
`CONFIG.md` 里明写：
- 对 `15m` 市场，`min_elapsed_sec` 建议抬到 `530` 左右
- `no_entry_before_end_sec` 建议改到 `335` 左右

也就是说，这份 repo 不只是“支持 5m/15m 切换”，而是已经暗示了：
**15m 版更像在 market 后半段的一个很窄 admission window 里做 continuation。**

### 3) live public-data availability 是真的，不是 README 口嗨
我直接检查了 Polymarket Gamma API 当前 live market：

- **5m 市场** `btc-updown-5m-1775924100`
  - `bestBid = 0.50`
  - `bestAsk = 0.51`
  - `liquidityClob ≈ 20,075.11`
  - `orderMinSize = 5`

- **15m 市场** `btc-updown-15m-1775924100`
  - `bestBid = 0.45`
  - `bestAsk = 0.46`
  - `liquidityClob ≈ 30,920.12`
  - `orderMinSize = 5`

这说明最关键的一点：
**研究数据入口是公开可得的，最小复现实验不需要先搞私有数据库。**

---

## 为什么我把它归类成 raw alpha，而不是 filter / overlay
因为它的入场条件本身就是闭环的：

- 市场对象：固定的 `BTC 5m / 15m hard-expiry binary`
- 方向：当前 favorite-side
- 触发：`price band + VWAP deviation + momentum`
- timing：生命周期后段
- execution：`FAK + price_offset + retry`
- sizing：`bet_amount_usd`
- hedge：可选 `0.02` 对侧挂单

这已经是一条完整的 **主信号雏形**，不是依附于别的 alpha 才能存在的门控层。

当然，它也可以反过来服务别的 raw alpha：
- 给 prediction-market 其他策略做更细的 admission；
- 给 BTC `1m` / `3m` perp 最后 60~120 秒做外部 sidecar。

但那是 **secondary use-case**。第一性分类仍然应该是 **raw alpha**。

---

## 这份 repo 最重要的价值，不是“能直接上线”，而是“能直接拿来拆”
这里要特别老实一点：

### 1) 文档和代码的 momentum 门槛并不完全一致
`README / CONFIG.md` 的语言更像：
- 只要 momentum 为正、方向一致即可。

但 `main.py` 实际写的是：
- `mom_ok = fav_mom is not None and fav_mom > 5`

也就是要求：
**favorite token 相对 60 秒前，已经涨了 5% 以上。**

这不是一个小差异。
因为对二元 token 来说，`+5%` 不是很轻的门槛，尤其当价格已经在 `0.75~0.88` 区间时，这会大幅减少信号数。

所以第一轮实验不能只照 README 抄，必须把：
- `mom > 0`
- `mom > 2`
- `mom > 5`

做成三档比较。

### 2) exit / PnL 记账在公开代码里并不够严谨
`main.py` 里有一个很值得警惕的实现：
- 在距离结算 `<= 10s` 时，用 **当下 token `last_price`** 作为 `final_price`
- 然后把 `final_price >= 0.70` 直接当成“赢了”

这意味着公开代码里：
- 不是按真实 market resolution（0 或 1）结算；
- 更像是用临近到期的 last trade price 近似最终结果。

对研究来说，这样做会把两件事混在一起：
1. **alpha 是否真预测了结算结果**
2. **临近收盘 token 自身 mark-to-market 有没有提前反映**

所以它的策略骨架值得拿，但 **PnL / exit accounting 不能直接信**。

### 3) `win_rate_csv` 在配置里被引用，但公开仓库树里没有直接看到该文件
`config.json` 引用了：
- `data/win_rate.csv`

但本轮 GitHub 树检查时，没有在公开目录里直接拉到这个路径。

这不影响我们复现 alpha 本体，
但说明：
**repo 里某些“显示历史胜率”的配套材料，不应被当成可直接复现的既成事实。**

因此本轮 4 个字段里，我把“是否可直接落地完整策略”标成了 **否**。
不是因为它没有策略壳，而是因为：
**它的公开实现仍然需要先把 exit / accounting / conditioning table 审清楚。**

---

## 最小可复现实验怎么做

## 数据源
1. **Gamma API**
   - 市场发现
   - live bid/ask
   - liquidity / min size
2. **Polymarket market WebSocket**
   - trade prints
   - BBO 更新
3. **resolution 结果**
   - 用市场最终 outcome / redeemable result 对齐
   - 不要偷懒用 `10s before expiry` 的 last trade 当真结算

## 公开性
- 研究 / 回放阶段：公开可得
- 真实下单：需要 Polymarket 凭证

## 更新频率
- 市场：每 `5m` / `15m` 一个新 hard-expiry contract
- WebSocket：近实时
- metadata：HTTP 轮询即可

## 最小实验口径
我建议第一轮先只做 BTC，别一上来加多币：

### 实验 1：忠实复刻 repo 信号，但修正结算口径
- 市场：BTC `5m` + `15m`
- 入场侧：当前 favorite
- 条件：
  - price in `[0.75, 0.88]`
  - elapsed >= threshold
  - deviation >= `3%`
  - momentum > `0 / 2 / 5` 分桶
- 执行：假设 taker 买入 `best_ask + 0.01/0.02`
- 结算：必须按真实 outcome（0/1）

先看：
- hit rate
- 平均单笔 EV
- 按价格桶的 ROI
- 按 time-left 的 ROI
- 按 momentum 桶的单调性

### 实验 2：和“favorite-only late-entry”基线做增量比较
同样只做 favorite，但分三版：
1. 只看 favorite + price band
2. favorite + price band + deviation
3. favorite + price band + deviation + momentum

目的不是证明 repo 神，而是回答一个更有价值的问题：
**VWAP / momentum 到底有没有提供增量信息，还是只是把交易数砍少了？**

### 实验 3：拆开 `5m` 与 `15m`
不要合并统计。
因为两者虽然都叫 Up/Down binary，但结构并不一样：
- `5m` 更像超短 event-time continuation
- `15m` 更像更慢的 late consensus continuation

有很大概率会出现：
- `5m` 更吃 momentum
- `15m` 更吃 price band + time-left

### 实验 4：检验“过贵区”是不是主要杀手
重点分桶：
- `0.75~0.80`
- `0.80~0.84`
- `0.84~0.88`
- `>0.88`

因为这类 bounded payoff 策略最常见的失败，不是方向错，而是：
**方向对了，但赔率已经不值。**

---

## 我最建议先测的 4 个假设

### 假设 1：`deviation × momentum` 比单独任何一个都更值钱
只有高于 VWAP，不代表趋势在继续；
只有 60s momentum 为正，也可能只是偶发拉价。

更可能有效的是：
**价格已经站上近期成交均价，而且还在继续被买。**

### 假设 2：`0.80~0.86` 可能比 repo 默认整段更甜
`0.75` 太低时，共识可能不够稳；
`0.88` 太高时，赔率经常太差。

所以真正的甜蜜区，很可能是中间更窄的一段，而不是整段 `[0.75, 0.88]`。

### 假设 3：`15m` 的最优入场窗口可能比 repo 建议更靠后
repo 文档建议 15m 把 `min_elapsed_sec` 拉到 `530` 左右。

但真正值得测的是：
- `480~530s`
- `530~565s`
- `565s 以后`

因为 hard-expiry 市场常常在最后一小段才真正把赔率压实。

### 假设 4：对这类策略，**赔率纪律** 比“是否追上车”更重要
很多人看到这类 token continuation，第一反应是怕错过。

但 binary 的数学本质决定了：
**买得太贵，比晚一点买更伤。**

所以这条策略最终更可能死在：
- 高价追入
- 滑点过大
- 临近结算成交稀薄

而不是死在“方向逻辑完全无效”。

---

## 风险与失败模式

1. **bounded payoff 的赔率天花板非常硬**
   - 方向对也不代表值；
   - 高胜率不等于高 EV。

2. **最后一分钟最容易出现流动性抽干**
   - 即便盘口显示有 bid/ask，真实可成交深度也可能不稳定。

3. **favorite flip 的速度比 indicator 刷新更快**
   - 尤其在 `5m` 市场最后几十秒，状态翻转很快。

4. **公开 repo 的结算/PnL 写法会污染研究结论**
   - 如果继续沿用 `final_price >= 0.70 -> win`，很容易把“临近收盘的 mark”误当“真正预测力”。

5. **prediction-market alpha 不应直接硬搬到 perp**
   - 先在它原生市场里证明成立，再考虑做 cross-market donor。

---

## 和当前 short-cycle desk 的关系

### 1) 最自然的主战场就是 `5m / 15m`
这条策略不需要“映射”成短周期，它原生就是短周期。

### 2) 对 `1m / 3m` 的意义主要在两个地方
- 做更细的 replay / state sampling
- 看最后 `60~180s` favorite-side 状态，能不能作为外部 donor 给 BTC perp 的微型方向判断

### 3) 它补的是我们素材池里还不够多的一类 alpha
我们已经有不少：
- perp / spot / basis / funding
- pairs / stat-arb
- OFI / maker / microstructure
- cross-sectional trend / reversal

但 **hard-expiry binary 内部的 order-flow continuation** 仍然不多。
这类素材值得单独占一个位置。

---

## 结论
这轮最该拿走的，不是“又一个 Polymarket bot”，而是这条更干净的研究命题：

> **在 `5m / 15m` hard-expiry binary 市场里，favorite-side token 若处于“不过贵的中高赔率区”，并且同步出现 `站上近端 VWAP + 60s 正向 momentum`，它是否会比简单的 favorite-only late-entry 更稳定地延续到结算？**

这是一条：
- **raw alpha 清楚**
- **周期原生贴合 desk**
- **公开数据可复现**
- **可以和现有 Polymarket / Kalshi / perp 研究形成互补**

但也要保持克制：
**repo 的公开实现值得拆，不值得照抄。**
尤其是：
- momentum 阈值要重新标定；
- exit / PnL 一定要改成真实结算口径；
- `win_rate_csv` 不能当作现成真相。

---

## 下一步怎么测

### 第一优先（建议今天就开）
做一个 **BTC-only Polymarket 5m/15m replay**：
- 从公开 market/trade data 重建每秒状态；
- 用真实 resolution 做结算；
- 对比 `favorite-only` vs `favorite+VWAP` vs `favorite+VWAP+momentum` 三版。

### 第二优先
把以下 3 个参数做 3×3×3 小网格：
- `min_price`: `0.72 / 0.75 / 0.78`
- `max_price`: `0.84 / 0.86 / 0.88`
- `mom_threshold`: `0 / 2 / 5`

先看哪一层真正提供了 EV，而不是只减少交易数。

### 第三优先
若 Polymarket 原生 alpha 成立，再去测：
- 最后 `180s / 120s / 60s` 的 favorite-side VWAP/momentum 状态
- 是否对 Binance / Hyperliquid BTC `1m` 收盘方向有附加信息

也就是：
**先把它当 alpha，本体成立后，再把它当 sidecar。**