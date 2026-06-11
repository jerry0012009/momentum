# 别把这份 2026 新论文仓只读成 drawdown overlay：对 short-cycle desk，更该先测的是「XSM winner-minus-loser × BTC-vol Goldilocks / corr / dispersion scaling」这条完整 raw alpha

- 时间：2026-04-04 05:27 UTC
- 类型：quant_digest
- 主题标签：raw-alpha/cross-sectional/momentum/relative-value/winner-minus-loser/regime-aware/btc-vol/goldilocks/correlation/dispersion/exposure-scaling/crypto/15m/5m/3m/1m/repo/paper/public-data/cost/risk
- 证据类型：2026 GitHub 新 repo source audit（`README.md` + `macro_state_test.py` + `coordination_overlay_test.py` + `main1.tex`）+ Crossref metadata grounding

- 主题类型：raw alpha
- 基础 alpha：在可交易 crypto 横截面里，**做多近期相对强者、做空近期相对弱者**的 standardized long-short relative momentum；再用 BTC 波动、横截面相关性与 dispersion 状态去做 gross exposure scaling
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1. 这次看了什么
这份今天新出现的 2026 repo，真正值得 desk 先测的，不是“把回撤压低一点”的 overlay 叙事，而是：**先承认 base alpha 就是 cross-sectional winner-minus-loser 动量篮子，再把 BTC-vol / corr / dispersion scaler 当作可部署的 sizing shell**。这比继续补一个单币 breakout 旁支，更能扩充当前 desk 的 relative-value/raw-alpha 素材池。

## 2. 先回答一句：这篇东西的 base alpha 是什么？
先把话说死：
- **base alpha 不是** BTC 波动过滤器；
- **base alpha 不是** drawdown 管理；
- **base alpha 也不是** “市场结构会变” 这种解释层。

它的 alpha 本体很直接：
1. 在 crypto 横截面里，先看每个币最近一段时间的累计收益；
2. 做 cross-sectional 去均值、标准化；
3. **多相对强者、空相对弱者**，形成 standardized long-short basket；
4. 再把 gross exposure 按 BTC realized vol、平均相关性、dispersion 状态缩放。

翻成人话：**这是一条“横截面 relative momentum raw alpha + regime-aware sizing shell”**。如果把 sizing 拿掉，alpha 依然存在；所以它不是纯 filter / overlay 主题。

## 3. 为什么这轮值得写，而不是继续补一个单币形态分支
结合当前项目的 intake 取向，这轮有三个理由值得优先：

1. **它补的是 relative-value / cross-sectional 家族。**
   现在库里单币 trend / mean-reversion / microstructure 已经很厚；继续堆当然没问题，但边际增量在下降。相反，横截面 raw alpha 还值得持续补货。

2. **它给的是完整策略，不只是概念。**
   这个 repo 里不止有题目和结论，还有 `macro_state_test.py`、friction 参数、overlay 公式、paper draft，足够拆成 signal / sizing / risk / cost 四层。

3. **它把“为什么 crypto 横截面动量会突然失灵”说得比很多 plain XSM baseline 更清楚。**
   这点很关键：不是只告诉你“有一条 winner-minus-loser 线”，而是进一步把失效条件落到了可观测的状态变量上。

## 4. 这次看了什么
### 4.1 主来源：repo + paper draft
- **Authors**：Olorato MacDonald Makgolo, Cong Zhang
- **Year**：2026
- **Title**：*Regime-Aware Exposure Scaling in Cross-Sectional Relative Momentum Cryptocurrency Strategies*
- **Venue**：未发表 working paper（repo 内 `main1.tex`）
- **DOI**：N/A
- **Readable URL**：<https://github.com/mmakgolo/Regime-Aware-Exposure-Scaling-in-Cross-Sectional-Relative-Momentum-Cryptocurrency-Strategies>
- **Repo URL**：<https://github.com/mmakgolo/Regime-Aware-Exposure-Scaling-in-Cross-Sectional-Relative-Momentum-Cryptocurrency-Strategies>
- 关键文件：`README.md`、`macro_state_test.py`、`coordination_overlay_test.py`、`main1.tex`

