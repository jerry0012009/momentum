# 别把这份 Variational copy-trader repo 只读成“空投/跟单工具”：对 short-cycle desk，更该先拆的是「leaderboard wallet open-event × mirror-exit continuation」这条 raw alpha 壳

- 时间：2026-04-16 03:57 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `config.toml` + `python/scripts/trade.py` + `python/scripts/app.py` + `python/src/cli.py` + GitHub API metadata / repo tree）+ Variational 官方站点与 Arbitrum 官方博客交叉核对 + Arbitrum public RPC availability check
- 主题类型：raw alpha
- 基础 alpha：**当公开可观察的高绩效钱包在 RFQ perp DEX 上新开仓时，这本身就是一个“信息事件”——市场往往还没把这笔仓位代表的方向信息完全消化；更适合 short-cycle desk 的做法，不是长期当 copy-farming 工具，而是把它读成 `leaderboard wallet open-event × short-horizon mirror-follow`。**
- 是否可独立复现：是（**前提是用公开钱包地址 + Arbitrum RPC / 链上事件自己重建 watcher，而不是直接信 repo**）
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否（**README 把壳讲出来了，但源码实现证据明显不够；更像可直接拆解的策略草图，不是可直接上线的工程实现**）
- 主题标签：raw-alpha/event-driven/copy-trading/wallet-follow/leaderboard/informed-flow/continuation/mirror-exit/own-stop/rfq-dex/arbitrum/variational/perpetuals/1m/3m/5m/15m/repo/source-audit/public-onchain-data/risk
- 证据类型：repo source audit + official protocol pages + public-chain availability check

## 1. 这次看了什么

这轮看的是新仓：

- **Author：** `poxmetolog9iatb`
- **Year：** 2026
- **Title：** *Variational Copy Trader*
- **Venue：** GitHub repository
- **DOI：** N/A
- **Readable URL：** <https://github.com/poxmetolog9iatb/variational-copy-trader>
- **Repo URL：** <https://github.com/poxmetolog9iatb/variational-copy-trader>
- **Official venue URL：** <https://www.variational.io/>
- **Protocol context：** <https://blog.arbitrum.io/how-variational-is-reinventing-derivatives-onchain-with-arbitrum/>
- **GitHub metadata：** repo 创建于 `2026-04-03`，最近 push 于 `2026-04-15`，star `68`

先把一句话说清楚：

> **这篇东西的 base alpha 不是“跟单软件本身”，也不是“空投积分”。base alpha 是：公开 leader wallet 的新开仓事件，可能携带可被短周期 desk 利用的方向信息；mirror exit 只是出场壳。**

所以它不是纯 overlay，也不是单纯执行工具。只要链上地址与事件流是公开可见的，这就是一条可以独立定义的 **event-driven raw alpha**。

## 2. 这条 raw alpha 为什么值得单独收进素材池

Variational 官方站点把底层交易场景讲得很清楚：

- 协议当前宣传口径是 **`$190B+` total volume、`$600M+` current OI、`~500` listings**；
- 官方站点明确写到它是 **RFQ** 模式，而不是传统 order book；
- Arbitrum 官方博客提到 Omni 在 Arbitrum 上大约支持 **`515` markets**，并强调 **零手续费** 与 **team-operated OLP** 的报价机制。

这几点对 desk 的意义不是“平台很大”，而是三件更实在的事：

1. **钱包行为是公开的。** 既然链上开仓/平仓会留下可跟踪痕迹，那 wallet-follow 就天然是公开数据事件。
2. **零手续费让短持有更有讨论价值。** 至少不像很多 CEX copy-trade 壳那样先被手续费直接打穿。
3. **RFQ 模式意味着‘谁先动、谁被看见’更像信息事件。** 不是连续 order book 上的小噪音，而是离散的“新仓动作”。

翻成人话：

> **这题最值得测的，不是“长期跟着大佬跑”，而是“当公开 leader wallet 刚开一笔新仓时，接下来 `1m/3m/5m/15m` 有没有一段还没走完的跟随段”。**

## 3. README 真正提供了哪些可复用的策略壳

即使先不信 repo 代码质量，README 还是把一套 desk-friendly 壳讲得比较清楚：

- **entry：** 目标钱包出现新 perp 开仓；
- **sizing：** `copy_ratio` 按 leader notional 比例缩放；
- **risk cap：** `max_position_usd`、`min_position_usd`、`max_open_positions`、`daily_loss_limit_usd`；
- **universe filter：** `markets_filter`；
- **exit：** `mirror exit` 或 `own_stop_loss_pct`；
- **position management：** 可多钱包并行跟踪。

这正好对应 desk 常见拆法：

- alpha 本体：**leader wallet 新仓事件后的短时 continuation**
- filter：**只跟特定钱包 / 特定市场 / 特定最小 notional**
- risk：**单笔上限、总仓位上限、日损上限**
- exit：**mirror exit / own stop / fixed-hold 三选一**

所以这题虽然不是强实现证据，但它给了一个很干净的 alpha skeleton。

## 4. 为什么不能把这个 repo 当成“已验证实现”

这里必须泼冷水，而且这轮最大的价值恰恰在这个 source audit：

### 4.1 README 和仓库树明显对不上
README 说 Python 结构里应该有：
- `watcher.py`
- `decoder.py`
- `scaler.py`
- `executor.py`

但 GitHub tree 实际看到的是：
- `python/scripts/app.py`
- `python/scripts/trade.py`
- `python/src/cli.py`
- `python/src/server.py`
- 再加一堆明显和 README 叙述不一致的目录。

