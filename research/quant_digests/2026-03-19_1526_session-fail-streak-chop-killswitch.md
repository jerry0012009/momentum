# 别把“连续确认失败”想成自动救命阀：`session fail-streak` 在 15m 更像 setup-specific 风险覆盖层，不是三线共享 kill-switch
- 时间：2026-03-19 15:26 UTC
- 类型：GitHub + 本地代理快检
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/chop/failure-streak/session-overlay/risk-overlay/execution-veto/repo/crypto/15m
- 证据类型：repo 规则（工程证据）+ 公开行情代理快检

## 1. 这次看了什么
这轮看的是 **Powersup8 (2026) 的 `KeyLevelBreakout`**。我没有复刻它整套美股 level 框架，而是只抽一个更适合我们 desk 的旁支：
**当同一 session 内连续出现确认失败（`confFailStreak`）时，后续信号是否该降级/停手。**

repo 原文里有两条很关键的提示：
- `Chop Day Warning (3+ CONF fails)`
- 以及“afternoon signals are net negative”这类时段性退场提醒。

把它翻成我们 5m/15m 语言，就是一句话：
**别只看单笔信号的形状；还要看“这段时窗里你是不是已经连续做错了”。**

## 2. 核心结论
1. **一句话核心结论**：`session fail-streak` 作为“共享 kill-switch”在当前 15m 三线代理上几乎不触发，直接上主线价值很弱；它更像要做成 **setup-specific / side-specific** 的风险覆盖层。  
2. **一句话证明方式**：我复用本地 `BTC/ETH/SOL 120d 15m` cache，沿用三条 archetype（`breakout_short / fib_retest_long / ema_psar_long`）信号骨架，统一 `next-bar open + hold 8 bars + no-overlap`，比较 baseline 与 fail-streak overlay。  
3. 关键数据（`6bps/side`）：
   - **8h session、按 repo 原味 `3+ fail`**：几乎不触发；`retention=100%`，`mean_total_return=-1.97%`（与 baseline 基本一致）。
   - **放宽到 24h session + `2 fail veto`**：只拦到 `0.81%` 信号（`retention=99.19%`），整体 `mean_total_return` 反而 `-1.97% -> -1.98%`，无共享增益。
   - setup 分解（24h + fail2_veto）：`ema_psar_long -3.55% -> -3.14%`（略好），但 `breakout_short -3.55% -> -3.99%`（变差），`fib_retest_long` 基本不变（`+1.18%`）。
4. 这说明当前更诚实的读法不是“全 desk 一个 fail-streak 总闸门”，而是：
   - **EMA/PSAR continuation** 可能能吃到一点保护；
   - **breakout-short follow-up** 可能被误伤（该做反向或单独阈值）；
   - **Fib retest_hold** 对这类 session 计数不敏感。

## 3. 为什么和当前三条收口线直接相关
- **V3 final-verdict / breakout-short follow-up**：这条最需要“何时停手”，但共享 fail-streak 会把 short 侧优劣行情混在一起，导致该停不停、该做反而停。  
- **Fibonacci confirmation / retest_hold**：Fib 本身触发更稀、确认更结构化，直接套共享 fail-streak 没有明显增益。  
- **EMA / PSAR raw alpha focus**：EMA/PSAR 有一定“连错后降级”需求，但阈值需要按 setup 单独校准，而不是共享硬门。  

如果要回答“为什么这题值得做而不是换题”：因为它直接回答三条线共同的执行痛点——**连错后怎么处理**，且可以用公开数据快速复现。

## 4. 下一步怎么测（5m / 15m 最小实验）
### 4.1 数据与公开性
- 数据源：Binance Futures 公共 K 线（本轮复用本地 cache）
- 公开性：公开可得
- 更新频率：5m / 15m
- 本轮产物：
  - `reports/artifacts/quant_digests/session_fail_overlay_proxy/candidate_events.csv`
  - `reports/artifacts/quant_digests/session_fail_overlay_proxy/trade_log.csv`
  - `reports/artifacts/quant_digests/session_fail_overlay_proxy/asset_summary.csv`
  - `reports/artifacts/quant_digests/session_fail_overlay_proxy/overall_summary.csv`
  - `reports/artifacts/quant_digests/session_fail_overlay_proxy/by_setup_summary.csv`
  - `reports/artifacts/quant_digests/session_fail_overlay_proxy/summary_snapshot.json`

### 4.2 最小可复现实验口径（建议先做这个）
下一轮不要再测“共享 fail-streak”，改测 **setup-specific fail budget**：
1. 对每条线单独维护 `fail_count_{setup}`（只在该 setup 触发后更新）；
2. 三臂对照：
   - A：baseline
   - B：shared fail2 veto（当前失败基线）
   - C：setup-specific fail2 veto / half-size（主测试）
3. 再做 long/short 分侧阈值（尤其 `breakout_short` 单独阈值）。

先看 4 个指标：
- `post_cost_expectancy`
- `trade_count_retention`
- `flip_to_fail_3bars_rate`
- `setup-wise contribution`（避免单 setup 改善掩盖整体退化）

## 5. 风险与保留意见
- 源 repo 面向美股时段（含 premarket/afternoon 语义），直接迁移到 24/7 crypto 有结构偏差；
- 本轮“确认失败”定义是代理口径（`3-bar flip-to-fail` + early pass），不是 repo 完整 retest 状态机；
- 当前结果说明共享 fail-streak 不够强，不代表“连错管理”无效，只代表**共享门**这版不够好；
- 若下一轮 setup-specific 仍无提升，应把它降级为可选执行保险丝，避免继续占主资源位。

## 6. 来源
1. **Powersup8. (2026). _KeyLevelBreakout_.**
   - Venue: GitHub
   - DOI: N/A
   - Readable URL: <https://github.com/Powersup8/KeyLevelBreakout>
   - Repo URL: <https://github.com/Powersup8/KeyLevelBreakout>
2. **关键实现（Pine）**：`i_chopWarn`、`confFailStreak`、`3+ CONF fails` 相关逻辑
   - Readable URL: <https://github.com/Powersup8/KeyLevelBreakout/blob/main/KeyLevelBreakout.pine>
   - Raw URL: <https://raw.githubusercontent.com/Powersup8/KeyLevelBreakout/main/KeyLevelBreakout.pine>
3. **公开行情数据源**
   - Binance Futures Klines API: <https://fapi.binance.com/fapi/v1/klines>
