# 别把 liquidity 研究只当 market-quality 教科书：对 short-cycle desk，更该先补的是「CS/AR spread proxy × Amihud level × realized-vol trigger」这层共享 liquidity gate / sizing overlay

- 时间：2026-04-01 14:26 UTC
- 类型：quant_digest
- 主题标签：overlay/filter/liquidity/cost-model/spread-proxy/corwin-schultz/abdi-ranaldo/amihud/kyle-obizhaeva/realized-volatility/market-quality/shared-component/binance/bybit/okx/btc/eth/1m/3m/5m/15m/paper/public-data/cost/execution
- 证据类型：2021 *Journal of Banking & Finance* 开放获取 Highlights/Abstract + OpenAlex 元数据；2024 *Financial Innovation* 开放获取摘要/元数据

- 主题类型：overlay
- 基础 alpha：**不是独立 raw alpha；它服务的 base alpha 是高换手短周期策略，尤其是 `order-book / taker-flow directional`、`breakout / continuation`、`pairs / spread MR` 这几类最容易被成本和流动性状态吞掉的 raw alpha。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是，但角色是 **gate / sizing / cost overlay**，不是方向信号本体。

## 1. 先说结论
如果现在还继续只补 raw alpha 叶子，而不补一层**便宜、稳定、公开数据可得**的 liquidity/cost gate，desk 很容易重复犯同一个错：

**paper 上有 edge，实盘一上高换手就被 spread、冲击、挤仓时段和错误 venue 选择吃掉。**

这轮最值得 intake 的，不是“又一个方向因子”，而是：

1. 用 **Corwin-Schultz (CS)** / **Abdi-Ranaldo (AR)** 这类只靠 OHLC 就能算的 spread proxy，去跟踪**流动性变化**；
2. 用 **Amihud** / **Kyle-Obizhaeva (KO)** 这类 price-impact proxy，去跟踪**流动性水平**；
3. 再用 **realized volatility** 做上游 trigger，因为 2024 支持材料表明，对 BTC liquidity 来说，**已实现波动率是最稳的解释变量**。

翻成人话：
**先别急着问“方向对不对”，先问“这根 bar 值不值得交易、该不该降仓、是不是该换 maker-ish 执行”。**

## 2. 为什么这轮值得写，而不是继续补一条 raw alpha
当前 desk 已经连续 intake 了不少 raw alpha 候选：directional、pairs、cross-sectional、carry 都在加。
现在更缺的，是一层能同时服务多类 alpha 的**共享成本壳**：

- 对 `OBI / flow continuation`：它决定你是该 aggress，还是等价差回到可交易区；
- 对 `breakout / trend`：它决定高波动真突破时该不该放行，还是先被 spread tax 干掉；
- 对 `pairs / spread MR`：它决定看起来很美的 z-score 回归，是否只是低流动性假信号。

所以这轮虽然不是 raw alpha，但和当前短周期 desk 的关系非常直接：
**它不是解释世界，而是给已有/新 raw alpha 加一层“别在最贵的时候交易”的保护层。**

## 3. 这次看了什么
### 3.1 主论文：低频 proxy 能不能替代高频真实 liquidity
- **Authors**：Alexander Brauneis, Roland Mestel, Ryan Riordan, Erik Theissen
- **Year**：2021
- **Title**：*How to measure the liquidity of cryptocurrency markets?*
- **Venue**：*Journal of Banking & Finance*
- **DOI**：<https://doi.org/10.1016/j.jbankfin.2020.106041>
- **Readable URL**：<https://www.sciencedirect.com/science/article/pii/S0378426620303022?via%3Dihub>

当前可稳定拿到的核心信息：
- 论文直接比较了**高频 benchmark liquidity** 与**低频、易计算 proxy** 在 crypto 里的表现；
- 研究对象明确写到 **BTC 和 ETH**；
- Highlights 与 Abstract 都能稳定拿到，足够支撑这轮 digest 的主结论。

### 3.2 supporting paper：liquidity 到底被什么驱动
- **Author**：Walid M. A. Ahmed
- **Year**：2024
- **Title**：*On the robust drivers of cryptocurrency liquidity: the case of Bitcoin*
- **Venue**：*Financial Innovation*
- **DOI**：<https://doi.org/10.1186/s40854-023-00598-9>
- **Readable URL**：<https://doi.org/10.1186/s40854-023-00598-9>

这篇 supporting paper 的价值不在“给新 alpha”，而在告诉我们：
**当你想提前预判 liquidity 变坏时，最该盯的上游变量是什么。**

