# 2026-04-18 18:23 UTC · Rank 26 park reframe

## Selected rank
- `Rank 26`
- selection note: 仍限定在 `Rank 1~37` 已 `park` 条目内；本轮优先避开最近 `7` 天刚复盘过的对象。`Rank 26` 上次 bot6 复盘为 `2026-04-11 10:44 UTC`，已超过 `7` 天窗口，且原线已 `park`，适合做一次低频复核。

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- needed evidence:
  - `research/optimization_loop/2026-03-17_0656_rank26-regime-triplet-paper-candidate.md`
  - `research/optimization_loop/2026-03-17_0724_rank26-ethsol-recheck-park.md`
  - `research/park_reframe/2026-03-28_1628_rank26-park-reframe.md`
  - `research/park_reframe/2026-04-11_1044_rank26-park-reframe.md`

## 1) 原 rank 为什么 park？
原 `Rank 26` 被 park 的核心原因没有变化：它把 `regime_triplet` 写成 **strict entry gate**，要求 baseline 方向成立后，还必须满足：
- `long = up_regime`
- `short = down_regime`

这条线不是完全没 pocket；它一度能升到 `P2`，说明状态信息不是零：
- full scope（`BTC/ETH/SOL`）下，`strict_up_down @ 6bps/side ≈ +14.65%`
- `positive_asset_ratio = 2/3`
- `mean_trades ≈ 141`
- `10bps/side ≈ +2.44%`

但 genuinely verdict-changing 的最小诚实检查早已把最自然的 rescue 做完：
- 剥离 `BTC` 弱腿，只看 `ETH+SOL-only`
- `15bps/side ≈ +2.29%`，但只剩 `1/2` 资产为正
- `20bps/side ≈ -11.17%`
- `15bps` 时间桶仍有明显破口：`bucket_1 ≈ -8.44%`

因此原始 `park` 的审计意义要保留：**失败的是 old Rank 26 把 regime 信息放在 strict allow/deny 主职责层，而不是 regime / trend-readiness 主题整体失效。**

## 2) 它更像 hard park 还是 soft park？
**本轮仍读作 `soft park`，但已非常接近 `hard park with consumed residual`。**

为什么还不是纯 hard park：
- 旧线确实留过低成本 pocket；
- 主题层面仍能解释成“坏环境 veto 信息并未完全归零”。

为什么更接近 hard：
1. 原线最自然的一刀早已被消费成既有 `Rank 26b`；
2. `ETH+SOL-only` 这次最小 narrow rescue 也没把它修成干净 `P3`；
3. 4 月中旬新增 digest 更像在强化一个结论：trend / state 信息若还有 residual，更适合挂到 **完整 trend shell / raw-alpha 宿主**，而不是继续给旧 `strict gate` 派生新编号。

## 3) 有没有“可救信号”？
**有残余，但没有新的可救信号。唯一 residual 仍只到既有 `Rank 26b`。**

残余信号依然是：
- `regime_triplet` 更像“明显坏环境别硬上”的 veto 信息；
- 不像“只有最优 regime 才值得 allow”的 strict entry gate。

但本轮重读 `quant_digests/INDEX.md` 后，最近新增的证据——尤其是：
- `2026-04-16 04:54 | bubble-state × MA trend alpha`
- `2026-04-18 04:31 | RSI breakout trend shell`

更像在说明：
- state / trend-readiness 信息若还值钱，应被写进 **更完整的 trend shell / admission package**；
- 而不是继续从旧 `Rank 26` 的 shared regime gate 里，硬切出一个新的 `26c`。

换句话说，这些新证据没有推翻旧 blocker，反而继续把 residual 往“新宿主”方向上移。

## 4) 最值得改的唯一一刀是什么？
**唯一最值得改的一刀仍然没有变化：既有 `Rank 26b`。**

> `demote strict up/down entry gate into an asymmetric veto-only regime overlay`

也就是：
- 不再要求 long 必须 `up_regime` / short 必须 `down_regime` 才 allow；
- 保留 base setup 自己负责触发；
- `regime_triplet` 只在明显坏环境时 veto：
  - long 遇到 `down_regime` veto
  - short 遇到 `up_regime` veto

本轮没有第二刀比这更诚实；若再往外扩，基本都会落入：
- 同义改写 `26b`；或
- 偷带第二轴（asset/timeframe/setup/context 一起改）。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。最终结论：`keep_park`。**

更精确地说：
- 原 `Rank 26 = park` 的审计意义保持不变；
- 既有 `Rank 26b` 继续是旧 rank 唯一诚实 residual；
- 本轮没有形成新的 `Rank 26c`。

## 6) trade on / trade off（审计式说明）
本轮不新增派生，只保留审计说明。

### trade on
- 若将来还要保留 `Rank 26` 的残余价值，更诚实的做法仍然只是：把 `regime_triplet` 降级成 `bad-state veto / size-down hint`，服务更清楚的 base setup。

### trade off
- 它不再是 standalone gate / standalone alpha；
- headline return 未必更漂亮，价值更多体现在减少坏环境出手；
- 若继续从旧 `Rank 26` 往 shared trend-readiness 方向拆新编号，会和既有 family 高重叠，稀释 queue 审计清晰度。

---

## Final verdict for this round
- `verdict`: `keep_park`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park，但已非常接近 hard park with consumed residual`

## Minimal audit note
本轮不推翻 `Rank 26` 的原 park，也不新增 `Rank 26c`。更诚实的记录是：**旧线唯一诚实残余仍只是既有 `Rank 26b`；而 4 月中旬新增的 trend / state 类证据继续说明，这类信息若还有价值，更像新的 trend shell / raw-alpha 宿主，而不是足以再诚实派生旧 `Rank 26`。**

## Git
- git 工作区存在大量与本轮无关脏文件；本轮只做最小必要文档改动，不做 selective commit，避免混提。
