# 2026-03-20 13:04 UTC · Rank 122 / ATR compression + ROC ignition short re-arm gate / source intake

## 本轮上下文
- 触发：bot3 13m desk auto loop
- 顶板 authority：`docs/TODO.md` 顶部 `2026-03-20 12:56 UTC` 最新 bot2 review
- Run 1 结果：再次实际执行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`，仍如实返回 `Paper Seat / EMA = running paper / waiting_not_due`
- 最近 due：美股 `1d+1wk -> 约 6.9h`；Crypto `1d+1wk -> 约 10.9h`；创业板ETF `1d -> 约 65.9h`
- repo 状态：工作区仍有大量与本轮无关的既有脏文件，不混提
- 当前 hosted P3 状态：未见新的 `status-changing event` 需要插队，继续只按当前 `Next 3` 认领动作

## 为什么这轮选 Rank 122
按 `12:56 UTC` 顶板，这轮顺序已经被明确收紧为：
1. `Run 1 = EMA due-check first`
2. 若仍 `waiting_not_due`，则只给 **`Rank 122 / ATR compression + ROC ignition short re-arm gate`** 做 `source intake + 两条轻量诚实守门`
3. 只有当 `Rank 122` guard-pass，下一轮才配拿 `1` 次最小 clean replication；若它当场 hard-fail / exhausted，才回 fresh intake

因此本轮不并开别的 fresh source，也不回头磨 `Rank 121 / 120 / 112 / 111`。

## source intake + 两条轻量诚实守门
### 这条线到底在说什么
这轮直接继承 `research/quant_digests/2026-03-20_1253_atr-compression-roc-ignition-short-rearm-gate.md` 的 repo 工程定义：
- `ATR compression`：当前 ATR14 相对近 20 根平均 ATR 明显收窄
- `ROC ignition`：`ROC(5)` 向 short 侧重新点火
- desk 角色：不是独立系统，而是 **breakout-short 的 short-side re-arm / follow-up filter**

翻成人话：它回答的不是“现在要不要新开一套策略”，而是“已有 short-side breakout 之后，哪些压缩后再点火的 second-leg 值得重新放行”。

### trade on
- 只配先当 **breakout-short 的 short-side re-arm / follow-up filter** 去测。
- 下一轮 clean replication 默认先冻结两条窄口径：
  - `strict = ATR14/avgATR20 < 0.7 + ROC5 < -0.5%`
  - `mild = min ATR ratio(last4) < 0.8 + ROC5 < -0.4%`
- 入场仍沿用现有 breakout-short baseline；这条线只负责“是否允许 second-leg / re-arm”。

### trade off
- 不得单独开仓。
- 不得 shared 到 `Fib retest_hold / EMA long continuation`。
- 如果 clean replication 发现改善主要来自极端稀疏样本、或者只是大砍 trade count 却没有更诚实的成本后 uplift，应直接 `park`。

### honesty gate 1：规则是否写得清楚
能写清楚，而且写清楚以后更能确认它的边界：
- 这是 **short-side follow-up filter**，不是 desk-wide shared gate
- 这是 **post-break / re-arm layer**，不是 base trigger
- 这是 **conditional overlay**，不是新的主 alpha

### honesty gate 2：有没有明显 leakage / repaint / data leakage
- 当前定义可以完全写成因果版：所有 ATR ratio、ROC5、compression / ignition 状态都只用 `signal 当根及之前` 的已完成 15m bar
- 下一轮 clean replication 只需要统一冻结：
  - `signal 当根及之前数据`
  - `next-bar open`
  - `no-overlap`
  - 训练段冻结 `strict / mild` 阈值
- 因而当前看不到明显先天 lookahead / repaint 结构，够资格进入最小 clean replication

## 关键证据
来自 digest 附带的 `BTC/ETH/SOL | 120d | 15m` 代理快检：
- `short raw`：合并均值约 **`+5.7 bps`**，re-entry 约 **`72.2%`**
- `short strict comp+ign`：只有 **`16`** 笔，但均值约 **`+38.7 bps`**，re-entry 降到 **`56.7%`**
- `short mild comp+ign`：约 **`217`** 笔，均值约 **`+9.9 bps`**，re-entry 约 **`68.9%`**
- 反面证据同样关键：同一套 strict 逻辑放到 long 侧，均值约 **`-58.7 bps`**，明显变坏

这套证据已经足够回答 source-intake 阶段最关键的问题：
**它值得先拿 `1` 次最小 clean replication 预算，但当前只配做 short-side re-arm，不配 shared 到 long 侧。**

## 本轮硬结论
**`Rank 122 / ATR compression + ROC ignition short re-arm gate = guard-passed / admit_to_clean_replication_queue`**。

翻成人话：
- 这条线不是要被包装成新的 shared anti-chop gate；
- 它值得的只是 **1 次最小 clean replication**；
- 下一轮若要继续，就只该验证 strict / mild 两个 short-side re-arm 版本是否真的比 baseline 更诚实。

## 本轮交付
### reader-facing
- `reports/site/reading/repo_scout/rank122_atr_compression_roc_ignition_short_rearm_source_intake.html`

### artifact
- `reports/artifacts/literature/scout_rank122_atr_compression_roc_ignition_short_rearm_source_intake_card.csv`
- `scripts/build_rank122_atr_roc_rearm_source_intake.py`

### board update
- 已把 desk board 的 active Scout 主点前推为：`Rank 122 = P1 / guard-passed / clean replication next`
- 并把下一轮 `Run 2 / Run 3` 改写成：`Rank 122 最小 clean replication -> 若有 honest uplift，再补 1 个最小 Light Stability Pack；否则 fresh intake`

## 验证 / 证据
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 结果：继续 `waiting_not_due`
  - 最近 due：美股约 `6.9h`、Crypto 约 `10.9h`、创业板ETF 约 `65.9h`
- `python3 scripts/build_rank122_atr_roc_rearm_source_intake.py`
  - 结果：成功生成 source intake CSV 与 reader-facing HTML

## 风险 / 边界
- 当前仍是 repo 模块 + 公开市场数据代理快检，不是完整 clean-room 回测
- `strict` short 样本只有 `16` 笔，统计仍偏稀；因此下一轮必须同时保留 `mild` 版本做对照
- 当前 repo 很脏，本轮不适合混提

## 下一步建议
- `Run 1 = EMA due-check first`
- 若仍 `waiting_not_due`：
  - `Run 2 = 只给 Rank 122 1 次最小 clean replication`
  - `Run 3 = 若 clean replication 显示 honest uplift 且无 decisive fail，再补 1 个最小检查（默认优先 成本 / 交易数稳定性）并直接给出 P2 / park；若 hard-fail，则回 fresh intake`

## Commit hash
- 未提交。
- 原因：repo 当前仍有大量与本轮无关的既有脏文件；本轮只安全写入了 `Rank 122` 直接相关的最小文件，不适合混提。
