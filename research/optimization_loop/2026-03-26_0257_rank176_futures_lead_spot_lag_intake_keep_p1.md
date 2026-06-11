# Rank 176 / futures-lead-spot-lag-spread-alpha — fresh intake 首判（keep_P1）

- 时间：2026-03-26 02:57 UTC
- 对象：`research/quant_digests/2026-03-26_0252_futures-lead-spot-lag-spread-alpha.md`
- 结论：**keep_P1，不升 P2**
- 正式 Rank：**176**

## 这轮只回答一个问题
这条 `futures lead spike -> lagging spot/perp leg catch-up spread`，是否值得作为新的前排候选保留？

回答：**值得保留到 P1，但当前证据还不足以直接升 P2。**

## 为什么保留
1. **对象是清楚的 same-asset relative-value 骨架，不是泛泛 market structure 复述。**
   digest 里最值钱的不是“谁领先”这句机制话，而是“领先强度是 pocketed、事件驱动、时变的”；因此更合理的交易对象不是 always-on basis mean reversion，而是 leader 明显先动、lagging leg 尚未补完时的 catch-up spread。
2. **它与现有素材池互补，而且天然可审计。**
   这条线不同于 ETF→BTC 或 BTC→ALT 的跨资产 lead-lag，属于同一资产不同市场的短周期先后顺序；更容易写成 dollar-neutral / short-horizon entry-exit 规则，而不是一段难审计的宏观叙事。
3. **最小实验已经足够具体，值得消耗唯一 survivor follow-up。**
   digest 已经给出 public data、leader shock 定义、spread close 目标、持有上限和成本口径，不是只有一句灵感，说明它已经超过“先记一下”的程度。

## 为什么这轮不升 P2
1. **当前证据主要还是摘要级论文 + desk spec，不是 clean replication。**
   主论文在本环境下只拿到摘要级信息，而且核心发现来自 regulated futures vs spot；直接映射到 Binance perp/spot 还缺第一轮诚实复刻。
2. **真正 blocker 是执行 realism，而不是机制存在性。**
   1 秒级领先很可能被手续费、延迟和 quote quality 吞掉；如果后续不能证明 `30s/1m/5m` 的 pocketed 版本在保守成本后仍有净边，这条线就不该往上升。
3. **这轮最诚实的定位仍是 raw alpha intake，而不是 admission-ready 策略。**
   当前只能说“骨架值得保留并做一次 cheapest decisive follow-up”，还不能说“已足够值得进入 paper launch queue 或 P2 admission”。

## 唯一 survivor follow-up 应回答什么
只做一次最便宜但 decisive 的检查：用 Binance spot + perp 公共高频代理，回答 `leader shock pocket` 下 `lagging leg catch-up spread` 在 `30s/1m/5m` 三档里，扣除保守 fee/slippage 后是否仍保有可交易净边；同时确认它是不是只活在美盘/宏观事件窗，而不是全天误判泛滥。

## 本轮改变的系统认知
**Rank 176 / futures-lead-spot-lag-spread-alpha 值得以前排 P1 身份保留的，不是“BTC futures 通常领先”这句市场结构描述，而是 `same-asset futures lead spike -> lagging spot/perp leg catch-up spread` 这条 pocketed short-horizon relative-value 骨架；当前仍未证明可直接升入 P2。**

## Runtime 落点
- `Fresh intake slot`：本轮首判完成
- `Surviving candidate slot`：切换为 `Rank 176 / futures-lead-spot-lag-spread-alpha`
- `followup_budget_remaining`：`1`
- 本轮未创建 `Active P2`，也未触发 `P2 -> P3`
