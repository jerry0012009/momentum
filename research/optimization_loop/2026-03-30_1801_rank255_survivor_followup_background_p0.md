# Rank 255 / settlement-TWAP anchor gap / Deribit near-expiry options — survivor follow-up exit to background/P0

- Time: 2026-03-30 18:01 UTC
- Target: `Rank 255 / settlement-TWAP anchor gap / Deribit near-expiry options`
- Source: `research/quant_digests/2026-03-30_1426_deribit-expiry-twap-anchor-alpha.md`
- Action type: survivor decisive follow-up

## What was checked

本轮只执行 `cycle_plan` 的当前第一项，不扩题、不重排顺序。

目标不是再重复 intake，而是回答唯一剩下的 decisive blocker：**这条线能不能从 `mark/IV fair-value monitor` 升级成公开口径下、带执行摩擦的 frozen replication，从而值得进 `P2`。**

本轮直接重审并固定的证据：

1. repo `Option_Scraper.py` 的核心实现仍然是：
   - 每 `5s` 抓 `btc_usd` index；
   - 用过去 `30m` rolling average 当 settlement proxy；
   - 用 `mark_iv` + 剩余到期时间算 `our_price`；
   - 再和 `mark_price` 对比。
2. digest 已经把真正该做的诚实版本写得很明确：
   - 研究对象必须收窄到 `BTC 日度到期期权最后 30m`；
   - 可成交口径必须升级成 `best bid/ask` 或 conservative mid；
   - 必须并排看 `long-underpriced only` 与 `long/short`；
   - 必须显式计入 `fees + half-spread + latency`。
3. 但当前可公开回填到历史事件级的强证据，仍然只稳定覆盖：
   - 到期链条 / instrument universe；
   - 最终 settlement label；
   - repo 的 `mark_price` / `mark_iv` monitor 逻辑。

## What changes system belief

这一步的关键结论不是“想法不存在”，而是：**目前公开可核验链条仍停在 monitor 级 proxy，尚不足以把 `fair-value gap` 诚实外推成可成交 edge。**

更具体地说：

1. **repo 没有给出历史 `best bid/ask` frozen replication。**
   现成实现只比较 `mark_price` 与模型价；这能证明“存在 fair-value 偏离监控思路”，但不能证明在真实可成交盘口上仍然留得住 edge。
2. **当前 survivor 的唯一 blocker 仍是 execution realism，而且这正是唯一 follow-up 应该解决的点。**
   本轮重新核对后，仍没有新增公开样本能把该 blocker 从“monitor 幻觉风险”推进到“可审计 post-cost edge”。
3. **在 short leg 尚未收口、bid/ask 历史样本未冻结之前，long/short 版本和 even long-only 版本都还缺可验证的成交口径。**
   也就是说，问题已不是“概念边界够不够清楚”，而是“最后一公里的执行诚实性仍然没有被解决”。
4. **按 policy，这类 survivor 不能继续无限加研究项。**
   Rank 255 已经用掉 intake 后唯一一次 follow-up；若仍然无法把 monitor 级偏差升级成公开、可回填、post-cost 的执行证据，就应诚实收口，而不是拖成开放式 `keep_P1`。

## Formal exit decision

- Verdict: `background/P0`
- Slot effect: `Surviving candidate slot` 清空
- Reason: 唯一 decisive follow-up 已用尽，但公开证据仍只支持 `settlement-TWAP fair-value monitor`，没有把 `best bid/ask 或 conservative mid + fees + half-spread + latency` 的 frozen replication 做实；因此它目前仍更像一个值得保留的 options event-monitor 题，而不是足以晋级 `P2` 的可交易 raw alpha。

## One-line result

`Rank 255 / settlement-TWAP anchor gap / Deribit near-expiry options` 的唯一 survivor follow-up 已完成：虽然对象边界仍独立且 settlement label 可公开回填，但当前公开证据依旧停留在 `mark/IV` monitor，未能把 `best bid/ask 或 conservative mid + fees + half-spread + latency` 的 frozen replication 做实，因此本轮用尽唯一 follow-up 后将其收口回 `background/P0`。