# 别把 `options-arb` 只读成“期权多 venue 大平台”：对 short-cycle crypto desk，更该先回答的是「same-strike / same-expiry 跨 CLOB IV gap 收敛」这条 raw alpha 壳，在公开 mark 口径下到底还剩多少

- 时间：2026-04-25 13:45 UTC
- 类型：2026 GitHub repo source audit（`docs/plan.md` + `crates/arb-scanner/src/lib.rs` + `bin/options-arb/src/main.rs` + `crates/connector-aevo/src/lib.rs` + `crates/connector-derive/src/lib.rs`）+ Deribit / Aevo public-options overlap probe（`BTC/ETH`）
- 主题类型：raw alpha
- 基础 alpha：**同一标的、同到期、同 strike 的期权，如果跨 venue 的隐波/报价出现短时可交易偏离，价格会向更深、更快的共识面收敛。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否（repo 已给出完整壳，但这轮公开数据快检显示：`mark-IV` 层几乎无边，真正值得测的是 `orderbook/local-lag/executable-quote` 层）
- 主题标签：raw-alpha/options/relative-value/stat-arb/cross-clob/implied-vol/convergence/deribit/aevo/derive/1m/3m/5m/repo/public-data/cost/risk
- 证据类型：repo source audit + public options portability probe

## 1. 这次看了什么
这轮主材料不是论文，而是一个 2026 新仓：

- **Author / Owner:** `daiwanwei`
- **Year:** 2026
- **Title:** `options-arb`
- **Repo:** <https://github.com/daiwanwei/options-arb>
- **Repo API metadata:** created `2026-03-10`, Rust workspace, description = `Crypto options arbitrage system`

我这轮重点读的不是“能接多少 venue”，而是 repo 里最像 desk 可复现实盘壳的那几段：

1. `docs/plan.md`
   - 直接把策略拆成：
     - `Cross-CLOB IV arb`
     - `CeFi vs AMM vol lag`
     - `Put-call parity`
     - `0DTE arb`
     - `Vol surface arb`
2. `crates/arb-scanner/src/lib.rs`
   - 明确把 **same instrument cross-venue IV spread** 写成扫描器；
   - `build_signal()` 的核心就是：`sell_bid_iv - buy_ask_iv - fees - slippage`；
   - 还顺手给了 `put_call_parity`、`cefi_amm_vol_lag`、`cross_venue_parity_dislocations`。
3. `bin/options-arb/src/main.rs`
   - 已经不是“指标玩具”，而是 paper-trading / metrics / risk-manager / executor 的骨架。
4. `crates/connector-aevo/src/lib.rs`
   - 明确了 Aevo 的公开入口：`https://api.aevo.xyz`、`wss://ws.aevo.xyz`。
5. `crates/connector-derive/src/lib.rs`
   - 明确了 Derive/Lyra 的公开接口：`wss://api.lyra.finance/ws`。

所以，这个 repo 对我们最有价值的地方不是“又一个期权 bot”，而是它把 **期权跨 venue 收敛** 这条 alpha 拆得足够实盘化：

> **base alpha 很清楚：同一份 option contract 的跨 venue vol / quote 偏离，最终应向统一面回归。**

## 2. 一句话结论
- **一句话核心结论：** 这条 alpha 本身成立得很清楚，且 repo 已把 signal / fee / slippage / risk / paper-trading 壳拆出来；但我用 **Deribit + Aevo 当前公开 mark 口径** 做诚实快检后发现：**`mark IV` 基本已经贴平，当前能做的不是“盯 mark 搬砖”，而是继续下钻 `orderbook/local-lag/executable-quote` 层。**
- **一句话证明方式：** repo 的 scanner 明确以跨 venue IV spread 为信号；但公开交集快检中，`BTC` 有 `840` 个重叠期权、`ETH` 有 `706` 个重叠期权，近 `7d` 合约的 `median abs IV gap` 基本都是 **`0.00` vol pts**，最大也只有 **`0.01` vol pts** 量级，说明 **公开 mark 面几乎没肉**。

