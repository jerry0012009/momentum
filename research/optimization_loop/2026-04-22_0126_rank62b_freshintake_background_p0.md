# 2026-04-22 01:26 UTC · Rank 62b fresh intake first verdict

## 本轮结论
- 执行对象：`research/park_reframe/2026-04-21_0542_rank62-park-reframe.md`
- 执行动作：fresh intake first verdict
- 结论：**`Rank 62b / 前 2~3 根 bar fail-fast 检查后 handoff 到 slow exit` 直接收口 `background/P0`**
- 一句话结果：`two-stage handoff` 虽把原 Rank 62 在 `fib_retest_long` 上的 winner truncation 从“明显过早截断”缓和成“更接近 baseline”，但新增改善主要来自把退出时钟整体放慢，且没有留下跨 archetype、非单一 `SOL` pocket 的独立 after-cost 新价值，因此不保留 `keep_P1`。

## 为什么这轮只补这一个最小 blocker
按当前 `cycle_plan`，本轮只允许回答一个问题：
- `Rank 62b` 是否真的修复了原 Rank 62 的 `fib winner truncation`，而不是仅仅靠“把 full-lifecycle fail-fast 改慢”制造纸面改善。

因此本轮冻结：
- **不改 entry / sizing / regime / universe**；
- 只在原 `Rank 62` clean replication 同一口径上，加一条最小 `two-stage handoff` 对照；
- 对照仍只看三条原 archetype：`ema_psar_long`、`fib_retest_long`、`breakout_short`。

## 复核口径
复用原 `Rank 62` clean replication 脚本与同一批 `BTC/ETH/SOL 120d 15m` 缓存：
- 入场：`signal bar -> next-bar open`
- no-overlap
- base hold cap：`8 bars`
- 成本：统一 `6bps/side`
- 原对照：
  - `base_exit`
  - `ema_vwap_atr_fail_fast`
- 本轮新增最小 honesty 对照：
  - `two_stage_donchian20`：前段只保留 `ema/atr fail-fast`；若 trade 存活满 `3` 根 bar 或顺向达到约 `0.75 ATR`，则 handoff 到慢 exit
  - `two_stage_donchian35`：同上，但用更慢的 Donchian 参数复核“改善是否只是继续放慢”

## 最小检查结果
### 1) `fib_retest_long`：确实缓和了 winner truncation，但没有把对象救成独立 front candidate
整体均值（3 个资产平均 total return）：
- `base_exit ≈ +0.88%`
- `ema_vwap_atr_fail_fast ≈ -1.88%`
- `two_stage_donchian20/35 ≈ -0.11%`

解释：
- 两段式 handoff 的确比“全程 fail-fast”更接近 baseline；
- 但它并没有恢复到稳定优于 baseline，仍然整体小幅为负；
- 真正的修复几乎都来自 `SOL`：
  - `SOL ≈ +4.63%`, `winner_truncation_rate=0.00`
- 另外两条并没形成同样的独立修复：
  - `BTC ≈ -2.74%`, `winner_truncation_rate=0.60`
  - `ETH ≈ -2.23%`, `winner_truncation_rate=0.50`

也就是说，Fib 的“修复”没有跨到至少两个非单一资产 pocket，只留下单一 `SOL` pocket，不能诚实写成可继续前排追踪的通用 exit 重写。

### 2) `ema_psar_long`：两段式没有保住原 fail-fast 的主要新增价值
整体均值（3 个资产平均 total return）：
- `base_exit ≈ -5.55%`
- `ema_vwap_atr_fail_fast ≈ -3.92%`
- `two_stage_donchian20 ≈ -6.05%`
- `two_stage_donchian35 ≈ -6.29%`

解释：
- 原 Rank 62 之所以还能留下 residual，就是因为 `ema_psar_long` 上 full fail-fast 至少能更快认错；
- 但两段式一旦把 exit clock 放慢，`ema_psar_long` 的平均表现直接掉回接近甚至劣于 baseline；
- 这说明它没有证明“前段 fail-fast + 后段 slow exit”同时保留了原本的 quick-failure edge。

换句话说，`Rank 62b` 不是在原 strongest archetype 上更诚实地修复，而是先丢掉了原本唯一比较像新增价值的那部分。

### 3) `breakout_short`：没有形成新增修复，只是回到接近 baseline 的弱负值
整体均值：
- `base_exit ≈ -2.58%`
- `ema_vwap_atr_fail_fast ≈ -3.12%`
- `two_stage_donchian20/35 ≈ -2.61%`

解释：
- 两段式只是把 full fail-fast 的劣化往 baseline 拉回一点；
- 但它没有把原本负 pocket 修成可继续追踪的 after-cost edge；
- 因此第三条 archetype 也没有给出“shared exit handoff 值得继续”的支持票。

## 这轮最关键的 honesty 结论
本轮问的不是“two-stage handoff 听起来是否合理”，而是：
- 它是否真修复了原 Rank 62 的 blocker；
- 且不是仅靠把退出整体放慢来制造表面改善。

答案是：**没有。**

更具体地说：
1. `fib_retest_long` 上的改善确实存在，但主要集中在单一 `SOL` pocket；
2. `ema_psar_long` 上原 fail-fast 的 quick-failure edge 反而丢失；
3. `breakout_short` 仍未被修复；
4. `donchian20` 与 `donchian35` 几乎给出同样结论，说明这不是一个“只差再调一点参数”的 survivor blocker，而更像结构上没有留下独立新增价值。

因此，本对象当前更像一条 **exit-clock rewrite note**：
- 可作为“不要把 fail-fast 全程绑死在持仓上”的工程提醒；
- 但还不足以作为新的 front-slot hypothesis 保留。

## First verdict
**`Rank 62b = background/P0`**

原因冻结为一句话：
- `two-stage handoff` 没有在不牺牲 `ema_psar_long` 原 quick-failure edge、且不依赖单一 `SOL fib` pocket 的前提下，留下跨 archetype 的独立新增价值；当前改善主要只是把退出时钟整体放慢后的局部修补，而不是值得继续保留为 `keep_P1` 的新 hypothesis。

## 对 runtime 的直接影响
- `Fresh intake slot`：本轮当前对象直接收口 `background/P0`
- 不形成 `keep_P1`
- 不占用 `Surviving candidate slot`
- 当前 `cycle_plan` 的第 2 项（conditional survivor prewrite）其前置条件已被本轮结论否定

## 产物说明
- 本轮未改 policy / brief / cron prompt
- 本轮只新增内部研究日志与 runtime 结论
- publish homepage / email 作为尾部动作独立执行；若失败，不回滚上述 verdict

## 尾部动作回执（异步）
- `publish_homepage_index.sh`：进程最终 `SIGKILL` 结束（非阻断尾部失败，未回滚本轮 verdict/state/log）。
- `send_text_email.py`：执行成功，邮件已发送。
