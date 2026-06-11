# 别把 Ichimoku 只读成“云图确认系统”：对 short-cycle crypto desk，更该先拆的是「Tenkan/Kijun cross」这条 trend raw alpha，到底是可交易延续，还是手续费陷阱
- 时间：2026-04-21 15:48 UTC
- 类型：GitHub / repo source audit + Binance USDⓈ-M public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：当 `Tenkan-sen`（近 9 根高低点中线）上穿/下穿 `Kijun-sen`（近 26 根高低点中线）时，市场短趋势可能进入一段新的延续；`close vs Kijun` 只是更慢、更钝的同族变体，不是另一条独立 alpha
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：trend / momentum / ichimoku / tenkan / kijun / crossover / Binance / 15m / 5m
- 证据类型：repo 明确规则 + public-data first probe

## 1. 这次看了什么
这次看的不是论文，而是 **reuniware (repo created 2021, updated 2026), CryptoForex-Trader-Framework** 里两份把 Ichimoku 规则写得很直白的脚本：
- `Binance_Backtest_BTCUSDT_ICHIMOKU_TS_KS_CROSS.py`：`Tenkan` 上穿 `Kijun` 做多，下穿做空
- `Binance_Backtest_BTCUSDT_ICHIMOKU_KS.py`：`close` 上穿 `Kijun` 做多，下穿做空

这类材料对我们 desk 的价值，不在“Ichimoku 很经典”，而在它把一条**可直接复刻、无需额外外部数据**的 trend raw alpha 壳写得足够清楚，适合拿来做 `5m/15m` 最小实验。来源：
- Authors / Year / Title / Venue / DOI：`reuniware / 2021-2026 / CryptoForex-Trader-Framework / GitHub repo / N/A`
- Repo URL: <https://github.com/reuniware/CryptoForex-Trader-Framework>
- GitHub API metadata: <https://api.github.com/repos/reuniware/CryptoForex-Trader-Framework>
- Readable URL: <https://github.com/reuniware/CryptoForex-Trader-Framework>
- TS/KS cross code: <https://raw.githubusercontent.com/reuniware/CryptoForex-Trader-Framework/main/Binance_Backtest_BTCUSDT_ICHIMOKU_TS_KS_CROSS.py>
- Kijun cross code: <https://raw.githubusercontent.com/reuniware/CryptoForex-Trader-Framework/main/Binance_Backtest_BTCUSDT_ICHIMOKU_KS.py>
- Kijun/Tenkan helper: <https://raw.githubusercontent.com/reuniware/CryptoForex-Trader-Framework/main/Binance_Calculate_Kijun_Tenkan.py>

## 2. 核心结论
- **一句话核心结论：**这篇东西的 base alpha 很明确，就是 **短窗中线 `Tenkan` 与中窗中线 `Kijun` 的方向切换**；但把它直接搬到 Binance USDⓈ-M liquid majors 的 `15m/5m` 后，**裸跑 gross 只有一点点趋势味，net 基本全被成本吃掉**。
- 更具体地说：在我用 `BTC/ETH/SOL/BNB/XRP/DOGE/ADA/LTC` 做的 quick probe 里，`Tenkan/Kijun cross` 比 `close/Kijun cross` 更像真正的 base alpha；后者基本只是更频繁、更钝、更容易磨损的慢信号。
- `Tenkan/Kijun cross` 的最好 pocket 出现在 **`5m` 多头持有 `8` 根**：8 币平均 **gross `+2.30 bps/笔`**，而且 **8/8 symbols** 都是正 gross；但若粗扣 `4 bps` round-trip，仍是 **net `-1.70 bps/笔`**。
- `15m` 也没过线：`Tenkan/Kijun` 空头持有 `4` 根时平均 **gross `+0.69 bps/笔`**，但扣成本后 **net `-3.31 bps/笔`**；多头侧整体更弱。
- `close/Kijun cross` 更差：例如 `15m` 多头持有 `8` 根虽有 **gross `+2.42 bps/笔`**，但 net 仍 **`-1.58 bps/笔`**；说明 **同一套 Ichimoku 里，真正值得继续保留的是 `Tenkan/Kijun` 这层 faster directional state，而不是 price-vs-Kijun 的慢翻面。**

## 3. 为什么和当前项目有关
这条线对 `momentum` 项目有两个直接价值：
1. **它是标准 raw alpha，不是解释型 overlay。** 只用 OHLCV 就能生成方向信号，适合快速进入素材池。
2. **它很适合做 parent/child 拆层。** `Tenkan/Kijun` 本身像 `15m` 或 `5m` 的 parent direction；真正需要补的是更便宜的 child trigger、regime gate、maker-first execution，而不是再去争论 Ichimoku 画得漂不漂亮。

换成人话：`Tenkan` 就是“更快的短期均衡价”，`Kijun` 是“更慢一点的中期均衡价”。快线刚翻到慢线上面，本质上是在说：**过去 9 根的中枢，刚把过去 26 根的中枢顶上去了。** 这确实可能意味着趋势开始，但在短周期里，它也非常容易变成“大家都已经看到了，所以你追进去后只剩手续费”。

