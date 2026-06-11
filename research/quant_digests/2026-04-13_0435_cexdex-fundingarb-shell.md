# 别把这篇 funding-arb 新论文直接读成“稳定收租”：对 short-cycle desk，更该先拆的是「cross-venue rich-funding carry × basis-compression」这条完整 raw alpha 壳

- 时间：2026-04-13 04:35 UTC
- 类型：2025 论文元数据/摘要复核（OpenAlex + Crossref）+ Binance public `1h` portability probe
- 主题标签：raw-alpha/carry/funding/basis/cross-venue/cex-dex/delta-neutral/complete-shell/binance/5m/15m/execution/paper/abstract-metadata/public-data/cost/risk
- 证据类型：abstract-level 论文证据 + 公共数据 portability probe

- 主题类型：raw alpha
- 基础 alpha：**当同一标的的 perp 腿 funding 明显偏高、且合约价格相对 hedge 腿偏贵时，做 `short rich perp + long cheap hedge leg`，同时赚 funding carry 与 basis 回归；若 hedge 腿来自低 funding venue / DEX，这本质上就是 cross-venue relative-value carry。**
- 是否可独立复现：是（**策略壳与最小实验可复现，但本轮未拿到论文全文，只拿到摘要与元数据**）
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（**壳完整，但本轮 Binance same-venue 便携版不过成本线**）

## 1. 先把一句话说清楚：这篇东西的 base alpha 是什么？

> **base alpha = `rich funding + rich basis` 说明 perp 这条腿被挤得更贵；如果你去空高 funding 的 perp、同时买入更便宜的对冲腿，后面既可能继续收 funding，也可能再赚一段 basis 收敛。**

翻成人话：
- 不是赌 BTC / ETH 要涨还是跌；
- 是赌“同一资产的两条腿现在定价不平”，而且贵的那条腿还在持续付钱；
- 所以它不是 filter，也不是纯风险管理，而是一条 **carry / basis / relative-value raw alpha**。

## 2. 这次看了什么

### 主来源（论文）
- **Authors：** Warodom Werapun, Tanakorn Karode, Jakapan Suaboot, Tanwa Arpornthip, Esther Sangiamkul
- **Year：** 2025
- **Title：** *Exploring Risk and Return Profiles of Funding Rate Arbitrage on CEX and DEX*
- **Venue：** *Blockchain: Research and Applications*
- **DOI：** <https://doi.org/10.1016/j.bcra.2025.100354>
- **Readable URL：** <https://doi.org/10.1016/j.bcra.2025.100354>
- **Repo URL：** N/A

### 本轮能确认到的论文级信息
OpenAlex 摘要明确给出：
- 样本含 **Binance / BitMEX** 等 CEX，与 **ApolloX / Drift** 等 DEX；
- 资产至少覆盖 **BTC / ETH / XRP / BNB / SOL**；
- 比较对象不只是套利本身，还拿来和 **HODL** 做 risk/return 对照；
- 论文声称在 **60 个 arbitrage scenarios** 里，funding arbitrage 与 HODL 低相关，且最强场景 **6 个月收益可到 115.9%**，对应 **possible losses 仅 1.92%**。

注意：**这轮没拿到全文正文**，所以不能把这些数字当成已经被我完整复核过的方法结论；当前只能把它们当作“高强度研究线索 + 需要 desk 自己做 portability 审查”的证据。

## 3. 这篇论文真正值得拿走的，不是“高收益叙事”，而是完整策略壳

它比很多 funding 文章更值钱的地方，在于它至少把下面四件事同时摆在桌上：

1. **alpha 本体清楚**：不是泛泛说 funding 有用，而是明确说 funding-rate arbitrage；
2. **对冲腿清楚**：不是裸方向，而是 delta-neutral / relative-value；
3. **收益来源清楚**：不是只吃 carry，也包含定价回归；
4. **比较对象清楚**：不是只报绝对收益，还和 HODL 做风险收益比较。

这就让它天然比“某个 funding 指标能不能拿来做 gate”更高一层：

> **它是完整策略壳，不是单一特征。**

