# 2026-04-07 18:47 UTC · Rank 72 park reframe review

## Scope
- source rank: `Rank 72 / realized-vol mid-band cost-survival gate`
- original verdict stays: `park / evidence pool`
- this round only asks: **after the newer liquidity / execution-overlay evidence from early April, should Rank 72 spawn a narrower reframe, or should it stay parked?**

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- needed evidence:
  - `research/optimization_loop/2026-03-19_0032_rank72-midband-clean-replication.md`
  - `research/quant_digests/2026-03-18_2136_realized-vol-midband-cost-survival-gate.md`
  - `research/quant_digests/2026-04-01_1426_lowfreq-liquidity-proxy-gate-overlay.md`
  - `research/quant_digests/2026-04-02_0448_utc-slot-costmap-route-veto-overlay.md`

## Why this rank this round
- 继续遵循 `bot6` 的低频轮转：本轮仍优先看 `Rank 50+` 的 parked rank。
- `Rank 72` 目前还没在 `research/park_reframe/INDEX.md` 里留下单独复盘，且原 park 已超过 7 天，没有撞上“刚复盘过同一条”的回避规则。
- 它是个典型“主题可能没死，但原 shared allow/deny 角色已经被审得很硬”的对象，正好适合用最近两周的新证据回答：到底还有没有属于原 rank 的单轴可救空间。

## 1) 原 rank 为什么 park？
原 `Rank 72` 被 park，不是因为“波动状态”这个主题完全没信息，而是因为它被写成 **shared realized-vol mid-band allow/deny gate** 后，结果很不诚实地依赖大幅砍样本：

- `ema_psar_long`
  - `base @ 6bps ≈ -3.79%`
  - `rv_midband_q20_80 @ 6bps ≈ +1.78%`
  - 但 `trade_count_retention ≈ 21.49%`
- `fib_retest_long`
  - `base @ 6bps ≈ +1.20%`
  - `rv_midband_q20_80 @ 6bps ≈ -1.22%`（另一版摘要里是更接近打平，但都谈不上 clean rescue）
  - `trade_count_retention ≈ 21.90%`
- `breakout_short`
  - `base @ 6bps ≈ -3.54%`
  - `rv_midband_q20_80 @ 6bps ≈ -2.53%`
  - `trade_count_retention ≈ 17.76%`

原 park 的关键审计结论很集中：
- 这条线不是在“更聪明地放行”，而是在**强行裁掉大部分交易**；
- 改善没有在三条主线上形成统一、可迁移的 shared gate 价值；
- 所以被否掉的是“mid-band realized-vol 本身可以充当 shared 15m allow/deny 主语”这层写法，而不是所有 volatility / tradeability 信息都无效。

## 2) 它更像 hard park 还是 soft park？
**更像 `soft park`，但对原 Rank 72 本体读法已经明显偏硬。**

原因：
- soft 的地方在于：波动 / 可交易性 / 成本生存这类信息，显然仍然是 desk 关心的；
- hard 的地方在于：`mid-band shared allow/deny gate` 这条原始写法已经被审清，问题不太像“阈值还没调对”，而更像**职责摆错了**。

换成人话：
- “看波动状态再决定少做还是多做”这件事没死；
- 但“用 q20~q80 这种 realized-vol 中段去统一服务三条 setup 的共享入场门”这条具体表达，已经很难再救。

## 3) 现有证据里是否存在“可救信号”？
**有一点 residual，但不够长成新的 derived hypothesis。**

### 可救信号是什么
- 原 clean replication 至少说明：极端高波 / 极端低波之外，某些 tradeability 条件确实会影响结果；
- 4 月初的新 digest 又继续把这个方向往更诚实的角色层上推：
  - `lowfreq liquidity proxy gate overlay` 更像在说：**波动 / 流动性信息适合做 cost-aware overlay**；
  - `UTC slot cost map route veto overlay` 更像在说：**真正值钱的是时段成本地图 / 执行 veto / route 约束**，而不是 bar-level 的 shared entry gate。

### 为什么这不等于“可以救 Rank 72”
问题在于，这些新证据抬升的，已经不是原 `Rank 72` 那种 `realized-vol mid-band` 单一主语，而是更上位的：
- execution / liquidity / timing overlay family；
- cost-aware veto / sizing / routing family。

也就是说：
- 可救信号不是“Rank 72 原写法快成功了”；
- 而是“它留下的一点 residual，正在外流到更泛、更上位的 execution overlay 家族”。

## 4) 最值得改的唯一一刀是什么？
**如果今天硬要保留唯一一刀，最自然的一刀是：把 `shared allow/deny gate` 降级成 `cost-aware size-down / veto overlay`。**

也就是：
- 不再让 `realized-vol mid-band` 负责决定 setup 能不能进；
- 只让它在已有 setup 触发后，做 `size-down / veto` 级别的 tradeability 调整；
- 第一轮最多也只该测 `baseline vs vol-aware size-down/veto`，不应再偷带新的时段 map、liquidity proxy 组合、route、exit 第二轴。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论：`keep_park`。**

原因有三：
1. 这唯一可想象的一刀已经太泛，开始滑向“execution overlay 家族”的通用语言，而不是 `Rank 72` 自己仍保持 distinct 的单轴残余；
2. 最近的新证据把主题继续往 `liquidity-proxy / UTC-slot cost map / routing veto` 这类更上位宿主上推，说明它更像新的 family intake 线索，不像原 rank 的诚实窄派生；
3. 如果现在硬 draft 一个 `Rank 72b`，大概率会把“realized-vol mid-band”偷换成“泛 tradeability overlay”，这会稀释原 `park` verdict 的审计意义。

## 6) trade on / trade off 如何写？
本轮**不新增** derived hypothesis，因此不新写正式的 `trade on / trade off` 草案。

如果只作为审计备注，唯一还算说得通的 residual 读法是：
- `trade on`：vol / liquidity / slot-cost 信息可能适合做后置 `size-down / veto`；
- `trade off`：一旦把它写成独立 shared entry gate，就很容易重新退化成“靠砍样本美化结果”。

但这还不够具体，也不够 distinct，不能诚实升级成 queue-only 新提案。

## Final verdict for this round
- `verdict`: `keep_park`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park (theme still has residual value), but already quite hard for the original Rank 72 implementation`

## Minimal audit note
This round does **not** overturn the original `park`.
The newer early-April evidence is useful, but it mainly says the residual value of this line now lives more naturally inside **execution / liquidity / slot-cost overlays**, not as another honest extension of old `Rank 72`.

## Git
- 本轮只做最小必要文档更新；未做 commit。
- 原因：git 工作区存在大量无关脏文件 / 未跟踪文件，当前不适合安全地 selective commit。
