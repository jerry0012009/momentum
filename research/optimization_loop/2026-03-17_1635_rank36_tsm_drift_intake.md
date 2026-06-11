# 2026-03-17 16:35 UTC · Rank 36 TSM vs drift honesty-gate intake

## 本轮归属
- Desk lane：`Run 2 / Scout Seat fresh intake`
- 触发原因：
  - `Paper Seat / EMA` 当前仍是 `waiting_not_due`
  - 顶部 `TRADING DESK BOARD` 明确要求：当 `Run 1` 被 waiting-window 卡住时，不得空转；优先切到 `Scout Seat`
  - 当前 `Rank 30~35` 已完成本轮允许动作并 park，`Rank 6` 也已完成最小 clean replication 并 park，`Rank 17 / Rank 2 / Rank 29` 的 `P3 continuity` 预算不应继续消耗
  - 因此本轮按规则从 `research/quant_digests/INDEX.md` / 既有 seed 池里再认领 `1` 条新的 paper-based intake

## 开工前检查
- 已先读：`docs/AUTO_OPTIMIZATION_LOOP.md`、`docs/TODO.md` 顶部 `TRADING DESK BOARD`
- repo 状态：工作区仍有大量与本轮无关的既有脏文件 / 未跟踪文件；本轮只做 selective 写入，不混提
- due guardrail snapshot：当前 desk 没有 `due-now / overdue` lane；最近的后续 close 仍是 `美股 20:00 UTC / Crypto 00:00 UTC / A股 07:00 UTC`
- active Scout 边际价值比较（本轮前）：
  - `Rank 17 / Rank 2 / Rank 29`：属于 `P3 continuity`，不是这轮默认主资源
  - `Rank 30~35`：已完成当前允许动作并 park
  - `Rank 6`：external-data fallback 已做完最小 clean replication，当前 verdict=`park / evidence pool`
  - 结论：这轮最诚实动作是**重新打开 1 条 fresh paper-based intake**，而不是回到 `Run 3`

## 本轮主点 + 紧邻子点
- **主点**：新增一条 fresh paper-based scout intake：`Rank 36 / recent-return sign vs history-drift honesty gate`
- **紧邻子点**：把 intake 结果写回 `docs/TODO.md` 顶部 authoritative override，并同步 reader-facing 网页落点

## 为什么选这条线
来源：`Huang, Li, Wang, Zhou (2020), Time series momentum: Is it there?`

选择原因不是它能直接给出一条 ready-made alpha，而是它能给当前 desk 一个更便宜、更诚实的 admission 问题：
- 一条 `sign(momentum)` 邻近候选到底是在吃 `recent-return signal`
- 还是只是在吃更慢的 `history drift / beta`

这非常适合当前排班，因为：
1. 不需要外部新数据
2. 能复用现有 `BTC/ETH/SOL 120d 15m` cache
3. 下一轮可以直接做 **1 次最小 clean replication**，不需要先开新框架

## 冻结后的 source-intake 口径
### 候选名
- `Rank 36 recent-return sign vs history-drift honesty gate`

### 三档最小 clean-room 对照（仅 source intake，尚未开跑）
1. `recent_sign_only`
2. `history_drift_only`
3. `recent_and_drift_agree`

### trade on / trade off
- `trade on = recent-return sign 有方向（baseline）/ history-drift sign 有方向（对照）/ 两者同向时允许 recent-momentum 保留（agree-only gate）`
- `trade off = 方向缺失或 recent sign 与 drift sign 冲突`

### 下一轮若继续，固定先看
- `post_cost_return`
- `positive_asset_ratio`
- `trade_count`
- `time-pocket honesty`

## 本轮 hard verdict
- **`Rank 36` 当前 verdict = `fresh source intake admitted / next = 最小 clean replication`**

更直白地说：
- 它现在**还不是** `paper candidate`
- 也**不是** `narrow paper pilot`
- 但它已经满足当前 board 对 fresh intake 的最低要求：
  1. 来源清楚
  2. `trade on / trade off` 能清楚写成 clean-room 规则
  3. 不依赖外部新数据
  4. 可以直接服务下一轮 `Run 2`

## 本轮具体写入
### 新增研究卡 / reader-facing 落点
- `research/quant_digests/2026-03-17_1635_tsm-vs-drift-honesty-gate.md`
- `reports/site/reading/quant_digests/2026-03-17_1635_tsm-vs-drift-honesty-gate.html`
- `reports/site/reading/quant_digests/report.html`

### 同步索引 / 指挥板
- `research/quant_digests/INDEX.md`
- `docs/TODO.md`

## 对 `docs/TODO.md` 的最小写回
本轮把顶部 authoritative override 改成：
- 当前已有新的 fresh intake 可执行，因此**默认下一手不是 `Run 3`**
- 当前更诚实顺序变为：`Run 2 -> Rank 36 最小 clean replication`

同时在 Scout 清单里新增：
- `Rank 36 recent-return sign vs history-drift honesty gate`

## 最小验证
已执行：
- `python3 scripts/build_quant_digest_site.py`
- `bash scripts/publish_homepage_index.sh`

已抽查：
- `reports/site/reading/quant_digests/report.html` 中已出现新 digest 卡
- `docs/TODO.md` 中已出现 `Rank 36 recent-return sign vs history-drift honesty gate`

结果：
- 构建成功退出（code 0）
- 首页已重新发布：`https://jp.jerrypsy.top/momentum/`

## 风险 / 边界
- 这轮只完成了 `source intake`，没有提前假装做完 clean replication
- 原论文是跨资产月频证据；迁移的是**诚实门逻辑**，不是参数
- 这条线下一轮很可能仍会被 `park`；但即使如此，也比在 `EMA waiting_not_due` 时继续磨 `P3 continuity` 或空转更符合当前 board

## Git
- 未提交
- 原因：repo 内仍有大量与本轮无关的脏文件 / 未跟踪文件，避免混提