## 4. 这两篇东西给了 desk 哪 4 个硬点
### 4.1 低频 proxy 不是没用，反而够资格做短周期 gate
2021 JBF 的 abstract 结论非常直接：

- **Corwin-Schultz (2012)** 和 **Abdi-Ranaldo (2017)** 在描述**流动性的时间序列变化**时，优于其他候选；
- 这个结论对**不同观察频率、不同 venue、不同 benchmark、不同币种**都成立；
- 它们在**高 / 低收益、高 / 低波动、高 / 低成交量时期**都表现稳定。

对 desk 的含义是：
如果你现在没有稳定全市场 L2 / tick 数据，**不代表你只能裸跑策略**。用 OHLC + volume 就能先搭一层足够像样的 liquidity state machine。

### 4.2 想看“变化”，优先 CS / AR；想看“绝对水平”，优先 Amihud / KO
这篇 2021 论文还给了一个很重要的拆分：

- **CS / AR 更擅长追踪 liquidity 的变化过程**；
- **Amihud (2002) illiquidity ratio** 和 **Kyle-Obizhaeva (2016)** 更擅长估计**liquidity level**；
- 后两者还更能识别**venue 之间的流动性差异**。

这点很关键，因为 short-cycle desk 经常把“有没有恶化”和“绝对贵不贵”混成一个维度。其实应该拆开：

- `变化维度`：现在是不是突然变差了？
- `水平维度`：这个 venue / 这个币 / 这个时段，本来是不是就贵？

### 4.3 Amihud 很便宜，先上它；CS/AR 做 second opinion
如果只从最小实验成本看，**Amihud** 最适合先落：

- 公式简单：`ILLIQ_t = abs(ret_t) / dollar_volume_t`；
- 公开 K 线 / quote volume 就能先做；
- 很适合先给现有 alpha 做 `cost veto / size scaling`。

但如果只用 Amihud，又会漏掉**spread 自身的状态变化**。所以更合理的 desk 化方案是：

- 用 **CS 或 AR** 盯 spread proxy 的变化；
- 用 **Amihud** 盯 impact/capacity；
- 如果后面有更好的成交级数据，再补 KO。

### 4.4 2024 支持材料：最稳的上游 trigger 是 realized volatility
2024 *Financial Innovation* 的 abstract 也很有用：

- 研究用的是 **BTC/USD 的 60-min 高频数据**；
- 在 Leamer 版 EBA 下，**realized volatility 是解释 Bitcoin liquidity 的唯一稳健变量**；
- 在 Sala-i-Martin 版 EBA 下，除 realized volatility 外，还多了 **negative returns、trading volume、hash rate、Google search volume** 这 4 个稳健解释变量。

翻成人话：
如果你只允许先上一个最便宜、最稳的 liquidity deterioration trigger，**先上 realized vol，不要先上“花哨情绪解释”。**

## 5. 这东西怎么映射到 1m / 3m / 5m / 15m
### 5.1 它不是方向信号，而是 admission / sizing / execution veto
这轮要非常诚实：

- 它**不是**独立 raw alpha；
- 它更像一个共享的 `tradeability layer`；
- 所以最适合的角色是：
  - `15m / 5m`：主 gate / size scaler
  - `3m / 1m`：execution veto / maker-vs-taker switch

### 5.2 最小可复现实验口径
**公开数据源**：
- Binance / Bybit / OKX 公共 OHLCV / quote volume / 公开 trade 或 mark price 数据
- 数据公开性：公开可得
- 更新频率：`1m` 或更高，再聚合到 `3m/5m/15m`

**第一版指标建议**：
1. `amihud_5m = abs(ret_5m) / quote_volume_5m`
2. `amihud_15m = abs(ret_15m) / quote_volume_15m`
3. `spread_proxy_5m = CS_or_AR_from_OHLC_5m`
4. `rv_15m = realized_vol_15m_or_1h`
5. `liq_state = z(amihud) + z(spread_proxy) + z(rv)`

其中：
- `CS_or_AR` 先直接复用论文对应 estimator 的标准实现，不建议第一刀自己手写猜公式；
- `rv` 先用最朴素的 rolling realized vol 就够；
- `liq_state` 不要一开始搞复杂 ML，先做分桶和简单阈值。

## 6. 对当前 desk 最有价值的不是“测 proxy 本身”，而是做 transfer
这轮最该先跑的，不是孤零零地看 proxy 跟 spread 的相关系数，而是做**对已有 alpha 的迁移实验**。

### 实验 A：给 OBI / flow continuation 加 liquidity veto
**服务 alpha**：`order-book imbalance / taker-flow continuation`

