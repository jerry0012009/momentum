# 2026-04-26 01:12 UTC · Rank 54 park reframe review

## Scope
- Source rank: `Rank 54 / LVN rejection + POC acceptance gate`
- Original authoritative verdict stays: `park / evidence pool`
- This round only asks: **在不推翻原 park 的前提下，4 月 18 日的 auction-profile / POC-LVN shell 与 4 月 23 日的 anchored-VWAP regime-extreme 新证据，是否足以让 Rank 54 再诚实派生一条新的窄 reframe hypothesis。**

## Why this rank this round
- 按 `bot6` 轮转，当前仍优先看 `50~79` 号段。
- `Rank 54` 上次 park-reframe 复盘是 `2026-04-15 21:09 UTC`，已超过 `7` 天。
- 它仍属于典型的“主题变量本身未死，但旧 shared gate 写法已被审计打薄到近乎不可交易”的 parked rank，适合做低频复看。
- 这轮最相关的新旁证是：
  - `research/quant_digests/2026-04-18_0049_auction-profile-poc-lvn-shell.md`
  - `research/quant_digests/2026-04-23_0419_anchored-vwap-regimeextreme-reversion-alpha.md`

## Read set
- required:
  - `docs/TODO.md`
  - `docs/PARK_REFRAME_QUEUE.md`
  - `docs/RECENT_PAPER_SEEDS.md`
  - `research/quant_digests/INDEX.md`
  - `research/park_reframe/INDEX.md`
- needed evidence:
  - `research/optimization_loop/2026-03-18_1104_rank54-source-intake-guard-passed.md`
  - `research/optimization_loop/2026-03-18_1135_rank54-clean-replication-park.md`
  - `research/park_reframe/2026-04-15_2109_rank54-park-reframe.md`
  - `research/quant_digests/2026-04-18_0049_auction-profile-poc-lvn-shell.md`
  - `research/quant_digests/2026-04-23_0419_anchored-vwap-regimeextreme-reversion-alpha.md`

---

## 1) 原 rank 为什么 park？
原 `Rank 54` 被 park 的核心原因没有变化：**只要把 `LVN rejection + POC acceptance` 写成足够题面正确的 shared confirmation gate，交易就会被砍到几乎不可用。**

最小 clean replication 的主结论仍然是：
- `breakdown_reclaim_short + lvn_rejection_plus_poc_acceptance @ 6bps/side`
  - `mean_total_return ≈ 0.00%`
  - `positive_asset_ratio = 0/3`
  - `mean_trades = 0.0`
  - `mean_trade_count_retention = 0.00%`
- 稍宽松的 `ema_pullback_long + lvn_rejection`
  - 虽有约 `+1.40%` 的跨资产均值回报
  - 但只剩 `~22.45%` retention，且 `positive_asset_ratio = 1/3`

也就是说，原 rank 被审计出来的问题不是“参数还没抛光”，而是 **POC acceptance 在这个 shared-gate 职责上会塌成 sample veto**。

## 2) 它更像 hard park 还是 soft park？
**本轮仍更像 `soft park`，但比 4 月 15 日那轮又更接近 `hard park with consumed residual`。**

为什么还没直接写成 hard：
- `POC / LVN / auction structure` 这组变量本身并没有被打成无信息；
- 4 月 18 日与 4 月 23 日的新 digest 继续说明，auction/fair-value anchor 主题确实还能产出 pocket。

为什么继续向 hard 收紧：
- 新证据活下来的主语都更像 **single-asset raw alpha / fair-value anchor**；
- 而不是给旧 breakout / pullback setup 继续做 shared allow/deny gate；
- 这说明旧 Rank 54 的职责摆放问题并没有被修复，反而被进一步坐实。

## 3) 现有证据里是否存在“可救信号”？
**有，但可救的是主题，不是旧壳。**