### 4.2 文献地基（metadata grounding）
- **Han, Chulwoo; Kang, Byeongguk; Ryu, Jehyeon (2024)**
- **Title**：*Time-Series and Cross-Sectional Momentum in the Cryptocurrency Market: A Comprehensive Analysis under Realistic Assumptions*
- **Venue**：SSRN Electronic Journal
- **DOI**：10.2139/ssrn.4675565
- **Readable URL**：<https://doi.org/10.2139/ssrn.4675565>
- **Repo URL**：N/A

这篇 2024 SSRN 不是本轮主 digest 的 alpha 本体，但它给这份 2026 repo 的横截面 / 时序动量地基做了文献坐标。

## 5. repo 里到底怎么定义这条策略
### 5.1 Base signal：标准化横截面 relative momentum
`macro_state_test.py` 的 base 权重不是花哨版本，而是很清楚的 standardized XSM：

1. 先算每个资产过去 `k_lookback=20` 天累计 log return；
2. 对当日横截面去均值；
3. 再除以横截面标准差；
4. 最后用绝对值和归一化，形成 long-short 组合权重。

代码核心是：
- `S_raw = R.rolling(cfg.k_lookback).sum().shift(1)`
- `S_dm = S_raw.sub(S_raw.mean(axis=1), axis=0)`
- `S_std = S_dm.div(S_dm.std(axis=1).replace(0, np.nan), axis=0)`
- `W0 = S_std.div(abs_sum, axis=0).fillna(0.0)`

也就是说，它不是只买 top decile，也不是只做 loser basket，而是**整条横截面 standardized WML/relative-momentum 书**。

### 5.2 状态变量：不是改信号，而是缩 gross exposure
repo 的主创新点不在“重新发明 XSM”，而在给 XSM 配一个 regime-aware gross scaler：

1. **BTC vol scaler**
   - `sigma_target = 0.80`
   - `g_btc = clip(0.80 / sigma_btc, 0.10, 1.0)`
   - BTC realized vol 越高，gross 越缩。

2. **平均相关性 scaler**
   - `rho_ref = 0.40`
   - `g_rho = clip((1 - rho_bar) / (1 - 0.40), 0.10, 1.0)`
   - 横截面越一起动，relative-value 空间越差，gross 越该缩。

3. **dispersion / hybrid scaler**
   - 用横截面 return dispersion 的历史分位来决定何时进一步去风险；
   - 不是直接改 rank signal，而是决定“什么时候少做”。

4. **Goldilocks BTC-vol scaler**
   - repo 还显式写了一个 Goldilocks 版本：BTC vol 处在历史分位的中间区间时给更高权重，过热或过冷都降杠杆；
   - 这是对 short-cycle desk 很有启发的一点：**不只是 high vol 才危险，极低 vol 的拥挤/缺 dispersion 状态同样可能让 XSM 变钝。**

### 5.3 friction 假设写得比很多学生 repo 认真
repo 不是完全忽略成本：
- `long_trade_cost_bps = 10`
- `short_trade_cost_bps = 20`
- `btc_short_funding_annual = 0.05`
- `eth_short_funding_annual = 0.07`
- `short_borrow_scarcity_annual = 0.03`
- `short_margin_friction_annual = 0.02`

这当然还是 daily 研究口径，不是 perp 短周期真实成交模型，但至少已经把“short 端更贵”写进去了，不是裸 Sharpe 幻觉。

## 6. 最值得拿走的硬数据点
这份 paper draft 里，最值得记的不是“收益更高”，而是**raw alpha 在什么状态下被公共因子吞掉**。

### 6.1 baseline XSM 有 alpha，但回撤极其难看
`main1.tex` 表 1 给出的 baseline：
- **Ann. Return**：`21.7%`
- **Ann. Vol**：`49.3%`
- **Sharpe**：`0.44`
- **Max Drawdown**：`-85.9%`

