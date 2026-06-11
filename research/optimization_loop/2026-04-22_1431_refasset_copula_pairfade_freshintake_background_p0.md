# 2026-04-22 14:31 UTC — ref-asset copula pair fade fresh intake -> background/P0

- target: `research/quant_digests/2026-04-22_1215_refasset-copula-pairfade-alpha.md`
- action: fresh intake：只补 1 个最小 decisive blocker，回答这条 `BTC 参考资产残差 × copula 条件失衡 × alt-alt pair fade` 是否已经证明相对已 live pairs 主线存在独立新增 after-cost alpha，且不是单一 pair / 单一窗口 / 双腿执行幻觉。
- success_criterion: 只有在最小 pair-family distinctness、双腿执行现实与非单一 pair/window 支撑都成立时才 `keep_P1`；否则直接 `background/P0`。

## 本轮读取与核对
1. `research/quant_digests/2026-04-22_1215_refasset-copula-pairfade-alpha.md`
2. `reports/artifacts/quant_digests/copula_reference_pairs_probe_20260422/summary.csv`
3. `reports/artifacts/quant_digests/copula_reference_pairs_probe_20260422/btc_reference_candidates.csv`
4. 现有同家族前排/历史收口记录：
   - `research/optimization_loop/2026-04-21_1408_rank431_p3_launch_wiring_connected_runner_live.md`
   - `research/optimization_loop/2026-04-19_0935_rank424_p3_launch_wiring_connected_runner_live.md`
   - `research/optimization_loop/2026-03-28_1510_rank224_survivor_followup_keep_p1_background.md`
   - `research/optimization_loop/2026-04-15_2254_rank416_p2_exit_drop_background_execution_realism.md`

## 最小 decisive blocker 结果

### 1) 非单一 pair / window 支撑并未成立
本地 portability probe 只给出一个近期 `28d` 窗口、一个实际测试对 `DOGEUSDT/XRPUSDT`：

- `trades = 12`
- `win_rate = 33.3%`
- `avg_gross_bps = -58.84`
- `total_gross_bps = -706.1`
- `avg_hold_bars = 72`（基本持续撞 `6h` time stop）

这说明当前最接近 desk 可移植口径的证据并没有形成“至少两个独立 pair / 窗口仍为正”的 first-pass 支撑，反而显示信号主要靠单对、单窗口假设存活；而且连 gross 都为负，还没进入更严格 after-cost 讨论。

### 2) 与已 live 的 pairs 主线没有证明新增可迁移 pocket
当前 pairs/front 家族里已经有：

- `Rank 424 / cointegration-first pair admission × strongest residual z-score spread fade`（已 `connected_runner_live`）
- `Rank 431 / cointegration maker-first + hard time-stop pairs`（已 `connected_runner_live`）

这次 digest 想证明的新增层是 `BTC-anchor residualization + copula conditional probability`。但本轮没有给出同口径 A/B：

- 没有展示它相对 plain residual z-score / cointegration baseline 的净增益；
- 没有展示它能保留与 `Rank 424/431` 不同的一组 durable pair pocket；
- 当前唯一 probe 甚至连单窗口 gross 都没保住。

因此它目前更像“pairs signal-layer 复杂化提案”，而不是一个已经证明比现有 live pair stack 多出独立 after-cost alpha 的新 front 对象。

### 3) 双腿执行现实只会更差，不会把当前负 gross 翻成正边
这轮 probe 已在非常轻的实现下为负：

- 还没有加入更完整的双腿 bid/ask、maker/taker 失配、legging loss、orphan-leg 管理；
- 持有期长且常撞 time stop，说明信号回归效率本身已弱；
- 一旦补上真正的双腿执行现实，净值只会进一步恶化。

所以本轮最便宜、最能改变结论的 honesty / execution realism 子检查已经隐含完成：**当前负 gross 本身就说明不存在一个等待成本细化后会变好的 front verdict。**

## 结论
`BTC 参考资产残差 × copula 条件失衡 × alt-alt pair fade` 这条线仍可作为 pairs signal-layer 的背景研究线索保留，但本轮 fresh intake 不能给它 `keep_P1`：它没有证明非单一 pair / 非单一窗口支撑，也没有证明相对已 live 的 `Rank 424/431` 留下独立新增 pocket，而当前唯一 portability probe 还在最轻口径下就是负 gross。

## runtime 写回
- `Fresh intake slot`：当前对象收口为 `background/P0`
- `cycle_plan[2]`：写为 `done`
- 不分配新 `Rank`，因为本轮 verdict 不是 `keep_P1` 或更高

## 一句话结果
`BTC 参考资产残差 × copula 条件失衡 × alt-alt pair fade` 没有证明相对已 live pair stack 留下独立、可迁移的新增 after-cost pocket，且当前唯一 portability probe 单对单窗口已是负 gross，因此本轮 fresh intake 直接收口 `background/P0`。