# 2026-03-26 02:18 UTC — Rank 96 park reframe review

## 本轮选择
- 选定条目：`Rank 96`
- 选择原因：符合本轮默认轮转里的 `80~110` 段；最近 `7` 天内未见 `bot6` 对 `Rank 96` 的 park-reframe 复盘记录；且它属于已 `park`、仍留有一丝“执行语义残余”的条目，适合做一次低频复查。

## 原 rank 为什么 park
先回看原始 intake / clean replication 与相关 digest：
- `research/optimization_loop/2026-03-19_1808_rank96-source-intake.md`
- `research/optimization_loop/2026-03-19_1825_rank96-clean-replication-park.md`
- `research/quant_digests/2026-03-19_1734_advancedma-retest-count-admission-layer.md`
- 旁证：`research/quant_digests/2026-03-23_0825_prev-candle-fib-second-chance-not-shared-gate.md`

原始 `park` 的核心原因很清楚：
1. **second-touch 确实让 short 侧从“明显负”改善到“接近打平”**，但没有把结果稳稳推过成本门槛；
2. 这点改善主要伴随 **trade_count_retention 只剩约 20%**，很像靠大砍样本换出来；
3. **跨资产不一致**：主变体下只有 `ETH short` 留正，`BTC/SOL` 都不行；
4. **long 侧更差**，说明它并不是可共享的 long/short 通用 retest gate；
5. clean replication 自己已经把最诚实结论写死：它最多只是 `setup-specific short admission / veto` 的弱线索，不值得继续占主资源位。

## 它更像 hard park 还是 soft park
**结论：`soft park`，但不软到可以直接起草 `Rank 96b`。**

原因：
- 它不是“主题彻底没信息”的 hard fail；
- 但也不是“只差一刀就能诚实重开”的状态；
- 更准确的读法是：**有局部残余信息，但这点残余太依赖 short-side / ETH-side / 强砍样本，暂时只够记成 candidate note。**

## 有没有“可救信号”
有，但很弱，而且只集中在一个很窄的位置：
- `retestCount>=2` 对 **short follow-up** 比对 long retest 更像有用；
- clean replication 里真正还像回事的，只剩 **`second_touch_plus_candle_quality` on short side**；
- 对应的 quant digest 也早就给过同样提醒：`retestCount>=2` 更像 breakout-short follow-up 的 admission layer，而不是三条线共享的万能 gate；
- 2026-03-23 的 `prev-candle Fib second-chance` 新证据又进一步说明：**“等 textbook pullback 再做”更像分支 entry style，不像 shared hard gate。**

所以，可救信号不是“Rank 96 原方向能复活”，而只是：
- **retetst count 可能在 short-side delayed admission 里留有一点信息量。**

## 最值得改的唯一一刀是什么
如果以后真要再碰它，唯一值得保留的一刀只能是：

**把原来的 generic `retestCount>=2` 读法，收缩成 `short-side only second-touch + candle-quality admission delay`。**

也就是：
- 不再把它写成 shared hard gate；
- 不碰 long 侧；
- 不把它升格成独立 alpha；
- 只把它当成 breakout / failure-followthrough 语境里的一个很窄、很便宜的 short-side admission delay 线索。

## 是否值得形成新的 derived hypothesis
**结论：不值得；本轮状态 = `soft_reframe_candidate`。**

不直接 draft 的原因：
1. 残余改善仍然太依赖样本收缩，审计上不够干净；
2. 没有跨资产一致性，不像 queue-facing 的新 rank；
3. 主题残余与已有 `failure / follow-up / second-chance` 家族高度重叠，单独再起一条 `Rank 96b` 容易只是换壳重讲；
4. 当前最诚实的位置，是先保留一句 **“只在 short-side second-touch + candle-quality admission delay 里还有一点残余信息”**，而不是把它推进成 bot2 需要判断是否入板的正式 draft。

## trade on / trade off（仅作 candidate note，不是正式 drafted hypothesis）
- trade on：若未来 fresh intake 不足，且 desk 想专门补 `short-side delayed admission` 这块，可回看 `second-touch + candle-quality` 这一条 very narrow clue。
- trade off：不要把它重新包装成 shared retest gate、不要镜像到 long 侧、不要顺手叠 volume / Fib / regime / exit 第二轴。

## 本轮最终结论
- `Rank 96`
- `verdict = soft_reframe_candidate`
- `original park verdict kept = yes`
- 一句话：**原 Rank 96 仍应保持 park；唯一残余价值只像 short-side second-touch + candle-quality admission delay 的弱线索，当前不诚实直接 draft Rank 96b。**

## 文件更新
- 新增本轮日志：`research/park_reframe/2026-03-26_0218_rank96-park-reframe.md`
- 追加索引：`research/park_reframe/INDEX.md`
- 更新队列：`docs/PARK_REFRAME_QUEUE.md`
- 未改：`docs/TODO.md`

## git / 提交
- 当前 `git status --short | wc -l = 3234`，共享脏文件很多；
- 本轮只做 park-reframe 最小必要改动；
- **不做 commit**，避免混提。
