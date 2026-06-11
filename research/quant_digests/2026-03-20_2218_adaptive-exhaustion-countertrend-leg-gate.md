# 别把回踩腿写成“摸到位就够了”：`adaptive exhaustion` 更像 breakout-short / Fib / EMA-PSAR 的 countertrend-leg gate
- 时间：2026-03-20 22:18 UTC
- 类型：GitHub 仓库 + 论文背景
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/exhaustion/countertrend/retest/follow-up/admission/filter/repo/paper/crypto/5m/15m
- 证据类型：工程证据（开源指标仓库）+ 成本背景（crypto TA paper）

## 1. 这次看了什么
这轮主看 **just-nilux (2023)** 的 GitHub 仓库 **`legendary_ta`**，重点不是整包指标，而是其中两个能直接服务 desk 的小部件：`dynamic_exhaustion_bars` 与 `breakouts`。我这次不认领“exhaustion bar 本身就是独立 alpha”，而是只抽一个更贴近我们三条收口线的旁支：**当价格回踩到 broken level / Fib zone / EMA trigger 附近时，先问“这条 countertrend leg 是不是已经走到衰竭”，再决定这次 retest / follow-up 能不能放行。**

另外补一层背景：**Svogun, Bazán-Palomino (2022)** 已经提醒过，crypto 里的技术规则对交易成本很敏感。所以这轮更值得偷的，不是再多造一个高换手主信号，而是给已有 setup 加一个便宜的 `retest-leg veto / admission`。

## 2. 核心结论（先说人话）
- **一句话核心结论：** 对 5m/15m 来说，`retest_hold` / `follow-up` 不该只看“有没有摸回线位”，还要看“摸回来的这条反向腿是不是已经衰竭”；否则你经常是在接一条还没走完的 countertrend leg。
- **一句话证明方式：** 这个 repo 没直接给我们绩效结论，但它把“衰竭”写成了一个很便宜、很可复现的状态机：
  1. 先用 `close pct-change z-score` 的平滑值，生成 `1.5x ~ 5.0x` 的动态 multiplier；
  2. 再用默认 `window=500` 去估计最近的连续涨跌长度与 swing spacing；
  3. 最终输出 `leledc_minor / leledc_major`，把“买盘/卖盘是不是已经累了”写成可直接接到现有 setup 上的布尔/状态量。
- 一个特别值钱的细节是：`leledc_minor = 1` 代表 **sellers exhausted**，`leledc_minor = -1` 代表 **buyers exhausted**。这正好能镜像接到我们当前三条线：
  - `Fib / EMA long retest` 想看的是 **跌回来的这条腿是不是卖压衰竭**；
  - `breakout-short follow-up` 想看的是 **反抽回 broken level 的这条腿是不是买盘衰竭**。
- 这不是“alpha 已被证明”，而是一个**角色很诚实的 gating idea**：不改原始方向来源，只问 countertrend leg 还能不能继续推翻这笔交易。

## 3. 为什么这轮值得优先做（对齐三条收口线）
这轮不是乱开新坑，反而是对当前三条收口线的同层补刀：
1. **V3 final-verdict / breakout-short follow-up：** 下破后最怕追在 relief bounce 还没走完的时候。把 `buyers exhausted` 放到 broken support 附近，比继续猜“要不要立刻追空”更贴近 follow-up 真问题。  
2. **Fibonacci confirmation / retest_hold：** Fib 现在最缺的不是再争 `0.5 / 0.618 / 0.71` 哪个神，而是把“这次回踩到底是健康 pullback，还是仍在继续砸”说清楚；`sellers exhausted` 正好补这块。  
3. **EMA / PSAR raw alpha focus：** 这条线已经越来越明确该被降成方向层 / overlay。那最自然的搭法就是：EMA/PSAR 继续给方向，`adaptive exhaustion` 只负责确认回踩腿有没有衰竭。  
4. **它还顺手服务当前 active scout：** 现在 `Rank 131` 看的，是“最近 1~2 根有没有连续 violation memory”；这轮看的，是“当前这条回踩腿本身有没有衰竭”。两者是正交的，值得在开新题前先补这一刀。

