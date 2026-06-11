# 别把 funding carry 继续写成只看 funding 数字：这份 2026 GitHub 仓库更该先测的是「richest-venue routing × hysteresis hold」完整 raw alpha
- 时间：2026-03-29 09:39 UTC
- 类型：2026 GitHub 仓库 + strategy/notebook 输出审阅 + perpetual 定价论文地基
- 主题类型：raw alpha
- 基础 alpha：同一币种跨 venue 做 `long spot@Binance + short richest-funding perp`（负 funding 分支可反向），并只在 funding 相对自身历史显著极端时入场，等异常回归后退出
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/carry/funding/cross-venue/relative-value/stat-arb/spot-perp/richest-venue-routing/hysteresis/min-hold/hyperliquid/gate/binance/1m/3m/5m/15m/repo/paper/external-data/cost
- 证据类型：工程实现证据 + notebook 输出审计 + 论文地基

## 1. 这次看了什么
主材料是 2026 GitHub 仓库 **`PietroC21/Crypto-PerpetualFutures`**。我重点看了：
- `strategy.py`
- `strategy_cross.py`
- `README.md`
- `notebook_cross.ipynb`
- `FINAL_Notebook.ipynb` / `FINAL_Notebook_V2.ipynb`

这次最值得 intake 的，不是“perp funding 能收租”这个老结论，而是它把一条 **cross-venue delta-neutral carry** 写成了完整策略：
1. 先在 Binance / Gate / Hyperliquid 之间选 **当期 richest funding venue**；
2. 再用 funding 相对自身历史的 **z-score** 判“现在是不是值得做”；
3. 然后用 **hysteresis + min_hold** 控 turnover；
4. 最后把 **OI gate / macro gate / 两腿成本** 一起落进回测里。

也就是说，这份材料真正补的是：**funding carry 不是“看 funding 大就上”，而是“route 到 richest venue，再等异常回归”**。

## 2. 核心结论
- **一句话核心结论：** 这份 repo 最值钱的不是证明 funding carry 存在，而是证明 **venue routing 本身就是 alpha 的大头**；没有 richest-venue routing，单 venue 版本在成本后很容易直接死掉。
- **一句话它怎么证明：** `notebook_cross.ipynb` 直接把 `Binance-only` 和 `cross-exchange` 并排跑了，而且把 `best_fr`、venue share、gross/net、drawdown 都拆出来了。

几个最值得记住的数据点：
- `notebook_cross.ipynb` 的显式代码输出里，**全样本 net cross-exchange** 版本是：`CAGR 13.9%`、`Ann.Vol 1.85%`、`Sharpe 2.56`、`Max DD 3.62%`。
- 同一 notebook 的 `2023-09 以后` 对比里，**Binance-only net = -10.0% CAGR**，而 **cross-exchange net = +27.8% CAGR**；也就是说，真正把策略从“成本后不行”翻成“成本后能活”的，不是更复杂的预测器，而是 **richest venue routing**。
- 在 `2023+` 的 7 币样本里，repo 给出的 **Binance 平均 8h funding 只有 0.59 bps**，而 **best-exchange 平均 8h funding 达到 6.68 bps**，等于每个 8h 窗口多出 **+6.10 bps** 的可收取 carry uplift（约 `+1041.6%`）。
- exchange dominance 也很说明问题：repo 的 notebook 给出 **Binance≈45% / Hyperliquid≈55%** 的 active position share。意思不是 Binance 没用，而是 **如果不允许路由到更“贵”的 perp venue，alpha 会被你自己砍掉大半**。
- 退出逻辑同样关键。`strategy_cross.py` 不是简单地“z 小于 entry 就平”，而是：
  - `z_entry = 2.0`
  - `z_exit = 0.0`
  - `min_hold = 3`（即至少持有 `3 × 8h = 24h`）
  这本质上就是在对抗 **carry 策略最常见的 fee drag**：刚开完就被小幅回摆洗掉，来回交手续费。

### 2.1 这份材料真正新增了什么
最近素材池里已经有不少 funding / carry 主题，但很多更像：
- sign prediction
- APR gate
- spread veto
- duration gate
- forced refresh