## 3. 为什么这轮值得做
这轮值得做，不是因为“期权套利听起来高级”，而是因为它满足当前选题优先级里最关键的几条：

1. **raw alpha 很清楚。**
   这不是 filter，也不是讲故事；就是典型 `relative value / stat-arb`：
   - rich venue 卖
   - cheap venue 买
   - 赌收敛
2. **复现素材是公开可得的。**
   - Deribit public option summaries
   - Aevo public option markets
   - 如果继续往下测，还能直接接两边 websocket 盘口
3. **它和 desk 当前积累直接相关。**
   我们已经连续做过 `pairs / basis / funding / cross-venue quote-gap`；这条是同一类“law-of-one-price / relative-value”主线在 **options** 上的自然延伸。
4. **repo 的可落地性比很多“学术好看但落不了地”的论文强。**
   这里至少已经把 `scanner + risk + executor + paper trading` 的结构写出来了。

## 4. repo 真正值得拿走的是什么

### 4.1 不是“支持好多 venue”，而是把 alpha 本体写清楚了
`docs/plan.md` 里最关键的一行其实是：

- `Cross-CLOB IV | Deribit ↔ Derive ↔ Aevo | Same strike/expiry, IV diff > fees`

这句话很短，但交易上已经足够完整：
- 标的怎么对齐：**same strike / same expiry**
- 信号怎么定义：**IV diff**
- 何时出手：**大于 fees**

这比很多只会说“发现 mispricing”却不说怎么对齐的材料强得多。

### 4.2 `arb-scanner` 不是抽象概念，而是实打实在算“能不能做”
`crates/arb-scanner/src/lib.rs` 里 `build_signal()` 的逻辑很直接：

1. 读 `buy.ask_iv` 与 `sell.bid_iv`
2. 算 `iv_spread`
3. 用 `vega` 把 vol spread 变成大概的毛收益
4. 扣 `fees`
5. 再扣 `slippage`
6. 只有 `estimated_pnl > min_expected_pnl` 才发信号

翻成人话：
> 这不是“看见价差就激动”，而是先问一句：**扣完真实摩擦后还剩不剩。**

这也是它比很多 repo 更接近实盘的地方。

### 4.3 repo 还顺手给了一条很重要的 desk 启发：先别贪 multi-idea，先把最可验证的那一条做深
这个仓同时列了：
- cross-CLOB IV
- CeFi vs AMM vol lag
- parity
- 0DTE
- vol surface

但对我们现在的优先级，最应该先拿的不是最花的那条，而是：

> **跨 CLOB、同 contract、vol/quote 收敛**

因为它最接近：
- 独立复现
- 1m/3m/5m 快速实验
- 明确的成本建模
- 明确的 entry / exit / veto

## 5. 我做的最小 portability probe

### 5.1 数据与口径
这轮我故意先做 **最保守、最诚实** 的快检，不去碰私有接口，不去假装自己有真实挂单成交：

- **数据源 1：** Deribit public `get_book_summary_by_currency`
- **数据源 2：** Aevo public `/markets?asset=BTC|ETH&instrument_type=OPTION`
- **公开性：** 都公开可得，无需 API key
- **资产：** `BTC`, `ETH`
- **匹配口径：** `instrument_name` 完全一致，即 same underlying / expiry / strike / call-put
- **比较变量：**
  - 优先比较 **IV**，而不是直接比较价格；
  - 因为不同 venue 的价格展示/计价口径容易让人看花，但 **IV 更适合做单位统一比较**。

本轮生成了两份产物：
- 行级结果：`/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-25_134321_options_xvenue_iv_probe_rows.csv`
- 汇总结果：`/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-25_134321_options_xvenue_iv_probe_summary.json`

### 5.2 快检结果
#### 交集合约数量
- `BTC` 重叠合约：**`840`**
- `BTC` 近 `7d` 重叠合约：**`204`**
- `ETH` 重叠合约：**`706`**
- `ETH` 近 `7d` 重叠合约：**`166`**

