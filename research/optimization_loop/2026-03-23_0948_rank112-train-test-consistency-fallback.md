# 2026-03-23 09:48 UTC · Rank 112 / basis dislocation short veto / train-test consistency fallback

## 本轮一句话
按 `docs/TODO.md` 顶板，本轮走 **Scout / Run 1 / Rank 112**，目标是补一刀最短、最能封口的 **cheap decisive fallback**：`basis_extreme_veto` 到底有没有跨 split 的稳定 uplift，足以继续保留 `P2` 想象。结论：**没有**。本轮 authoritative call 固定为 **`P1 / keep_P1 / evidence pool / 不升 P2`**。

## 本轮路径判断
- `Paper launch queue`：`empty`
- `Interrupt`：未见任何正在自动运行的 paper runner 出现 `stale / error / refresh 失步 / ledger 异常 / red-watch`
- 因此本轮路径 = **`Scout`**

## 顶板认领动作
- 主点：`Rank 112 / basis dislocation short veto`
- 紧邻子点：把结论写回 `TRADING DESK BOARD`，让默认主资源从 `Rank 112` 继续轮转到 `Rank 111`

## 为什么选这刀
`Rank 112` 之前已经做过：
1. source intake；
2. 最小 clean replication；
3. `Rank 140` family compare 里的显式三臂补看。

但顶板还留着一个没封口的问题：
> 它到底只是 `P1 evidence pool`，还是还值得继续保留一点 `P2` 想象？

最短、最诚实的收口方式不是再补一个新代理，而是直接问：
**如果把 `basis_extreme_veto` 放到最简单的 train/test 口径里，它有没有稳定 shared uplift。**

如果没有，就不该继续占默认主资源位。

## 主点：Rank 112 train-test consistency fallback
### 数据来源
复用既有 artifact：
- `reports/artifacts/scout_rank112_basis_dislocation_short_veto_15m/trade_log.csv`
- 既有 variant：
  - `baseline`
  - `basis_extreme_veto`
  - `basis_extreme_plus_oi_veto`
- 成本继续看：`6 / 10 bps per side`

### 本轮判定规则
按 `baseline` 的 `signal_ts` 做时间顺序 `50/50 train/test` 切分；对每个 `variant × cost` 组合，只有同时满足以下条件，才算还能支持继续保留 `P2` 想象：
1. `train return_delta > 0`
2. `test return_delta > 0`
3. `train false_break_8bars 不恶化`
4. `test false_break_8bars 不恶化`

### 新增产物
- `reports/artifacts/scout_rank112_basis_dislocation_short_veto_15m/train_test_consistency_cut.csv`
- `reports/artifacts/scout_rank112_basis_dislocation_short_veto_15m/train_test_consistency_cut.json`
- `reports/site/factors/scout_rank112_basis_dislocation_short_veto_15m/train_test_consistency_cut.html`

## 结果
### 总结
- `shared_candidate_count = 0 / 4`
- `shared_candidate = false`

### 逐项读法
#### 1) `basis_extreme_veto`
- **收益侧**：
  - `6bps`：train `+0.1415%`，test `+0.6774%`
  - `10bps`：train `+0.2215%`，test `+1.3171%`
- **坏消息**：test 侧 `false_break_8bars` 都恶化
  - 从 `73.33% -> 77.27%`
- 说明它更像：
  - **砍掉了几笔更亏的单子**，所以总收益看起来略好；
  - 但保留下来的 short，并没有在后续 follow-through/false-break 结构上变得更干净。
- 这不够支撑它继续包装成更高层级的 shared veto 候选。

#### 2) `basis_extreme_plus_oi_veto`
- train 基本没有新增信息；
- test 侧收益与 `false_break_8bars` 都一起变差；
- 说明 `oi_delta_1h <= 0` 这层不是增强器，更像额外噪声层。

## 硬结论
## authoritative verdict
**`Rank 112 / basis dislocation short veto = P1 / keep_P1 / evidence pool / 不升 P2`**

翻成人话：
- 它不是完全没信息；
- 但这点信息没有通过最便宜的 train/test consistency 守门；
- 所以最多保留成 **evidence-bearing reserve**；
- 不应再以“也许还能回 `P2`”的名义继续占默认主资源位。

## 紧邻子点：board writeback
已同步更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`：
- `Active Scout` 中把 `Rank 112` 改成：
  - `P1 / keep_P1 / evidence pool / train-test consistency fallback done / 不升 P2`
- `Next 3 bot3 runs` 改成：
  - `Rank 125` 与 `Rank 112` 都已完成 cheap decisive / consistency fallback；
  - 默认主资源继续轮转给 `Rank 111`
- 最近关键 evidence 顶部新增本轮结论，避免后续循环又把 `Rank 112` 当成待验证主位

## 简短 scorecard（Scout 要求）
- 主点（Rank 112 decisive fallback）：**done**
- 紧邻子点（desk writeback / handoff）：**done**
- 是否升层：**no**
- 层级结论：**`keep_P1 / evidence pool`**
- 下一默认轮转：**`Rank 111`**

## 验证
本轮实际执行：
```bash
python3 - <<'PY'
# 读取 trade_log.csv，按 baseline signal_ts 做 50/50 train/test split，
# 输出 train_test_consistency_cut.{csv,json,html}
PY
```

关键读数：
- `basis_extreme_veto @ 6bps`
  - train `return_delta=+0.001415`
  - test `return_delta=+0.006774`
  - test `false_break_8bars_delta=+0.039394`
- `basis_extreme_veto @ 10bps`
  - train `return_delta=+0.002215`
  - test `return_delta=+0.013171`
  - test `false_break_8bars_delta=+0.039394`
- `basis_extreme_plus_oi_veto`：`0/2` 成本都未通过

## 风险 / 边界
- 这不是在证明 `Rank 112` 完全无效，而是在证明：
  **它当前不值得继续以 `P2` 候选的身份占主资源。**
- 若未来要 reopen，必须带来更窄、更可解释的上下文（例如明确只服务某个 setup / asset pocket），而不是再重复 shared 15m 叙事。

## 交付落点
- 日志：本文件
- 产物：
  - `reports/artifacts/scout_rank112_basis_dislocation_short_veto_15m/train_test_consistency_cut.csv`
  - `reports/artifacts/scout_rank112_basis_dislocation_short_veto_15m/train_test_consistency_cut.json`
- 网页：`reports/site/factors/scout_rank112_basis_dislocation_short_veto_15m/train_test_consistency_cut.html`
- 顶板：`docs/TODO.md`

## Commit hash
- 未提交。
- 原因：仓库当前存在大量与本轮无关的脏文件；本轮只做了 `Rank 112` 相关 artifact、日志与 `TODO` 顶板 writeback。
