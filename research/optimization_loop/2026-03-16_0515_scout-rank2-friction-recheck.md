# 2026-03-16 05:15 UTC｜Scout Seat：Rank 2 combo_all 轻量 friction recheck（Run 3 fallback）

## 为什么这次选这个
先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 与 `Next 3 bot3 runs` 检查席位：

- **Run 1 / Paper Seat**：`reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 显示各 active lane 仍是 `waiting_not_due`，A 股下次 close 约 `07:00 UTC`，当前不能伪造 refresh。
- **Run 2 / Live Seat**：`reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_revisit_guard_20bps.csv` 显示最近 heavy recheck 在 `2026-03-15 23:25 UTC`，当前仍在 `6h cooldown` 窗口内，不应重复 heavy rerun。
- **Run 3 / Scout fallback**：按板上约束，本轮应优先检查 Rank 1 是否有足够新 bar；实际 cache 末端仍是 `03:45 UTC`，不足以做“有新 bar 的 honest recheck”。

因此本轮只认领 **1 个主点**：对 Rank 2 `combo_all` 做一刀轻量 `friction recheck`；并认领 **1 个紧邻子点**：把 recheck 同步到 reader-facing 页面与 TODO 镜像。

## 做了什么改动
### 主点（Run 3）
1. 扩展脚本：`scripts/build_volume_supportflip_higherlow_first_verdict.py`
   - 新增 `friction ladder` 计算（对 `raw_breakout / higher_low_only / combo_all` 在 `6/10/15/20 bps per side` 口径下做成本敏感性快检）；
   - 新增 artifact：
     - `reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_friction_ladder.csv`
   - 在 Rank 2 factor 页新增“轻量 friction recheck”区块，给出 hard verdict 与 cost ladder 表。
2. 更新试验元数据：`trial_meta.csv` 增加 `friction_recheck_verdict` 字段，供上游 scout 页面读取。

### 紧邻子点（reader-facing continuity）
1. 更新 `scripts/build_trendline_alpha_scout_report.py`：
   - Rank 2 卡片新增 `friction recheck` 摘要与 artifact 落点。
2. 更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`：
   - 新增 `2026-03-16 05:13 UTC` 的 Scout Seat 补充；
   - 刷新当前窗口排班，明确在出现真实新 bar 前不要重复同样本 scout 续切。
3. 站点镜像同步：`reports/site/plans/momentum_todo.html`。

## 验证 / 证据
执行（最小必要验证）：
1. `python3 -m py_compile scripts/build_volume_supportflip_higherlow_first_verdict.py scripts/build_trendline_alpha_scout_report.py scripts/build_plans_site.py`
2. `python3 scripts/build_volume_supportflip_higherlow_first_verdict.py`
3. `python3 scripts/build_trendline_alpha_scout_report.py`
4. `python3 scripts/build_plans_site.py`
5. `grep` 检查页面落点：
   - `reports/site/factors/scout_volume_supportflip_higherlow_15m/report.html`
   - `reports/site/reading/trendline_alpha_scout/report.html`
   - `reports/site/plans/momentum_todo.html`

关键结果（`combo_all_friction_ladder.csv`）：
- `combo_all`：`mean_total_return` 在 `6/10/15/20 bps` 分别约 `+2.33% / +1.78% / +1.10% / +0.42%`，`positive_asset_ratio` 持续 `2/3`；
- `higher_low_only`：到 `10 bps` 已转负（约 `-0.22%`）；
- `raw_breakout`：全梯度深负（`20 bps` 约 `-81.07%`）。

## 本轮 hard verdict
`Rank 2 combo_all` 在更高摩擦下仍保持正的跨资产平均收益，当前应继续保留为更窄的 **confirmation challenger**，并进入轻量 forward 复核；但样本仍是 `120d / 15m / 3` 币种，不足以宣布 `replace-ready` 或 `tiny-live ready`。

## 风险 / 边界
- 本轮是 **friction 快检**，不是新 bar forward 验证；
- 不引入路由偏差、成交偏差、资金上限与 kill-switch 真实执行约束；
- 交易笔数仍偏少（combo_all 跨资产均值约 6.7 笔），需防样本偶然性。

## 下一步建议
1. breakout cooldown 结束后，若仍满足 guard，按规则给 `support_breakout_v0` 一次且仅一次 honest heavy rerun；
2. 若 Run 1/Run 2 再次 blocked，fallback 优先做 `small_live parity_red action / sample-row`，不要继续重复同样本 scout 微切；
3. 等 Rank 1 出现真实新 bar 后，再回到 `τ-band` continuation。

## Commit hash（基线）
- `45dc474`

## 如果未提交，原因
当前工作区存在大量与本轮无关的既有脏文件与未跟踪文件；为避免混提，本轮仅做 selective 产物与页面刷新，不做打包提交。
