# 别把 15m 的 post-entry 管理搬成 fixed `+50 pips` partial：repo 里的 absolute partial 更像 FX portability trap，若要服务 breakout-short / Fib / EMA，先改成 `R-multiple / ATR`
- 时间：2026-03-20 22:42 UTC
- 类型：GitHub 仓库 + 内部 runbook 对照
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/partial-exit/path-management/r-multiple/atr/portability/risk-overlay/repo/crypto/15m
- 证据类型：仓库代码（工程证据）+ 本地策略文档对照

## 1. 这次看了什么
这轮主看 **carlosrod723 (2025)** 的 GitHub 仓库 **MQL5-Trading-Bot**，但不抄它最显眼的“多策略 FX 机器人”叙事，而是只抽其中一个更贴当前 desk 的旁支：
**partial exit / trailing 的触发阈值，到底该写成 fixed absolute distance，还是写成相对风险单位？**

repo 里这段管理逻辑非常直白：
- `UsePartialExit = false`
- `PartialExitRatio = 0.5`
- `UseTrailingStop = false`
- `TrailStopPips = 20.0`
- `CheckPartialExit(...)` 里直接写死：`return (pips > 50);`

翻成人话：**仓位走出固定 `50 pips` 就先砍半，trailing 默认也是固定 `20 pips`。**
这在 FX / point-size 明确的环境里可以先跑起来，但如果直接搬去 `Crypto 5m/15m`，它更像一个**可移植性陷阱**：
你以为自己在研究“部分止盈有没有用”，其实先偷偷混进来了三件事：
1. 资产价格量级；
2. 交易所最小报价单位；
3. setup 自身的初始风险距离。

## 2. 核心结论
- **一句话核心结论：** 对当前三条收口线来说，fixed absolute partial trigger 不该直接进入共享 runbook；若要研究 partial exit，第一优先应改写成 `R-multiple` 或 `ATR-scaled` 触发。  
- **一句话证明方式：** repo 把 partial/trailing 逻辑明文写成 `50 pips / 20 pips / 50%`；再对照我们本地当前更接近生产的 exit 口径（`ATR TP/SL + timeout`），可见 absolute-distance partial 与现有 desk 的风险计量体系并不兼容。

关键数据点：
1. **repo 的 partial 触发是固定距离，不看 setup 风险：** `CheckPartialExit()` 只看 `pips > 50`，和 `sl`、`tp`、`ATR` 都没有关系。
2. **partial 规模也是写死的：** `PartialExitRatio = 0.5`，意味着一旦触发就固定砍半，而不是按波动或 path quality 调整。
3. **我们当前本地 exit runbook 反而是相对尺度：** `docs/CANARY_32B_PHASE6.md` 里推荐 `exit.tp_atr_mult = 1.25`、`exit.sl_atr_mult = 1.0`、`exit.timeout_minutes = 120`；也就是 desk 已经默认用 `ATR/时间` 管理风险，而不是 fixed pips。

翻成人话：
- repo 这段代码不是“partial exit 已被证明有效”；
- 它真正给我们的价值，是提醒：**如果要做 post-entry overlay，先把管理单位统一到风险单位。**
- 否则你最后测出来的，很可能不是“partial exit 的边际”，而是“某个绝对距离刚好碰巧适合某个币 / 某段波动期”。

## 3. 为什么这轮比继续塞一个新 entry gate 更值得
这不是偏题。

当前三条收口线里，entry 端今天已经非常拥挤：
- breakout-short 已连续补过 `final-verdict / timeout / follow-up / range-location / adaptive exhaustion`；
- Fibonacci 也已经补了 `hold-quality / reclaim / confirmation / long-bias asymmetry`；
- EMA / PSAR 则反复收敛到“raw alpha 弱，更多是 role / overlay 问题”。

这时继续找一个“再多一层 admission filter”，边际未必最高。反而更缺的是：
**一旦这笔单已经被放行，后半段到底该怎么拿、怎么减、怎么别被 absolute threshold 误导。**

而且这件事和 backlog 是对齐的：
- `docs/FACTOR_BACKLOG.md` 已明确把 `trailing stop 变体` 记为 `SCOPED`；
- 说明项目已经意识到“出场/管理层”值得独立实验，只是还没把它收成一条干净结论。

所以这轮更像给三条线补 **path-management common layer**，不是把研究带偏。

## 4. 对三条收口线分别意味着什么
### 4.1 `V3 final-verdict / breakout-short follow-up`
对 breakout-short 来说，最怕的是：
- 前面已经很认真筛了 `avoid-chop / follow-up / final verdict`；
- 后面却用一个 fixed absolute partial 提前把 winner 切碎。

