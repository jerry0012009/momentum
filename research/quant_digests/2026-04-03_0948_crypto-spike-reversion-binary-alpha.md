# 别把这份 2026 prediction-market OS 只读成大而全平台：对 short-cycle desk，更该先测的是「5m spike reversion × 30m shape gate × 8m time-box」这条完整 raw alpha

- 时间：2026-04-03 09:48 UTC
- 类型：2026 GitHub 新 repo source audit（GitHub API metadata + `README.md` + `backend/services/strategies/crypto_spike_reversion.py` + `backend/services/strategies/reversion_helpers.py`）
- 主题类型：raw alpha
- 基础 alpha：`short-horizon crypto price spike` 之后，短时二元市场概率会对冲击方向过度定价；做反向一侧，赌其在几分钟内回归
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/mean-reversion/single-asset/crypto/binary-market/spike-reversion/5m-impulse/30m-shape-gate/2h-cap/oracle-diff/kelly/time-box/1m/3m/5m/15m/repo/public-data/external-data/cost
- 证据类型：repo-based（README + 策略源码 + helper 规则 + GitHub metadata）

**先回答 base alpha：这篇东西的 base alpha 很清楚，不是“预测市场平台故事”，而是“5m 级别的急涨急跌会让短到期 crypto 二元市场在几分钟内出现可反做的过度定价”，而且源码把 entry / exit / sizing / hold window 都写出来了。**

## 1. 这次看了什么
这次重点看的是 2026 新仓库 `braedonsaunders/homerun` 里和 crypto 高频方向最相关的几部分：
- `README.md`
- `backend/services/strategies/crypto_spike_reversion.py`
- `backend/services/strategies/reversion_helpers.py`
- GitHub repo metadata

先说结论：**这轮更值得 intake 的不是 README 里那句“38 strategies, 39 data sources”，而是源码里这条已经被写成完整规则壳的 `Crypto Spike Reversion`。**

GitHub metadata 也给了它“新且活跃”的基本信号：
- repo 创建时间：**2026-02-03**
- 最近 push：**2026-04-03 02:32 UTC**
- stars：**13**
- README 明确把 `Crypto HF`、`Flash Crash Reversion`、`VPIN Toxicity` 这些短周期方向列为内置策略家族

## 2. 核心结论（给 desk 的版本）
- **一句话核心结论**：这份 2026 新 repo 里，最适合我们 desk 快速最小实验的，不是平台层基础设施，而是这条已经落成规则的 **`5m spike fade` raw alpha**。
- **base alpha 很纯**：不是 filter，不是 regime，也不是单纯执行优化；它就是在赌 **短时冲击过头后的小窗回归**。
- **最值钱的地方**：源码不是“讲思路”，而是直接给了完整壳：
  - 入场阈值
  - 方向定义
  - 形态过滤
  - 成本粗扣
  - Kelly sizing
  - 止盈 / 止损 / 最大持有时间
- **和最近学习进展的关系**：最近 digest 池里 pairs / basis / carry / cross-sectional 已经很密，这条线正好补一条 **single-asset / within-market mean reversion raw alpha**；而且也呼应 `FACTOR_BACKLOG.md` 里还只是 `SCOPED / PROTOTYPED` 的 `volume spike / volume recovery` 方向——这次不是把它当确认层，而是把它提升为一条能独立下单的 raw alpha skeleton。

## 3. 为什么这轮值得优先做
### 3.1 它补的是 raw alpha，不是 overlay
这轮优先级应该先问：**能不能直接写成完整策略？**

这里答案是能，而且很直接：
1. 先识别 `5m` 急涨/急跌；
2. 再判断这次冲击是否主要是短时 impulse，而不是更长周期趋势延续；
3. 然后反向买二元市场的一侧；
4. 用短 `time-box` 把持仓锁在几分钟，而不是把它拖成宏观判断。

### 3.2 它比继续补一篇 generic filter 更值钱
因为这条线能直接扩充：
- `mean reversion` 原型池
- `single-asset` 原型池
- `event / shock-driven` 原型池
- `binary wrapped crypto` 这一类特殊执行容器的素材池

而不是再写一层“这个条件也许可以 veto 那个 alpha”。

### 3.3 它和 `1m / 3m / 5m / 15m` 的关系并不弱
虽然源码主信号写成 `move_5m`，但它本质是：
- **5m 冲击定义 alpha**
- **1m / 3m 做更细执行与重采样**
- **15m 做更慢的迁移验证与稳健性对照**

所以这不是“只能做 5m”——而是 **5m 是母信号，1m/3m/15m 是实验层的不同投影**。

## 3.5 策略拆解（必填）
- 方向属性：双向 mean reversion（急涨后偏向 `buy_no`，急跌后偏向 `buy_yes`）
- 基础 alpha：`5m impulse overshoot → binary-probability reversion`
- regime：优先在 30m 趋势没有完全接管、2h 级别未进入大级别单边时交易
- filter / veto：
  - `|move_5m|` 必须足够大
  - `5m` 冲击必须相对 `30m` 趋势占主导
  - `2h` 累积波动过大时不做
  - 流动性不够、入场价格过高时不做
