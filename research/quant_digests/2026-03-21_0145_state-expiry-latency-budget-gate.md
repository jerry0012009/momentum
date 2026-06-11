# 别把确认层写成“可无限等待”：`confirmWindow + entryWindow` 双时窗 expiry，更像 15m breakout-short / Fib / EMA-PSAR 的 honest follow-up gate
- 时间：2026-03-21 01:45 UTC
- 类型：GitHub 仓库（代码规则审阅）
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/follow-up/confirmation/latency-budget/expiry/state-machine/filter/repo/crypto/5m/15m
- 证据类型：工程规则证据（源码可复核）

## 1) 这次为什么值得先写
这轮优先级直接服务三条收口线，而且比再堆一个新指标更紧急：
**我们最近反复碰到的是 `late retest / stale follow-up`——信号触发后拖太久才确认，最后把“过期路径”也当成同一笔 continuation。**

`CO0Ki3/smc-structure-ts` 这份 2026 新仓库里，最值得偷的旁支不是 SMC 名词本身，而是它把流程明确写成：
`SWEPT -> CONFIRMED -> ENTRY`，并且每一步都带**超时失效（expiry）**。

## 2) 看的来源
### Source A（主）
- **CO0Ki3 (2026). _smc-structure-ts_. GitHub repository.**
- Venue: GitHub
- DOI: `N/A`
- Readable URL: `https://github.com/CO0Ki3/smc-structure-ts`
- Repo URL: `https://github.com/CO0Ki3/smc-structure-ts`
- 关键代码：
  - `src/strategy/runStrategy.ts`
  - `src/strategy/types.ts`
  - `src/smc/structure.ts`

### Source B（补充对照）
- **yeboster (2026). _liquidity-sweep-freqtrade_. GitHub repository.**
- Venue: GitHub
- DOI: `N/A`
- Readable URL: `https://github.com/yeboster/liquidity-sweep-freqtrade`
- Repo URL: `https://github.com/yeboster/liquidity-sweep-freqtrade`

## 3) desk 版一句话结论
- **一句话核心结论：** 对 15m 来说，确认层最该先补的不是“再加一个更花的过滤器”，而是给 post-trigger 路径加**时间预算**：确认超时作废、入场超时作废。
- **一句话证明方式：** 主仓库把交易链写成显式状态机，并在源码里硬编码了 `sweep->confirm` 与 `confirm->entry` 两段 window 过期逻辑；这让“过期信号”不能偷偷混入同一类样本。

## 4) 最关键的数据点（来自源码默认参数）
1. `confirmWindowBars = 12`（15m 下约 3 小时）
2. `entryWindowBars = 24`（15m 下约 6 小时）
3. `timeoutBars = 288`（15m 下约 3 天）

补充：同一实现还把 `rr=2.0`、`feeBps=10`（round-trip）直接参数化，说明它默认就把“成本+超时”视为规则的一部分，不是事后补丁。

## 5) 对三条收口线的直接价值
- **V3 final-verdict / breakout-short follow-up**：
  把“破位后拖很久才出现的确认”剔除，可直接减少 stale continuation 假阳性。
- **Fibonacci confirmation / retest_hold**：
  Fib 回踩不是无限期有效；`signal->retest_hold` 也该有最大等待窗，否则会把结构变形后的回踩误算成同类样本。
- **EMA / PSAR raw alpha focus**：
  先不改 EMA/PSAR 本体，先加 `latency budget` 这层 honesty gate，通常比再调参数更便宜、更可审计。

## 6) 下一步怎么测（最小实验）
先不引入新因子，只测“时间预算”本身有没有增量：

- **实验对象**：现有三条 setup（breakout-short / fib_retest_hold / ema_psar_long）
- **固定项**：`BTC/ETH/SOL` perpetual，`15m`，`next-bar open`，`no-overlap`，成本 `6/10/15 bps per side`
- **三臂对照**：
  - `A`：无 expiry（当前口径）
  - `B`：仅 `confirmWindow`（例如 8/12/16 bars）
  - `C`：`confirmWindow + entryWindow`（例如 (8,16)/(12,24)/(16,32)）
- **先看 4 个指标**：
  1) `post_cost_expectancy`
  2) `failure_rate`（或 `tp_first` 对应失败侧）
  3) `trade_count_retention`
  4) `time-to-confirm` / `time-to-entry` 分布是否左移

若 `B/C` 只是靠极端砍单好看（retention 过低），就不升 shared gate；若 failure 下降且 retention 仍可接受，再进入下一轮。

## 7) 风险与保留意见
- 这是 repo 规则启发，不是已验证的跨市场论文结论；
- 源仓库是 SMC 语境，直接照搬名词会过拟合；我们只借“状态机 + expiry”框架；
- window 过严时很容易只剩稀疏样本，必须和 retention 联合审计，不能只看收益均值。

## 8) 本轮产物
- 研究笔记：`research/quant_digests/2026-03-21_0145_state-expiry-latency-budget-gate.md`

## 9) 来源
1. **CO0Ki3. (2026). _smc-structure-ts_. GitHub repository.**
   - Venue: GitHub
   - DOI: `N/A`
   - Readable URL: `https://github.com/CO0Ki3/smc-structure-ts`
   - Repo URL: `https://github.com/CO0Ki3/smc-structure-ts`
   - Key files:
     - `https://raw.githubusercontent.com/CO0Ki3/smc-structure-ts/main/src/strategy/runStrategy.ts`
     - `https://raw.githubusercontent.com/CO0Ki3/smc-structure-ts/main/src/strategy/types.ts`
     - `https://raw.githubusercontent.com/CO0Ki3/smc-structure-ts/main/src/smc/structure.ts`
2. **yeboster. (2026). _liquidity-sweep-freqtrade_. GitHub repository.**
   - Venue: GitHub
   - DOI: `N/A`
   - Readable URL: `https://github.com/yeboster/liquidity-sweep-freqtrade`
   - Repo URL: `https://github.com/yeboster/liquidity-sweep-freqtrade`
   - Key file: `https://raw.githubusercontent.com/yeboster/liquidity-sweep-freqtrade/main/README.md`

---
一句话收口：

**先把确认层从“无限等待”改成“有时效预算”，是当前 15m 三条收口线更值得优先做的一步诚实修复。**