更诚实的做法是：
- short 入场后，先按初始 stop 定义 `1R`；
- 若走出 `+0.75R` 或 `+1.0R` 再考虑 partial；
- 而不是不分币种/不分波动，统一“到了某个固定价差就砍半”。

### 4.2 `Fibonacci confirmation / retest_hold`
Fib 线的核心不是“动一点就收米”，而是“回踩守住后，能不能拿到第二段”。

如果 partial trigger 写成 fixed absolute distance，最容易发生两种错：
- 波动大的币：太快触发，winner 被过早切短；
- 波动小的币：长期触发不到，partial 逻辑形同虚设。

所以 Fib 更适合：
- `entry risk = low_of_retest - entry`（或 mirror short）；
- partial 只在 `MFE >= 1R` 或 `MFE >= 1.0~1.25 ATR` 时触发；
- 这样才和 `hold-quality` 的逻辑一致。

### 4.3 `EMA / PSAR raw alpha focus`
EMA / PSAR 线现在最大的风险，不是“少一个 fixed partial”，而是**角色继续混乱**。

如果 raw alpha 本来就薄，再加一个 absolute partial，常见结果不是更稳，而是：
- winner 被切短；
- trade log 变漂亮；
- 成本后 edge 更薄。

因此这条线若要碰 partial，应该先当：
- `R-based de-risk overlay`，不是新 alpha；
- 并且必须和 `PSAR trailing role`、`fail-fast overlay` 分开测，不要偷带多轴变化。

## 5. 最小实验（下一步怎么测）
### 研究假设
在冻结现有三条 entry 定义后，`relative partial trigger`（`R-multiple` / `ATR-scaled`）会比 `fixed absolute trigger` 更稳，也更容易跨 `BTC/ETH/SOL` 保持可解释性。

### 首轮只测 4 臂
- `A | base`：不做 partial，沿用当前 baseline exit
- `B | fixed_abs_partial`：代理 repo 口径，达到固定距离就砍 `50%`
- `C | R1_partial`：`MFE >= 1.0R` 时砍 `50%`
- `D | ATR1_partial`：`MFE >= 1.0 ATR(entry)` 时砍 `50%`

### 冻结口径
- 资产：`BTC / ETH / SOL` perpetual
- 周期：`15m` 主评估，必要时 `5m` 做执行细化
- 样本：近 `180d`
- 执行：`next-bar open`、`no-overlap`
- 成本：至少 `6 / 10 / 15 bps per side`
- 约束：**entry 完全冻结，只改 partial 管理层**

### 第一轮最该看哪 4 个指标
1. `post-cost expectancy`
2. `winner_median_return`
3. `MFE_capture_ratio`
4. `cross-asset dispersion`（看它是不是只在单一资产碰巧有效）

### 一条很重要的 honesty rule
如果 `fixed_abs_partial` 的改善只来自：
- 交易数大幅下降，或
- winners 被提前切短但 loser 看起来更小，
那它不该被包装成“更聪明的 exit”，而应老实归类为 **measurement mismatch / portability artifact**。

## 6. 风险与保留意见
- 这轮证据主要是 **仓库代码 + 本地 runbook 对照**，不是 OOS 完整回测；
- `50 pips` 在 FX 平台里有明确语义，但迁到 crypto/perp 后，和 tick size / contract spec 的关系会变脏；
- `R-multiple` 与 `ATR` 也不是自动正确，它们只是比 fixed absolute threshold 更诚实的 first pass；
- partial exit 很容易改善“主观体感”，却不一定改善成本后收益，后续必须和 `no partial` 做硬对照。

## 7. 来源
1. **Carlos Rodriguez. (2025). _MQL5-Trading-Bot_. GitHub repository.**
   - Authors: Carlos Rodriguez
   - Year: 2025
   - Title: MQL5-Trading-Bot
   - Venue: GitHub
   - DOI: `N/A`
   - Readable URL: `https://github.com/carlosrod723/MQL5-Trading-Bot`
   - Repo URL: `https://github.com/carlosrod723/MQL5-Trading-Bot`
2. **关键实现：`MQL5/Experts/MyTradingBot.mq5`**
   - Authors: Carlos Rodriguez
   - Year: 2025
   - Title: `MyTradingBot.mq5`（position management / partial exit / trailing stop）
   - Venue: GitHub source file
   - DOI: `N/A`
   - Readable URL: `https://github.com/carlosrod723/MQL5-Trading-Bot/blob/main/MQL5/Experts/MyTradingBot.mq5`
   - Repo URL: `https://github.com/carlosrod723/MQL5-Trading-Bot`

## 8. 本地对照文件
- `docs/FACTOR_BACKLOG.md`
- `docs/CANARY_32B_PHASE6.md`
