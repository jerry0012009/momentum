# Rank 32b Canary / Phase 1 Skeleton

## 这一步做什么
- 把 32b canary 从“长文档计划”变成一个能手动跑一轮的最小执行骨架。
- 先落地：
  - Signal Adapter
  - Risk Guard
  - Order Intention Layer
  - Event Bus / Audit Log
  - Dashboard JSON / 网页

## 这一步明确不做什么
- 不自动下真实单
- 不接管 bot2 / bot3 / bot6 / bot7 既有定时任务
- 不把整个项目退回 paper trade 阶段
- 不在这一轮实现 trailing / break-even / position sync 闭环

## 当前运行方式
- 手动运行：`python scripts/run_rank32b_canary_phase1.py`
- 结果写到：`reports/artifacts/rank32b_canary/`
- 网页看板：`reports/site/factors/rank32b_canary/report.html`

## Phase 1 交付物
- 统一信号 envelope（signal_id / trace_id / alpha_version）
- 风控拒绝理由标准化
- entry intention 标准化（但不下单）
- 结构化事件日志 JSONL
- 状态/摘要 JSON
- 人类可读看板

## 下一阶段
- Phase 2：最小订单闭环（place / cancel / query / sync）
- Phase 3：再决定 systemd timer / OpenClaw 巡检的分工
