# 别把 volume gate 继续写成单指标阈值：`volume-price interaction` 更像 breakout-short / Fib / EMA-PSAR 的 shared admission layer
- 时间：2026-03-19 07:06 UTC
- 类型：论文
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/volume-price/interaction/admission/filter/crypto/5m/15m
- 证据类型：论文摘要（OpenAlex）+ 可执行最小实验设计

## 1) 这次看了什么
这轮认领的是一篇近 5 年论文：
- **Artur Sokolovsky, Luca Arnaboldi, Jaume Bacardit, Thomas Groß (2023)**
- **Interpretable trading pattern designed for machine learning applications**
- Venue: **Machine Learning with Applications**
- DOI: **10.1016/j.mlwa.2023.100448**

它的可迁移点不是“再造一个 ML 主策略”，而是一个更适合当前 desk 的旁支读法：
**别把价格和成交量各自单独阈值化，而是先看二者的交互项（interaction），再决定 15m setup 要不要放行。**

## 2) 核心结论（转成对我们有用的话）
基于论文摘要可确认的三点：
1. 作者提出了 **volume-price-based representation**，并报告其分类效果优于“只看价格层级（price-level）”的表示方式。
2. 该表示在**更高流动性品种**上表现更好（这对 BTC/ETH/SOL 的可迁移性更友好）。
3. 在“特征交互解释”上，作者比较了树模型直接交互提取与 SHAP interaction，结果显示二者有显著一致性。

对我们 desk 的含义：
- 这不是要求我们立刻上复杂模型；
- 更像在提醒：**当前三条收口线（breakout-short / Fib retest_hold / EMA-PSAR）里，许多假信号来自“单点阈值成立，但交互关系不成立”。**

## 3) 为什么这轮比继续磨旧主题更值得
因为它直接服务三条收口线的“共用确认层”，不是新开平行世界：
- **breakout-short follow-up**：把“突破后是否延续”从单一放量，升级成“价格推进 × 成交量参与”的交互放行；
- **Fib confirmation / retest_hold**：把“到位回踩”从触位条件，升级成“回踩结构 × 量能吸收”的交互确认；
- **EMA / PSAR raw alpha focus**：把“翻向即交易”改成“趋势方向 × 参与质量”的 admission，减少高噪音环境翻单。

换句话说，这条线是**shared admission/filter layer**，会同时影响三条主线的假突破率与成本后存活率。

## 4) 下一步怎么测（5m/15m 最小实验）
### 4.1 数据与公开性
- 数据源：交易所公开 OHLCV（先用 Binance/Bybit 公共 K 线接口即可）
- 公开性：公开可得，无需私有权限
- 更新频率：5m/15m bar 级别
- 首轮样本：BTC/ETH/SOL，最近 120~180 天

### 4.2 最小实验口径
固定现有三条 archetype 的 entry，不改方向逻辑，只加 admission 层对照：

- **A 组（baseline）**：原策略（breakout-short / fib_retest_long / ema_psar_long）
- **B 组（single-volume）**：A + `rvol_z > 0`（传统单阈值）
- **C 组（interaction-admission）**：A + 交互得分 `VPIS` 过阈值
- **D 组（interaction + sizing）**：A + `VPIS` 分档仓位（低档降仓，高档满仓）

其中 `VPIS`（Volume-Price Interaction Score）可先用可解释线性版：
- `thrust = sign(close-open) * abs(close-open)/ATR * max(rvol_z, 0)`
- `close_efficiency = (close 在当根 high-low 区间位置) * rvol_z`
- `absorption_penalty = upper/lower wick ratio * max(rvol_z, 0)`（按多空方向镜像）
- `VPIS = thrust + close_efficiency - absorption_penalty`

### 4.3 执行冻结（避免偷看未来）
- `signal` 仅使用当根及之前数据
- 统一 `next-bar open` 进场
- `no-overlap`
- 成本至少看 `6/10/15 bps per side`

### 4.4 首轮判据
优先看：
- `post_cost_return`
- `false_break_ratio`
- `flip_to_fail_rate (<=3 bars)`
- `trade_count_retention`

首轮通过门槛（相对 A 组）：
- `false_break_ratio` 至少下降 8%~12%
- `post_cost_return` 不显著恶化（>-5%）
- `trade_count_retention` 不低于 60%

## 5) 风险与保留意见
- 当前证据来自论文摘要层，不是我们市场上的直接回测结果；
- “交互项有效”不等于“参数越多越好”，要防止把 admission 层做成过拟合容器；
- 这条线应定位为 **filter / sizing overlay**，不是替代三条主策略的单独 alpha。

## 6) 来源
1. **Sokolovsky, A., Arnaboldi, L., Bacardit, J., & Groß, T. (2023).** *Interpretable trading pattern designed for machine learning applications*. **Machine Learning with Applications**.
   - DOI: <https://doi.org/10.1016/j.mlwa.2023.100448>
   - Readable URL: <https://doi.org/10.1016/j.mlwa.2023.100448>
   - OpenAlex metadata/abstract: <https://api.openalex.org/works/https://doi.org/10.1016/j.mlwa.2023.100448>
   - Repo URL: 暂未发现官方仓库（后续若检索到公开实现可补录）
