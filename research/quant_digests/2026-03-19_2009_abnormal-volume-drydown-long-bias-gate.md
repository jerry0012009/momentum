# 别把 volume confirmation 只盯着放量：`3-step volume dry-down` 更像 Fib retest / EMA continuation 的 long-side hold-quality gate
- 时间：2026-03-19 20:09 UTC
- 类型：GitHub + 本地代理快检
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/volume/abnormal-volume-loss/decreasing-volume/pullback/long-bias/asymmetry/repo/crypto/15m
- 证据类型：repo 规则（工程证据）+ 公开行情代理快检

## 1. 这次看了什么
这轮看的是 **800cherries (2023) 的 `Tradingview-Indicators` repo** 里那条之前没被我们单独拎出来的旁支：**Abnormal Volume Scanner**。

我没把它读成“又一个放量突破指标”，而是只抽了更适合当前 desk 的分支问题：

> 对 `Fib retest_hold / EMA-PSAR continuation` 来说，真正更值钱的也许不是 breakout 当根放量，
> 而是**回踩阶段先出现 3 根递减成交量（每根衰减约 5%~30%）+ 低于 20-bar 均量的 dry-down**，再看 reclaim 是否更干净。

repo 里直接给了这条思路的规则骨架：
- `abnormalVolSpikeCandles = 3`
- `abnormalVolSpikeMultiplier = 0.4`
- `abnormalVolLoss`
- `decreasingVolume`
- `consecutiveCandlesLimit = 3`
- `minVolChange = 5%`
- `maxVolChange = 30%`

## 2. 核心结论
1. **一句话核心结论**：对 15m 而言，`3-step volume dry-down` 更像 **long-side retest/continuation 的 hold-quality gate**，不是 breakout-short 可镜像复用的 shared trigger。  
2. **一句话证明方式**：复用本地 `BTC/ETH/SOL 120d 15m` cache，做一个最小 `EMA10>EMA40 + touch/reclaim EMA10` 代理；统一 `next-bar open` 入场、`hold 8 bars`、`no-overlap`、`6bps/side`，比较 `baseline / low-volume-only / dry-down-only / dry-down+low-volume`。  
3. 关键数据（long side）：
   - `baseline`：`avg_net_ret_h8 = -0.117%`，`win_rate = 38.4%`
   - `low-volume-only (lv80)`：`-0.106%`，说明**只看低量还不够**
   - `dry-down + low-volume (dv3_lv80)`：`+0.001%`，`win_rate = 48.1%`，但 `retention = 3.4%`
4. 跨资产上，`dv3_lv80` 不是全面翻正，但已经从全负改善到 `2/3` 资产为正：
   - ETH：`+0.205%`
   - SOL：`+0.017%`
   - BTC：`-0.229%`
5. **短侧镜像是坏的**：short baseline 只有 `-0.070%`，镜像后的 `dv3_lv80` 反而恶化到 `-0.247%`，`win_rate` 也掉到 `26.2%`。这条线更像 **breakout-short 的 short veto**，不是 short admission。

## 3. 为什么它直接服务当前三条收口线
- **Fibonacci confirmation / retest_hold（最直接）**：它把“缩量回踩”从一句经验话，压成可审计规则：`3 根递减量 + low-volume budget`。  
- **EMA / PSAR raw alpha focus**：它回答的是 continuation 里最难的一层——**什么样的回踩像吸收，什么样的回踩只是没人接**。  
- **V3 breakout-short follow-up / final verdict**：这轮最有价值的不是给 short 再加一个 trigger，而是明确告诉我们：**不要把 long-side dry-down 逻辑直接镜像到 short**。

如果问“为什么这题比继续补已有近义 gate 更值”：因为最近几轮更偏向 **breakout bar / retest bar 本身质量**，这轮补的是更前面的 **pullback participation decay**，而且它正好呼应学习地图里一直高优先级的 `volume spike + 缩量回调`。

## 4. 下一步怎么测（5m / 15m 最小实验）
### 4.1 数据与公开性
- 数据源：Binance Futures 公共 K 线（本轮复用本地 cache）
- 公开性：公开可得
- 更新频率：5m / 15m
- 本轮产物：
  - `reports/artifacts/quant_digests/abnormal_volume_pullback_proxy/trade_log.csv`
  - `reports/artifacts/quant_digests/abnormal_volume_pullback_proxy/overall_summary.csv`
  - `reports/artifacts/quant_digests/abnormal_volume_pullback_proxy/asset_summary.csv`
  - `reports/artifacts/quant_digests/abnormal_volume_pullback_proxy/summary_snapshot.json`

### 4.2 最小可复现实验口径
下一轮别把它当 shared trigger，改成 **分线测试**：
1. **Fib retest_long**：只有在 `drydown_score` 过门（过去 3 根量递减，且 `mean(vol[-3:-1]) < 0.8 * vol_sma20`）时，`0.5/0.618` reclaim 才允许入场；
2. **EMA/PSAR continuation long**：把 `drydown_score` 放到 reclaim 前的 `armed state`，而不是触发后补刀；
3. **breakout-short**：不要拿它当 short confirm，只测成 `short_veto`（若反弹阶段出现 long-style dry-down，则降低 short size / 直接不做）。

先看 4 个指标：
- `post_cost_expectancy`
- `trade_count_retention`
- `flip_to_fail_3bars_rate`
- `stopout_rate`

## 5. 风险与保留意见
- 源 repo 是通用 TradingView 工具，不是专为 crypto 15m 设计；
- 本轮是代理快检，不是完整 OOS 策略回测；
- `dv3_lv80` 的保留率只有 `3.4%`，很可能过于稀疏，后续应先扫 `2-bar / 3-bar`、`0.8 / 0.9` 两组松紧度；
- 当前结果更像在提示 **long-side absorption**，不代表它能直接迁移到所有币、所有 regime。

## 6. 来源
1. **800cherries. (2023). _Tradingview-Indicators_.**
   - Venue: GitHub
   - DOI: N/A
   - Readable URL: <https://github.com/800cherries/Tradingview-Indicators>
   - Repo URL: <https://github.com/800cherries/Tradingview-Indicators>
2. **Abnormal Volume Scanner（Pine Script）**
   - 关键规则：`abnormalVolLoss`、`decreasingVolume`、`consecutiveCandlesLimit=3`、`minVolChange=5%`、`maxVolChange=30%`
   - Readable URL: <https://github.com/800cherries/Tradingview-Indicators/blob/main/indicators/Abnormal%20Volume%20Scanner>
   - Raw URL: <https://raw.githubusercontent.com/800cherries/Tradingview-Indicators/main/indicators/Abnormal%20Volume%20Scanner>
3. **仓库元数据（stars / created_at / pushed_at）**
   - URL: <https://api.github.com/repos/800cherries/Tradingview-Indicators>
4. **公开行情数据源**
   - Binance Futures Klines API: <https://fapi.binance.com/fapi/v1/klines>
