# 别把这份 2026 spread scanner repo 只读成 Telegram 报警器：对 short-cycle desk，更该先测的是「small-cap cross-venue perp BBO dislocation × fast close-out」这条 relative-value raw alpha
- 时间：2026-04-11 20:58 UTC
- 类型：GitHub
- 主题类型：raw alpha
- 基础 alpha：**同一标的 perpetual 在不同交易所的顶级盘口会因碎片化流动性、报价陈旧、symbol alias / 1000x 面值差异而短暂错位；可交易部分不是“任何价差”，而是 `same-asset cross-venue net spread > round-trip cost` 之后的快速回归。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha/relative-value/stat-arb/cross-venue/perpetuals/bbo/small-cap/symbol-normalization/staleness/liquidity-confidence/binance/hyperliquid/gate/1m/3m/5m/repo/public-data/cost/risk
- 证据类型：源码审计 + 公共 live-BBO portability probe

## 1. 这次看了什么
看了 `VadymManiuk/spreadfinder` 这个 2026 新仓库。表面上它只是一个 **Binance / Hyperliquid / Gate 三所 perp spread scanner + Telegram alerts**，但真正值得 desk 拿走的不是报警器外壳，而是它把一条 **same-asset cross-venue relative-value raw alpha** 拆得相当清楚：
- 先做 **symbol normalization**（含 `1000PEPE` / `kPEPE` 这类 1000x 面值归一）
- 再做 **顶级盘口 gross / net spread**
- 再用 **freshness / liquidity / volume / spread magnitude** 算置信度
- 最后用 **persistence + cooldown + stale veto** 过滤掉大部分假信号

这比“看见跨所价差就冲”成熟得多，也比我们此前看过的 majors 跨所壳更贴近 **small-cap / alias-heavy / quote-fragmented** 这条新素材线。

## 2. 核心结论
- **一句话核心结论：** 这份 repo 真正可迁移的，不是 Telegram 推送，而是它把「**同资产跨所 perp 顶级盘口错位 -> 价差回归**」写成了一条可拆解的 raw alpha；其中 freshness、盘口深度、24h 成交额和 alias/collision 处理，不是附属细节，而是 alpha 能不能活下来的主体条件。
- **一句话证明方式：** 结论来自源码拆解 + 三所公共实时盘口快检，而不是 README 宣传词。
- `spread_engine/calculator.py` 明牌给了核心定义：
  - `gross_spread = sell_bid - buy_ask`
  - `gross_spread_bps = gross_spread / buy_ask * 10000`
  - `net_spread = gross_spread - estimated_fees - estimated_slippage`
- 它不是只比价格，还专门处理了 **Binance `1000PEPE` / Hyperliquid `kPEPE` / Gate `PEPE`** 这类名义面值差异；若不做这个归一，很多“价差”其实只是合约单位不同导致的假象。
- `ticker_aliases.py` 还显式屏蔽了不少 collision ticker（如 `BEAM`、`NEIRO`、`AI`、`CAT`、`X`），这对小币跨所策略非常关键：**ticker 相同 ≠ underlying 相同**。
- `confidence.py` 把可执行性压成四个分量：`freshness 30%`、`liquidity 30%`、`volume 20%`、`spread magnitude 20%`。这其实已经在告诉我们：这条线不是“价差越大越好”，而是“**价差真实 + 书够厚 + quote 够新**”才值得上桌。
- 我做了一个三所公共 live-BBO 快检（`WLD/SEI/PYTH/CRV/SUI/FLOKI/TRUMP/PEPE/APE/LINK/ENA/ARB/WIF/BONK/LDO/JUP/TIA/APT/DOGE/NEAR` 共 `20` 个三所重叠标的）：
  - `15/20` 个标的当前最优跨所 gross spread 非负；
  - `6/20` 个达到 `>=5bps`；
  - `5/20` 个达到 `>=10bps`；
  - `1/20` 个达到 `>=20bps`。
- 当次快检 top 5：
  - `PEPE`: Gate 买 / Hyperliquid 卖，gross 约 `21.5bps`
  - `NEAR`: Gate 买 / Hyperliquid 卖，gross 约 `13.6bps`
  - `WLD`: Gate 买 / Hyperliquid 卖，gross 约 `13.4bps`
  - `ENA`: Gate 买 / Hyperliquid 卖，gross 约 `11.4bps`
  - `TRUMP`: Binance 买 / Gate 卖，gross 约 `10.5bps`
- 但按源码默认费率近似，若用 **taker 开两腿 + 把平仓成本也粗略预留进去**，Gate↔Hyperliquid 一笔 round-trip 粗成本大约已经在 `15bps` 左右量级；这意味着**不是所有 gross spread 都是 alpha，很多只是“看起来有肉、净后没肉”**。这正是这份 repo 比普通价差报警器更有用的地方。

## 3. 为什么和当前项目有关
当前 `momentum` 素材池里，跨所方向已经有 majors 的 maker/taker BBO 壳、same-expiry basis、funding/basis carry 等线，但 **small-cap perp 的 same-asset cross-venue dislocation** 还不够系统，尤其缺：
- **symbol normalization / collision veto** 这一层工程现实；
- **盘口新鲜度 + 深度 + volume** 这类可执行性评分；
- **不是 majors、而是 alt / meme / alias-heavy universe** 的 relative-value 录取框架。

这份 repo 正好补这块。它不是又一个“价差搬砖教程”，而是把 desk 真会踩到的坑——陈旧 quote、假同名、1000x 合约、薄书、过期机会——直接写进了 signal layer。

