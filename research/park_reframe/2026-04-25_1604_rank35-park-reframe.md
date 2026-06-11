# 2026-04-25 16:04 UTC · Rank 35 park reframe revisit

## Selected rank
- `Rank 35`
- selection note: 继续遵守 bot6 单轮只处理 1 条 parked rank。`Rank 35` 虽在近 7 天内看过一次，但 4 月 21 日与 4 月 23 日新增了更近的 trend-pullback 旁证（`triple EMA stack × RSI veto × ATR bracket`、`StochRSI 极值回摆 × RSI/MACD continuation`），因此本轮允许做一次低频复核，判断这些新证据是否足以把 old `Rank 35` 诚实地派生成新假设。

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- needed evidence:
  - `research/optimization_loop/2026-03-17_1248_rank35-clean-replication-park.md`
  - `research/park_reframe/2026-04-19_1240_rank35-park-reframe.md`
  - `research/quant_digests/2026-04-21_1358_tripleema-rsi-atr-stack-alpha.md`
  - `research/quant_digests/2026-04-23_0548_stochrsi-macd-pullback-continuation-alpha.md`

## 1) 原 rank 为什么 park？
原 `Rank 35 / VWAP pullback + trend-template qualifier` 被 park 的原因没有变：
- 真正站得住的是更宽的 `higher_tf_bias` 方向信息，不是它想验证的 `VWAP reclaim + RSI reclaim` 这套 queue-facing pullback entry；
- `bias_plus_vwap_reclaim` 对 `VWAP anchor` 很敏感，`utc_day` 与 `funding_8h` 差异大；
- `combo_long_only` 虽不至于直接塌穿，但 `mean_trades≈3.7~4.0`、`mean_no_trade_ratio≈99.88%~99.89%`，样本薄到不够诚实；
- `time-pocket honesty` 里中段 bucket 为负，说明它不是稳定 pocket。

所以原 `park` 的审计含义仍然成立：**失败的是 old Rank 35 这条“VWAP reclaim + RSI reclaim admission”职责，不是所有 trend-pullback 语义都死了。**

## 2) 它更像 hard park 还是 soft park？
**本轮仍判为 `soft park`，但已更接近 `hard park with consumed residual`。**

- 之所以还保留 soft，是因为旧线曾留下过一条自然 residual：`删掉 VWAP reclaim，只保留 higher-tf bias + RSI pullback reclaim`；
- 之所以更接近 hard，是因为这条 residual 已被既有 `Rank 35b` 表达并消费，而最近新证据没有给出 old Rank 35 壳内第二条诚实单轴。

## 3) 有没有“可救信号”？
**有主题层面的可救信号，但没有 old `Rank 35` 壳内的新可救信号。**

最近两篇 digest 都在强化同一个方向：
- `2026-04-21_1358_tripleema-rsi-atr-stack-alpha.md` 说明 `EMA stack + RSI veto` 更像完整 trend shell / parent signal；
- `2026-04-23_0548_stochrsi-macd-pullback-continuation-alpha.md` 说明“趋势内回摆结束后接续第二脚”在 `15m` parent 上仍有信息，但它更像新的 oscillator-confirmed pullback raw alpha。

这类新证据说明：
- **trend-pullback 主题仍然活着；**
- 但它活在新的完整 shell / raw-alpha 宿主里，
- **而不是足以把 old `Rank 35` 再诚实地写成 `Rank 35c`。**

## 4) 最值得改的唯一一刀是什么？
**唯一最值得改的一刀仍然没变：删掉 `VWAP reclaim`，只保留 `higher-tf bias + RSI pullback reclaim`。**

也就是既有 `Rank 35b` 的那一刀：
- `remove VWAP reclaim requirement; keep higher-tf bias + RSI pullback reclaim`

本轮没有出现比这更诚实的新单轴。若继续往前写，就会不可避免地偷带第二轴，把 `EMA stack / StochRSI / MACD / ATR bracket` 这些新壳里的信息一起混进来；那已经是新的 trend-pullback raw-alpha family，不再是 old Rank 35 的窄 reframe。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。最终结论：`keep_park`。**

原因：
1. 原 `park` verdict 仍需保留，不能推翻；
2. old Rank 35 唯一自然 residual 仍只到既有 `Rank 35b`；
3. 4 月 21 日与 4 月 23 日的新证据强化的是“新的完整 trend-pullback shell”，不是 old `Rank 35` 的新单轴；
4. 现在硬写 `Rank 35c`，会把“新 trend-shell 母题”误写成“旧 Rank 35 的窄派生”，不够诚实。

## 6) trade on / trade off（审计式说明）
### trade on
- 保留 old `Rank 35` 的原 `park` 审计意义；
- 承认 trend-pullback 主题最近仍有增量旁证；
- 同时明确这些增量更像新的完整 trend shell / oscillator-confirmed pullback raw alpha，而不是 old Rank 35 的新一刀。

### trade off
- 不把新母题硬塞回旧 parked shell；
- 不把 `EMA stack / StochRSI / MACD / ATR bracket` 等第二轴混成假装“还是 Rank 35”的 reframe；
- 承认 old Rank 35 现在只剩既有 `Rank 35b` 这一条 cheap residual note，而不是新的 queue-facing draft。

## Final verdict for this round
- `verdict`: `keep_park`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park，但已更接近 hard park with consumed residual`

## Minimal audit note
本轮不新增 `Rank 35c`。更诚实的记录是：**old Rank 35 的唯一自然 residual 仍只到既有 `Rank 35b`；4 月 21~23 的新 trend-pullback 证据继续说明，主题若还有价值，更像新的完整 trend-shell / oscillator-confirmed pullback raw-alpha 宿主，而不是足以再诚实派生旧 `Rank 35`。**

## Git
- 未做 selective commit。
- 原因：git 工作区存在大量与本轮无关的脏文件，且 `docs/PARK_REFRAME_QUEUE.md` 已被其他流程修改；本轮仅做最小必要文档写入，避免混提。

## 邮件短标题
- `Rank 35 继续 park，trend pullback 仍属新壳`