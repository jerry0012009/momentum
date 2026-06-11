# 别把回踩确认写成“只看当前这根 RSI”：`phase-wide RSI memory` 在 15m 更像 breakout-short / Fib / EMA-PSAR 的实用过滤层（且阈值应从 40/60 重标到 55/44）
- 时间：2026-03-21 00:41 UTC
- 类型：GitHub 仓库 + Binance 公共数据最小快检
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/rsi/retest/memory/filter/threshold-calibration/repo/crypto/15m
- 证据类型：仓库证据 + 本地最小复核

## 1) 这次看了什么
这轮主看一个近期仓库：**TheVision333/trading-bot（2026 更新）**，重点不是它整套策略，而是里面一个很适合我们 desk 的旁支细节：

> **RSI 不只看“触发当根”，而是看“整段回踩期里 RSI 有没有破坏趋势结构”**。

仓库在配置里给了 `RSI_RETEST_FLOOR` / `RSI_RETEST_CEIL`（默认 `40/60`），并在回踩阶段维护 RSI 状态。这个思路非常贴三条收口线：
- 对 `V3 breakout-short follow-up`：可做 continuation vs failed bounce 的 veto；
- 对 `Fib retest_hold`：可做 hold 质量过滤（不是碰线就算）；
- 对 `EMA / PSAR`：可做后置确认层，不抢主触发。

## 2) 核心结论（先说人话）
- **一句话结论：** 在 15m 上，`phase-wide RSI memory` 这件事有信息量，但仓库默认 `40/60` 对 crypto 过宽，几乎不过滤；更有区分度的起步阈值是 **long: min RSI≥55，short: max RSI≤44**。
- **一句话证明：** 用 `BTC/ETH/SOL` 近 240 天 15m 公共数据做最小事件快检后，`phase` 阈值相对只看 `entry RSI` 的分层更清晰、样本也更可用。

### 关键数据点（pooled，BTC/ETH/SOL）
1. **默认 40/60 基本失效**：
   - long 侧 `min RSI>=40` 通过率 = **100%**
   - short 侧 `max RSI<=60` 通过率 = **100%**
   => 对 15m 几乎没有过滤作用。

2. **phase 阈值（55/44）有可见分层**：
   - long：`min RSI>=55`（n=1298）`tp_first=45.53%`；不通过（n=152）`tp_first=36.84%`
   - short：`max RSI<=44`（n=1241）`tp_first=52.22%`；不通过（n=166）`tp_first=46.99%`

3. **phase 比 entry 更像“结构质量”**（同阈值 55/44 对比）：
   - long：entry 失败样本仅 28 条；phase 失败样本 152 条（更可检验）
   - short：entry 失败样本仅 35 条；phase 失败样本 166 条（更可检验）

## 3) 为什么比继续泛找新题更值得
这轮不是偏题，它直接帮三条收口线继续收敛：
- **breakout-short follow-up**：当回踩段 RSI 结构已被破坏，继续追更像吃“失败后的反抽”；
- **Fib retest_hold**：把“触位确认”升级成“触位 + 回踩动量结构没坏”；
- **EMA/PSAR raw alpha**：给 raw trigger 加便宜且可复核的 post-entry 过滤层，优先降错单密度。

## 4) 最小可复现实验口径（本轮）
- 数据源：Binance USDⓈ-M Futures 公共 K 线 API（公开可得）
- 资产：`BTCUSDT / ETHUSDT / SOLUSDT`
- 周期：`15m`
- 样本：近 `240d`
- 事件定义（轻量 clean-room proxy）：
  - breakout：20-bar 前高/前低突破 + breakout candle 质量约束（body/range≥0.5，收盘位于上/下 30%）
  - retest：12 bars 内回踩至 level ± 0.75 ATR
  - invalidation：反向超过 1.0 ATR
  - entry：reclaim 确认后 next-bar open
  - verdict：未来 8 bars 用 ±0.75 ATR 判断 `tp/sl/timeout`

> 说明：这是“旁支假设的 first verdict”，不是最终 production 口径。

## 5) 下一步怎么测（必须动作）
先别全局改参数，按三条收口线做同口径 A/B：

1. `A=baseline`（无 phase gate）
2. `B=phase gate`（long `min RSI>=55`，short `max RSI<=44`）
3. `C=soft sizing`（不 veto，只在不通过时 size×0.5）

统一看四个指标：
- `post_cost_expectancy`
- `tp_first - sl_first`
- `trade_count_retention`
- `timeout_share`

若 B/C 在 `breakout-short` 与 `Fib retest_hold` 同时改善且交易数未明显塌缩，再考虑把 55/44 升级为 shared 默认；否则回退为“仅单线 overlay”。

## 6) 风险与保留意见
- 当前是仓库旁支 + 快检，不是完整 walk-forward；
- `55/44` 只是起步阈值，不是终值；
- verdict 用的是统一 ATR barrier proxy，后续需接入策略真实止盈止损口径；
- pooled 指标正负受口径影响，当前主要看相对分层，不做绝对收益宣称。

## 7) 来源
1. **TheVision333 (2026). _trading-bot_. GitHub Repository.**
   - Authors / Org: TheVision333
   - Year: 2026（仓库最近更新）
   - Title: trading-bot
   - Venue: GitHub
   - DOI: N/A
   - Readable URL: <https://github.com/TheVision333/trading-bot>
   - Repo URL: <https://github.com/TheVision333/trading-bot>
   - 关键文件：`strategy/retest_signals.py`、`config.py`（`RSI_RETEST_FLOOR/CEIL`）

2. **Binance Developers. USDⓈ-M Futures Market Data API.**
   - Authors / Org: Binance
   - Year: 2026（文档现行版本）
   - Title: Kline/Candlestick Data (USDⓈ-M Futures)
   - Venue: Binance Developers Docs
   - DOI: N/A
   - Readable URL: <https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data>
   - Repo URL: N/A

## 8) 产出文件（本轮）
- `reports/artifacts/literature/retest_phase_rsi_events_2026-03-21.csv`
- `reports/artifacts/literature/retest_phase_rsi_summary_2026-03-21.csv`
- `reports/artifacts/literature/retest_phase_rsi_meta_2026-03-21.json`