## 3.5 策略拆解（必填）
- 方向属性：**跨所 / same-asset / relative-value / stat-arb / 快速收敛型**
- 基础 alpha：**同标的 perp 在不同交易所的顶级盘口短时错位，会在 quote 刷新或套利者对齐后收敛**
- regime：更适合 **小币、交易所间上币节奏不一致、做市覆盖不均、局部流动性碎片化** 的环境；majors 上通常被更快压平
- filter / veto：
  - `data_age_ms <= 2000`
  - `persistence >= 1000ms`
  - 盘口最小深度 / 24h 成交额过滤
  - ticker collision / alias veto
  - gross spread 过大（源码里默认上限很宽，但逻辑上应视作坏数据或风控警报）
- risk / sizing / execution overlay：
  - 以更薄的一腿的 top-of-book size 做仓位上限
  - 按交易所对单独设定 fee ladder
  - 时间止损（如 `10s/30s/60s`）+ spread re-cross exit
  - 必须区分 `可开仓 gross` 与 `可平仓 net`

## 4. 可复刻的最小实验
- **研究假设：** 在 `1m/3m/5m` 的 crypto perp 里，真正可迁移的不是“跨所都有机会”，而是 **小币 / alias-heavy 标的在三所顶级盘口偶发失配后，是否存在足以覆盖 round-trip 成本的收敛 alpha**。
- **最小信号定义：**
  1. 对同 underlying 的三所 perp 做 canonical mapping；
  2. 每秒或每 `250~500ms` 记录最优 `buy_ask` 与 `sell_bid`；
  3. 当 `gross_spread_bps > fee_budget_bps + slippage_budget_bps + entry_buffer` 时记为候选；
  4. 仅保留 `data_age_ms <= 2000`、`min(book_size_usd) >= threshold`、`confidence >= 0.3`、`persistence >= 1000ms` 的样本。
- **最小数据口径：**
  - Binance USDⓈ-M: `fapi/v1/ticker/bookTicker` 或 websocket `@bookTicker`
  - Gate Futures: `futures.book_ticker` / REST tickers
  - Hyperliquid: `l2Book` + `/info`
  - 数据公开可得，更新频率可做到实时或近实时
- **最小可复现实验口径：**
  - 先不做真成交，先做 **paper fill**：入场按 `buy ask / sell bid`，出场按下一次 `spread <= exit_threshold` 或时间止损时的反向 BBO；
  - 先测 `PEPE / WLD / NEAR / ENA / TRUMP` 这类快检里出现 gross spread 的标的；
  - 先跑 `10s / 30s / 60s / 180s` 四档 holding window，再看 `1m/3m/5m` 聚合后是否还留边。
- **下一步怎么测：**
  1. 把 repo 的 alert book 改成事件日志：记录 `entry gross/net/confidence/data_age/sizes` 与 `exit re-cross time`
  2. 单独做 **fee realism sweep**：`maker/maker`、`taker/maker`、`taker/taker`
  3. 按标的分组：meme（`PEPE/BONK/FLOKI`）vs mid-cap（`WLD/ENA/ARB/NEAR`）
  4. 加上 funding 与 mark/index 偏离，区分“纯盘口错位”还是“风险转移导致的合理价差”
  5. 若 `>=10bps` gross 只在极薄书才出现，就把它降级成 **execution-viability gate**，不要硬说是稳定 raw alpha

## 5. 风险与保留意见
- 这份 repo **没有 execution / hedge / close-out engine**，只有 alerting；所以它更像 raw alpha 候选与研究抓手，不是可直接上 production 的完整策略。
- README 里的默认阈值（如 `MIN_GROSS_SPREAD_BPS=10`, `MIN_NET_SPREAD_BPS=5`）与 `config/settings.py` 里的默认值（`50bps / 100bps`）并不一致，说明项目还在快速演化，参数可信度不能照单全收。
- `estimated_fees` 和 `slippage` 都是粗估，对 small caps 来说真实冲击成本可能显著更高；如果没有更细的盘口深度与成交回放，净值预估会偏乐观。
- 这条线最怕的不是“没有 spread”，而是 **spread 来自坏数据、合约差异、ticker 误配、或一腿根本吃不掉**。因此 alias/collision 与 freshness 不是文书工作，而是策略主体。
- 从我们这次 live 快检看，**gross spread 常见，但真正越过 round-trip net 门槛的不算多**；这意味着它更适合作为 **高筛选、低频次、事件驱动的 relative-value book**，而不是全时段不停打。

## 6. 来源
- admin. (2026). *Spread Scanner Bot / spreadfinder*. GitHub repository.
- Repo URL: `https://github.com/VadymManiuk/spreadfinder`
- README: `https://github.com/VadymManiuk/spreadfinder/blob/main/README.md`
- Spread calculator: `https://github.com/VadymManiuk/spreadfinder/blob/main/spread_engine/calculator.py`
- Confidence scoring: `https://github.com/VadymManiuk/spreadfinder/blob/main/spread_engine/confidence.py`
- Filters: `https://github.com/VadymManiuk/spreadfinder/blob/main/filters/opportunity_filters.py`
- Exchange adapters: `https://github.com/VadymManiuk/spreadfinder/tree/main/exchange_adapters`
- Symbol aliases / collision map: `https://github.com/VadymManiuk/spreadfinder/blob/main/symbol_mapper/ticker_aliases.py`
- Repo latest commit seen locally: `bb62a570d8262fd437614c924a3e583cfc43a54e` (`2026-04-11 15:46:50 +0300`)
- 本地 public live probe：Binance USDⓈ-M `bookTicker`、Gate futures tickers、Hyperliquid `l2Book` / `metaAndAssetCtxs`，2026-04-11 UTC 当次快照，重叠标的 `20` 个，用于验证三所同资产 perp BBO 可得性与 gross spread 分布；**不代表历史回测结果**
