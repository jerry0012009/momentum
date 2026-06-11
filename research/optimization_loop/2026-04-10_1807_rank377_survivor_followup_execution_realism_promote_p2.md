# 2026-04-10 18:07 UTC · Rank 377 survivor follow-up（execution realism）

## 执行动作
- 对象：`Rank 377 / liquid staking basis mean reversion`
- 任务类型：survivor 唯一一次 follow-up（仅做 `honesty / execution realism` 最小 decisive 检查）
- 对齐 state 小点：`cycle_plan #2`

## 检查口径（最小且可复算）
数据源：
- `reports/artifacts/literature/liquid_staking_basis_probe_detail_2026-04-10.csv`

策略壳（与首判保持一致）：
- `15m`
- entry：`|z|>=3`
- exit：`|z|<=0.5` 或 `max_hold=32`

本轮只补执行现实性两件事：
1. **成交实现度门槛**：用 `entry bar volume` 作为最小可成交代理，要求 `entry_vol >= 1 WBETH`（并给出更高门槛对照）。
2. **容量/摩擦一致口径**：在 round-trip `4 bps` 基础上，加一个保守 participation impact 罚项（`impact_bps = 5*sqrt(q/entry_vol)`，q 为单笔名义 WBETH，q<=5%*entry_vol 才允许成交）。

## 结果摘要
基线（不加成交门槛）：
- trades=`95`
- gross=`+4.79 bps/笔`

加最小成交门槛（entry-only，避免事后按 exit 过滤）：
- `entry_vol>=1`：`82` 笔，gross `+5.31 bps/笔`，net@4bps `+1.31 bps/笔`
- `entry_vol>=5`：`66` 笔，gross `+5.94 bps/笔`，net@4bps `+1.94 bps/笔`
- `entry_vol>=10`：`61` 笔，gross `+6.10 bps/笔`，net@4bps `+2.10 bps/笔`

容量+impact（在 `4bps rt` 上叠加）：
- `q=0.05 WBETH`：`82` 笔，平均 impact `0.25 bps`，net `+1.06 bps/笔`
- `q=0.10 WBETH`：`76` 笔，平均 impact `0.27 bps`，net `+1.09 bps/笔`
- `q=0.20 WBETH`：`70` 笔，平均 impact `0.31 bps`，net `+1.29 bps/笔`
- `q=0.50 WBETH`：`61` 笔，平均 impact `0.34 bps`，net `+1.76 bps/笔`

## 本轮 verdict
- 一句话改变系统认知：
  - `Rank 377` 在 survivor 唯一 follow-up 的 execution realism 口径下仍保留正净边际（`entry_vol>=1` 时 net@4bps 约 `+1.31 bps/笔`，并在小规模 participation 约束下继续为正），不再是单一 decisive blocker。
- 去向：**`promote_P2`**（进入 `Active P2 slot`）。

## 对 runtime 的影响
- `Surviving candidate slot`：`Rank 377` follow-up 预算用尽并收口，槽位清空。
- `Active P2 slot`：切换为 `Rank 377`，`p2_rounds_since_level_change=0`，`p2_consecutive_keep_p2=0`，`p2_last_evidence_axis=execution_realism_fill_capacity`。
- `cycle_plan #2`：`status -> done`，写入上述 verdict 句。

## 尾部动作记录
- 首页刷新：`bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` 已触发但运行无输出且超时未完成，按 policy 记为非阻断尾部失败，不回滚本轮 verdict/state/log。
- 邮件通知：`[momentum-bot3-auto] Rank377执行现实性收口并升P2` 已发送。