- 原信号照旧给方向；
- 若 `liq_state` 进入最差分位（比如 top decile illiquid），则：
  - 禁止 taker 进场；
  - 或把 size 降到 25% / 50%；
  - 或改成 maker-ish 参与。

要回答的问题：
**alpha 的毛 edge 会不会小降，但 after-cost Sharpe / hit-rate / avg trade pnl 反而上升？**

### 实验 B：给 breakout / continuation 做“高波动 ≠ 可交易”分流
**服务 alpha**：`breakout / trend / continuation`

- 常见错误是把高波动直接当“更值得追”；
- 这里改成二阶段判断：
  1. breakout 条件触发；
  2. 只有当 `rv` 上升但 `spread_proxy` / `amihud` 没同步恶化到阈值外，才放行。

要回答的问题：
**能不能把“方向对但成本太贵”的假阳性砍掉？**

### 实验 C：pairs / spread MR 上的 venue-aware 降仓
**服务 alpha**：`pairs / stat-arb / spread MR`

- 如果 z-score 到位，但一条腿所在 venue 的 `Amihud / KO` 明显更差；
- 或者 `CS/AR` 提示 spread proxy 正在恶化；
- 那就不是不做，而是：
  - 降仓；
  - 拉宽 entry band；
  - 或强制 maker-only first leg。

要回答的问题：
**MR 的表面回归优势，是否只是被 illiquid leg 的 hidden cost 假放大？**

## 7. 一个够用的 first-pass 策略骨架
### Entry gate
对任意已有 raw alpha `alpha_score_t`：

1. 先算 `alpha_score_t`；
2. 再算 `amihud_t`、`spread_proxy_t`、`rv_t`；
3. 得到 `liq_state_t`；
4. 只有当 `liq_state_t < gate_threshold` 才允许正常进场；
5. 若 `liq_state_t` 落在灰区，只允许半仓或 maker-only；
6. 若 `liq_state_t` 极差，则 veto。

### Sizing
- `normal`：底层 alpha size × 1.0
- `watch`：× 0.5
- `bad`：× 0 或只挂 maker 小仓

### Cost/Risk
至少拆三档：
- `maker-ish`
- `mixed`
- `taker-heavy`

如果一个 alpha 只有在 `liq_state` 最差时还必须用 `taker-heavy` 才能抓到信号，那它很可能不是真的 edge，只是 paper edge。

## 8. 这轮最该记住的 3 个数字 / 事实
1. **2021 JBF**：BTC/ETH 上，**CS / AR 最适合追时间序列变化**；**Amihud / KO 最适合看 liquidity level 与 venue 差异**。
2. **2024 Financial Innovation**：基于 **BTC/USD 60-min 高频数据**，**realized volatility 是最稳的 liquidity 解释变量**。
3. 这意味着 short-cycle desk 完全可以先用**公开 OHLCV + quote volume**搭一层低成本 liquidity gate，而不用等完整 L2 基础设施才开始做成本控制。

## 9. 局限与别误读的地方
1. **这不是 raw alpha 本体。** 不要把它伪装成“单独赚钱的方向信号”。
2. **2021 论文的 benchmark 是高频 liquidity，不等于你的实际 fill。** 所以 transfer 时一定要看 after-cost，不要只看 proxy 相关性。
3. **2024 supporting paper 只看 Bitcoin。** 所以 realized-vol trigger 迁移到 ALT 时，要单独做稳健性。
4. **不同 venue 的 quote volume 口径可能不完全一致。** first-pass 先做单 venue 内实验，再做 cross-venue。

## 10. 下一步怎么测
### 本轮建议只做 1 个最小实验
**先拿一条已有高换手 alpha，给它外挂这层 gate，再做 ablation。**

优先顺序：
1. `OBI / taker-flow directional`
2. `breakout / continuation`
3. `pairs / spread MR`

### 最小 ablation ladder
1. 原始 alpha（无 gate）
2. + `Amihud`
3. + `Amihud + CS/AR`
4. + `Amihud + CS/AR + realized-vol trigger`

### 只看这 5 个输出
- after-cost Sharpe
- avg trade pnl
- fill-adjusted hit-rate
- turnover change
- veto 后被砍掉交易的 pnl 分布

如果第 4 档明显优于第 1 档，这层 overlay 就值得正式进入实盘组件池；如果只改善 paper pnl、不改善 after-cost，就说明它只是漂亮解释，不是好 gate。

## 11. 一句话收尾
这轮不是再找一条“看起来很聪明”的方向因子，而是补一层**低数据门槛、可跨策略复用、直接决定 edge 能不能活过成本**的 liquidity overlay。对现在这个 short-cycle desk，它比再多收一条相似 raw alpha 更值钱。