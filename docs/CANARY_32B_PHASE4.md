# Rank 32b Canary / Phase 4 Minimal Real Order Experiment

## 目标
做一次最小、最克制、最安全的“真实下单通道实验”。

## 这轮的定义
- 使用真实私钥签名
- 使用真实交易所私有接口
- 但优先走 **Binance Futures TEST order**
- 不部署资金
- 不留下真实持仓

## 为什么这么做
这比直接发真实市价单更安全，但又比本地模拟更接近真实世界：
- API key / secret / signing 路径是真的
- 权限、签名、风控、参数校验都是真的
- 但不会成交，不会动资金

## 当前口径
- venue：Binance USDT-M perp
- endpoint：`POST /fapi/v1/order/test`
- 附带前后账户快照对比
- Phase 4 结束后仍然不自动进 live order

## 下一阶段
- 单次人工确认的 1 笔极小 notional live order
- 继续保留 kill switch / 手工确认 / 全量审计日志
