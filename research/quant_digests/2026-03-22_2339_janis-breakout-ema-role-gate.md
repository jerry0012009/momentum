# 别把 breakout 直接配固定 ±2% 就当 15m 可用：在 Janis 仓库骨架里，EMA 更像 context gate，不是和 breakout 平级的第二触发键
- 时间：2026-03-22 23:39 UTC
- 类型：GitHub 仓库 + Binance 公共数据最小快检
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/raw-alpha/breakout/fixed-bracket/ema-stack/context-gate/repo/crypto/15m
- 证据类型：仓库规则审阅 + 本地最小复核

## 1) 这次看了什么
这轮主看 **Janis174756 / Binance-Futures-Trading-Bot (2026)** 里一个非常“可快检”的旁支：
- `breakout()` 用 `20-bar` 前高/前低触发，且固定 `SL=0.98*entry, TP=1.02*entry`；
- 同仓库另有 `tripleEMAStochasticRSIATR()`（`EMA9/21/50` 顺序 + RSI 限制）。

我没有复刻整套机器人，而是把这两个模块拆成一个 desk 可执行问题：
> **在 15m 上，breakout + 固定 ±2% bracket 是否应先过 EMA stack context gate？**

## 2) 核心结论（先说人话）
- **一句话结论：** 在这个仓库骨架下，`EMA9/21/50` 更像 breakout 的 **上下文过滤层**；直接裸跑 breakout + 固定 ±2% 会把很多低质量单带进来。  
- **一句话证据：** 同样 120 天、同样 15m、同样 ±2% first-hit 判决，`raw` 的期望分数只有 `0.025`，加 `EMA gate` 后升到 `0.053`，同时交易频率下降约 `31%`（更像“少做差单”，不是“靠加仓赚钱”）。

### 关键数据点（Binance Spot 15m，BTC/ETH/SOL，最近 120 天）
判决口径：信号后 24 根（6h）内，先 hit `+2%` 记 `continue`，先 hit `-2%` 记 `fail`，都没 hit 记 `timeout`。

1) **总体验证：EMA gate 明显优于 raw breakout**
- `raw`: `n=3109`, `continue 22.1% / fail 19.6% / timeout 58.3%`, `exp_r=0.025`, `8.64 笔/天/币`
- `ema`: `n=2138`, `continue 25.1% / fail 19.8% / timeout 55.1%`, `exp_r=0.053`, `5.94 笔/天/币`

2) **raw 的 long 侧几乎没有优势，说明“上破就追”不够诚实**
- `raw long`: `exp_r=-0.001`（接近 0，略负）
- `raw short`: `exp_r=0.051`

3) **EMA gate 后，多空两侧都被“净化”，但 short 改善更明显**
- `ema long`: `exp_r=0.037`
- `ema short`: `exp_r=0.067`

> 读法：这组结果不支持“EMA 与 breakout 平级双触发”；更支持“先用 EMA stack 做 regime/context，再让 breakout 去做触发”。

## 3) 为什么这题值得优先（而不是离开三条收口线）
- **对 V3 breakout-short follow-up：** 直接给了一条可执行收敛线——先过滤 context，再谈 post-break follow-up，避免“刚破就追”。
- **对 Fib retest_hold：** 这条也可当 Fib 前置门：只有在 EMA context 合法时，才让 retest_hold 进入确认队列（减少无趋势回踩噪音）。
- **对 EMA/PSAR raw alpha focus：** 这轮证据更支持“EMA 是角色层（gate）”，不是“再多加一个触发键就更强”。

如果不先做这一步，后面继续细抠 final-verdict / retest_hold，很多噪音其实来自“前门放人太松”。

## 4) 最小可复现实验（下一步怎么测）
下一步建议直接做一个 **2×2 小矩阵**（不要先上复杂模型）：

1. 触发层：
- A: `raw breakout(20)`
- B: `breakout(20) + EMA stack gate`

2. 判决层：
- V1: 固定 `±2%`（仓库原味）
- V2: `±k*ATR`（例如 `k=1.5/2.0`）

在 `BTC/ETH/SOL` 的 `5m/15m` 同时比较四个指标：
- `exp_r`（first-hit 期望分数）
- `timeout_rate`
- `trades/day`
- `post-cost proxy`（至少先扣单边手续费 + 1 tick 滑点）

**升级条件（进入 paper/shadow）**：B 在 5m/15m 都能维持 `exp_r` 提升，且交易数保留率 > 60%。

## 5) 风险与保留意见
- 本轮是 **proxy first-hit test**，不是完整组合回测；
- 固定 ±2% 来自仓库实现，本身可能对不同币种波动不公平；
- `timeout` 占比仍高（>55%），说明只靠 breakout+EMA 还不够，需要后续 follow-up/failure 判决层接力；
- 结果使用 Spot K 线代理，和永续合约（费率、基差、杠杆约束）仍有落差。

## 6) 来源
1. **Janis174756 (2026). _Binance-Futures-Trading-Bot_. GitHub Repository.**
   - Authors / Org: Janis174756
   - Year: 2026（仓库创建 2026-03-12，近期仍在更新）
   - Title: Binance-Futures-Trading-Bot
   - Venue: GitHub
   - DOI: N/A
   - Readable URL: <https://github.com/Janis174756/Binance-Futures-Trading-Bot>
   - Repo URL: <https://github.com/Janis174756/Binance-Futures-Trading-Bot>
   - 关键文件：<https://raw.githubusercontent.com/Janis174756/Binance-Futures-Trading-Bot/main/strategies/trading_strats.py>
   - 本文使用的关键规则：`breakout()`（20-bar 高低 + 固定 ±2%）与 `tripleEMAStochasticRSIATR()`（EMA9/21/50 + RSI）

2. **Binance Open Platform (2026). _Spot REST API – Kline/Candlestick Data_.**
   - Authors / Org: Binance
   - Year: 2026
   - Title: Kline/Candlestick data
   - Venue: Binance Developers Docs
   - DOI: N/A
   - Readable URL: <https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#klinecandlestick-data>
   - Repo URL: N/A

## 7) 产出文件（本轮）
- `scripts/run_janis_breakout_ema_role_proxy.py`
- `reports/artifacts/quant_digests/2026-03-22_janis_breakout_ema_role/events.csv`
- `reports/artifacts/quant_digests/2026-03-22_janis_breakout_ema_role/summary_by_variant.csv`
- `reports/artifacts/quant_digests/2026-03-22_janis_breakout_ema_role/summary_by_variant_side.csv`
- `reports/artifacts/quant_digests/2026-03-22_janis_breakout_ema_role/summary.json`
