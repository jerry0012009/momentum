# 别把 Fib retest_hold 继续写成独立硬门：新 ORB repo 里，活下来的不是 `conservative retest`，而是 `breakout → retest → bounce + score`
- 时间：2026-03-23 02:05 UTC
- 类型：GitHub 仓库
- 主题标签：fibonacci/retest-hold/breakout-short/ema/psar/orb/phase-state-machine/retest/bounce/score/rvol/vwap/atr/repo/crypto/5m/15m
- 证据类型：仓库 README + Pine 实现

## 1) 这次看了什么
这轮不再泛找“新指标”，而是直接回答当前 `Fib confirmation / retest_hold` 最卡的一件事：
> **回踩确认，到底该被写成一个单独的 hard gate，还是只该是更大状态机里的一个 phase？**

我看的对象是一个很新的仓库：**Mrshahidali420 / ORB-Multi-Model-Indicator (2026)**。它本体是 NY session 的 ORB 工具，不是 crypto 15m 成品；但其中一个旁支想法非常适合我们现在的三条收口线：
- repo 里保留了 **M10 = `breakout → retest → bounce` 三阶段状态机**；
- 同时保留了 **Combined confidence score**；
- 但把 **M5 Conservative Retest** 这类“更像把 retest 单独当成主逻辑”的模型直接删掉了。

这正好能回答我们 desk 当前的问题：**`retest_hold` 更像该当“过程里的质量确认”，而不是独立 alpha / 独立硬门。**

## 2) 核心结论（先说人话）
- **一句话结论：** 对 `Fib retest_hold` 来说，更值得偷的不是“回踩本身”，而是 **`phase state machine + timeout/abort + score`** 这套骨架。  
- **一句话证据：** 这个新 repo 最后留下的是 **7 个 active model + 1 个 Combined score 模式**，而被删掉的恰恰包括 **`M5 Conservative Retest`**；README 直接写明：`M2 / M5 / M8` 因为跨品种、跨周期回测只有 **0%~26% win rate** 被移除。

### 关键数据点（都来自仓库本身）
1. **repo 没有把 retest 单独捧成“最好模型”**
   - active：`7` 个 ORB 模型 + `1` 个 Combined mode
   - removed：`M2 / M5 / M8`
   - removed models 的 README 口径：**`0%~26% win rate`**

2. **活下来的 retest 不是“摸到就上”，而是三阶段状态机**
   - `Phase 1`：先确认 breakout
   - `Phase 2`：再等 retest touch
   - `Phase 3`：最后等 bounce reclaim 才入场
   - 代码里默认 `retest tolerance = 0.15 × ATR`
   - 并且给 `Phase 2 / 3` 单独设置 `max wait`，超时就取消

3. **Combined mode 也不是二元 yes/no，而是最少过一个 60 分及格线**
   - 默认 `i_minScore = 60`
   - `VWAP alignment = 25 分`
   - `RVOL` 分档：`1.2 / 1.5 / 2.0` 对应 `10 / 18 / 25 分`
   - `HTF EMA alignment = 20 分`
   - `RSI 带内 = 15 分`
   - `agreement count` 额外最多加 `30 分`

> 读法：repo 在用实际保留/淘汰告诉你——**“有回踩”不够，必须把它放回更完整的上下文里。**

## 3) 为什么这题比继续泛找更值得
因为它直接服务当前三条收口线，而且是现在最缺的“角色判断”：

- **Fib confirmation / retest_hold**：最直接。它在提醒我们，`retest_hold` 更像 **phase-quality layer**，不是独立 hard gate；
- **V3 breakout-short / final-verdict / follow-up**：也能直接借它的 `timeout + opposite-boundary abort` 思路，避免把 follow-up 写成无限等待；
- **EMA / PSAR raw alpha focus**：repo 的 Combined score 也在提醒我们，裸 trigger 之外更值得加的是 **VWAP / RVOL / HTF alignment** 这类 overlay，而不是继续幻想 raw alpha 自己会变干净。

所以这轮不是离开主线，而是在替 `Fib / breakout-short / EMA-PSAR` 统一回答一句：**确认层该扮演什么角色。**

## 4) 给 desk 的最小映射：怎么把它翻成 5m / 15m 实验
不要复刻 ORB 的 NY session 外壳，只偷它最值钱的骨架：

1. **Phase 1 = 15m 主信号先成立**
   - `Fib retest_hold`：已有 `BOS / fresh breakout / Fib anchor` 候选
   - `breakout-short`：已有初始 break + follow-up 观察窗
   - `EMA / PSAR`：已有 raw trigger，但先不直接成交

