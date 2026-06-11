# 别把这份 HyperData Terminal 只读成鲸鱼看板：对 short-cycle desk，更该先测的是「recent-trader whale-position imbalance × short-horizon follow」这条 raw alpha

- 时间：2026-04-13 18:37 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `src/data_layer/position_scanner.py` + `src/strategies/examples/whale_follow.py` + `src/strategies/base.py`）+ Hyperliquid public API live probe
- 主题标签：raw-alpha/event-driven/positioning/whale/open-position-imbalance/recent-trader-discovery/hyperliquid/public-wallets/liquidation-distance/state/direction-follow/short-horizon/1m/3m/5m/15m/repo/public-data/cost/risk
- 证据类型：源码规则 + 公共接口 live sample + desk-level strategy reframing

- 主题类型：raw alpha
- 基础 alpha：**最近活跃的大额公开地址，如果在同一标的上出现明显的净持仓方向失衡（尤其是“刚成交过的地址”而不是静态鲸鱼榜），其后续 `1m/3m/5m/15m` 更可能沿该方向继续重定价；liquidation distance 更像状态变量，不是 alpha 本体。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1. 先把一句话说清楚：这篇东西的 base alpha 是什么？

> **base alpha = recently-active public-whale position imbalance → short-horizon continuation。**

不是“看见鲸鱼就跟”。
也不是“看见 liquidation map 就猜一定要爆仓”。

这份 repo 里真正适合 desk 拿来做最小实验的，不是 `whale_follow.py` 那个教学版“盯最大一笔仓位、方向一致就下单”，而是它背后的更有用结构：

1. **先用 `recentTrades` 找到刚刚还在市场里活跃的地址；**
2. **再用 `clearinghouseState` 把这些地址的 open positions 拉出来；**
3. **对单个标的做“净多/净空 notional 失衡”聚合；**
4. **把 `distance-to-liquidation` 当成状态变量，判断这是“从容持仓的方向信息”，还是“临近清算的挤压燃料”。**

翻成人话：
- 这不是传统 order-flow；
- 也不是 funding/basis/pairs；
- 它更像一条 **公开地址持仓定位数据驱动的 event/positioning raw alpha**；
- alpha 本体是 **方向失衡本身**，不是 `liq distance`；
- `liq distance` 主要决定你更该做 **follow**、**squeeze chase**，还是干脆不做。

## 2. 这次看了什么

### 主来源（repo）
- **Author / Owner：** GitHub owner `Co-Messi`
- **Year：** 2026
- **Title：** *HyperData Terminal*
- **Venue：** GitHub repository
- **DOI：** N/A
- **Readable URL：** <https://github.com/Co-Messi/HyperData-Terminal>
- **Repo URL：** <https://github.com/Co-Messi/HyperData-Terminal>
- **GitHub metadata：**
  - created: `2026-04-08T14:45:20Z`
  - pushed: `2026-04-09T11:50:53Z`
  - updated: `2026-04-10T15:14:01Z`
  - stars: `1`
  - description: `open-source crypto trading terminal ... whale tracking, liquidation cascades, and paper-traded strategies`

### 本轮直接审的关键文件
- `README.md`
- `src/data_layer/position_scanner.py`
- `src/strategies/examples/whale_follow.py`
- `src/strategies/base.py`

### 本轮自建 probe 产物
- 脚本：`reports/artifacts/quant_digests/2026-04-13_hyperliquid_recenttrader_position_probe.py`
- 汇总：`reports/artifacts/quant_digests/hyperliquid_recenttrader_position_probe_summary_2026-04-13.json`
- 明细：`reports/artifacts/quant_digests/hyperliquid_recenttrader_position_probe_detail_2026-04-13.csv`

## 3. 一句话核心结论 + 一句话证明方式

### 一句话核心结论
> **repo 表面上给的是一个很幼稚的“largest whale 跟单示例”，但真正值得 desk 收下的，是“recent-trader address discovery → open-position imbalance → liquidation-distance state split” 这条可独立复现的 raw alpha 壳。**