#### IV gap 分布
- `BTC_all`：
  - `mean IV gap` ≈ **`-0.0019` vol pts**
  - `median abs IV gap` = **`0.00` vol pts**
  - `p90 abs IV gap` = **`0.00` vol pts**
- `BTC_near_7d`：
  - `mean IV gap` ≈ **`-0.0002` vol pts**
  - `median abs IV gap` = **`0.00` vol pts**
  - `p90 abs IV gap` = **`0.00` vol pts**
- `ETH_all` / `ETH_near_7d`：结论也几乎一样，**基本贴平**。

#### 当前最大 gap 也只有什么量级？
近 `7d` 里能看到的 top case，大多也只有：
- **`0.01` vol pts** 左右

例如：
- `BTC-26APR26-76000-C`：Aevo `28.61` vs Deribit `28.62`，gap = **`-0.01` vol pts**
- `BTC-26APR26-77000-P`：Aevo `19.81` vs Deribit `19.80`，gap = **`+0.01` vol pts**
- `ETH-28APR26-2325-P`：Aevo `44.06` vs Deribit `44.07`，gap = **`-0.01` vol pts**

### 5.3 这组数说明什么
这组数基本把一个“太天真”的版本直接否了：

> **如果你以为只盯公开 mark / summary 面就能稳定抓到跨 venue 期权 vol 偏离，那这轮结果不支持。**

更直白点说：
1. **raw alpha 的理论没问题；**
2. **但公开 mark 面已经非常有效；**
3. 真正可能还剩 edge 的，不是 `mark IV convergence`，而是：
   - 本地 orderbook 不同步
   - 薄盘口瞬时穿档
   - venue 更新时延
   - maker/taker 费用差
   - 某边挂单为空、某边仍残留旧价

也就是说，真正该测的是：

> **可执行 quote gap / local lag，不是 summary page 上的 mark gap。**

## 6. 对当前 desk 最值钱的 desk 化读法
这轮最值钱的不是“找到一个立刻能跑的 options alpha”，而是把这条思路从概念拆成了两个层级：

### 层 1：不要把 `mark-IV spread` 当 alpha 本体
它更像：
- 研究入口
- 监控基准面
- sanity check

但不是最该下注的地方。

### 层 2：真正值得下注的是 `executable quote divergence`
也就是：
- 同一 option
- A venue 能买到的真实价
- 和 B venue 能卖掉的真实价
- 扣掉 fee / slippage / hedge 成本
- 还要剩 enough edge

这才是这条策略在 `1m / 3m / 5m` 上真正能不能活下来的地方。

## 7. 最小可落地策略壳，应该怎么写
如果继续做，我会把它写成下面这个实盘骨架，而不是“盯一个 IV diff 就冲”：

### 7.1 universe
- 先只做 `BTC / ETH`
- 先只做 **近 `0DTE ~ 7DTE`、ATM 附近**
- 不碰太深虚值、也不碰远月

### 7.2 signal
- 同 contract 跨 venue 对齐
- 优先看：
  - executable bid / ask price
  - 对应换算出的 bid-IV / ask-IV
- 触发条件：
  - `sell_bid_iv - buy_ask_iv > fee + slippage + safety buffer`

### 7.3 entry
- 默认 **maker-first on rich venue**
- 另一侧：
  - 能同步对敲就同步
  - 否则先用 underlying / perp 做临时 delta hedge

### 7.4 exit
- gap 回到阈值内就平
- 或者 TTL 超时（比如 `30s ~ 180s`）强平
- 或 book 消失 / 深度掉到阈值下直接撤退

### 7.5 sizing
- 以最薄一边的可成交 size 为上限
- 再叠加：
  - net delta limit
  - vega limit
  - venue inventory cap

### 7.6 risk / veto
- 如果其中一边 orderbook 为空，直接 veto
- 如果需要全 taker 才能成交，默认 veto
- 如果 hedge venue 延迟高 / 盘口跳太快，默认 veto

