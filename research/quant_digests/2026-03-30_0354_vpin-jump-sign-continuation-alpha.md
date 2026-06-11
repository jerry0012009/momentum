# 别把 VPIN 继续只当风险 veto：这篇 2025 RIBAF + 2026 公共数据仓库更该先测的是「high-VPIN × realized jump sign」1m/3m/5m raw alpha
- 时间：2026-03-30 03:54 UTC
- 类型：2025 *Research in International Business and Finance* 摘要级证据（OpenAlex/Crossref）+ 2026 GitHub 公共 Binance trade-data microstructure 仓库 code audit
- 主题类型：raw alpha
- 基础 alpha：**高毒性订单流推动的同向跳跃延续**——当 `VPIN` 处于高分位、且当前 bar 已经出现可识别的方向性 jump 时，下一到数根 bar 更值得先测 **jump-sign continuation**，而不是无脑把高 VPIN 只当 veto
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/microstructure/vpin/order-flow-toxicity/price-jump/jump-sign/continuation/single-asset/btc/binance/aggtrades/ofi/tca/1m/3m/5m/paper/repo/public-data/cost
- 证据类型：论文摘要级因果结论 + 开源指标实现 + 公共数据最小实验口径

## 1. 这次看了什么
这次主看两份材料：

1. **Atiwat Kitvanitphasu, Khine Kyaw, Tanakorn Likitapiwat, Sirimon Treepongkaruna (2025)**，
   **_Bitcoin wild moves: Evidence from order flow toxicity and price jumps_**，
   *Research in International Business and Finance*，Volume 81，Article 103163，DOI: `10.1016/j.ribaf.2025.103163`。
2. **Matthew Carlino (2026)** 的 GitHub 仓库 **`crypto-microstructure`**，用 Binance 公共 `aggTrades` 直接计算 `VPIN / OFI / Kyle's lambda / spread / TCA`，给了一个不依赖私有数据的可复现骨架。

这轮选题之所以值得做，不是因为 VPIN 这个词新，而是因为我们之前更常把它当：
- breakout 的风险 veto，或
- “高毒性 = 少做”的 shared overlay。

但这篇 2025 论文给出一个更值得 desk 立刻单独拉出来测的读法：

> **高 VPIN 不是只能告诉你“这里危险”，它还可能告诉你“这里有单边知情流正在推进 jump，本身就是可交易的方向性 alpha 素材”。**

也就是说，这轮不把 VPIN 当 filter 主角，而是把它升级成：
**`high-VPIN × realized jump sign → next-bar / next-few-bar continuation`** 的 raw alpha 候选。

## 2. 核心结论
### 2.1 先回答一句：这篇东西的 base alpha 是什么？
**base alpha = 高毒性订单流驱动的方向性 jump 延续。**

更具体说：
- 当市场进入 **高 VPIN**（订单流高度不平衡、信息不对称升高）状态时；
- 如果当下已经出现了一个方向明确的 **price jump**；
- 那下一段时间更值得先测的是 **沿 jump 方向继续跟随**，而不是立刻反手去做均值回归。

### 2.2 论文里明确给出的东西
按 OpenAlex 可读摘要，这篇 2025 RIBAF 论文明确写了几件事：

- 用 **Bitcoin high-frequency data**；
- 用 **VAR** 框架研究 `VPIN` 与 `price jumps` 的动态关系；
- 发现 **VPIN 显著预测未来价格跳跃**；
- 同时 **VPIN 本身和 jump size 都存在正向序列相关**，作者将其解释为 **persistent asymmetric information + momentum effects**；
- price jump 对 VPIN 的反向作用“偶尔存在”，但不是主导关系；
- 结果对不同 jump test 都稳健，尤其提到 **Jiang and Oomen (2008)** jump test；
- 论文还观察到 **time-zone / day-of-week** 差异，这说明时区和星期效应更适合做第二层 gate，而不是 alpha 本体。

一句话压缩：

> **不是“高 VPIN 所以别碰”，而是“高 VPIN 下已经发生的 jump，更可能不是噪音，而是知情流推动的短窗单边推进”。**

### 2.3 这和我们之前的 VPIN 用法有什么不同
之前 desk 更自然的读法是：
- 高 VPIN → 流动性更差 / adverse selection 更高；
- 所以拿它去做 **减仓、veto、执行避险**。

这当然没错，但这篇 paper 的值钱之处在于它提示了另一面：
- **高 VPIN 同时也是方向信息密度更高的时刻**；
- 如果你已经观察到一个方向性 jump，
- 那更该先测的是 **same-direction continuation raw alpha**。

因此，这轮最重要的 reframing 是：

- `VPIN alone`：更像 regime / execution warning；
- `VPIN × realized jump sign`：可以升级成 **raw alpha**。

## 3. 为什么和当前项目有关
这轮 bot7 的默认优先级是：
**可独立复现且可直接落地为完整策略的 raw alpha > 只会解释市场结构的 filter/overlay**。

这个主题符合要求，原因有四个：

