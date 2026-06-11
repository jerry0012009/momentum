# Rank 32b Canary / Phase 5 Minimal Live Order Gate

## 目标
执行一次真正的 live order，但把风险压到尽可能低：
- 只 1 笔
- 极小 notional
- 尽量不成交
- 拿到完整 live receipt chain

## 当前设计
- venue：Binance USDT-M perp
- order type：LIMIT + GTX（post-only）
- side：由配置指定
- price：挂在当前价外侧（默认 100bps）
- qty：自动抬到满足 Binance 最小下单限制（minQty / stepSize / minNotional）
- ack 后立即 cancel

## 关键约束
- 这一步已经是 live order，不再是 test order。
- 但目标不是成交，而是验证真实 live order admission + cancel + final status。
- 任何时候都不自动循环，不接现有 bot2 / bot3 / bot6 / bot7。

## 成功标准
- live order 被 Binance 接受
- 立刻 query 到 order snapshot
- 成功 cancel
- final status 显示 CANCELED / EXPIRED / NEW->CANCELED
- 账户余额变化近似为 0（不应出现真实成交）
