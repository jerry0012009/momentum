# 别把 `confirmed swing + HTF` 结构一致当 breakout-short 的 shared gate：它在 15m 更像 Fib / EMA 的 long-side context
- 时间：2026-03-20 11:12 UTC
- 类型：GitHub 仓库 + Binance 公共数据代理快检
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/market-structure/swing/htf-alignment/asymmetry/continuation/failure/filter/repo/crypto/5m/15m
- 证据类型：仓库代码（工程证据）+ 公开 OHLCV 最小代理快检

## 1. 这次看了什么
这次主看一个近 5 年新仓库：**TheVision333/trading-bot（2026）**。它不是给了一个“更神的指标”，而是把一个常见但容易被误用的旁支想法写得很清楚：
**先用确认过的 swing high/low 定义结构，再叠 15m→1h 的 HTF 结构一致性，作为 breakout/retest 的确认层。**

我重点抽取了 repo 里这 3 个可复用模块：
- `strategy/market_structure.py`：`SWING_LOOKBACK=5`，用“确认后才可用”的 swing（避免前看）；
- `strategy/mtf.py`：`merge_asof(direction='backward')`，只用已收盘 1h 结构；
- `strategy/retest_signals.py`：把结构一致性放在 retest 入场前，而不是单独开仓。

## 2. 核心结论
- **一句话核心结论：** `confirmed swing + HTF` 在 15m 上不适合做三条线共享的多空对称 gate；它更像 **Fib retest_hold / EMA continuation 的 long-side context**，对 breakout-short 反而容易变差。  
- **一句话证明方式：** 按 repo 同款“确认 swing + backward HTF 合并”口径，我用 Binance 公共 BTC/ETH/SOL 15m/1h（近 120 天）做了最小事件代理快检，对比 `raw break`、`LTF 对齐`、`LTF+HTF 双对齐` 的 4-bar 路径收益与 re-entry 率。

关键数据点（4-bar signed return，bps）：
1. **long 侧有改善迹象**：`long raw` 平均约 **-4.32 bps**，`long dual aligned` 平均约 **+4.82 bps**；re-entry 率从 **57.74%** 降到 **51.55%**。  
2. **short 侧明显恶化**：`short raw` 平均约 **-1.69 bps**，`short dual aligned` 变成 **-16.41 bps**（中位约 **-17.84 bps**），说明它不该直接用于 breakout-short 放行。  
3. **跨资产也不是“统一加分”**：`dual aligned long` 里 ETH 最好（均值约 **+10.40 bps**，re-entry 约 **41.46%**），但 BTC long 仍负、SOL long 分布很不稳；更说明它是“条件化上下文”，不是共享默认键。

## 3. 为什么和当前三条收口线有关
这轮值钱点不是“又多一个 gate”，而是**角色边界更清楚**：

- **V3 final-verdict / breakout-short follow-up**  
  当前证据不支持把 `dual bearish structure` 当 short 侧 shared admission。它更像 short-veto/size-down 的候选，而不是“对齐了就更该追空”。

- **Fibonacci confirmation / retest_hold**  
  这条线更偏 long 侧回踩确认，`confirmed swing + HTF bullish` 在这里更像“是否值得继续等 retest_hold”的上下文层，优先级高于拿去做 short 放行。

- **EMA / PSAR raw alpha focus**  
  对 EMA/PSAR continuation，更合理做法是把结构一致性当 **admission/sizing context**（尤其 long 侧），而不是强行当双向硬门；这样更符合“EMA 主干、PSAR 辅助”的当前角色判断。

## 4. repo 里最值得复用/复现的点
不是某个阈值，而是这套“防幻觉”的实现纪律：
1. **确认 swing 再用**（`j+n` 才确认）——减少“刚画出来就拿来交易”的重绘风险；
2. **HTF backward merge**——15m 时刻只看已收盘 1h 结构；
3. **结构层只当确认层**——不单独开仓，挂在既有 breakout/retest/continuation 之上。

翻成人话：这不是新 alpha，而是把“结构一致”从口号改成能回测、能审计、可复现的状态机骨架。

## 5. 可复刻的最小实验（下一步怎么测）
### 研究假设
`confirmed swing + HTF` 在 15m 更适合作为 long-side context（Fib/EMA），不适合 breakout-short 的 shared short-admission。

### 一个可计算定义（首轮冻结）
- 15m 上用 `n=5` 生成确认 swing 与 `market_structure`；
- 1h 上同法生成结构，并 `merge_asof(backward)` 到 15m；
- `long dual aligned`：15m bullish 且 1h bullish；
- `short dual aligned`：15m bearish 且 1h bearish。

### 最小回测切口
- 资产：BTC/ETH/SOL perp
- 周期：15m（信号）+ 1h（上下文）
- 样本：近 120 天
- 执行：`signal 当根及之前数据 + next-bar open + no-overlap`
- 成本：先 6/10/15 bps per side

### 先看哪 2 个指标
1. `post-cost expectancy`（long 与 short 分开看）
2. `false-follow / re-entry rate`（入场后 4~8 bar 内是否回到破位线反侧）

### 三条线的落地建议
- breakout-short：先测“`dual bearish` 只做 short-veto/size-down”，不要做 admission。  
- Fib retest_hold：把 `dual bullish` 作为 long-side 放行上下文，比较 `baseline vs context-gated`。  
- EMA/PSAR：只加 context/sizing，不改原始触发，防止把角色混成新主信号。

## 6. 风险与保留意见
- 这轮是 **repo 规则 + 公开数据代理快检**，不是完整策略级回测；
- 事件级结果说明“方向与角色边界”，不等于可直接实盘；
- 120 天窗口可能有阶段偏置，下一步必须补 rolling 与成本分层；
- 当前结论应理解为：**“不要 shared default 化”**，不是“结构一致性完全无用”。

## 7. 来源
1. **TheVision333. (2026). _trading-bot_. GitHub repository.**
   - Authors: GitHub user `TheVision333`
   - Year: 2026
   - Title: Crypto trading bot with breakout and retest strategies
   - Venue: GitHub
   - DOI: `N/A`
   - Readable URL: `https://github.com/TheVision333/trading-bot`
   - Repo URL: `https://github.com/TheVision333/trading-bot`
   - Key files:
     - `https://github.com/TheVision333/trading-bot/blob/main/strategy/market_structure.py`
     - `https://github.com/TheVision333/trading-bot/blob/main/strategy/mtf.py`
     - `https://github.com/TheVision333/trading-bot/blob/main/strategy/retest_signals.py`

2. **Binance. USDⓈ-M Futures Market Data REST API: Kline/Candlestick Data.**
   - Authors/Org: Binance
   - Year: live docs
   - Venue: Official API docs
   - DOI: `N/A`
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`
   - Data URL example: `https://fapi.binance.com/fapi/v1/klines?symbol=BTCUSDT&interval=15m&limit=1500`
   - 公开性：公开可得
   - 更新频率：每根 K 线更新（5m/15m/1h）
   - 最小可复现实验口径：BTC/ETH/SOL perp，15m 信号 + 1h 上下文

---
快检文件：
- `reports/artifacts/literature/confirmed_structure_alignment_pool_summary_2026-03-20.csv`
- `reports/artifacts/literature/confirmed_structure_alignment_asset_direction_summary_2026-03-20.csv`
- `reports/artifacts/literature/confirmed_structure_alignment_event_examples_2026-03-20.csv`
- `reports/artifacts/literature/confirmed_structure_alignment_metadata_2026-03-20.json`