1. **base alpha 很清楚。**
   不是“情绪变差可能更危险”这种模糊命题，而是：
   `high-VPIN + signed jump -> short-horizon continuation`。

2. **数据公开可得。**
   GitHub 仓库直接走 Binance 公共 `aggTrades`，无需私有逐笔撮合数据，也不需要 API key。

3. **能自然映射到 1m / 3m / 5m。**
   论文虽然只明确写 high-frequency，没在摘要里披露最终 bar 频率；但 repo 已经提供 `1min / 5min / 1h` 聚合与 TCA 指标，desk 只要把 jump proxy 和 holding horizon 缩到 `1~5 bars` 就能做最小实验。

4. **和近期学习进展不冲突，且补的是新的 raw alpha 路线。**
   我们最近已经把不少 microstructure 因子写成 `filter / veto / execution overlay`；这次更值得补的是：
   **把订单流毒性从“不要做”升级为“在特定条件下该顺着做”。**

## 3.5 策略拆解（必填）
- 方向属性：BTC 单币 directional long/short
- 基础 alpha：`high-VPIN × realized jump sign` 的短窗 continuation
- regime：高毒性订单流时段；论文还提示可叠加 `time-zone / day-of-week` gate
- filter / veto：
  - 若只有高 VPIN、没有 jump，不把它直接当入场；
  - 若 jump 已出现，但 `effective spread / taker cost / slippage proxy` 过高，则 veto；
  - 若 VPIN 高但 OFI 与 jump sign 不一致，则降级为观察而非交易。
- risk / sizing / execution overlay：
  - 仓位按 `VPIN quantile × jump strength / realized vol` 缩放；
  - 强制使用成本约束，不能只看方向命中率；
  - 高毒性状态默认优先短持有、少加仓、严格限时退出。

## 4. 真正值得 desk 先偷哪一段
如果只读论文标题，很容易把它归到“市场结构解释文献”。
但对 desk 更值钱的不是解释，而是下面这个可立即实验的命题：

### **raw alpha 假设：有毒流不是只该躲，有时应该顺着它**
把它写成更交易化的语言：

1. 先用逐笔成交计算 `VPIN`；
2. 再定义一个可执行的 `jump proxy`；
3. 只在 **VPIN 高分位 + jump sign 明确** 时开仓；
4. 持有极短，专吃接下来 `1~3` 根 bar 的 follow-through；
5. 若毒性仍高但价差/冲击成本过高，则退出或 veto。

也就是说，**高 VPIN 本身不是 entry；高 VPIN 只是告诉你当前方向性 jump 更不该被自动当成“过热就会反转”。**

这比“把 VPIN 继续塞回 risk overlay”更值得先测，因为它直接扩充的是 raw alpha 素材池。

## 5. 最小可复现实验
### 5.1 数据源与公开性
- **主数据源**：Binance 公共 `/api/v3/aggTrades`
- **公开性**：公开可抓，无需 key
- **最小频率**：逐笔成交 → 可自行聚合成 `1m / 3m / 5m`
- **可用开源实现**：`crypto-microstructure`
  - `compute_vpin(trades_df, bucket_size=100000, lookback_buckets=20)`
  - `order_flow_imbalance(trades_df, freq='1min')`
  - `compute_spreads(...)`
  - `maker_taker_analysis(...)`

仓库里默认示例包含两条很有用的复现口径：
- `VPIN` 默认按 **$100k notional bucket** 演示；
- `scripts/analyze.py` 支持直接输出 `spread / vpin / kyle_lambda / ofi / tca`。

### 5.2 base alpha 的最小 desk 版定义
先不要上复杂 jump test。第一版直接做一个诚实的 proxy：

**Step A：算 VPIN**
- 对逐笔成交按 notional volume 分桶；
- 每个 bar 取截至该 bar 的最新 `VPIN`；
- 用 rolling quantile 做标准化，例如：`VPIN_q = pct_rank(VPIN, 20d intraday history)`。

**Step B：定义 jump**
在 `1m` 或 `3m` bar 上，满足任一即可先记为 jump：
- `abs(ret_1bar) > 2.0 * rolling_sigma_1m`；
- 或 `abs(ret_1bar) > 90%~95%` rolling intraday percentile；
- 若想更贴论文，再升级到 bipower variation / Jiang-Oomen jump proxy。

**Step C：入场**
- `long`：`VPIN_q >= 0.90` 且 `jump_sign > 0` 且 `OFI > 0`
- `short`：`VPIN_q >= 0.90` 且 `jump_sign < 0` 且 `OFI < 0`

这里 `OFI` 不是 alpha 本体，而是确认层：
避免出现“bar 收涨，但订单流其实在净卖出”的假 continuation。

### 5.3 出场与持有
第一版不用复杂 trailing：
- 默认持有 `1 bar / 3 bars / 5 bars` 三档平行回测；
- 或在 `VPIN_q` 回落到 `0.70` 以下时提前平仓；
- 或当下一个 bar 出现反向 jump 时立刻止损离场。

