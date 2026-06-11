# 别把 Polymarket 只读成情绪盘：对 short-cycle desk，更该先测的是「adjacent-horizon YES-price spread × Kalman-OU reversion」这条 raw alpha
- 时间：2026-04-07 07:40 UTC
- 类型：2026 GitHub 新 repo + Polymarket public docs source audit
- 主题类型：raw alpha
- 基础 alpha：同一事件族里、相邻到期/截止时间的 YES 概率曲线会短时扭曲，随后向更平滑的 term structure 回归
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/relative-value/stat-arb/prediction-market/polymarket/term-structure/mean-reversion/kalman/ou/kelly/external-data/1m/3m/5m/15m
- 证据类型：工程经验 / repo source audit

## 1. 这次看了什么
这次看的是 **razr321 (2026) 的 GitHub repo `polymarket-pairs`**，repo 自我描述就很直接：**“Polymarket term structure pairs trading — Kalman + OU + Kelly sizing”**。虽然仓库目前公开出来的主文件是 `streamlit_app.py`，不是完整论文或回测报告，但它已经把策略骨架暴露得很清楚：`pair_state` 里有 `last_z / last_hr / ou_kappa / ou_halflife / is_cointegrated / coint_pval / kelly_fraction / position_size`，`signals` 里记录 `signal_type / z_score / price_short / price_long`，`trades` 里还有 `entry_z / exit_z / hours_held / exit_reason / pnl_usd`。这说明它不是泛看板，而是一条已经拆到**配对、建模、入场、 sizing、出场**的 relative-value 策略壳。

## 2. 核心结论
- 这条东西的 **base alpha 很清楚**：不是赌 BTC 会涨还是跌，而是赌**同一事件不同 horizon 的隐含概率曲线不会长期扭曲**。短腿贵了、长腿便宜了，或者反过来，往往更像 term structure 的局部 kink，而不是永久新信息。  
- repo 暗示的最小可交易定义也很清楚：**Kalman 动态 hedge ratio + OU half-life + z-score 入场 + Kelly fraction sizing**。也就是先把两条相关合约做成 spread，再赌 spread 向均值回去。  
- 这对当前 desk 的价值在于：它补的是一条**和 trend / breakout / 单币 mean reversion 完全不同的 raw alpha**。你不用先判断方向，只需要抓**同事件曲线内部的相对错价**。  
- 它和短周期的关系也顺：Polymarket 的公开盘口/市场列表天然能按分钟采，先做 `1m`，再降采到 `3m/5m/15m` 看噪音与成交可行性，研发成本不高。

## 3. 为什么和当前项目有关
这条线最值钱的地方，是它把 **external-data / prediction-market** 真正变成了一条可独立复现的 raw alpha，而不是把外部数据硬装成 shared gate。对当前 `momentum` desk，它更像：
- 一条新的 **relative-value / stat-arb** 素材；
- 一个和现有 breakout、LOB continuation、basis/funding 收敛互补的 alpha 家族；
- 一个能训练我们把“外部概率曲线”也写成 **entry / exit / sizing / risk** 的工程模板。

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / 统计套利  
- 基础 alpha：相邻 horizon YES-price spread 的均值回复  
- regime：同事件族、可配对、cointegration 仍成立、距离结算还有安全缓冲  
- filter / veto：`coint_pval` 不通过不做；盘口过宽/过浅不做；临近结算、信息跳变或 stale quote 不做  
- risk / sizing / execution overlay：`kelly_fraction` 上限、单 pair gross cap、`2×OU half-life` time stop、maker-first 或严格 taker 成本门槛

## 4. 可复刻的最小实验
- **研究假设**：同一 crypto 事件族（例如同一标的、不同截止时间）里，相邻合约的 YES 概率曲线若出现异常陡峭/倒挂，未来 `1~12h` 会向更平滑结构回归。  
- **一个可计算定义**：每分钟抓取同事件族两个相邻 horizon 的 `yes_price`，用 Kalman 估动态 hedge ratio，定义 `spread_t = price_long - hr_t * price_short`，再用 rolling OU / z-score 标准化；当 `|z| > 2` 才开仓，`z` 回到 `0 ~ 0.5`、或达到 `2×half-life`、或接近结算时平仓。  
- **最小回测切口**：只选 Polymarket 上流动性最好的 crypto recurring markets，先做最近 `60~90d`，主频 `1m`，再对照 `3m/5m/15m`。  
- **最该先看**：`post-cost pnl/trade`、`持仓时长 vs OU half-life`，再补 `胜率 / max adverse excursion / 成交占比`。如果 `1m` 太吵，就先看 `5m` term-structure spread bar。  

## 5. 风险与保留意见
- 这是 **repo 级证据**，不是论文级强证据；当前公开仓库更像 live monitor + state schema，证据强度中等。  
- Prediction market 的价格会受**离结算时间、盘口深度、单边情绪、手续费**强影响，不能把它当连续期货曲线。  
- 同事件不同 horizon 也可能对应**真实信息更新**，不一定回归；所以必须加**临近结算 veto、盘口宽度 veto、最大持有时长**。  
- 若成交主要靠 taker，成本和滑点可能直接吃掉 edge；这条线优先适合做**高流动 pair 的轻仓 relative-value sleeve**，不是无脑全市场扫射。

## 6. 来源
1. **razr321 (2026). _polymarket-pairs_. GitHub repository.**  
   - Repo URL: `https://github.com/razr321/polymarket-pairs`  
   - Readable URL: `https://github.com/razr321/polymarket-pairs`  
   - Code URL: `https://raw.githubusercontent.com/razr321/polymarket-pairs/main/streamlit_app.py`  
   - Repo note: description 为 `Polymarket term structure pairs trading — Kalman + OU + Kelly sizing`；创建时间 `2026-03-29`，最近 push `2026-04-01`。  
2. **Polymarket Docs. _CLOB Introduction_.**  
   - Readable URL: `https://docs.polymarket.com/developers/CLOB/introduction`  
3. **Polymarket Docs. _Gamma Markets API / Get Markets_.**  
   - Readable URL: `https://docs.polymarket.com/developers/gamma-markets-api/get-markets`
