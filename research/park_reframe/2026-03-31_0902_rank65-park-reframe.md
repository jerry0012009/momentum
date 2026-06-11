# 2026-03-31 09:02 UTC — Rank 65 park reframe review

## 为什么这轮看 Rank 65
- 遵循 `bot6` 轮转：当前默认优先 `Rank 50+`，而 `Rank 65` 仍属已 `park` 但尚未进入 `park_reframe` 低频复盘记录的旧条目。
- 它的原始故事是 `perp-stress resetComplete / re-arm gate`，属于典型“概念很顺，但可能职责放错层”的命题；最近一周又新增了多条与 `funding / basis / OI / liquidation` 直接相关的新 digest，值得确认一次：
  1. `2026-03-24_0631_liquidation-consensus-cascade-continuation-alpha.md`
  2. `2026-03-23_1632_perp-premium-gap-mean-reversion-fullstack.md`
  3. `2026-03-30_2344_current-next-funding-closecost-carry-alpha.md`
- 目标不是替 `bot2 / bot3` 接手 crowding / carry 新主线，而只是判断：原 `Rank 65` 还有没有诚实的单轴可救空间。

## 本轮补读
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/optimization_loop/2026-03-18_1940_rank65-source-intake-guard-passed.md`
- `research/optimization_loop/2026-03-18_2018_rank65-clean-replication-park.md`
- `research/quant_digests/2026-03-18_1845_perp-stress-reset-complete-rearm-gate.md`
- `research/quant_digests/2026-03-24_0631_liquidation-consensus-cascade-continuation-alpha.md`

## 1) 原 Rank 为什么 park？
原 `Rank 65` 想做的是：
- 不改 `breakout_short / fib_retest_hold / ema_psar_long` 的原始方向；
- 只在最近出现 `perp stress` 后，等到 `resetComplete = basis neutral + OI flush + ATR compression` 才重新允许三条线继续触发；
- 本质上是一条 `shared post-stress re-arm gate`。

但原始最小 clean replication 给出的否决非常干净：
1. **三臂结果完全一样。**
   - `no_gate / stress_pause_only / stress_pause_reset_rearm` 在 `6bps/side` 下整体结果几乎一致；
   - 这不是“gate 很稳”，而是它根本没实质筛到交易。
2. **根因是 coverage fail，而不是有样本但效果差。**
   - `stress_event_board.csv` 里 `BTC / ETH / SOL` 都是 `stress_events=0`、`reset_complete_bars=0`；
   - 也就是说，在 frozen 的公开代理定义下，连“先发生过一次可复核的 stress event”都站不住。
3. **因此原 park 不是风格偏好问题，而是最小可审计口径下的定义不可用。**
   - 在 coverage 都没有的前提下，再讨论 time stability / parameter stability 已经没有意义。

翻成人话：
**Rank 65 被 park，不是因为“perp stress 主题彻底没信息”，而是因为它当时那版 `15m 三线共用 resetComplete / re-arm gate` 在公开代理口径下根本打不到事件，连入场券都没有。**

## 2) 它更像 hard park 还是 soft park？
结论：**soft park，但作为 queue-facing 的旧命题已经很偏 hard。**

原因：
- `funding / basis / OI / liquidation` 这个大主题显然没死；
- 但最近新增证据说明它更诚实的承载方式，已经不是原 `Rank 65` 这类 shared re-arm gate，而是：
  1. **事件驱动的 crowding / cascade raw alpha**（如 `funding + OI 背离 + liquidation cluster` 的延续或 panic reversal）；
  2. **可独立落地的 basis / funding carry / premium-gap raw alpha**；
  3. 少数情况下才是更上位的数据完整性 / risk overlay。
- 换句话说，主题没死，但原编号的血缘边界已经明显变窄。

所以它不是 classic hard park——因为母主题仍然活着；
但对“继续诚实派生 `Rank 65b`”这件事来说，它已经很偏 hard 了。

## 3) 现有证据里有没有“可救信号”？
**有，但更像主题迁移，不像原命题可救。**

### 可救信号 1：crowding / liquidation 信息本身是活的
`2026-03-24_0631_liquidation-consensus-cascade-continuation-alpha.md` 很明确：
- `funding + OI 背离 + liquidation cluster` 更像**事件驱动延续 raw alpha**；
- 它的自然表达是完整 `entry / exit / timeout / cost` 策略骨架；
- 重点不再是“什么时候恢复三条旧 setup 的资格”，而是“级联事件本身能不能交易”。

这说明：
- 原 `Rank 65` 抓到的母主题没错；
- 但它把主题写成 `post-event re-arm gate`，大概率是职责放错层。

### 可救信号 2：basis / funding 更像独立 raw alpha，不像 15m shared re-arm
近几天的多条 digest 都在重复同一件事：
- `2026-03-23_1632_perp-premium-gap-mean-reversion-fullstack.md`
- `2026-03-30_2344_current-next-funding-closecost-carry-alpha.md`

这些新证据的共同指向是：
- `basis / funding` 若要活，往往应该写成**可独立成交、可过成本门槛的 raw alpha / carry / relative-value**；
- 而不是继续硬塞回 `15m` 三条线共用的 `stress reset / re-arm` 背景门。

### 但这些新证据也顺手证明：原命题不好救
最关键的一点仍然是：
- 原 clean replication 失败的方式不是“效果差一点”；
- 而是 **strict proxy 下连 event coverage 都没有**。

这会直接限制任何“窄修补”：
- 你只要保持原命题血缘（shared、15m、public proxy、resetComplete/re-arm），就很容易再次撞上 coverage=0；
- 一旦为了救它而明显放松阈值，就不再是原命题的诚实派生，而是在重写新东西。

## 4) 最值得改的唯一一刀是什么？
如果硬保留原线血缘，唯一还算诚实的一刀只能是：

**把 `shared post-stress re-arm gate` 改成 `单一事件族专用的 post-shock abstain / re-arm state`，先只服务一个最强事件主语，而不是三条线共用。**

也就是：
- 不再把 `basis neutral + OI flush + ATR compression` 写成 generic shared gate；
- 只保留一个最可复核的 event family（例如明确的 liquidation / crowding shock aftershock）；
- 先回答“event 后这段 dirty zone 要不要 abstain / cooldown”，而不是顺手给三条 base setup 同时发 re-arm 许可。

但这刀**本轮仍不值得写成新的 derived hypothesis**，因为：
1. 它已经不再是原 `Rank 65` 的小修小补，而是在把 shared gate 改写成单事件状态机；
2. 最近 digest 已经把更诚实的剩余价值迁移到 event-driven raw-alpha family；
3. 若现在硬写 `Rank 65b`，大概率只是把已迁移出去的 residual 硬绑回旧编号，反而模糊原 `park` 的审计边界。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。**

本轮结论：`keep_park`

## 为什么不是 `soft_reframe_candidate`
因为这次不是“distinct residual 还在，只是证据不够”；
而更像：
- 原 `Rank 65` 的最佳剩余已经迁移成别的主语：
  1. `crowding / liquidation cascade` 的 event-driven raw alpha；
  2. `basis / funding carry / premium-gap` 的 relative-value / carry raw alpha；
  3. 极少数情况下才是数据完整性 / 风险层。
- 这些都不再是 `Rank 65b` 这种旧血缘派生该承接的东西。

换句话说，**原命题真正剩下的，不属于“再窄一点的 Rank 65b”，而属于别的 family。**

## 本轮按模板回答
1. **原 rank 为什么 park？**
   - 因为原 `15m` 三线共用 `resetComplete / re-arm gate` 在 frozen 公开代理口径下出现了 `stress_event=0`、`reset_complete_bars=0` 的 coverage fail；三臂结果完全一样，说明 gate 没有实际筛选作用。
2. **它更像 hard park 还是 soft park？**
   - `soft park`，但比原审计时更偏 hard。
3. **有没有“可救信号”？**
   - 有；但信号在指向 crowding / liquidation event-driven raw alpha 与 basis / funding raw alpha，而不是救原 `Rank 65` 本身。
4. **最值得改的唯一一刀是什么？**
   - 若硬改，只能把 shared `re-arm gate` 收窄成单一事件族专用的 `post-shock abstain / re-arm state`。
5. **是否值得形成新的 derived hypothesis？**
   - 不值得。
6. **为什么不写 `Rank 65b`？**
   - 因为唯一能活下来的残余已经迁移到更独立的新主语；硬写成 `65b` 会模糊原 `park` 的审计边界，也会和更新的 crowding / carry raw-alpha family 重叠。

## 最终结论
- 原 `park` verdict：**保留**
- 本轮状态：**`keep_park`**
- 一句话总结：
  - **Rank 65 不是在证明 perp stress 没信息，而是在证明“15m 三线共用 resetComplete / re-arm gate”这版写法不诚实；最近新增证据把残余价值迁移到 crowding / liquidation 事件驱动 raw-alpha 与 basis / funding raw-alpha family，当前不诚实再派生 Rank 65b。**

## 对 queue 的最小写回
- `research/park_reframe/INDEX.md`：追加本轮索引；
- `docs/PARK_REFRAME_QUEUE.md`：只追加一条最近复盘记录；
- 不新增 `Rank 65b`；
- 不改 `docs/TODO.md` 顶部排班。

## Git / 提交
- 本轮未提交。
- 原因：工作区长期存在大量无关脏文件；本轮只做最小必要文本改动，避免混提。
