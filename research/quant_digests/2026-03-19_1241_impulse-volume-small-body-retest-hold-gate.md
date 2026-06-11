# 别把 retest_hold 写成“碰到旧线就算守住”：`impulse-volume anchor + small-body retest` 更像 15m 的 hold-quality gate
- 时间：2026-03-19 12:41 UTC
- 类型：GitHub + 本地代理快检
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/retest/volume/body-ratio/hold-quality/confirmation/repo/crypto/5m/15m
- 证据类型：repo 代码规则（工程证据）+ 公开行情代理快检

## 1. 这次看了什么
这轮看的是 **wwakeford (2025) 的 `breakout-retest-backtest`**。我没有照搬它的“小时线美股水平阻力突破”整套框架，而是只抽出一个更适合当前 desk 的旁支：
**先用 breakout 那根的冲击量做锚，再要求 retest 那根是“小实体 + 缩量”，把它当成 hold-quality gate。**

仓库里这条线是显式写出来的：
- breakout：`close/高点` 真正站上水平位，且 `volume >= 2x avg volume`；
- retest：回到原 level 附近时，要求 `body_ratio <= 0.30`；
- 同时 `retest volume <= 0.5 * breakout volume`；
- 满足后才允许把这次 retest 当成有效入场。

## 2. 核心结论
1. **一句话核心结论**：对 15m 来说，`小实体 + 缩量 retest` 更像在回答“这次回踩是不是温和确认”，它更适合当 **hold-quality gate**，不是单独抬收益的主 alpha。  
2. **一句话证明方式**：repo 里把这条规则写成了明确阈值；我再用 Binance Futures 公开 15m K 线（BTC/ETH/SOL，各 1500 bars）做了 breakout→retest 代理快检，看过滤前后 `hold/reclaim` 有没有改善。  
3. 本地代理快检（20-bar breakout、EMA200 同向、未来 8 bars 内找 retest、触位后看 4 bars）结果：
   - 全样本 `hold4`：**44.9% -> 68.8%**（`107 -> 16`）
   - 全样本 `reclaim4`：**63.6% -> 75.0%**
   - 但 `win4` 没同步变强：**55.1% -> 50.0%**
4. 这说明它更像 **“别把 level 太快打穿” 的质量过滤器**，而不是“立刻把 4-bar 收益做大”的 continuation 加速器。
5. 短侧（更贴近 breakout-short follow-up）里，`hold4` 从 **49.1% 升到 85.7%**，但样本只有 `53 -> 7`，只能先记成有启发、不能记成定论。

## 3. 为什么和当前三条收口线直接相关
- **V3 final-verdict / breakout-short follow-up**：镜像到 short 侧后，它能把“下破后的上抽”区分成两类——若回抽 bar 仍是大实体、高成交量，更像反打；若是小实体、缩量回抽，才更像可继续 follow-up 的温和 retest。
- **Fibonacci confirmation / retest_hold**：这条最直接。Fib 回踩不是“碰到 0.5/0.618 就算守住”，而是要问：**回踩那根有没有 aggressive counterattack**。`body_ratio + retest_vol / impulse_vol` 正好在量化这件事。
- **EMA / PSAR raw alpha focus**：EMA/PSAR 继续管方向，这层只管 pullback 质量。也就是：方向层不改，entry admission 更诚实。

## 4. 下一步怎么测（5m / 15m 最小实验）
### 4.1 数据与公开性
- 数据源：Binance Futures 公共 K 线（`/fapi/v1/klines`）
- 公开性：公开可得
- 更新频率：5m / 15m
- 本轮代理快检产物：
  - `reports/artifacts/quant_digests/2026-03-19_breakout_retest_compression_proxy_events.csv`
  - `reports/artifacts/quant_digests/2026-03-19_breakout_retest_compression_proxy_summary.json`

### 4.2 最小可复现实验口径（建议）
把三条 archetype 都接一层同样的 retest gate：
1. 先定义 `impulse bar`（breakout / reclaim / EMA continuation 触发 bar）；
2. 记录 `impulse_volume`；
3. 若未来 `1~4` 根 15m 出现 retest：
   - `body_ratio <= 0.30`
   - `retest_volume / impulse_volume <= 0.50`
   - 可选再加 `5m reclaim close` 做真正触发
4. 对照 3 组：
   - A：baseline
   - B：`small-body only`
   - C：`small-body + vol-compression`（本轮主张）

先看 4 项：`hold4_rate`、`reclaim4_rate`、`false_break_ratio`、`post_cost_expectancy (6/10/15 bps per side)`。

## 5. 风险与保留意见
- 原仓库是 **小时线股票 breakout** 语境，不是 crypto 15m 成品模板；
- 本轮快检是事件级代理，不是完整策略回测；
- 过滤后样本显著变少，说明它更像“严 admission”，不是高频入场器；
- 如果后续发现它只提升 `hold/reclaim`、却持续伤害成本后收益，应把它降级为 **Fib / breakout 专属 gate**，不要硬推广成全局规则。

## 6. 来源
1. **wwakeford. (2025). _breakout-retest-backtest_.**
   - Venue: GitHub
   - DOI: N/A
   - Readable URL: <https://github.com/wwakeford/breakout-retest-backtest>
   - Repo URL: <https://github.com/wwakeford/breakout-retest-backtest>
2. **关键实现：`strategy.py`**
   - Readable URL: <https://github.com/wwakeford/breakout-retest-backtest/blob/main/strategy.py>
   - Raw URL: <https://raw.githubusercontent.com/wwakeford/breakout-retest-backtest/main/strategy.py>
3. **关键实现：`utils.py` + `config.py`**
   - `is_valid_retracement()`：`body_ratio <= 0.30` 且 `retest volume <= 0.5 * breakout volume`
   - Readable URL: <https://github.com/wwakeford/breakout-retest-backtest/blob/main/utils.py>
   - Readable URL: <https://github.com/wwakeford/breakout-retest-backtest/blob/main/config.py>
4. **公开行情数据源**
   - Binance Futures Klines API: <https://fapi.binance.com/fapi/v1/klines>
