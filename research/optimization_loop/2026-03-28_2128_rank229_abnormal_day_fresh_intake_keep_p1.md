# Rank 229 / abnormal-day continuation to close — fresh intake 首判 keep_P1

- 时间：2026-03-28 21:28 UTC
- 对象：`research/quant_digests/2026-03-28_0641_abnormal-day-continuation-to-close-alpha.md`
- 动作：fresh intake 首判
- 结论：`keep_P1`，分配正式 `Rank 229`
- 不升级原因：同一 skeleton 在 public `5m` Binance USDT perp 最近 `365d` 的最小复现里呈现明显 **ETH 强、BTC 很薄、LTC 反向**，说明它不是可以立刻按“BTC/ETH/LTC 通用异常日 continuation raw alpha”推进到 `P2` 的干净对象；但它在 ETH 上留下了足够大的净后口袋，仍值得保留一轮 survivor follow-up 去做 honest re-scope。

## 这轮做了什么
用公开 `Binance USDT perp 5m` 数据，对 `BTCUSDT / ETHUSDT / LTCUSDT` 跑了最小论文忠实版 proxy：

1. 以 `UTC day` 为 session；
2. `ret_from_open_t = close_t / open_day - 1`；
3. 用前 `30` 个日收益的 rolling std 作为 `sigma_day`；
4. 当 `|ret_from_open_t| >= k * sigma_day` 首次触发时按同方向入场；
5. 继续持有到当日 UTC 收盘；
6. 统计 gross 与扣掉 round-trip `8 bps / 12 bps` 后的单笔均值；
7. 只把离收盘至少还剩 `M` 根 bar 的事件纳入（`M ∈ {4,8,12}`）。

## 最关键结果（最近 365d，5m）
### BTCUSDT
- 最好口袋在 `k=2.0`：
  - `47` 笔事件
  - gross mean `+12.1 bps`
  - net after `8 bps` ≈ `+4.1 bps`
  - net after `12 bps` ≈ `+0.1 bps`
  - median 为负、胜率仅 `46.8%`
- 解读：BTC 只剩很薄的 residual edge，接近“稍有摩擦就没了”。

### ETHUSDT
- 最好口袋在 `k=1.25, M>=12`：
  - `106` 笔事件
  - gross mean `+75.8 bps`
  - net after `8 bps` ≈ `+67.8 bps`
  - net after `12 bps` ≈ `+63.8 bps`
  - median `+29.3 bps`，胜率 `55.7%`
- 更严格阈值 `k=1.5~1.75` 仍保留 `+40~52 bps` 的 net-8 单笔均值。
- 解读：ETH 上不是只剩论文包装；same-day continuation 在 public 5m perp proxy 上仍明显活着。

### LTCUSDT
- 全部主要口袋都是负的：
  - `k=1.5` 附近 gross mean 约 `-66 ~ -73 bps`
  - 扣成本后更差
- 解读：论文里的 `BTC/ETH/LTC` 三币同读法迁移到当前 perp 不成立，LTC 直接起反作用。

## 为什么这轮只能给 keep_P1
这条对象已经证明：
- **不是纯 event-clock 包装** —— ETH 上确实有独立 event-driven continuation pocket；
- 但也**不是可直接写成三大币通用 raw alpha** —— 跨资产稳定性明显不够，至少 LTC 明确反向，BTC 仅弱正；
- 因此当前最诚实的状态不是 `drop`，也不是直接 `promote_P2`，而是：
  - 先保留为 `Rank 229`
  - 把它缩成 **ETH-led liquid-major abnormal-day continuation candidate**
  - 用 survivor 的唯一一次 follow-up 去回答：这是不是一个可被 honest re-scope 后存活的单资产/窄资产事件 alpha

## 建议的唯一 survivor follow-up 方向
只允许做一次便宜但 decisive 的 re-scope 检查：

> 把对象从“BTC/ETH/LTC 通用 abnormal-day continuation”收缩成“ETH 优先、BTC 只作旁证”的候选，检查有效性是否依赖 `UTC day` 锚点，还是在 `rolling/alt session` 下也保留主要口袋。

如果 session / anchor 一换就塌，说明它更像日历会话效应；
如果 ETH 口袋在 alternative session 下仍基本保留，再考虑升 `P2`。

## 本轮 verdict
- 正式编号：`Rank 229`
- 层级：`fresh intake -> keep_P1 -> Surviving candidate slot`
- 一句话结果：`Rank 229` 不是可直接按 BTC/ETH/LTC 通用模板推进的完整 raw alpha，但 ETH 上仍保留明显的 same-day continuation pocket，值得以 `ETH-led` 的 honest re-scope 进入唯一一次 survivor follow-up。
