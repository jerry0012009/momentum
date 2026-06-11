# Rank 156 / Distance-first crypto pairs with trade-buffer governance fresh intake

- Time: 2026-03-24 16:59 UTC
- Slot: Fresh intake
- Rank: 156
- Target: `Distance-first crypto pairs mean reversion with trade-buffer/cost governance`
- Source digest: `research/quant_digests/2026-03-24_1633_pairs-distance-first-cost-buffer-raw-alpha.md`
- External sources:
  - Paper: <https://doi.org/10.1080/10293523.2023.2268386>
  - Repo: <https://github.com/ryanczm/Crypto-Stat-Arb>

## What it claims
- 基础 alpha 不是“先上 cointegration 再说”，而是更便宜的 `Distance-first` 选对后，利用 pair spread 偏离的短周期均值回归赚钱。
- 论文给出的强 claim 是：在 Binance crypto pairs 样本里，`Distance` 选对在 `1m/5m/60m` 都是前排方法，且工程仓库说明 `trade_buffer + commission/funding` 治理是能否把研究 edge 变成可交易 alpha 的关键。
- 对当前 desk 的直接价值是：它补的是 `pairs / relative-value / stat-arb` 的原始 alpha 素材池，而不是又一层泛 filter。

## What is actually evidenced
- 公开证据不是一句口号：digest 已经把论文中的方法排序、样本窗口、以及可直接借用的工程骨架都拆清楚。
- 更重要的是，作者侧与本地最小快检都把 **成本与换手** 放进主结论，而不是只报毛收益：
  - 论文层面说明 `Distance` 方法排序有优势；
  - 本地 5m 公共数据最小快检则明确显示：**在当前口径下 Distance 虽优于 correlation，但成本后仍为负**。
- 这说明它已经越过了“只有故事没有证据”的 fresh-intake 壳项目门槛，但还远没到 admission：真正的单一 blocker 不是 alpha 定义不清，而是 **trade-buffer / cost-governance 是否足以把负毛利拉回可生存 pocket**。

## Why not direct park
- 若本地快检显示 `Distance` 与替代方法同样失效，或 repo 连基本执行摩擦治理接口都没有，那就该直接 park。
- 但当前公开证据已经给出一个非常清楚、且只需一次便宜 follow-up 就能回答的 decisive question：
  - 在同一 public-data 口径下，补做 `cost ladder × trade_buffer` 二维治理检查后，是否还能找到穿越成本线的稳定 pocket？
- 这类问题适合占用 survivor 的唯一一次 follow-up；它不是开放式“再看看”，而是一个单一、可收口的 yes/no 检查。

## Intake verdict
`Rank 156 / Distance-first crypto pairs with trade-buffer governance` 本轮 fresh intake 结论为 **keep_P1**。

原因不是它已经有可交易收益，而是它已经拿出了足够具体且带执行摩擦口径的公开证据，并暴露出唯一高杠杆 blocker：**成本后为负是否只是未治理 turnover，还是 alpha 本身不过成本线。** 这值得消耗 survivor 的那唯一一次 follow-up，去做同口径 `cost ladder + trade_buffer` 决断；若仍不过线，就应直接 `drop_to_background`，不再拖长。

## Result sentence
`Rank 156 / Distance-first crypto pairs with trade-buffer governance` 已凭“Distance 排序优势存在但当前成本后仍为负”的公开与本地证据进入 `keep_P1`；它唯一值得做的下一步是同口径 `cost ladder × trade_buffer` decisive follow-up，而不是继续停留在 fresh-intake 壳项目层。