这类信号的关键不是拿长波段，而是：
**只吃高毒性驱动的短窗 follow-through。**

### 5.4 sizing / risk / cost
- `base position`：按 `1 / realized_vol_20d` 做波动率归一；
- `signal scaler`：
  - `size_mult = min(1.0, max(0, (VPIN_q - 0.90) / 0.10))`
  - jump 振幅越大、VPIN 分位越高，仓位越接近上限；
- `cost veto`：
  - 若 `effective_spread` 或 `taker_cost_bps` 位于最近分布的高分位，直接 veto；
  - 若 jump 发生后盘口已明显拉开，也不追。

### 5.5 先测哪些标的
按优先级：
1. `BTCUSDT`
2. `ETHUSDT`
3. `SOLUSDT`

原因很简单：
- 逐笔成交公开、样本多；
- 先在最高流动性标的上判断这是不是普适 microstructure edge，
- 再去看小币是否只是“更毒但也更滑”。

## 6. 这张卡最容易错在哪里
### 6.1 把高 VPIN 当成单独方向因子
这是最常见误读。
- `high VPIN` 本身只说明订单流毒性高；
- 它不天然给方向；
- 真正的 raw alpha 来自 **高 VPIN 与已实现 jump sign 的交互**。

### 6.2 只看命中率，不看交易成本
高毒性时段往往也是：
- spread 更宽；
- taker 冲击更大；
- 被 adverse selection 吃到的概率更高。

所以必须把 repo 里的 `spread / TCA / OFI` 一起带上，
否则很容易做出“方向对，但净值不赚钱”的假 edge。

### 6.3 把它误写成中频趋势策略
这张卡更像：
- `1m / 3m / 5m` 的短窗 impulsive continuation；
- 不是 `1h / 4h` 的慢趋势。

如果持有太久，很可能把“毒性推进”变成“尾声追价”。

## 7. 为什么这轮值得进研究池
这轮不是在补一个新 filter，而是在补一个之前容易被误判成 filter 的 **raw alpha**：

- 过去读到 VPIN，直觉上容易说“高毒性就收手”；
- 但这篇 2025 paper 提示：
  **某些高毒性时刻，恰恰是 jump continuation 最该被优先测的时刻。**

对当前 desk，这比继续补一个“高 VPIN 就减仓”的 overlay 更值钱，
因为它给的是一条新的、可短持有、可直接在 BTC/ETH 上开跑的 microstructure raw alpha 线。

## 8. 下一步怎么测
按顺序做，不要一上来就堆复杂性：

1. **先做条件收益表**
   - 横轴：`VPIN quantile`
   - 纵轴：`current jump sign`
   - 输出：后续 `1/3/5 bars` 平均收益、胜率、t-stat、平均最大顺行/逆行

2. **再做成本后版本**
   - round-trip 先假设 `3 / 5 / 8 bps` 三档；
   - 再接 repo 里的 `effective spread` 与 `taker cost` 做状态化成本扣减。

3. **再做 confirm / veto 分层**
   - `OFI same-sign` vs `OFI opposite-sign`
   - `US session overlap` vs `Asia hours`
   - `weekday` 分层

4. **最后才升级 jump 定义**
   - baseline：rolling sigma jump
   - upgrade：bipower / Jiang-Oomen proxy

如果第一轮实验里：
- `high-VPIN × same-sign jump` 在 `1~3 bars` 上持续为正、
- 且成本后仍留边，
那这张卡就应该从 research digest 升级到 replication queue。

## 9. 来源与链接
### 论文
- **Authors**: Atiwat Kitvanitphasu, Khine Kyaw, Tanakorn Likitapiwat, Sirimon Treepongkaruna
- **Year**: 2025
- **Title**: *Bitcoin wild moves: Evidence from order flow toxicity and price jumps*
- **Venue**: *Research in International Business and Finance*, Volume 81, Article 103163
- **DOI**: `10.1016/j.ribaf.2025.103163`
- **Readable URL**: <https://doi.org/10.1016/j.ribaf.2025.103163>
- **Metadata / Abstract mirror**: <https://api.openalex.org/works?filter=doi:https://doi.org/10.1016/j.ribaf.2025.103163>

### 仓库
- **Author**: Matthew Carlino
- **Year**: 2026
- **Repo**: `Matthew-Carlino/crypto-microstructure`
- **Repo URL**: <https://github.com/Matthew-Carlino/crypto-microstructure>
- **README**: <https://raw.githubusercontent.com/Matthew-Carlino/crypto-microstructure/main/README.md>
- **VPIN implementation**: <https://raw.githubusercontent.com/Matthew-Carlino/crypto-microstructure/main/src/microstructure.py>

## 10. 一句话结论
**别再把 VPIN 只当“别做”的风控灯；这篇 2025 paper 更值得 desk 先测的是：当高 VPIN 与已实现 jump sign 同向共振时，下一到数根 bar 的 continuation 本身就是一条可以独立成卡的 microstructure raw alpha。**