这说明：**横截面动量本体不是没有，但裸跑太脆。**

### 6.2 regime-aware scaling 牺牲收益，换来更可部署的分布
同一张表里，regime-aware XSM：
- **Ann. Return**：`16.7%`
- **Ann. Vol**：`32.8%`
- **Sharpe**：`0.51`
- **Max Drawdown**：`-66.4%`

翻成人话：
- 没有发明新 alpha；
- 但把**同一条 raw alpha 的收益分布**修得更像能部署的东西。

### 6.3 失效机制抓得很实
paper draft 里的另外三条数字很值钱：
- **第一主成分解释约 `66%` 的横截面方差**；
- 这条主成分与 BTC 回报**相关性约 `0.85`**；
- 对应 **`R²` 约 `0.73`**。

也就是说，很多时候你以为自己在做“横截面 relative value”，其实市场已经被同一个 BTC 因子一起拖着跑了。

### 6.4 高波动 stress regime 会显著削弱 XSM
paper draft 明写：
- 当 BTC realized vol 超过历史 **80% 分位**时，
- `momentum_strength × high_vol_regime` 的交互项大约 **`-0.233`**，
- **`p = 0.029`**。

这条结果对 desk 很重要：**不是“波动大就好做”**，对横截面动量来说，高 stress 反而可能让 all-coins-one-beta，relative edge 被压扁。

## 7. 我对这份材料的 desk 结论
### 7.1 真正值得 intake 的，不是“daily XSM 又多一个版本”
如果只是把它读成 daily 论文，那信息增量有限；但对 short-cycle desk，它更有价值的读法是：

**“把 cross-sectional relative momentum 当 raw alpha，把 BTC vol / corr / dispersion 当 exposure router。”**

这比继续围绕某个单币形态内循环更值钱，因为：
- 它补的是**relative-value / basket alpha** 家族；
- 它天然能做 **market-neutral / beta-light**；
- 它给了一个很清楚的 **何时减 gross** 的框架。

### 7.2 这份 repo 更像一个可迁移框架，而不是可原样抄的参数包
不能原样抄的地方：
- 数据频率是 **daily**；
- 研究区间是 **2015–2026**；
- 动态 universe 依赖 **CoinGecko Pro API key**；
- 真实 short-cycle perp 执行成本，跟 paper 里 daily friction 不是一回事。

但可直接迁移的东西非常明确：
- **标准化横截面动量权重**
- **BTC-vol scaler**
- **corr scaler**
- **dispersion / Goldilocks state scaler**

这四样拆出来，完全可以在 `15m / 5m / 3m` 上先做最小实验。

## 8. 对 `1m / 3m / 5m / 15m` 的 desk 化落地
我不建议第一步就把它硬压到 `1m`。更合理的 desk 版本是：**15m 生成 basket signal，5m/1m 做执行与滑点监控。**

### 8.1 Entry / rebalance
- **Universe**：Binance / Bybit / OKX 的 top `12~20` 个高流动性 USDT perp
- **Signal bar**：`15m`
- **Formation lookback**：先试 `8 / 16 / 32` bars（对应 `2h / 4h / 8h`）
- **Signal**：过去 H bars 累计 return 的横截面 standardized score
- **持仓**：long relative winners，short relative losers，组合 gross 归一化到 1
- **更新频率**：每个 `15m` bar rebalance 一次

### 8.2 Exit
这条线不需要复杂花式出场，先用最干净的：
- **默认 exit = 下一次 rebalance 覆盖旧仓**；
- 另加一个 **max holding bars**（先试 `4 / 8 / 12` bars）防 stale signal；
- 不先塞 ATR 止损，避免把 basket alpha 搞成单币趋势线。

### 8.3 Sizing
核心不是单名次大小，而是组合 gross：
- **base weights**：按 standardized cross-sectional score 归一化；
- **gross scalar**：`g_t = g_btc × g_rho × g_gold` 或先做 one-at-a-time A/B；
- **单币上限**：单腿绝对权重上限先卡 `10%~15%`；
- **总 gross**：默认 `1.0x`，由 scaler 降到 `0.1x~1.0x`。