### 可救信号 A：auction-profile / value-area / LVN 本身仍有信息
`2026-04-18_0049_auction-profile-poc-lvn-shell.md` 的主结论很清楚：
- 更值得先测的是 `value-area re-entry -> POC 回归`；
- 以及 `LVN traverse -> 下一块成交密集区方向延续`；
- 这是一条完整的 `auction-market raw alpha shell`，不是旧 Rank 54 的 shared acceptance gate。

### 可救信号 B：anchored fair-value extreme reversion 也成立，但主语已换
`2026-04-23_0419_anchored-vwap-regimeextreme-reversion-alpha.md` 继续说明：
- `AVWAP` / fair-value anchor 更像 **primary mean-reversion 锚点**；
- 最小可交易 pocket 更偏 `BTC / better anchor / maker-first`；
- 这同样是在说“公平价锚有用”，不是在救旧的 `POC acceptance` shared gate。

### 审计式归纳
这两条新证据共同给出的不是“Rank 54 还差一个窄参数”，而是：
- **auction / fair-value anchor 主题有 residual value**；
- 但它更自然的宿主是 `range-reversion raw alpha`、`anchor-extreme reversion raw alpha`、或 `HTF fair-value -> child execution`；
- 不是 old Rank 54 的 queue-facing shared gate。

## 4) 最值得改的唯一一刀是什么？
**若只允许改一刀，最自然的一刀仍是：把 `POC/LVN` 从 shared confirmation gate 改写为 primary fair-value / auction anchor。**

但这也是本轮不 draft 的关键原因：
- 一旦这么改，条目的职责已从“给别的 setup 做 confirm”变成“自己就是 alpha”；
- 这不是旧 Rank 54 壳内的窄修补，而是直接换宿主；
- 审计上更诚实的写法应是新的 intake family，而不是假装成 `Rank 54b`。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论：`keep_park`。**

理由：
1. 原 blocker 没变：旧 Rank 54 的 `POC acceptance` 写法仍会把交易压到接近归零；
2. 4 月 18 日的新 auction-profile 证据支持的是完整 `value-area / LVN` raw-alpha 壳；
3. 4 月 23 日的新 AVWAP 证据支持的是更明确的 `anchored fair-value extreme reversion` 宿主；
4. 若现在硬写 `Rank 54b`，本质会是把“新 raw-alpha 宿主”伪装成“旧 gate 的窄重开”，这不符合保留原 `park` 审计意义的要求。

## 6) trade on / trade off 怎么读？
本轮不新增派生，只保留审计式复述：

- `trade on`：
  - 原 Rank 54 至少留下一个清晰残余：`auction / fair-value anchor` 主题仍值得在研究池继续保留；
  - 特别是 `value-area re-entry`、`LVN traverse`、`swing-anchor AVWAP extreme reversion` 这些主语更完整的写法。
- `trade off`：
  - 一旦把这条线写得更可交易，它自然就会滑向新的单资产 raw-alpha / HTF-anchor 宿主；
  - 那时得到的已经不是 shared gate，也就不再是诚实的 `Rank 54b`；
  - 因此当前更该保留 `park` 审计，而不是扩张队列身份。

---

## Final verdict for this round
- `verdict`: `keep_park`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park，但比 2026-04-15 那轮更接近 hard park with consumed residual`

## Minimal audit note
本轮不重开 `Rank 54`，也不新增 `Rank 54b`。

更诚实的记录是：**4 月 18 日的 auction-profile / POC-LVN shell 与 4 月 23 日的 anchored-VWAP regime-extreme 新证据，继续说明 auction / fair-value anchor 主题仍有信息；但它救活的是新的单资产 range-reversion / anchored-fairness raw-alpha 宿主，而不是旧 Rank 54 的 `LVN rejection + POC acceptance` shared gate。**

## Git
- 本轮只做最小必要文档改动；默认不改 `docs/TODO.md`。
- 未做 commit。
- 原因：共享工作区存在大量与本轮无关的未跟踪脏文件，不适合安全 selective commit。
