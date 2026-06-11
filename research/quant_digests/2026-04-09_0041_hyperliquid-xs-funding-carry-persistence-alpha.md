# Hyperliquid 小时 funding 排名，不只是看榜：它更像一条 `XS carry` 原始 alpha
- 时间：2026-04-09 00:41 UTC
- 类型：GitHub / 数据型仓库
- 主题类型：raw alpha
- 基础 alpha：`trailing-24h funding rank × next-4h/24h funding persistence`，以 delta-neutral carry 方式兑现
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：carry / funding / cross-sectional / relative-value / delta-neutral / Hyperliquid / hourly / liquidity
- 证据类型：工程经验 + 公共数据快检

## 1. 这次看了什么
看的是 GitHub 仓库 `exo-trading/crypto-carry-screener`。虽然 README 几乎没写内容，但源码里很明确：`market_data_collector.py` 直接从 Hyperliquid `fundingHistory` 和 `candleSnapshot(1h)` 拉全市场小时 funding 与成交额，`docs/script.js` 再把最新值与 `1d/3d/5d/30d` 年化 funding、`isNew/isDelisted` 等状态做成 screener。

## 2. 核心结论
- 这东西最值得拿来做的，不是“看谁 funding 高”，而是 **做小时级横截面 carry 排名**：挑持续最贵的 perp 去做 `short perp + long spot`，挑持续最便宜的 perp 去做 `long perp + short spot`。
- 我用 repo 自带的 `funding_data_all_coins.csv`（229 币，2026-01-09~2026-04-09）和 `ohlcv_data_main.csv` 做了本地快检；在有成交额数据的公共窗口（2026-03-12~2026-04-08）里，若只保留 **24h ADV 前 10** 且至少有 `72h` 历史的名字，再按 `24h 平均 funding` 做 top/bottom 20% 分桶：
  - top bucket 的 trailing funding 约 **+1096.9 bps 年化**；
  - bottom bucket 约 **-2807.9 bps 年化**；
  - 等权 `long bottom + short top` 的 **未来 funding spread** 约为：`+0.41 bps / 1h`、`+1.70 bps / 4h`、`+3.50 bps / 8h`、`+10.69 bps / 24h`。
- 更关键的是它不是“一次性跳点”而是 **会持续**：top bucket 未来 `4h/24h` funding 继续为正的比例约 **97.4% / 99.4%**，bottom bucket 继续为负的比例约 **76.7% / 97.4%**。
- 但容量并不对称：正 funding 那边的 top bucket 平均 `24h ADV` 只有约 **$6.88m**，负 funding 那边约 **$18.26m**。这说明它更像 **可做的小型 carry sleeve**，不是无限加码的大容量主引擎。

## 3. 为什么和当前项目有关
这条线和 desk 当前目标直接相关，因为它补的是 **carry / funding** 这一类可独立复现的 raw alpha，而不是又一个趋势过滤器。它的好处是：
- 不依赖复杂标签，公开 API 就能拿；
- 信号频率天然是小时级，但完全可以在 `1m/3m/5m/15m` 上做分批入场、冲击控制和 funding boundary execution；
- 后续还能和 basis、OI、liquidation、borrow/spot availability 叠成更完整的 relative-value 书。

## 3.5 策略拆解（必填）
- 方向属性：横截面 / 相对价值 / carry
- 基础 alpha：`24h funding mean rank` 本身，而不是价格方向
- regime：优先在 funding 符号稳定、近 `4~24h` 持续性高时开机
- filter / veto：`24h ADV`、新币排除、极端 premium 偏离、spot 不可借/借币太贵 veto
- risk / sizing / execution overlay：delta-neutral 对冲；按 `min(ADV, funding edge)` 缩放；在 funding 时点前后用 `5m/15m TWAP` 分批进出；设置 sign-flip / edge-decay / time-stop

## 4. 可复刻的最小实验
- 研究假设：**小时 funding 的横截面极值具有 4~24h 持续性，可支撑一条小容量 delta-neutral carry 书。**
- 可计算定义：每小时对可交易币计算 `fund24h_mean`，在流动性前 10~15 名里做 top/bottom 20% 分桶；记录未来 `1/4/8/24h` 累积 funding。
- 最小回测切口：Hyperliquid 全市场小时 funding + 小时成交额；交易层先用 `15m` 切片模拟 `short rich perp + long spot` / `long cheap perp + short spot`。
- 先看两项指标：
  1. `post-fee future funding bps`；
  2. `sign persistence` 与 `edge decay half-life`。

## 5. 风险与保留意见
- 这篇东西的主证据目前还是 **funding 持续性**，不是完整净收益回测；要正式进 desk，必须补上现货借贷/借币成本、maker/taker 费用、冲击和可借券约束。
- Hyperliquid 的高 funding 名单里会混入容量偏小的币，容量约束比表面看起来更严。
- 负 funding 端虽然更肥，但未必总能低成本做 `long perp + short spot`；借券与融币条件会决定能不能把“看起来很肥”真的吃到嘴里。

## 6. 来源
- exo-trading. (2025/2026). *crypto-carry-screener*. GitHub.
- Repo URL: `https://github.com/exo-trading/crypto-carry-screener`
- Readable URL: `https://github.com/exo-trading/crypto-carry-screener`
- Key source files:
  - `https://raw.githubusercontent.com/exo-trading/crypto-carry-screener/main/market_data_collector.py`
  - `https://raw.githubusercontent.com/exo-trading/crypto-carry-screener/main/docs/script.js`
  - `https://raw.githubusercontent.com/exo-trading/crypto-carry-screener/main/funding_data_all_coins.csv`
  - `https://raw.githubusercontent.com/exo-trading/crypto-carry-screener/main/ohlcv_data_main.csv`