2. **Phase 2 = 下钻 5m 看“诚实回踩”**
   - `retest_tol_atr ∈ {0.10, 0.15, 0.20}`
   - `max_wait_5m_bars ∈ {3, 6, 9}`
   - 对 `Fib`：看价格是否回到 defended zone / defended line 附近
   - 对 `breakout-short`：看破位后是否回抽到 break level 附近

3. **Phase 3 = 只在 bounce / reclaim 后才放行**
   - long：5m close 重新站回 defended line / zone 上方
   - short：5m close 重新回到 defended line / zone 下方
   - 若先穿越 opposite invalidation boundary，直接 abort
   - 若超过 wait window 还没 bounce，直接 timeout/cancel

4. **再给它加一个 cheap score，而不是再造一个 hard gate**
   - `+25`：VWAP 同侧
   - `+10/18/25`：same-clock RVOL 分档
   - `+20`：1h EMA20/50 同向
   - `+15`：RSI 落在 continuation band
   - `+10`：额外 agreement（例如 breakout bar conviction / CLV / rebreak）
   - 先测 `score >= 60` 与 `score >= 70`

## 5) 下一步怎么测（必须给实验口径）
先只做 **Fib retest_hold**，不要三线一起上：

1. 样本：`BTCUSDT / ETHUSDT / SOLUSDT`，Binance public spot/perp，`15m` 主框架 + `5m` 确认，近 `90d`
2. 母信号：沿用当前 `Fib confirmation / retest_hold` 候选事件流
3. 对照组：
   - `A` = 当前二元 retest_hold
   - `B` = `phase state machine`（不加 score）
   - `C` = `phase state machine + score>=60`
   - `D` = `phase state machine + score>=70`
4. 统一看 4 个指标：
   - `trade_count_retention`
   - `continue / fail / timeout share`
   - `post-cost expectancy`（先按 `10bps` round-trip）
   - `12-bar / 24-bar invalidation ratio`

### 我预期最值得验证的一句假设
> **B/C/D 大概率不会让胜率暴涨，但应该能把“碰线就算 hold”的假确认压下去，同时把 `timeout` 诚实地暴露出来。**

如果只看到 `trade_count` 大幅掉、`timeout` 大幅升、但成本后收益没改善，就说明这条路仍然只是“更好看的确认叙事”，还不配升格。

## 6) 风险与保留意见
- 这是 **repo intake**，不是正式 replication；
- repo 主战场是 `NY ORB / 1m~5m`，不是 crypto `15m`，所以只能偷骨架，不能照抄参数；
- README 提到的跨品种 win rate 没附完整审计细节，可信度只够拿来做 **研究排序**，不够当最终证据；
- `agreement count` 这类分数项很容易把已有过滤器重复计分，实验时一定要防止把同一信息灌两次。

## 7) 来源
1. **Mrshahidali420 (2026). _ORB Multi-Model Indicator_. GitHub Repository.**
   - Authors / Org: Mrshahidali420
   - Year: 2026（`created_at = 2026-03-13`；`updated_at = 2026-03-20`）
   - Title: ORB Multi-Model Indicator
   - Venue: GitHub
   - DOI: N/A
   - Readable URL: <https://github.com/Mrshahidali420/ORB-Multi-Model-Indicator>
   - Repo URL: <https://github.com/Mrshahidali420/ORB-Multi-Model-Indicator>

2. **Mrshahidali420 (2026). _ORB_Multi_Model_Indicator.pine_.**
   - Authors / Org: Mrshahidali420
   - Year: 2026
   - Title: ORB_Multi_Model_Indicator.pine
   - Venue: GitHub (source file)
   - DOI: N/A
   - Readable URL: <https://github.com/Mrshahidali420/ORB-Multi-Model-Indicator/blob/master/ORB_Multi_Model_Indicator.pine>
   - Repo URL: <https://raw.githubusercontent.com/Mrshahidali420/ORB-Multi-Model-Indicator/master/ORB_Multi_Model_Indicator.pine>
   - 关键实现点：`i_minScore=60`、`RVOL 1.2/1.5/2.0` 分档、`M10` 的 `breakout → retest → bounce` 状态机、`0.15 × ATR` retest tolerance、超时/越界 abort。

## 8) 产出文件（本轮）
- `research/quant_digests/2026-03-23_0205_orb-phase-retest-score-not-hard-gate.md`
