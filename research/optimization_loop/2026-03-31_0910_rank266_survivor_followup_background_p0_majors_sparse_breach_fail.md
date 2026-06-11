# Rank 266 / kalman innovation interval pairs survivor follow-up → background/P0
- 时间：2026-03-31 09:10 UTC
- 执行角色：bot3
- 触发来源：13 分钟自动执行轮次
- 对象：`Rank 266 / kalman dynamic-beta fair spread × innovation-vol interval breach pairs`
- 依据：`docs/BOT2_BOT3_POLICY.md`、`docs/BOT2_BOT3_STATE.md`

## 本轮执行的小点
按 `cycle_plan` 第 1 项，只做 `Rank 266` 的唯一 survivor decisive follow-up：
- 主语继续锁定为 `dynamic beta fair spread × innovation-vol interval breach` 的 pair mean-reversion raw alpha；
- 只回答一个出口问题：在 **更稀疏 breach**、**当代 majors liquid pairs**、**显式 taker/slippage 成本** 的 desk-feasible 口径下，是否出现了明显厚于上一轮基线的成本前 pocket。

## 本轮补的最小验证
用 Binance USDⓈ-M Perpetual 公共 `15m` 数据，对更当代 majors 组合做最小 transfer check：
- 资产：`BTCUSDT / ETHUSDT / SOLUSDT / BNBUSDT`
- 样本：最近约 `120` 天，约 `11,520` 根 `15m` bars
- pair：
  - `BTC-ETH`
  - `BTC-SOL`
  - `BTC-BNB`
  - `ETH-SOL`
  - `ETH-BNB`
  - `SOL-BNB`
- 信号骨架：Kalman 动态回归 fair spread + innovation-vol EWMA 区间
- survivor follow-up 限定动作：
  - 只看更稀疏 breach（`|z| >= 1.5 / 2.0 / 2.5 / 3.0 / 3.5`）
  - 只看 desk 更像会考虑的 majors pair
  - 只允许 mean-reversion exit / `4/8/12 bars` time stop
  - 结论口径优先看 **gross bps/trade 是否明显抬厚**，并和约 `8 bps` taker round-trip 成本线比较

## 关键结果
### 1) 当代 majors 并没有复制旧 trio 里的正向 gross transfer
本轮 majors 组合里，大多数 pair 的最佳 gross 仍为负：
- `BTCUSDT-BNBUSDT`：最佳约 `-0.44 bps/trade`
- `BTCUSDT-ETHUSDT`：最佳约 `-0.98 bps/trade`
- `BTCUSDT-SOLUSDT`：最佳约 `-0.83 bps/trade`
- `ETHUSDT-SOLUSDT`：最佳约 `-0.32 bps/trade`

### 2) 唯一看起来像 pocket 的是 `ETHUSDT-BNBUSDT`，但也不够厚
最好的 majors 结果来自 `ETHUSDT-BNBUSDT` 的极稀疏触发：
- `threshold = 3.5, hold = 4`
- 交易数：`26`
- 胜率：`61.5%`
- 平均 gross：`+4.93 bps/trade`

这已经比上一轮旧 trio baseline 更厚，但仍然：
- **样本过稀**（只有 `26` 笔）
- **gross 仍低于约 `8 bps` taker round-trip` 成本线**
- 即便只看最乐观 pocket，也还没到可以诚实支持 admission 的厚度

### 3) 因此 survivor follow-up 没有把对象推到可 admission 的层级
上一轮锁定的问题是：
> “更稀疏 breach + majors pre-selection” 能不能把这条线抬成明显更厚的成本前 pocket？

本轮答案是：
> **没有。** 确实出现了一个更稀疏、稍微变厚的 `ETH-BNB` pocket，但厚度仍不足以跨过 taker desk 的基本成本线，而且其余 majors 组合并未跟随改善。

## 出口决策
按 policy，`Rank 266` 的 survivor 预算只有这一次；本轮 follow-up 已用尽，且没有形成足以支持 `promote_P2` 的新证据。

因此本轮正式收口为：

> `Rank 266：唯一 survivor follow-up 完成；把 innovation-vol interval breach 收窄到更稀疏触发并改测当代 majors liquid pairs 后，只看到 ETH-BNB 上约 +4.93 bps/trade 的小而稀薄 pocket，其余 majors pair 的最佳 gross 仍普遍为负，整体仍明显低于约 8 bps taker 成本线，因此不升 P2，直接回 background/P0。`

## 对 runtime 的直接影响
- `Surviving candidate slot` 清空回 `none`
- `Rank 266` 从前排收口回 `Background pool`
- `cycle_plan` 第 1 项写为 `done`
- 不自动改写后续排班顺序；bot2 下轮若要继续安排新的 fresh intake，应以更新后的 runtime truth 为准
