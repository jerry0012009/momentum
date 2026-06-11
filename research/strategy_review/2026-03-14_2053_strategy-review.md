# 2026-03-14 20:53 UTC · Light Strategy Review

## 本轮一句话判断

这轮的主判断是：**先不继续改 TODO / prompt / cron；当前最合理的动作是维持上一轮刚刷新的接力棒，并把观察点收窄成“bot3 下一棒到底有没有真正接上”。**

原因不是 bot2 该变保守，而是目前可见的最新 bot3 durable artifacts 仍停在 `20:03` 左右，而上一轮 `20:13` 刚把 `Current relay baton` 刷新成新的未完成 Top 3。也就是说：**当前板子入口层并没有再次过时，真正有待确认的是 bot3 是否会按新接力棒继续推进，而不是 bot2 现在就再改一轮。**

## 当前 strongest evidence

1. **上一轮刷新的接力棒仍然是对的，没有被最新证据推翻**
   - 目前 TODO 顶部的 `当前接力棒（2026-03-14 20:13）` 已经把“刚完成的旧任务”清掉，并明确把下一棒收窄到：
     1. `avoid_fluctuating -> hourly portfolio path / sizing honesty`
     2. `EMA baseline family survivors -> family-level honesty`
     3. `raw breakout -> 更正式 sizing / portfolio honesty`
   - 截至本轮可见证据，还没有出现新的结果足以推翻这三个顺序。

2. **breakout 线当前已完成的收口已经足够支持“先别再纠结 confirm_1 抢位”**
   - `confirm_1` 在更诚实口径下的结果已很完整：
     - `raw`：约 `75.03% / 19.40% / 14.04% / 13.83%`
     - `confirm_1`：约 `59.38% / 12.04% / 11.54% / 5.06%`
       （per-asset / entry-only equal-weight / hourly path / 1-slot）
   - 且 `hourly path` 下回撤也没更优：
     - `raw` max DD 约 `-12.03%`
     - `confirm_1` 约 `-13.60%`
   - 同时 raw 在 `20bps hourly path` 下的弱口袋也仍存在：
     - `test`：约 `-2.92%`
     - `up`：约 `-1.99%`
   - 所以当前 breakout 线的下一步，确实更应该看 `avoid_fluctuating` 能不能改善这些弱口袋，而不是继续在 `confirm_1` 身上绕圈。

3. **EMA 线当前的正确问题也已经被收窄，不是再回去包装 60m**
   - 目前 family survivors 结果已经够清楚：
     - `EMA non60m (1d + 1wk)`：`18/18` gross 为正，`20bps` 下也 `18/18` 存活，positive-only median breakeven cost 约 `2066.8bps`
     - `EMA 60m`：`7/9` gross 为正，`20bps` 后只剩 `4/9`，positive-only median breakeven cost 约 `27.5bps`
   - 这意味着：
     - `EMA 60m crypto` 是 fail pocket；
     - 但 `non60m baseline family` 仍然厚得多，值得继续做更诚实的 family-level honesty。
   - 因此当前接力棒把第二优先级放到 `EMA family-level honesty`，仍然是合理的。

4. **当前最大的新增风险不是方向错，而是 bot3 是否短暂停顿 / 尚未接上新 baton**
   - 截至这轮可见产物，bot3 的最新 durable artifact 仍停在 `20:03` 附近；
   - 而 `Current relay baton` 是 `20:13` 刚刷新过的。
   - 因此当前最该观察的，不是再改板子，而是看 bot3 下一轮是否真的接上：
     - `avoid_fluctuating hourly path`
     - 或 `EMA family-level honesty`

## 当前 weakest / should-watch-now

1. **当前最需要盯的不是研究结论，而是“接力棒是否被真正接住”**
   - 若下一轮仍没有新的 visible artifact 落在新的 Top 3 上，
   - 那说明问题不在排序本身，而更可能在：
     - bot3 选题执行没跟上；
     - 或可见产物落盘节奏出现停顿。

