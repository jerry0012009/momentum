# Strategy Spec (M1)

## strategy_id
`trend_momentum_v1`

## 目标
在单市场（crypto）上验证趋势动量策略从信号到交易闭环。

## 输入
- 标准化 K 线（`data/silver`）
- 策略配置（`config/strategies/trend_momentum_v1.yaml`）

## 输出
- 交易信号（long/flat）
- 交易日志（entry/exit, price, size, fee）
- 回测指标（累计收益、最大回撤、夏普、胜率）

## 非功能性要求
- 参数和回测结果可复现
- 日志可审计
- 模块可单测
