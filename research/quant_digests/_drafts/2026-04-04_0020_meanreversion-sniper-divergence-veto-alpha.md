# 别把这份今天还在更新的 adaptive-grid repo 只读成 infra：对 short-cycle desk，更该先测的是「extreme stretch × CVD/OFI divergence × no-liq-surge」这条 countertrend raw alpha

- 时间：2026-04-04 00:20 UTC
- 类型：2026 GitHub 新 repo source audit（GitHub API metadata + `README.md` + `docs/07_GRID_POLICY_LIBRARY.md` + `docs/06_TOXICITY_SPEC.md` + `docs/STATE.md`）
- 主题类型：raw alpha
- 基础 alpha：**短窗价格极端伸展后的 exhaustion fade**；`CVD/OFI divergence` 只是 admission，`liq_surge / toxicity` 是 veto 与风险层，不是 alpha 本体
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是，但 repo 当前主要给的是 policy spec，回测与执行壳需要我们自己补
- 主题标签：raw-alpha/mean-reversion/single-asset/microstructure/exhaustion-fade/cvd/ofi/divergence/liquidation-veto/toxicity/1m/3m/5m/15m/repo/public-data/cost/risk
- 证据类型：repo policy-spec audit（主）

## 1) 先回答：这篇东西的 base alpha 是什么？
一句话先说清：

> **base alpha 不是 divergence，也不是 toxicity。base alpha 是“极端短窗 stretch 之后的回归”。**

repo 里真正适合我们 desk 单独拎出来的，不是整套 adaptive grid，而是 `Mean Reversion Sniper Policy` 这条旁支：
- 先找 **5m 极端伸展**；
- 再要求 **1m order-flow 出现背离/衰竭**；
- 同时 **不在 liquidation surge 里硬接飞刀**；
- 最后用小仓位、紧 time-box/stop 去做 countertrend fade。

所以它符合这轮优先级里的 `raw alpha`：
- alpha 本体：**exhaustion fade / short-horizon mean reversion**
- admission：`CVD/OFI divergence`
- veto：`liq_surge`, `toxicity_high`
- risk shell：tight stop、短持有、缩尺

这很重要，因为 `docs/FACTOR_BACKLOG.md` 已经把 **Price-volume divergence** 标成了 `REVIEWED + PARKED`——也就是“单独拿出来当主角，证据偏弱”。这份新 repo 真正有意思的地方，恰恰是它**没有把 divergence 伪装成独立 alpha**，而是把它塞回一个更像样的 raw-alpha 壳里。

---

## 2) 为什么这轮选它
当前研究池里已经有：
- liquidation continuation
- liquidation panic MR
- 各种 BB/RSI/z-score fade
- 若干 trend / carry / pairs 壳

但还缺一类更适合 `1m / 3m / 5m` 的中间带：

> **不是单纯 price extreme 就反手，也不是单纯背离就硬做；而是“极端 stretch + order-flow exhaustion + 非清算冲击窗口”三件套合在一起。**

这类 alpha 的好处是：
1. **足够短周期。** 主信号天然更适合 `1m / 3m`，也能下沉成 `5m`；
2. **base alpha 清楚。** 不是 overlay，不是解释层；
3. **与 factor backlog 最近学习一致。** divergence 单独证据弱，那就别再把 divergence 当主角，而是让它服务 raw alpha admission；
4. **能直接拆成完整策略。** entry / exit / sizing / veto / cost 都能明确写出来。

所以这轮比继续补另一个“泛 breakout/泛 funding”更值得。

---

## 3) 来源与可追溯信息
### 3.1 主来源（repo）
- **Author / Owner：** `bnzr-team`
- **Year：** 2026
- **Title：** `grinder`
- **Venue：** GitHub repository
- **DOI：** N/A
- **Readable URL：** <https://github.com/bnzr-team/grinder>
- **Repo URL：** <https://github.com/bnzr-team/grinder>
- **Description：** `GRINDER - Adaptive Grid Trading System for Crypto Perpetuals`
- **GitHub metadata：** created `2026-01-30T19:23:27Z`, updated `2026-04-04T00:08:42Z`, pushed `2026-04-04T00:18:20Z`

### 3.2 这轮真正有用的文件
- `README.md`
- `docs/07_GRID_POLICY_LIBRARY.md`
- `docs/06_TOXICITY_SPEC.md`
- `docs/STATE.md`

### 3.3 重要保留：repo 的“最值钱部分”目前主要还是 spec，不是已完成 backtest
`README.md` 和 `STATE.md` 都写得很清楚：
- infra / replay / live remediation 很成熟；
- 但 **policy library 里很多更聪明的 alpha/policy 还是 docs/spec 层**；
- 尤其这次看的 `Mean Reversion Sniper Policy` 更像“已经写清规则、尚未严肃回测”的策略说明。

