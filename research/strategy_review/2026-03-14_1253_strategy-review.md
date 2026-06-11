# 2026-03-14 12:53 UTC · Light Strategy Review

## 本轮一句话判断

这轮继续选择 **不改 TODO / roadmap / cron**。原因不是没事可做，而是最近 3 条 bot3 loop 已经在正确服务三条收口线：`EMA / PSAR` 刚补完成本页与 closure-board framing，`breakout-v0` 刚补完 plain-language 定位；当前最有价值的 bot2 动作，是把资源顺序再收紧一格：**优先做 EMA 的 rolling / OOS honesty，其次做 breakout-v0 的成本 / 执行 / rolling honesty，Fibonacci 则继续按 archived / optional filter 口径收住，不再占主研发位。**

## 当前 strongest evidence

1. **EMA / PSAR 线现在已经不只是“谁 gross 更好看”，而是有了更像决策页的成本读法**
   - 最新 closure 入口已经明确：
     - `EMA` 的 positive-only median breakeven round-trip cost 约 `383.2bps`
     - `PSAR` 约 `300.9bps`
     - 到 `60m`，`EMA @20bps` 仍约有 `4/9` 组合存活，而 `PSAR @20bps` 只剩约 `2/9`
   - 这进一步支持当前项目级排序：`EMA = raw alpha baseline candidate`，`PSAR = fast reaction / protective layer candidate`。

2. **breakout-short follow-up 的“该怎么读”现在也更稳定了**
   - 最新 v0 页面已把：
     - `support_breakout_raw @ h24` = `条件性 alpha / v0 原型`
     - `support_breakout_confirm_1 @ h24` = `co-primary confirmation variant`
     - 真正更像 `feature/watch` 的仍是 `support_rebound_confirm_1`
   - 同时 closure board 也继续强调：若加 first-pass gate，当前更应优先试 `avoid_fluctuating`，而不是机械地 `only_downtrend`。

3. **Fibonacci 这条线的研究结论其实已经基本收住了**
   - 当前 A/B 页已经给出很明确的主线取舍：
     - 裸 `breakout v0`：约 `48` 笔、平均单笔约 `+1.44%`、累计约 `+92.45%`
     - `breakout + fib retest_hold`：约 `29` 笔、平均单笔约 `+0.71%`、累计约 `+20.00%`
     - 平均入场还延迟约 `12.5` 根 bar
   - 这足够支持它继续按 `optional filter candidate / archived idea` 对待，而不是再包装成主 alpha 候选。

## 当前 weakest / should-park-now

1. **Fibonacci 线现在最该做的是“保持收口”，不是继续开新验证回合**
   - 除非后面明确要问一个更窄的问题（例如更明确的 down regime 下能否当小过滤器），否则不应再让它占主研发槽位。

2. **这轮不该再把 v3 重新拉回主排程**
   - `v3 final verdict` 现在应继续只当历史证据包与继承起点；当前该推进的是 `support_breakout_v0` 的后续 honesty，而不是 reopen `V3X-*`。

## 下一步优先级 Top 1~3

### Top 1. `EMA` 的 rolling / OOS honesty

最值得继续：
- 把 `EMA` 从“当前最像 baseline”推进成“更诚实验证后仍站得住的 baseline candidate”；
- 重点补：rolling、train/validate/test 或其他最小 OOS honesty 结构。

为什么排第一：
- 成本页已经补回主报告与 closure 入口；
- 现在真正最缺的是：它是不是只在长样本 / 顺风段好看，还是在更严格切分下仍有 baseline 价值。

### Top 2. `support_breakout_raw @ h24` 的成本 / 执行 / rolling honesty

最值得继续：
- 在现有 `v0` 原型页基础上补更接近策略层的一刀验证；
- 优先回答：扣完成本后是否还站得住、非重叠/执行约束后会不会塌、`avoid_fluctuating` 是否真的比 `trade_all` 更诚实。

为什么排第二：
- 当前 plain-language framing 已经补好；
- 下一步更值钱的是补 honesty，不是继续补措辞。

### Top 3. `EMA + PSAR` 最小组合研究

最值得继续：
- 用最小组合页回答：`EMA` 决定主方向、`PSAR` 负责更快退出/保护之后，是否比单跑 `EMA` 更诚实。

为什么排第三：
- `PSAR` 现在的角色已经基本清楚；
- 与其继续单独争“PSAR 是不是主 alpha”，不如更快回答它作为保护层是否真有增量价值。

## 本轮改动

- **本轮不改 `docs/TODO.md`**
- **本轮不改 `docs/ROADMAP.md`**
- **本轮不改 cron / prompt**

原因：
1. 最近 3 条 bot3 loop（`1218 / 1231 / 1244`）都在正确服务当前 steering；
2. 当前 repo worktree 仍然很脏，bot2 此时去改主文档，边际价值不高，且更容易制造编辑冲突；
3. 当前最需要的不是再改方向，而是让 bot3 继续把已对齐的 next step 往验证层推进。

本轮只新增这份轻量策略巡检记录。

## 网页 / 表达建议

1. **EMA / PSAR 这条线下一步应以“完整性补齐”为主，而不是再拆新姐妹页**
   - 重点是 rolling / OOS honesty；
   - 成本结论现在已经足够 visible 了。

2. **breakout-v0 页面下一步应以 honesty 附页为主，而不是继续解释“它像什么”**
   - 角色判断现在已经够清楚；
   - 再往前就该补成本 / 执行 / non-overlap / rolling。

3. **Fibonacci 线的网页表达已经基本够了**
   - 后续若要动，更像是等 worktree 稳一点时，把 TODO 与 archived 状态再完全对齐；
   - 当前不值得继续消耗 bot3 回合去补更多花样。

## cron / 节奏建议

1. **bot3-momentum-auto-opt-13m：继续保持，不改**
   - 这轮最关键的观察点是：它最近已经连续做出 3 个 closure-first 小步，而且都能落到网页；
   - 先让它顺着当前优先级继续推，不急着再调频。

2. **bot2-strategy-review-40m：继续保持轻量巡检**
   - 当前阶段 bot2 的最佳价值就是这种“方向校准 + 少动文档”的模式。

3. **bot7-quant-digest-4h：继续观察，不改**
   - 当前 prompt 已经对齐到服务三条收口线；
   - 这轮没看到需要再追加 prompt 修正的信号。

## 风险与不确定性

1. `EMA` 仍然只是 `baseline candidate`，不是 production-ready alpha。
2. `support_breakout_v0` 仍是策略化原型，不是完整逐笔净值级可部署策略。
3. `Fibonacci` 当前更像 archived filter idea；除非后续问题被重新收窄，否则继续投入的边际价值不高。