- risk / sizing / execution overlay：
  - Kelly fractional sizing
  - liquidity cap
  - 明确 `take_profit / stop_loss / max_hold_minutes`
  - 粗略 fee/slippage 扣减已内嵌在 edge 近似里

## 4. 源码里最值得抄的规则骨架
## 4.1 方向不是拍脑袋，而是“反着 5m 冲击做”
`crypto_spike_reversion.py` 的核心方向定义非常干净：
- 若 `move_5m > 0`，说明标的短时急涨，策略 **买 `NO`**
- 若 `move_5m < 0`，说明标的短时急跌，策略 **买 `YES`**

翻成人话：
**这条 alpha 的第一原则就是反做冲击。**

## 4.2 入场阈值已经给了可直接复现的起点
默认参数里最重要的几条：
- `min_abs_move_5m = 1.8%`
- `max_abs_move_2h = 14.0%`
- `min_edge_percent = 2.8`
- `min_confidence = 0.44`
- `min_liquidity_usd = 2000`
- `max_entry_price = 0.92`

这套口径翻译过来就是：
- 没有至少 **1.8% 的 5m 冲击**，不做；
- 如果 **2h** 已经是特别大的大级别走势，不做；
- 盘口太差、不够便宜、不够有边际，不做。

这很适合我们先跑一个 honest baseline，因为它不是模糊的“等明显 spike”，而是已经给出可编码阈值。

## 4.3 它不是无脑抄反转，而是加了一层 reversion shape gate
`reversion_helpers.py` 里最关键的不是函数名字，而是这句关系：

> 只有当 `|move_5m| >= 0.55 * |move_30m|` 时，才算短时 impulse 足够主导。

再加上：
- 如果 `|move_2h| > 14%`，就拒绝；
- 如果 `require_reversion_shape=True`，没有 shape 就不进场。

翻成人话：
**它不是见 spike 就反手，而是要求“这次冲击更像局部尖刺，而不是更大趋势的一部分”。**

这条规则特别重要，因为它决定了这更像：
- `shock fade`
而不是：
- 单纯左侧摸顶 / 摸底。

## 4.4 edge 计算虽然粗，但已经能当最小实验骨架
源码里的 edge 近似是：
- 若有 oracle / `price_to_beat`：
  - `edge ≈ 0.6 * |move_5m| + oracle_diff_pct`
- 否则：
  - `edge ≈ 0.6 * |move_5m|`
- 再粗扣一个：
  - `net_edge_percent = edge - 0.25`

这不是 production 级成本模型，但对 intake 阶段有两个优点：
1. 它逼你把 **冲击幅度** 和 **合约当前误价** 放在同一个打分框架里；
2. 它默认就承认 **成本不是 0**，比很多 repo 只算 gross signal 更诚实。

## 4.5 exit 壳已经写全了
默认 exit：
- `take_profit_pct = 8.0`
- `stop_loss_pct = 4.0`
- `max_hold_minutes = 8.0`

这意味着作者没有把它写成“回归到收盘 / 回归到结算前”那种长拖尾逻辑，
而是明确承认：

> **这条 alpha 的生命很短，核心是快进快出，不是慢等均值。**

这点对 short-cycle desk 很友好，因为它天然就是一条几分钟级别的 time-boxed raw alpha。

## 4.6 sizing 不是补丁，而是策略的一部分
默认 sizing：
- `sizing_policy = kelly`
- `kelly_fractional_scale = 0.45`
- `liquidity_cap_fraction = 0.07`
- `max_markets_per_event = 24`

这说明作者默认就把这条线当成“会同时出现多标的候选，需要容量约束”的东西来写。

对 desk 的启发是：
**如果我们后面把它迁移到更传统的 perp / spot bar 策略，也别只抄 entry/exit，仓位分配和流动性上限也应该一起抄。**

## 5. 给 `1m / 3m / 5m / 15m` 的最小实验
## 5.1 这条线最适合先做什么实验
### 先测对象
优先顺序建议是：
1. **Prediction-market crypto 5m 二元市场**（最贴近源码原意）
2. **把同一逻辑迁移到常规 perp/spot 的 5m shock-fade proxy**（验证 alpha 是否可脱离二元容器）

### 数据源
- **Underlying 价格**：Binance public API / WebSocket
- **二元市场价格**：Polymarket / Kalshi 公共市场数据接口
- **公开性**：公开可得
- **更新频率**：秒级到分钟级，足够重采样到 `1m / 3m / 5m / 15m`
- **最小可复现实验口径**：
  - 用 Binance 算 `move_5m / move_30m / move_2h`
  - 用二元市场 mid/ask 作为入场价格
  - 以 8 分钟 time-box 检验是否出现可交易回归

## 5.2 第一版最小规则（建议直接上手）
### 版本 A：贴源码的 honest baseline
1. 计算：
   - `move_5m`
   - `move_30m`
   - `move_2h`
