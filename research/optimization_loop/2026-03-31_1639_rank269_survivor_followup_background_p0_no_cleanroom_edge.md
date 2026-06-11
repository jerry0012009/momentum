# Rank 269：survivor 唯一 follow-up 完成，clean-room replication 未证明可迁移净边，回 background/P0

- 时间：2026-03-31 16:39 UTC
- 执行轮次：bot3 13 分钟自动执行
- 对应 cycle_plan 小点：`Rank 269 / cointegration pair + graduation + daily throttle`
- 结论：**`Rank 269 / cointegration pair + graduation + daily throttle` 的唯一 survivor follow-up 已完成：现有 clean-room 证据足以支持它是一条完整的 `cointegration spread MR + pair graduation + daily throttle` operating blueprint，但并没有证明这条对象在受控 crypto perp universe、统一成本与最小 pairbook 下仍保留可迁移净边；因此本轮用尽 survivor follow-up 后不升 `P2`，直接收口回 `background/P0`。**

## 这轮实际回答的问题
bot2 留给 bot3 的唯一问题是：
> 在统一成本口径下，小 pairbook clean-room replication 是否仍保留可迁移净边，以及 `graduation + daily throttle` 是否真的提升 after-cost retention，而不是只美化作者环境里的 pairbook 结果？

本轮答案是否定的，原因不是 blueprint 不完整，而是 **当前可独立审计的 clean-room 证据只证明“骨架能写清”，没有证明“净边能迁移”。**

## 为什么这一步足以收口
### 1) 同一底层 repo 已有公开数据 clean-room probe，而且结果直接指向净边不可迁移
当前 workspace 里已经有同一 repo 的本地 transfer check 产物：
- `reports/artifacts/quant_digests/repo-statarb-live-stack-probe_20260326_0020/summary.json`
- `reports/artifacts/quant_digests/repo-statarb-live-stack-probe_20260326_0020/pair_results.csv`

这组 probe 的口径虽然是 desk-oriented proxy，不是 faithful 复刻，但已经足够回答 survivor 轮要的核心问题：
- universe：`BTC / ETH / SOL / XRP / ADA / DOGE / LINK / LTC`
- bar：`15m`
- 训练/测试：`1000 / 499` bars
- 选对过滤：`ADF < -2.5`、`p < 0.1`、近 200 根最小 `quote volume > 10m USDT`
- 信号：`|z| >= 2` 入场，`z` 过零退出，`24` bars timeout，`|z| >= 3.2` 风险退出
- 成本：每次开/平各按 `4 bps` pair bundle 近似

结果不是“边变弱但还能活”，而是：
- 只筛出 **1 对** 候选：`ETHUSDT-SOLUSDT`
- after-cost 测试收益：**`-2.30%`**
- `trade_count = 24`
- `win_rate = 45.8%`
- `mean_trade_bps = -7.7`
- `median_hold_bars = 1`

也就是说，在一个已经相当克制、可承载、并且成本口径明确的 majors 小 pairbook 里，**我们看到的不是 repo headline 的迁移，而是“候选很少、持有很短、边很薄、成本后转负”。**

### 2) `graduation` 这一层目前没有被 clean-room 证据证明成真正的 after-cost enhancer
`Rank 269` 相比更早那张 repo 卡，新增强调的是：
- `recent expectancy graduation`
- `daily throttle / daily stop`

但当前可独立复核的证据仍停在：
- repo 规则说明了 graduation 怎么打标签；
- 作者环境里似乎有一套外部维护的 pairbook / recent trade history；
- 我们自己的 clean-room majors probe 只留下 1 对、24 笔交易、且成本后为负。

这意味着当前并没有足够证据证明：
1. `graduation` 在 desk-feasible universe 下真的能把坏 pair 剔掉并留下净边；
2. 它提升的是 **after-cost retention**，而不只是作者私有 pairbook 上的 recent performance cosmetics；
3. 在候选 breadth 极窄时，`graduation` 不是把“本来就没几对可做”进一步压成几乎不可交易。

换句话说：**graduation 仍像一个值得保留的 governance 组件，但还不是能把这条具体对象推过 `P2` admission 的独立证据。**

### 3) `daily throttle` 是风控/治理层，不是能救回负 raw edge 的 admission 证据
当前 clean-room 证据里，raw spread body 在受控 majors universe 下已经没有显示出可迁移 after-cost 净边。此时把注意力转向 `+1% throttle` / `-3% daily stop`，并不能诚实地回答 “这条具体策略值得升 `P2` 吗”。

更准确的说法应该是：
- `daily throttle` 依然可能是一个 **可复用 shared overlay**；
- 但如果 raw pairbook 本体在统一成本下没有保留可迁移净边，那么 overlay 只能改善回撤治理，不足以单独把对象升成 `P2`。

## 这轮改变了什么系统认知
改变点不是“cointegration pairs 全都不行”，而是：

> **`Rank 269` 真正值得留下来的，是 `recent expectancy graduation + daily throttle` 这套 pairs governance blueprint；但这条具体的 `cointegration pair + graduation + daily throttle` 对象，并没有在 desk-feasible clean-room pairbook 上留下足够强的成本后净边证据，因此不能继续占用前排。**

也就是说：
- 作为完整 operating skeleton，它是成立的；
- 作为当前 desk 的前排 admission 候选，它不够诚实；
- 应该保留到后排的是组件认知，不是这条对象继续前推。

## 最终出口决策
- `Rank 269`：**survivor 唯一 follow-up 用尽**
- 当前层级动作：**不升 `P2`，回 `background/P0`**
- 不再占用 `Surviving candidate slot`

## 一句话 result（供 runtime 回写）
`Rank 269` 的唯一 survivor follow-up 已证明：这条 repo 真正可迁移的是 `recent expectancy graduation + daily throttle` 这套 pairs governance blueprint，而不是已被 clean-room majors pairbook 证实的成本后净边；现有统一成本证据下 only surviving candidate `ETH-SOL` 仍录得 `-2.30%`、`-7.7 bps/trade`，因此本轮用尽 follow-up 后回 `background/P0`。
