# Rank 331 P2 admission（effectiveness × cross-asset）→ drop_to_background
- Time: 2026-04-04 18:33 UTC
- Target: `Rank 331 / spot-perp basis state × funding-pressure × delta-neutral flip`
- Action type: `Active P2` admission 第 1 轮
- Verdict: `drop_to_background`

## 一句话结论
`Rank 331` 的 canonical sign 没问题，但按 `BTC/ETH` 的最小 clean-room `15m discovery + 5m execution` 口径重建后，raw basis drift 信号虽然在两币上都能给出一致的**成本前**微弱正毛利，平均每笔只有约 `+1.3bps`，而双腿成交成本一加入就连 `2bps` 这种偏乐观口径都守不住；因此它不满足 `effectiveness / expected return` admission，直接从 `Active P2` 退回 `Background pool`。

## 这轮怎么测的
我没有再沿用 repo 的整套 ensemble 回测壳，而是围绕 `robbie` 的 canonical 语义做了一个更小、更诚实的 clean-room：

1. **标的**：`BTCUSDT`、`ETHUSDT`
2. **数据**：Binance public `spot klines`、`perp mark-price klines`、`fundingRate history`
3. **频率**：`15m` discovery
4. **目标**：未来 `24` 根 `15m`（即 `6h`）的 `basis_change = basis[t+24] - basis[t]`
5. **特征**：
   - `basis`
   - `basis_z`（48 根滚动）
   - `basis_chg_1h`
   - `basis_chg_6h`
   - `fundingRate`
   - `funding_pressure`
   - `cross_basis`（BTC 用 ETH basis；ETH 用 BTC basis）
6. **模型**：滚动 `10d` 训练窗的线性 clean-room（只为回答 alpha 主语是否保留，不追求复刻原 repo 模型容量）
7. **交易解释**：
   - `pred > threshold` → `long basis = long perp + short spot`
   - `pred < -threshold` → `short basis = short perp + long spot`
8. **PnL**：
   - `gross_return = signal * future_basis_change`
   - `funding_cashflow ≈ -0.75 * signal * current_fundingRate`（6h 持有期下的 funding 近似）
   - 成本敏感性：`2 / 4 / 8 / 12 bps` roundtrip

## admission 读数
### 1) 成本前：BTC / ETH 都只剩“方向对，但边很薄”
- `BTCUSDT`
  - 样本：`1333` 笔
  - 平均毛收益：`+1.29bps/trade`
  - 累计毛收益：`+17.15%`
  - 平均 funding 贡献：`+0.03bps/trade`
- `ETHUSDT`
  - 样本：`1339` 笔
  - 平均毛收益：`+1.27bps/trade`
  - 累计毛收益：`+16.98%`
  - 平均 funding 贡献：`-0.02bps/trade`

解读：
- **cross-asset consistency 其实不差**：BTC/ETH 都是同方向、同量级的毛利；
- 但 **effectiveness 太薄**：这更像一个“basis 微漂移分类器”，不是能直接扛双腿交易壳的净 alpha。

### 2) 成本后：连 2bps 偏乐观口径都守不住
- `BTCUSDT`
  - `2bps`：`-0.69bps/trade`，累计 `-9.15%`
  - `4bps`：`-2.69bps/trade`，累计 `-35.81%`
  - `8bps`：`-6.69bps/trade`，累计 `-89.13%`
  - `12bps`：`-10.69bps/trade`，累计 `-142.45%`
- `ETHUSDT`
  - `2bps`：`-0.75bps/trade`，累计 `-10.09%`
  - `4bps`：`-2.75bps/trade`，累计 `-36.87%`
  - `8bps`：`-6.75bps/trade`，累计 `-90.43%`
  - `12bps`：`-10.75bps/trade`，累计 `-143.99%`

这里最关键：
> admission 不需要它完美，但至少要看到“成本后不过度塌缩”的 pocket。现在 BTC/ETH 两边都没有；不是只有 ETH 坏掉、BTC 还能撑住，而是两边都被双腿成本系统性吃穿。

### 3) funding 不是救命项
repo 里 funding 是重要 explanatory feature，但在这版 clean-room 里：
- BTC 平均 funding 贡献只有 `+0.03bps/trade`
- ETH 是 `-0.02bps/trade`

也就是说：
- funding 在这条 admission 里没有把 `+1.3bps gross` 变成可交易净 edge；
- 它更像弱修饰项，不是足以让 `P2` 继续往前的 decisive blocker solution。

## 为什么这轮不能写 keep_P2
policy 明确要求：
- 这轮要直接回答 admission verdict；
- 如果 `effectiveness` 或 `cross-asset` 明确失败，就应直接 `drop_to_background`；
- 不能因为“方向准确率挺高 / sign audit 已通过”就继续拖成开放式研究。

这轮的实话是：
1. **不是 sign 错了**；
2. **也不是只有单币成立、跨币不成立**；
3. **而是 raw edge 本身过薄，无法覆盖最基本的双腿交易壳成本。**

因此失败点落在：
- `effectiveness / expected return`：失败
- `cross-asset stability`：方向一致，但只是“一致地太薄”，不能抵消 effectiveness failure

## 最终 admission verdict
`Rank 331`：canonical `basis widening / convergence` 语义成立，且 BTC/ETH clean-room 均能复现出同向的 basis-drift 毛利信号；但该信号平均只有约 `+1.3bps/trade`，funding 增量近乎为零，加入哪怕 `2bps` roundtrip 成本后两币都转负，因此这条 `spot-perp basis state × funding-pressure × delta-neutral flip` 不具备足够的 post-cost expected return，本轮直接 `drop_to_background`。
