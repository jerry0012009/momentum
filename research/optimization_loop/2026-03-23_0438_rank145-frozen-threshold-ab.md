# 2026-03-23 04:38 UTC · Rank 145 / equity drawdown throttle + recovery hysteresis overlay frozen-threshold A/B

- 严格遵循：`docs/TODO.md` 顶部 `TRADING DESK BOARD` + `docs/AUTO_OPTIMIZATION_LOOP.md`
- 本轮类型：`Scout / Run 1 / Rank 145 最小稳定性检查`
- 范围控制：只推进 **1 个主点**（Rank 145）+ **1 个紧邻子点**（用 desk 现成共享代理判断它是否值得升到 `P2`）。

## 0. 先判 interrupt
- 未见 `Paper / 正在自动运行` runner 的真实 `stale / error / refresh 失步 / ledger 爆雷 / open-position 异常 / red-watch`。
- `EMA` 状态页显示 `waiting_not_due`，不是异常。
- 因此继续执行默认 Run 1，而不是抢 interrupt。

## 1. 本轮只做什么
按上轮 intake 的授权边界，这次只做 **1 次 frozen-threshold 本地 A/B**，不继续扩题：
- baseline：`Rank32b 15m primary 6bps` 现成交易明细
- 口径：先看 `BTC / ETH / SOL` 单资产，再看 `BTC+ETH+SOL` 等权合并共享代理
- overlay：
  - `equity_dd_from_peak > {8%,10%,12%}` → `size *= {0.25,0.5}`
  - `equity >= {95%,98%} * peak_equity` 才恢复
- 指标：
  1. `max_drawdown`
  2. `calmar`
  3. `post_cost_return`
  4. `time_in_reduced_mode`

## 2. 为什么拿 Rank32b 做共享代理
这不是说 Rank 145 只服务 Rank32b，而是当前 desk 上它是**最省成本、最接近真实 15m 交易流、又能覆盖 BTC/ETH/SOL 三资产**的现成基线。

如果 overlay 连这个共享代理都几乎不会触发，就说明它至少**现在还不值得升到 shared overlay 主资源位**。

## 3. 结果（核心）
### 单资产结果
- `BTC-USD`：baseline `post_cost_return=+19.54%`，`max_drawdown=4.44%`
- `ETH-USD`：baseline `post_cost_return=+33.41%`，`max_drawdown=6.77%`
- `SOL-USD`：baseline `post_cost_return=+99.31%`，`max_drawdown=3.43%`
- 在 `dd=8/10/12%` 的全部配置下：**一次都没有进入 reduced mode**，所以 A/B 结果与 baseline 完全相同。

### 共享代理结果（更重要）
- `PORT_EQW_BTC_ETH_SOL`（等权合并）baseline：
  - `post_cost_return = +47.89%`
  - `max_drawdown = 1.85%`
  - `calmar = 125.89`
  - `time_in_reduced_mode_ratio = 0.0`
- 在 `dd=8/10/12%`、`size=0.25/0.5`、`recover=95/98%` 的全部配置下：
  - **仍然 0 次触发降档**
  - `MDD improvement = 0%`
  - `return damage = 0%`

## 4. 这意味着什么
这不是“overlay 已被证明没用”，而是更诚实的一句：

> **在 desk 当前可直接复用的 Rank32b 15m 共享代理上，这组 frozen thresholds 根本没有被命中，因此当前还拿不出足够证据把 Rank 145 升到 `P2`。**

换成人话：
- 当前 proxy 的资金曲线本来就比较平，`8%~12%` 的权益回撤阈值太远；
- 所以这层风控并没有在现有 desk 共享代理里承担真实工作；
- 现在如果继续烧默认预算去“证明它可能以后会有用”，性价比不高。

## 5. 轻量 scorecard（本轮补充后的 authoritative 读法）
- `usefulness = 2/3`
- `time_stability = 1/3`
- `cross_asset_stability = 1/3`
- `cost_trade_stability = 2/3`
- `deployability = 2/3`
- `hard-fail flags = not_alpha_but_risk_overlay;thresholds_not_armed_on_local_proxy;shared_proxy_mdd_too_shallow;no_live_safety_gain_proven_yet`
- `recommended_action = keep_P1`
- `why_now = 这刀已经回答最关键问题：在 desk 现成共享代理上它还没有足够 leverage 改变 routing，因此不该继续占默认 primary`
- `main_weakness = 当前 frozen thresholds 在本地共享代理上一次都没触发，无法证明真实回撤压缩价值`

## 6. routing verdict
- `Rank 145` 维持：**`P1 / keep_P1`**
- 但状态从 `fresh intake admitted` 更新为：**`budget used / no promote / 退出默认 primary`**
- 原因：
  1. 本地 A/B 已做；
  2. 结果没有触发 overlay；
  3. 当前还不足以支持 `promote_P2`。

## 7. 产物
- `reports/artifacts/scout_rank145_equity_dd_throttle_overlay_15m/frozen_threshold_ab_summary.csv`
- `reports/artifacts/scout_rank145_equity_dd_throttle_overlay_15m/frozen_threshold_ab_summary.json`
- `reports/artifacts/scout_rank145_equity_dd_throttle_overlay_15m/frozen_threshold_ab_portfolio_trade_detail.csv`
- `reports/artifacts/scout_rank145_equity_dd_throttle_overlay_15m/frozen_threshold_ab_portfolio_summary.json`

## 8. 本轮结论
本轮不是把 Rank 145 做成新主线，而是**用最便宜的本地共享代理，及时证明它还不够强**：
- 它仍可留在 evidence pool / keep_P1；
- 但当前不该继续占用默认 Run 1；
- 下一个默认主资源位应回到更短、更能改变 routing 的 active compare / fresh reserve。