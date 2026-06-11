# 2026-04-07 20:55 UTC · Rank 33 park reframe review

## Scope
- source rank: `Rank 33 / NW + confirmed HL reclaim`
- original verdict stays: `park / evidence pool`
- this round only asks: **after the newer early-April structure / event-verdict evidence, should Rank 33 stay a soft reframe candidate, or is it finally narrow enough to draft a queue-facing `Rank 33b`?**

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- recent park-reframe references:
  - `research/park_reframe/2026-04-07_1847_rank72-park-reframe.md`
  - `research/park_reframe/2026-04-07_1459_rank8-park-reframe.md`
  - `research/park_reframe/2026-04-07_1232_rank13-park-reframe.md`
- needed evidence:
  - `research/optimization_loop/2026-03-17_1150_rank33-clean-replication-park.md`
  - `research/park_reframe/2026-03-23_1337_rank33-park-reframe.md`
  - `research/quant_digests/INDEX.md` relevant newer signals:
    - `2026-04-02_0041_largebody-engulfing-reversal-alpha.md`
    - `2026-04-04_2132_intraday-horizon-router-cubic-alpha.md`
    - `2026-04-05_1701_chartpattern-neckline-imbalance-alpha.md`

## Why this rank this round
- 继续按 `Rank 1~37` 的 parked rank 低频复盘来选；`Rank 33` 上次 park-reframe 复盘是 `2026-03-23 13:37 UTC`，已超过 7 天。
- 它目前仍停在 `soft_reframe_candidate`，但还没有真正形成 queue-facing 的 `Rank 33b`。
- 4 月初的新 digest 又连续提供了更偏“事件确认 / failure verdict / horizon routing”的证据，正适合回答：这些新证据是否终于足以把 `Rank 33` 压成一个唯一单轴提案，还是只会进一步说明它更像 shared verdict hint。

## 1) 原 rank 为什么 park？
原 `Rank 33` 被 park，不是因为“结构 reclaim”主题完全没信息，而是因为它写成 **standalone `NW + confirmed HL/LH reclaim` entry** 后，结果依旧不够诚实：

- `raw_extrema_reclaim @ 6bps`：`mean_total_return ≈ -1.72%`，`positive_asset_ratio = 1/3`，`mean_false_reclaim_ratio ≈ 49.13%`
- `nw_hl_reclaim @ 6bps`：`mean_total_return ≈ -1.39%`，`positive_asset_ratio = 1/3`，`mean_false_reclaim_ratio ≈ 47.20%`
- `nw_hl_plus_highbreak @ 6bps`：`mean_total_return ≈ -8.51%`，`positive_asset_ratio = 1/3`，`mean_no_trade_ratio ≈ 98.71%`

原审计结论很清楚：
- `NW` 平滑能把假 reclaim 比例压低一点；
- 但压低假 reclaim 并没有长成可部署收益；
- 一旦再叠 `highbreak`，就迅速滑向“极度稀疏 + 几乎不交易”的美化；
- 所以被否掉的是“`NW + reclaim` 自己就是可独立交易的 continuation entry”这层写法。

## 2) 它更像 hard park 还是 soft park？
**仍更像 `soft park`，但比 3 月底更偏硬。**

原因：
- soft 的地方在于：它留下的 `false reclaim / bad reclaim` 识别能力，仍然有一点 residual value；
- 偏硬的地方在于：这点 residual 越来越清楚地不是 standalone alpha，而只是给别的 setup 提供 `failure verdict / veto hint` 的角色层。

换句话说：
- “reclaim 后是不是假动作”这个问题还有信息；
- 但“把平滑后的 reclaim 本身直接拿来开仓”这条旧 Rank 33 读法，已经更难诚实重开。

## 3) 有没有“可救信号”？
**有，但还停留在 `soft_reframe_candidate`，没有长成可直接 draft 的新 rank。**

### 可救信号是什么
原 clean replication 和 3 月 23 日复盘已经说明：
- `Rank 33` 真正剩下的，不是 reclaim continuation edge；
- 而是它对 `false reclaim / failure path` 有一点识别价值。

