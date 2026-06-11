# 别把这份 2026 Hyperliquid lead-lag repo 只读成 network-science demo：对 short-cycle desk，更该先测的是「Lévy rowscore leader move × follower catch-up basket」
- 时间：2026-04-07 15:49 UTC
- 类型：GitHub repo source audit（`README.md` + `main.py` + `portfolio.py` + `trading_signal.py` + `bot.py`）
- 主题类型：raw alpha
- 基础 alpha：先找出在最近窗口里“经常先动”的 leader 币，再用 leader 最新一根收益的方向，去做 follower 币的滞后跟随篮子；赚的是 **leader 先动、follower 后补** 这段短时 lead-lag 传导。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha / cross-sectional / lead-lag / relative-value / follower-catch-up / network-ranking / Hyperliquid / 15m / 5m / 1h / repo / cost / risk
- 证据类型：工程经验

## 1. 这次看了什么
这次主看 **mateofrqt / `Crypto-LeadLag-Strategy`**。它不是普通“相关性排序”脚本，而是先用 **Lévy area signatures** 估计币对之间的方向性先后关系，再把每个币在有向网络里的行均值分数当成 leader / follower 排名，最后把这套排名翻译成可交易的 long-short 篮子与 live bot。对我们 desk 来说，它最像一条 **可快速最小复现的 cross-sectional lead-lag raw alpha**，而不是单纯研究图论结构。

## 2. 核心结论
- 这条东西的 **base alpha 很清楚**：不是赌 breakout，也不是赌均值回复，而是赌 **“先动币”对“后动币”的短时传导**。leader 已经朝某个方向明显动了以后，followers 往往会补这一步。
- 它最有用的工程化翻译是：先在滚动窗口上算 lead-lag matrix，再把 **row-score 高的币当 leaders、低的币当 followers**；下一根如果 leaders 平均收益为正，就做多 follower 篮子；为负，就做空 follower 篮子。
- 仓位层不是一句“等权”带过。源码里 follower 权重直接按 **对 leaders 的绝对 lead-lag 强度** 来分配，bot 侧又加了 `risk_per_trade`、`target_volatility`、`max_leverage`、`rebalance_threshold`、`min_leader_move` 这些约束，说明作者想把它往真实组合壳推进。
- 但当前 repo 还没到 production：`main.py` 示例回测只用了很短样本，默认还把 `use_risk_management=False`；更关键的是，**回测里几乎没认真处理手续费、滑点、冲击成本**，所以它现在更像“信号骨架已清楚、成本层还没补完”的 raw alpha 候选。
- 对 short-cycle desk 真正值钱的地方不是照搬 Lévy / Hermitian 这些术语，而是学到一个可迁移模板：**先做 leader ranking，再做 follower basket catch-up**。这比单币追涨更接近可组合、可做多空双开的 alpha 组件。

## 3. 为什么和当前项目有关
它直接补的是我们素材池里相对还不够多的一层：**cross-sectional lead-lag raw alpha**。最近我们已经积累了不少 pairs、carry、maker、single-asset continuation，但“谁先动、谁后补”这种 **横截面传导** 仍然值得持续补货，尤其适合 `5m / 15m` 甚至 `3m`。

一句话核心结论：**这份 repo 最值得拿来测的，不是复杂数学名词，而是“leader 先涨先跌后，follower 篮子会不会在下一两个 bar 补动作”这条可直接下单的横截面 alpha。**  
一句话证明方式：**作者把 lead-lag 先后关系写成 rolling matrix、ranking、篮子回测和 live bot 参数，而不是只停留在相关性图或论文图表。**

## 3.5 策略拆解（必填）
- 方向属性：横截面 / 相对价值 / lead-lag continuation
- 基础 alpha：leader 最新收益方向对 follower 下一根或下几根收益有预测力
- regime：流动性较好、币种间联动增强、市场有共同驱动但传导不同步的时段
- filter / veto：`min_leader_move`、leader/follower 分位筛选、cluster 内交易、rebalance threshold、风险预算开关
- risk / sizing / execution overlay：follower 篮子按 lead-lag 强度加权；组合 notional 受 `risk_per_trade`、`target_volatility`、`max_leverage`、`max_drawdown` 约束；实盘侧通过定时轮询和最小调仓阈值降低换手

## 4. 可复刻的最小实验
- 研究假设：在 liquid perp universe 中，若过去 `N` 根里 A/B/C 经常领先 D/E/F，且本根 leaders 的均值收益绝对值足够大，则 followers 在下一根仍会同向补动作。
- 一个可计算定义：
  1. 用 `30` 根滚动窗口在 `1h` 先复刻 repo 口径，算 lead-lag score matrix；
  2. 每根按 row-score 排名前 `10%` 为 leaders、后 `10%` 为 followers；
  3. 若 `leaders_ret_t > +0.4%`，做多 follower basket；若 `< -0.4%`，做空 follower basket；
  4. 先持有 `1` 根，再测 `2` 根；权重先用等权，再测 `abs(score)` 加权。
- 最小回测切口：
  - 资产：Hyperliquid 或 Binance perpetual 的 top `20~30` liquid names
  - 周期：先 `15m` 稳健复刻，再降到 `5m` 看 alpha 是否更强但更脆
  - 样本：至少 `90~180` 天，不要沿用 repo 那种极短样本
- 最该先看哪 1~2 个指标：**成本前后 next-bar / next-2-bar alpha 是否仍为正**、**调仓换手后净 edge 是否被费用吃掉**。

## 5. 风险与保留意见
- 当前 repo 最大问题不是信号，而是 **证据强度不够**：示例样本偏短，且成本处理明显不充分，容易把换手型 alpha 看得太漂亮。
- lead-lag 策略最怕两件事：一是 **共同因子同时反转**，二是 **followers 其实已经同步、只是假象上看起来滞后**。所以一定要补市场 beta / sector beta 去残差化对照。
- 如果下到 `5m / 3m`，真正的敌人不是统计显著性，而是 **交易成本、盘口深度、调仓摩擦**；这条线很可能从 raw alpha 逐步变成“低频一点能活，高频太碎会死”的策略。
- 另外，repo 里 live bot 有风险管理接口，但仓位、成交、费用、滑点的 production 闭环还不完整，所以目前更适合当 **research shell**，不适合直接当实盘成品。

## 6. 来源
1. **mateofrqt.** `Crypto-LeadLag-Strategy`.
   - Repo URL: `https://github.com/mateofrqt/Crypto-LeadLag-Strategy`
   - Repo metadata: GitHub repo，创建于 `2026-02-23`，最近一次可见更新约为 `2026-03-23`
2. **README / overview**
   - Readable URL: `https://github.com/mateofrqt/Crypto-LeadLag-Strategy/blob/main/README.md`
3. **Backtest entrypoint** `main.py`
   - Readable URL: `https://github.com/mateofrqt/Crypto-LeadLag-Strategy/blob/main/main.py`
4. **Portfolio construction / backtest logic** `portfolio.py`
   - Readable URL: `https://github.com/mateofrqt/Crypto-LeadLag-Strategy/blob/main/portfolio.py`
5. **Lead-lag matrix construction** `trading_signal.py`
   - Readable URL: `https://github.com/mateofrqt/Crypto-LeadLag-Strategy/blob/main/trading_signal.py`
6. **Live execution shell** `bot.py`
   - Readable URL: `https://github.com/mateofrqt/Crypto-LeadLag-Strategy/blob/main/bot.py`
