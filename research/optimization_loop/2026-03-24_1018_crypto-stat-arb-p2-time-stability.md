# bot3 自动优化日志：Crypto-Stat-Arb P2 admission（time stability）

> Post-hoc identity note（2026-03-24 10:53 UTC）：该对象现已正式分配 `Rank 154`；后续 desk 口径统一写作 `Rank 154 / Crypto-Stat-Arb`。
- 时间：2026-03-24 10:18 UTC
- 路径判断：Scout
- 主点：Active P2 slot admission follow-up
- 紧邻子点：time stability（按季度 / 年度切片）
- 认领动作：`cycle_plan` 第 1 项

## 本轮执行
1. 读取 desk board、policy 与 runtime state，确认当前合法路径是 `Active P2 slot` 的最小 admission follow-up，而不是重开 fresh intake。
2. 直接从 `ryanczm/Crypto-Stat-Arb` 公共仓库拉取 `model_df.pkl` 与 `rsims.py`，沿用上一轮同一套 `commission=10bps / trade_buffer=5%` 口径。
3. 用 repo 的 daily universe + funding + target weights 重建 `combined` 与 `carry` 回测，并按 `季度 / 年度` 切片检查时间稳定性。
4. 目标只回答 admission 问题：这条线该 `keep_P2 / promote_P3 / drop_to_background` 哪一个。

## 关键结果
### 1) `combined` 组合的时间稳定性：不是单边顺滑，但仍明显强于单腿 carry
- 全样本（2020-02 至 2024-02，10bps，buffer=5%）：年化约 `45.7%`，Sharpe `1.32`，最大回撤约 `-33.0%`，平均日换手约 `7.3%`。
- 年度切片：
  - `2020`：总收益 `+65.1%`，Sharpe `1.85`
  - `2021`：总收益 `+93.8%`，Sharpe `1.88`
  - `2022`：总收益 `-7.0%`，Sharpe `-0.12`
  - `2023`：总收益 `+44.0%`，Sharpe `1.60`
- 解释：它不是“每年都赢”的 P3 级平滑组合；`2022` 明确掉坑，但并没有把前后两段的正边完全抹掉。

### 2) 季度切片显示：负段真实存在，但坏的时候也主要是中段 regime，不是从头到尾都塌
- `combined` 的明显负季度主要集中在：
  - `2021Q3`：总收益 `-2.4%`
  - `2022Q1`：总收益 `-2.5%`
  - `2022Q3`：总收益 `-12.9%`
  - `2022Q4`：总收益 `-13.0%`
  - `2023Q2`：总收益 `-3.4%`
- 但正季度也足够硬：
  - `2022Q2`：总收益 `+24.3%`
  - `2023Q3`：总收益 `+25.6%`
  - `2023Q4`：总收益 `+10.1%`
- 读法：这条线更像“有 regime 依赖、但不是一次性样本幻觉”的组合骨架，适合继续留在 admission 层，而不是直接 handoff。

### 3) `carry` 单腿的时间稳定性更差，说明 `combined` 的价值不只是收益高，而是更抗时间波动
- `carry` 全样本（同口径）年化约 `30.4%`，Sharpe `1.04`，平均日换手约 `29.2%`。
- 年度切片：
  - `2020`：`-12.3%`
  - `2021`：`+129.4%`
  - `2022`：`-2.0%`
  - `2023`：`+30.2%`
- 负季度更深，包括 `2023Q4 = -20.7%`。
- 这说明上一轮看到的 `combined > carry` 不只是成本后更高收益，也包括 **time stability 更好 + 换手更低**；组合化确实在帮它削尖锐度，而不是纯粹叠收益。

## 本轮结论
- verdict：`keep_P2`
- 一句话结果：`ryanczm/Crypto-Stat-Arb` 在 10bps / 5% buffer 口径下，`combined` 组合跨年仍保持显著正边，且时间稳定性明显强于高换手 `carry` 单腿；但 2022 年与若干负季度说明它还没平滑到可直接升 `P3`，因此本轮 admission 更诚实的结论是继续 `keep_P2`，等待下一刀只补 `execution realism / honesty` 后再做 promote-or-park。

## 简短 scorecard
- time stability（跨年不只一段样本）：7/10
- regime robustness（有负段但未全线崩）：6/10
- combined vs carry improvement：8/10
- direct P3 readiness：4/10
- 本轮总评：**keep_P2，不升 P3，不退 background**

## 对下一轮的明确交接
若继续推进这条 `Active P2`，下一轮只补 1 个 admission 缺口：
- 优先做 `honesty / execution realism`：检查 daily close 执行假设、同日 funding 记账、以及 `trade_buffer`/成本口径是否过于友好；
- 目标直接回答 `promote_P3 / drop_to_background / 继续 keep_P2`；
- 不扩成多市场、多频率大重构。
