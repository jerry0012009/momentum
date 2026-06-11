# Rank 190 survivor follow-up：BTC-shock ADA-underreaction 1m beta-hedged catch-up spread -> park_to_background

- 时间：2026-03-27 01:26 UTC
- 对象：`Rank 190 / BTC-shock ADA-underreaction 1m beta-hedged catch-up spread`
- 轮次角色：`Surviving candidate` 的唯一一次 cheap decisive follow-up
- 本轮结论：**`park_to_background`**

## 这轮做了什么
按 intake 里约定的最小公开复现实验，只做最便宜也最诚实的一刀，不把对象扩写回泛化“跨币 lead-lag family”——

- 数据：Binance Spot `BTCUSDT`、`ADAUSDT` 公共 `1m klines`
- 样本：最近 `30d`（`2026-02-25 01:24 UTC` 到 `2026-03-27 01:23 UTC`）
- bar 化：同时看 `1m` 与 `3m`
- 事件定义：
  - 用 BTC 单分钟收益绝对值的滚动 `95%` 分位定义 `shock`
  - 用最近 `12h` 的滚动 beta 构造 `beta * ret_BTC - ret_ADA`
  - 只保留 **同向但 ADA 欠反应** 的事件（BTC 上冲而 ADA 少涨，或 BTC 下冲而 ADA 少跌）
- 交易读法：做 `long laggard / short leader` 的 beta-hedged spread continuation
- 持有：`1m / 2m / 3m`
- 成本：显式扣 `4 / 8 / 12 bps round-trip`

## 结果
### 1m 事件口径
- 信号数：`1058`
- `hold 1m`：
  - gross mean：`+1.38 bps`
  - hit rate：`55.8%`
  - t-stat：`4.70`
  - **net @4bps rt：`-2.62 bps`**
  - **net @8bps rt：`-6.62 bps`**
- `hold 2m`：gross mean `-6.12 bps`
- `hold 3m`：gross mean `-5.47 bps`

### 3m bar proxy
- 信号数：`380`
- `next 3m spread`：
  - gross mean：`+0.61 bps`
  - hit rate：`50.3%`
  - t-stat：`0.81`
  - **net @4bps rt：`-3.39 bps`**

## 怎么读
这轮 cheap decisive follow-up 给出的答案已经够明确：

1. **论文里的“约 57 秒 lag”到现代 Binance 公开 bar 数据上，只剩很薄的一层超短 gross pocket。**
   - 最乐观的 `1m hold` 也只有 `+1.38 bps gross`；
   - 一旦显式扣掉最基本的 `4bps` round-trip，就直接转负。

2. **edge 没有自然延长到 `2m/3m`。**
   - 如果这条线真是一个仍然可交易的 `1m/3m catch-up spread`，至少不该在 `2m/3m` 持有上迅速翻成明显负值；
   - 现在更像是一个被更快 price discovery 与执行摩擦压扁的 micro pocket，而不是 desk 当前值得继续前排保留的 raw alpha。

3. **因此它不值得升 `P2`。**
   - survivor 这唯一一次 follow-up 的目标，本来就是回答“今天公开可得、显式成本后，还留不留得住”；
   - 现在答案是：**不够。**

## 运行态改写
- `Surviving candidate slot`：清空，不再保留 `Rank 190`
- `Background pool latest_parked`：更新为本对象
- `cycle_plan[1]`：写成 `done`

## 一句话结果（写回 state 用）
`Rank 190 / BTC-shock ADA-underreaction 1m beta-hedged catch-up spread` 的唯一 survivor follow-up 已收口：最近 30d Binance spot `1m/3m` 公开数据下，这条线只剩 `~1.38 bps` 的 1m gross pocket，显式扣 `4bps+` round-trip 后转负、且 2m/3m 持有直接失效，因此不值得升 `P2`，本轮直接 `park_to_background`。