所以这篇 digest 的定位不是“repo 已经替我们证明了 alpha”，而是：

> **repo 今天提供了一条足够清晰、可直接搬去做最小实验的 raw-alpha 规格。**

---

## 4) repo 里这条 raw alpha 到底怎么定义
`docs/07_GRID_POLICY_LIBRARY.md` 给的 `MeanReversionSniperPolicy` 规则相当直接：

### 4.1 入场骨架
1. **价格到极端**
   - `momentum_5m > +3`：视为向上过热；
   - `momentum_5m < -3`：视为向下过热。

2. **出现衰竭/背离确认**
   - 若价格向上极端，但 `cvd_change_1m < 0`，说明价格上去、净主动买量却没跟；
   - 或 `ofi_zscore < -1`，说明盘口/订单流并不支持继续向上；
   - 向下极端时反过来：要求 `cvd_change_1m > 0` 或 `ofi_zscore > 1`。

3. **不能正处在 liquidation surge**
   - `liq_surge = False`
   - 也就是：不在强制平仓瀑布正在发生时硬接反手。

### 4.2 仓位与报价骨架（repo 给的参数）
- `sniper_spacing_bps = 8`
- `sniper_levels = 3`
- `sniper_size = 60`
- 极端阈值：`3.0`

翻成人话：
- 这不是大仓抄底/摸顶；
- 这是**小尺寸运行的 countertrend sniper**；
- 目的是抓“最后一脚”的回摆，而不是赌趋势反转成大级别拐点。

### 4.3 repo 外再加一层风险约束（来自 `docs/06_TOXICITY_SPEC.md`）
repo 的 toxicity spec 还明确写了：
- `toxicity_score > 2.0` 视为 `TOXICITY_HIGH`
- 高毒流下应 pause / throttle

这对 desk 的意义很直接：
- **alpha 本体是 exhaustion fade**；
- **toxicity 只是 execution/risk veto**；
- 如果把这层拿掉，countertrend 单很容易在“表面像衰竭、实则是毒流 continuation”的时段被打穿。

---

## 5) 这条东西为什么算 raw alpha，而不是又一个 filter 话题
关键在于别把组件主次搞反。

### 5.1 真正的 alpha 本体
这条线的本体是：

> **短窗极端伸展后的均值回归 / 回摆。**

也就是：
- 价格先走到 stretch 区；
- 我们赌后面会有一小段回摆；
- 赚的是这段回摆，不是背离本身。

### 5.2 divergence 在这里是什么
不是主 alpha，只是 **admission**：
- 没有 divergence，不开；
- 有 divergence，才说明“极端 move 可能已经开始空转”。

这和 backlog 里被 parked 的“纯 price-volume divergence”是两回事。

### 5.3 liquidation / toxicity 又是什么
- `liq_surge`：**硬 veto**，防止把正在发生的 forced move 误判为 exhausted move；
- `toxicity_score`：**执行风险 veto**，防止在 adverse-selection 过强时继续做 countertrend。

所以完整拆解应该写成：
- **raw alpha：** extreme-stretch fade
- **admission：** CVD / OFI divergence
- **veto：** no-liq-surge + toxicity cap
- **risk shell：** small size + tight stop + short hold

---

## 6) 与当前 short-cycle（1m / 3m / 5m / 15m）的关系
这条东西不是慢频，也不该伪装成 15m 大波段策略。更合理的落地是：

### 6.1 主战场：`1m / 3m`
- `1m`：做 `CVD`, `OFI`, `liq_surge proxy`, `toxicity proxy`
- `3m`：做更稳的 entry bucket，减少假信号抖动

### 6.2 次战场：`5m`
- 用 `5m` 定义 extreme stretch（例如 z-score、NATR-normalized return、distance-to-VWAP/EMA）
- `5m` 更像 state 定义层，而不是精细 execution 层

### 6.3 `15m` 的正确用法
- 不是把这条 alpha 直接粗暴抬到 15m 主做；
- 更适合作为 **higher-TF veto / context**：
  - 若 `15m` 处于强趋势扩张或高 toxicity 桶，降低或禁做；
  - 若 `15m` 只是普通 stretch，`1m/3m` 的 exhaustion fade 才有空间。

所以这条 raw alpha 更偏 **快频高强度**，是允许的那类 `1m / 3m` intake，不是默认 `15m` 壳。

---

## 7) desk 版最小可复现实验（可直接开工）
下面这版是我建议的 first pass，不照搬 grid，而是先把 alpha 本体剥出来。

### 实验 A：先只测 raw alpha 本体（不加 liquidation）
**标的：** `BTCUSDT`, `ETHUSDT`, `SOLUSDT` perpetual  
**频率：** `1m` 执行 + `5m` state