2. **当前最不该做的是 bot2 再连续重写 relay baton**
   - 上一轮刚完成一次高杠杆刷新；
   - 这轮再改，容易把“入口层稳定性”本身又打散。

## 下一步优先级 Top 1~3

### Top 1. breakout：`avoid_fluctuating -> hourly portfolio path / sizing honesty`

最值得继续：
- 直接回答 `avoid_fluctuating` 是否比“换成 `confirm_1`”更能改善：
  - `test`
  - `up`
  这两个当前最弱口袋。

为什么排第一：
- 因为 `confirm_1` 会不会抢位这件事已经基本看清；
- breakout 线当前最值钱的未决问题，就是环境 gate 在更正式组合口径下有没有真帮助。

### Top 2. EMA：`baseline family survivors -> family-level honesty`

最值得继续：
- 从“non60m 还活着”推进到“哪些 `asset × freq` 真值得保留”；
- 这比继续包装 `EMA 60m` 有高得多的边际价值。

为什么排第二：
- 因为当前 EMA 线已经完成从“60m hopeful”到“family survivors”的换题；
- 现在该把第二步做完。

### Top 3. breakout：raw 的更正式 sizing / portfolio honesty

最值得继续：
- 若继续沿 breakout 线推进，再补一个更正式但仍克制的 sizing / portfolio follow-up；
- 让它从“first-pass realism 足够”进一步靠近“策略层 truthfulness 足够”。

为什么排第三：
- 因为这条线仍值得继续；
- 但当前顺序上，仍排在 `avoid_fluctuating` 与 `EMA family-level honesty` 之后。

## 本轮改动

### 1) 本轮不改 `docs/TODO.md`
- 理由：上一轮刚把接力棒刷新成新的未完成 Top 3；
- 截至本轮，可见证据还没有推翻这一排序；
- 当前更值得做的是观察 bot3 是否接棒，而不是再重写入口层。

### 2) 本轮不改 `docs/ROADMAP.md`
- 理由：没有大方向漂移；
- 现在的问题是执行接力，而不是 roadmap 本身失效。

### 3) 本轮不改 cron / prompt
- 理由：目前没有看到 bot3 又退回 protocol / cleanup 碎微步；
- 当前更该先给新接力棒一个完整观察窗口。

本轮只新增这份轻量策略巡检记录。

## 网页 / 表达建议

1. **当前不需要再继续改 closure board / TODO 的表达层**
   - 入口层已经够清楚；
   - 现在更重要的是让新的 Top 3 真被执行掉。

2. **EMA 页下一步仍应坚持 family-level honesty，不回头包装 60m**
   - 这条边界本轮不变。

3. **breakout 页下一步仍应聚焦 `avoid_fluctuating` 与更正式组合层**
   - 不是再回头做 `confirm_1` 身份讨论。

## cron / 节奏建议

1. **bot3-momentum-auto-opt-13m：本轮继续保持当前频率与口径**
   - 当前最关键的不是继续改规则；
   - 而是观察新接力棒是否在下一轮被真正接住。

2. **bot2-strategy-review-40m：继续保持**
   - 本轮 bot2 最正确的动作就是“不乱改已经刚更新过的入口层”。

3. **下一轮 bot2 的核心观察问题已经很窄**
   - 只看：
     1. 是否出现 `avoid_fluctuating hourly path`；
     2. 或是否出现 `EMA family-level honesty`。
   - 若仍都没有，再考虑是“bot3 暂停/停顿问题”而不是“排序问题”。

## 风险与不确定性

1. breakout v0 当前仍只是更诚实的组合级 first-pass，不等于已通过正式 portfolio engine 级验证。
2. EMA 当前只是把 `60m fail pocket` 与 `non60m survivors` 切开了，还没做完 family-level honesty。
3. 截至本轮可见产物，bot3 最新 durable artifact 仍停在 `20:03` 左右；若下一轮仍无新 artifact，需要开始把注意力转向“执行是否卡住”，而不只是继续做研究排序。
