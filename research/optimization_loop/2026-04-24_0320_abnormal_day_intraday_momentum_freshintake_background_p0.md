# abnormal-day intraday momentum — fresh intake first verdict 收口 background/P0

- 时间：2026-04-24 03:20 UTC
- 对象：`research/quant_digests/2026-04-23_2251_abnormal-day-intraday-momentum-alpha.md`
- 动作：fresh intake 首判
- 结论：`background/P0`
- decisive_result：这篇 abnormal-day intraday momentum 论文没有留下一个相对现有 runtime 仍可独立排队的新 after-cost pocket；它的可移植价值基本被已 live 的 `Rank 229 / ETH-led abnormal-day continuation (session-defined)` 吸收，剩下更多是 abnormal-day admission / timing 提示，而不是新的前排 raw alpha。

## 这轮为什么可以直接收口
本轮不需要再为这篇论文重复跑一条新的重型 admission，因为系统里已经有同一家族对象的诚实收口链条：

- `Rank 229` 的 fresh intake / survivor / P2 / P3 记录，已经把“异常日后 same-day intraday continuation”这条 skeleton 做过最小可执行复现；
- 该链条最终只保留下来 **ETH-led、session-defined、same-day continuation** 的窄口袋，并已完成 `connected_runner_live`；
- 这说明论文标题里更宽的叙事（`BTC/ETH/LTC`、异常日后小时延续、乃至次日跟随）在当前 perp / after-cost / honest execution 口径下，并没有自动变成一个新的通用 front-slot 候选。

## 本轮用于 first verdict 的最小 decisive blocker
这条 intake 要想留在前排，至少需要证明下面任一项：

1. 存在一个**非单 asset、非单月份 lucky-run** 的 after-cost abnormal-day continuation pocket；或
2. 它相对现有 `Rank 229` 家族，提供了**独立新增价值**（例如稳定的次日 follow-through、或可跨 asset 复用的厚 pocket）。

当前 digest 本身没有提供这类新证据；而已有 runtime 证据反而说明：

- 原始 wider thesis 在最小 portability 检查后已明显收缩，不是 `BTC/ETH/LTC` 通用 alpha；
- 最终能存活并上线的，只是其中一条更窄、更诚实的 `ETH-led same-day continuation` 版本；
- 因此把这篇新 digest 再作为一条独立 fresh intake 保留，会与现有 live 家族重复占用前排。

## 为什么不是 keep_P1
如果把它留成 `keep_P1`，等于默认承认这里还有一条尚未被回答的独立候选。
但当前最重要的事实恰好相反：

- “异常日门控 + 日内顺势延续” 这条主线已经在 `Rank 229` 上被研究、收缩并上线；
- 这篇 2020 论文没有额外拿出一条新的、未被现有 runtime 吸收的 after-cost 口袋；
- 次日 follow-through 虽然在论文叙事里有趣，但当前并没有形成足以改变分层的新 runtime artifact。

所以最诚实的 first verdict 不是再给一次 survivor 预算，而是直接承认：**它更适合作为已 live abnormal-day 家族的背景参考 / wording / admission 提示，而不是新的 front-slot 对象。**

## 本轮 verdict
- 层级：`fresh intake -> background/P0`
- 一句话结果：`abnormal-day intraday momentum` 没有提供超出已 live `Rank 229` 的独立 after-cost continuation pocket；它的新增价值主要退化为 abnormal-day admission / timing 提示，因此本轮直接收口 `background/P0`。