**信号定义**：
- `stretch_z_5m = zscore(5m return or 5m distance-to-VWAP, lookback 96~288 bars)`
- 做空条件：
  - `stretch_z_5m >= +3`
  - `cvd_change_1m < 0` **或** `ofi_zscore < -1`
- 做多条件：
  - `stretch_z_5m <= -3`
  - `cvd_change_1m > 0` **或** `ofi_zscore > +1`

**入场**：
- 触发后下一根 `1m` open 入场；
- 禁止同向连续加仓；
- 单信号只开 1 笔，不做 martingale。

**退出**：
- `time_stop = 3~8 bars`
- 或回到 `VWAP / EMA / stretch_z_5m` 中线附近；
- 或 `1 x ATR(1m)` 止损

**仓位**：
- `size ∝ 1 / realized_vol_1m`
- 上限小仓，先控制单笔风险在账户 `10~20 bps`

**成本**：
- 先跑 `2 / 4 / 6 / 8 bps` round-trip 梯度

### 实验 B：把 `liq_surge` veto 接上去
**公开数据路径**：
- Binance Futures `forceOrder` stream / 公开清算流
- 或可替代的 public liquidation feed / exchange event proxy

**规则**：
- 若信号出现时，最近 `N` 分钟 liquidation volume / liquidation count 超阈值，则：
  - 要么直接 veto；
  - 要么加 `cooldown = 2~5 bars` 再决定。

**要回答的问题**：
- 这层 veto 是真的减少接飞刀，还是把最好的一批 overshoot 都过滤掉了？

### 实验 C：再加 toxicity veto
**proxy**：
- spread spike
- book imbalance shock
- short-horizon impact proxy
- volume burst / range burst composite

**规则**：
- `toxicity > cutoff` 时不进场

**目的**：
- 判断 countertrend alpha 真死在“信号逻辑”还是“执行环境太毒”。

---

## 8) 这个题最该盯的 4 个指标
这类 alpha 最容易被“看起来胜率还行”骗，所以建议 first pass 只看 4 组：

1. **净 `bps/trade`**
   - 不看 gross heroics，直接看成本后剩多少
2. **MAE / adverse excursion**
   - 这是 countertrend 单最核心的生死指标
3. **time-to-revert**
   - 若大多数胜单都要拖很久才回摆，这条线不适合 fast desk
4. **continuation false-positive rate**
   - 也就是：信号后没回摆，反而继续扩张的比例

如果 `liq veto + toxicity veto` 只能把 trade count 砍掉，却没明显改善 `MAE` 和 `net bps/trade`，那说明这条线只是“看起来更高级”，不是真的更有 edge。

---

## 9) 风险与我对这条线的保留意见
### 9.1 repo 目前更多是 spec，不是 production proof
不能因为仓库 infra 很完整，就默认 policy library 里的每条线都已经被证明。

### 9.2 divergence 很容易被误用
如果把这条 digest 错读成“divergence 就是 alpha”，那就又回到 backlog 已经提示过的坑里了。

### 9.3 liquidation veto 可能同时砍掉最肥的 edge
很多最猛的回摆，本来就发生在清算瀑布后。如果 veto 太硬，可能把最好样本过滤光。一定要测：
- `strict veto`
- `cooldown then allow`
- `no veto`

### 9.4 这条线天然偏快，容量别高估
它更像 `1m / 3m` 里抓局部回摆，不像 funding/pairs 那样容量自然大。上线前必须先看：
- 冲击成本
- 滑点随 size 上升的弯曲程度
- 信号拥挤时的 fill quality

---

## 10) 这轮最值得记住的一句话
如果只留一句：

> **别再把“背离”单独当主角；更值得测的是“extreme stretch 的 raw alpha”，然后让 CVD/OFI divergence 只做 admission，让 liquidation/toxicity 只做 veto。**

这正好把我们最近学到的东西摆正了：
- divergence 单独证据弱；
- 但放进一个结构清楚的 exhaustion-fade 壳里，它就可能从“玄学确认层”变成“有用 admission”。

---

## 11) 下一步怎么测
按优先级我建议直接这样排：

1. **先做 A：** `BTC/ETH/SOL`，`1m + 5m`，不加 liquidation，只测 `stretch + divergence`
2. **再做 B：** 接 public liquidation veto，比较 `strict / cooldown / none`
3. **最后做 C：** 接 toxicity veto，看有没有明显改善 `MAE` 和成本后净值
4. **周期迁移：**
   - 主看 `1m / 3m`
   - 再看 `5m`
   - `15m` 只做 context gate，不要硬装成主信号

如果 A 本体都活不下来，就别因为 repo 写得漂亮而继续投时间；
如果 A 活、B/C 还能明显改善 `MAE` 与 post-cost edge，这条就值得进入下一轮复现队列。

---

## 12) 来源链接
1. **