# 别把 Heikin Ashi 当新 alpha：在 5m/15m 上它更像 breakout-short / Fib / EMA-PSAR 的 `neutral-state veto`
- 时间：2026-03-22 17:43 UTC
- 类型：GitHub 仓库 + Binance 公共数据最小快检
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/heikin-ashi/neutral-state/veto/anti-chop/regime/filter/repo/crypto/5m/15m
- 证据类型：仓库规则 + 本地最小复核

## 1) 这次看了什么
这轮主看了两个仓库的“旁支信息”，不是抄主策略收益：

1. **Janis174756/Binance-Futures-Trading-Bot（2026, 546★）**
   - 这个高信号新仓库把 `heikin_ashi_ema` 放进策略菜单，提示 HA 在实盘社区里常被当作“降噪层”。
2. **Emindu/heikin_ashi_ema_strategy（2021, 2026 有更新）**
   - 代码里明确是 **4h EMA 方向偏置 + 1h Heikin Ashi indecision/confirm** 的双层结构（不是裸方向信号）。

对我们 desk 真正有价值的是：
> **HA 更像“状态过滤器”，尤其是把“中性/纠缠状态”先 veto，而不是再造一个主 alpha。**

## 2) 核心结论（先说人话）
- **一句话结论：** 在 5m/15m，Heikin Ashi 先当 `neutral-state veto` 比当“方向预测器”更诚实，直接服务三条收口线的 `avoid-chop / follow-up` 问题。  
- **一句话证据：** 用 BTC/ETH/SOL 的最小复核里，HA 版本相对 raw 版本都出现了更少换向（flip），且 `neutral` 桶在 breakout 代理事件里明显更差。

### 关键数据点（本地最小快检）
样本口径：`BTCUSDT/ETHUSDT/SOLUSDT`，Binance Spot 公共 `klines`，成本代理 `10~12 bps roundtrip`。

1. **EMA(9/21/50) 状态机换向次数下降（先看“降噪”）**
   - 15m（60d, pooled）：`raw_flips 1090 -> HA_flips 1024`（**-6.06%**）
   - 5m（30d, pooled）：`raw_flips 1693 -> HA_flips 1621`（**-4.25%**）

2. **同一套 proxy 下，HA 版本成本后表现不再像纯噪声**（仅作 first verdict，不作收益宣称）
   - 15m pooled：`raw_net_logret 0.398 -> HA_net_logret 1.163`
   - 5m pooled：`raw_net_logret -0.491 -> HA_net_logret 0.032`

3. **Breakout 代理事件里，HA-neutral 桶最差（更像该 veto 的区间）**
   - `neutral`：n=252，`mean_net4 = -0.0027`，`fail2_ratio = 65.08%`
   - `aligned`：n=666，`mean_net4 = -0.0010`，`fail2_ratio = 59.16%`

> 解读：这组证据更支持“先排除 HA-neutral”，而不是“HA 同向就必胜”。

## 3) 为什么这题比继续泛找更值得
它直接贴三条收口线：
- **V3 breakout-short follow-up**：先过滤 `HA-neutral`，避免在纠缠段追 continuation；
- **Fib confirmation / retest_hold**：回踩确认可先要求“非 neutral 状态”，降低“到位但没趋势承接”的假确认；
- **EMA / PSAR raw alpha focus**：把 HA 退化成廉价 anti-chop 过滤层，优先降翻向噪声和无效换手。

## 4) 最小可复现实验口径（本轮）
- 数据源：Binance Spot REST `GET /api/v3/klines`（公开可得）
- 资产：`BTCUSDT / ETHUSDT / SOLUSDT`
- 周期：`15m(60d)` + `5m(30d)`
- HA 定义：
  - `HA_close=(O+H+L+C)/4`
  - `HA_open=(prev_HA_open + prev_HA_close)/2`
