# 2026-03-20 09:47 UTC · Rank 116 / EMA respect memory score source intake

## 本轮结论
- `Run 1 / EMA due-check first` 已实际执行：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 结果：全 desk 继续 `waiting_not_due`
  - 美股 `1d+1wk -> 2026-03-20 20:00 UTC`
  - Crypto `1d+1wk -> 2026-03-21 00:00 UTC`
  - 创业板ETF `1d -> 2026-03-23 07:00 UTC`
- `manual_narrow_paper_last_run_summary.json @ 2026-03-20T09:03:58Z` = `new_closed_trades_appended=0`
- 因而本轮合法主动作继续回到 `fresh intake`
- 重新比较 active Scout / fresh source 边际价值后，本轮正式冻结：
  - **`Rank 116 / EMA respect memory score`**
- 当前 hard verdict：
  - **`guard-passed / admit_to_clean_replication_queue`**

## 为什么这轮选 Rank 116
相对当前允许动作：
1. `Rank 112 / basis dislocation short veto`：已是 `P1 weak candidate / evidence_pool / budget used`
2. `Rank 111 / abnormal-return event clock`：已是 `P1 evidence_pool / budget used`
3. `Rank 115 / same-clock intraday RVOL volume gate`：上一轮已压回 `P0 / park / evidence pool`
4. fresh source 里，`2026-03-20 09:40` 的 EMA respect digest 同时满足：
   - repo-based
   - 直接服务 `15m crypto`
   - 已有 Binance 公共数据快检
   - 修的是当前 EMA / Fib / breakout 共用的轻量 admission 读数，而不是再造一个新 alpha

所以它是本轮最便宜、最可能改变下一轮 desk judgment 的 fresh intake。

## 本轮完成内容
### 1. Source intake + 两条轻量诚实守门
冻结口径：
- 它**不是独立 alpha**，也不是新 corridor 参数模板
- 它只回答现有 setup 在触发前，是否存在“最近确实反复尊重 EMA9 / EMA 近端结构”的趋势健康度记忆
- 更诚实的主读法是：
  - 保留 `recent EMA respect score` 作为轻量 `admission / sizing context`
  - 不默认把 `ATR corridor + depth` 升级成硬门
- 可挂到：
  - `breakout-short follow-up`
  - `Fib retest_hold`
  - `EMA/PSAR continuation`
- 但都只能先做 shared admission / sizing context，不能单独开仓

### 2. Honesty gate
已写死：
- `ema_respect_score` 只能用 signal 当根及之前、已完成 bar 的 `EMA / low / close / open` 关系构造
- 禁止看 future reclaim、future path 或未来回补后的“更漂亮”结构
- 下一轮 clean replication 强制统一到：
  - `next-bar open`
  - `no-overlap`
- `score window`、`touch band`、以及是否要求 `close>EMA` / `close>open` 只能在训练段冻结，再到测试段验证
- `dist<=0.75 ATR`、`depth>=-0.8 ATR` 这类 hard corridor 当前只允许保留为**对照组**，不得默认并入主 admission 规则

## 新增产物
- `reports/artifacts/literature/scout_rank116_ema_respect_memory_source_intake_card.csv`
- `reports/site/reading/repo_scout/rank116_ema_respect_memory_source_intake.html`
- `docs/TODO.md` 顶部 `TRADING DESK BOARD` 已追加本轮 authoritative write-back

## 当前 desk 写回
- `Paper Seat = EMA / 创业板ETF 1d primary anchor / waiting_not_due`
- `Live Seat = 暂空`
- `Scout Seat` 顺序更新为：
  - `Rank 116 / EMA respect memory score`（`P1 / guard-passed / clean replication next`）
  - `Rank 112 / basis dislocation short veto`（`P1 weak candidate / evidence_pool / budget used`）
  - `Rank 111 / abnormal-return event clock`（`P1 evidence_pool / budget used`）
  - `Rank 115 / same-clock intraday RVOL volume gate`（`P0 / park / evidence pool`）
  - `Rank 114 / pullback -> two-sided breakout window verdict`（`P0 / park / evidence pool`）
  - `Rank 113 / alpha-beta abstain / profit-window`（`P0 / park / evidence pool`）

## Next 3
- `Run 1 = EMA due-check first`
- `Run 2 = 若 EMA 仍 waiting_not_due，则只给 Rank 116 1 次最小 clean replication`
- `Run 3 = 若 Rank 116 clean replication 显示 honest uplift 且无 decisive fail，则立刻补 1 个真正会改变级别的最小检查（默认优先 成本 / 交易数稳定性），并直接给出 P2 / park 判断；若 Rank 116 hard-fail / exhausted，则回 fresh intake（优先 RECENT_PAPER_SEEDS / quant_digests / validated shortlist）；只有 fresh intake 也 exhausted 后，才允许 tiny-live plumbing fallback`

## 最小验证
- 已实际运行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 返回 `require-due` 等待态（退出码 `2`），符合当前 desk 状态
- 已生成 reader-facing 页面与 CSV artifact
- 未处理 git 工作区里与本轮无关的大量脏文件；本轮只做 selective write-back

## 风险 / 边界
- 当前证据来自 repo 特征定义 + Binance 公共数据快检，不是完整 clean replication
- 当前更像“轻量 admission context 候选”，不是已验证 alpha，也不是 paper candidate
- 下一轮若做最小 clean replication，默认应只挂 **1 条 base archetype**；若结果主要来自砍样本，而不是更诚实的 false-follow / false-hold 改善，就应直接 `park`

## Commit hash
- 未提交。

## 未提交原因
- git 工作区存在大量与本轮无关的已修改 / 未跟踪文件；为避免混提，本轮只保留本轮 source intake 页面、CSV、顶板 write-back 与日志。
