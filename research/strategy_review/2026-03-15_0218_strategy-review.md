# 2026-03-15 02:18 UTC · Strategy Review（paper-trading 导向微调）

## 本轮一句话判断

Jerry 这次反馈是对的：`bot2` 不该只做 `bot3` 的督工，也不该停留在“把三条收口线讲清楚”的层面；当前更高目标应该是**尽快判断谁最早有资格进入 paper trading / 伪实盘，以及离 admission 还缺哪一个 gate**。

## 当前 strongest evidence

1. **EMA 线现在最像“可先拿去做 baseline paper trading”的对象，但必须收窄 deployment scope。**
   - `EMA baseline family final survivor map` 已经把边界压清：`60m crypto` 出局，`A股 weekly frontier` 出局，`A股 daily` 只剩 `创业板ETF 1d` 更像 survivor，`沪深300ETF 1d` 只是 `mixed / watch`。
   - 这说明 EMA 不是“全市场通用 baseline”，但已经足够进入下一步：把 surviving pockets 写成明确 deployment scope，而不是继续泛泛谈 family。

2. **breakout 线仍有价值，但更像 conditional alpha，不适合现在就包装成通用 short。**
   - `raw + avoid_fluctuating + pair-conditioned halfsize` 是当前默认主原型；
   - 更窄的 `context-conditioned / pure-test × up` 分支已经被诚实 park；
   - 这说明 breakout 线最缺的不是新变体，而是更硬的 admission verdict：到底够不够进 shadow paper trading。

3. **Fibonacci 当前已基本完成角色判断。**
   - 更像 `archived / optional filter`，不是近期该投入 paper trading 精力的对象。

## 当前 weakest / should-park lines

1. `Fibonacci` 不应再消耗主资源；保留 archived/filter 口径即可。
2. breakout 线不应再回去纠结 `confirm_1` 抢位或扩更多新变体。
3. EMA 线不应再继续补 `protocol / wording / closure-copy` 之类低杠杆微步。

## 下一步优先级 Top 1~3

### Top 1. EMA：把 final survivor map 压成 `paper-trading candidate spec`

要回答：
- 哪些 pocket 先进入 baseline paper trading / shadow book；
- 哪些 pocket 明确排除；
- `mixed / watch` 的 pocket 是先 shadow 观察还是先不做；
- 基础监控指标是什么。

### Top 2. breakout：给 `raw + avoid_fluctuating + pair-conditioned sizing` 一版更硬的 admission verdict

要回答：
- 它现在是否已经够资格进入 shadow paper trading；
- 如果还不够，缺的是 `test pocket` 迁移性、`down` 环境尾部，还是组合层资金曲线可信度。

### Top 3. 项目级：统一给出三条线的 `paper trading admission verdict`

建议至少固定成三档：
- `closest to paper`
- `needs one more gate`
- `park / archive`

避免后续继续把三条线当作“都同样重要”。

## 本轮改动

1. 更新 `docs/BOT2_STRATEGY_REVIEW_BRIEF.md`
   - 明确 bot2 的更高目标是：以尽快把最有希望挣钱的候选推进到 `paper trading / 伪实盘` 为核心；
   - 新增 `paper trading admission` 视角下的判断框架；
   - 明确可以不平均推进三条线，而是集中火力在最接近部署的一条线上。

2. 更新 `docs/BOT2_STRATEGY_REVIEW_CRON_PROMPT.txt`
   - 要求 bot2 每轮都显式回答：谁最接近 paper trading、还缺哪个 gate。

3. 更新 `docs/TODO.md`
   - 新增“当前更高目标（2026-03-15）”；
   - 重写“当前接力棒”，把已完成的 closure work 换成新的 deployment-facing Top 3。

4. 实际更新 cron payload
   - 已把 `bot2-strategy-review-40m` 的 system event prompt 同步成新的 paper-trading 导向版本。

5. 重建 plans 镜像
   - 已执行 `python3 scripts/build_plans_site.py`，同步 `plans/momentum_todo.html`。

## 网页 / 表达建议

1. `alpha_closure_board` 下一步应该显式出现 `paper trading admission verdict`，而不只是 `main alpha / conditional alpha / filter / park`。
2. `EMA / PSAR` 页面下一步该从“family 结论页”转向“candidate spec / deployment scope page”。
3. `support_breakout_v0` 页面下一步该从“follow-up 研究页”转向“是否够资格进 shadow paper trading”的 admission 页。

## cron / 节奏建议

1. **bot2 频率先不改，方向已改。**
   - 40 分钟节奏仍合适；真正该改的是判断目标，而不是频率。

2. **bot3 频率先不改，但默认任务要更结果导向。**
   - 当前 bot3 仍可保持 13m；但 bot2 后续应更积极地把它推向 `candidate spec / admission verdict / hard gate` 一类任务，而不是说明文小修。

3. **暂不改 bot7。**
   - 当前更关键的是把手头最接近部署的对象推进到 admission judgement，而不是再找更多新线索。

## 风险与不确定性

1. `EMA` 虽然最接近 baseline paper trading，但当前证据更像“market-specific survivors”，不是全市场通用模板。
2. breakout 仍是 `conditional alpha`，若 `test` 或组合层 honesty 不够硬，仍不应过早上 shadow book。
3. 当前这轮微调主要改的是 steering，不是新增回测证据；后面仍需要真实结果来支撑 admission verdict。
