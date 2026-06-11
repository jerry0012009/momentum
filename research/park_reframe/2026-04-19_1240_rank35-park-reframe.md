# 2026-04-19 12:40 UTC · Rank 35 park reframe revisit

## Selected rank
- `Rank 35`
- selection note: 本轮继续遵守 bot6 单轮只处理 1 条 parked rank 的约束。按近期覆盖情况，`Rank 50+` 与 `80~110` 号段已在近几轮持续被复盘，而 `Rank 35` 上次 bot6 复盘为 `2026-04-12 11:14 UTC`，已刚好超过 `7` 天窗口；同时 4 月 18 日又新增了同主题的 `RSI breakout trend-shell` 旁证，适合做一次低频复核。

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- recent park-reframe context:
  - `research/park_reframe/2026-04-19_0955_rank14-park-reframe.md`
  - `research/park_reframe/2026-04-19_0507_rank25-park-reframe.md`
  - `research/park_reframe/2026-04-19_0203_rank21-park-reframe.md`
- needed evidence:
  - `research/optimization_loop/2026-03-17_1248_rank35-clean-replication-park.md`
  - `research/park_reframe/2026-04-12_1114_rank35-park-reframe.md`
  - `research/quant_digests/2026-04-08_0405_htf-ema-rsi-pullback-trend-shell.md`
  - `research/quant_digests/2026-04-18_0431_rsi-breakout-trend-shell.md`

## 1) 原 rank 为什么 park？
原 `Rank 35 / VWAP pullback + trend-template qualifier` 的 blocker 没有变化。

`2026-03-17_1248_rank35-clean-replication-park.md` 已把旧 rank 的审计结论说得很清楚：
- 真正稳的是更宽的 `higher_tf_bias` 本体，而不是它想验证的 `VWAP pullback + RSI reclaim` 这套 queue-facing entry；
- `bias_plus_vwap_reclaim` 对 anchor 明显敏感，`utc_day` 与 `funding_8h` 表现差异很大；
- `combo_long_only` 虽然没有直接塌穿，但 `mean_trades≈3.7~4.0`、`mean_no_trade_ratio≈99.88%~99.89%`，交易数薄到不够诚实；
- time bucket 上中段翻负（`bucket_2` 为负），说明它也不是稳定 pocket。

所以原 `park` 必须继续保留：
**失败的是“VWAP reclaim + RSI reclaim 打包成一条 queue-facing pullback admission”这层职责，而不是所有 trend-pullback 语义都失效。**

## 2) 它更像 hard park 还是 soft park？
**本轮仍判为 `soft park`，但已比 4 月 12 日那轮更接近 `hard park with consumed residual`。**

为什么仍保留 soft：
- 旧线并非一开始就纯 hard fail；
- 它确实留下过一条自然 residual：`去掉 VWAP reclaim，只保留 higher-tf bias + RSI pullback reclaim`。

为什么更接近 hard：
1. 这条唯一自然 residual 早已被既有 `Rank 35b` 表达；
2. 4 月 8 日与 4 月 18 日的新证据都没有给出属于 old `Rank 35` 壳内的第二条独立单轴；
3. 新证据反而更明确地说明：如果主题还有价值，更像新的完整 trend-shell / raw-alpha 宿主，而不是旧 parked shell 再切 `35c`。

## 3) 有没有“可救信号”？
**有 residual，但没有新的可救信号；唯一 residual 仍只到既有 `Rank 35b`。**

这轮新旧证据合起来，方向反而更收紧：

### A. 4 月 8 日的 HTF EMA × RSI pullback 旁证
`2026-04-08_0405_htf-ema-rsi-pullback-trend-shell.md` 已经说明：
- 这类信息更像 `HTF gate × LTF shallow pullback continuation` 的完整 raw-alpha；
- 主语已经不是“旧 Rank 35 再修一刀”，而是新的完整 trend-pullback 宿主。

### B. 4 月 18 日的 RSI breakout trend-shell 旁证
`2026-04-18_0431_rsi-breakout-trend-shell.md` 进一步说明：
- 慢趋势 / trend-strength / volume-readiness 这类条件若还有价值，更像挂在完整 trend shell 上；
- 它救活的是“趋势已成立后追第二脚”这类完整壳，而不是 old `Rank 35` 的 `VWAP reclaim` admission。

换句话说，最近的新证据不是在说：
- “旧 Rank 35 只差再调一层 pullback filter”；
而是在说：
- “trend-pullback 主题本身仍有信息，但更该写成新的完整 shell，而不是旧 Rank 35 的窄 reframe”。

## 4) 最值得改的唯一一刀是什么？
**唯一最值得改的一刀仍然不变：删掉 `VWAP reclaim`，只保留 `higher-tf bias + RSI pullback reclaim`。**

也就是既有 `Rank 35b`：
- `remove VWAP reclaim requirement; keep higher-tf bias + RSI pullback reclaim`

本轮没有出现比这更诚实的新一刀。若继续往前写：
- 要么只是把 `35b` 换句话说；
- 要么会偷带第二轴，把 HTF EMA / ADX / volume / ATR trail 一起混进来；
- 那就已经更像新的完整 trend shell，不再属于 old `Rank 35` 的审计边界。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。最终结论：`keep_park`。**

原因：
1. 原 `park` 的审计意义仍然成立，不能推翻；
2. 唯一诚实 residual 早已被 `Rank 35b` 消费；
3. 4 月 18 日新增的 RSI breakout trend-shell 证据没有形成 old `Rank 35` 壳内的新单轴，反而继续把主题上移到新的完整宿主；
4. 若现在硬写 `Rank 35c`，本质会把“新 trend shell 母题”误写成“旧 Rank 35 的窄 reframe”，不够诚实。

## 6) trade on / trade off（审计式说明）
### trade on
- 保留 old `Rank 35` 的原 `park` 审计意义；
- 承认它仍留下一条很窄 residual，即 `去掉 VWAP reclaim` 后的 `higher-tf bias + RSI pullback reclaim`；
- 同时明确这条 residual 已被既有 `Rank 35b` 提炼并消费。

### trade off
- 不再把 trend-pullback 主题继续硬塞回旧 parked shell；
- 不把新的 `HTF gate / RSI breakout / ATR trail` 完整 trend-shell 误写成 `Rank 35c`；
- 承认 old `Rank 35` 能保留的只剩 cheap residual note，而不是新的 queue-facing draft。

---

## Final verdict for this round
- `verdict`: `keep_park`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park，但已比 4 月 12 日那轮更接近 hard park with consumed residual`

## Minimal audit note
本轮不推翻 `Rank 35` 的原 park，也不新增 `Rank 35c`。更诚实的记录是：**old Rank 35 的唯一自然 residual 仍只到既有 `Rank 35b`；而 4 月 18 日新增的 RSI breakout trend-shell 证据继续说明，trend-pullback / readiness 信息若还有价值，更像新的完整 trend-shell / raw-alpha 宿主，而不是足以再诚实派生旧 `Rank 35`。**

## Git
- git 工作区存在大量与本轮无关脏文件；本轮只做最小必要文档改动，不做 selective commit，避免混提。

## 邮件短标题
- `Rank 35 继续 park，trend pullback 已外流到新壳`
