# 别把这份 market-making sandbox 只读成“做市回放工具”：对 short-cycle crypto desk，更该先拆的是「micro_signal fair-value shift × maker-first quote skew」这条 microstructure raw alpha 壳
- 时间：2026-04-21 18:42 UTC
- 类型：GitHub / repo source audit + Binance USDⓈ-M live public-depth probe
- 主题类型：raw alpha
- 基础 alpha：盘口里的 **微价格偏移（microprice edge）+ 深度不平衡（imbalance）+ OFI / aggressor flow** 会先于 mid price 漂移；交易上不是追涨杀跌，而是把这个短漂移翻成 **fair-value shift**，再用 maker-first skew 去吃下一小段方向优势和 spread capture
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：microstructure / microprice / imbalance / OFI / trade-flow / maker-first / market-making / quote-skew / Binance / 1m / 3m / 5m
- 证据类型：repo 工程骨架 + live public-depth first probe

## 1. 这次看了什么
这轮主来源是一个 2026 新仓：**FlorentinBrn (2026), `crypto-market-making-marex`**。它表面上是“Coinbase BTC 做市研究沙盒”，但真正值得 short-cycle desk intake 的，不是 UI、回放或 stress test，而是它把一个可交易的微观结构 alpha 写得很明白：

1. 先从盘口里抽一个 **combined micro signal**；
2. 再把这个信号直接映射成 **fair price / reservation price shift**；
3. 最后用 **inventory skew + dynamic spread + reduce-only risk** 把它落成完整 maker 策略。

也就是说，这不是“有个做市系统，顺手带点指标”；而是反过来：**先有 microstructure alpha，再把它包成做市壳。**

## 2. 核心结论
- **一句话核心结论：**这份仓最值钱的不是“会做市”，而是把 base alpha 明确写成了：`microprice edge + depth imbalance + OFI/trade-flow` 能预测未来几秒到几十秒的 mid drift，然后用 maker quote skew 去兑现，而不是用 taker 硬追。
- **一句话证明方式：**作者不是靠口头叙事，而是把信号直接写进 fair-price / reservation-price 更新公式，并补了 historical replay、walk-forward、stress、latency、inventory/risk 模块，说明它是可复现策略骨架，不只是指标展示。
- README 和源码里把核心逻辑写得很直白：
  - analytics 层给出 `microprice_edge_bps`、`imbalance_l3`、`ofi_ewma`、`trade_flow_signed`、`vpin`、`fast_vol_bps`
  - 组合信号默认近似：`micro_signal_bps = 1.0*microprice_edge_bps + 2.0*imbalance_l3 + 0.05*ofi_ewma + 1.5*trade_flow`
  - strategy 层把它翻成 `fair_price = mid * (1 + signal_shift_bps/10000)`，再叠 `inventory_shift_bps` 形成 `reservation_price`
  - 同时用 `inside spread / volatility / VPIN / imbalance` 动态拉宽半边 spread，并在风险吃紧时进入 `reduce-only`
- 我这轮做了一个超轻量 Binance USDⓈ-M live public-depth probe（`BTC/ETH/SOL`, 90 秒, top20 depth, 约 1Hz）：
  - 用 repo 的简化可迁移版本 `micro_signal_bps ≈ microprice_edge_bps + 2*imbalance_l3` 做 first check
  - `BTC` 在 `|signal| >= 1bp` 时，signed next `5s / 15s / 30s` 平均约 `+0.22 / +0.21 / +1.29 bps`，其中 `30s` 命中率约 `83.3%`
  - `ETH` 在 `signal <= -1bp` 这侧更显著，signed next `15s / 30s` 约 `+0.89 / +2.73 bps`，命中率约 `76.0% / 77.8%`
  - 全样本 `signal vs next 15s` 相关系数约：`BTC 0.263`、`ETH 0.175`、`SOL 0.162`
- **第一性结论：**这条线更像 **1m/3m child-execution alpha**，不是拿去直接替代 `15m` 父级方向信号；但它很适合做 `5m/15m` 父信号下的 maker-first 执行增益层。

## 3. 为什么和当前项目有关
这轮的价值很直接：我们最近 intake 了不少 `15m` raw alpha，但真正容易被成本吃掉的地方，往往不在“有没有方向感”，而在**最后怎么进、怎么挂、怎么不被毒流量咬死**。

这份仓给的是一个很实用的拆法：
- **alpha 本体**：盘口短时失衡会先于 mid 漂移
- **执行表达**：别 taker 追，先把 fair value 往预测方向偏一点，再用 maker skew 去收 spread + drift
- **风控表达**：inventory 过重时自动缩一边 / reduce-only；毒性和快波动升高时自动拉宽

所以它不是脱离 desk 的 HFT 学术玩具，而是正好补我们当前素材池里相对缺的一层：**microstructure raw alpha → maker-first execution shell**。

## 3.5 策略拆解（必填）
- 方向属性：微观结构 / 超短漂移 / maker-first relative edge
- 基础 alpha：`microprice edge + depth imbalance + OFI/trade-flow` 预示未来几秒到几十秒的同向 mid drift
- regime：高毒性（VPIN）、高快波动、极窄/极宽 inside spread
- filter / veto：当 `vpin` 过高、波动过高、风险状态触发 `can_continue=false` 时不继续挂；当库存吃紧时切 `reduce-only`
- risk / sizing / execution overlay：`inventory skew`、dynamic half-spread、touch join、aggressive join、queue-share fill sim、max exposure / max loss / health score

## 4. base alpha 到底是什么
先按要求明确回答一句：

