# 别让 PSAR 一翻面就当 15m 入场键：`close-confirmed flip + 第 N 根 trend bar`，更像 EMA/PSAR 与 breakout-short 共用的 follow-up gate
- 时间：2026-03-18 21:08 UTC
- 类型：GitHub
- 主题标签：breakout-short/ema/psar/follow-up/confirmation/entry-delay/repo/crypto/15m
- 证据类型：工程经验（开源代码）
- 证据强度提示：**中等偏弱**（代码规则很清楚，但不是论文，也没有可信的同口径 crypto 绩效）

## 1. 这次看了什么
这次看的是 GitHub 仓库 **0xeth-drc-888 / PARABOLIC-STOP-AND-REVERSE-PSAR-Strategy-at-closing-period-updated-v.3.5**（2020，2024 仍有更新痕迹），重点不是“PSAR 又一个神奇参数”，而是源码里两条很适合现在 desk 的便宜约束：**只有收盘价真正越过上一根 PSAR 才翻向**，以及 **不是翻向当根就追，而是允许等到第 `N` 根 trend bar 再进**。

## 2. 核心结论
- **一句话核心结论**：对 `15m` crypto，PSAR 更值得先测成 **close-confirmed follow-up gate**，而不是一翻面就立即开仓的原始 alpha。
- **一句话说明它怎么证明**：不是靠论文统计，而是代码把 `sar_long_to_short = close <= psar[1]`、`sar_short_to_long = close >= psar[1]` 和 `strategy.entry(... when = trend_bars == ±entry_bars)` 直接写死，等于把“先收盘确认、再决定要不要等第 2/3 根”变成可回测规则。
- 最值钱的不是 PSAR 本身，而是 **把 wick flip 和 confirmed flip 拆开**；这正好贴着当前 `EMA / PSAR raw alpha focus` 的痛点。
- 代码里的默认加速参数仍是经典 `start=0.02 / increment=0.02 / maximum=0.2`，说明更值得偷的不是参数炼丹，而是 **flip 口径** 与 **follow-up 延迟**。
- `entry_bars` 这个小开关很适合直接服务 `V3 final-verdict / breakout-short follow-up`：第 1 根更像告警，第 2/3 根才更像 continuation 确认。

## 3. 为什么和当前项目有关
这轮值得做它，不是因为它比三条收口线更“新潮”，而是因为它**正面回答了其中一条还没完全收干净的问题**：PSAR 到底该扮演什么角色。

- 对 **`EMA / PSAR raw alpha focus`**：最近几轮已经越来越明确，PSAR 不适合继续单扛 15m 原始 alpha；这份代码给了一个更诚实的岗位——**快反应结构翻向时钟**。先确认 close flip，再决定要不要等第 `2/3` 根 follow-up bar。
- 对 **`V3 final-verdict / breakout-short follow-up`**：很多 short breakout 死在“刚跌破就追”，结果下一根立刻收回。若把 `confirmed PSAR short + trend_bar>=2` 当 follow-up 许可层，就能把“跌破发生了”与“跌破真的延续了”拆开。
- 对 **`Fibonacci confirmation / retest_hold`**：镜像做法也成立。回踩后不是一根反弹就算 hold，而是先看 PSAR 是否 close-confirmed 翻回多头，再看是否走到第 `2` 根确认 bar。

## 4. 可复刻的最小实验
### 研究假设
在 `BTC / ETH / SOL` perpetual 的 `15m` 上，把 `PSAR raw immediate flip` 改成 `close-confirmed flip + entry_bar delay`，会降低 `2~4 bar` whipsaw / 假跌破追空率，并改善成本后 continuation 质量。

### 最小可计算定义
- 先按 repo 口径重写 PSAR 翻向：
  - `flip_short = trend_dir[1]==1 and close <= psar[1]`
  - `flip_long  = trend_dir[1]==-1 and close >= psar[1]`
- 计算 `trend_bars`：翻空后记 `-1,-2,-3...`；翻多后记 `1,2,3...`
- 三个最小对照臂：
  1. `N=1`：close-confirmed 后立刻进（最接近 raw PSAR）
  2. `N=2`
  3. `N=3`
- 对 `breakout-short` 的接法：只有当原 `short_trigger` 已触发，且 `trend_dir=-1 & abs(trend_bars)>=N` 时才允许开空。
- 对 `Fib retest_hold long` 的接法：只有当 `reclaim/hold` 已触发，且 `trend_dir=1 & trend_bars>=N` 时才允许开多。

### 最小回测切口
- 标的：`BTC / ETH / SOL` perpetual
- 周期：`15m`
- 样本：最近 `180~365d`
- 执行：`next-bar open`、`no-overlap`
- 成本：先统一看 `6 / 10 / 15 / 20 bps per side`

### 最该先看 4 个指标
- `flip_to_fail_rate`：翻向后 `2~4` 根内又反翻的比例
- `false_break_ratio`：breakout-short 入场后 `X` 根内收回原区间的比例
- `post_cost_expectancy`
- `trade_retention`：`N=2/3` 相比 `N=1` 还保留多少样本

## 5. 风险与保留意见
- 这是 **老 repo + 低社会证明** 的工程骨架，不是高等级学术证据；它更像“值得偷一条规则”，不是“可直接相信的策略成绩”。
- `entry_bar` 延迟会天然错过最快的一段；若最后只是胜率升但收益塌得更快，就说明它只是“看起来更稳”。
- PSAR 仍是 price-only 规则；遇到新闻驱动、急 V 反转、极端 squeeze，close-confirmed 也不一定够。
- 若 `N=2/3` 只是在交易数砍半后才换来一点点改善，这条线就该停在 **shared follow-up veto**，不要再包装成主信号。

## 6. 来源
1. **0xeth-drc-888 (2020, updated 2024)**, *PARABOLIC-STOP-AND-REVERSE-PSAR-Strategy-at-closing-period-updated-v.3.5*.
   - Venue: GitHub
   - DOI: N/A
   - Readable URL: https://github.com/0xeth-drc-888/PARABOLIC-STOP-AND-REVERSE-PSAR-Strategy-at-closing-period-updated-v.3.5
   - Repo URL: https://github.com/0xeth-drc-888/PARABOLIC-STOP-AND-REVERSE-PSAR-Strategy-at-closing-period-updated-v.3.5
2. **Raw source code**: *Parabolic SAR Strategy (on close) [QuantNomad]*（仓库 `Source Code` 文件）
   - Readable URL: https://raw.githubusercontent.com/0xeth-drc-888/PARABOLIC-STOP-AND-REVERSE-PSAR-Strategy-at-closing-period-updated-v.3.5/master/Source%20Code
   - 关键规则：`close <= psar[1]` / `close >= psar[1]` 翻向；`strategy.entry(... when = trend_bars == ±entry_bars)`
