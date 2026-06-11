# 别把 PSAR trailing stop 直接接管 15m 出场：它更像可选 fail-safe，不是三条收口线的 shared 默认 exit
- 时间：2026-03-20 10:04 UTC
- 类型：GitHub 仓库 + Binance 公共数据代理快检
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/trailing-stop/exit-role/handoff/fail-safe/repo/crypto/5m/15m
- 证据类型：仓库代码（工程证据）+ 公开 OHLCV 最小代理快检

## 1. 这次看了什么
这轮主看两份近 5 年可复刻仓库线索：
- **EarnForex / PSAR-Trailing-Stop（2023 建仓，2025 仍活跃）**：明确把 PSAR 用成 trailing stop，而不是入场器；
- **fmzquant / Parabolic-SAR-Trailing-Stop-Loss-Strategy（2023）**：同样强调“PSAR 更像翻向止损/跟踪器”。

这轮不抄“PSAR 反转即开仓”的 headline，而是只抽一个更贴合 desk 的旁支问题：
**PSAR 在 15m 上更适合扮演“全程默认退出器”，还是“入场后可选 fail-safe（handoff）”？**

## 2. 核心结论
- **一句话核心结论：** 在 15m 上，PSAR 不适合直接接管三条主线的默认出场；更合理的定位是“存活若干 bar 后再接手”的可选 fail-safe。  
- **一句话证明方式：** 仓库给出可计算规则（PSAR trailing）；我用 Binance 公开 15m K 线（BTC/ETH/SOL 近 180d）做最小代理，对比 `baseline exit`、`immediate PSAR exit`、`3-bar handoff→PSAR` 三臂。

关键数据点（聚合，单边成本 10 bps，回合成本 20 bps）：
1. **immediate PSAR 并未改善成本后期望**：`baseline` 加权期望 **-19.26 bps/trade**，`PSAR` 为 **-19.79 bps/trade**（更差）；且中位持有从 **3 bar** 降到 **1 bar**，明显更“急停”。
2. **handoff3（前 3 bar 用基线，再交给 PSAR）略好于 baseline**：加权期望 **-18.94 bps/trade**，较 baseline 改善约 **+0.32 bps/trade**；但仍未转正，只是“减亏级”改进。
3. **跨资产不一致，不能直接 shared 默认化**：handoff3 在 SOL 改善（-18.90 → -16.43 bps），但 BTC/ETH 分别变差到 **-20.21 / -19.82 bps**，说明它更像 setup/资产条件化工具。

翻成人话：
- PSAR 的“止损纪律”没问题；
- 但“立刻交给 PSAR 全程托管”容易过早把单子掐掉；
- 更诚实的角色是：**先让入场逻辑自己走几根确认，再把 PSAR 当 fail-safe 接管。**

## 3. 为什么和当前三条收口线有关
- **EMA / PSAR raw alpha focus**：这轮直接回答“角色判断”——PSAR 更像 exit 风险阀，不像 raw alpha 主引擎。  
- **V3 final-verdict / breakout-short follow-up**：可把 PSAR 放在 follow-up 已成立之后，作为“失速再退出”的后置阀门，而不是 entry 当下主判决。  
- **Fibonacci confirmation / retest_hold**：对 retest_hold 同理，先看 hold 成立，再让 PSAR 接管尾部风控，避免“刚站上就被同周期噪声扫掉”。

## 4. 可复刻的最小实验（下一步怎么测）
### 研究假设
在冻结现有三条收口线入场定义后，`handoff→PSAR` 会优于 `immediate PSAR`，并在不显著砍交易数的前提下改善成本后表现。

### 一个可计算定义（先冻最小版）
- `A`：现有 baseline exit（不改入场）；
- `B`：入场后立即启用 PSAR trailing；
- `C`：入场后前 `N=3` bar 用 baseline，之后启用 PSAR trailing；
- （可选）`D`：`C + ATR buffer`（仅用于二轮，不进首轮）。

### 最小回测切口
- 资产：`BTC/ETH/SOL` perpetual（首轮也可先用 spot/public proxy 做 smoke test）
- 周期：`15m` 主评估，`5m` 做执行细化
- 样本：近 `180d`
- 执行：`next-bar open`、`no-overlap`
- 成本：`6 / 10 / 15 bps per side`

### 先看哪 2 个指标
- `post-cost expectancy`
- `trade retention + median hold`（防止“只靠早退把波动压小”）

## 5. 风险与保留意见
- 当前是“仓库规则 + 公开 K 线代理”快检，不是严格论文级因果识别；
- 代理实验使用简化 EMA continuation 入场，并非 desk 三条线完整生产定义；
- `PSAR 参数（0.02/0.02/0.2）` 与执行滑点敏感，跨资产稳定性需二轮验证；
- 本轮结论是“角色定位优先级”，不是“PSAR 无效”。

## 6. 来源
1. **EarnForex Team. (2023, updated 2025). _PSAR-Trailing-Stop_. GitHub repository.**
   - Authors: EarnForex Team
   - Year: 2023（仓库更新时间 2025）
   - Title: PSAR Trailing Stop
   - Venue: GitHub
   - DOI: `N/A`
   - Readable URL: `https://github.com/EarnForex/PSAR-Trailing-Stop`
   - Repo URL: `https://github.com/EarnForex/PSAR-Trailing-Stop`
2. **ChaoZhang. (2023). _Parabolic-SAR Trailing Stop Loss Strategy_. FMZ / GitHub mirror.**
   - Authors: ChaoZhang
   - Year: 2023
   - Title: Parabolic-SAR Trailing Stop Loss Strategy
   - Venue: FMZ Quant + GitHub (`fmzquant/strategies`)
   - DOI: `N/A`
   - Readable URL: `https://www.fmz.com/strategy/426993`
   - Repo URL: `https://github.com/fmzquant/strategies`
3. **Wilder, J. W. (1978). _New Concepts in Technical Trading Systems_.**
   - Authors: J. Welles Wilder
   - Year: 1978
   - Title: New Concepts in Technical Trading Systems（PSAR 概念来源）
   - Venue: Book
   - DOI: `N/A`
   - Readable URL: `https://en.wikipedia.org/wiki/Parabolic_SAR`
   - Repo URL: `N/A`
4. **Binance Spot Kline/Candlestick API（公开数据）**
   - Readable URL: `https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#klinecandlestick-data`
   - 公开性：公开可得
   - 更新频率：逐根 K 线更新（5m/15m 可直接获取）

---
快检文件：
- `reports/artifacts/literature/psar_trailing_role_proxy_asset_summary_2026-03-20.csv`
- `reports/artifacts/literature/psar_trailing_role_proxy_pool_summary_2026-03-20.csv`