### 一句话证明方式
> **证明不靠 README 口号，而是靠源码路径本身：`recentTrades` 发现地址、`clearinghouseState` 拉仓位、`distance_pct` 算清算距离；我再用公共接口 live probe 复核后发现，仅从 `BTC/ETH/SOL/DOGE` 最近成交地址就能映射出 `40` 个活跃地址、`633` 个 open positions，其中 BTC 单标的已能聚出 `~2191` 万美元 gross notional，且净暴露明显偏空。**

## 4. 为什么这轮值得写，而不是继续做 funding / basis / pairs / 又一个 order-flow 题

因为它补的是当前 digest 池里相对缺的一类素材：

1. **这不是 funding/basis/pairs 的重复变体。**
   - 收益来源不是 carry、basis 压缩或 spread 回归；
   - 而是 **公开地址持仓方向失衡带来的后续价格跟随/重定价**。

2. **它不是单纯“看板数据”。**
   - repo 真正有用的地方，是把公共地址发现和持仓聚合都写成了可复用组件；
   - 这意味着我们可以不依赖私有链上标签，不依赖 Coinglass 付费面板，也能先做最小实验。

3. **它和现有 short-cycle 主线有直接关系。**
   - 可以服务 `1m/3m/5m/15m` 的 event-driven directional alpha；
   - 也能和现有 microstructure / liquidation / trend 书架拼接成 confirmation 或 veto；
   - 但它本身依然是可以独立测的 raw alpha，不只是 overlay。

## 5. repo 真正提供了什么

## 5.1 `position_scanner.py` 才是核心，不是示例策略本身
`src/data_layer/position_scanner.py` 这份文件比 `whale_follow.py` 更重要。

它做了 4 件关键事：

1. **地址发现**
   - 从 `recentTrades` 抓最近活跃地址；
   - 默认扫 `BTC / ETH / SOL / DOGE / ARB / SUI / WIF / PEPE`。

2. **仓位抓取**
   - 对每个地址调用 `clearinghouseState`；
   - 拉到 `coin / side / size_usd / entry / liq / leverage / upnl`。

3. **清算距离状态化**
   - 直接算出 `distance_pct = |current - liq| / current`；
   - 还能给出 `within_1pct / within_2pct / within_5pct` 的分层摘要。

4. **最近成交地址 + 当前持仓 的连接**
   - 这点比“静态鲸鱼榜”更重要；
   - 因为我们要找的是 **刚刚还在交易、且当前仍有仓位的参与者**，而不是沉睡大户。

这条链路已经足够形成一个完整 research shell。

## 5.2 `whale_follow.py` 本身太幼稚，但正因为幼稚，反而好拆
教学版示例逻辑非常直接：

- 找某个 symbol 最大的一笔公开仓位；
- 如果 notional 超过阈值（默认 `$500k`）；
- 多就买，空就卖。

源码自己都写了：
> `Educational example — not real trading alpha.`

但这不是坏事。
它反而明确告诉我们：
- repo 并没有假装“已经把 alpha 做完”；
- 它只是把 **数据 plumbing** 和最粗的策略接口交出来；
- desk 真正该做的是把 `largest whale follow` 升级成 **basket imbalance follow**。

## 5.3 `base.py` 把落地接口定义得够清楚
`Signal(symbol, action, size_usd, confidence, reason)` 这种接口很朴素，但已经足够对应 desk 口径：

- signal 本体：方向（BUY / SELL）
- size：仓位大小
- confidence：可映射到杠杆或 budget
- reason：方便日志 / 复盘 / 质检

所以这不是只能做 dashboard 的 repo；
而是 **已经可以很快挂上 paper trading / replay / execution simulator** 的研究底座。

## 6. 我做的 Hyperliquid public API live probe：最关键的数字

## 6.1 数据与口径
- **数据源：** Hyperliquid public `/info`
  - `recentTrades`
  - `clearinghouseState`
  - `allMids`
  - `meta`
