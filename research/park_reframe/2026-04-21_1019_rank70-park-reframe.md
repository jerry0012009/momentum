# 2026-04-21 10:19 UTC｜Rank 70 park reframe

## 轮次定位
- 对象：`Rank 70 / fast-entry slow-exit handoff spine`
- 原始结论：`park / evidence pool`
- 本轮结论：**`keep_park`**
- 结论标签：`soft park（但已明显向 hard park 靠，且 residual 更接近被新 raw-alpha 宿主吸收）`

## 这轮为什么看 Rank 70
- 按 `BOT6_PARK_REFRAME_BRIEF` 与 `PARK_REFRAME_QUEUE` 当前规则，默认优先看 `Rank 50+`。
- 最近 `7` 天已复盘过 `Rank 50 / 59 / 62 / 72 / 74 / 77 / 79` 等，但 **没有** 复盘 `Rank 70`。
- `Rank 70` 属于典型的 `overlay / post-entry spine` 对象，正适合回答：它是不是还值得收窄成一个 queue-facing 的窄 reframe，还是应该继续留在 park。

## 回看的原始证据
### 1) 原 rank 为什么会被 park
根据 `research/optimization_loop/2026-03-18_2253_rank70-source-intake.md` 与 `2026-03-18_2312_rank70-clean-replication-park.md`：
- `Rank 70` 原本想解决的是：**entry 不动，只重写 post-entry 持仓时钟**。
- 它的最小 clean replication 比了四臂：
  - `baseline_exit`
  - `all_fast_fail`
  - `all_slow_trailing`
  - `handoff_exit`
- 真正把它压回 `park` 的不是“完全没反应”，而是 **shared handoff spine 不统一**：
  1. `handoff` 只在 `ema_psar_long` 上少亏，但仍是负；
  2. `fib_retest_long` 上真正变好的是 `all_slow_trailing`，不是 `handoff`；
  3. `breakout_short` 上三种改写都比 baseline 更差；
  4. `mean_giveback_after_handoff≈78.60%`，说明 handoff 后利润大多吐回去。
- 所以原 `park` 的审计含义很清楚：
  **问题不在“exit 重要不重要”，而在“快 entry / 慢 exit handoff”没有形成一个便宜、统一、可共享的 spine。**

## hard park 还是 soft park
我这轮判断：**更像 soft park，但已经比 3 月 18 日更接近 hard park with absorbed residual。**

为什么不是直接写 hard park：
- `fib_retest_long + all_slow_trailing` 这条局部 pocket 仍说明：**慢退出** 这个方向本身不是完全没信息。
- 也就是说，`Rank 70` 不是“主题彻底死亡”，而是 **shared handoff overlay 这层写法失败了**。

为什么又说它已经明显向 hard park 靠：
- 唯一还活着的信号，并没有支持“保留一个跨 setup 共用的 handoff spine”；
- 它更像在说：**某些完整策略壳，各自需要各自的 terminal exit 设计**。
- 一旦这样改写，残余就已经不再是原 `Rank 70` 的 queue-facing 窄派生，而是在迁移到新的完整 raw-alpha / shell 宿主里。

## 这轮有没有新的“可救信号”
有，但很弱，而且**不支持继续保留 old Rank 70 的 queue-facing 身份**。

### 可救信号 1：局部慢退出 pocket 仍存在
原 clean replication 里，`fib_retest_long` 明显是 `all_slow_trailing` 优于 `handoff`。这说明：
- 可救的不是“两段式 handoff 机制”；
- 而是 **某类 setup 的 setup-local slow exit**。

### 可救信号 2：4 月 19~21 的新 repo / digest 更支持“exit 必须跟完整壳一起定义”
这轮补看的新证据包括：
- `2026-04-19_2132_bbtouch-oppositeband-maker-shell.md`
- `2026-04-21_0607_mefai-scalping-microtrend-volspike-shell.md`

它们的共同点不是“都证明 slow exit 必胜”，而是：
- 真正还能站住的 exit 逻辑，都是 **跟 entry / admission / timeout / cost 一起写成完整 shell**；
- 例如 `opposite-band maker exit`、`15m hard-timeout` 这类退出，并不是可无损抽象成一个 setup-agnostic shared handoff spine；
- 这反而进一步确认：`Rank 70` 若还有信息，也更像新的 **setup-local exit shell / raw-alpha 宿主的一部分**，而不是旧的共享 handoff overlay。

## 最值得改的唯一一刀是什么
如果硬要给出 **唯一最自然的一刀**，它会是：

**把“shared fast-entry -> slow-exit handoff spine”收窄为“仅针对单一 setup 的 terminal slow-exit / hard-timeout exit shell”，不再追求跨 setup 共用。**

但这刀为什么我最终没有 draft：
- 它已经不只是对 `Rank 70` 做窄修；
- 它其实是在改对象的“职责边界”：
  - 从 `shared post-entry management spine`
  - 变成 `setup-local full-shell exit design`
- 这会让它与最近新 intake 的完整 repo shell（如 opposite-band / timeout / maker-first 一类）高度重叠，**不再是诚实的 Rank 70b**。

## 是否值得形成新的 derived hypothesis
**不值得。**

原因有三层：
1. 原 blocker 没被推翻：`handoff` 依旧没有形成跨 setup 统一增量；
2. 唯一残余只支持 `setup-local slow exit`，不支持 `shared handoff spine`；
3. 4 月 19~21 的新增证据把 exit 主题更明确地推向 **完整 raw-alpha / shell 宿主**，而不是把 old Rank 70 救回 queue-facing 窄派生。

换句话说：
- `Rank 70` 没有被“救活”；
- 被救活的是一个更上位的新判断：**exit 逻辑如果真有 edge，应该被写进完整策略壳，而不是单独抽成共享 handoff overlay。**

## 本轮回答（按 brief 必答）
### 1. 原 rank 为什么 park
因为 minimal clean replication 证明：`handoff_exit` 没有形成跨 setup 的统一便宜增量，且 `giveback_after_handoff` 很高，真正局部有效的是某个 setup 上的 `all_slow_trailing`，不是 shared handoff 本身。

### 2. 更像 hard park 还是 soft park
**soft park，但已更接近 hard park with absorbed residual。**

### 3. 有没有“可救信号”
有，但只剩 **setup-local slow exit** 这个残余；它不能诚实地救回 old Rank 70 的 shared overlay 身份。

### 4. 最值得改的唯一一刀是什么
若只谈自然修改轴，唯一一刀是：
**放弃 shared handoff，收窄成单一 setup 的 terminal slow-exit / hard-timeout exit shell。**

### 5. 是否值得形成新的 derived hypothesis
**否。** 因为这刀已经把对象改写成新的完整 shell 宿主，超出了 old Rank 70 的诚实窄派生边界。

## 最终结论
**`keep_park`**

一句话收口：
> `Rank 70` 的原 `park` 应保留；4 月 19~21 的新增 repo / digest 证据没有把 old fast-entry slow-exit handoff spine 救回 queue-facing 窄派生，反而更明确地说明：若 exit 逻辑还有 residual value，它也更像新的 setup-local full-shell / raw-alpha 宿主，而不是足以再诚实派生 `Rank 70b`。

## 文件与工作区说明
- 本轮只新增本日志，并准备最小更新 `research/park_reframe/INDEX.md` 与 `docs/PARK_REFRAME_QUEUE.md`。
- `git status` 显示工作区存在大量与本轮无关的脏文件；本轮不做混提。