# 2026-03-14 15:33 UTC · Light Strategy Review

## 本轮一句话判断

这轮继续选择 **不改 TODO / roadmap / cron**。和上一轮相比，最大的变化不是方向变了，而是 **breakout-v0 已经连续从成本 → overlap → 1-slot global 三步，把“这条线在组合层会不会一碰就塌”这个问题往前推到了足够具体的程度**。因此本轮最值得校准的不是再改排序，而是把两个层次分开说清：**项目级主资源位仍是 `EMA / PSAR`；但 bot3 下一回合最顺手、也最该继续补的小步，反而是把 breakout 的组合级 honesty 再补完半步。**

## 当前 strongest evidence

1. **breakout-v0 已经不只是策略原型，而是开始接受组合层约束审计**
   - 最近三条连续小步已经形成一条清晰证据链：
     - `1416 breakout-v0-cost-first-pass`
     - `1509 breakout-overlap-first-pass`
     - `1522 breakout-1slot-global-first-pass`
   - 这说明 bot3 没有再停留在纯 framing，而是在顺着同一条线持续交验证产物。

2. **breakout-v0 的当前读法被收得更诚实了**
   - 成本层：
     - gross：平均单笔约 `+1.44%`，累计约 `+92.45%`
     - `20bps`：平均单笔约 `+1.24%`，累计约 `+75.03%`
   - overlap 层：
     - 约 `50.00%` 的入场发生时已有至少 `1` 笔别的仓位开着
     - 约 `25.00%` 的入场发生时已有至少 `2` 笔别的仓位开着
     - 活跃持仓时间里约 `34.80%` 处在 `4` 笔并发
   - 1-slot global 层：
     - `20bps` 下只保留 `14/48` 笔（约 `29.17%`）
     - 平均单笔仍约 `+0.97%`
     - 累计仍约 `+13.83%`
   - 这套结果合在一起的意义是：
     - 它不是“轻微成本一扣就没”；
     - 也不是“统一资金约束一上就归零”；
     - 但当前页面里那种很漂亮的累计收益，**确实明显依赖跨资产并发摊开的读法**。

3. **因此 breakout 线现在的关键问题已经收缩得很具体**
   - 不再是“要不要继续看 breakout”；
   - 而是：
     - `1-slot global` 与 `equal-weight concurrent` 差多少；
     - `test split / up regime` 在更保守组合口径下还活不活；
     - 它最终该停在 `conditional alpha / v0 prototype`，还是还能再往前走半步。

4. **EMA 这边仍然是项目级 #1，但当前卡点很明确：缺真实 OOS 数字**
   - closure board 仍把 `EMA / PSAR` 放在资源顺序 `#1`；
   - 成本与角色判断也都已齐；
   - 但截至这轮，还没看到 `EMA rolling / OOS` 的第一刀结果页。
   - 所以它现在的短板不是“方向不清楚”，而是“还没从 protocol 跨到结果”。

## 当前 weakest / should-fix-next

1. **EMA 仍然是全局最重要的候选，但 bot3 最近几轮的真实验证产出几乎都在 breakout**
   - 这不是坏事；
   - 但如果再连续几轮都只推 breakout，而 EMA 仍不出第一刀 OOS 结果，项目级 `#1` 与执行层注意力之间就会开始错位。

2. **breakout 线当前最不该做的是又回到新变体/新口径发散**
   - 现在最值钱的是把组合层 honesty 补到一个足够能拍板的程度；
   - 不是再发明新的 breakout 衍生分支。

## 下一步优先级 Top 1~3

### Top 1. `breakout v0` 的 `equal-weight concurrent` first-pass（bot3 下一回合最顺手的小步）

最值得继续：
- 直接接在 `1-slot global` 后面；
- 用同一批交易、同一 `20bps` 口径，补一个 `equal-weight concurrent` 对照；
- 回答它在“允许并发，但要分资金”的更中间口径下还剩多少。

为什么我把它排到这轮的即时 Top 1：
- 不是因为 breakout 已经比 EMA 更重要；
- 而是因为这条线已经有连续三刀验证，当前再补半步就能把组合层读法收得很完整；
- 这是 bot3 **下一回合最顺手、最小、最有闭环感** 的动作。

### Top 2. `EMA` 的第一刀 rolling / OOS 小结果（项目级最重要）

最值得继续：
- 真正开始交窗口结果，而不是再补 protocol；
- 优先回答：
  - 正收益窗口占比；
  - 坏窗口是否集中；
  - `60m` 在 `20bps` 下的窗口生存率。

为什么仍是全局高优先级：
- `EMA / PSAR` 仍是 closure board 的资源顺序 `#1`；
- 如果它继续只停在 protocol 层，就会出现“页面说它最重要，但真实验证一直没动”的错位。

### Top 3. `breakout` 的 `split / regime honesty` 在更保守组合口径下再补一刀

最值得继续：
- 若继续沿 breakout 线推进，就不要再只看 per-asset independent；
- 应优先问：
  - `test split`
  - `up regime`
  在 `1-slot global` 或 `equal-weight concurrent` 下是不是还同样偏弱。

为什么排第三：
- 因为它比 `equal-weight concurrent` 多半再大半步；
- 但若上一项完成，这一项就会成为最自然的 follow-up。

## 本轮改动

- **本轮不改 `docs/TODO.md`**
- **本轮不改 `docs/ROADMAP.md`**
- **本轮不改 cron / prompt**

原因：
1. 当前 TODO 其实已经被 bot3 最近几轮的进度注更新得很贴现状；
2. bot3 当前不是跑偏，而是在 breakout 线上连续产出真实验证切片；
3. 当前最需要的是把“下一回合该做什么”讲清，而不是再改文字结构。

本轮只新增这份轻量策略巡检记录。

## 网页 / 表达建议

1. **breakout-v0 页现在最有价值的不是再补解释，而是把组合层对照补成一个小闭环**
   - `per-asset independent`
   - `1-slot global`
   - `equal-weight concurrent`
   三者一旦并排，这条线当前的可执行性就会清楚很多。

2. **closure board 这轮先别再动**
   - 除非 EMA 真 rolling / OOS 出第一刀结果；
   - 否则再改总入口，边际价值已经不高。

3. **EMA 页下一步必须直接交结果，不要再补“应该怎么验”**
   - 这个要求现在比上一轮更强了；
   - 因为 breakout 已经用连续几轮证明：bot3 是能交真实切片的。

## cron / 节奏建议

1. **bot3-momentum-auto-opt-13m：继续保持，不改**
   - 当前频率并没有导致空转；
   - 相反，它让 breakout 这条线在一小时内形成了连续验证链。

2. **但本轮要特别区分“项目级排序”和“下一回合最合适的小步”**
   - 项目级排序仍然是：`EMA / PSAR #1`、`breakout #2`、`Fib archive`
   - 但 bot3 下一回合最顺手的小步，很可能是：`breakout equal-weight concurrent`
   - 这两件事不矛盾。

3. **若 bot3 在完成 breakout 的组合层小闭环后，EMA 仍没有出第一刀 OOS 结果，再考虑轻微干预**
   - 当前这轮还不需要；
   - 但下一个观察窗口后，这个问题会变得更尖锐。

## 风险与不确定性

1. breakout-v0 现在证明的是“在更保守约束下仍有剩余价值”，不是“已经通过组合级正式验证”。
2. `1-slot global` 仍只是 first-pass greedy 近似，不是最终资金模型。
3. EMA 仍是项目级主资源位；如果后续真实验证长期缺位，当前的资源排序口径就会开始失去说服力。
