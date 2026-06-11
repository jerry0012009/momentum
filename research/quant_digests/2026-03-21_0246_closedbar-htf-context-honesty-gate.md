# 别把未收盘 HTF 结构偷渡进 15m 确认：closed-bar `merge_asof(backward)` 才是 breakout-short / Fib / EMA-PSAR 的 honest context gate
- 时间：2026-03-21 02:46 UTC
- 类型：GitHub 仓库 + 官方文档
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/htf/merge_asof/closed-bar/no-lookahead/context/filter/repo/docs/crypto/15m
- 证据类型：工程规则证据（源码 + 官方 API/文档可复核）

## 1. 这次看了什么
看了 `TheVision333/trading-bot` 里的 `strategy/mtf.py` 与 Pandas 官方 `merge_asof` 文档。最值得偷的不是某条均线，而是它把高周期上下文写成一个**严格 closed-bar only** 的合并规则：LTF 在时点 `T` 只能拿到 **已收盘** 的 HTF 状态，不能偷看正在形成中的 4H / 1D bar。

## 2. 核心结论
- **一句话核心结论**：15m 的 HTF 确认层，先要过“已收盘高周期”这道 honesty gate；否则很多看起来更稳的确认，其实只是未来信息泄漏。
- **一句话证明方式**：主仓库明确用 `pd.merge_asof(..., direction='backward')`；Pandas 官方文档也明确写着，`backward` 只会选取 `right_key <= left_key` 的最后一行，也就是**只拿过去或当前已知值**。
- 这条规则的实际量级不小：如果 15m 直接读取“当前未收盘 HTF bar”，最大潜在前视泄漏可达：
  - `15m -> 1h`：**45 分钟 = 3 根 15m bar**
  - `15m -> 4h`：**225 分钟 = 15 根 15m bar**
  - `15m -> 1d`：**1425 分钟 = 95 根 15m bar**
- 仓库注释给了一个很好的口径示例：**`14:00` 的 1H 信号，只能拿 `12:00` 已收盘 4H bar 的结构，不能拿 `16:00` 那根还没收完的 4H bar。**

## 3. 为什么和当前项目有关
这轮虽然不是再加一个新 alpha，但它比继续堆一个新过滤器更值：**先把三条收口线的 HTF 上下文做干净，否则后面的胜率/回撤改善可能只是“偷看未来”。**

- `V3 final-verdict / breakout-short follow-up`：若 15m breakout-short 用了“当前 4H 已转弱/转强”当 follow-up gate，但那根 4H 其实还没收盘，final verdict 容易被虚高。
- `Fibonacci confirmation / retest_hold`：Fib 回踩特别依赖 1H/4H 趋势背景；如果 HTF 对齐口径不诚实，`retest_hold` 的确认强度会被高估。
- `EMA / PSAR raw alpha focus`：在继续讨论 EMA/PSAR 是主触发还是 overlay 之前，先确认 HTF trend filter 没有 lookahead，比再调参数更要紧。

## 4. 可复刻的最小实验
- **研究假设**：当前任何依赖 1H/4H/1D context 的 15m setup，只要把“当前未收盘 HTF 值”改成“closed-bar only”，绩效会有一部分回落；若几乎不回落，才说明这层确认是诚实的。
- **可计算定义**：
  1. `Honest`：HTF 特征先按 HTF close timestamp 计算，再用 `merge_asof(direction="backward")` 合并到 15m；
  2. `Naive`：把当前 HTF bar 直接 `resample/ffill` 到 15m，允许未收盘 bar 的值提前进入。
- **最小回测切口**：`BTC/ETH/SOL` perpetual，`15m` 主信号；HTF 先测 `1h/4h` 两层；时间先取 `2023-01-01` 至今；成本先固定 `6/10/15 bps per side`。
- **先看 4 个指标**：
  1. `post_cost_expectancy`
  2. `failure_rate`
  3. `trade_count_retention`
  4. `HTF gate flip rate`（多少笔在 naive 通过、honest 不通过）
- **优先顺序**：先在现有 `breakout-short`、`fib_retest_hold`、`ema_psar` 三条线上各做一次 `naive vs honest` A/B；如果某条线对口径极敏感，就先暂停加新过滤器，回头重审证据。

## 5. 风险与保留意见
- 这不是新 alpha，而是**研究诚实性修复**；它可能让回测更难看，但更可信。
- 不同数据源对 bar timestamp 的标注（开盘时刻 vs 收盘时刻）可能不同，若不统一，`merge_asof` 也会错位。
- closed-bar 规则会牺牲一点“反应速度”；但这属于真实交易限制，不该在回测里被偷掉。

## 6. 来源
- TheVision333. (2026). **trading-bot**. GitHub Repository.  
  - Venue: GitHub  
  - DOI: `N/A`  
  - Readable URL: `https://github.com/TheVision333/trading-bot`  
  - Repo URL: `https://github.com/TheVision333/trading-bot`  
  - Key files:  
    - `https://raw.githubusercontent.com/TheVision333/trading-bot/main/strategy/mtf.py`  
    - `https://raw.githubusercontent.com/TheVision333/trading-bot/main/config.py`
- pandas development team. (2025-2026). **pandas.merge_asof — pandas documentation**. Official Documentation.  
  - Venue: pandas docs  
  - DOI: `N/A`  
  - Readable URL: `https://pandas.pydata.org/docs/reference/api/pandas.merge_asof.html`
