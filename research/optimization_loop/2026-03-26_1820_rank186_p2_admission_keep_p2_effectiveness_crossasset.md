# Rank 186 / CME expiry postfix short BTC — P2 admission keep_P2（effectiveness + cross-asset）
- 时间：2026-03-26 18:20 UTC
- 对象：`Rank 186 / CME expiry postfix short BTC`
- 本轮角色：bot3 对 `Active P2` 做第一轮 admission，只回答这条 `last Friday 16:00 London -> post 60~120m short BTC` exact-time 事件策略在最小成本后 effectiveness 与 spot/perp cross-asset stability 上，是否已足够接近 `P3`

## 结论
**单一 admission verdict：`keep_P2`。**

当前更诚实的说法是：`Rank 186` 已经通过了“值得继续做正式 admission”的门槛，但**还没到可以直接升 `P3 / paper launch queue`** 的程度。原因不是方向塌了，而是当前能支持 `P3` 的证据仍主要集中在 **同一段样本、同一组固定参数、同一类 timestamp 假设**；因此这轮先把 `effectiveness + cross-asset stability` 收口为正面结论，并把剩余 blocker 明确缩小到 `time / parameter / honesty` 三项。

## 本轮补的 admission 证据
### 1) effectiveness：最小成本后，60m / 120m 都仍是正的
直接从 `btc_expiry_vs_friday_events.csv` 的 `14` 个月度事件上，按“到期后做空”的单次事件收益粗算：

- **Binance perp**
  - `post60` gross mean ≈ **+21.00 bp**；扣 `4 / 6 / 8 / 10 bp` 后 net mean 仍约 **+17.00 / +15.00 / +13.00 / +11.00 bp**
  - `post120` gross mean ≈ **+21.37 bp**；扣 `4 / 6 / 8 / 10 bp` 后 net mean 仍约 **+17.37 / +15.37 / +13.37 / +11.37 bp**
- **Binance spot`（做空需替代实现，但先作为方向对照）**
  - `post60` gross mean ≈ **+20.79 bp**；扣 `4 / 6 / 8 / 10 bp` 后 net mean 仍约 **+16.79 / +14.79 / +12.79 / +10.79 bp**
  - `post120` gross mean ≈ **+21.23 bp**；扣 `4 / 6 / 8 / 10 bp` 后 net mean 仍约 **+17.23 / +15.23 / +13.23 / +11.23 bp**

翻成人话：**这条线不是靠 1~2bp 薄 edge 勉强活着**。哪怕先用比较粗糙但不算乐观的 `6~10bp` round-trip 成本去压，它在当前样本均值上仍然留有双位数 bp 的缓冲。

### 2) cross-asset stability：spot / perp 方向与厚度几乎重合
从 `expiry_minus_placebo_summary.csv` 看，spot / perp 的 expiry 相对普通周五同钟窗口差值几乎一模一样：

- `post60 mean diff`：perp **-36.45 bp**，spot **-36.24 bp**
- `post120 mean diff`：perp **-41.36 bp**，spot **-41.16 bp**

进一步看逐月事件，`14/14` 个月度事件里：
- `post60` 的 spot / perp **方向一致率 = 14/14**
- `post120` 的 spot / perp **方向一致率 = 14/14**

这意味着本轮 admission 要回答的 cross-asset 问题，已经有了一个很强的最小答案：**这不是单 venue 偶发 artefact；至少在 Binance 的 spot/perp 两套市场上，事件后弱势方向完全同向。**

## 为什么这轮不是 promote_P3
不是因为对象不值得，而是因为离 `P3` 还差的 blocker 已经很具体：

1. **time stability**：当前月度样本主要落在 `2025-01` 到 `2026-02`，虽然 `2025` 与 `2026 YTD` 都没翻向，但总样本仍只有 `14` 次，历史不够长。
2. **parameter stability**：当前结论主要围绕 `post60 / post120` 两个固定持有窗；还没回答 `entry delay`、`hold window`、`pre-ramp threshold` 是不是单点参数最优幻觉。
3. **honesty / execution realism**：这条线高度依赖 `last Friday 16:00 London` 的事件戳与 DST 对齐；在进入 `paper launch` 前，必须把 timestamp / entry slicing / 可成交口径再做一次更正式的因果核对。

也就是说，**剩余 blocker 已不再是 effectiveness 或 cross-asset**，而是明确收敛成 `time / parameter / honesty` 三项。这正符合 `keep_P2` 的定义，而不是开放式拖延。

## 为什么这轮也不是 drop_to_background
- 不是 `drop_to_background`：因为这轮 admission 新增的是会改变系统认知的正面证据——成本后仍厚、spot/perp 几乎镜像一致。
- 当前对象没有出现明显 fatal flaw；相反，它更像一个**已经基本坐实 edge，但还没做完上线前最后三项 admission** 的候选。

## 建议的下一步 admission 收口方向
下一轮若继续做 `Rank 186`，必须只围绕以下剩余 blocker 之一，不得回到已回答过的 effectiveness / cross-asset 轴：
1. `time stability`：把历史往前扩，并确认 `2026 YTD` 不是偶然续命
2. `parameter stability`：只做一次最小参数扰动（`entry delay / 60m vs 90m vs 120m / pre-ramp gate`）
3. `honesty / execution realism`：核对 London DST、event timestamp、入场切片与 production 可成交口径

## 本轮改变系统认知的一句话
`Rank 186 / CME expiry postfix short BTC` 第一轮 P2 admission 结论为 `keep_P2`：当前 `last Friday 16:00 London -> post 60~120m short BTC` 在 Binance spot/perp 上不仅 expiry-vs-placebo 差值几乎重合（`-36bp` 到 `-41bp`），而且按事件粗算后即使扣 `6~10bp` 成本均值仍为正，但由于剩余 blocker 已明确收敛到 `time / parameter / honesty` 三项，暂不直接升 `P3`。

## 复用产物
- `reports/artifacts/quant_digests/cme_expiry_postfix_short_20260326/btc_expiry_vs_friday_events.csv`
- `reports/artifacts/quant_digests/cme_expiry_postfix_short_20260326/bucket_summary.csv`
- `reports/artifacts/quant_digests/cme_expiry_postfix_short_20260326/expiry_minus_placebo_summary.csv`
