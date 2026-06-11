# 2026-03-30 08:53 UTC · Rank 14 park reframe review

## Scope
- Source rank: `Rank 14 / cross-asset TSMOM confirmation gate`
- Original authoritative verdict stays: `park / evidence pool`
- This round only asks: 在不推翻原 `park` 的前提下，`Rank 14` 是否还值得再派生一条新的窄 reframe hypothesis。

## Why revisit Rank 14 this round
- 最近 `7` 天内没有再复盘过 `Rank 14`；上一次 park-reframe 是 `2026-03-22 16:33 UTC`。
- 但最近新增了两条与 cross-market intraday TSMOM 直接相关、且口径比旧 `peer confirm` 更完整的新证据：
  1. `research/quant_digests/2026-03-28_1545_leader-window-basket-itsm-alpha.md`
  2. `research/quant_digests/2026-03-30_0844_pseudosession-open-leader-continuation-alpha.md`
- 本轮要回答的不是“cross-market 有没有信息”，而是：这些新证据会不会诚实地支持 `Rank 14c`，还是反而进一步说明原 `Rank 14` 的残余价值已经被既有 `Rank 14b` 和更上位 raw-alpha family 吸收。

## Read set
- required:
  - `docs/TODO.md`
  - `docs/PARK_REFRAME_QUEUE.md`
  - `docs/RECENT_PAPER_SEEDS.md`
  - `research/quant_digests/INDEX.md`
  - `research/park_reframe/INDEX.md`
- needed evidence:
  - `research/optimization_loop/2026-03-17_0052_rank14-cross-asset-tsmom-park.md`
  - `research/park_reframe/2026-03-22_1633_rank14-park-reframe.md`
  - `research/quant_digests/2026-03-28_1545_leader-window-basket-itsm-alpha.md`
  - `research/quant_digests/2026-03-30_0844_pseudosession-open-leader-continuation-alpha.md`

## 1) 原 rank 为什么 park？
原 `Rank 14` 想验证的是：
- 单币 `sign(momentum)` 若再叠一层 **peer-basket 同频共振确认**，是否能把 `15m` crypto 动量从 evidence 推到 candidate。

但 clean replication 已把这条路审得很清楚：
- baseline `sign(momentum)` 本身已很差；
- `peer_1h / peer_4h / peer_dual_gate / peer_dual_strict` 都没有救回来；
- `peer_dual_gate` 在 `6bps/side` 下甚至比 baseline 更差，跨资产 `positive_asset_ratio=0/3`；
- 时间、参数、跨标的、成本四类 stability 一起 fail。

翻成人话：
**不是 cross-market 完全没信息，而是“另外两币和我同向”这种同频 peer confirm 写法，既没救活 sign-momentum，反而把它变得更差。**

## 2) 它更像 hard park 还是 soft park？
**结论：soft park，但比 2026-03-22 更偏硬。**

原因：
- hard 的部分没有变：原 `Rank 14` 作为 standalone `peer confirm rescue` 已经被硬审计为失败；
- soft 的部分也还在：cross-market 信息并没有消失，最近新 digest 反而继续说明这类信息有交易价值；
- 但它活下来的位置越来越清楚地不在原 `Rank 14` 这个“shared confirmation gate”角色里，而是在更上位的 **leader-driven raw alpha / basket raw alpha / dominant-leader continuation** family。

## 3) 有没有“可救信号”？
**有，但越来越不像在救 `Rank 14` 本身。**

### 可救信号 A：2026-03-28 leader-window basket 证据
`2026-03-28_1545_leader-window-basket-itsm-alpha.md` 的核心不是“peer 同向就放行”，而是：
- 先看 **leader 首窗方向**；
- 再去交易 **相关资产篮子尾窗同向**；
- 它更像完整的 `leader -> basket` raw alpha。

这和原 `Rank 14` 的区别很大：
- 原 Rank 14 把 cross-asset 信息写成 **shared confirmation gate**；
- 新证据更像把 cross-asset 信息写成 **alpha 本体**。

### 可救信号 B：2026-03-30 dominant leader continuation 证据
`2026-03-30_0844_pseudosession-open-leader-continuation-alpha.md` 更进一步：
- 真正留边的不是“至少 2/3 同向”；
- 而是 **leader 自己先明显跑赢 runner-up**，再去做 leader 的后续续动；
- `spread-to-runner` 是 admission gate，但 alpha 本体是 **dominant leader continuation**。

