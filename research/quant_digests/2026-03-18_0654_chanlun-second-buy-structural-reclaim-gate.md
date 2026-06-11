# 别把“二买”当图形玄学：对 15m 来说，它更像 breakout / Fib 回抽后的 structural reclaim 确认层
- 时间：2026-03-18 06:54 UTC
- 类型：GitHub
- 主题标签：breakout-short/fibonacci/retest-hold/chanlun/second-buy/reclaim/structure/confirmation/repo/crypto/15m
- 证据类型：repo 规则拆解 + 工程示例回测 / 待验证

## 1. 这次看了什么
这轮主看的是 **yijixiuxin** 的 GitHub 仓库 **chanlun-pro**，重点读了 README、`缠论买卖点和背驰规则` 文档，以及 `strategy_multiple_zs_mmds.py` / `多中枢类型相同买卖点策略.md`。这个 repo 最值得我们拿走的，不是整套缠论名词，而是它把“二买/二卖”压成了**逐 Bar 增量确认**的结构规则：先有趋势/中枢，再看创新低后的“不再创新低”或创新高后的“不再创新高”，最后再等一个重新站回触发位的确认。对当前 desk，这比继续把 Fib、breakout、EMA/PSAR 各自孤立处理更有价值，因为它更像一层能跨两三条线复用的 **post-break structural reclaim gate**。

## 2. 核心结论
- **一句话核心结论**：`二买 / 二卖` 最适合被读成 **突破/回抽后的结构确认层**，不是 15m 上独立开火的“玄学 alpha”。
- **一句话证明方式**：`chanlun-pro` 不是只画图讲故事；它在 README 里明确写了 **逐 Bar 计算、信号可能继续确认也可能消失**，在策略代码里又把交易条件压成了 `多中枢同向交集 + 笔停顿 + MACD 回拉零轴`，说明它本质上是在做 **选择性更强的确认过滤**，不是追求高频裸信号。
- 文档对二买的定义很直接：**两中枢趋势后，创新低后后续段不再创新低；或不创新低但段背驰；以及一买后不创新低，也可出现二买。** 翻成人话，就是：**先跌一腿把人吓出来，再看后面的回抽是不是已经跌不动了。**
- `多中枢类型相同买卖点策略` 给的 A 股日线示例，也支持“它更像过滤层”这个读法：三类中枢交集把交易数从 `563~647` 笔压到 `352` 笔，胜率抬到 `41.76%`；trade 模式下总收益 `125.56%`、最大回撤 `-23.29%`。这不是 15m crypto 证据，但足够说明：**交集确认的价值，主要来自少做、晚做、只做更像样的结构。**
- 对我们最值得复用的 3 个点是：
  1. **结构对象必须因果确认、逐 Bar 更新**，不能把事后画好的笔/中枢回填成入场依据；
  2. **“不再创新低/高”比“碰到回撤位就做”更像真确认**；
  3. **反向买卖点或背驰更适合当退出/否决条件**，而不是只盯入场那一刻。

## 3. 为什么和当前项目有关
它直接服务三条当前收口线，而且不是绕开它们：
- 对 `Fibonacci confirmation / retest_hold`：Fib 0.618 本来只是“回到可能有支撑的位置”，但**二买式结构确认**会再多问一句：这次回抽有没有形成一个因果可见的 `higher-low + reclaim`？如果没有，Fib 更像只是碰线，不像 hold。
- 对 `V3 final-verdict / breakout-short follow-up`：短侧不要直接机械镜像升格，但可以先把 `二卖 / lower-high reclaim fail` 当成 **continuation vs fake-break** 的过滤层；也就是 breakdown 后先看反抽是不是已经“弹不回去”。
- 对 `EMA / PSAR raw alpha focus`：EMA / PSAR 更像方向层，`二买/二卖` 更像执行许可层。换句话说，**EMA/PSAR 负责告诉我们风向，structural reclaim 负责告诉我们这次回抽是不是真的站稳/跌稳。**

如果非要回答“为什么这题比继续死磕三条线更值得”，答案是：**因为它不是第四条新线，而是给现有三条线补一个共用、可测试、能降假动作的结构确认层。**

