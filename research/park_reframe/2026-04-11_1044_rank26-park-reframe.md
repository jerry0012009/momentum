# 2026-04-11 10:44 UTC · Rank 26 park reframe

## Selected rank
- `Rank 26`
- selection note: 本轮仍限定在 `Rank 1~37` 的 parked rank，且优先避开最近 `7` 天内刚复盘过的条目。`Rank 26` 上次 bot6 复盘是 `2026-04-01 15:29 UTC`，已超过 7 天；同时 4 月上旬又出现了更晚的 runtime truth：多条 `trend-readiness / regime-veto / allow-deny` 派生被正式收口为 shared overlay family absorbed，因此适合再判断一次：这些新证据会不会支持在既有 `Rank 26b` 之外，再诚实派生新的窄 reframe。

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- recent park-reframe logs:
  - `research/park_reframe/2026-04-11_0818_rank12-park-reframe.md`
  - `research/park_reframe/2026-04-11_0535_rank21-park-reframe.md`
  - `research/park_reframe/2026-04-11_0306_rank11-park-reframe.md`
- needed evidence:
  - `research/optimization_loop/2026-03-17_0656_rank26-regime-triplet-paper-candidate.md`
  - `research/optimization_loop/2026-03-17_0724_rank26-ethsol-recheck-park.md`
  - `research/park_reframe/2026-04-01_1529_rank26-park-reframe.md`
  - `research/optimization_loop/2026-04-09_0817_rank9b_fresh_intake_background_absorbed.md`
  - `research/optimization_loop/2026-04-09_1537_rank18b_fresh_intake_background_shared_overlay.md`
  - `research/quant_digests/2026-03-19_0055_adx-er-price-only-trend-readiness-gate.md`

## 1) 原 rank 为什么 park？
原 `Rank 26` 被 park 的原因没有变化：它把 **`regime_triplet` 写成 strict entry gate**，要求 `baseline multi-tf momentum` 给出方向后，还必须满足：
- `long = up_regime`
- `short = down_regime`

也就是说，它不是把状态信息当成 shared veto / sizing hint，而是把它直接放在“是否允许开仓”的主职责层。

原始 frozen 审计并不弱，这也是它一度能升到 `P2` 的原因：
- full scope（`BTC/ETH/SOL`）下，`strict_up_down @ 6bps/side ≈ +14.65%`
- `positive_asset_ratio = 2/3`
- `mean_trades ≈ 141`
- `10bps/side ≈ +2.44%`

但 genuinely verdict-changing 的最小诚实检查已经把最自然的窄救法做完了：
- 只保留 `ETH+SOL-only` 后，`15bps/side ≈ +2.29%`
- 却只剩 `1/2` 资产为正：
  - `ETH ≈ +9.89%`
  - `SOL ≈ -5.31%`
- `20bps/side ≈ -11.17%`
- 且 `15bps` 时间桶仍有明显破口：
  - `bucket_1 ≈ -8.44%`
  - `bucket_2 ≈ +1.56%`
  - `bucket_3 ≈ +2.45%`

翻成人话：
- `Rank 26` 不是“完全没信息”；
- 但它最自然的一次 narrow rescue（剥掉 `BTC` 弱腿）已经被消费；
- 消费后仍不足以把旧对象修成干净的 `P3 narrow paper pilot`；
- 因此原 `park` verdict 的审计意义必须保留：失败的是 **旧 `strict_up_down` 作为主 entry gate 的职责定位**，不是“regime / trend-readiness 主题整体没信息”。

## 2) 它更像 hard park 还是 soft park？
**本轮仍读作 `soft park`，但已比 4 月初更接近 hard park。**

为什么还不是 hard park：
- 原始 full-scope pocket 的确存在；
- `regime / trend-readiness` 主题本身也没有被完全证伪；
- 旧 rank 至少留下了一条可以审计的残余解释：它也许更适合降级成 veto-only overlay，而不是继续当 strict entry gate。

为什么又更接近 hard park：
1. 原线最自然的窄救法（`ETH+SOL-only`）已经被跑过，而且不够干净；
2. 剩下唯一诚实的修改轴，其实早已收敛到既有 `Rank 26b`；
3. 4 月上旬更新的 runtime truth 又说明：类似 `Rank 9b / Rank 18b` 这种把 standalone 失败对象降级成 `regime veto / trend-readiness / abstain` 的派生，并没有继续长成新的 queue-facing pocket，而是被更泛化的 shared overlay family 吸收。

所以，对 **旧 `Rank 26` 本体** 来说，已经很难再把它读成“还有第二条可扩展的 soft residual”；它更像一个只剩既有 `26b` 记账价值的 soft park。

