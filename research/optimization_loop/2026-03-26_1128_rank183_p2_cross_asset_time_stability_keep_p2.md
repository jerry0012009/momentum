# Rank 183 / cbeth-eth-rolling-fair-basis-mr — P2 admission (cross-asset + time stability)
- 时间：2026-03-26 11:28 UTC
- 对象：`Rank 183 / cbeth-eth-rolling-fair-basis-mr`
- 本轮角色：bot3 只执行当前 `cycle_plan` 中排在最前的 pending 小点；不改排班，只回答这条 `CBETH spot + ETH perp 15m rolling fair-basis MR` 是否只是单月/单时段幻觉，还是已具备足够诚实的时段稳定 pocket

## 结论
**单一收口 verdict：`keep_P2`。**

更具体地说：

> `Rank 183` 不是只靠单一方向或单一月份撑起来的幻觉；但它的稳定性明显集中在 **`15m / z>=2.0` 的更窄 pocket**。这足够让它继续留在 `Active P2`，但也把下一轮默认收口方向收得更紧：应按出口决策回答“这个窄版 spec 是否已经够格进 `P3`”。

## 本轮怎么检查
复用产物：
- `reports/artifacts/quant_digests/cbeth_eth_basis_probe_20260326_0850_15m/trade_log.csv`
- 上一轮 effectiveness 已确认：更保守口径可把 pair RT 视为约 `30 bps`

因此这轮不再看理想化 `20 bps`，而是直接把 `trade_log.csv` 里的 `net_ret`（对应 `20 bps` pair RT）统一再减 `10 bps`，得到 **`30 bps` pair RT** 下的月份、方向、UTC 时段切片。

## 结果
### 1) `z>=1.5`：不是彻底失效，但时间稳定性已经明显收缩
在 `30 bps` pair RT 下：
- **按月份**
  - `2026-02`：`220` 笔，mean `+17.23 bps`，win rate `85.5%`
  - `2026-03`：`188` 笔，mean `+2.31 bps`，win rate `46.8%`
- **按方向**
  - `long CBETH / short ETH`：`140` 笔，mean `+14.03 bps`
  - `short CBETH / long ETH`：`268` 笔，mean `+8.44 bps`
- **按 UTC 小时（仅看样本 >= 8）**
  - `24` 个小时桶里，只有 `05:00 UTC` 为非正：mean `-0.60 bps`
  - `04:00 / 07:00 UTC` 也只剩约 `+4.10 / +4.94 bps`

翻成人话：`z>=1.5` 并不是“完全靠一个方向或一个小时在硬撑”，但到了更保守成本口径后，它在 **3 月份** 已经明显变薄，部分时段只剩低个位数 bps，已经不适合作为当前 paper-spec 的主支柱。

### 2) `z>=2.0`：时间稳定性明显更像 admission / pre-paper 主 pocket
在 `30 bps` pair RT 下：
- **按月份**
  - `2026-02`：`121` 笔，mean `+27.78 bps`，win rate `100.0%`
  - `2026-03`：`99` 笔，mean `+10.19 bps`，win rate `69.7%`
- **按方向**
  - `long CBETH / short ETH`：`87` 笔，mean `+21.85 bps`，win rate `92.0%`
  - `short CBETH / long ETH`：`133` 笔，mean `+18.56 bps`，win rate `82.7%`
- **按 UTC 小时（仅看样本 >= 8）**
  - 共 `14` 个小时桶达到样本门槛
  - **没有任何小时桶为非正**
  - 最弱小时桶也仍约 `+7.70 bps`

翻成人话：如果把对象老老实实收窄成 `15m / z>=2.0`，它就不再像“2 月的一次性好运气”。虽然 **3 月份明显弱于 2 月**，但仍是正的；而且两个交易方向都站得住，小时切片也没有塌成只剩极窄一个点。

## cross-asset 这条轴怎么诚实解释
这条对象本体从一开始就不是“可横向搬到很多币”的 cross-asset stat-arb，而是 **单一 `CBETH spot + ETH perp` relative-value pair**。因此这轮能诚实回答的，不是“是否跨很多资产普适”，而是：
- 它**不是**单边方向幻觉；
- 它**不是**单一小时窗口幻觉；
- 它在最近两个月里虽有衰减，但 **`z>=2.0` 仍保有跨月份的正 pocket**。

也就是说：当前 object 已经更像一个 **单 pair、窄参数、可写 spec 的 pre-paper 候选**，而不是需要再去外推成“LSD basis 在很多资产都通用”的故事。

## 为什么这轮是 keep_P2，不是 promote_P3 / P1 re-scope / P0
- **不是 `promote_P3`**：这轮稳定性已经足以让对象继续留在前排，但它同时把事实收得更窄——真正站得住的是 `15m / z>=2.0`。在还没完成下一轮 `parameter stability + exit framing` 收口前，我不认为它已经强到可以跳过 spec 锁定直接进 `P3`。
- **不是 `P2->P1 re-scope`**：这里没有出现新的 scope 翻案；相反，是把当前 P2 对象的主 pocket 明确锁得更紧，而不是改写成另一个新对象。
- **不是 `drop_to_background`**：因为 `z>=2.0` 在更保守口径下仍穿透了月份、方向和小时切片，不符合“只剩单月幻觉/明显 fatal flaw”的条件。
- **是 `keep_P2`**：因为系统现在知道，`Rank 183` 的时间稳定性不是全盘脆弱，而是 **主 edge 仍在，但只能诚实地押注在更窄的 `higher-z` pocket 上**。

## 本轮改变系统认知的一句话
`Rank 183` 在更保守的 `30 bps` pair RT 下并非单月或单方向幻觉：`15m / z>=2.0` pocket 在 `2026-02` 与 `2026-03` 两个月、双向交易和可见小时切片里都仍为正；但 `z>=1.5` 在 3 月已明显变薄，因此当前对象应继续 `keep_P2`，且下一轮必须按更窄 spec 做出口决策。

## 产物
- 复用：`reports/artifacts/quant_digests/cbeth_eth_basis_probe_20260326_0850_15m/trade_log.csv`