## 8. 下一步怎么测
下一步别再盯 summary API 了，应该直接做 3 个更关键的最小实验。

### 实验 A：100ms book-level gap replay
- 同时接：
  - Deribit `ticker/book` websocket
  - Aevo `orderbook-100ms`
- 只看 overlapping contracts
- 记录每次：
  - best bid/ask
  - executable spread
  - quote 存活时间
- 核心问题：
  - **有没有持续超过 `300~500ms` 的可执行 gap？**

### 实验 B：near-ATM / near-expiry router
- 只保留：
  - `0DTE ~ 3DTE`
  - `25Δ ~ 75Δ`
- 因为太深虚值和太远月虽然也可能有 gap，但常常只是“没人交易”。
- 核心问题：
  - **edge 是真来自收敛，还是来自 illiquidity 假象？**

### 实验 C：fill-model honesty check
- maker fill 假设：挂单后最多等 `300ms / 500ms / 1s`
- taker hedge 假设：扣保守 fee + 半档/一档滑点
- 核心指标：
  - signal count
  - fill rate
  - post-cost bps
  - inventory overhang
- 核心问题：
  - **这条 alpha 是不是只有“看起来有”，实际上吃不到？**

## 9. 我的判断
这轮我会给一个很明确、但不夸张的判断：

> **`options-arb` 里的 cross-CLOB IV convergence 是一条合格的 raw alpha 候选；但当前公开 mark 口径下几乎已经被抹平，所以这轮最该保留的不是“mark spread 搬砖”，而是“book-level executable gap + local-lag replay”这个下一步。**

换句话说：
- **题是对的**；
- **第一层实现方式太天真就不对**；
- **真正值得继续投研究时间的是 execution-heavy 版本。**

## 10. 风险与保留意见
- 这轮只用了 **公开 summary / markets 数据**，还没上真实双边 orderbook replay。
- Aevo 公开 `markets` 更接近 mark 面，不等于真实可成交深度。
- Derive 这轮还没纳入实时交集检验，所以目前更像 `Deribit ↔ Aevo` 的保守 sanity check。
- 期权跨 venue 收敛很容易沦为“理论正确、实盘卡在成交与延迟”的典型 execution 策略，必须严防把不可成交的 paper edge 写成 alpha。

## 11. 本轮产物
- 研究笔记：`/root/clawd/jerry/momentum/research/quant_digests/2026-04-25_1345_crossclob-iv-gap-shell-realitycheck.md`
- 行级探针：`/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-25_134321_options_xvenue_iv_probe_rows.csv`
- 汇总探针：`/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-25_134321_options_xvenue_iv_probe_summary.json`

## 12. 来源
### Repo / code
- daiwanwei (2026), **options-arb**. GitHub repo: <https://github.com/daiwanwei/options-arb>
- Implementation plan: <https://raw.githubusercontent.com/daiwanwei/options-arb/main/docs/plan.md>
- Arb scanner: <https://raw.githubusercontent.com/daiwanwei/options-arb/main/crates/arb-scanner/src/lib.rs>
- Main binary: <https://raw.githubusercontent.com/daiwanwei/options-arb/main/bin/options-arb/src/main.rs>
- Aevo connector: <https://raw.githubusercontent.com/daiwanwei/options-arb/main/crates/connector-aevo/src/lib.rs>
- Derive connector: <https://raw.githubusercontent.com/daiwanwei/options-arb/main/crates/connector-derive/src/lib.rs>

### Public data endpoints used in this round
- Deribit public book summary by currency: <https://www.deribit.com/api/v2/public/get_book_summary_by_currency?currency=BTC&kind=option>
- Deribit public book summary by currency: <https://www.deribit.com/api/v2/public/get_book_summary_by_currency?currency=ETH&kind=option>
- Aevo public markets: <https://api.aevo.xyz/markets?asset=BTC&instrument_type=OPTION>
- Aevo public markets: <https://api.aevo.xyz/markets?asset=ETH&instrument_type=OPTION>
