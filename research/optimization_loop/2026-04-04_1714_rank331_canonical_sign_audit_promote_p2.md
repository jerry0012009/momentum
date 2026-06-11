# Rank 331 canonical sign audit → promote_P2
- Time: 2026-04-04 17:14 UTC
- Target: `Rank 331 / spot-perp basis state × funding-pressure × delta-neutral flip`
- Action type: survivor 唯一一次 decisive follow-up
- Verdict: `promote_P2`

## 结论先说
这轮唯一 decisive blocker 已经收口：

- `robbie/main.py` 与 `robbie/research.ipynb` 在 **target label / prediction sign / position direction** 上是自洽的；
- 根目录 `main.py` 只是一个简化且方向写反的 stale demo，不应再被当成 canonical implementation；
- 因此这条对象并不是“方向实现混乱导致 edge 主语塌缩”的伪 alpha，而是 **canonical 语义明确的 basis drift / convergence raw alpha**，应从 survivor 直接升到 `Active P2`。

## 核查到的硬证据

### 1) notebook 的 target 定义是“未来 6h basis change”
`robbie/research.ipynb` 明确写的是：

```python
prediction_horizon = 6
labels = features_df['basis'].shift(-prediction_horizon) - features_df['basis']
labels.name = 'target_basis_change_6h'
```

这表示：
- label > 0：未来 6 小时 **basis widening**（perp 相对 spot 更强）
- label < 0：未来 6 小时 **basis convergence / narrowing**

所以 canonical target 不是价格方向，而是 **basis 本身未来变化的方向与幅度**。

### 2) `robbie/main.py` 的交易方向与这个 target 是同向的
`robbie/main.py` 中：

- `ensemble_pred` 经过 `tanh` 得到 `conviction`
- `conviction > threshold` 时执行：
  - `MarketOrder(self.btc_perp, quantity)`
  - `MarketOrder(self.btc_spot, -quantity)`
  - 并打日志 `LONG basis=...`
- `conviction < -threshold` 时执行：
  - `MarketOrder(self.btc_perp, -quantity)`
  - `MarketOrder(self.btc_spot, quantity)`
  - 并打日志 `SHORT basis=...`

也就是说 `robbie/` 版本对正预测的解释是：

> 预期 basis 上升 → long perp + short spot → long basis

这与 notebook 的正 label（未来 basis widening）是同向一致的。

### 3) 根目录 `main.py` 的方向实现与自己的 label 相冲突
根目录版训练目标写的是：

```python
df['target'] = (df['basis'].shift(-6) > df['basis']).astype(int)
```

这同样表示：
- `target = 1`：未来 basis 更高

但它下单时却写成：

- `pred == 1` → `short future / long spot`
- `pred == 0` → `long future / short spot`

所以根目录版把“预测 basis 上升”映射成了 **short basis**，与 label 语义正好反向。

这不是轻微命名差异，而是明确的 sign inversion。

## 对 `PnL sign / funding cashflow` 的解释
### PnL sign
在 canonical 语义下：
- `long basis = long perp + short spot`，当 perp 相对 spot 走强、basis widening 时应赚钱；
- `short basis = short perp + long spot`，当 basis 收敛 / narrowing 时应赚钱。

`robbie/main.py` 的持仓命名（`long_perp` / `short_perp`）虽然没有把 basis PnL 分解到腿级别打印出来，但其下单方向与上述 PnL 语义是一致的。

### funding cashflow
这轮 sign audit 没看到 `robbie/main.py` 在 realized PnL 里显式逐笔累加 funding cashflow；更像是把 funding 主要当成 explanatory feature / state variable，而不是回测里单独 ledger 化的现金流项。

这意味着：
- **sign 一致性 blocker 已解除**；
- 但 funding 是否被完整记账、以及成本后有效性如何，仍是下一阶段 `P2 admission` 里应继续诚实核查的维度，而不是继续卡在 survivor 的理由。

## 为什么这轮该直接 promote_P2
根据 policy，survivor 只允许一次最小 decisive follow-up；本轮必须给唯一出口 verdict。

这次 follow-up 的目标不是证明最终能赚钱，而是确认：
1. 这条对象有没有独立 raw-alpha 主语；
2. canonical sign 是否可自洽；
3. 是否值得进入更正式的 `P2 admission`。

现在答案是：
- 有：主语就是 **spot-perp basis future drift / convergence 的状态依赖可预测性**；
- 有：canonical 版本应锚定 `robbie/main.py + robbie/research.ipynb`；
- 值得：因为它仍保留完整的 `basis state / long-short switch / entry-exit-sizing-risk-cost shell / 15m discovery + 5m execution` clean-room 迁移路径。

所以 survivor blocker 已消除，不应继续停留在 `P1`，直接升为 `Active P2`。

## 进入 P2 后真正该看的 admission 维度
下一阶段不再重复 sign audit，而应转到更高杠杆的问题：
1. `effectiveness / expected return`：basis-only vs basis+funding 在 15m discovery 口径下，成本前后是否仍有 edge；
2. `cross-asset stability`：BTC-only 还是 ETH 也成立；
3. `time stability`：不同最近窗口是否稳定；
4. `parameter stability`：prediction horizon / threshold / hold time 是否脆弱；
5. `honesty / execution realism`：funding cashflow 是否被正确记账、双腿成本与可成交性是否真实。

## 本轮一句话 result
`Rank 331`：canonical sign audit 通过，`robbie/main.py + robbie/research.ipynb` 在 `future basis change → long/short basis direction` 上同向自洽，根目录 `main.py` 只是 sign inversion 的 stale demo；因此 survivor blocker 已解除，正式 `promote_P2`。