这条证据对 `Rank 14` 很关键，因为它几乎直接否掉了“peer 同向确认”那套旧读法：
- breadth / peer coherence 可以是条件；
- 但真正该交易的不是“我和别人一起同向”，而是“最强 leader 自己继续领跑”。

## 4) 最值得改的唯一一刀是什么？
如果硬要继续保留与 `Rank 14` 的血缘关系，**唯一还能算诚实的一刀**只会是：

- **把 `cross-asset peer confirmation` 彻底降级成 `dominant leader continuation` 的 admission context**，而不再把它写成 shared gate。

但这刀本轮**不值得立项**，原因有三：
1. 它已经不再是原 Rank 14 的微调，而是在把主题改写成另一条更完整的 raw-alpha 骨架；
2. 这会与最新的 leader/basket/dominant-leader 新 family 高度重合，超出 `bot6` 此轮“只做窄 reframe”的边界；
3. 既有 `Rank 14b` 已经把原命题还能留下的最自然 residual（directional breadth coherence long-side veto）记录完了，再写 `14c` 只会把 residual 从 gate 再推向 raw alpha，审计边界会变脏。

## 5) 是否值得形成新的 derived hypothesis？
**结论：不值得。**

本轮最终 verdict：**`keep_park`**。

原因不是 cross-market 主题死了；恰好相反，最近证据说明它活得还行。
但活下来的东西越来越像：
- `leader-window basket raw alpha`
- `dominant leader continuation raw alpha`
- `spread-to-runner admission gate`

而不是新的 `Rank 14c`。

## 6) 如果勉强要写 trade on / trade off，会是什么？
仅作为“不立项”的澄清：

- `trade on`：pseudo-session 首 30m 出现明显 dominant leader，且 `leader - runner_up` 扩大到阈值以上时，允许 leader continuation。
- `trade off`：只有宽泛 breadth / peer same-direction、但没有 clear dominant leader 时 abstain。

但这已经明显是另一条 raw-alpha 家族的定义，不是 `Rank 14` 的诚实 queue-only 派生，因此本轮明确不写成 `Rank 14c`。

## why now
因为 3/28 与 3/30 的新证据很容易让人产生一种错觉：
- “既然 cross-market intraday TSMOM 又有新 digest，`Rank 14` 应该还能再救一次。”

本轮的作用就是把这层错觉切干净：
- **cross-market 主题还活着；**
- **但它活在 leader-driven raw alpha family 里，不再诚实地活在 `Rank 14` 的 peer-confirm gate 血缘里。**

## suggested initial state
- 不适用；本轮不是 `derived_hypothesis_drafted`。

## Final template answers
1. **原 rank 为什么 park？**
   - 因为 `peer-basket` 同频确认不仅没救活 `sign(momentum)`，反而在 `BTC/ETH/SOL 120d 15m` 最小 clean replication 下比 baseline 更差，且 stability 四件套一起 fail。
2. **它更像 hard park 还是 soft park？**
   - soft park，但比 2026-03-22 更偏硬。
3. **有没有“可救信号”？**
   - 有，但信号指向 `leader-driven / dominant-leader` raw-alpha family，而不是新的 `Rank 14c`。
4. **最值得改的唯一一刀是什么？**
   - 若硬改，只能把 peer confirm 彻底降级成 dominant-leader continuation 的 admission context。
5. **是否值得形成新的 derived hypothesis？**
   - 不值得。
6. **为什么不立 `Rank 14c`？**
   - 因为新证据已经超出原 rank 的窄 reframe 边界，进入另一条更完整的 raw-alpha family；继续写 `14c` 会污染原 `park` 的审计边界。

## Queue write-back
- `docs/PARK_REFRAME_QUEUE.md`：仅追加一条最近复盘记录；不新增 `Rank 14c`
- `research/park_reframe/INDEX.md`：追加本轮索引
- `docs/TODO.md`：不改

## Git / commit
- 本轮不做 commit。
- 原因：`git status --short | wc -l = 4123`，工作区无关脏文件过多，不适合安全 selective commit。