## 3.5 策略拆解（必填）
- 方向属性：顺势 / 趋势切换
- 基础 alpha：`Tenkan-sen` 上穿 `Kijun-sen` 做多，下穿做空
- 同族慢变体：`close` 上穿/下穿 `Kijun`
- regime：repo 原版没有独立 regime 层
- filter / veto：repo 原版几乎没有；这恰好也是它最容易失血的地方
- risk / sizing / execution overlay：repo 示例脚本只有最简 all-in 切换与手续费扣减，没有认真做 `time-stop / volatility veto / size schedule / maker-first admission`

## 4. 可复刻的最小实验
### 4.1 本轮实验口径
- 数据源：Binance USDⓈ-M 公共 K 线 API，公开可得
- universe：`BTCUSDT/ETHUSDT/SOLUSDT/BNBUSDT/XRPUSDT/DOGEUSDT/ADAUSDT/LTCUSDT`
- 频率：`15m`（近 `45d`）、`5m`（近 `30d`）
- 入场：信号确认后的**下一根开盘**
- 出场：固定持有 `1/2/4/8` 根，对照 forward-return 厚度
- 成本：粗扣 `4 bps` round-trip

### 4.2 关键结果：Tenkan/Kijun cross（主角）
- `5m` 多头持有 `8` 根：合计 `1746` 笔，8 币平均 **gross `+2.30 bps/笔`**，**8/8 币**为正 gross，但 net 仍 **`-1.70 bps/笔`**。
- `5m` 多头持有 `4` 根：合计 `1746` 笔，平均 **gross `+1.40 bps/笔`**，net **`-2.60 bps/笔`**。
- `15m` 空头持有 `4` 根：合计 `921` 笔，平均 **gross `+0.69 bps/笔`**，net **`-3.31 bps/笔`**。
- `15m` 多头侧整体偏弱：`1/2/4/8` 根平均 gross 分别约 `-2.58 / -3.45 / -4.22 / -2.50 bps`。

### 4.3 关键结果：close/Kijun cross（慢变体，对照组）
- `15m` 多头持有 `8` 根：合计 `1875` 笔，平均 **gross `+2.42 bps/笔`**，但 net **`-1.58 bps/笔`**。
- `5m` 空头持有 `2` 根：合计 `3673` 笔，平均 **gross `+0.73 bps/笔`**，net **`-3.27 bps/笔`**。
- 其余大多围绕 `0 bps` 附近来回抖，说明它更像“慢速确认线”，不像可直接拿来吃短周期肉的主信号。

### 4.4 first verdict
- **若硬问 raw alpha 是什么：**答案就是 `Tenkan/Kijun cross continuation`。
- **若硬问它现在能不能裸上：**不能。它有一点 gross 厚度，但还不够厚到自己盖住 taker 成本。
- **若问这轮应保留谁：**保留 `Tenkan/Kijun`，把 `close/Kijun` 降级成 filter / state confirmation 候选。

## 5. 下一步怎么测
1. **先做 parent/child 拆层，不要再裸跑。**
   - parent：`15m` 或 `5m` 的 `Tenkan/Kijun` 方向
   - child：`1m/3m/5m` 的 pullback re-entry、micro breakout、或 maker-first queue placement
   - 目标不是提高 gross signal 数，而是把 entry 从“翻线即追”改成“方向先定，触发更便宜”
2. **给它补一个最小 veto。**
   - 只在 `ATR percentile` 不太低时启用，避免低波动磨损
   - 或只在 `quote volume z-score > 0` 时启用，避免没人交易时的假翻线
3. **把多空拆开，不要混。**
   - 当前 probe 显示 `15m` 空头略好，`5m` 多头略好；下一轮应直接做 `bull-only`、`bear-only`、`symbol pocket` 三组 A/B
4. **做 maker/taker 成本阶梯。**
   - 现在最强 pocket 也只有 gross `+2.30 bps/笔`，所以必须测 `0 / 1 / 2 / 4 bps`
   - 如果连 `1~2 bps` 都盖不住，就别把它当主 alpha，只能当方向层
5. **和已有 raw alpha 组合，而不是单打独斗。**
   - 最自然的搭法：`Tenkan/Kijun` 决定方向，`breakout / pullback / volume spike` 决定是否真正进场
   - 也就是把它从“交易信号本体”改成“趋势 parent state”

## 6. 风险与提醒
- 这是 **repo-based first probe**，不是 admission 级回测；它只告诉我们“这条 raw alpha 在短周期有没有肉”，还没做到资金曲线级别验证。
- 当前实验只看公共 K 线 forward returns，没有吃到真实盘口、排队、滑点与 funding；所以 gross 这么薄时，实盘只会更难。
- 这轮最重要的认知不是“Ichimoku 没用”，而是：**Ichimoku 里真正像 alpha 的部分只有快慢中线切换；但如果没有更便宜的 execution 和更严的 veto，它在 `5m/15m` 上很容易沦为手续费陷阱。**

## 7. 本轮产物
- `reports/artifacts/quant_digests/2026-04-21_ichimoku_tk_cross_probe.py`
- `reports/artifacts/quant_digests/2026-04-21_ichimoku_tk_cross_probe_summary.csv`
- `reports/artifacts/quant_digests/2026-04-21_ichimoku_kijun_cross_probe.py`
- `reports/artifacts/quant_digests/2026-04-21_ichimoku_kijun_cross_probe_summary.csv`
- `reports/artifacts/quant_digests/2026-04-21_ichimoku_cross_variant_comparison.csv`