## 4. 可复刻的最小实验
- **研究假设**：在 `BTC / ETH / SOL` 的 `15m` perpetual 上，把 `二买/二卖` 压缩成因果版 `structural reclaim gate`，会比裸 `Fib retest_hold` 或裸 `breakout follow-up` 更能减少 `2~4 bar` 内的快速打脸。
- **最小可计算定义（先做 long，再把 short 分开测）**：
  1. 先冻结一个因果 `breakout_anchor`（最近确认 swing high / neckline / breakout level）；
  2. breakout 后出现 pullback，但 pullback low **不跌破**最近确认结构低点，记为 `higher_low_candidate`；
  3. 若随后 `1~4` 根内再次 **收回 anchor 上方**，记为 `structural_reclaim = 1`；
  4. 若同时 `1h EMA fast > EMA slow` 或 `PSAR` 未翻空，则允许入场；否则 veto。
- **三臂最小对照**：
  1. `raw_fib_or_retest`：现有 `Fib retest_hold / breakout retest_hold` 原规则；
  2. `+ structural_reclaim`：加入 `higher-low + close back above anchor`；
  3. `+ structural_reclaim + HTF direction`：再叠 `1h EMA/PSAR` 方向过滤。
- **short 侧单独做，不和 long 混池**：用镜像的 `lower-high + reclaim fail` 去测 `breakout-short follow-up`，但必须单独统计，因为我们已经知道 crypto 的 sell-side 往往不如 long 侧对称。
- **样本与执行**：最近 `180~365` 天，`next-bar open` 入场，`hold 4 / 8 / 12 bars`，`no-overlap`，成本先看 `6 / 10 / 15 bps per side`。
- **最先看的 4 个指标**：`post-cost expectancy`、`2~4 bar fail rate`、`trade_count retention`、`false_reclaim_ratio`。

## 5. 风险与保留意见
- `chanlun-pro` 的公开示例主要是 **A 股日线**，还有明显的 long-only 语境；不能把它的回测数字偷换成 crypto 15m 证据。
- repo README 自己就写了：**买卖点后续可能继续确认，也可能消失**。这对我们反而是提醒：如果回测里把事后确认的结构倒灌回去，结果一定会虚高。
- “中枢/笔/线段” 的程序化划分本身就存在实现口径差异，所以这轮不该照搬整套缠论对象，而要先压成更朴素、可审计的 `higher-low / lower-high + reclaim` 近似。
- short 侧不能默认镜像升格。当前更诚实的做法，是先把它当 `breakout-short` 的 **failure veto / continuation confirmation**，而不是单独新 alpha。
- 如果 `structural_reclaim` 只是把交易数砍得很少，却没有改善成本后收益或 fail rate，那这层东西就该留在 evidence pool，不该硬升主线。

## 6. 来源
- yijixiuxin. (2021–2026). *chanlun-pro*. GitHub.
  - Venue / DOI：GitHub / N/A
  - Repo URL: <https://github.com/yijixiuxin/chanlun-pro>
  - Readable URL: <https://github.com/yijixiuxin/chanlun-pro/blob/master/README.md>
  - Repo metadata：created `2021-12-10`；pushed `2026-03-13`；stars `819`；forks `312`
- yijixiuxin. *缠论买卖点和背驰规则*.
  - Readable URL: <https://github.com/yijixiuxin/chanlun-pro/blob/master/cookbook/docs/缠论买卖点和背驰规则.md>
- yijixiuxin. *多中枢类型相同买卖点策略*.
  - Readable URL: <https://github.com/yijixiuxin/chanlun-pro/blob/master/cookbook/docs/多中枢类型相同买卖点策略.md>
  - Strategy file: <https://github.com/yijixiuxin/chanlun-pro/blob/master/src/chanlun/strategy/strategy_multiple_zs_mmds.py>

## 7. 下一步怎么测
先别碰整套缠论对象，也别急着把 `二买/二卖` 写成新主策略。直接拿现有 `Fib retest_hold` 与 `breakout-short follow-up` 的事件集，各补一层最朴素的 `higher-low / lower-high + reclaim` 因果确认；只要它能在 **不过度砍掉样本** 的前提下，稳定压低 `2~4 bar fail rate` 并改善 `post-cost expectancy`，这条 `structural reclaim` 线就值得升格为当前 desk 的正式确认模块。