### 8.4 Risk / veto
这条线最该加的不是更多信号，而是 4 个约束：
1. **集中度 veto**：若横截面有效名字数太少，不开仓；
2. **相关性 veto**：若 `rho_bar` 过高，直接 size-down；
3. **BTC shock veto**：BTC 突发大幅单边冲击时，临时减 gross；
4. **funding / borrow stress veto**：short 端 carry 太贵时，把 alpha 和 carry 成本分开看。

### 8.5 Cost
至少跑三套：
- `2 bps/side`
- `4 bps/side`
- `6 bps/side`

外加：
- short funding 年化摊入
- 极端拥挤时的 slippage uplift

否则很容易把 basket alpha 误判成“稳定可做”。

## 9. 这份 repo 的几个真实 caveat
### 9.1 它更像研究仓，不是 production code
repo 很完整，但仍明显偏研究脚本 / paper draft：
- 路径里有大量 report builder；
- 主要口径是 daily；
- 真实交易层没有短周期执行细节。

### 9.2 这里最该带走的是结构，不是参数
不要死记：
- `20d` lookback
- `0.80` sigma target
- `0.40` rho_ref

更该带走的是：
- **相对动量本体**
- **状态变量可观测**
- **gross 应随状态缩放**

### 9.3 它也提醒我们：raw alpha 和 overlay 要分账
这份材料最好的地方，就是让你能把问题拆清楚：
- raw alpha 本体行不行？
- 失效是不是来自公共因子 dominance？
- 去风险是改善分布，还是掩盖信号弱？

这种可分账性，比再拿一个“回测年化 80%”的裸 repo 更值钱。

## 10. 下一步怎么测
### 实验 A：先测 raw alpha 本体，不加任何 overlay
目标：确认在短周期 perp universe 里，standardized XSM 自身有没有 post-cost edge。

- **市场**：Binance USDT perp
- **Universe**：top `15` 流动性合约
- **频率**：`15m`
- **Formation**：`8 / 16 / 32` bars cumulative return
- **权重**：横截面去均值、标准化、绝对值和归一
- **持有**：每 `15m` rebalance，另测 max hold `4 / 8 / 12` bars
- **成本**：`2 / 4 / 6 bps per side`
- **回答问题**：这条 raw alpha 在我们 desk 的 liquid universe 里，post-cost 还能不能站住？

### 实验 B：只加一个 scaler，看谁最有用
目标：分开看 BTC vol、corr、Goldilocks 哪个真的有增量。

按 A 的 raw alpha baseline，分别单独加入：
1. **BTC RV scaler**
2. **平均 off-diagonal corr scaler**
3. **BTC-vol Goldilocks scaler**

比较：
- post-cost Sharpe
- max drawdown
- turnover
- beta vs BTC

### 实验 C：再做组合 scaler
若 B 里有明确增量，再试：
- `g_btc × g_rho`
- `g_btc × g_gold`
- `g_btc × g_rho × g_gold`

重点不是追最高收益，而是看：
- **能否把 MDD 明显压下去**；
- **同时不把 raw alpha 完全缩死**。

### 实验 D：执行层分离
如果 `15m` signal 站得住，再加一层：
- `15m` 产出目标仓位
- `5m / 1m` 做 TWAP / maker-first 执行模拟

这样才能分清：
- 是 signal 本体没 edge；
- 还是 basket turnover / 执行把 edge 吃掉了。

## 11. 一句话结论
**这份 2026 新 repo 最值得 desk 抄的，不是“再做一个 daily 风险控制故事”，而是把 cross-sectional relative momentum 当 raw alpha，把 BTC-vol / corr / dispersion 当可分账的 exposure router；先在 `15m` top-liquid perp basket 上做最小实验，再决定它能不能进入短周期正式素材池。**