- **公开性：** 完全公开，无需 key
- **更新频率：** 近实时（交易与持仓状态级）
- **本轮最小实验口径：**
  1. 从 `BTC / ETH / SOL / DOGE` 的最近成交里发现地址
  2. 截断到最近 `40` 个活跃地址
  3. 拉这些地址当前 open positions
  4. 聚合单标的 gross / net notional 与 liquidation-distance 分层

## 6.2 先记最重要的 6 个数

### 数 1：只用 4 个种子市场，就发现了 `40` 个最近活跃地址
- `BTC`: `10` recent trades
- `ETH`: `10`
- `SOL`: `10`
- `DOGE`: `10`

这说明最小实验的数据入口并不稀缺，**公开接口本身就足够先做研究。**

### 数 2：这 `40` 个地址映射出了 `633` 个 open positions
这点很关键：
我们抓到的不是“几条零碎地址标签”，
而是一层可以持续扫描的 **公开持仓图谱**。

### 数 3：BTC 单标的就有 `21` 笔仓位、`$21.91m` gross notional
具体到 BTC：
- long notional：`$5.91m`
- short notional：`$16.00m`
- gross：`$21.91m`
- net long-minus-short：约 `-$10.10m`

翻成人话：
> **这一刻的“最近活跃公开地址”样本里，BTC 明显是净偏空的。**

### 数 4：最大单笔 BTC 仓位就是一笔 `~$15.69m` 的空单
probe 里最大的 BTC 仓位是：
- side：`short`
- size：`$15.69m`
- leverage：`20x`
- liquidation distance：`151.76%`

这说明两件事：
1. repo 那种“直接跟最大一笔”的逻辑，样本上确实会得到很强的单边信号；
2. 但这笔仓位离 liquidation 很远，**它更像 conviction position，不像 imminent squeeze fuel。**

### 数 5：BTC 的 `within_5pct` notional 只有 `~$3.15m`
- within `1%`：`$0`
- within `2%`：`$80`
- within `5%`：`$3.15m`

也就是说：
> **这个时间点上，BTC 的公开活跃地址样本并不是“马上要爆的大拥挤仓位”，而更像“方向偏空、但离清算还远”的持仓状态。**

这恰好支持前面的拆分：
- **alpha 本体** 是 position imbalance；
- **liq distance** 是状态变量。

### 数 6：不只 BTC，ETH / SOL 也同样出现明显净空暴露
probe 前几大标的摘要：
- `ETH`: gross `~$24.52m`，net `~-$15.30m`
- `BTC`: gross `~$21.91m`，net `~-$10.10m`
- `SOL`: gross `~$6.85m`，net `~-$6.29m`
- `DOGE`: gross `~$3.43m`，net `~-$2.65m`

这意味着更值得测的不是“单地址神话”，而是：
> **同一批最近活跃地址，是否会在多个大币上同步形成方向性持仓失衡，并对后续 `5m/15m` 产生可交易的 drift。**

## 7. 这条线对 short-cycle desk 的正确读法

## 7.1 它是 raw alpha，不是 overlay
原因很简单：
- base alpha 清楚；
- entry / exit / sizing / risk / cost 都能定义；
- 不需要先挂到已有 breakout / mean-reversion / basis 书架上才能存在。

所以它应归类为：
> **event-driven / positioning raw alpha**。

## 7.2 但不要照抄“largest whale blindly follow”
repo 自带示例太粗：
- 单地址噪声太大；
- 容易被偶然的大仓位绑架；
- 不区分新开仓、老持仓、减仓后残留仓；
- 不区分“离 liquidation 远的 conviction”与“离 liquidation 近的 squeeze fuel”。

更合理的 desk 版，至少要升级为：
- **单标的 basket net exposure**，不是单地址；
- **active-address refresh**，不是静态白名单；
- **liq-distance split**，不是一锅炖；
- **time stop + decay**，不是无限持有。