这份 repo 的真正新增点，是把上面这些再往前推进了一步：**它把“去哪条腿收 funding”这件事单独抬成核心 alpha 组件**，并且给了一个很诚实的对照：
- 单 venue：成本后容易负；
- richest-venue routing：成本后转正。

对当前 desk 来说，这比再加一个泛泛的 funding filter 更像 **可落地的完整原型**。

### 2.2 需要诚实保留的 caveat
这份仓库里不同 notebook 版本的 headline 数字 **并不完全一致**：
- 有的版本写 `Net CAGR 5.76%`
- 有的版本写 `Net CAGR 13.9%`
- 有的版本甚至写到 `Net CAGR 28.1%`

所以这里不能把 repo 的收益表当铁证。**更可信的不是精确收益率数值，而是结构性结论：`Binance-only` vs `cross-exchange` 的符号翻转、best-funding uplift、以及 hysteresis 对 fee drag 的治理。**

## 3. 为什么和当前项目有关
这条线和当前 desk 直接相关，因为它满足这轮最优先的那一类：**可独立复现且可直接落地为完整策略的 raw alpha。**

它不是纯 overlay，也不是把 funding 硬装成 15m bar-bar 主信号；它是一条很明确的 **carry / relative-value / stat-arb**：
- alpha 本体由 funding cashflow 提供；
- `1m / 3m / 5m / 15m` 负责的是 **监控、排队、择 venue、控制价差、执行进出**；
- funding clock（8h / 1h）负责兑现收益。

这正好符合当前短周期 desk 的真实读法：
**慢的是 cashflow 结算，不慢的是 entry / routing / spread / inventory 风险。**

## 3.5 策略拆解（必填）
- 方向属性：carry / relative-value / cross-venue delta-neutral
- 基础 alpha：`best_funding_venue_rate - local_funding_venue_rate - trading_cost - spread_drift - hedge_slippage`
- regime：只在 richest venue 的 funding 明显高于该币自身历史常态，且腿间价格没明显失真、成交量/OI 仍健康时启动；负 funding 分支可保留为二阶段扩展
- filter / veto：
  - `best_fr_z > z_entry` 才做正 funding 分支；
  - `cross-venue spread` 过宽直接 veto；
  - `OI < rolling_mean × 0.5` veto；
  - repo 还用了 `VIX > 30` 或 `SPY 5d DD > 5%` 的 macro gate
- risk / sizing / execution overlay：
  - 仓位可用 `fixed 1/N_universe` 或 `1/N_active`；
  - 进入后至少持有 `24h`，只有当 funding anomaly 真回归才退出；
  - 成本模型显式包含 perp leg + spot leg taker fee；
  - 先 route 到 richest venue，再决定下不下单；
  - 单 venue 无 edge 时不强行开仓

## 4. 可复刻的最小实验
### 4.1 研究假设
对 short-cycle desk 来说，**真正值得先复现的不是“funding 是否为正”，而是“richest venue routing + hysteresis hold”能否把 cross-venue carry 从 fee-negative 翻成 fee-positive。**

### 4.2 数据源、公开性、更新频率
1. **Funding rates（公开可得）**
   - Binance：8h funding
   - Gate / Hyperliquid：1h funding，可聚合成 8h 等价 funding
   - 公开性：公开接口可抓；不下单时无需私钥
   - 更新频率：1h 或 8h

2. **Spot / perp quotes（公开可得）**
   - Binance spot mid / perp mid
   - richest venue 的 perp bid/ask / mid
   - 公开性：公开 order book / ticker 接口可抓
   - 更新频率：秒级到分钟级，可聚合到 `1m / 3m / 5m / 15m`

3. **Open interest（公开可得或可替代）**
   - 先用交易所公开 OI；如果历史不齐，可先只做 top-liquid majors
   - 更新频率：分钟到小时级

4. **Macro gate（可选）**
   - repo 用了 `VIX / SPY` 日频序列
   - 对 desk 的 first pass 可以先简化成 `BTC realized vol gate`，避免先被外部宏观依赖卡住

