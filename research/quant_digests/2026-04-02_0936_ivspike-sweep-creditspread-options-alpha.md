# 别把这份 2025 新 repo 只读成“UI 期权脚本”：对 short-cycle desk，更该先测的是「near-expiry IV spike × 1m liquidity sweep → short vertical credit spread」这条事件驱动 raw alpha
- 时间：2026-04-02 09:36 UTC
- 类型：2025 GitHub 新仓库 source audit（`README.md` + `iv_crush_bot.py` + GitHub API metadata）+ Delta Exchange 公共 API live snapshot（`/v2/products` `/v2/tickers` `/v2/history/candles`）
- 主题类型：raw alpha
- 基础 alpha：同日到期期权在 `IV 短时抬升 + 1m 扫流动性假突破` 后，期权时间价值与隐含波动率更容易快速回落；通过卖出同到期垂直 credit spread 捕捉 `IV crush + theta` 回归。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（可 paper/live 直接跑，但需补成交质量与滑点治理）
- 主题标签：raw-alpha/options/mean-reversion/iv-crush/liquidity-sweep/event-driven/vertical-credit-spread/near-expiry/same-venue/btc/1m/3m/5m/15m/repo/external-data/cost/risk
- 证据类型：2025 GitHub repo source audit（主证据）+ Delta Exchange 公共 API 实时口径核验（辅助证据）

## 1. 这次看了什么
一句话：**这轮值得 intake 的不是“又一个期权看板”，而是一条可直接落地的短周期 options raw alpha：当 near-expiry ATM IV 突升且 1m 出现 sweep wick 时，卖出同到期窄宽度 credit spread，赚 IV 回落与时间衰减。**

## 2. 先回答：base alpha 是什么？
这篇的 base alpha 很清楚，不是 filter：

> **`near-expiry implied vol overshoot` 的短时均值回归 + `0DTE theta decay`**。

`sweep` 和 `EMA` 在这个框架里是**入场确认与方向选择**，不是 alpha 本体。

## 3. 主来源与可追溯信息

### A) 主证据（仓库）
- Owner / Year: **NOVESH-CREATE (2025)**
- Title: **iv-crush-daily-options-bot**
- Venue: GitHub repository
- Readable URL: https://github.com/NOVESH-CREATE/iv-crush-daily-options-bot
- Repo URL: https://github.com/NOVESH-CREATE/iv-crush-daily-options-bot
- API metadata（抓取时间 2026-04-02 UTC）：
  - created_at: `2025-11-26T06:53:54Z`
  - pushed_at: `2025-11-26T07:36:50Z`
  - stars: `1`
- 核心文件：
  - `iv_crush_bot.py`
  - `app.py`

### B) 数据与执行接口（公开可得）
- Delta Exchange public API（无需私钥即可拉市场数据）
  - `GET /v2/products`
  - `GET /v2/tickers`
  - `GET /v2/history/candles`
- Readable URL（根域名）：https://api.delta.exchange

### C) 理论地基（定价与 Greeks 框架）
- Black, F., & Scholes, M. (1973). *The Pricing of Options and Corporate Liabilities*.
- Venue: *Journal of Political Economy*
- DOI: `10.1086/260062`
- Readable URL: https://doi.org/10.1086/260062

> 这里用经典文献只做“期权溢价/Greeks/时间价值”框架锚点；本轮 alpha 主证据仍是开源策略源码与交易所公开接口。

## 4. 从源码拆出来的可执行策略骨架

### 4.1 入场（repo 语义）
1. **IV spike 条件**
   - `ATM_IV >= rolling_IV * (1 + IV_SPIKE_PCT)`
   - 默认 `IV_SPIKE_PCT = 10%`
2. **流动性 sweep 条件**
   - 用 `1m` K 线 wick/body 判断扫单形态
3. **波动底线**
   - `ATM_IV >= 30`
4. 三者同时满足时触发入场候选

### 4.2 建仓
- 构建同到期 vertical credit spread（卖近 ATM，买保护腿）
- 默认保护宽度：`PROTECTION_WIDTH_PCT = 3%`
- 目标盈利：`TARGET_PROFIT_PCT = 40%`
- 最大持有：`MAX_TIME_MIN = 30`

### 4.3 仓位与风控
- 风险预算：`RISK_PER_TRADE_PCT = 1.5%`（按账户）
- `contracts = risk_amount / max_loss`
- 平仓触发：
  - 达到目标利润
  - 触及最大亏损
  - 超时（time exit）
  - 价格贴近关键 strike（near_strike）

### 4.4 这条策略为什么是 raw alpha（不是 overlay）
因为它的收益驱动是可交易的**期权定价偏离回归（IV overshoot 回落）+ 同日时间衰减**，确认层（sweep）只负责减少误入场。