## 7.3 更像哪类完整策略？
更像下面这条壳：

1. **发现地址：** 每 `1m` 更新最近活跃地址池
2. **聚合方向：** 对每个币算 `net_notional = long - short`
3. **做 admission：** 只做 gross notional 足够大、地址数足够多的币
4. **做状态划分：**
   - 若 `within_5pct / gross_notional` 很低：按 **directional follow** 处理
   - 若该比值很高：按 **squeeze continuation / exhaustion** 另立分支
5. **执行：** 在 Binance / Hyperliquid 自己的 `1m/3m/5m/15m` 上做子执行

## 8. 下一步怎么测（必须项）

### 8.1 先做最小可复现实验，不要先做复杂回测系统
第一步不是上生产框架，而是先回答一个最基本的问题：

> **recent-trader basket 的净持仓失衡，到底能不能预测后续 `5m / 15m` 收益方向？**

最小实验建议：

1. 每分钟抓一次：
   - 活跃地址池
   - 当前 open positions
   - 每个 symbol 的 `gross / net / within_5pct`
2. 对每个 symbol 生成 3 个主特征：
   - `net_notional / gross_notional`
   - `address_count`
   - `within_5pct / gross_notional`
3. 预测 future returns：
   - `t+1m`
   - `t+3m`
   - `t+5m`
   - `t+15m`
4. 先只看最朴素分桶：
   - top decile 净多 vs top decile 净空
   - high-liq-risk vs low-liq-risk split

### 8.2 第一版策略壳
如果最小实验有方向性，就先做最简单版本：

- **entry：**
  - `|net/gross| >= q80`
  - `gross_notional >= symbol-specific floor`
  - `active_address_count >= min_n`
- **direction：**
  - `net > 0` 做多
  - `net < 0` 做空
- **exit：**
  - 固定 `5m` / `15m` time stop
  - 或 `net/gross` 回到中性区间
- **risk：**
  - 单币 notional cap
  - 同向 cluster cap
  - liquidation-risk 高时降杠杆
- **cost：**
  - 先按 taker bps 压一次
  - 再测 maker-improved 版本

### 8.3 第二版再考虑与现有书架拼接
如果 raw alpha 本体成立，再去做这些增强：
- 与现有 microstructure flow 做同向确认
- 与 liquidation surge 做 branch split
- 与 funding / basis crowding 做 veto
- 与 trend book 做 regime router

顺序别反。
先确认 raw alpha 本体，再谈 overlay。

## 9. 当前 verdict

> **值得进研究池，而且应该按 raw alpha 立项。**

但要非常明确：
- 不是照抄 repo 的 `largest whale follow`；
- 而是把它升级成 **recent-trader position imbalance**；
- 并把 `liquidation distance` 从“信号本体”降级成“状态分层器”。

如果这条线后续成立，它会给 desk 补上一块目前还不算拥挤的素材：

- 不是 funding/basis
- 不是 pairs
- 不是纯 order-flow
- 而是 **公开地址持仓定位 → 短周期方向漂移**

这对 `1m / 3m / 5m / 15m` 的 short-cycle 研究，是真正值得补的一条新 raw alpha 线。

## 10. 来源
- Co-Messi (2026), *HyperData Terminal*, GitHub repo: <https://github.com/Co-Messi/HyperData-Terminal>
- Repo raw files:
  - <https://raw.githubusercontent.com/Co-Messi/HyperData-Terminal/main/src/data_layer/position_scanner.py>
  - <https://raw.githubusercontent.com/Co-Messi/HyperData-Terminal/main/src/strategies/examples/whale_follow.py>
  - <https://raw.githubusercontent.com/Co-Messi/HyperData-Terminal/main/src/strategies/base.py>
  - <https://raw.githubusercontent.com/Co-Messi/HyperData-Terminal/main/README.md>
- Hyperliquid public API root used in probe: <https://api.hyperliquid.xyz/info>
