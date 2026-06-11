# 2026-04-15 23:10 UTC · Rank 73 park reframe review

## Scope
- Source rank: `Rank 73 / PSAR close-confirmed follow-up gate`
- Original authoritative verdict stays: `park / evidence pool`
- This round only asks: **在不推翻原 park 的前提下，4 月上旬新增的 `Wilder-RSI breakout trend shell` / `daily-trend veto × technical-vote continuation shell` 证据，是否足以让 Rank 73 再诚实派生一条新的窄 reframe hypothesis。**

## Why this rank this round
- 按 `bot6` 轮转，本轮仍优先看 `50~79` 号段。
- `Rank 73` 上次 park-reframe 复盘是 `2026-04-04 16:16 UTC`，已超过 `7` 天。
- 它属于典型“主题未必死，但原 fixed-bar confirm 职责已被审得很硬”的 parked rank，适合低频再确认一次。
- 这次最相关的新旁证是：
  - `research/quant_digests/2026-04-13_0558_wilder-rsi-adx-atr-shell-transfer-check.md`
  - `research/quant_digests/2026-04-14_0140_dailyveto-technicalvote-shell.md`
  - 辅助旧旁证：`research/quant_digests/2026-03-21_0652_cusum-event-bar-confirm-veto-gate.md`

## Read set
- required:
  - `docs/TODO.md`
  - `docs/PARK_REFRAME_QUEUE.md`
  - `docs/RECENT_PAPER_SEEDS.md`
  - `research/quant_digests/INDEX.md`
  - `research/park_reframe/INDEX.md`
- recent context:
  - `research/park_reframe/2026-04-15_2109_rank54-park-reframe.md`
  - `research/park_reframe/2026-04-15_1822_rank53-park-reframe.md`
  - `research/park_reframe/2026-04-15_1336_rank80-park-reframe.md`
- needed evidence:
  - `research/optimization_loop/2026-03-19_0103_rank73-clean-replication.md`
  - `research/park_reframe/2026-04-04_1616_rank73-park-reframe.md`
  - `research/quant_digests/2026-04-13_0558_wilder-rsi-adx-atr-shell-transfer-check.md`
  - `research/quant_digests/2026-04-14_0140_dailyveto-technicalvote-shell.md`
  - `research/quant_digests/2026-03-21_0652_cusum-event-bar-confirm-veto-gate.md`

---

## 1) 原 rank 为什么 park？
原 `Rank 73` 被 park 的主因没有变化：**把 PSAR 写成 `close-confirmed + wait N bars` 的 fixed-bar follow-up gate，没有改善 continuation 质量，只是在制造延迟。**

最小 clean replication 的关键结果：
- `breakout_short`
  - `raw_trigger @ 6bps`: `mean_total_return ≈ -2.58%`
  - `close_confirmed_n2 @ 6bps`: `mean_total_return ≈ -2.82%`
  - `trade_count_retention ≈ 92.75%`
  - `false_break_ratio` 与 `flip_to_fail_rate` 都没变好，反而略差
- `ema_psar_long`
  - `raw_trigger @ 6bps`: `mean_total_return ≈ -5.41%`
  - `close_confirmed_n2 @ 6bps`: `mean_total_return ≈ -6.21%`
  - `close_confirmed_n3 @ 6bps`: `mean_total_return ≈ -6.11%`
  - `trade_count_retention ≈ 58%~59%`
  - `positive_asset_ratio` 从原本残存的 `1/3` 进一步掉到 `0/3`

也就是说，旧 Rank 73 失败的不是“还没等到合适的 N”，而是：
> **fixed time-bar follow-up 本身没有给 PSAR 带来更诚实的 continuation 识别。**

## 2) 它更像 hard park 还是 soft park？
**本轮仍读作 `soft park`，但比 4 月 4 日那轮更接近 hard。**

为什么还保留一点 soft：
- `PSAR` / trend-follow 主题本身没有死；
- 近期新证据继续说明“趋势确认后 drift”仍可能活在完整趋势壳里。