> **这篇东西的 base alpha 是什么？**
>
> **答：是盘口失衡导致的短时 mid-price drift。**
>
> 更具体地说，是 `microprice edge + imbalance + OFI + aggressor flow` 这些微观结构变量先动，几秒到几十秒后的 mid 往往顺着它们偏移的方向走。

所以它不是纯 overlay，不是纯风控，也不是“有信号再决定怎么挂单”的次级模块；**它本身就是 raw alpha，只是表达形式更接近 maker quote skew。**

## 5. 这条壳为什么值得保留
### 5.1 它把 alpha 和执行连接得很近
很多仓把 alpha 和 execution 分两本书写：一个说“方向会涨”，一个说“怎么下单”。这份仓更实在：**信号直接进入 fair price**，因此策略不是“先判断方向、再随便挂”，而是“方向预测直接影响报价中心”。

### 5.2 它天然适合短周期 desk，而不是只能服务纯做市
你完全可以不照搬整套双边做市，只抽其中一层：
- 当 `micro_signal_bps` 与父级 `5m/15m` 信号同向时，更积极 join 对应一侧
- 当 `micro_signal_bps` 反向时，降低挂单侵略性，甚至 veto taker 追单
- 当 `micro_signal_bps` 很强但父级没信号时，可作为独立 `1m/3m` scalping sleeve

### 5.3 first probe 虽然很小，但方向是对的
这轮 live probe 只有 90 秒，当然远远不够下 production verdict；但至少回答了一个关键问题：**把 repo 里的 micro_signal 简化搬到 Binance perp top-book 上，不是完全失灵。** 这就够让它进入研究池，而不是停在“看起来像国外做市课设”。

## 6. 可复刻的最小实验
### 本轮 live probe 口径
- 市场：Binance USDⓈ-M perpetual
- 标的：`BTCUSDT / ETHUSDT / SOLUSDT`
- 数据：`fapi/v1/depth`，top20 深度，约 `1Hz` 连续 90 秒
- 可迁移信号：`micro_signal_bps = clip(microprice_edge_bps + 2 * imbalance_l3, ±6)`
- 评估：next `5s / 15s / 30s` signed mid return

### 本轮产物
- `reports/artifacts/quant_digests/2026-04-21_marex_micro_signal_probe.py`
- `reports/artifacts/quant_digests/marex_micro_signal_live_rows_2026-04-21.csv`
- `reports/artifacts/quant_digests/marex_micro_signal_live_summary_2026-04-21.csv`

## 7. first verdict：这些数字怎么读
### 7.1 不是拿来做 15m 主信号
这条线的天然频率是秒级到分钟级。你要是硬把它伪装成 `15m` 方向因子，反而会把它读错。

### 7.2 但它很适合给 `1m/3m` 执行层提供 admission / skew
当前更合理的读法是：
- `15m` 决定“该不该做这个币、做多还是做空”
- `1m/3m` 的 `micro_signal_bps` 决定“现在是 join、pass、还是小 size 试探”

### 7.3 负向信号一侧在 ETH 上更干净
这轮 probe 里 `ETH signal <= -1bp` 后续 `15s/30s` 的 signed drift 明显更厚，说明 **卖压驱动的短时失衡** 可能比买压更能迁移成有效 pocket。这个很值得后续专门拆 long/short 非对称。

## 8. 下一步怎么测
1. **先把数据频率提上来。**
   别再用 `1Hz REST` 当正式证据。下一轮至少抓 Binance websocket `depth + aggTrade` 连续 `2~6h`，这样才能把 repo 里的 `ofi_ewma + trade_flow + vpin` 全量迁过来。

2. **做 `parent signal × child micro-signal` 二层实验。**
   选一个已入池的 `5m/15m` raw alpha（例如 trend / breakout / MR 任意一个），比较：
   - 裸 next-open / taker entry
   - maker join + micro-signal 同向时入场
   - micro-signal 反向时 veto / 降 size
   先看成本后 improvement，不先看 gross。

3. **做 maker-first friction ladder。**
   这条壳最怕研究时默认“都能吃满 spread”。下一轮至少测：
   - fill ratio
   - queue drag
   - maker rebate / fee
   - adverse selection after fill

4. **拆 long/short 非对称。**
   当前小样本已经提示 ETH/SOL 在负向失衡上更像样；下一轮应分资产、分方向、分 inside-spread bucket 看 pocket。

## 9. 风险与保留意见
- 这轮 live probe 样本非常小，只能当 **first verdict**，不能当稳定性结论。
- 我只迁了 repo 组合信号里最容易公开复刻的两项：`microprice_edge + imbalance_l3`；真正完整版还应补 `OFI / trade-flow / VPIN / fast vol`。
- repo 主场是 Coinbase BTC-USD，desk 目标是 Binance perp；这个 transfer 需要更长时段验证。
- 即使 alpha 成立，也不代表净边成立；**microstructure alpha 最后死不死，很多时候死在 fill realism，而不是方向本身。**

## 10. 来源
- FlorentinBrn. (2026). *crypto-market-making-marex*. GitHub.
- Repo URL：<https://github.com/FlorentinBrn/crypto-market-making-marex>
- Readable URL：<https://github.com/FlorentinBrn/crypto-market-making-marex/blob/main/README.md>
- 关键代码：
  - `crypto_mm/data/analytics.py`
  - `crypto_mm/core/strategy.py`
- GitHub metadata：仓库创建于 `2026-04-20`，最近更新 `2026-04-21`

## 11. 一句话收尾
**这份仓最值得抄的不是“做市框架”，而是：把盘口短漂移 alpha 直接翻成 fair-price shift，再用 maker skew 去兑现，而不是继续用 taker 把 edge 全交给手续费和 adverse selection。**
