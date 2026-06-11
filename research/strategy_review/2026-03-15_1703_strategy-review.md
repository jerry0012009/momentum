# 2026-03-15 17:03 UTC · Light Strategy Review

## 本轮一句话判断

这轮项目级排序仍然不变：`EMA = closest to paper`，`breakout = one_more_gate`，`Fibonacci = park`。但 **EMA 当前最缺的 gate 又往前推进了一格**：bot3 刚刚把 `Crypto-1d / 贵州茅台-1d` 的断流清零，又把 `创业板ETF 1d / 沪深300ETF 1d` 的 A 股日频 refresh 源从 fallback 升成了 `Eastmoney live`；也就是说，EMA 现在最显性的 source-risk 已基本拆掉。**因此本轮最小必要干预，不再是继续催它修 source，而是把下一步重新收紧成：沿同一张 live ledger 继续交真实 `market-close refresh / week-1 review` 结果。**

## 本轮先检查了什么

1. repo 状态与最近 3 条 optimization loop：
   - `2026-03-15_1638_ema-refresh-continuity.md`
   - `2026-03-15_1646_ema-refresh-dependency-audit.md`
   - `2026-03-15_1701_ema-eastmoney-live-source.md`
2. 当前 cron 状态：
   - `bot3-momentum-auto-opt-13m`：`lastRunStatus = ok`、`consecutiveErrors = 0`
   - `bot2-strategy-review-40m`：正常
   - `bot7-quant-digest-4h`：正常
3. `docs/TODO.md` 当前 deployment-facing 剩余动作
4. EMA 主报告与 `alpha_closure_board` 当前 admission / deployment 口径

## 当前 strongest evidence

### 1) bot3 已经真正把 EMA 的 source-risk 主 blocker 拆掉了

最近 3 条 EMA 推进不是近义 wording，而是连续三步真实运行支撑：
- `16:38`：修复 `Crypto-1d / 贵州茅台-1d` refresh continuity
- `16:46`：把 all active `1d` lanes 压成 dependency audit
- `17:01`：把 `创业板ETF 1d / 沪深300ETF 1d` 从 fallback 升成 `Eastmoney live`

这说明 bot3 不是只在写“应该怎么跑”，而是真把 EMA 从 `can-ledger but source-risk` 推到了更接近 **可连续运行** 的位置。

### 2) EMA 当前最缺的 gate 已从 `data continuity / source-risk` 切回 `真实前瞻续写 honesty`

现在最新口径已经是：
- active `1d` lanes 约 `live = 5`
- `cache fallback = 0`
- `data unavailable = 0`

这意味着 EMA 当前最显性的运行 blocker 已经不再是：
- 哪条 lane 断流
- 哪条 lane 还靠 cache
- primary 是否还卡在 source-risk

而是：
- **这张账本连续 refresh 几轮之后，primary / front-queue secondary / shadow lane 的真实状态会不会开始转弱**。

换句话说，当前最需要的新证据不再是“数据能不能来”，而是“来了之后，forward refresh / week-1 review 是否还守得住”。

### 3) breakout / Fibonacci 这轮没有新证据足以改写总排序

- **breakout**：当前仍是 `one_more_gate`，而且 same-sample retrospective slicing 已冻结；没有新的 `pure-test / down-tail` overturn evidence。
- **Fibonacci**：继续 `park / archive`。

因此当前最值得集中火力的对象仍然是 EMA，而不是重新平均推进三条线。

## 当前 weakest / should-park lines

1. **Fibonacci**：继续 archive。
2. **breakout 的 same-sample micro-slicing**：继续冻结；除非出现新的 shadow / forward pure-down 命中。
3. **EMA 的 source-risk 近义说明页**：在 `live = 5 / fallback = 0 / unavailable = 0` 之后，继续补这类文案边际价值很低。

## 本轮最小必要干预

### 只做 1 个动作：把 EMA 下一步从“修 source”切回“连续真实 refresh / week-1 review”

已在 `docs/TODO.md` 新增：

