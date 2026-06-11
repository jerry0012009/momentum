# Rank 32b Canary / Phase 2 Minimal Receipt-Chain Loop

## 目标
把 Phase 1 的 `signal -> risk -> intention` 再往前推进一小步，变成一个最小但真实的订单生命周期实验：

- place
- ack
- query / status sync
- cancel
- final status

## 重要约束
- 这不是把整个 32b 项目重新拉回 paper trade 阶段。
- 这里只允许做 **最小轮次订单实验**。
- 当前默认模式是 `test/no-fill`：
  - 不部署资金
  - 不留下真实仓位
  - 目标只是拿到完整 receipt chain
- 与 bot2 / bot3 / bot6 / bot7 的既有定时任务链路完全隔离。

## 当前实现
- runner：`python scripts/run_rank32b_canary_phase2.py`
- broker adapter：`src/momentum/execution/canary32b/broker_adapter.py`
- 默认 adapter：`TestNoFillBrokerAdapter`
- 产物目录：`reports/artifacts/rank32b_canary/`

## 当前闭环口径
`intent -> ack -> status_sync -> cancel -> final_status`

## 下一阶段
- 接入真正的 broker/query surface（仍然先保持 isolated canary）
- 增加 TTL lifecycle / active order ledger / state resync
- 再决定何时把某一条最小实验接到独立 service/timer
