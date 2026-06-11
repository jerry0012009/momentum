# 2026-03-16 03:18 UTC · Desk Board Review

## 本轮一句话判断

**席位不换，但排班再收紧一格：`Paper Seat = EMA` 不变，`Live Seat = breakout` 继续保留且正式维持 `keep but narrower-scope`，`Scout Seat` 继续找更短周期 crypto challenger；这轮真正该补的是把 `TRADING DESK BOARD` 里的 `Next 3 bot3 runs` 从通用顺序改成当前 blocked 窗口下的具体三步排班。**

## 当前 strongest evidence

1. **Paper Seat 仍只能是 EMA**
   - 仍是 `closest to paper`；
   - 已有 `runbook / ledger / monitoring / refresh history`；
   - 当前真正缺口仍是 **连续 market-close refresh / week-1 review 的 forward honesty**，而不是更多说明页。

2. **Live Seat 仍只能先给 breakout，但必须按更窄口径读**
   - `breakout` 目前仍是最接近 `crypto tiny-live review` 的现有 challenger；
   - 但 current blocker 没有本质缩短，仍是：
     - `pure down coverage = 0`
     - `pre-down bridge coverage = 0`
   - 所以当前更诚实的结论只能是：**`keep but narrower-scope`**，而不是继续把它当会自然升级的大主线。

3. **bot3 最近已开始按 Run 3 fallback 动起来**
   - 最近 optimization log 已新增：`2026-03-16_0314_tiny-live-plumbing-board.md`；
   - 说明双阻塞窗口里，bot3 已不再只会交 `NO_PROGRESS`，而是开始去做 `tiny-live plumbing`。
   - 但 cron run history 同时显示最近一轮列表状态是 `error`，主因是 **exact-text edit mismatch**，不是研究方向跑偏。

## 当前 weakest / should-park lines

- **Fibonacci**：继续 `park / archive`，本轮没有任何理由回升优先级。
- **breakout 的同样本重复 rerun**：当前最该避免。既然仍处于 `narrower-scope + cooldown-aware` 阶段，就不该继续把时间烧在近义 rerun 上。

## 建议优先级 Top 1~3

1. **先把未来 3 个 bot3 runs 排具体**
   - 因为接下来约 40 分钟内，`EMA` 大概率仍未到 A 股 next close；
   - 如果这时还只保留通用 `Run 1/2/3` 说明，bot3 仍可能在 blocked 窗口里摇摆。

2. **Live Seat 继续 `keep but narrower-scope`，优先交 blocker sync / hard verdict，而不是重复 rerun**
   - 若 breakout 仍在 cooldown，就优先出 `keep-one_more_gate / narrower-scope` 的硬口径更新；
   - 只有 cooldown 结束且 cache 仍领先时，才允许做 1 次 heavy rerun 检查。

3. **Scout / tiny-live 继续补替补通道**
   - 先补 1 张 `crypto 5m/15m breakout/confirmation` shortlist card；
   - 再沿 `small_live_plumbing_v1` 补最小 operator 切片（`live ledger / routing dry-run / mismatch guard`）。

## TODO / web / cron 本轮改动

### 已改：`docs/TODO.md` 顶部 `Next 3 bot3 runs`

新增当前窗口排班（2026-03-16 03:17）：
1. `breakout` 的 cooldown-aware hard verdict / blocker sync
2. 一张 `Scout Seat` shortlist card（优先 `crypto 5m/15m breakout/confirmation`）
3. `small_live_plumbing_v1` 续一小步（`live ledger / routing dry-run / mismatch guard` 三选一）

这轮改动的核心价值是：**把 desk board 从“抽象顺序”推进到“当前窗口的明确排班”**，减少 bot3 在 blocked 窗口里的解释空间。

### 这轮不改

- 不改 `Paper Seat`
- 不改 `Live Seat` 归属
- 不改 `Scout Seat` 角色
- 不改 cron 频率
- 不改首页主排序文案

原因：当前问题不在席位归属，而在 **当前 3 个 bot3 runs 需要更具体**。

## 风险与不确定性

1. 这轮改的是调度清晰度，不是新增 alpha 证据本身。
2. 若接下来 bot3 仍在 blocked 窗口里频繁因 exact-text edit mismatch 报错，下一轮应考虑把相关 prompt 再收紧成“少 edit、多写新 artifact / 新 log”。
3. 若 breakout 很快出现新的 `pure-test / down-tail` blocker reduction，当前 `narrower-scope` 读法可以再复核；但在此之前，不应自动恢复为宽口径主线。

## 本轮一句话结论（给 Jerry）

**这轮我没换席位，而是把当前 3 个 bot3 runs 的排班写得更具体：EMA 继续坐 Paper Seat，breakout 继续坐 Live Seat 但按 `keep but narrower-scope` 读，Scout 继续补替补；接下来 bot3 不该再在 blocked 窗口里空转，而要按“breakout blocker sync → scout shortlist → tiny-live plumbing”这三步走。**
