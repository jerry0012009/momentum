# 2026-04-10 12:40 UTC — Rank 86 park reframe review

## 0) 本轮选择
- 选定条目：`Rank 86`
- 轮转理由：当前 `50+` 号段近期虽已多次覆盖，但 `Rank 86` 距上次 `bot6` 复盘（`2026-03-28`）已超过 7 天，且它属于 `80~110` 段里仍有明确历史 residual、但未在最近 7 天重复处理的 parked rank。
- 本轮目标：只判断 **原 `Rank 86` 是否还值得再派生一个新的窄 reframe hypothesis**；不改 `TODO` 顶部排班，不给 `bot2 / bot3` 新分工。

## 1) 原 rank 为什么 park
原 `Rank 86 / SignalPro penetration×ATR admission` 被 park 的原因，核心不是“penetration 主题完全没信息”，而是：
1. 它作为 **shared gate** 的写法不稳，时间稳定性不过关；
2. clean replication 后改善主要集中在更窄的 short-side / breakout family，而不是整个 shared admission 框架；
3. 原对象的可交易残余更像“只对 breakout-short 的 short-side penetration 质量有一点筛选价值”，不足以支撑继续把旧 `Rank 86` 当成完整 queue-facing 策略保留。

一句话：**被 park 的是原来的 shared-gate 角色，不是 penetration/ATR 这个局部语义本身。**

## 2) 它更像 hard park 还是 soft park
本轮判断：**`soft park`，但已明显向 `hard park` 靠拢。**

原因：
- soft 的地方在于：它历史上确实留下过一个可审计 residual——`penetration × ATR` 在 breakout-short short-side admission 上比原 shared 写法更诚实；
- hard 的地方在于：这条唯一残余后来已经被正式收窄、转译并消费成 `Rank 222`，不再是“尚未测试的可救空间”。

## 3) 有没有可救信号
有，但只剩 **一个已经被消费过的可救信号**：
- `penetration/ATR` 不适合作为 shared gate；
- 它更像 **breakout-short 专用、short-side only 的 admission clue**；
- 这条线后来已经被具体化为 `Rank 222 / breakout-short penetration×ATR short-admission reframe`。

也就是说，`Rank 86` 不是完全没有残余，**但残余已经不再“空着”等待 bot6 再发明一次新命名**。

## 4) 最值得改的唯一一刀是什么
若只看原 `Rank 86`，最值得改、而且也是唯一诚实的一刀，其实已经很清楚：

- **唯一主修改轴：把 `shared penetration×ATR admission gate` 降级成 `breakout-short short-side only admission`。**

这条单轴不是本轮新发现，而是历史上已经被提纯并落地过的那一刀。

## 5) 是否值得形成新的 derived hypothesis
本轮结论：**不值得。**

原因有三条，而且都足够 decisive：
1. **唯一诚实残余已被消费。**
   - `Rank 86` 的 residual 已经不是抽象可能性，而是被正式转写成 `Rank 222` 去做过 fresh intake / follow-up。
2. **消费后的对象也没有长成新的强宿主。**
   - `Rank 222` 首判虽一度 `keep_P1`，但 survivor 唯一 follow-up 后已经收口回 `background`，说明这条 residual 够得上“值得试一次”，但还不够支撑继续再衍生 `86c / 86d` 一类新条目。
3. **继续再派生只会重复命名，不会增加信息。**
   - 如果现在再从 `Rank 86` 起草一个新 hypothesis，本质上只会重复 `Rank 222` 已经试过的 breakout-short / short-side admission 语义，审计上属于 duplicate，不诚实。

## 6) trade on / trade off（仅用于说明为何本轮不再 draft）
历史上唯一值得 trade 的那一刀已经很明确：
- trade on：放弃 shared gate 幻觉，把 residual 收窄到 breakout-short short-side admission；
- trade off：trade density 与适用范围都会明显收缩，而且一旦 narrow 版本也只到接近打平，就不该继续靠更换包装续命。

当前状态下，这组 trade on / trade off 已经被 `Rank 222` 审计过一次，因此本轮不再重复 draft。

## 7) 本轮结论
- verdict: `keep_park`
- original verdict kept: `park`
- current classification: `soft park，但已明显向 hard park 靠；唯一可救轴已被 Rank 222 正式消费并在 follow-up 后回到 background，因此当前不诚实再派生新的 Rank 86c / Rank 86 reframe`

一句会改变后续动作的话：
> `Rank 86` 不是没有 residual，而是它唯一诚实的 residual 已经被 `Rank 222` 用掉了；既然消费后的宿主也没长成新的前排对象，就不该再从旧 rank 继续分叉命名。

## 8) 文件与流程影响
- 更新 `research/park_reframe/INDEX.md`
- 更新 `docs/PARK_REFRAME_QUEUE.md`
- 不改 `docs/TODO.md`
- 不新增 derived hypothesis 提案

## 9) git / 提交说明
本轮只做最小必要文档改动。

未做 commit：当前 git 工作区存在无关脏文件 / 未跟踪文件，按要求不混提。