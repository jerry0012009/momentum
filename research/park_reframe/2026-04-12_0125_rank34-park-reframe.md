# 2026-04-12 01:25 UTC · Rank 34 park reframe revisit

- source rank: `Rank 34 / chip-distribution trapped-holder reclaim / winner-ratio gate`
- current authoritative verdict: `park / evidence pool`
- this round verdict: `keep_park`
- original park verdict kept: `yes`

## Why this rank this round
- 按 `bot6` 轮转纪律，本轮不再重复碰最近 7 天内刚复盘过的 `50+` 与 `1~24` 旧项，转到 `25~49` 段。
- `Rank 34` 上次 park-reframe 复盘是 `2026-04-04 04:55 UTC`，已超过 7 天，满足低频复看要求。
- 这条线原本就属于审计边界很清楚的 parked rank：真正 blocker 在 `synthetic shares / turnover` proxy 的 assumptions sensitivity，而不是简单阈值没调好；适合在 4 月上旬新证据累积后做一次复核。

## Files read this round
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/park_reframe/2026-04-11_2325_rank69-park-reframe.md`
- `research/park_reframe/2026-04-11_2100_rank18-park-reframe.md`
- `research/optimization_loop/2026-03-17_1222_rank34-clean-replication-park.md`
- `research/park_reframe/2026-03-25_0055_rank34-park-reframe.md`
- `research/park_reframe/2026-04-04_0455_rank34-park-reframe.md`
- `research/quant_digests/2026-04-05_1755_poc-cvd-absorption-alpha.md`
- `research/quant_digests/2026-04-11_2010_stacked-orderflow-vote-shell.md`

## 1) 原 rank 为什么 park？
原 `Rank 34` 被 park 的主因一直没有变：
**edge 主要寄生在 `synthetic shares / turnover anchor` 的乐观写法上，一旦锚点假设放宽，就很快失真。**

原 clean replication 的关键结果仍然成立：
- `raw_baseline @ 6bps/side` 三资产均值约 `-7.38%`，base line 本身不成立；
- 看上去最好的 `chip_cost_reclaim` 只在 `conservative anchor` 下好看：
  - `mean_total_return ≈ +18.14%`
  - `positive_asset_ratio = 3/3`
- 但切到 `neutral / aggressive anchor` 后迅速退化：
  - `neutral @ 6bps`：均值尚可，但 `positive_asset_ratio` 已掉到 `1/3`
  - `aggressive @ 6bps`：均值直接转为明显负值
- 成本升到 `15~20bps` 后，即便 `conservative anchor` 的 pocket 也站不稳。

所以原 rank 被 park，不是因为“库存/筹码故事完全没信息”，而是因为：
**可交易结论过度依赖一个很难诚实冻结的持仓分布代理。**

## 2) 它更像 hard park 还是 soft park？
本轮结论：**更像 hard park。**

理由：
- blocker 不在 entry/exit 的表层写法，而在核心 explanatory variable 本身；
- 最好看的结果始终依赖最保守、最容易“看起来合理”的 anchor 版本；
- 4 月上旬新证据并没有把旧 proxy 变得更诚实，反而持续把主题上移到更直接的 `POC / CVD absorption / order-flow` 原始宿主。

若勉强保留一点 soft 成分，只剩：
- `conservative anchor` 下曾有正 pocket；
- 这说明“库存拥挤 / trapped-holder reclaim”这类市场直觉并非完全空想。

但这点 soft 成分不足以改变总判断，因为 pocket 的成立条件本身就不够诚实。

## 3) 有没有“可救信号”？
**有主题级可救信号，但没有属于旧 Rank 34 本体的可救信号。**

本轮补读的 4 月新证据给出了更清楚的去向：
1. `2026-04-05_1755_poc-cvd-absorption-alpha.md`
   - 把 volume-profile / inventory-anchor 主题重新写成：`1H POC-proximal price/CVD absorption × 15m child execution`
   - 主语已经是更直接的 `POC + signed-flow divergence`，不再依赖 synthetic shares proxy。
2. `2026-04-11_2010_stacked-orderflow-vote-shell.md`
   - 进一步说明 `CVD trend / bar delta / absorption` 更像可拆解的 order-flow raw alpha / exit shell；
   - 也不是旧 Rank 34 那种 assumptions-sensitive trapped-holder reclaim gate。

因此当前真正的“可救信号”是：
- **volume-profile / inventory-anchor 主题仍有信息量；**
- **但有信息量的宿主已经换成更直接的 POC / CVD / order-flow raw-alpha family。**

它救的是主题，不是旧 `Rank 34` 的 proxy 壳。

## 4) 最值得改的唯一一刀是什么？
如果只保留唯一主修改轴，最诚实的一刀仍然只能写成：

**把 `chip-distribution reclaim` 从可交易 trigger 降级成离线 crowding / context 证据层，而不是继续当 15m 可执行 gate。**

也就是：
- 不再让它决定 bar-level allow/deny；
- 只把它保留为一种“背景拥挤/库存压力解释变量”。

但这也是本轮不 draft 新派生的原因：
- 一旦降到这个层级，它已经不再是 bot2 可直接判断是否入板的 queue-facing hypothesis；
- 它也没有把旧 proxy 的 honesty 问题解决掉，只是把它进一步边缘化；
- 更重要的是，4 月新证据提供的更优解法不是“继续保留旧 proxy 但降级”，而是直接换到新的 `POC / CVD absorption / order-flow` 宿主。

## 5) 是否值得形成新的 derived hypothesis？
结论：**不值得；本轮维持 `keep_park`。**

理由：
1. 原 `park` verdict 的审计意义依然很强，没必要推翻；
2. 4 月新增证据没有修复 `synthetic shares / turnover` proxy 的 assumptions sensitivity；
3. 若现在硬写 `Rank 34b`，大概率只是把旧 proxy 改名后再讲一次，或者滑向“换宿主 + 换变量”的多轴大改；
4. 更诚实的处理方式，是承认旧 Rank 34 已更接近 hard park，而主题残余已经外流到新的 raw-alpha family。

## 6) 如果硬要写 trade on / trade off，会怎样？
本轮不 draft，但为了审计边界，仍把它写清楚：

### 假如硬写成 reframe，唯一可能的一刀
- single modification axis:
  - `demote chip-distribution reclaim from executable 15m trigger into offline crowding/context evidence only`

### trade on
- 保留原 rank 对“库存拥挤/套牢盘重夺”直觉的审计痕迹；
- 不再要求它自己给出 bar-level entry / gate；
- 只把它作为背景解释层，辅助理解更直接的 POC / CVD / absorption 主题。

### trade off
- 它不再是 queue-facing hypothesis；
- 没有解决旧 proxy 的核心 honesty 问题；
- 很容易沦为“事后解释变量”，而非可复现实验对象。

也正因为这组 `trade on / trade off` 已经说明它不再适合作为独立候选，本轮不应把它正式写成 `Rank 34b`。

## Final verdict
**`keep_park`**

- 原 `park` verdict 保留；
- `Rank 34` 本体更像 `hard park`；
- 4 月新证据只说明 volume-profile / inventory-anchor 主题应迁到更直接的新宿主，而不是足以从旧 `Rank 34` 再诚实派生一个窄 reframe；
- 因此本轮不 draft `Rank 34b`。

## Queue impact
- 仅更新 `docs/PARK_REFRAME_QUEUE.md` 的最近复盘记录；
- 仅更新 `research/park_reframe/INDEX.md`；
- 默认不改 `docs/TODO.md` 顶部排班；
- 不新增 active reframe candidate。

## Commit note
- 本轮只做最小必要文档改动。
- 工作区存在大量与本轮无关的脏文件 / 未跟踪文件，因此**不做 selective commit**，避免混提。
