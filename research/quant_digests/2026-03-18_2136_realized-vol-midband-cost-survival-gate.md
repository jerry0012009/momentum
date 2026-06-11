# 别把 Svogun 2022 只读成“1m 成本会吃掉 alpha”：对 15m 来说，更值得先测的是 `realized-vol mid-band` shared allow/deny gate
- 时间：2026-03-18 21:36 UTC
- 类型：论文
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/realized-volatility/cost-survival/regime/filter/paper/crypto/15m
- 证据类型：论文证据 + 本地 pocket check
- 证据强度提示：**中等**（论文全文可得、样本较广，但原文频率不是 15m；当前 desk 读法还需要本地 clean replication）

## 1. 这次看了什么
这次回看的是 **Svogun, Bazán-Palomino (2022)** 的论文 *Technical analysis in cryptocurrency markets: Do transaction costs and bubbles matter?*。和 3 月 10 日那篇 digest 不同，这次不再把它当“成本会吃掉 1m 技术分析”的总论，而是专门抽它对当前 desk 更值钱的旁支：**先别把 vol/regime 写成大而泛的宏观叙事，先把它测成一个很便宜的 shared allow/deny gate。**

## 2. 核心结论
- **一句话核心结论**：对当前 `15m` 三条收口线，更值得先测的不是再发明一个新信号，而是把 `realized-vol mid-band / no-high-vol-extreme` 做成共享过滤层，避开最容易被成本和失真一起放大的 pocket。
- **一句话说明它怎么证明**：论文把 **69 条参数化 MA / breakout 规则** 放到 **BTC、ETH、XRP、LTC、BCH** 的 **2016–2021**、**1-min 与 1-day** 样本里比较扣成本前后表现，再用 **PSY bubble** 去看 excess return 的条件变化。
- 原文最重要的信息不是“技术分析彻底没用”，而是：**扣成本后还能活下来的规则明显变少，尤其 1-min 更惨；1-day 的 survivorship 明显更好。** 这正好提醒我们：不要把任何 15m continuation / retest 规则默认当成 everywhere-on 的主信号。
- 对当前 desk 最值钱的不是复刻论文 headline，而是抽出它的旁支读法：**当成本与 bubble/regime 会重排 survival 时，最便宜的第一步不是预测方向，而是先定义哪些 vol pocket 根本不值得做。**
- 本地现成 pocket check 也给了一个诚实起点：在既有 `rolling_breakout_20` 事件里，`60m_365d / net_low / low_vol / non-bubble` 的均值约 **+0.12%**，而 `high_vol / bubble=True` 约 **-0.22%**；但拉长到 `730d` 后，前者又接近 **0**。这说明它更像**共享生存门**，不像值得单独吹成新 alpha 的主引擎。

## 3. 为什么和当前项目有关
这轮值得认领，不是因为它比三条收口线“更新”，而是因为它**直接帮三条线减少无谓出手**：
- 对 **`V3 final-verdict / breakout-short follow-up`**：很多失败不是方向错，而是出在最挤、最吵、最贵的扩张段；先测 `no_high_vol_extreme`，比再堆一层花哨 shape filter 更便宜。
- 对 **`Fibonacci confirmation / retest_hold`**：回踩守住常死在高波动乱流里；若 `rv_pct` 已在极端分位，先别把一次回抽站回硬读成有效 hold。
- 对 **`EMA / PSAR raw alpha focus`**：既然这条线已经确认对成本敏感，那最优先该补的不是新参数，而是**共享 allow/deny gate**，看它能不能压掉最差 pocket。

## 4. 可复刻的最小实验
### 研究假设
在 `BTC / ETH / SOL` perpetual 的 `15m` 上，给现有三条收口线叠加一个 **realized-vol gate**，能在**不过度砍掉交易数**的前提下，改善成本后表现与失败率；若不能，就应尽快丢回研究池。

### 一个可计算定义
- 用 `rv20 = sqrt(sum(logret^2, 20 bars))` 或等价 20-bar realized vol；
- 用**纯历史窗口**做 `rv_pct`（例如过去 60d 的 trailing percentile，禁止 lookahead）；
- 先只比 3 个便宜版本：
  1. `baseline`：不加 gate；
  2. `no_high_vol_extreme`：仅剔除 `rv_pct >= 0.8`；
  3. `rv_midband_q20_80`：只保留 `0.2 <= rv_pct < 0.8`。
- 三条线都保持原 entry / exit 不变，只加 allow/deny。

### 最小回测切口
- 标的：`BTCUSDT / ETHUSDT / SOLUSDT` perpetual
- 周期：`15m`
- 样本：近 `180~365d`
- 执行：`next-bar open`、`no-overlap`
- 成本：先统一看 `6 / 10 / 15 bps per side`

### 最该先看 4 个指标
- `post_cost_expectancy`
- `failure_before_target`（breakout-short / Fib hold 的早死率）
- `trade_count_retention`
- `positive_window_ratio`

## 5. 风险与保留意见
- 原论文直接频率是 `1-min / 1-day`，不是 `15m`；所以它给的是**方向正确的过滤思路**，不是现成参数答案。
- 论文里的 bubble 用 `PSY`，而第一轮 desk 实验大概率只能先用轻量 `realized-vol percentile` 代理；这会损失一部分 regime 识别精度。
- 这条线最容易犯的错，是把“高波动里更难活”误写成“高波动一律不做”；若最后只是靠大幅砍单换一点点改善，就不值得升格。
- 本地 pocket check 已经提醒我们：这条线可能只有**温和过滤价值**，未必配得上主预算。

## 6. 来源
1. **Svogun, D., & Bazán-Palomino, W. (2022).** *Technical analysis in cryptocurrency markets: Do transaction costs and bubbles matter?* Journal of International Financial Markets, Institutions and Money.
   - DOI: https://doi.org/10.1016/j.intfin.2022.101601
   - Readable URL: https://www.sciencedirect.com/science/article/pii/S1042443122000816
   - Crossref URL: https://api.crossref.org/works/10.1016/j.intfin.2022.101601
   - Repo URL: N/A
2. **Current local evidence anchor**
   - File: `reports/artifacts/literature/scout_rank23_vol_regime_pocket_check.csv`
   - File: `reports/artifacts/literature/scout_rank23_vol_regime_source_intake_card.csv`

## 7. 下一步怎么测
第一步不要另起炉灶，也不要引入新外部数据。**只在现有三条收口线上叠一个 `rv gate`**，比较 `baseline`、`no_high_vol_extreme`、`rv_midband_q20_80`。如果它能在保留大部分交易数的前提下，明显压低 `failure_before_target` 并改善 `post_cost_expectancy`，就留作 shared gate；如果改善只靠大幅砍单，或 OOS 一拉长就归零，这条线就该停在 `park / evidence pool`。