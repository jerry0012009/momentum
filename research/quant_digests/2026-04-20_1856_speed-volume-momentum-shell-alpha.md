# 别把这份涨速策略只读成“行情扫描器”：对 short-cycle crypto desk，更该先拆的是「价格涨速 + 成交量放大」这条 short-term strength continuation raw alpha
- 时间：2026-04-20 18:56 UTC
- 类型：GitHub
- 主题类型：raw alpha
- 基础 alpha：短窗价格加速后，强势币种更容易继续跑
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：trend / momentum / volume / volatility / regime / execution / risk
- 证据类型：工程经验

## 1. 这次看了什么
看了 `yeshunyi/crypto-momentum-strategy`：一个 2025 维护痕迹仍然很新的加密货币涨速策略仓，核心是按涨速、成交量、RSI、ATR 和市场波动状态，去挑短期强势币并做分段入场。

## 2. 核心结论
- **一句话核心结论**：这套东西的 base alpha 很清楚，就是“短窗涨得快、量也跟上”的币，下一小段往往还会继续强。
- 仓库不只是信号器，代码层已经把 `signal -> risk -> order -> performance` 串起来，算是一个完整策略壳。
- 但我做的 5m portability probe 显示：**强度最高的一档并不最好**，`strongest_only` 在 `3/6/12` bars 上分别约 `-7.21 / -7.03 / -11.89 bps`，反而是 `mid-vol` 桶更像样。
- `mid-vol` 只占 `23` 个事件，但 `3/6/12` bars 平均约 `+63.83 / +130.55 / +160.69 bps gross`；这更像“有 pocket，但很窄”，不是可无脑放大的普适趋势机。

## 3. 为什么和当前项目有关
它和 `momentum` 主线直接对口：这是一个标准的 **trend/momentum raw alpha**，而且把 volume confirmation、ATR regime、RSI veto、分段入场、止盈止损都摆在同一壳里，适合拿来拆成可复用组件。

## 3.5 策略拆解（必填）
- 方向属性：顺势 / 横截面长仓
- 基础 alpha：短窗涨速 + 成交量扩张
- regime：BTC ATR 桶（高/中/低波动）
- filter / veto：RSI<75、黑名单、板块/热门币筛选
- risk / sizing / execution overlay：分段入场、ATR 目标、止损/移动止损、单笔/总风险控制

## 4. 可复刻的最小实验
- 研究假设：涨速信号本身是对的，但要先过“中波动”门，太猛的那一档可能已经追高。
- 可计算定义：`mom_pct >= threshold_pct` 且 `vol_ratio >= 1.5` 且 `RSI14 < 75`，threshold 随 BTC ATR 桶变化（`low/mid/high = 1.5/2.0/3.0%`）。
- 最小切口：Binance USDⓈ-M 5m，10 个 liquid majors，2026-01~03。
- 先看 2 个指标：`avg bps` 和 `win rate`，再看 strongest-only 是否比 mid-vol 桶更差。

## 5. 风险与保留意见
- 这不是“已经证明能赚钱”的结论；它更像一个 **pocket 识别器**。
- 目前 `mid-vol` 样本很少，容易被少数大波段拉高均值。
- repo 里提到的 sector ranking / social data 在代码和文档之间未必完全一致，别把它们当成已验证 alpha 本体。

## 6. 来源
- yeshunyi. (2025). *crypto-momentum-strategy*. GitHub.
- Repo URL: <https://github.com/yeshunyi/crypto-momentum-strategy>
- Readme / code audit: `README.md`, `momentum_strategy.py`, `signal_generator.py`, `market_analyzer.py`, `risk_manager.py`, `config.yaml`