### 4.2 `config.toml` 很像通用模板，不像 Variational 专用配置
实际 `config.toml` 里大量字段仍是通用 `CLOB-style bot` 模板口吻，甚至出现 Polygon/CLOB 交易模板式占位，而不是 README 里说的 Arbitrum + Variational RFQ watcher 专用结构。

### 4.3 Python 源码和主题错位得很明显
抽查到的 `python/scripts/trade.py` / `app.py` / `python/src/cli.py` 主要在讲 **Polymarket**、Gamma、RAG、news 等模块，后面还混入大段生成式 filler 内容；这和 README 里承诺的 Variational copy-trader 逻辑基本不是一回事。

### 4.4 README 里的域名也不稳
README 写的是 `variational.market`，但实际可解析、可访问的是 **`www.variational.io`**。这类细节不致命，但会进一步降低“README 可直接相信”的分数。

结论很简单：

> **这不是一个可以直接背书工程质量的 repo；更像一个 marketing-heavy 壳子。能保留的，是它提示出来的 alpha 方向，而不是它当前源码本身。**

## 5. 为什么它和当前 desk 仍然直接相关

我们最近已经写了不少：
- funding / basis / carry
- OI / liquidation / whale positioning
- leader-lagger / relative value

但 **“公开 leader wallet 新开仓事件”** 这条线，和前面几类还是不一样：

- 它不是 funding carry；
- 不是传统 order-flow delta；
- 不是 pairs spread；
- 也不是“鲸鱼当前持仓很多”这种慢变量；
- 它更像 **离散的、可观察的、带身份标签的信息事件**。

也就是说，它给 raw alpha 素材池补的是：

> **`wallet identity + open event` 这一类 event-driven continuation，而不是又一条价格/资金费率派生物。**

这对 desk 很有用，因为后面完全可以和已有东西拼：
- 和 `OI shock` 拼，做“leader wallet + OI 同向放大”
- 和 `liquidity veto` 拼，做“只跟可容纳 slippage 的市场”
- 和 `funding` 拼，做“leader 跟单但避开过度拥挤 funding”

## 6. 可复刻的最小实验

### 研究假设
公开 leader wallet 的新开仓事件，后面 `5m / 15m` 还存在一段可交易 continuation；而且 **mirror exit** 不一定最优，`fixed-hold` 或 `time-stop` 可能更诚实。

### 数据源 / 公开性 / 更新频率
- **数据源：** 公开钱包地址、Arbitrum public RPC（如 `https://arb1.arbitrum.io/rpc`）、Variational 官方站点/公开 leaderboard 页面（若页面不可直抓，可手工维护 wallet list）
- **公开性：** 公开链上数据 + 官网公开信息
- **更新频率：** 区块级 / 秒级事件流
- **最小可复现实验口径：** 先只做 `BTC-PERP / ETH-PERP`，挑 `5~10` 个公开 leader wallets，研究最近 `30d`

### 一个最小可计算定义
1. 记录 leader wallet 新开仓时间 `t0`、方向、名义规模；
2. 若 `size_usd >= threshold`，在 `t0 + latency_buffer` 后同向入场；
3. exit 先做三组 A/B：
   - `mirror exit`
   - `fixed 5m / 15m hold`
   - `own stop-loss + time-stop`
4. 统一先扣一个保守的 **quote/slippage buffer**，不要因为“官方零手续费”就把执行成本当 0。

### 最该先看的 2 个指标
- **post-latency average bps / trade**
- **事件后 `5m/15m` continuation hit-rate**

如果这两项先不过线，就没必要往更复杂的钱包评分和多钱包聚合走。

## 7. 风险与保留意见

这题最容易被误读的地方有四个：

1. **公开 leader wallet 不等于真 alpha。** 很多地址可能只是 points farming、做市对冲、或本身就不是“信息型交易者”。
2. **RFQ 不等于零摩擦。** 零手续费不代表零 spread、零 quote deterioration、零复制延迟。
3. **mirror exit 可能不是最优 exit。** leader 可能持仓更久，但 short-cycle desk 真正该收的是第一段信息扩散，不一定要等对方平仓。
4. **repo 当前工程质量不足。** 这轮不该把仓库当“已验证产品”，只能把它当作一个提醒：**wallet-follow 本身值得正式进入 raw alpha 候选池。**

## 8. 下一步怎么测

如果下一轮继续推进，我建议别再纠缠这个 repo 本身，而是直接做三件更实在的事：

1. **先手工维护一个极小 leader wallet 白名单**
   - 只保留 `5~10` 个地址；
   - 先做人肉样本，别一上来就追“全 leaderboard”。
2. **先做 event study，不急着做完整 copy-trade**
   - 研究 `t0+1m / +3m / +5m / +15m` 的条件收益；
   - 先回答“有没有扩散段”，再回答“怎么赚”。
3. **把 exit 从 `mirror exit` 拆出来**
   - `mirror exit`、`5m fixed-hold`、`15m fixed-hold`、`ATR/time stop` 做 A/B；
   - 很可能真正适合 desk 的，不是“全程复制”，而是“只吃 wallet-open 后的第一段 continuation”。

如果这三步里 `5m/15m` 还能留住正的 post-latency edge，这条线就值得继续升格成正式的 event-driven baseline；如果不过线，这篇 digest 也依然值钱，因为它已经帮我们把一个新方向的 **base alpha** 说清楚了。
