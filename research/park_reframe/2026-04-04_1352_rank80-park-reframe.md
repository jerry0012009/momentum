# 2026-04-04 13:52 UTC — Rank 80 park reframe

## 本轮选择
- 按 `bot6` 当前轮转，`50+` 号段近 24h 已连续覆盖 `50/51/52/54/57/58/59`，因此本轮切到 `80~110` 号段。
- `Rank 80` 近 7 天未被 `bot6` 低频复盘；同时过去两天新增了更直接的开段冲击旁证（尤其是 `2026-04-03_0042_btc-volclock-first30-impulse-alpha.md`），值得判断它是否还能诚实派生出一个新的窄 reframe。

## 读集
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/park_reframe/2026-04-04_1140_rank59-park-reframe.md`
- `research/park_reframe/2026-04-04_0924_rank58-park-reframe.md`
- `research/optimization_loop/2026-03-19_0528_rank80-first30m-impulse-intake.md`
- `research/optimization_loop/2026-03-19_0547_rank80-clean-replication-keep-p1.md`
- `research/quant_digests/2026-04-03_0042_btc-volclock-first30-impulse-alpha.md`
- `research/park_reframe/2026-04-03_1551_rank87-park-reframe.md`

## 原 rank 为什么 park
原 `Rank 80` 想做的是：
- 把 `00/08/16 UTC` funding-style session 前 `30m` 的方向、量能、波动，写成一个 **shared continuation gate / sizing layer**；
- 横向服务 `breakout_short / ema_psar_long / fib_retest_long`；
- 也就是说，它的主语不是单币事件 alpha，而是“开段冲击质量够不够高，值得不值得继续放行后续 continuation”。

但最小 clean replication 已经把 blocker 交代得很清楚：
- `impulse_halfsize` 相比 baseline 只是把 desk 级总亏损从约 `-2.00%` 收窄到 `-1.09%`，`mean_expectancy` 也只是小幅改善，**没有把 early-fail 真正压下去**；
- `impulse_veto` 虽然表面上接近转正，但 `mean_trade_count_retention ≈ 14.01%`，明显带着“靠极端砍样本美化”的味道；
- 真正有用的 pocket 主要集中在 `breakout_short`；
- `fib_retest_long` 反而被冲击 gate 稀释，说明它并不是三条 lane 都受益的 shared 质量层。

翻成人话：
**原 Rank 80 不是完全没信息，而是它留下的残余更像“某一类 continuation / 某一类单币开段事件可用”，不足以继续撑住跨三条 setup 的 shared gate 角色。**

## 它更像 hard park 还是 soft park
**结论：`soft park`，但现在已经明显偏硬。**

为什么仍算 soft park：
- 开段冲击质量本身不是假命题；
- clean replication 至少证明 `half-size` 比 `strict veto` 更诚实，也证明“开段强弱”确实带一点 continuation 信息。

为什么现在更偏硬：
- 这点残余越来越不像 `Rank 80` 自己还能再诚实派生的新 shared gate；
- 最近新证据把它继续推向 **单币 / event-style raw-alpha family**，而不是推回旧 shared continuation gate 写法。

## 有没有可救信号
**有，但更像主题外流，不像 `Rank 80` 本体还值得再写 `80b`。**

本轮能确认的可救信号只有一条：
- **“前 30 分钟冲击质量” 这层信息仍然有残余价值，但更自然的宿主不是 shared gate，而是更窄的单币 volume-clock / pseudo-open 事件型 continuation。**

新增旁证主要有两层：
1. `2026-04-03_0042_btc-volclock-first30-impulse-alpha.md`
   - 新 digest 已把同主题明确收敛成：`BTC volume-clock 首30m极端冲击 × 同向续行 30~60m`；
   - 这已经不是“给三条 lane 共用的 gate”，而是更直接的 **单币 event-style raw alpha**。
2. `2026-04-03 15:51 UTC | Rank 87`
   - 近邻 `volume-clock + CS spread shared gate` 已在昨天被判定：其残余价值更像新的单币 event-style raw-alpha family，而不是旧 shared gate 的诚实窄派生；
   - 这与 `Rank 80` 当前看到的残余方向高度一致。

另外，`docs/PARK_REFRAME_QUEUE.md` 里已有 `Rank 5b`：
- 它已经把“session 开段 impulse 质量”这条 shared continuation sizing / veto 读法占住了；
- 所以即便还想保留 `shared gate` 语义，最自然的那条窄改写也早已被 `Rank 5b` 吸收。

## 最值得改的唯一一刀是什么
如果只保留 **1 条唯一主修改轴**，本轮最值得改的一刀其实是：

**把 `Rank 80` 从跨 setup shared continuation gate，继续收窄成 `BTC-only / volume-clock anchored / first30m impulse -> 30~60m continuation` 的单币事件型宿主。**

但这刀本轮**不值得再单独写成新的 `Rank 80b`**，原因有三：
1. 这已经不只是窄化，而是在换岗位：从 shared gate 变成单币 raw alpha；
2. 这条语义已被最新 `btc-volclock-first30-impulse` digest 明确承接，血缘上更像新 family，而不是旧 `Rank 80` 的诚实派生；
3. 若现在硬写 `Rank 80b`，会与既有 `Rank 5b`（shared gate 版本）和 `Rank 87` 的最新审计边界打架，模糊原 `park` verdict。

## 是否值得形成新的 derived hypothesis
**不值得。最终结论：`keep_park`。**

原因：
- 原 `park` blocker 没被推翻：作为 shared continuation gate，它仍主要是 lane-specific pocket，而不是 desk 级统一改善；
- 唯一可救信号已经分流到两边：
  - shared-gate 语义已基本被既有 `Rank 5b` 吸收；
  - 更强的新旁证则把主题继续推向单币 volume-clock event raw-alpha family；
- 因此现在再写 `Rank 80b` 不够诚实，保留原 `park` 的审计边界更对。

## 模板回答
1. **原 rank 为什么 park？**
   - 因为它作为 shared continuation gate 只留下很薄的 lane-specific 改善：`halfsize` 只是小幅减亏、`strict veto` 明显靠极端砍样本，且真正有效的 pocket 主要集中在 `breakout_short`，还会稀释 `fib_retest_long`。
2. **更像 hard park 还是 soft park？**
   - `soft park`，但现在已明显偏硬。
3. **有没有可救信号？**
   - 有；但更像“first30m impulse” 应外流到单币 volume-clock / pseudo-open 事件型 raw-alpha 宿主，或者继续由既有 `Rank 5b` 承接其 shared-gate 语义。
4. **最值得改的唯一一刀是什么？**
   - 从 shared gate 继续收窄成 `BTC-only first30m impulse -> 30~60m continuation` 的单币事件型宿主。
5. **是否值得形成新的 derived hypothesis？**
   - 不值得。

## 最小审计结论
- 保留原 `park` verdict；
- `Rank 80` 本轮记为 **`keep_park`**；
- 它留下的不是值得新写 `Rank 80b` 的独立残余，而是：
  - shared-gate 语义已被既有 `Rank 5b` 基本吸收；
  - 更强的新旁证则把主题继续外流到单币 volume-clock / first30m event-style raw-alpha family。

## Git
- 当前 repo 仍有与本轮无关的脏文件；本轮只做 park-reframe 所需最小文本更新，不改 `docs/TODO.md`，也不做混合提交。
