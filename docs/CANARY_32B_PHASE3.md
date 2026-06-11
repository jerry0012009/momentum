# Rank 32b Canary / Phase 3 Query Surface + Ledger + TTL

## 目标
在不直接进入真实下单的前提下，把 canary 推进到更接近真实运行的层：

- 连接真实私有 query surface（Binance / Lighter）
- 生成 venue health / account snapshot
- 维护本地 order ledger
- 计算 TTL lifecycle / expiry state

## 重要约束
- 这一步仍然不自动发真实订单。
- 允许复用 FR_Monitor 的 connector / private config，但 secrets 必须放在当前项目的本地私密路径，并加入 `.gitignore`。
- 这一步的意义是把 canary 从“假 broker 回执链”推进到“真 query + 真状态观察”，给下一步的一次性最小 live order 实验铺路。

## 当前实现口径
- 优先读取：`config/private/fr_monitor_config_private.py`
- 兼容桥接：`/root/jerry/wlfi/FR_Monitor`
- 当前只用到：
  - Binance private query
  - Lighter private query
  - Phase 2 订单链的本地 ledger / TTL 推导

## 下一阶段
- 单次人工确认的最小真实下单实验
- active order ledger 持久化 + restart recovery
- 更细的 TTL cancel / status sync loop
