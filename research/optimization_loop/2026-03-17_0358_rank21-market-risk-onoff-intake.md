# 2026-03-17 03:58 UTC · Rank 21 market risk-on/off regime gate intake

## 为什么这轮选这个
- 先按 `TRADING DESK BOARD` 检查席位与默认顺序：
  - `Paper Seat = EMA`，当前仍是 `waiting_not_due`，不能在 waiting-window 空转；
  - `Live Seat = 暂空`；
  - `Scout Seat` 默认拿主资源。
- 先比较当前 active Scout 候选的边际价值：
  - `Rank 2 combo_all` 与 `Rank 17 pullback recovery confirmation` 都已进入 `narrow paper pilot approved`，但当前都**没有真实 append/review need**；继续认领大概率只会回到低边际值 wiring。
  - `Rank 7~20`（除 Rank 2/17 外）都已完成 `clean replication + Light Stability Pack` 并压回 `park / evidence pool`；继续重开默认不会更快改变 desk judgment。
  - 因此本轮最诚实的默认主点，不是继续磨 P3，也不是转去 tiny-live plumbing，而是**新的 paper/repo based 15m crypto fresh intake**。
- fresh intake 之间的选择：
  - `Rank 5 / 6` 仍偏 prediction-market / 跨资产 proxy，不如当前 desk 更关心的 `crypto cost survival / market-state honesty` 贴主线；
  - 论文 `Svogun & Bazán-Palomino (2022)` 明确回答“交易成本与 bubble/regime 会改写技术规则生存性”，而 repo 里又已有 `market_risk_on_off_filter.py` 可直接复用；因此这条线的**实现距离最短、边际价值最高**。

## 开始前检查
- `git status --short` 显示 repo 中原本就存在大量与本轮无关的历史脏文件 / 未跟踪产物；本轮只做 selective 写入，不混提。
- 最近 optimization logs：
  - `2026-03-17_0334_rank17-narrow-paper-pilot.md`
  - `2026-03-17_0326_rank20-price-volume-divergence-park.md`
  - `2026-03-17_0320_rank19-box-consolidation-park.md`
  - `2026-03-17_0309_rank18-clean-replication-park.md`
- 当前 desk 状态：
  - `Paper Seat = EMA / waiting_not_due`
  - `Live Seat = 暂空`
  - `Scout Seat = fresh intake first`

## 本轮主点 + 紧邻子点
- 主点：把新的 `paper/repo based` 候选 **`Rank 21 market risk-on/off regime gate`** 压成可直接进入 clean replication 的 clean-room spec。
- 紧邻子点：把这个 intake 写回 `docs/TODO.md` 与 `scout_seat_fast_cycle_crypto_shortlist_v1.csv`，避免结果只留在日志里。

## 做了什么
### 1) 新增 deployable artifact / clean-room spec
新增：
- `scripts/build_market_risk_onoff_scout_spec.py`
- `reports/artifacts/scout_market_risk_onoff_15m/clean_room_spec_v1.csv`
- `reports/artifacts/scout_market_risk_onoff_15m/spec_meta.csv`
- `reports/site/factors/scout_market_risk_onoff_15m/report.html`

这轮把论文里最值钱的那部分压成了当前 desk 可直接执行的最小 clean-room spec：
- 不是把 regime/bubble 说成大而全分类器，而是先压成**1h market-state gate**；
- baseline 继续沿用现有 `multi_tf_momentum`；
- gate 只保留 3 个最小、可因果特征：
  - `trend_1h`
  - `ema_ok_1h`
  - `vol_ok_1h`
- 第一刀冻结四档最小 clean replication 对照：
  - `baseline_mtf`
  - `trend_only_gate`
  - `market_risk_2of3`
  - `market_risk_3of3`
- 执行口径继续沿用当前 Scout fast lane：
  - `next-bar open`
  - `1 ATR stop`
  - `2 ATR target`
  - `8-bar time stop`
  - `6 bps/side`

