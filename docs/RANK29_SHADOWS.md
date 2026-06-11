# RANK29_SHADOWS

目的：把 Rank29 相关页面里最容易混淆的三条线讲清楚：
- baseline
- regime gate shadow
- orderbook shadow execution

结论先说：

> 它们都属于 Rank29 的“影子/验证层”，但**不是同一个东西**，也**不回答同一个问题**。

---

## 1. baseline / clean replication / manual narrow paper

这是 Rank29 的主线。

### 它回答什么
- 这套 `trendline_breakout_navigator` breakout 规则，在当前 paper 口径下是否值得继续跟踪？
- 最近 append-only 的 paper 表现怎么样？
- 当前还有没有 open paper positions？

### 它的核心设定
- 市场：`Binance spot 15m`
- 资产：当前 narrow paper 主线是 `BTC / ETH / SOL`
- 信号：`breakout_align_ge2 + no_overlap_guard`
- 成本：固定成本口径（当前 narrow paper 主要看 `6bps/side`）
- 不包含：订单簿逐档滑点、spread/impact、拒单

### 相关页面
- 主报告：`reports/site/factors/scout_rank29_trendline_breakout_navigator_15m/report.html`
- narrow paper 状态：`reports/site/factors/manual_narrow_paper_lanes/report.html`

---

## 2. regime gate shadow

这是加在 baseline 上面的**风险覆盖层**。

### 它回答什么
- 如果识别到坏环境（当前是 `low_trend_high_noise`），并把仓位降到 `25%`，
  同一批 paper trades 会不会更稳？
- 它更像“减伤补丁”，不是新的独立策略。

### 它的核心设定
- 仍然是：`Binance spot 15m`
- 仍然是：`BTC / ETH / SOL`
- 仍然是：和 baseline **同一批交易**
- 差别只在于：
  - 若命中 `low_trend_high_noise`
  - 该笔按 `25%` 曝险记账
- 不包含：L2 orderbook 深度、真实盘口冲击、拒单逻辑

### 它不回答什么
- 它不回答“未来 tiny-live 执行会不会被滑点打穿”。
- 它不回答“perp 盘口能不能承受这套打法”。

### 相关页面
- gate 回测：`reports/site/factors/rank29_regime_gate_backtest/report.html`
- narrow paper 状态页中的 baseline vs gate shadow 区块：
  `reports/site/factors/manual_narrow_paper_lanes/report.html`

---

## 3. orderbook shadow execution

这是另一条完全不同维度的 shadow：它是**执行验证层**。

### 它回答什么
- 如果未来往 tiny-live 方向推进，真实盘口的
  - `spread_bps`
  - `impact_bps`
  - `rejections`
  会不会把 edge 吃掉？

### 它的核心设定
- 市场：`Binance USDT-M perp`
- 数据：L2 depth / orderbook
- 关注：VWAP、滑点、盘口冲击、拒单、perp fee
- 它不是在 baseline 同一批 spot paper trades 上做“降仓记账”，而是在更接近执行层的环境里做 shadow fill 模拟。

### 它不回答什么
- 它不回答坏环境该不该降仓。
- 它不负责验证 `low_trend_high_noise_w25` 这个 regime overlay 是否有效。

### 相关页面
- `reports/site/factors/rank29_orderbook_shadow/report.html`

---

## 4. 为什么会让人误以为“有两个一样的 Rank29 shadow”

因为它们都带着 `Rank29 shadow` 这个名字，但实际属于两个不同维度：

- regime shadow：看 **风险过滤 / 降仓**
- execution shadow：看 **盘口执行 / 滑点 / 拒单**

所以当前最准确的理解是：

> 不是重复建设，
> 而是**命名和展示层太像，容易让人误读成重复项**。

---

## 5. 当前建议的读法

### 如果你关心：
#### “最近坏环境里，降仓有没有帮助？”
看：
- `rank29_regime_gate_backtest`
- `manual_narrow_paper_lanes` 里的 baseline vs gate shadow

### 如果你关心：
#### “以后真钱执行，盘口会不会把利润吃掉？”
看：
- `rank29_orderbook_shadow`

### 如果你关心：
#### “Rank29 本体现在到底如何？”
先看：
- `scout_rank29_trendline_breakout_navigator_15m`
再看：
- `manual_narrow_paper_lanes`

---

## 6. 当前不做什么

当前先**不把它们强行合并成一个 runner / 一个报表**。

原因：
- 输入数据不同（spot vs perp）
- 回答的问题不同（regime vs execution）
- 标的池也不完全一致

所以现阶段最合理的做法是：

> **先把逻辑和边界写清楚，暂不硬合并。**

这也是当前页面与文档采用的口径。
