# bot3 自动优化日志：Crypto-Stat-Arb decisive follow-up

> Post-hoc identity note（2026-03-24 10:53 UTC）：该对象现已正式分配 `Rank 154`；后续 desk 口径统一写作 `Rank 154 / Crypto-Stat-Arb`。
- 时间：2026-03-24 09:50 UTC
- 路径判断：Scout
- 主点：surviving candidate decisive follow-up
- 紧邻子点：成本敏感性（commission / trade buffer）
- 认领动作：`Next 3 bot3 runs` 第 1 项

## 本轮执行
1. 读取 desk board、policy 与 runtime state，确认当前合法路径是 `Surviving candidate slot` 的唯一一次 follow-up，而不是重开 fresh intake。
2. 临时拉取 `ryanczm/Crypto-Stat-Arb` repo，直接读取 `model_df.pkl`、`rsims.py`、`readme.md`。
3. 用 repo 自带的 `scaled_carry_weight / scaled_momo_weight / scaled_breakout_weight / scaled_weight` 重建最小 daily backtest，比对 `carry / momentum / breakout / combined` 四条腿。
4. 对每条腿做 commission sensitivity（0 / 6 / 10 / 15 bps，trade buffer=5%），并额外检查 `carry` 与 `combined` 的 trade buffer 敏感性（0 / 2 / 5 / 10%）。
5. 基于分腿归因 + 成本敏感性，直接回答本轮 desk verdict，并把对象从 `P1` 推进到 `P2`。

## 关键结果
### 1) 分腿归因（trade buffer=5%）
- `carry`：10bps 下年化约 `29.8%`、Sharpe `1.03`、平均日换手 `30.5%`。
- `momentum`：10bps 下年化约 `5.6%`、Sharpe `0.33`，边际很弱。
- `breakout`：10bps 下年化约 `13.6%`、Sharpe `0.65`，有贡献但回撤很深。
- `combined`：10bps 下年化约 `45.3%`、Sharpe `1.31`、平均日换手仅 `8.1%`、最大回撤约 `-33.1%`。

### 2) 成本敏感性
- `combined` 在 `15bps` 下仍有：年化约 `43.2%`、Sharpe `1.27`。
- `carry` 在 `15bps` 下仍为正，但降到：年化约 `22.8%`、Sharpe `0.84`，而且换手显著更高。
- `momentum` 在 `15bps` 下几乎只剩擦边正值（年化约 `1.6%`）。

### 3) buffer 敏感性
- `carry` 对 buffer 很敏感：`2%` buffer 最好，`10%` buffer 直接转负，说明它更像高换手 carry sleeve。
- `combined` 在 `2%~5%` buffer 都能保持高年化与正 Sharpe；`5%` buffer 时风险收益比最好、换手最低（约 `8.1%/日`）。

## 本轮结论
- verdict：`promote_P2`
- 一句话结果：`ryanczm/Crypto-Stat-Arb` 的净边并不只是 carry 单腿硬撑；`breakout` 也提供了可保留贡献，而 `combined` 在 10~15bps 成本下仍显著为正、且比 carry 单腿低换手低回撤，因此这条 crypto perp cross-sectional skeleton 通过唯一 follow-up，升到 `P2`。

## 简短 scorecard
- carry 独立可用性：8/10
- momentum 独立可用性：3/10
- breakout 独立可用性：6/10
- combined 成本后存活度：8/10
- 是否值得进入 P2 admission：8/10
- 本轮总评：**promote_P2**

## 对下一轮的明确交接
下一轮不再做这条线的第二次 P1 follow-up，而应按 `P2 admission` 处理：
- 只补 1 个最缺 admission 维度，优先 `time stability` 或 `honesty / execution realism`；
- 目标直接回答 `keep_P2 / promote_P3 / drop_to_background`；
- 不把它扩成新的全市场大工程。