## 4. 15m 最小可复现实验（下一步怎么测）
**目标：** 给现有 `breakout-short follow-up / Fib retest_hold / EMA reclaim` 增加一个 `countertrend-leg exhaustion` admission 层，看它能不能减少假 hold / 假 follow-up。

- 资产：`BTC / ETH / SOL` perpetual  
- 信号周期：`15m`  
- 执行周期：`5m`（只用于读回踩腿是否衰竭）  
- 成本：`6 / 10 / 15 bps per side`  
- 执行：`next-bar open + no-overlap`

### 实验三臂
1. `A: baseline`
   - 保留当前 `breakout-short follow-up` / `fib_retest_hold_long` / `ema_reclaim_long` 原规则。
2. `B: baseline + minor exhaustion gate`
   - **short follow-up：** 先有 downside breach；当价格反抽回 broken level 附近时，只在最近 `1~3` 根 `5m` bar 出现 `leledc_minor = -1 (buyers exhausted)` 时放行 short。  
   - **Fib / EMA long：** 当价格回踩 `0.5/0.618` 或 EMA trigger 区附近时，只在最近 `1~3` 根 `5m` bar 出现 `leledc_minor = 1 (sellers exhausted)` 时放行 long。  
3. `C: B + major exhaustion strict tier`
   - 若 `major` 与交易方向冲突，则直接 veto；
   - 若只有 `minor`、没有 `major`，只给 half-size 或更紧 stop；
   - 若 `minor + major` 都同向支持，再保留正常 size。

### 先看 5 个指标
- `post_cost_expectancy`
- `false_reclaim_ratio@4bars`（long：4 根内再次失守 zone；short：4 根内重新收回 broken level）
- `mae@4bars` 或 `sl_first_rate`
- `trade_count_retention`
- `entry_delay_bars`（别用“晚很多”换漂亮报表）

## 5. 风险与保留意见
- 这条证据主要来自**开源实现**，不是“已有大样本 crypto OOS 论文”——它能证明的是“这个 gating 机制写得出来”，不能证明“已经有 alpha”。  
- repo 默认 `window=500` 放到 `15m` 上大约相当于近 `5` 天多的条数，第一轮应至少比 `160 / 320 / 500` 三档，避免直接照搬。  
- exhaustion 很容易**太晚**：强趋势里，等它亮灯可能已经错过最干净那一脚。所以它更适合做 `veto / strict admission`，不适合接管主触发。  
- 不能让它偷偷变成“见 exhaustion 就做反转”。当前 desk 更诚实的角色仍是：**只有在既有 breakout / Fib / EMA setup 已成立时，才额外问一句 countertrend leg 有没有衰竭。**

## 6. 来源
1. **just-nilux (2023). _legendary_ta_. GitHub Repository.**  
   - Author/Org: GitHub user `just-nilux`  
   - Year: 2023（repo 创建时间 2023-04-21）  
   - Title: legendary_ta  
   - Venue: GitHub  
   - DOI: `N/A`  
   - Readable URL: <https://github.com/just-nilux/legendary_ta>  
   - Repo URL: <https://github.com/just-nilux/legendary_ta>  
   - Code URL: <https://raw.githubusercontent.com/just-nilux/legendary_ta/master/legendary_ta.py>
2. **Svogun, A., & Bazán-Palomino, W. (2022). _Technical analysis in cryptocurrency markets: Do transaction costs and bubbles matter?_ Journal of International Financial Markets, Institutions and Money.**  
   - DOI: <https://doi.org/10.1016/j.intfin.2022.101601>  
   - Readable URL: <https://www.sciencedirect.com/science/article/pii/S1042443122000130>  
   - Repo URL: `N/A (paper-based)`
3. **Binance Developers. USDⓈ-M Futures Kline/Candlestick Data.**  
   - Readable URL: <https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data>

## 7. 下一步怎么测（一句话）
先别再把 retest / follow-up 写成“到位就做”，直接给三条 baseline 各加一个 `countertrend-leg exhaustion` 的 B 臂；如果它能在不明显砍光交易数的前提下压低 `false_reclaim_ratio@4bars`，再考虑把它升成 shared admission。