# Rank 320 — P2 admission（honesty / execution realism + post-cost effectiveness）：keep_P2

- Time: 2026-04-04 02:26 UTC
- Target: `Rank 320 / Wilder RSI breakout × EMA200/ADX/volume allow × fast RSI-45 exit`
- Action type: `Active P2` admission step 1
- Verdict: `keep_P2`

## 结论
`Rank 320` 在更诚实的执行现实检验下没有暴露出“优势主要来自理想 friction 幻觉”的致命问题：基于上一轮已确认的最佳 short-cycle admission 路径，按现有 artifact 反推的 **单笔可再承受额外 round-trip friction 缓冲**，`15m` 三币约还有 `58~92 bps/笔`，`5m` 的 `ETH/SOL` 约还有 `50~62 bps/笔`，连最薄的 `BTC 5m` 也仍有约 `24.5 bps/笔` 的余量；这说明它即使放进比现有 `10bps fee + 5bps slippage + scaled funding` 更保守的 mixed / taker-ish 口径，核心路径大概率仍保留正 expectancy，因此本轮应把它留在 `P2` 继续做后续 admission，而不是因为“也许执行后会塌”直接降回背景池。

## 本轮怎么做的
本轮不重复 asset/timeframe 结论，而是只回答 policy 要求的 `honesty / execution realism + post-cost effectiveness`：
1. 读取上一轮 `survivor -> P2` 已确认的 best-path artifact：
   - `reports/artifacts/quant_digests/2026-04-03_rsi_momentum_5m_faster_exit_probe.csv`
   - `reports/artifacts/quant_digests/2026-04-03_rsi_momentum_15m_threshold_sweep.csv`
2. 对每个 `symbol × interval` 取当前总收益最高的那条 fast-exit admission 路径；
3. 用一个更保守、但对 admission 足够诚实的估算：
   - `额外可承受 friction(bps/round-trip) ≈ total_return / trades × 10000`
   - 它不是精确撮合仿真，而是回答“在已有成本口径之上，这条路径每笔还能再承受多少额外摩擦才会把累计优势吃光”。

## 结果
### 15m best-path（现有 admission 候选里最厚的一层）
- `BTCUSDT 15m, entry 55 / exit 45`：
  - total return `+27.17%`
  - trades `47`
  - PF `5.97`
  - max DD `-3.65%`
  - **额外 break-even friction ≈ 57.8 bps/笔**
- `ETHUSDT 15m, entry 60 / exit 45`：
  - total return `+48.23%`
  - trades `54`
  - PF `6.55`
  - max DD `-3.94%`
  - **额外 break-even friction ≈ 89.3 bps/笔**
- `SOLUSDT 15m, entry 65 / exit 45`：
  - total return `+45.79%`
  - trades `50`
  - PF `3.59`
  - max DD `-4.65%`
  - **额外 break-even friction ≈ 91.6 bps/笔**

结论很直接：`15m` 这层不是“只要再多几 bp 就没了”的脆边，而是明显厚于常见 taker-ish 再恶化一档的 admission 缓冲。

### 5m best-path（更接近主战场，但也更该防执行乐观）
- `BTCUSDT 5m, entry 62 / exit 45`：
  - total return `+35.06%`
  - trades `143`
  - PF `1.76`
  - max DD `-7.61%`
  - **额外 break-even friction ≈ 24.5 bps/笔**
- `ETHUSDT 5m, entry 58 / exit 45`：
  - total return `+90.77%`
  - trades `146`
  - PF `3.21`
  - max DD `-4.40%`
  - **额外 break-even friction ≈ 62.2 bps/笔**
- `SOLUSDT 5m, entry 58 / exit 45`：
  - total return `+61.22%`
  - trades `123`
  - PF `2.57`
  - max DD `-8.15%`
  - **额外 break-even friction ≈ 49.8 bps/笔**

这里也能把层次看清：
- `ETH/SOL 5m` 仍明显厚，说明 fast-exit 不是靠理想 fills 才活；
- `BTC 5m` 虽然还没薄到“再加 5~10bps 就归零”，但已经明显比另外两条更敏感，意味着它更像 admission 里的弱腿，后续若进入 paper，优先级应落后于 `15m` 与 `ETH/SOL 5m`。

## 为什么这足够回答本轮问题
本轮需要的不是把对象直接送进 `P3`，也不是装作已经做完精细撮合模拟；需要回答的是：

> 这条策略的现有优势，是否主要来自乐观执行假设，以至于一旦把口径拉诚实就应该直接退出？

当前答案是否定的：
1. 现有 artifact 本身已经是 **含成本** 口径，而不是裸 alpha；
2. 对 best-path 的逐条测算显示，主路径每笔仍留有可观的额外 friction 缓冲；
3. 没有出现“只有单一币、单一 timeframe、单一 lucky path 勉强为正”的塌缩图景；
4. 最薄的 `BTC 5m` 也只是说明后续 paper 更应做 selective launch，而不是说明整个 Rank 320 的 edge 已被执行现实证伪。

## 为什么本轮是 keep_P2，不是 promote_P3
虽然 honesty / post-cost 这一维已经通过，不该再把它当主要 blocker，但本轮还缺：
- 更长时间窗下的 `time stability`
- 邻近 entry threshold / exit threshold 扰动后的 `parameter stability`
- 哪些腿该进入最小 paper lane、哪些腿只保留为 supporting evidence 的最终收口

所以此刻最诚实的层级动作仍是：
- **不是 `drop_to_background/P0`**：因为 realism 并未把 edge 抹平；
- **也还不是 `promote_P3`**：因为 admission 第 2 步还没完成，launch lane 还没收窄；
- **因此应写成 `keep_P2`**。

## 本轮写回 runtime 的系统认知变化
- `Rank 320` 已通过 `honesty / execution realism + post-cost effectiveness` 这一维的首轮 admission；
- 当前系统不应再把“fast-exit 版本也许只是 friction 幻觉”视为默认主 blocker；
- 后续若继续研究 `Rank 320`，应把重心切到 `time stability + parameter stability` 收口，而不是重复执行 realism 质疑。

## Reader-facing 一句话
`Rank 320` 在更诚实执行口径下没有塌成摩擦幻觉：`15m` 三币与 `ETH/SOL 5m` 都仍保留厚实的额外 friction 缓冲，因此本轮 admission 先收口为 `keep_P2`，下一步该查的是时间/参数稳定性，而不是继续纠缠“会不会只是回测 fills 太乐观”。
