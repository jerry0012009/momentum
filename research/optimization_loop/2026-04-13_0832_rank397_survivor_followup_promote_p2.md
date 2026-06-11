# bot3 执行日志 — Rank 397 survivor 唯一 follow-up（5m 执行层封口）

- 时间：2026-04-13 08:32 UTC
- 执行动作：`cycle_plan` 第 1 项（survivor 唯一 follow-up）
- 目标对象：`Rank 397 / ETH downside outlier fade × Europe-hours veto`

## 结论（会改变系统认知）
- `Rank 397` 已完成 survivor 唯一 follow-up，并在统一 `12bps round-trip` 成本口径下保留可执行费后正边际，按规则从 `P1 survivor` **升级为 `Active P2`**（`promote_P2`）。
- admission 入口假设收口为：**仅保留 `next-5m immediate` 执行分支；`micro lower-low fail` 作为次级执行假设，不作为主入场。**

## 本轮最小证据
数据与口径：
- 标的：`ETHUSDT`（Binance USDⓈ-M）
- 事件定义：`15m logret <= -z*sigma(672)`，且 `Europe-hours veto`（仅 `UTC<08` 或 `UTC>=16`）
- 执行分支：
  1. `next5m_immediate`：事件确认后下一根 `5m` 立即入场
  2. `micro_lowerlow_fail`：前 3 根 `5m` 内先出现 lower-low 且同根收回到 event close 上方，再下一根入场
- 统一成本：`12bps round-trip`
- 持有：入场后 `60m`
- 滚动切片：按月统计 `net_mean_bps_12`

### 1) 5m 执行层主结果（聚合）
- `z=3.0, next5m_immediate`：`events=96`，`gross_mean=+31.47bps`，`net@12=+19.47bps`
- `z=3.0, micro_lowerlow_fail`：`events=66`，`gross_mean=+18.57bps`，`net@12=+6.57bps`
- 稳健性对比：`z=2.5/3.0/3.5` 三档均显示 `next5m_immediate` 的费后均值高于 `micro_lowerlow_fail`。

### 2) 最小 honesty / execution realism 子检查（本轮新增）
- 显式加入“信号确认延迟”与“可成交路径”差异：
  - `next5m_immediate` 平均延迟 `0` 分钟；
  - `micro_lowerlow_fail` 平均延迟约 `7` 分钟（`avg_delay_min≈7.20 @ z=3.0`），且触发后样本数下降（`96 -> 66`）。
- 结论：延迟确认并未提升费后质量，反而稀释了 edge；因此 admission 入口应优先 immediate 路径。

### 3) 滚动切片（time stability）
- 月度切片显示两分支均存在负月，说明该对象尚未达到 `P3` 级“近似无争议”稳定度；
- 但 survivor 本轮只要求回答“是否可执行且值得进入 admission”，在统一成本下 `next5m_immediate` 给出明确正费后均值与可交易事件密度，满足进入 `P2` 的门槛。

## 产出文件
- `reports/artifacts/literature/rank397_survivor_5m_exec_summary_2026-04-13.csv`
- `reports/artifacts/literature/rank397_survivor_5m_exec_monthly_2026-04-13.csv`

## 本轮判定
- survivor 唯一 follow-up：`done`
- 对象层级变更：`Rank 397` 从 `Surviving candidate` -> `Active P2`
- 本轮不执行 `P2 exit`（仅完成 survivor 收口与升级）

## 尾部执行
- 首页刷新（best-effort）：已尝试执行 `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`，进程未在预期窗口内返回并终止；按规则记为非阻断尾部失败，不回滚本轮 verdict/state/log。
- 邮件通知：`send_text_email.py` 执行成功（sent）。
