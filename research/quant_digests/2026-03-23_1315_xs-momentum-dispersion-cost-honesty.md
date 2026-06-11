# 别把横截面动量直接判死：这份 2026 新仓库更值钱的是「dispersion-aware XS momentum」这条 raw alpha 检验骨架
- 时间：2026-03-23 13:15 UTC
- 类型：GitHub 新仓库 + Binance 公共数据最小快检 + 论文线索（含 abstract-only）
- 主题类型：raw alpha
- 基础 alpha：cross-sectional momentum（同一时点做多近期赢家、做空近期输家）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-sectional/momentum/relative-value/dispersion/regime/cost/turnover/perp/crypto/5m/15m
- 证据类型：工程证据 + 本地快检 + 论文线索

## 1. 这次看了什么
先回答 base alpha：**这篇东西的基础 alpha 是横截面动量（XS momentum）本体**，不是 filter。主看 2026 新仓库 `prams2104/crypto-momentum-backtest`，并用 Binance USDT perp 公共 15m 数据做了同家族最小快检；另外用 `Jamestilfords/statarb-crypto` 做成本敏感度对照（同属 XS 动量/反转框架）。

## 2. 核心结论
- **一句话核心结论：** XS momentum 不是“永远有效”也不是“完全无效”，对当前 desk 更诚实的读法是：它是可独立复现的 raw alpha 家族，但强烈依赖 `cross-sectional dispersion + 成本/换手约束`。
- **一句话证明方式：** 新仓库给了分段 OOS 与统计检验；本地 15m 快检进一步把同一 alpha 压到短周期并显式计入成本，结论是“毛边有、净值难活”。
- 仓库（2026）里 20-day XS momentum 的分段结果：Training 年化 alpha 约 **+36.2%**（t≈2.02），Validation 降到 **+13.5%**（t≈1.08），OOS（2025–2026）变成 **-12.5%**（t≈-0.81）。这说明“同一套动量排序”有明显状态依赖。
- 同仓库也展示了一个反面教材：短反转即便 OOS 看起来强，若日换手过高（文中约 **138%/day**），净值会被成本吃掉。
- 本地 15m 最小快检（90 天、20 个液态 USDT perp、8h 排名+1h 持有、top/bottom 20%、粗成本 8bps）：
  - `raw_all`: **gross +1.603 bps/trade**, **net -6.397 bps/trade**
  - `disp_top_third`: **gross +4.125 bps/trade**, **net -3.875 bps/trade**
  读法：高离散度区间确实更像“有信号”，但还没跨过成本线。

## 3. 为什么和当前项目直接相关
- 这是在补 **raw alpha 素材池**（cross-sectional / relative-value），不是继续加一个 breakout 配件。
- 它天然可落地完整策略：有 entry（排序分组）、exit（固定持有/反向信号）、sizing（美元中性权重）、risk（集中度/单币上限）、cost（换手+费率）。
- 对当前 `5m/15m` 主线很实用：不是再争论“有没有 alpha”，而是直接进入“什么条件下成本后能活”的 first verdict。

## 3.5 策略拆解（必填）
- 方向属性：横截面 / 相对价值（市场中性 long-short）
- 基础 alpha：按过去 `L` 根收益对币种横截面排序，long top quantile、short bottom quantile
- regime：优先在横截面离散度高、成交活跃、相关性不极端收敛时启用
- filter / veto：低离散度、薄流动性、重大事件窗口、极端 funding 扰动时降档或停机
- risk / sizing / execution overlay：美元中性、单币权重上限、换手上限、maker 优先/分批执行、显式费率与冲击成本入账

## 4. 可复刻的最小实验（下一步怎么测）
- **研究假设：** XS momentum 在 `15m` 不是全时段可交易；只有在高离散度 + 成本可覆盖时才可能形成可活的短周期 pocket。
- **最小定义：**
  - 数据：Binance USDT perp 公共 klines（公开可得，15m；后续可下钻 5m/3m）
  - 信号：`r_i(t,L)=P_i(t)/P_i(t-L)-1`，横截面分位排序
  - 组合：long top 20%、short bottom 20%，美元中性
  - 出场：固定持有 `H` 根后平仓（先测 `H=2/4/8`）
  - 成本：至少 `maker/taker + 滑点`，再加 participation-based impact
- **最小回测切口：**先跑 `L ∈ {16,32,64}` × `H ∈ {2,4,8}` 的 15m 网格；再将最稳两组下钻到 5m/3m。
- **先看 4 个指标：**`post-cost bps/trade`、`turnover/day`、`dispersion-conditional hit ratio`、`capacity@participation cap`。

## 5. 风险与保留意见
- 这条 alpha 最大风险不是“信号不存在”，而是**信号太薄 + 换手太高**导致成本后为负。
- 本地快检成本是粗口径（8bps），实盘应按账户费率与成交方式重算。
- 当前引用的 SSRN 论文链接受反爬限制，本文对其仅作题录线索，不把未读全文内容当强证据。

## 6. 来源
1. **Pramesh. (2026). _crypto-momentum-backtest_. GitHub repository.**
   - Repo URL: https://github.com/prams2104/crypto-momentum-backtest
   - Readable URL: https://github.com/prams2104/crypto-momentum-backtest
2. **Jamestilfords. (2026). _statarb-crypto_. GitHub repository.**
   - Repo URL: https://github.com/Jamestilfords/statarb-crypto
   - Readable URL: https://github.com/Jamestilfords/statarb-crypto
3. **Han, J., Kang, J., & Ryu, D. (2024). _Time-Series and Cross-Sectional Momentum in the Cryptocurrency Market: A Comprehensive Analysis under Realistic Assumptions_. SSRN.**
   - DOI: `10.2139/ssrn.4675565`
   - Readable URL: https://doi.org/10.2139/ssrn.4675565
4. **Wen, F., Bouri, E., Xu, Y., & Zhao, L. (2022). _Intraday return predictability in the cryptocurrency markets: Momentum, reversal, or both_. North American Journal of Economics and Finance.**
   - DOI: `10.1016/j.najef.2022.101733`
   - Readable URL: https://doi.org/10.1016/j.najef.2022.101733

## 7. 本地复现产物
- `reports/artifacts/quant_digests/xs_momentum_15m_20260323/summary.csv`
- `reports/artifacts/quant_digests/xs_momentum_15m_20260323/trade_log.csv`
- `reports/artifacts/quant_digests/xs_momentum_15m_20260323/close_tail_500.csv`
- `reports/artifacts/quant_digests/xs_momentum_15m_20260323/meta.txt`
