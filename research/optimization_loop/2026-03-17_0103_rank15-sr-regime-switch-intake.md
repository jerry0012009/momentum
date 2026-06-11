# 2026-03-17 01:03 UTC｜Scout Seat：Rank 15 support/resistance regime-switch confirmation gate intake

## 为什么这轮选这个
先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 执行：

- `Run 1 / Paper Seat`：`EMA` 上一轮已完成 `Crypto 1d+1wk` 的 due-now refresh，当前重新回到 `waiting_not_due`，这轮不能停在 waiting-window 空转；
- `Run 2 / Scout Seat`：当前默认主资源位；
- `Run 3 / tiny-live plumbing`：只有在 `Scout Seat` 也没有合格动作时才回退。

本轮先比较 active Scout 候选的边际价值：

1. `Rank 2 combo_all`
   - 仍是 `narrow paper pilot approved`；
   - 当前没有新的真实 `append/review need`，继续做大概率又会滑回近义 wiring。
2. `Rank 7 ~ Rank 14`
   - 都已完成 `clean replication + Light Stability Pack` 并压回 `park / evidence pool`；
   - 当前没有新的数据源 / 新 spec / bot2 重开指令，不该继续吃默认主资源。
3. 新鲜候选里，`Henderson et al. (2021/2025)` 这条 `support/resistance regime-switch confirmation gate`
   - 是 paper-based、并且更贴当前 `15m crypto` fast lane；
   - 不需要新数据源，可直接复用现有 structure / zone / EMA / ATR 资产；
   - 能把“第一次越线就追”收窄成 `provisional_break -> confirmed_switch`，直接回答确认层到底有没有边际价值。

因此这轮主点定为：**把 support/resistance 的 path-dependent regime-switch 思想，从 digest 直接推进到 implementation-ready clean-room spec，并把它写回当前 Scout board。**

## 本轮主点（1 个）
- 新增脚本：`scripts/build_sr_regime_switch_scout_spec.py`
- 把这条候选压成最小、可执行、可审计的 15m crypto clean-room spec：
  - `candidate_id = scout_sr_regime_switch_15m_v1`
  - 样本固定：`BTC / ETH / SOL | Binance 120d | 15m`
  - 线位来源固定：只允许使用当前已确认的 causal zone / active support-resistance
  - 状态机固定：`touch_or_cross -> provisional_break -> confirmed_switch`
  - 第一轮实验矩阵固定为：
    - `touch_or_cross_baseline`
    - `confirm1_outside`
    - `confirm2of3_outside`
    - `retest_hold_reclaim`
  - 执行口径固定：
    - `next-bar open`
    - `1 ATR stop`
    - `2 ATR target`
    - `8-bar time stop`
    - `6 bps/side`

## 紧邻子点（1 个）
- 最小回写 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 与 `scout_seat_fast_cycle_crypto_shortlist_v1.csv`：
  - 新增 `Rank 15 support/resistance regime-switch confirmation gate`
  - 明确它当前状态是 `source intake / clean replication next`
  - 在 `Run 2` 的 active Scout 顺位里补上 `2i`，避免下一轮继续把默认主资源绑回已 `park` 的旧候选

## 产物 / deployable artifact
### 新脚本
- `scripts/build_sr_regime_switch_scout_spec.py`

### 新 artifacts
- `reports/artifacts/scout_sr_regime_switch_15m/clean_room_spec_v1.csv`
- `reports/artifacts/scout_sr_regime_switch_15m/spec_meta.csv`

### 网页可见落点
- `reports/site/factors/scout_sr_regime_switch_15m/report.html`
- `docs/TODO.md` 顶部 `TRADING DESK BOARD`（Control Tower 会同步）
- `https://jp.jerrypsy.top/momentum/`

## 最小验证
已执行：

1. `python3 /root/clawd/jerry/momentum/scripts/build_sr_regime_switch_scout_spec.py`
2. 核对：
   - `reports/artifacts/scout_sr_regime_switch_15m/spec_meta.csv`
   - `reports/artifacts/scout_sr_regime_switch_15m/clean_room_spec_v1.csv`
   - `reports/site/factors/scout_sr_regime_switch_15m/report.html`
3. 写回并复核：
   - `reports/artifacts/literature/scout_seat_fast_cycle_crypto_shortlist_v1.csv`
   - `docs/TODO.md`
4. `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`

执行结果：
- 脚本成功输出：`[ok] sr regime-switch scout spec generated`
- 首页成功刷新并发布：`https://jp.jerrypsy.top/momentum/`

## 硬结论（hard verdict）
- **`Rank 15 support/resistance regime-switch confirmation gate` 当前最诚实的读法是：`source intake / clean replication next`。**
- 这条线当前最值钱的点，不是再发明新线位，而是更锋利地回答：
  - `第一次越线是不是太早？`
  - `confirm1 / confirm2of3 / retest_hold` 这些确认层，能不能比 `touch_or_cross` 更诚实地代表状态切换？
- 但在补完最小 clean replication 与 `Light Stability Pack` 之前，**它还不是 `paper candidate`，更不是 `Live Seat` 候选。**

## 对主线的意义
- 这轮没有改变 `Paper Seat = EMA` 的席位判断；
- 也没有给 `Live Seat` 送出新的 promoted candidate；
- 但它确实把一个新的 paper-based fast-lane 候选，从“paper digest”推进到了“下一轮可直接做 clean replication”的状态；
- 相比继续在 `Rank 2` 上补近义 wiring，或重看已 `park` 的 `Rank 7~14`，这更符合当前 board 的资源分配规则。

## 风险 / 边界
1. 这条 spec 迁移的是论文里的机制视角（path-dependent regime switch），不是连续时间最优停时模型的 faithful 数值复刻；
2. 当前 v1 刻意只做 long-or-flat，不把 breakout short 拉回主舞台；
3. 这轮没有任何收益 / 稳定性数字，因此当前只能诚实写成 `clean replication next`，不能抢跑写成 `paper candidate`。

## Git / 提交
- 未提交。
- 原因：工作区里存在大量与本轮无关的脏文件与未跟踪文件，不适合安全 selective commit。

## 下一轮建议
- 若 `EMA` 仍是 `waiting_not_due`：`Run 2` 默认可优先认领 `Rank 15` 的最小 clean replication；
- 第一刀重点先看：
  - `post_cost_return`
  - `false_break_ratio`
  - `positive_asset_ratio`
  - `trades_per_asset`
  - `no_trade_ratio`
  - `cost_survival`
- 若 clean replication 后只是靠 `no_trade_ratio` 飙升才显得更稳，或对 `touch_or_cross_baseline` 没有明确增量，默认直接 `park`。
