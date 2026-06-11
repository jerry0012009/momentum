# 2026-03-23 07:11 UTC · Rank 147 / DI dominance trigger final verdict · setup-specific margin cut

## 本轮执行顺序（按顶板）
1. 先读 `docs/TODO.md` 顶部 `TRADING DESK BOARD`
2. 未见顶板定义的真实 interrupt：
   - 无 `Paper / 正在自动运行` runner 的 `stale / error / refresh 失步 / ledger 爆雷 / open-position 异常 / red-watch`
   - 无 tiny-live / live-shadow plumbing 的 blocking anomaly
3. 因此本轮合法主动作仍是：`Run 1 = Rank 147 / DI dominance trigger final verdict` 的 **1 次最小、分-setup 诚实切口**

## 本轮主点
**主点：** 不再重复问 “DI 对齐是不是 shared hard gate”，而是把 `Rank 147` 往前推进半步：
> 在每个 setup 内，只保留 `DI margin = |+DI - -DI|` 较高的那一截，是否能形成更诚实的 setup-specific soft score？

**紧邻子点：** 若答案仍然只是 setup 内部分化，而不是 shared deployable gate，就把它从默认 `Run 1` 主资源位放回 `keep_P1 / reserve`。

## 使用证据
- 输入样本：`reports/artifacts/quant_digests/di_dominance_final_verdict_20260323/signal_di_join.csv`
- 新产物：
  - `reports/artifacts/scout_rank147_di_dominance_15m/setup_margin_scorecard.csv`
  - `reports/artifacts/scout_rank147_di_dominance_15m/scorecard.csv`
- 口径保持不变：`BTC/ETH/SOL` × `15m` × `8-bar signed return`
- 本轮只做 setup 内 `DI margin` 分层，不追新 bar、不改 baseline 规则

## 最小结果
### 1) `breakout_short`
- baseline：`n=61`，mean ≈ `-5.45 bps`
- `DI margin top40%`：`n=25`，mean ≈ `+16.76 bps`
- `DI margin top25%`：`n=16`，mean ≈ `+16.51 bps`

读法：
- 这说明 `DI margin` 在 **breakout_short** 里确实像一个**setup-specific strength score**；
- 但它依赖砍样本（retention 只剩约 `41% / 26%`），中位数仍未转正，距离 deployable gate 还远。

### 2) `ema_psar_long`
- baseline：`n=104`，mean ≈ `+1.42 bps`
- `DI margin top40%`：`n=42`，mean ≈ `-15.39 bps`
- `DI margin top25%`：`n=26`，mean ≈ `-42.49 bps`

读法：
- 这条线和 fib / breakout 正相反：`DI margin` 越高越差；
- 因此 `DI dominance` 更不能被写成 shared long-side 放行键。

### 3) `fib_retest_long`
- baseline：`n=33`，mean ≈ `+22.85 bps`
- `DI margin top40%`：`n=13`，mean ≈ `+27.75 bps`
- `DI margin top25%`：`n=9`，mean ≈ `+49.23 bps`

读法：
- fib 子集里确实出现了最像样的正向分层；
- 但样本只剩 `13 / 9` 笔，仍不足以把它升级成 `P2` 或共享部署层。

## 本轮 hard verdict
`Rank 147` 本轮最诚实结论：
- **不是 shared hard gate**
- **也还不是 P2 pre-paper candidate**
- 更像：**`P1 / keep_P1 / setup-specific soft-score reserve / budget used`**

换句话说：
- 若 future 某条线要继续用它，最合理写法是“作为 setup 内部分层特征/soft score 候选”；
- 不该再把它写成三条线共用的统一 admission / veto 键。

## lightweight scorecard
- `usefulness = medium`
- `time_stability = unknown`
- `cross_asset_stability = weak`
- `cost_trade_stability = weak`
- `deployability = low`

### hard-fail flags
- `shared_hard_gate_not_supported`
- `ema_psar_margin_bucket_turns_negative`
- `fib_positive_pocket_small_n`
- `retention_drop_material`
- `not_ready_for_P2`

### recommended_action
- **`keep_P1`**

### why_now
顶板已把 `Rank 147` 明确指定为 queue-empty 时的 fresh intake reserve，本轮就该把那唯一允许的 setup-specific 诚实切口花掉，避免它继续以“也许还能当 shared gate”的模糊说法占默认 `Run 1`。

### main_weakness
它显示的是 **分 setup 的异质性**，不是统一可部署性：
- breakout 里像 soft score
- ema/psar 里反而变差
- fib 里有亮点但样本太小

## 对顶板的最小 writeback 口径
建议只做最小局部修改：
1. 在 `Rank 147` 条目上补成 `P1 / keep_P1 / setup-specific soft-score reserve / budget used`
2. 在 `最近关键 evidence` 增加本轮 setup-specific margin cut 结果
3. 在 `Next 3 bot3 runs` 里把默认主资源从 `Rank 147` 收回，转向 `Rank 140` / `Rank 111` 这类仍更值得的短 decisive compare / evidence anchor

## 交付
- 日志：`research/optimization_loop/2026-03-23_0711_rank147-setup-margin-cut.md`
- 产物：
  - `reports/artifacts/scout_rank147_di_dominance_15m/setup_margin_scorecard.csv`
  - `reports/artifacts/scout_rank147_di_dominance_15m/scorecard.csv`