2. 仅当以下同时满足才进场：
   - `|move_5m| >= 1.8%`
   - `|move_5m| >= 0.55 * |move_30m|`
   - `|move_2h| <= 14%`
   - `liquidity >= 2000`
   - `entry_price <= 0.92`
3. 方向：
   - `move_5m > 0` → 做反向
   - `move_5m < 0` → 做反向
4. 成本前信号分数：
   - `edge = 0.6 * |move_5m| + oracle_diff_pct`
5. 成本后粗过滤：
   - `net_edge >= 2.8`
6. 出场：
   - `+8%` take profit
   - `-4%` stop loss
   - `8m` time stop

### 版本 B：给常规 crypto desk 的可迁移 proxy
如果暂时不碰二元市场，先做一个传统交易所 proxy：
- 用 `BTC/ETH/SOL` 的 perp 或 spot-perp 合约
- 把 `selected_price` 换成方向仓的入场价
- 仍保留：
  - `5m shock threshold`
  - `30m shape gate`
  - `2h regime cap`
  - `8m / 15m time-box`
- 用 future return / basis compression / microprice 回归之一做 exit proxy

这样能先回答：
**这个 alpha 是“只在预测市场容器里成立”，还是“底层冲击反转本身就有迁移性”。**

## 5.3 频率映射建议
- **1m**：做执行层重采样，观察更细入场点是否改善 fill 与回撤
- **3m**：做更激进的短反转版本
- **5m**：主实验频率，最贴源码
- **15m**：做低频稳健性版，把 `move_15m / move_1h / move_4h` 当作对应 shape 层级

## 5.4 先看哪 3 个指标
第一轮别上来就看 Sharpe，先看：
1. **平均入场后 8 分钟的回归幅度**
2. **条件分组后胜率**：按 `|move_5m|`、`move_30m`、`move_2h` 分层
3. **after-cost expectancy**：显式扣掉 taker fee + 半个 spread + 滑点

## 6. 这条线最容易犯的错
- **把它误读成 generic bottom-fishing**：不是所有急跌都该抄底；源码明确要求 `shape gate`。
- **把 30m / 2h 过滤删掉**：一删就很容易把“局部尖刺”做成“逆大趋势硬顶硬抄”。
- **忽略 time stop**：这条 alpha 的核心是几分钟内的回归，不是长持有解释故事。
- **把预测市场和传统 perp 完全等同**：binary market 的 payoff 结构和 perp 不一样，迁移时必须重新标定 TP/SL。
- **只算 gross edge**：源码虽然只粗扣 `0.25`，但至少承认成本存在；我们实测时必须做更诚实的成本拆解。

## 7. 我对 desk 的结论
如果今天只允许往池子里加 1 条新的 **single-asset / shock-driven mean reversion** 原型，我会收这条：

> **`5m spike reversion × 30m shape gate × 8m time-box`**

原因不是它有多花哨，而是：
- base alpha 清楚；
- 源码完整；
- 最小实验门槛低；
- 与我们最近过密的 pairs / basis / carry intake 形成互补；
- 还能顺手补上 `volume spike / recovery` 这个 backlog 方向的独立 raw alpha 化版本。

## 8. 下一步怎么测
1. **先用公开数据重建 30 天 BTC / ETH / SOL / XRP 的 `move_5m / 30m / 2h` + 二元市场报价面板。**
2. **按源码阈值跑第一版 baseline**：`1.8% shock + 0.55 shape gate + 8m hold`。
3. **做三档成本**：乐观 / 中性 / 悲观，别只看一套费率。
4. **对照两种 exit**：`8%/4%/8m` 固定壳 vs `time-box + oracle-gap compression`。
5. **最后做传统 perp proxy**：验证这条 alpha 是不是能从 prediction-market 容器外溢到更常规的 crypto execution stack。

## 9. 来源
### 仓库
- **Author / Owner**：Braedon Saunders
- **Year**：2026
- **Title**：*Homerun*
- **Type / Venue**：GitHub repo
- **Repo URL**：<https://github.com/braedonsaunders/homerun>
- **GitHub API metadata**：<https://api.github.com/repos/braedonsaunders/homerun>
- **README**：<https://raw.githubusercontent.com/braedonsaunders/homerun/main/README.md>
- **Strategy source**：<https://raw.githubusercontent.com/braedonsaunders/homerun/main/backend/services/strategies/crypto_spike_reversion.py>
- **Helper source**：<https://raw.githubusercontent.com/braedonsaunders/homerun/main/backend/services/strategies/reversion_helpers.py>

### 公共数据口径
- **Underlying 价格**：Binance Spot API / WebSocket docs：<https://developers.binance.com/docs/binance-spot-api-docs/web-socket-streams>
- **Prediction market 数据**：Polymarket docs：<https://docs.polymarket.com/>；Kalshi docs：<https://docs.kalshi.com/>
- **公开性**：公开可得
- **更新频率**：秒级 / 分钟级
- **最小可复现实验口径**：`Binance move features + binary market quotes + 8-minute post-entry reversion test`