### 4.3 最小实验口径
先不要一上来复现全宇宙全双向，先做一个诚实的 3 步版：

1. **只做正 funding 分支**
   - 标的：`BTC / ETH / SOL`
   - 每 `15m` 记录一次：
     - `best_fr_t = max(Binance_8h, Gate_1h×8, HL_1h×8-equivalent)`
     - `best_exch_t = argmax(best_fr_t)`
     - `spread_t = perp_mid(best_exch_t) - spot_mid(Binance)`
     - `best_fr_z_t`

2. **三组策略并排**
   - A：`Binance-only` carry
   - B：`richest-venue routing`，但无 hysteresis（`z` 跌回 `2` 下方就退）
   - C：`richest-venue routing + hysteresis`（`z_entry=2.0, z_exit=0, min_hold=24h`）

3. **统一执行口径**
   - signal 冻结在已发布 funding + 已完成 `15m` quote/OI
   - `next bar open` 或下一个可成交 mid/taker proxy 入场
   - 明确计入：spot leg fee、perp leg fee、跨 venue spread、滑点 buffer
   - 输出核心指标：
     - `post-cost return / trade`
     - `carry realized vs quoted funding`
     - `turnover`
     - `spread blowout frequency`
     - `capital utilization`
     - `venue share`

## 5. 先记住的交易结论
如果这条线要进 desk，正确写法不是“funding 高就收租”，而是：
**先找 richest venue，再等 funding anomaly 回归；如果你不能 route 到 richest venue，或者 hold 不够久把 carry 兑现出来，这条策略很可能在成本后直接从正变负。**

## 6. 下一步怎么测
1. **先把 routing edge 单独拆出来**：固定同一组币，同一成本模型，只比较 `Binance-only` vs `richest-venue`，别一开始就把所有 gate 都揉在一起。
2. **再把 hysteresis 单独拆出来**：比较 `immediate exit` vs `z_exit=0 + min_hold=24h`，确认净收益是不是主要来自减少 fee drag。
3. **把 15m desk 化执行补齐**：不是逐根猜方向，而是每 `15m` 重算 `best_fr / best_exch / spread / OI`，把 venue route 和入场时机变成可调度对象。
4. **做一张“quoted funding → realized carry” 对账表**：很多 carry 策略回测赢在 quoted funding，实盘输在 quote drift、腿间 spread 和换腿成本；这一步必须先审计。
5. **负 funding 分支放到第二阶段**：先把 `long spot + short perp` 的正 funding 分支做通，再决定要不要扩到 `short spot + long perp` 或替代对冲腿。

## 7. 来源
1. **Bavaresco, C., Candiani, P., Desauty, T., Donnelly, A., & Nguyen, K. (2026). _Crypto-PerpetualFutures / Cross-Exchange Delta-Neutral Spot-vs-Perp Cash-and-Carry_. GitHub / QTS Final Project.**
   - Authors: Cesare Bavaresco, Pietro Candiani, Thibaut Desauty, Alan Donnelly, Khanh Nguyen
   - Year: 2026
   - Title: *Crypto-PerpetualFutures* / *Cross-Exchange Delta-Neutral Spot-vs-Perp Cash-and-Carry*
   - Venue: GitHub / course project
   - DOI: N/A
   - Readable URL: https://github.com/PietroC21/Crypto-PerpetualFutures
   - Repo URL: https://github.com/PietroC21/Crypto-PerpetualFutures

2. **Park, H., Choi, M., & Lim, A. E. B. (2025). _Designing funding rates for perpetual futures in cryptocurrency markets_. arXiv.**
   - Venue: arXiv
   - DOI: https://doi.org/10.48550/arXiv.2506.08573
   - Readable URL: https://arxiv.org/abs/2506.08573
   - Repo URL: N/A

3. **He, S., Manela, A., Ross, O., & von Wachter, V. (2024, v6). _Fundamentals of Perpetual Futures_. arXiv.**
   - Venue: arXiv
   - DOI: https://doi.org/10.48550/arXiv.2212.06888
   - Readable URL: https://arxiv.org/abs/2212.06888
   - Repo URL: N/A
