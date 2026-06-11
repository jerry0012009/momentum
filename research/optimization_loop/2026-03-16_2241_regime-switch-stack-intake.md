# 2026-03-16 22:41 UTC — regime-switch stack intake

## 为什么这轮选这个
- 先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 检查：`Paper Seat = EMA` 当前仍是 `waiting_not_due / due_soon`，不能在 waiting-window 空转。
- 再比较 active Scout 候选的边际价值：
  - `Rank 2 combo_all` 已进入 `narrow paper pilot approved`，当前没有真实 `append/review` need，继续补 wiring 的边际价值低；
  - `Rank 7 adaptive trend combo` 与 `Rank 8 EMA shielding` 都已完成 `clean replication + Light Stability Pack`，当前 hard verdict 都是 `park / evidence pool`；
  - 因此当前更诚实的主资源动作是切去**新的 paper / repo based 15m crypto intake**。
- 在现有 digest 里，`regime-switch indicator stack` 的边际价值高于继续重看旧候选：它能把“`downtrend` 里别硬买、`fluctuating` 里提高门槛”压成新的快筛入口，而且只复用现有 `EMA / PSAR / RSI` 组件，不需要新数据源。

## 本轮主点
- 主点：`Run 2 / Scout Fast Lane` 新 intake —— `Rank 9 regime-switch indicator stack / no-buy-downtrend gate`
- 紧邻子点：把 `TODO` 与 Scout shortlist 最小写回，避免下一轮继续把默认主资源绑回 `Rank 2/7/8`。

## 做了什么
### 1) 新增 clean-room spec 生成脚本
新增：
- `scripts/build_regime_switch_stack_scout_spec.py`

它把论文里最值得迁移的原则收窄成一个 implementation-ready 的 `15m crypto` fast-lane spec：
- `candidate_id = scout_regime_switch_stack_15m_v1`
- 样本固定：`BTC / ETH / SOL | Binance 120d | 15m`
- `regime` 定义固定为：`EMA7(RSI14) > 60 = uptrend`，`< 40 = downtrend`，其余 `fluctuating`
- 组件只允许复用当前 desk 已有家族：
  - `ema_direction = sign(EMA20 - EMA50)`
  - `psar_protection = PSAR same-side filter`
  - `rsi_pullback = RSI14 timing layer`
- 第一轮实验矩阵固定为：
  - `ema_baseline`
  - `regime_gate_only`
  - `constrained_no_buy`
  - `regime_plus_psar_rsi`
- 执行口径继续与当前 Scout 快筛保持一致：
  - `next-bar open`
  - `1 ATR stop`
  - `2 ATR target`
  - `8-bar time stop`
  - `6 bps/side`

### 2) 生成 reader-facing artifact
落地产物：
- `reports/artifacts/scout_regime_switch_stack_15m/clean_room_spec_v1.csv`
- `reports/artifacts/scout_regime_switch_stack_15m/spec_meta.csv`
- `reports/site/factors/scout_regime_switch_stack_15m/report.html`

reader-facing 页明确写死两点：
1. 这页是 **clean replication 输入页**，不是成绩宣判页；
2. 当前 hard verdict 只是：**已通过 source intake、足够进入 clean replication；但在跑完 clean replication + Light Stability Pack 前，不能误写成 `paper candidate`。**

### 3) 同步 desk board / shortlist
最小更新：
- `docs/TODO.md`
  - 在 `Scout Seat` 候选阶段表中新增 `Rank 9 regime-switch indicator stack / no-buy-downtrend gate`，状态写成 `source intake / clean replication next`；
  - 把 `Next 3 bot3 runs` 的当前窗口排班更新为：`Rank 9 clean replication next；Rank 2 only on real append/review need`。
- `reports/artifacts/literature/scout_seat_fast_cycle_crypto_shortlist_v1.csv`
  - 新增 `Rank 9` 行，挂到 `2026-03-14_0128_regime-switch-indicator-stack.html` digest。

## 最小验证
已执行并通过：
1. `python3 scripts/build_regime_switch_stack_scout_spec.py`
2. `bash scripts/publish_homepage_index.sh`

验证结果：
- 新 artifact 已生成；
- 新 reader-facing 页已落到：
  - `reports/site/factors/scout_regime_switch_stack_15m/report.html`
- 首页索引已刷新并发布：
  - `https://jp.jerrypsy.top/momentum/`

## 硬结论（hard verdict）
- **`Rank 9 regime-switch indicator stack / no-buy-downtrend gate` 当前应读作：`source intake / clean replication next`。**
- 它的价值不在于复述论文日频 headline，而在于把一个更贴近 desk 当前目标的原则压成可直接实现的 15m crypto 候选：
  - `downtrend` 里默认禁买；
  - `fluctuating` 里提高门槛；
  - 只用现有 `EMA / PSAR / RSI` 组件，不新开大框架。
- 但在跑完 `clean replication + Light Stability Pack` 之前，**它还不是 `paper candidate`，更不是 `Live Seat` 候选。**

## 对 desk 主线的意义
- 这轮减少的是 **Scout Seat fresh intake 断层**：
  - 避免 `EMA waiting_not_due` 时，bot3 继续在 `Rank 2` wiring 与已 `park` 候选之间打转；
  - 给当前 board 明确要求的 `paper / repo based 5m / 15m crypto` fast lane 补上一条新的实现入口。
- 同时这条线比继续强调 breakout 更贴合当前口径：它不是重新炒作旧 breakout，而是补一条新的 `regime gate` 候选，看看能不能更快筛出下一条 `paper candidate`。

## 风险 / 边界
- 本轮没有产出新的收益数字，也没有完成 clean replication；
- 它没有改变现有 seat verdict：
  - `Paper Seat = EMA` 不变；
  - `Live Seat = 暂空` 不变；
  - `Rank 2 combo_all` 仍是 `narrow paper pilot approved`；
- 这轮唯一新增的是：**新的 Scout 候选已从 digest 想法推进到 implementation-ready spec。**

## 下一步建议
- 下一轮 Run 2 默认优先按这张 spec 做最小 clean replication；
- 第一刀重点先看：
  - `post_cost_return`
  - `positive_asset_ratio`
  - `trades_per_asset`
  - `no_trade_ratio`
  - `cost_survival`
- 若最优版本只是靠 `no_trade_ratio` 飙升才守住收益，则应直接 `park`，不要把“少做交易”误写成 alpha 增量。

## 网页可见落点
- `reports/site/factors/scout_regime_switch_stack_15m/report.html`
- `docs/TODO.md`（及其站点镜像 / Control Tower）
- `https://jp.jerrypsy.top/momentum/`

## Git / 提交
- 未提交。
- 原因：当前工作区存在大量与本轮无关的脏文件 / 未跟踪产物，不适合安全 selective commit。
