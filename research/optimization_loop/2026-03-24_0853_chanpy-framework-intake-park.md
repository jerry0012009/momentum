# bot3 optimization loop — chan.py framework intake park

- Time: 2026-03-24 08:53 UTC
- Path: Scout
- Claimed action: `Next 3 bot3 runs` #1 — 重开 fresh intake
- Candidate: `Vespa314/chan.py` repo-based fresh intake（缠论对象计算 / 多级别结构框架）
- Sources:
  - README: https://raw.githubusercontent.com/Vespa314/chan.py/main/README.md
  - Strategy map reference: /root/clawd/jerry/momentum/docs/MAINLINE1_STRATEGY_FACTOR_MAP.md

## Why this was the highest-leverage fresh intake
1. 来自当前项目学习地图里明确挂着的公开 repo，而且之前还没被正式 intake 过。
2. 不是旧 background pool 的 reopen，而是一个新的 repo 源头，符合本轮 `fresh intake` 规则。
3. 如果它能压成 clean-room skeleton，就可能为当前 `pullback / breakout-retest / structure-confirmation` 家族补一个更体系化的因果框架；如果压不成，也能快速诚实排除“把缠论大框架误当单一 alpha”的歪路。

## Minimal intake facts
- README 明写这是一个 **缠论框架**，覆盖 `分形 / 笔 / 线段 / 中枢 / 买卖点` 计算，并支持多级别联立。
- README 同时写明：公开版 **暂未包含完整策略类、特征、模型、AutoML、交易引擎对接等全部内容**；README 与公开代码也可能并不完全一致。
- 目录结构显示它是一个 **大而全的结构/特征/交易框架**：
  - 结构对象：`Bi / Seg / ZS / BuySellPoint / CustomBuySellPoint`
  - 指标/特征：`MACD / BOLL / TrendModel / Feature / ModelStrategy`
  - 交易壳：`Trade / Snapshot / OfflineData / FutuTradeEngine`
- README 还强调 `bsp` 与 `cbsp` 的差别：前者更接近事后可识别结构点，后者才是策略在每根新 K 线到来时用当下数据判断出来的交易点。

## Desk-style honest read
### 可取之处
- 它不是空洞概念，而是公开、维护中的完整结构计算框架。
- repo 明确强调 **逐 Bar / 增量确认**，这点对 desk 很重要，因为它直接提醒我们别把事后结构点偷改成因果信号。
- 作为“研究地图 / 术语翻译器 / 结构候选池”的上游资料是有价值的。

### 致命问题
1. **它不是单一 raw alpha，而是一个宽框架。**
   - 从结构计算、特征工程、模型、回测到交易壳都塞在一起，本轮没法诚实压成一个 desk 可直接验证的主因果。
2. **公开版与完整版不一致，增加了最小复现歧义。**
   - README 明写公开版不含完整策略/模型/交易能力，因此若继续往下做，很容易滑向“猜完整版本来想怎么交易”。
3. **形态学 `bsp` 与实时 `cbsp` 混在同一生态里，最容易引入 hindsight 幻觉。**
   - 这对当前 fresh intake 是硬风险：一旦没有先钉死单一 `trade on / trade off` 规则，就会回到“看图很像”的旧问题。
4. **当前更适合作为结构语言参考，不适合作为 fresh intake 主资源。**
   - 真要继续，也应该是从里面拆出一个很小、很因果的对象（例如某种 reclaim / second-buy 近似），而不是把整个 repo 当候选策略。

## Hard verdict
`park`

## One-line result for desk
`Vespa314/chan.py` 虽然是公开且成体系的缠论框架，但它本质上是结构计算+特征+模型+交易壳的宽平台，公开版又与完整版不完全一致，当前不能诚实压成 desk 需要的单一 clean-room raw alpha，因此 fresh intake 当轮直接 `park`。

## Short scorecard
- reproducible public source: 4/5
- causal clarity as a single alpha: 1/5
- direct fit for 1m/3m/5m/15m minimal experiment: 2/5
- hindsight / framework-overreach risk: 5/5
- verdict: `park`

## Delivery / next implication
- 本轮完成了 `1 主点 + 1 紧邻子点`：
  - 主点：认领一条新的 repo-based fresh intake
  - 紧邻子点：直接给出是否 `keep_P1` 的最小 honest verdict
- 因为结论是 `park`，按顶板规则，下一轮应继续打开 **新的 fresh intake**，不要把 `chan.py` 整个框架误升格成 surviving candidate。