4 月初的新证据继续把这个方向往“事件 verdict”上推：
- `large-body engulfing reversal` 更像在说：结构失败的值钱部分，常常集中在**短时反转事件**，不是慢平滑 reclaim 本身；
- `intraday horizon router` 更像在说：同一冲击之后该先分 `sub-hour fade` 和 `1h-1d follow`，说明结构主题更适合做 **route / verdict**，不是单一路径 entry；
- `neckline breakout × taker-imbalance confirmation` 则进一步提示：真正可交易的结构确认，往往靠 **break 事件当下的 conviction / imbalance**，而不是事后再等一层平滑 reclaim。

### 为什么这还不够救成 `Rank 33b`
因为这些新证据虽然都支持“`Rank 33` 应继续降级成 failure / verdict 角色”，但它们并没有给出一个仍然属于原 `Rank 33` 宿主、且足够 distinct 的单轴新写法：
- 要么更像新的 breakout-confirmation raw-alpha family；
- 要么更像新的 event-driven reversal family；
- 要么更像泛化的 horizon / failure router。

也就是说：
- 它们增强了 `why not standalone reclaim` 的判断；
- 却没有提供一个比现有“shared false-reclaim veto / failure-routing hint”更窄、更能直接上队列的新主语。

## 4) 最值得改的唯一一刀是什么？
**如果今天还保留唯一一刀，答案仍是：把 `Rank 33` 从 standalone `NW + reclaim` entry，降级成 `shared false-reclaim veto / failure-routing hint`。**

也就是：
- 不再让 `NW + confirmed HL/LH reclaim` 自己直接开仓；
- 只在已有 setup 触发后，额外判断这次 reclaim 更像 `clean reclaim` 还是 `false reclaim / failure path`；
- 第一轮最多只该测 `baseline vs veto-only / failure-note` 这一刀，不该顺手偷带 breakout-bar imbalance、engulfing event、新 exit、horizon router 第二轴。

## 5) 是否值得形成新的 derived hypothesis？
**暂时不值得。结论：`soft_reframe_candidate`。**

原因：
1. 原 `park` 的审计结论依然成立，不能被推翻；
2. 4 月初新证据的共同方向是“继续削弱 reclaim 本体、强化事件 verdict / failure routing 角色”，这支持它留在 soft reframe 区，但还不够 distinct；
3. 如果现在硬 draft `Rank 33b`，大概率会把原 `Rank 33` 偷换成别的宿主（breakout-bar confirmation / engulfing reversal / horizon router），这会稀释原 rank 的审计边界；
4. 因此，本轮更诚实的动作仍是：**保留 `soft_reframe_candidate`，但不升级成 `derived_hypothesis_drafted`。**

## 6) 如果值得，新假设的 trade on / trade off 如何写？
本轮**不新增** derived hypothesis，因此不写正式 queue-facing `trade on / trade off`。

若只作为 why-not-draft 备注，当前最接近的残余读法仍是：
- `trade on`：把 false-reclaim 识别能力迁移成 shared veto / failure-routing 层，减少把坏 reclaim 误当 continuation；
- `trade off`：它极容易退化成“砍单美化”或被别的 event-confirm 宿主吞掉；若不能对冻结 setup 做 strict A/B，就不该升格成 queue-only 新 rank。

但这还不够具体，也不够 distinct，暂不诚实升级为 `Rank 33b`。

## Final verdict for this round
- `verdict`: `soft_reframe_candidate`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park, but now closer to hard for the original standalone reclaim reading`

## Minimal audit note
This round does **not** overturn the original `park`.
The newer early-April evidence is useful, but it mainly says the residual value of `Rank 33` lives more naturally inside **failure-verdict / route-selection hints**, not as another honest standalone reclaim continuation strategy.

## Git
- 本轮只做最小必要文档更新；未做 commit。
- 原因：git 工作区存在无关脏文件（如 `../../bots-panel/*` 修改），当前不适合安全地 selective commit。