对我们 desk 来说，最有用的读法不是“马上照抄 CEX/DEX 组合”，而是先拆成两个可验证层：
- **核心 raw alpha**：rich-funding leg 最终会不会向更公平价格回归；
- **短周期执行层**：`5m / 15m` 能不能把 entry、boundary、平仓、避险做得比论文里的粗粒度持有更细。

## 3.5 策略拆解（必填）
- **方向属性：** relative value / stat-arb / carry
- **基础 alpha：** `short rich-funding perp + long cheap hedge leg`
- **regime：** funding 极端、basis 偏离、跨 venue 价差仍可执行
- **filter / veto：** funding 方向翻转、basis 已收敛、深度不足、gas / taker 成本过高、临近高波动事件
- **risk / sizing / execution overlay：** notional cap、single-venue / single-asset concentration cap、5m/15m boundary execution、maker-first / taker fallback、time-stop 到下一次 funding

## 4. 我做了一个最小 public-data portability probe：结论比论文摘要保守得多

### 4.1 数据源、公开性、更新频率、最小复现实验口径
- **数据源：** Binance public REST
  - `fapi/v1/fundingRate`
  - Spot `api/v3/klines`
  - USDⓈ-M Perp `fapi/v1/klines`
- **公开性：** 公开可得
- **更新频率：** funding 每 `8h`；K 线可下到分钟级，本轮先用 `1h` 对齐 funding window
- **最小实验口径：**
  - 资产：`BTC / ETH / BNB / XRP / SOL`
  - 样本：`2025-10-01 ~ 2026-04-13`
  - 事件：正 funding 事件
  - 交易：在 funding 时点做 `short perp + long spot`，持有到下一次 funding（约 `8h`）
  - 粗估 PnL：`funding_bps + basis_entry - basis_exit - 8bps round-trip cost`

### 4.2 结果
我把重点先放在 **“单 venue 便携版能不能活”** 这个最朴素问题上。

**结果：不太行。**

- 在 `funding >= +1 bps / 8h` 的事件里，五个币合计只有 **84** 个事件；
- 这 84 个事件的 **加权平均 gross 只有 `+0.59 bps / 8h`**；
- 如果粗扣 `8 bps` round-trip，**加权平均 net 变成 `-7.41 bps / 8h`**；
- `net > 0` 的事件比例是 **0%**；
- 分资产看，**BNB** 最好，gross 约 **`+1.27 bps / 8h`**；但仍远低于 `8 bps` 粗成本；
- **ETH** 在这个口径下甚至连 gross 都是负的，约 **`-0.63 bps / 8h`**。

更直白一点：

> **“CEX/DEX funding arbitrage 很美” ≠ “Binance 单 venue short rich-funding carry 现在就能稳定收租”。**

这也刚好解释了为什么这篇论文真正该被我们拿来学的，不是“always-on carry”，而是：
- **跨 venue** 才可能有足够厚的 funding differential；
- **basis 回归** 是第二收益来源，不能只看 funding 本身；
- **成本、深度、gas、转仓效率** 才是这类策略的生死线。

### 4.3 本轮 artifact
- `reports/artifacts/literature/funding_cexdex_binance_probe_2026-04-13_summary.csv`
- `reports/artifacts/literature/funding_cexdex_binance_probe_2026-04-13_asset_breakdown.csv`
- `reports/artifacts/literature/funding_cexdex_binance_probe_2026-04-13_detail.csv`

## 5. 为什么和当前项目有关

它和 `momentum` 当前主线有关，不是因为我们准备去做“超低频套利基金”，而是因为它补的是 **raw alpha 素材池里最缺的一块：carry / funding / basis 完整壳**。

当前很多 funding 相关材料的问题是：
- 只告诉你 funding 高/低；
- 但没把 hedge leg、exit、risk、cost 写完整；
- 最后只剩一个 filter。

这篇 paper 的好处是：
- 至少把 funding 这条线抬到了 **完整策略壳**；
- 让我们可以把 `5m / 15m` 研究重点放在：
  1. **boundary 前后怎么进**；
  2. **basis 还够不够宽**；
  3. **是否要做 maker-first / taker fallback**；
  4. **跨 venue 版本有没有真实容量**。