## 5. 公开 API 最小快检（2026-04-02 09:3x UTC 即时采样）

### 5.1 合约可交易性（same-day）
- `BTC` 当日到期（`2026-04-02 12:00:00Z`）可见：
  - `34` 个 call
  - `34` 个 put
- 说明：同到期多 strike 结构足够做窄宽度 vertical，不是“只有孤点盘口”。

### 5.2 ATM 报价与 IV（示例：66400 附近）
- BTC spot 约 `66,458.6`
- `C-BTC-66400-020426`：bid/ask `199 / 234`，spread `35`，bid/ask IV `0.3828 / 0.4634`
- `P-BTC-66400-020426`：bid/ask `139 / 174`，spread `35`，bid/ask IV `0.3799 / 0.4605`

### 5.3 垂直 credit spread 的即时 R/R（200 点宽度示例）
- Call spread（short 66400 / long 66600）：
  - net credit ≈ `56`
  - max loss ≈ `144`
- Put spread（short 66400 / long 66200）：
  - net credit ≈ `40`
  - max loss ≈ `160`

### 5.4 sweep 稀疏度（BTCUSDT 1m）
- 最近 `60` 根 1m，按 `wick > 2*(body+5)` 口径：
  - sweep 约 `6/60`（`10%`）
- 说明：不是每根都触发，具备事件型 alpha 所需“稀疏入场”特征。

## 6. 与 1m / 3m / 5m / 15m 的映射
- **1m**：主触发层（IV spike + sweep）
- **3m**：确认层（避免单根假突破，要求 3m 内无反向强 sweep）
- **5m / 15m**：执行时段与风控层（只在到期前 `TTE <= 120m` 且波动/流动性达标时启用）

> 也就是说：alpha 本体是 options IV 回归；`3m/5m/15m` 主要承担确认、时段和风险治理。

## 7. 为什么它适合当前 desk（而且不重复）
1. 近期 intake 虽有大量 options stat-arb（box / parity / butterfly），但**“IV spike + sweep 的同到期 credit spread”**这条尚未作为主标题入池。
2. 该策略天生是**可完整落地**（entry/exit/sizing/risk/cost 结构齐全），符合本轮优先级最高档。
3. 数据全部公开可得，且可在 `1m/3m` 快速做前向验证，不依赖私有链上数据供应商。

## 8. 主要风险与失败模式
1. **盘口深度与滑点**：near-expiry spread 可能看起来有 edge，但净收益被 half-spread 吃掉。
2. **事件拥挤**：IV spike 后若继续爆波（不是 crush），short premium 会被 gamma 打穿。
3. **执行质量**：若不能稳定成交双腿，裸腿风险会显著放大。

## 9. 下一步怎么测（最小可复现实验）

### 实验目标
验证 `IV spike + sweep` 在 near-expiry 条件下是否具有正的净期望（扣成本后）。

### 数据源与公开性
- 数据源：Delta Exchange `products/tickers/candles`
- 公开性：公开可得
- 更新频率：秒级 ticker / 分钟级 candle

### 实验口径（先 paper，再小额）
1. 录 `7~14` 天 BTC 当日到期 options chain（每 `30~60s`）
2. 同步录 `1m` 标的 K 线，计算 sweep 与短 EMA 方向
3. 入场条件：
   - `IV_spike >= 10%`
   - `sweep = True`
   - 方向一致（上扫优先 put-credit，下扫优先 call-credit）
4. 出场规则：
   - `profit >= 40% credit` 或
   - `time >= 30m` 或
   - `loss >= 1.0x max_loss`
5. 成本模型（必须）：
   - 双腿 half-spread + taker fee + 撤单重挂惩罚
   - 压力测试：`base / +25% / +50%` 成本档
6. 评估：
   - 胜率、盈亏比、单笔期望、最大回撤
   - `1m` 触发 vs `3m` 确认版本的净值对比

### 首轮成败阈值（建议）
- 50+ 笔样本后，若在中性成本档仍 `expectancy > 0` 且 max drawdown 可控，进入二阶段（多标的 + 自动化下单）；否则降级为 execution filter，不作为独立 alpha。

## 10. 一句话结论
**这份 2025 新 repo 对 short-cycle desk 的真正价值，不是“期权 UI”，而是一条能在公开数据上快速复现、并且能直接写成完整交易规则的 event-driven options raw alpha：`near-expiry IV spike × 1m sweep → short vertical credit spread`。**

## 文件信息
- 文件路径：`research/quant_digests/2026-04-02_0936_ivspike-sweep-creditspread-options-alpha.md`
- 站点相对 URL：`/reading/quant_digests/2026-04-02_0936_ivspike-sweep-creditspread-options-alpha.html`