- `EMA：沿同一张 live ledger 连续落下下一轮 market-close refresh / week-1 review 结果（不要在 source-risk 已清零后继续补近义 source 文案）`

目的很明确：
- 不改项目级总排序；
- 不改 cron；
- 不改 `alpha_closure_board` 主口径；
- 只把 bot3 的下一步从“修运行通道”推进到“继续交真正的前瞻运行结果”。

## 为什么这轮还要动，而不是说“现在别再管了”

因为当前已经到了一个典型的切档点：
- 如果 bot2 这轮不再收紧，bot3 很可能继续沿 `source-risk / dependency / live-source` 这一条写下一层近义 audit；
- 但 source-risk 最显性的 blocker 已经清掉了；
- 现在最有杠杆的新问题，已经是 **真实 refresh / week-1 review 会不会开始打出 yellow/red**。

所以这轮最合理的小动作不是再改 admission 结论，而是：
**逼下一轮直接交连续前瞻续写结果。**

## 下一步优先级 Top 1~3

### Top 1. EMA：沿同一张 live ledger 继续写 `market-close refresh / week-1 review`

重点回答三件事：
1. `创业板ETF 1d` primary 是否继续守住
2. front-queue secondary 是否需要 `keep / stricter recheck / demote`
3. week-1 review 是否第一次出现 `yellow / red`

### Top 2. breakout：继续维持 `one_more_gate`

在没有新的 `pure-test / down-tail` forward/shadow 命中前，不 reopen 同一样本里的 retrospective slicing。

### Top 3. 若 EMA 后续继续推进，优先看前瞻 honesty，不再回到 source 说明分支

现在更该盯：
- 连续 refresh
- review verdict
- demote / rollback 是否真的触发

而不是再补“数据源从哪来”的近义说明。

## 本轮改动

- 已编辑 `docs/TODO.md`
  - 新增并前推：`EMA 连续 market-close refresh / week-1 review`
- 新增 review 记录：
  - `research/strategy_review/2026-03-15_1703_strategy-review.md`
- 本轮不改：
  - `alpha_closure_board` 主排序
  - `bot2 / bot3 / bot7` cron 频率
  - breakout / Fibonacci 项目级结论

## 网页 / 表达建议

- 这轮不需要再改 closure board 主文案。
- 当前网页口径已经足够诚实：EMA 是 `closest to paper`，而且 source-risk 的主 blocker 已被最新运行结果显著压低。
- 下一次真正值得改网页，不是再补 source-risk 解释，而是：
  - 当同一张账本连续写出几轮 `market-close refresh`
  - 或第一次出现明确 `week-1 yellow/red review`
  再把这些真实运行态回写到入口页。

## cron / 节奏建议

- `bot2 40m`：不改
- `bot3 13m`：不改
- `bot7 4h`：不改

原因：
- 当前不是调度问题；
- 也不是 source 还不通；
- 当前最该推进的是 **live ledger 的连续前瞻续写 honesty**。

## paper trading admission verdict

- **closest to paper：EMA baseline family**
  - 当前最缺的 gate 已从 `operational data continuity / source-risk` 进一步推进为：
  - **连续 `market-close refresh / week-1 review` 的 forward honesty**
- **needs one more gate：support_breakout_v0**
  - 仍缺新的 `forward / pure-test / down-tail honesty`
- **park / archive：Fibonacci**

## 风险与不确定性

1. 这轮清掉的是 source-risk，不是新增 alpha 证据本身。
2. 即使 `live = 5 / fallback = 0 / unavailable = 0`，也不等于 EMA 已经通过 paper admission；真正的 admission honesty 仍要看连续 refresh / review。
3. 若后续几轮前瞻 refresh 很快出现 `yellow/red`，当前“closest to paper”的优势也会变窄。

## 本轮一句话结论（给 Jerry）

**EMA 这条线现在已经不再卡在“数据源通不通”了；最该继续的不是再修 source，而是沿同一张 live ledger 连续交出几轮真实 refresh / week-1 review，让它用前瞻结果证明自己到底能不能守住 `closest to paper`。**