所以这篇东西更像：
- **新 raw alpha 候选**，而不是单纯 overlay；
- 但 short-cycle desk 真正该接的，是它的 **execution / admission / cost layer**。

## 6. 可复刻的最小实验

### 实验 A：先做最朴素的 single-venue 否决
- **假设：** 如果同所 `short rich perp + long spot` 都过不了线，那就别急着吹跨 venue 大故事。
- **定义：**
  - `funding_bps >= 1 / 2 / 3 / 4`
  - `basis_bps = (perp / spot - 1) * 10000`
  - `gross = funding + basis_entry - basis_exit`
- **样本：** Binance `BTC/ETH/BNB/XRP/SOL`，先跑最近 `180d`
- **先看指标：** `mean gross bps`、`mean net bps`、`events`

### 实验 B：再做真正有 desk 意义的 `5m / 15m` 版本
- **假设：** 真正的 edge 不在“8 小时死拿”，而在 funding boundary 前后的更优 entry。
- **定义：**
  - 先用 `1h` / `8h` funding state 选事件；
  - 再在 `5m / 15m` 上找 `basis widening stop / first compression / depth okay` 的进场点；
  - exit 用 `next funding / basis z-score 回归 / time-stop` 三选一。
- **样本：** 先只做 `BTC / ETH / SOL`；
- **先看指标：** `entry basis improvement`、`post-cost net bps`。

### 实验 C：如果要继续，才进入 cross-venue
- **假设：** 论文真正的厚收益，主要来自跨 venue funding differential，而不是同所 carry。
- **最小数据：** Binance + 1 个 DEX / 1 个 CEX 的公开 funding、mid、fee、withdraw/gas 代理；
- **先看指标：** `net carry after all-in friction`、`time-to-close`、`max adverse excursion`。

## 7. 风险与保留意见

1. **全文缺失风险**：本轮没拿到正文，所以不知道论文的 leverage、调仓、成本、清算、gas、借币口径到底怎么写；摘要里的 `115.9% / 6m` 只能先当线索，不能直接当结论抄。
2. **频率错配风险**：funding 天生是 `8h` 节奏；若要映射到 `5m / 15m`，必须老实承认：短周期层更像 execution / admission，不是把 funding 硬伪装成逐根主信号。
3. **跨 venue frictions 可能吃掉大部分 edge**：尤其是 DEX gas、桥接、maker/taker、滑点、inventory 占用。
4. **同 venue 版本当前太薄**：本轮 Binance public probe 已经提示，single-venue rich-funding carry 本身不够厚，至少不能当“稳定印钞机”。

## 8. 一句话结论

> **这篇 2025 paper 值得进池，不是因为它“证明 funding 能赚钱”，而是因为它把 `funding + basis + hedge leg + risk/return` 组合成了完整 raw alpha 壳；但对我们 desk，第一落点应该是“先否决单 venue 薄 edge，再去找真正够厚的 cross-venue dislocation”。**

## 9. 来源

1. **Werapun, W., Karode, T., Suaboot, J., Arpornthip, T., & Sangiamkul, E. (2025). _Exploring Risk and Return Profiles of Funding Rate Arbitrage on CEX and DEX_. Blockchain: Research and Applications.**
   - DOI: <https://doi.org/10.1016/j.bcra.2025.100354>
   - Readable URL: <https://doi.org/10.1016/j.bcra.2025.100354>
   - OpenAlex metadata: <https://api.openalex.org/works/https://doi.org/10.1016/j.bcra.2025.100354>
   - Crossref metadata: <https://api.crossref.org/works/10.1016/j.bcra.2025.100354>

2. **Binance Public API Docs / Endpoints**
   - Spot klines: <https://api.binance.com/api/v3/klines>
   - Perp klines: <https://fapi.binance.com/fapi/v1/klines>
   - Funding history: <https://fapi.binance.com/fapi/v1/fundingRate>