为什么继续向 hard 靠：
- 原 rank 的 blocker 已经很具体：不是参数没调好，而是 **fixed-bar confirm 角色不成立**；
- 4 月 13~14 的新证据不是在修复 `close_confirmed_n2 / n3`，而是在继续把 PSAR/RSI/ADX 一类信息上移到 **完整 trend shell / daily veto** 宿主；
- 3 月 21 日的 `CUSUM event-bar` 旁证也早就说明：若要保留确认层，更自然的是 `event-confirm`，不是继续迷信“再等两根 15m bar”。

## 3) 现有证据里是否存在“可救信号”？
**有可救信号，但它救活的是更上位的 trend-shell / event-confirm 宿主，而不是旧 Rank 73。**

### 可救信号 A：PSAR/RSI/ADX 主题仍可在完整趋势壳里存活
`2026-04-13_0558_wilder-rsi-adx-atr-shell-transfer-check.md` 支持的不是“固定再等 N 根 bar”，而是：
- `Wilder RSI breakout × ADX/EMA regime × ATR trail` 的完整趋势延续壳；
- entry/exit/risk 一起定义，PSAR/趋势确认只是一部分语义。

### 可救信号 B：真正保住 edge 的是更上位的 daily veto / regime shell
`2026-04-14_0140_dailyveto-technicalvote-shell.md` 更明确：
- 15m continuation 若还能活，关键往往是 `daily-trend veto` 这类上层 regime；
- 不是“把 15m trigger 后再机械等两根 bar”。

### 可救信号 C：若还要做确认层，更像 event-flow 而不是 fixed-bar latency
`2026-03-21_0652_cusum-event-bar-confirm-veto-gate.md` 说明：
- 真正可能有信息的是 `same_dir_first / opp_dir_first / no_event_timeout` 这种 event-confirm；
- 这再次反证 `Rank 73` 的问题不在 PSAR 主题，而在 fixed-bar 写法本身。

## 4) 最值得改的唯一一刀是什么？
**如果硬要保留唯一一刀，最值得改的是：把 `fixed N-bar close-confirmed follow-up` 改写成 `event-driven continuation confirm-veto`。**

但这正是本轮不 draft 的原因：
- 一旦这么改，主语已经从 old `Rank 73` 的 `PSAR close-confirmed follow-up gate` 变成了更泛的 `event-confirm` 家族；
- 若再往上加 `daily veto / ADX / ATR trail`，就更明显是在借新 trend shell 给旧 rank 续命；
- 这不是诚实的 `Rank 73b`，更像新的宿主语言。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论：`keep_park`。**

理由：
1. 原 `park` blocker 没被推翻：fixed-bar latency 仍没有证明能减少 false break / early fail；
2. 新证据支持的是 `daily-veto trend shell`、`Wilder-RSI/ADX continuation shell` 或 `CUSUM event-confirm` 这类新/更上位宿主；
3. 如果现在硬写 `Rank 73b`，本质是在把“新的 trend-shell / event-confirm family”包装成“旧 PSAR gate 的窄 reframe”，审计上不诚实。

## 6) trade on / trade off 怎么读？
本轮不新增派生，只保留审计式复述：

- `trade on`：
  - 原 Rank 73 留下的一点 residual，只够说明 **PSAR/趋势确认主题仍值得保留在研究池**；
  - 尤其是它更适合做 trend shell 配角或 event-confirm 语言，而不是 fixed-bar 主确认。
- `trade off`：
  - 放弃继续把 `close_confirmed_n2 / n3` 写成 queue-facing 共享 gate；
  - 一旦继续硬写，大概率只会重复已有 trend-shell / event-confirm 宿主，或再次落入“延迟替代 edge”的老问题。

---

## Final verdict for this round
- `verdict`: `keep_park`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park，但比 2026-04-04 那轮更接近 hard`

## Minimal audit note
本轮不重开 `Rank 73`，也不新增 `Rank 73b`。

更诚实的记录是：**4 月上旬新增的 Wilder-RSI / daily-veto technical-vote 证据，继续说明趋势确认主题仍有信息；但它救活的是新的 trend-shell / daily-veto 宿主，辅以 `CUSUM event-confirm` 这类更诚实确认层，而不是旧 Rank 73 的 fixed-bar PSAR follow-up gate。**

## Git
- 本轮只做最小必要文档改动；未做 commit。
- 原因：共享工作区存在大量与本轮无关的未跟踪脏文件，不适合安全 selective commit。