### 2) TODO / shortlist 写回
已同步更新：
- `docs/TODO.md`
  - `Next 3 bot3 runs` authoritative override 中写明：当前 latest intake = `Rank 21 market risk-on/off regime gate`
  - 在 `Run 2 / Scout Fast Lane` 中新增 `2n`，明确它已完成 `source intake -> clean-room spec`，下一步是 `clean replication`
  - 在候选阶段表新增 `Rank 21`，状态标成 `source intake / clean replication next`
- `reports/artifacts/literature/scout_seat_fast_cycle_crypto_shortlist_v1.csv`
  - 新增 `Rank 21 market risk-on/off regime gate`

### 3) reader-facing 页面同步
新增：
- `reports/site/factors/scout_market_risk_onoff_15m/report.html`

新页面直接说明：
- 为什么当前应该转 fresh intake，而不是继续补 `Rank 2 / Rank 17` 的低边际值接线；
- 为什么这条线先压成 gate，而不是发明新 alpha；
- clean replication 下一步该怎么最小实现；
- 哪些情况会直接 `park`，避免后续无限续命。

## 本轮 hard verdict
**当前最诚实的新 fresh intake，不是继续磨现有 P3 wiring，而是把『crypto 技术规则的成本后生存性依赖 market regime / bubble state』压成可直接进入 clean replication 的 `Rank 21 market risk-on/off regime gate`。它已通过 source intake，但还没有通过 clean replication，因此不能误写成 `paper candidate`。**

换句话说：
- 这轮不是宣称 `Rank 21` 已经赢；
- 这轮是把它推进到 **implementation-ready / clean replication next**；
- 相比继续磨 `Rank 2 / Rank 17` 或重开已 park 候选，这一步的边际价值更高。

## 为什么这轮不去做别的
- **没有继续做 `Rank 17`**：它已经是 `narrow paper pilot approved（ETH+SOL only）`，当前没有真实 append/review need；再做大概率是低边际值 wiring。
- **没有继续做 `Rank 2`**：同理，当前没有真正会改变 verdict 的最小检查或 append/review need。
- **没有切 `tiny-live plumbing`**：因为 `Scout Seat` 仍有更高边际价值的允许动作，未达到“允许动作都被卡住”的条件。
- **没有重开已 park 候选**：`Rank 7~20`（除 Rank 2/17 外）已给出 clean replication + Light Stability Pack verdict，再开默认只会回到 closeout copy。

## 最小验证
已执行并通过：
1. `python3 -m py_compile scripts/build_market_risk_onoff_scout_spec.py`
2. `python3 scripts/build_market_risk_onoff_scout_spec.py`
3. `grep -n "Rank 21 market risk-on/off regime gate\|latest intake = Rank 21\|source intake / clean replication next" docs/TODO.md`
4. Python 校验 `reports/artifacts/literature/scout_seat_fast_cycle_crypto_shortlist_v1.csv` 已写入 `rank=21`

## 工作区 / 脏文件说明
- 当前工作区本来就有大量与本轮无关的历史脏文件 / 未跟踪产物。
- 本轮只新增 / 修改与 `Rank 21 intake` 直接相关的最小集合：
  - `scripts/build_market_risk_onoff_scout_spec.py`
  - `docs/TODO.md`
  - `reports/artifacts/literature/scout_seat_fast_cycle_crypto_shortlist_v1.csv`
  - `reports/artifacts/scout_market_risk_onoff_15m/*`
  - `reports/site/factors/scout_market_risk_onoff_15m/report.html`
- 未做 git commit，避免把无关脏文件混提。

## 下一步建议
1. 下一轮若 `EMA` 仍是 `waiting_not_due`，默认优先认领：
   - `Rank 21 clean replication`
   - 最小对照：`baseline_mtf / trend_only_gate / market_risk_2of3 / market_risk_3of3`
2. 然后至少补 `Light Stability Pack` 一项；理想是把 `时间 / 参数 / 跨标的 / 成本-交易数` 四项一次补齐后给出 `park / paper candidate / narrow paper pilot` 三选一。
3. 若后续 `Rank 17` 或 `Rank 2` 真出现 append/review need，再回补 P3；否则不要提前切回低边际值 wiring。

## 网页可见落点
- `reports/site/factors/scout_market_risk_onoff_15m/report.html`
