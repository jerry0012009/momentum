# Rank 159 survivor follow-up — drop to background

- 时间：2026-03-25 05:29 UTC
- 轮次角色：bot3 survivor follow-up 执行
- 对象：`Rank 159 / BTC→ALT trade-count-sorted 1m lag follower`
- 本轮动作：执行唯一一次 survivor 级 decisive follow-up，并直接收口为 `promote_P2` 或 `drop_to_background`
- 产物：
  - `reports/artifacts/rank159_trade_count_lag_followup/rank159_followup_summary.json`
  - `reports/artifacts/rank159_trade_count_lag_followup/rank159_followup_per_symbol.csv`

## 本轮采用的诚实口径
由于自动轮次里只保证基础环境，本轮采用 **clean-room 最小可执行快检**，全部基于 Binance Futures 公共 `1m` K 线：

1. universe：按 `24h quoteVolume` 取 **Top-20 非 BTC 的 Binance USDT perpetual**；
2. liquidity proxy：每个币按最近 **5d median 1m trade count** 排序，分成 3 个 trade-count bucket；
3. leader event：取 `BTCUSDT` 最近 5 天 `1m` 收益绝对值 **top decile** 的 impulsive 分钟（阈值约 `9.69 bps`）；
4. follower honesty filter：只保留 **ALT 当根尚未完全同步** 的事件，即 `|ALT 当根收益| < |BTC 当根收益|`；
5. 交易定义：下一根按 BTC 方向进入，分别统计后续 `1 / 2 / 3` 根累计 signed return；
6. 成本口径：统一扣除 **6 bps round-trip**，避免把分钟级微弱统计噪音误判成可交易 edge。

> 这版不是论文全文复刻；它回答的是 policy 需要的唯一 blocker：**在 desk 可交易 perp universe 内，低 trade-count follower 的 lag edge 是否在保守成本后仍为正。**

## 结果
### 1) 低 trade-count bucket 确实比高 trade-count bucket 更像“慢半拍”
- 低 trade-count bucket（7 个币）的最佳 horizon 是 `h1`，**gross ≈ +0.98 bps/trade**；
- 中 bucket 最好也只有 **gross ≈ +0.74 bps/trade**；
- 高 trade-count bucket 则已经转成 **gross ≈ -0.42 bps/trade**。

翻成人话：**“谁更慢半拍”这个排序方向没死**，低 trade-count follower 的确相对更像论文说的 lagger。

### 2) 但 edge 量级太小，保守成本后一律转负
按统一 `6 bps round-trip` 扣费后：
- 低 trade-count bucket 最好只有 **`-5.02 bps/trade`**；
- 中 bucket 最好 **`-5.26 bps/trade`**；
- 高 bucket 最好 **`-6.42 bps/trade`**。

也就是说：**排序关系还在，但可交易性已经不在。** 这不是“还能再补一点研究”的状态，而是 blocker 已经被明确回答：
> 在当前 desk 可接受的 perp universe + 保守 taker 成本口径下，`trade-count-sorted BTC→ALT 1m lag follower` 没冻结出可升级到 `P2` 的成本后正收益 pocket。

### 3) 单币也没有给出足够强的例外 pocket
- `ONTUSDT`、`DUSKUSDT`、`HYPEUSDT` 等个别币在 gross 口径下有 `+2~4 bps` 的局部亮点；
- 但放到统一 `6 bps` round-trip 后仍全部转负，说明当前幸存的更像 **raw microstructure hint**，不是 desk 可直接承接的 pre-paper 候选。

## 结论
**结论：`drop_to_background`，不升 `P2`。**

原因很直接：
- 本轮确实验证到“低 trade-count follower 更慢半拍”的方向性；
- 但 policy 要的是能决定层级的结论，不是方向上“有点像”；
- 既然在 desk 可交易 perp universe 里、按保守成本后已经没有正的 `post-cost avg return / trade` bucket，那么它就不再配得上继续占用 survivor / P1 前排资源。

## runtime 应写回的变化
- `Rank 159`：从 `Surviving candidate slot` 直接移入 `Background pool`
- `Surviving candidate slot`：清空
- `cycle_plan[3]`：标记为 `done`
- `cycle_plan[3].result`：写成 `Rank 159 / BTC→ALT trade-count-sorted 1m lag follower` 在 desk 可交易 perp universe 内虽保留“低 trade-count 更慢半拍”的排序方向，但 6 bps 保守成本后三个 bucket 最佳 pocket 全为负，因此直接 `drop_to_background`，不升 `P2`

## 一句话结果
`Rank 159 / BTC→ALT trade-count-sorted 1m lag follower` 在 desk 可交易 perp universe 内虽仍保留“低 trade-count 更慢半拍”的排序方向，但 6 bps 保守成本后三个 bucket 的最佳 pocket 全为负，因此 survivor follow-up 直接收口为 `drop_to_background`，不升 `P2`。
