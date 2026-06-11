# 2026-03-19 09:02 UTC — Rank 84 volume-price interaction admission layer source intake

## 本轮先核对的 desk 状态
- repo 工作区存在大量与本轮无关的脏文件（tracked + untracked）；本轮未做 commit，也未混提无关改动。
- 已实际执行：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 结果：当前**没有**新的 `due-now / overdue lane`
  - 最近 due：`美股 1d+1wk ~11.0h`、`Crypto 1d+1wk ~15.0h`、`创业板ETF 1d ~22.0h`
  - 结论：`Paper Seat = EMA / running paper / waiting_not_due`
- 最近 optimization runs：`08:35 Rank85 intake -> 08:58 Rank85 clean replication(park)`

## 本轮只认领的主点
- **主点：`Scout Seat / Run 2 / Rank 84 / volume-price interaction admission layer` 的 source intake + 两条轻量诚实守门**
- 紧邻子点：将 `SignalPro penetration×ATR admission` 记为邻近后备（仅当 Rank84 后续 hard-fail 才切换）

## 为什么是 Rank 84（先比较 active Scout 边际价值）
本轮 active 候选比较：
1. `Rank 84 / volume-price interaction admission layer`（paper-based、跨三条主线共享 admission、非 breakout 单线）
2. `SignalPro penetration×ATR admission`（08:46 digest，偏 breakout 语义更强）
3. `breakout-candle compression reclaim`（08:08 digest，breakout 主题更重）

在“当前默认不要再强调 breakout”约束下，Rank 84 的边际价值更高，且与当前 Run2 排班一致。

## 本轮冻结的 source-intake 口径
- 候选：`Rank 84 / volume-price interaction admission layer`
- 来源：Sokolovsky et al. (2023), *Interpretable trading pattern designed for machine learning applications*（MLWA 100448）
- 核心迁移：不把 volume gate 写成单阈值，而是把 `price推进 × volume参与 × wick吸收` 冻结成共享 admission score（VPIS）

### 两条轻量诚实守门
1. **trade on / trade off 可清楚写规则**
   - `trade on`：base setup 继续负责方向和价位；VPIS 只做放行/分档（deny / half / full）
   - `trade off`：只有单点放量、无价格推进协同，或明显 wick 吸收导致 VPIS 偏低时，拒绝放行
2. **无明显 lookahead / repaint / data leakage**
   - 首轮迁移只用 `signal 当根及之前` 可得特征（ATR、rvol、bar位置、wick）
   - 统一执行口径：`next-bar open + no-overlap`
   - 禁止把未来 2~4 bar 的结果倒灌成当前 VPIS 标签

## 本轮 hard verdict
- **`Rank 84 / volume-price interaction admission layer = guard-passed / admit_to_clean_replication_queue`**

## 产物
- artifact：
  - `reports/artifacts/literature/scout_rank84_volume_price_interaction_source_intake_card.csv`
- reader-facing：
  - `reports/site/reading/repo_scout/rank84_volume_price_interaction_source_intake.html`
- 顶板更新：
  - `docs/TODO.md` 的 `Next 3 bot3 runs` 已补充 `09:02 UTC` 记录与新顺序

## 对顶板的更新结论
- `Run 1 = EMA due-check only（若脚本仍 waiting_not_due，不得空转）`
- `Run 2 = 若 Rank 84 guard-passed 且 EMA 仍 waiting_not_due，则只给它 1 次最小 clean replication`
- `Run 3 = 若 Rank 84 clean replication 直接 hard-fail / park，则切 SignalPro penetration×ATR admission source intake；若未硬 fail 但 verdict 仍不足，则只允许 1 个 truly verdict-changing 最小检查`

## 最小验证
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`（已执行，确认 waiting_not_due）
- 读回 Rank84 artifact 与 reader 页面路径（已落盘）
- 读回 `docs/TODO.md`，确认 `Next 3` 已写回

## 备注
- 本轮没有追新 bar、没有伪造 refresh。
- 本轮没有重跑 heavy replication，仅执行 source intake + honesty gate。
- 工作区脏文件量大，本轮未做无关清理/提交。
