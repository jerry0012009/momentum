# 2026-03-17 04:52 UTC · Rank 23 volatility regime mid-band / cost-survival gate source intake

## 为什么这轮选这个
- 先按 `TRADING DESK BOARD` 检查席位：
  - `Paper Seat = EMA` 当前仍是 `waiting_not_due`
  - `Live Seat = 暂空`
  - 因此本轮不得在 `Run 1` 空转，默认应落到 `Run 2 / Scout Fast Lane`
- 先比较所有 active Scout 候选的边际价值：
  - `Rank 17`、`Rank 2` 都是 `P3 / narrow paper pilot`，但当前没有新的 `append/review need`
  - `Rank 7~22` 里能快筛的线已经基本完成 `clean replication + Light Stability Pack` 并回到 `park / evidence pool`
- 因此本轮最诚实的主点不是继续磨旧 P3 wiring，而是把新的 `paper / repo based 5m / 15m crypto` fresh intake 明确下来，并尽量让下一轮无需再花时间选题

## 开始前检查
- `git status --short` 显示 repo 工作区仍有大量与本轮无关的历史脏文件 / 未跟踪文件；本轮只做 selective 写入，不混提
- 最近 runs：
  - `2026-03-17_0437_rank22-clean-replication-park.md`
  - `2026-03-17_0416_rank22-updownwave-intake.md`
  - `2026-03-17_0412_rank21-clean-replication-park.md`
- 当前 desk 状态：
  - `Paper Seat = EMA running paper / waiting_not_due`
  - `Live Seat = 暂空`
  - `Scout Seat = fresh intake`

## 本轮主点 + 紧邻子点
- 主点：把新的 `Rank 23 volatility regime mid-band / cost-survival gate` 冻结成可执行的 source-intake 卡
- 紧邻子点：做 **1 次便宜 honest pocket check**，确认这条线至少值得进入下一轮 `clean replication`

## 为什么是 Rank 23，而不是继续碰旧线
- `Rank 17` 与 `Rank 2` 当前都已经进入 `P3`，继续认领大概率只会产出近义 `append/review` 文案，而不是改变 desk judgment
- `Rank 22` 刚完成 `clean replication + Light Stability Pack` 并如实压回 `park`
- 现有 shortlist 里更值得补的一类，不是继续强调 breakout 本身，而是把 **cost / regime 会不会留下 survival pocket** 压成一个更贴当前 desk 的环境门
- `Svogun & Bazán-Palomino (2022)` 已经在本地有 quant digest 与 `svogun2022_cost_regime_experiment` 现成证据，可低成本推进，不需要新数据源或重型下载

## 做了什么
### 1) 新增 deployable artifact：source intake card
新增：
- `reports/artifacts/literature/scout_rank23_vol_regime_source_intake_card.csv`

冻结定义：
- 候选名：`Rank 23 volatility regime mid-band / cost-survival gate`
- 来源：`Svogun & Bazán-Palomino (2022)` + 现有本地 `svogun2022_cost_regime_experiment`
- 目标市场：`BTC / ETH / SOL`
- 目标周期：`15m`
- `trade on`：保留现有 15m 方向层，只在 realized-vol state 没落入最差高摩擦 extreme pocket 时允许入场
- `trade off`：基线方向缺失，或 vol / cost-survival gate 失效

### 2) 做了 1 次便宜 honest pocket check
新增：
- `reports/artifacts/literature/scout_rank23_vol_regime_pocket_check.csv`

做法：
- 直接复用 `reports/artifacts/svogun2022_cost_regime_experiment/event_returns.csv`
- 只抽 `rolling_breakout_20`
- 按 `vol_state × bubble_proxy × cost_case` 聚合，检查是否存在至少一个 **不至于立刻塌掉** 的 pocket

### 3) 写回 shortlist 与作战板
更新：
- `reports/artifacts/literature/scout_seat_fast_cycle_crypto_shortlist_v1.csv`
- `docs/TODO.md`

同步内容：
- 新增 `Rank 23 volatility regime mid-band / cost-survival gate`
- 顶部 authoritative override 改为：当 `P3` 仍无真实 append/review need 时，下轮默认先做 `Rank 23 clean replication`
- `Next 3 bot3 runs` 新增 `2p` 条目，把当前诚实状态写清楚：`fresh intake accepted / pending clean replication`

## cheap pocket check 结果（只够支持继续，不够支持升格）
### 现有 60m 本地样本里，最值得看的 pocket
`rolling_breakout_20` 的 `low_vol + non-bubble` pocket：
- `365d / net_low`：`mean_return ≈ +0.12%`
- `730d / net_low`：`mean_return ≈ -0.01%`（接近打平）

### 反面 pocket
- `high_vol + bubble_proxy=True` 在 `365d / net_low` 约 `-0.22%`
- 同类 pocket 在 `net_high` 下更明显恶化

### 当前最诚实判断
这说明：
1. **cost / regime 确实会重排 survival**，不是纯文献空话
2. 但 pocket 还不够厚，尤其一拉长到 `730d` 就接近归零
3. 因此当前 verdict 只能是：
   - **值得进入下一轮最小 clean replication**
   - **还完全不配直接升成 `paper candidate`**

## 本轮 hard verdict
**Rank 23 当前状态 = `fresh intake accepted / pending clean replication`。**

不是 `paper candidate`，更不是 `narrow paper pilot`。
当前它只通过了：
- 来源清楚
- 规则能冻结成 `trade on / trade off`
- 有 1 个便宜 honest check 支持“值得做下一轮 clean replication”

## 下一轮应该怎么做
固定口径：
- 用现有 `BTC / ETH / SOL 120d 15m` cache
- 不追最新 bar，不新增重型下载
- 比较：
  - `baseline_mtf`
  - `no_high_vol_extreme`
  - `rv_midband_q20_80`
- 然后补 `Light Stability Pack`
- 最终只给三选一：`park / paper candidate / narrow paper pilot`

## 最小验证
已执行并通过：
1. 校验以下 artifacts 已写出：
   - `scout_rank23_vol_regime_source_intake_card.csv`
   - `scout_rank23_vol_regime_pocket_check.csv`
2. 校验 `docs/TODO.md` 已写入：
   - `Rank 23 volatility regime mid-band / cost-survival gate`
   - `fresh intake accepted / pending clean replication`
3. 校验 shortlist 已追加 `Rank 23`

## 风险 / 边界
- 本轮没有偷跑 clean replication，更没有提前给 alpha verdict
- cheap pocket check 来自既有 `60m` 样本，只能用于说明“这条线值得下一轮最小复现”，不能直接替代 `15m BTC/ETH/SOL` clean replication
- 如果下轮最小 clean replication 一跑就显示交易数失真、成本后归零或稳定性太差，应按 desk 规则直接 `park`

## 网页可见落点
- `docs/TODO.md` 顶部 `TRADING DESK BOARD / Next 3 bot3 runs`
- `reports/site/reading/svogun2022_cost_regime_experiment/report.html`（作为当前 source anchor）
- 首页索引将在本轮结尾刷新

## Git / 提交
- 本轮未提交
- 原因：当前工作区存在大量与本轮无关的脏文件 / 未跟踪文件，不适合安全 selective commit
