# Rank 267 P2 admission：parameter + honesty 通过，进入最终出口决策

- 时间：2026-03-31 12:07 UTC
- 对象：Rank 267 / crypto factor momentum × size/vol rotation
- 任务类型：P2 admission / parameter + honesty
- 结论：`done`

## 本轮只执行这一个小点
按 `BOT2_BOT3_STATE.md` 当前第 1 个 `pending` 小点，只检查：
- `24h / 72h / 7d` 排序
- `4h / 12h / 24h` 持有
- `1d / 3d / 5d` sleeve rotation
- 以及 universe 成分变化、beta-neutral 近似、turnover 成本口径

不重复 `cross-asset` / `time stability` 轴，也不追加新的 factor sleeves 或 optimizer。

使用证据：
- `reports/artifacts/rank267_survivor_followup_20260331/rank267_minimal_replication_summary.json`
- `reports/artifacts/rank267_cross_asset_20260331/rank267_cross_asset_summary.json`
- `reports/artifacts/rank267_time_stability_20260331/rank267_time_stability_summary.json`

## parameter 侧：最佳结果不是孤点，但也不是“任何参数都行”
### 1) rotation 不是单一幸运格子
在当前 `3 rank lookbacks × 3 holds × 3 rotation lookbacks` 的 `27` 个 rotation 组合里：
- `26 / 27` 个组合成本后仍为正
- `13 / 27` 个组合仍高于 `+50 bps/period`
- 唯一转负的是 `7d rank + 4h hold + 1d rotation`，约 `-0.83 bps/period`

这说明当前最优 `7d rank + 24h hold + 1d rotation` 不是孤点；对象的可交易边并没有窄到“只要轻微动一个旋钮就消失”。

### 2) 真正的参数结构，是“慢一点还活着，太快就被摩擦吃掉”
按持有期拆看 rotation 结果：
- `24h hold`：`9 / 9` 为正，且 `8 / 9` 高于 `+50 bps/period`，区间约 `+49.55 ~ +174.82 bps/period`
- `12h hold`：`9 / 9` 为正，`5 / 9` 高于 `+50 bps/period`，区间约 `+9.15 ~ +80.52 bps/period`
- `4h hold`：`8 / 9` 为正，但全部都只剩低双位数或更低，区间约 `-0.83 ~ +18.42 bps/period`

所以它不是“只有一个 24h 配置碰巧赚钱”，而是**慢频 rotation 有一整片正区间；快频版本则明显更脆**。这会改变后续出口判断：若保留该对象，应该诚实地把它理解成较慢节奏的横截面轮动，而不是可随意压到 `4h` 的高换手 alpha。

### 3) 排序 lookback 也呈现连续梯度，不是离散跳点
在 `24h hold` 下：
- `7d rank` rotation 约为 `+145.44 / +147.04 / +174.82 bps/period`（对应 `5d / 3d / 1d` rotation）
- `72h rank` rotation 约为 `+103.98 / +125.53 / +164.21 bps/period`
- `24h rank` rotation 约为 `+49.55 / +66.83 / +117.85 bps/period`

说明 strongest region 明确在 `72h~7d` 排序，而不是随机散布。`24h rank` 仍有正值，但已经明显弱于 `72h/7d`，更像被更高换手拖累。

## honesty / execution realism：没有致命 flaw，但 broad-crypto 叙事被当前样本选择放大
### 1) 当前高流动 universe 会放大“broad crypto 都成立”的错觉
沿用同一最佳骨架做 universe 拆分：
- `full universe` rotation：约 `+80.05 bps/period`
- `majors (BTC/ETH/SOL)`：约 `+11.17 bps/period`
- `ex-majors alts`：约 `+117.44 bps/period`

这说明当前高流动样本并不是在证明“majors 也稳、全市场也稳”，而是在证明：**真实净边主要来自 ex-majors 高流动 alt basket**。因此 broad-crypto / majors-capable 的表述不诚实，但这更像是**scope 约束**，还不是足以把对象直接打回 `background` 的致命实现漏洞。

### 2) turnover 成本已经在参数面上留下清晰痕迹，说明 edge 不是完全靠忽略摩擦幻觉得来
静态 sleeve 的平均 turnover 近似显示：
- `7d rank` 的 `momentum` turnover 约 `10.9%`
- `72h rank` 约 `15.6%`
- `24h rank` 约 `24.3%`

而结果也同步从 `7d / 72h` 强，递减到 `24h` 弱。再结合 `4h hold` 基本被压到手续费边缘，可以更诚实地说：
- 这条线**不是**“忽略成本才存在”的纯幻觉；
- 但它对换手很敏感，能活下来的主要是较慢排序 + `12h~24h` 持有区间。

### 3) beta-neutral 仍只是近似，不足以支撑直接 promote_P3，但还没形成一票否决
当前证据仍主要是 `dollar-neutral / long-short` 近似，而不是已经完成独立的 beta hedge 验证；不过：
- `leave-one-out` 仍全为正，说明不是单一币在救全局；
- `time stability` 也已通过，说明不是只靠最近一段；
- 真正未过关的核心仍是 **majors cross-asset blocker**，而不是新发现的 lookahead / leakage / 明显不可执行结构。

因此 honesty 审计更准确的结论不是“没问题可以直接上 paper”，而是：**没有新增到足以直接退出 P2 的 fatal flaw，但必须把 scope 收窄后的诚实去向交给下一步出口决策。**

## admission 结论
这一步改变系统认知的句子应写成：

> `Rank 267：parameter+honesty passed，进入最终出口决策。`

更展开地说：
- 最优结果不是孤点；`72h~7d` 排序、`12h~24h` 持有、`1d~5d` rotation 形成了一整片正区间；
- 但当前高流动 universe 的 broad-crypto 叙事被样本选择放大，诚实口径只能收窄到 **ex-majors 高流动 alt basket**；
- 目前没有新增到足以一票否决的 execution realism fatal flaw，因此下一步不该再做开放式 admission，而应直接做 `promote_P3 / one-time P2->P1 re-scope / drop_to_background` 的单一出口判断。

## 对 runtime 的直接影响
- 当前 `cycle_plan` 第 1 项应写为 `done`
- 当前小点 `result` 应写为：`Rank 267：parameter+honesty passed，进入最终出口决策`
- `Active P2` 的最新结论应改写为：
  - 参数面不是孤点；
  - 换手更快的 `4h` 版本明显脆；
  - broad-crypto 叙事不诚实，真实有效 scope 更接近 `ex-majors high-liquidity alt basket`；
  - 因此下一步只能做正式出口决策，不能再继续开放式 keep_P2。
