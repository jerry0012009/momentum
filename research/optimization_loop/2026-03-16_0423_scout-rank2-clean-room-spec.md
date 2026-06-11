# 2026-03-16 04:23 UTC｜Scout Rank 2：把 volume + support-flip + higher-low 压成 clean-room spec

## 为什么这次选这个
先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 检查当前席位与 run 顺序：

- **Repo / worktree**：当前仓库存在大量与本轮无关的既有脏文件与未跟踪文件；本轮只做 selective 改动，避免混提。
- **最近 runs**：
  - `03:55`：`τ-band 15m crypto first verdict`
  - `04:10`：`small_live_routing_dry_run_checklist_v1`
- **Run 1 / Paper Seat**：`EMA` 仍处于 `waiting_not_due`，当前没有真实 `market-close refresh` 可写，不能伪造 paper continuation。
- **Run 2 / Live Seat 首选（Rank 1 τ-band recheck）**：本轮先检查 `scout_tau_band_breakout_15m/cache_meta.csv`。上轮实验缓存尾部是 `2026-03-16 03:45 UTC`，而当前时间点相对它**只新增了 2 根 15m bar**，不够做 honest forward continuation。
- 因此本轮按当前 board 的 Run 2 fallback 自动切到 **Rank 2：`volume + support-flip + higher-low` 最小 clean-room spec**，而不是继续对 Rank 1 做同一样本近义重读。

## 本轮主点 + 紧邻子点
### 主点
把 `Yumna et al. (2024)` 这条 confirmation/filter 候选，压成一份可直接实现的本地最小实验 spec：

- 新脚本：`scripts/build_volume_supportflip_higherlow_scout_spec.py`
- 新 artifact：`reports/artifacts/scout_volume_supportflip_higherlow_15m/clean_room_spec_v1.csv`
- 新页面：`reports/site/factors/scout_volume_supportflip_higherlow_15m/report.html`

本轮冻结的关键口径：
- 市场 / 周期：`BTC-USD / ETH-USD / SOL-USD | Binance 120d | 15m`
- 方向层：`EMA20 > EMA50` 只做多；反之只做空
- breakout 边界：`Donchian(20) + 0.05 ATR`
- 确认链：
  1. `volume_confirmation`
  2. `support_flip_confirmation`
  3. `higher_low_confirmation`
- 首轮对照矩阵：
  - `raw_breakout`
  - `volume_only`
  - `support_flip_only`
  - `higher_low_only`
  - `combo_all`
- 执行层：`next-bar open entry | 1 ATR stop | 2 ATR target | 8-bar time stop | 6 bps/side`
- 评分板：`post_cost_return / false_break_ratio / retest_hold_rate / time_to_failure / max_drawdown / positive_asset_ratio`
- bench 规则也先写死：如果 `combo_all` 既没改善收益，也没改善假突破率，或大幅减交易但没有增量，就直接 `bench`，避免后续无限解释。

### 紧邻子点（reader-facing 落点）
把这份 Rank 2 spec 同步挂回 Scout 页面，避免产物只躺在单独 factor 页里：

- 修改：`scripts/build_trendline_alpha_scout_report.py`
- 更新：`reports/site/reading/trendline_alpha_scout/report.html`
- 新增一张 `Run 2 fallback（Rank 2 · volume + support-flip + higher-low spec）` 卡片，直接写清：
  - 为什么 Rank 1 本轮不该硬做 recheck；
  - Rank 2 现在已经 `implementation-ready`；
  - 下一步该实现什么，而不是继续补 wording。

## 验证 / 证据
执行：
1. `python3 -m py_compile scripts/build_volume_supportflip_higherlow_scout_spec.py scripts/build_trendline_alpha_scout_report.py`
2. `python3 scripts/build_volume_supportflip_higherlow_scout_spec.py`
3. `python3 scripts/build_trendline_alpha_scout_report.py`
4. 检查 `reports/artifacts/scout_tau_band_breakout_15m/cache_meta.csv`
   - `last_bar_utc = 2026-03-16 03:45 UTC`
   - 相对本轮时间点仅新增 `2` 根 `15m` bar
5. `sed -n '1,12p' reports/artifacts/scout_volume_supportflip_higherlow_15m/clean_room_spec_v1.csv`
6. `grep -n "Run 2 fallback（Rank 2\|clean_room_spec_v1.csv\|implementation-ready" reports/site/reading/trendline_alpha_scout/report.html reports/site/factors/scout_volume_supportflip_higherlow_15m/report.html`

已确认：
- Rank 2 的 clean-room spec artifact 生成成功；
- factor 页面已可直接阅读；
- Scout 总览页已出现新的 fallback 卡片；
- 本轮没有伪造 Rank 1 的“forward continuation”。

## 本轮 hard verdict
- **Rank 1 τ-band**：当前只新增 `2` 根 `15m` bar，**不足以**做 honest recheck；这轮若继续硬跑，价值很低。
- **Rank 2 volume + support-flip + higher-low**：现在已经被压成 **implementation-ready spec**；
- 但它目前仍只是 **spec verdict，不是 performance verdict**。

一句话总结：
**本轮最有效的推进，不是再对 Rank 1 近义重读，而是把 Rank 2 冻结成下轮可直接开跑的 15m clean-room 实验框架。**

## 风险 / 边界
- 这轮没有跑新的 performance slice，因此不能把 Rank 2 提前吹成 replace-ready candidate。
- `support-flip` 与 `higher-low` 的定义虽然已写成因果可实现版本，但仍是 `v1` 最小实现；后续若改成 pivot/zone 版，应另立变体，不应回写本 spec。
- 当前 worktree 脏文件很多，本轮继续避免任何混合提交。

## 下一步建议
- 下一刀优先实现 `raw_breakout + volume_only + combo_all` 三档，先给 Rank 2 一个本地 first verdict；
- 若 `volume_only` 单独有效、但 `support_flip / higher_low` 没继续增量，就把它诚实收窄成更窄的 execution guard；
- 若全部没有增量，就及时 `bench`，不要把这条线拖成又一轮文献复述。

## git / 提交
- 本轮未提交。
- 原因：当前工作区存在大量与本轮无关的既有脏文件与未跟踪文件，不适合安全 selective commit；本轮只刷新必须的脚本 / artifact / 页面。