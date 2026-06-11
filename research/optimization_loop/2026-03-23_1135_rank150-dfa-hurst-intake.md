# 2026-03-23 11:35 UTC · Rank 150 / DFA Hurst persistence gate fresh intake

- 严格遵循：`docs/TODO.md` 顶部 `TRADING DESK BOARD`、`docs/AUTO_OPTIMIZATION_LOOP.md`、`docs/BOT2_BOT3_OPERATING_CARD.md`
- 本轮路径：`Scout`
- 本轮范围：只做 **1 个主点 + 1 个紧邻子点**

## 0. 顶板判路
- `Paper / 待开启自动运行 = empty`
- 顶板未写入新的 `stale / error / refresh drift / ledger/open-position anomaly / red-watch`
- 因此本轮不走 `Paper launch`，也不走 `Interrupt`，按 `Next 3 bot3 runs` 执行：
  - **Run 1 = 下一条 fresh intake / raw-alpha reserve 守门**

## 1. 为什么本轮选 Rank 150
顶板刚刚已经把：
- `Rank 149 / spot-perp spread MR` 定为 `P0 / park`
- `Rank 148 / intraday CS reversal` 定为 `P0 / park`

所以本轮最有杠杆的小步，不是继续在 spread / session-reversal 近亲上磨细节，而是补一条 **不依赖双腿执行、又能服务现有三条 continuation 主线** 的新鲜候选。

`DFA Hurst persistence gate` 符合这个要求：
- 它不是独立下单 alpha，但能作为 `breakout-short / fib retest / EMA-PSAR` 共用的 shared regime gate；
- 它是 `price-only` 思路，不额外依赖难复现的外部微观结构；
- 它回答的是真问题：很多坏样本未必是 entry 形状错，而是市场本身处在 `low-persistence / chop` 段。

## 2. 本轮主点
### 主点
- **`Rank 150 / DFA Hurst persistence gate`**

reader-facing 定义：
> 先用 rolling `DFA Hurst` 判断当前市场更像“有趋势记忆”还是“来回抽打”；只有在 persistence 足够高时，才让 breakout / EMA-PSAR / fib-retset 这类 continuation 触发更大声地说话。

### 使用证据
- digest：`research/quant_digests/2026-03-23_0620_dfa-hurst-persistence-regime-gate.md`
- 理论锚点：`Noppakaew et al. (2025)`
- 实现锚点：`nolds.dfa()`

## 3. 最小 intake 结论
这条线值得被正式记为新的 Scout，但当前只到：
- **`P1 / keep_P1 / fresh intake admitted / shared regime gate candidate`**

最诚实的原因：
1. **有 desk 相关性**：它直接服务三条现有 continuation 主线，而不是另起一条执行上很重的新家族；
2. **有明确最小实验**：`BTC/ETH/SOL 15m` + rolling `DFA Hurst` + one-family gate compare，成本口径也已明确；
3. **但还没有 desk 本地校准证据**：目前仍是论文 + 开源实现层的可信启发，还不是已经在 crypto 15m 上跑过的 frozen local cut。

所以现在最对的口径不是“升 P2”，而是：
> **允许进入 active Scout，先停在 keep_P1；下一刀只能做 estimator-specific calibration + 单 family 最小 gate check。**

## 4. 紧邻子点
### 紧邻子点：它能不能直接越过 `Rank 140` 成为默认 primary？
结论：**不能。**

理由：
1. `Rank 140` 虽然也停在 `keep_P1`，但已经有 desk-local compare 证据，是当前 active compare anchor；
2. `Rank 150` 这轮只是 source intake，仍缺本地 `BTC/ETH/SOL 15m` 校准与 one-family honest cut；
3. 因此它现在更像 **值得放进 active Scout 排序的 fresh reserve**，而不是直接接管默认 primary。

但它比继续磨 `148/149` 更值得保留，原因也明确：
- 不再是 spread / reversal 近亲；
- 若成立，能便宜地同时改善三条 continuation 主线的 whipsaw；
- 它更像“可共享闸门”，不是又一个孤立 pocket。

## 5. 简短 scorecard
- `usefulness = 3/3`
- `time_stability = 1/3`
- `cross_asset_stability = 1/3`
- `cost_trade_stability = 2/3`
- `deployability = 2/3`
- `recommended_action = keep_P1`
- `why_now = 顶板 Run 1 要求的是新的 fresh intake/raw-alpha reserve；DFA Hurst 是非-spread、非近亲的新共享闸门候选，边际价值高于回头细磨 148/149。`
- `main_weakness = 还没有 desk-local estimator calibration 与单 family 冻结阈值回测，当前只能算 paper+implementation 级证据。`

### hard-fail flags
- `not_independent_alpha`
- `estimator_needs_local_calibration`
- `crypto_15m_not_tested_locally_yet`
- `not_ready_for_P2`

## 6. 本轮交付
- 日志：`research/optimization_loop/2026-03-23_1135_rank150-dfa-hurst-intake.md`
- scorecard：
  - `reports/artifacts/scout_rank150_dfa_hurst_persistence_gate_15m/promotion_scorecard.csv`
  - `reports/artifacts/scout_rank150_dfa_hurst_persistence_gate_15m/promotion_scorecard.json`
- source intake：
  - `reports/artifacts/scout_rank150_dfa_hurst_persistence_gate_15m/source_intake_card.csv`

## 7. 一句话结论
`Rank 150` 现在最像：**值得纳入 active Scout 的 shared regime gate reserve**；它还不是 `P2/P3` 候选，但比继续打磨刚判退的 spread / session-reversal 近亲更有下一刀价值。
