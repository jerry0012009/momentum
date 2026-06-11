# 2026-03-23 12:53 UTC · Rank 151 本地 frozen A/B/C cut

- 严格遵循：`docs/TODO.md` 顶部 `TRADING DESK BOARD`、`docs/AUTO_OPTIMIZATION_LOOP.md`、`docs/BOT2_BOT3_OPERATING_CARD.md`
- 本轮路径：`Scout`
- 本轮范围：只做 **1 个主点 + 1 个紧邻子点**

## 0. 顶板判路
- `Paper / 待开启自动运行 = empty`
- 顶板未写入新的 `stale / error / refresh drift / ledger/open-position anomaly / red-watch`
- 因此本轮不走 `Paper launch`，也不走 `Interrupt`，继续按 `Next 3 bot3 runs` 的 **Run 1 = Rank 150 / 151 的最小本地 frozen cut（二选一）** 执行。

## 1. 为什么这轮选 Rank 151，而不是 Rank 150
本轮目标不是再做 source intake，而是把顶板要求的 **最小本地 frozen cut** 真落下来。

两条候选里：
- `Rank 150` 还缺 estimator-specific calibration 脚手架；
- `Rank 151` 已经有本地 `BTC/ETH/SOL 15m` breakout 对齐快检产物，可以直接固化成一个 **A/B/C frozen compare**。

所以本轮最有杠杆、最可验证的小步，是先把 `Rank 151` 的 family-level frozen proxy cut 补齐。

## 2. 本轮主点
### 主点
- **`Rank 151 / EWMAC breakout band-pass gate`**

### 本轮做的最小 frozen cut
把已有本地快检固定成三臂对照：
- `A = baseline（不过滤）`
- `B = hard-positive（align_score > 0）`
- `C = band-pass（q20 < align_score <= q80）`

使用的冻结阈值来自本地快检产物：
- `q20 = -1.1560`
- `q80 = 1.6414`

## 3. 结果（可验证）
来自：`reports/artifacts/scout_rank151_ewmac_breakout_bandpass_gate_15m/family_frozen_abc_cut.csv`

### pooled A/B/C
- `A baseline`：`n=3445`，`mean_bps=+1.84`，`win_rate=45.25%`
- `B hard-positive`：`n=1970`，`mean_bps=+1.45`，`win_rate=44.97%`，`retention=57.2%`
- `C band-pass`：`n=2067`，`mean_bps=+9.53`，`win_rate=47.02%`，`retention=60.0%`

### 邻接诊断（不是主点，只做紧邻子点）
- `extreme tail`（`<=q20` 或 `>q80`）:
  - `n=1378`
  - `mean_bps=-9.68`
  - `win_rate=42.60%`

这说明对当前 frozen proxy 来说：
1. **“越强越追”并不成立**；
2. `hard-positive` 不是更优版本，反而比 baseline 更弱；
3. **中段 band-pass** 才是这条线当前最诚实的保留方式；
4. 这不是靠把样本砍到很薄换来的——仍保留了约 `60%` 事件量。

## 4. 紧邻子点
### 紧邻子点：它现在能不能直接升 `P2`？
结论：**还不能。**

原因很简单：
- 这轮 frozen cut 仍然是 **generic breakout proxy**，不是某一条 desk family（如 breakout-short / fib retest / EMA-PSAR）的正式 post-cost 守门；
- 它已经足够支持 `keep_P1 + fresh reserve 前排`，但还不足以支持 `promote_P2`；
- 所以下一步应该是：**只挑 1 条 desk family，复用这套 frozen 阈值做 family-specific A/B/C honest cut**，而不是继续改阈值或扩样本讲故事。

## 5. 简短 scorecard
- `usefulness = 3/3`
- `time_stability = 2/3`
- `cross_asset_stability = 2/3`
- `cost_trade_stability = 2/3`
- `deployability = 2/3`
- `recommended_action = keep_P1`
- `why_now = 顶板 Run 1 明确要求 Rank 150/151 做最小本地 frozen cut；Rank 151 已有本地快检产物，最适合本轮把 source-intake 前进一步，变成可审计的 A/B/C frozen compare。`
- `main_weakness = 仍是 generic breakout proxy，不是单一 desk family 的 post-cost frozen 守门，所以还不够升 P2。`

## 6. 本轮新增产物
- 日志：`research/optimization_loop/2026-03-23_1253_rank151-local-frozen-abc-cut.md`
- frozen compare：
  - `reports/artifacts/scout_rank151_ewmac_breakout_bandpass_gate_15m/family_frozen_abc_cut.csv`
  - `reports/artifacts/scout_rank151_ewmac_breakout_bandpass_gate_15m/family_frozen_abc_cut_meta.json`

## 7. 一句话结论
`Rank 151` 已经从“只有 source-intake 叙述”前进到“有本地 frozen A/B/C compare 的 fresh reserve”：**band-pass 明显优于 baseline/hard-positive，且 retention 仍有 60%，所以值得继续留在 active Scout 前排；但在做完 1 条 desk-family-specific honest cut 之前，仍只配 `keep_P1`，不升 `P2`。`