- 状态代理：`EMA9/21/50` 的 bull/bear/neutral 三态
- Breakout proxy：20-bar 前高/前低突破 + candle 质量（body/range, close-location）
- 评估：`flip count`、`net_logret proxy`、`4-bar forward net`、`2-bar fail ratio`

## 5) 下一步怎么测（必须动作）
按三条收口线做 A/B/C（同成本、同样本、同执行延迟）：

1. `A = baseline`（无 HA 过滤）
2. `B = HA-neutral veto`（仅允许 `state != neutral`）
3. `C = HA directional gate`（要求 `state == signal direction`）

统一比较 4 个指标：
- `post_cost_expectancy`
- `tp_first - sl_first`
- `trade_count_retention`
- `timeout_share`

判定规则建议：
- 若 **B 在三条线都降 timeout / 降失败率**，优先升级为 shared gate；
- 若 C 的留存率显著塌缩或 side-bias 明显，就退回 B（只 veto neutral，不强行同向）。

## 6) 风险与保留意见
- 本轮是 quick proxy，不是正式 walk-forward；
- `net_logret` 为统一简化成本口径，不能直接当 production PnL；
- HA 有滞后，趋势强时有帮助，转折快时可能错过首段；
- breakout 代理里 misaligned 样本不大，当前只把 `neutral` 视作更稳妥的 first veto 候选。

## 7) 来源
1. **Janis174756 (2026). _Binance-Futures-Trading-Bot_. GitHub Repository.**
   - Authors / Org: Janis174756
   - Year: 2026（created_at 2026-03-07；updated_at 2026-03-22）
   - Title: Binance-Futures-Trading-Bot
   - Venue: GitHub
   - DOI: N/A
   - Readable URL: <https://github.com/Janis174756/Binance-Futures-Trading-Bot>
   - Repo URL: <https://github.com/Janis174756/Binance-Futures-Trading-Bot>

2. **Emindu (2021; updated 2026). _heikin_ashi_ema_strategy_. GitHub Repository.**
   - Authors / Org: Emindu
   - Year: 2021（updated_at 2026-01-09）
   - Title: heikin_ashi_ema_strategy
   - Venue: GitHub
   - DOI: N/A
   - Readable URL: <https://github.com/Emindu/heikin_ashi_ema_strategy>
   - Repo URL: <https://github.com/Emindu/heikin_ashi_ema_strategy>
   - 关键文件：`main.py`（4h EMA bias + 1h HA indecision/confirm）

3. **Binance Open Platform (2026). _Spot REST API – Market Data Endpoints (Kline/Candlestick Data)_.**
   - Authors / Org: Binance
   - Year: 2026（现行文档）
   - Title: Market Data endpoints / Kline/Candlestick data
   - Venue: Binance Developers Docs
   - DOI: N/A
   - Readable URL: <https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#klinecandlestick-data>
   - Repo URL: N/A

## 8) 产出文件（本轮）
- `reports/artifacts/quant_digests/heikin_ashi_phase_gate_proxy_20260322/ema_stack_raw_vs_ha_summary.csv`
- `reports/artifacts/quant_digests/heikin_ashi_phase_gate_proxy_20260322/ema_stack_raw_vs_ha_5m15m_summary.csv`
- `reports/artifacts/quant_digests/heikin_ashi_phase_gate_proxy_20260322/ema_stack_raw_vs_ha_5m15m_pooled.csv`
- `reports/artifacts/quant_digests/heikin_ashi_phase_gate_proxy_20260322/breakout_proxy_events_with_ha_state.csv`
- `reports/artifacts/quant_digests/heikin_ashi_phase_gate_proxy_20260322/breakout_proxy_ha_state_alignment_summary.csv`
- `reports/artifacts/quant_digests/heikin_ashi_phase_gate_proxy_20260322/breakout_proxy_ha_state_alignment_side_split.csv`
- `reports/artifacts/quant_digests/heikin_ashi_phase_gate_proxy_20260322/metadata.json`