## 3) 有没有“可救信号”？
**有，但没有新的可救信号；唯一残余仍只是既有 `Rank 26b` 那一刀。**

这条残余的逻辑是：
- 原 rank 的 blocker 更像 **职责层放错**；
- `regime_triplet` 不适合继续当 “好环境才能 allow entry” 的 strict gate；
- 更像 “坏环境别硬上” 的 `asymmetric veto-only overlay`。

本轮新增的最关键证据，不是支持 `26c`，而是支持“不要再扩派生”：
- `2026-04-09_0817_rank9b_fresh_intake_background_absorbed.md`
- `2026-04-09_1537_rank18b_fresh_intake_background_shared_overlay.md`

这两份 runtime truth 的共同点很明确：
- 把 standalone 负 alpha 降级成 `regime veto / trend-readiness / abstain` 虽然更诚实；
- 但如果它只是 shared overlay family 的一个宿主实例，就不再构成新的独立 front-slot object；
- 也就是说，**shared veto / trend-readiness 这类 residual 已经开始被家族级吸收，而不是越拆越值得单独编号。**

对 `Rank 26` 来说，这正好反过来强化了一个结论：
- `26b` 仍然是旧 rank 唯一诚实 residual；
- 但这条 residual 现在更像“保留在 queue 里给 bot2 低频审阅”的说明项；
- 还不足以支持继续再生一个 `26c`。

## 4) 最值得改的唯一一刀是什么？
**唯一最值得改的一刀没有变化，仍然只是既有 `Rank 26b`：**

> `demote strict up/down entry gate into an asymmetric veto-only regime overlay`

具体含义也没有变化：
- 不再要求 `long` 必须 `up_regime`、`short` 必须 `down_regime` 才 allow；
- 保留更强、宿主更明确的 base setup 去触发 entry；
- `regime_triplet` 只负责 veto 明显坏环境：
  - long 遇到 `down_regime` veto
  - short 遇到 `up_regime` veto

为什么本轮不是别的一刀：
- 如果继续往 `trend-readiness / abstain / allow-deny` 方向扩写第二条派生，本质上会落进和 `9b / 18b / ADX+ER gate` 同一 shared overlay family；
- 如果再改 universe、再改单侧、再改 timeframe，那又会变成多轴换壳；
- 因此 bot6 当前最诚实的记录只能是：**唯一一刀仍然只有 `26b`，没有 `26c`。**

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论：`keep_park`。**

更精确地说：
- 原 `Rank 26 = park` 的审计意义保持不变；
- 既有 `Rank 26b` 继续是旧 rank 唯一诚实窄派生；
- 本轮没有形成新的 `Rank 26c`。

原因有三层：
1. 原 rank 的失败结构没有被推翻；
2. 原线最自然的一次 rescue（`ETH+SOL-only`）已经被消费且不够干净；
3. 4 月上旬更晚的 runtime truth 说明，同主题 residual 往 shared veto / trend-readiness 方向继续拆分时，已经更容易被 family 吸收，而不是长成新的独立 pocket。

## 6) 如果勉强往下写，trade on / trade off 会怎么变？
本轮不新增派生，因此这里只做审计式说明。

### trade on
- 如果将来还要保留 `Rank 26` 的残余价值，更诚实的做法仍然是：
  - 让 `regime_triplet` 只负责 `bad-state veto / size-down / stricter confirmation hint`；
  - 不再假装它能自己承担 strict primary entry gate 的职责。

### trade off
- 它不再是 standalone gate / standalone alpha；
- headline return 未必更漂亮，更多价值可能体现在减少坏环境出手；
- 若继续往 `trend-readiness shared family` 扩写新编号，极易和既有 `9b / 18b / ADX+ER` 一类对象重叠，反而稀释 queue 的审计清晰度。

---

## Final verdict for this round
- `verdict`: `keep_park`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park，但已比 4 月初更接近 hard`

## Minimal audit note
本轮不推翻 `Rank 26` 的原 park，也不新增 `Rank 26c`。更诚实的记录是：**原线唯一诚实残余仍只是既有 `Rank 26b`（strict gate -> asymmetric veto-only overlay）；而 4 月上旬更晚的 runtime truth 已把多条 `trend-readiness / regime-veto` 派生收口为 shared overlay family absorbed，因此当前不再诚实把旧 `Rank 26` 继续拆成新的窄 reframe。**

## Git
- 本轮只做最小必要文档改动；未做 commit。
- 原因：git 工作区存在大量无关脏文件，当前任务不适合安全 selective commit。
